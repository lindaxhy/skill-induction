#!/usr/bin/env python3
"""
Signal E + Mode G: Abstract style induction for academic researchers.

Pipeline steps:
  E1  Fetch papers from arXiv by author name
  E2  Extract style fingerprint (1 LLM call + human-review note)
  E3  Select reference examples (≤8 positives + 3 negatives)
  E4  Generate style annotations (1 LLM call)
  Assemble (E, G) skill file
  Eval  Generate abstracts from titles on held-out papers → ROUGE vs. ground truth

Validates the E+G path of SKILL_INDUCTION_PIPELINE.md.
Routing: Signal=E (examples only), Mode=G (generate new abstracts)
"""

import json
import os
import re
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI
from rouge_score import rouge_scorer

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    timeout=120,
)
MODEL = "openai/gpt-4o"
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
os.makedirs(SKILLS_DIR, exist_ok=True)

# ─── Configuration ────────────────────────────────────────────────────────────

TARGET_RESEARCHER  = "Yejin Choi"
NEGATIVE_RESEARCHER = "Greg Durrett"

# Local data file — provide this instead of live arXiv fetching.
# Format: {"yejin_choi": [...], "greg_durrett": [...]}
# Each entry: {"arxiv_id": "...", "title": "...", "abstract": "...", "year": 2025}
LOCAL_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "arxiv_abstracts.json")

EVAL_N      = 4   # hold out last N papers for ROUGE evaluation
INDUCTION_N = 8   # use first N papers for style induction

# ─── E1: Load papers from local file ─────────────────────────────────────────

def load_papers() -> tuple[list[dict], list[dict]]:
    """Load pre-downloaded paper data from LOCAL_DATA_PATH.
    Returns (target_papers, negative_papers)."""
    if not os.path.exists(LOCAL_DATA_PATH):
        print(f"[Error] Data file not found: {LOCAL_DATA_PATH}")
        print("Please create it using fetch_arxiv_abstracts.py")
        sys.exit(1)
    with open(LOCAL_DATA_PATH) as f:
        data = json.load(f)
    target_key   = TARGET_RESEARCHER.lower().replace(" ", "_")
    negative_key = NEGATIVE_RESEARCHER.lower().replace(" ", "_")
    target   = data.get(target_key,   data.get("target",   []))
    negative = data.get(negative_key, data.get("negative", []))
    return target, negative


# ─── E2: Extract style fingerprint ───────────────────────────────────────────

def extract_fingerprint(author: str, induction_papers: list[dict],
                        negative_papers: list[dict]) -> str:
    pos_block = "\n\n".join(
        f"[Positive {i+1}] {p['title']} ({p['year']})\n{p['abstract']}"
        for i, p in enumerate(induction_papers)
    )
    neg_block = "\n\n".join(
        f"[Negative {i+1}] {p['title']} ({p['year']})\n{p['abstract']}"
        for i, p in enumerate(negative_papers)
    )
    prompt = f"""You are a style analysis expert studying how different researchers write academic paper abstracts.

Below are abstracts written by {author}:

{pos_block}

---
For contrast, here are abstracts by a DIFFERENT researcher in the same NLP/AI field:

{neg_block}

---
Extract a structured STYLE FINGERPRINT describing how {author} writes abstracts. \
Be specific enough that another writer could reproduce this style. \
Do NOT use vague labels like "clear", "rigorous", or "concise."

1. **Opening patterns** — how does this author typically start? \
   Quote 2–3 opening sentences. Name the structural pattern (e.g., "problem-first", "context-first").

2. **Problem framing** — how do they present the research gap / motivation? \
   List 3+ specific phrases or sentence templates they reuse.

3. **Methodology description** — how do they describe their approach? \
   List verbs, framing phrases, and structural templates (e.g., "we introduce X, a Y that Z").

4. **Results and claims** — how do they present findings? \
   - Quantitative vs. qualitative balance
   - Hedging patterns (e.g., "demonstrates that", "significantly outperforms")
   - How do they frame benchmark comparisons?

5. **MOST IMPORTANT — unique fingerprint mechanisms** \
   List 3–5 patterns that appear in {author}'s abstracts but are absent or rare in the negatives. \
   For each: name the mechanism, quote ≥2 actual phrases, explain the rhetorical effect.

6. **What this author avoids** — specific constructions absent from their abstracts \
   (e.g., passive problem statements, numbered contribution lists, direct commercial framing)"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


# ─── E3: Select reference examples ───────────────────────────────────────────
# With N ≈ 12–15 positives, use up to 8 for the skill file + all negatives.
# Pipeline rule: do NOT truncate.

def select_examples(induction_papers: list[dict], n_select: int = 8) -> list[dict]:
    """Pick n_select papers that maximize topic diversity (simple: spread by index)."""
    if len(induction_papers) <= n_select:
        return induction_papers
    step = len(induction_papers) / n_select
    return [induction_papers[int(i * step)] for i in range(n_select)]


# ─── E4: Generate style annotations ─────────────────────────────────────────

def annotate_examples(author: str, fingerprint: str,
                      pos_examples: list[dict], neg_examples: list[dict]) -> dict:
    pos_block = "\n\n".join(
        f"[Positive {i+1}: {p['title']}]\n{p['abstract']}"
        for i, p in enumerate(pos_examples)
    )
    neg_block = "\n\n".join(
        f"[Negative {i+1}: {p['title']}]\n{p['abstract']}"
        for i, p in enumerate(neg_examples)
    )
    prompt = f"""You are annotating abstract examples to teach a language model to write in \
{author}'s style.

Style fingerprint (focus on section 5 — unique mechanisms):
{fingerprint}

For each abstract below, write a 2-sentence annotation:
- Positive: quote one phrase that demonstrates a mechanism from section 5, and name which mechanism.
- Negative: identify the one element that most violates {author}'s style.

{pos_block}

---
{neg_block}

Output JSON:
{{
  "positives": [{{"title": "...", "annotation": "..."}}],
  "negatives": [{{"title": "...", "annotation": "..."}}]
}}"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    raw = resp.choices[0].message.content.strip()
    m = re.search(r'\{[\s\S]+\}', raw)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return {"positives": [], "negatives": [], "raw": raw[:300]}


# ─── Assemble (E, G) skill file ───────────────────────────────────────────────

def assemble_skill(author: str, fingerprint: str,
                   pos_examples: list[dict], neg_examples: list[dict],
                   annotations: dict) -> str:
    pos_ann = {a["title"]: a["annotation"] for a in annotations.get("positives", [])}
    neg_ann = {a["title"]: a["annotation"] for a in annotations.get("negatives", [])}

    lines = [
        f"# {author} Abstract Style Skill\n",
        f"You are writing a research paper abstract in the style of {author}.",
        f"Study the style fingerprint and examples below, then generate an abstract that sounds like it was written by {author}.",
        "Do NOT copy content from the examples — reproduce the STYLE (structure, vocabulary, framing patterns), not the subject matter.\n",

        "## Style Fingerprint\n",
        fingerprint,
        "",

        "## Positive Examples (abstracts by this author)\n",
    ]
    for p in pos_examples:
        lines.append(f"### {p['title']} ({p['year']})")
        lines.append(p["abstract"])
        ann = pos_ann.get(p["title"], "")
        if ann:
            lines.append(f"\n**Style note:** {ann}")
        lines.append("")

    lines.append("## Negative Examples (different author, same field)\n")
    for n in neg_examples:
        lines.append(f"### {n['title']} ({n['year']})")
        lines.append(n["abstract"])
        ann = neg_ann.get(n["title"], "")
        if ann:
            lines.append(f"\n**What's missing:** {ann}")
        lines.append("")

    lines += [
        "## Generation Instructions\n",
        f"1. Read section 5 of the style fingerprint (unique mechanisms) — this is what makes {author}'s writing distinctive.",
        "2. Before writing, decide which mechanism(s) you will use as the structural backbone.",
        "3. Open the abstract with the pattern identified in section 1 of the fingerprint.",
        "4. Use the vocabulary and framing from sections 2–4.",
        "5. Do NOT use numbered contribution lists or bullet points unless the fingerprint says this author uses them.",
        "6. Output only the abstract text — no meta-commentary.",
    ]
    return "\n".join(lines)


# ─── Evaluation: generate abstracts from titles, compute ROUGE ───────────────

def generate_abstract(skill: str, title: str, intro: str, author: str) -> str:
    intro_block = f"\nIntroduction:\n{intro}" if intro.strip() else ""
    user_msg = (
        f'Write a research paper abstract for the following paper, '
        f'in the writing style of {author}:\n\n'
        f'Paper title: "{title}"'
        f'{intro_block}\n\n'
        f'Output only the abstract text.'
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": skill},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.5,
    )
    return resp.choices[0].message.content.strip()


def generate_abstract_zero_shot(title: str, intro: str, author: str) -> str:
    intro_block = f"\nIntroduction:\n{intro}" if intro.strip() else ""
    user_msg = (
        f'Write a research paper abstract for the following paper, '
        f'in the writing style of {author}:\n\n'
        f'Paper title: "{title}"'
        f'{intro_block}\n\n'
        f'Output only the abstract text.'
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.5,
    )
    return resp.choices[0].message.content.strip()


def rouge_scores(hypothesis: str, reference: str) -> dict:
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    s = scorer.score(reference, hypothesis)
    return {
        "r1_f": round(s["rouge1"].fmeasure, 4),
        "r2_f": round(s["rouge2"].fmeasure, 4),
        "rL_f": round(s["rougeL"].fmeasure, 4),
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # ── E1: Load papers from local file ───────────────────────────────────────
    print(f"E1: Loading papers from {LOCAL_DATA_PATH}...")
    target_papers, negative_papers = load_papers()
    print(f"  {TARGET_RESEARCHER}: {len(target_papers)} papers")
    print(f"  {NEGATIVE_RESEARCHER}: {len(negative_papers)} papers (negatives)")

    if len(target_papers) < EVAL_N + 3:
        print(f"[Error] Need at least {EVAL_N + 3} target papers, got {len(target_papers)}")
        return

    # Split: first INDUCTION_N for induction, last EVAL_N for eval
    induction_papers = target_papers[:INDUCTION_N]
    eval_papers      = target_papers[INDUCTION_N: INDUCTION_N + EVAL_N]
    print(f"  Induction: {len(induction_papers)} | Eval: {len(eval_papers)}")

    # ── E2: Extract style fingerprint ─────────────────────────────────────────
    print("\nE2: Extracting style fingerprint...")
    fingerprint = extract_fingerprint(TARGET_RESEARCHER, induction_papers, negative_papers)
    print("  [Human review note: Read section 5 of the fingerprint and verify mechanisms are operational, not abstract labels]")
    print(f"\n{'='*60}\nFINGERPRINT:\n{'='*60}")
    print(fingerprint[:1200], "..." if len(fingerprint) > 1200 else "")

    # ── E3: Select reference examples ─────────────────────────────────────────
    print("\nE3: Selecting reference examples...")
    selected_pos = select_examples(induction_papers, n_select=8)
    selected_neg = negative_papers[:3]
    print(f"  Selected {len(selected_pos)} positive, {len(selected_neg)} negative examples")

    # ── E4: Generate style annotations ────────────────────────────────────────
    print("\nE4: Generating style annotations...")
    annotations = annotate_examples(TARGET_RESEARCHER, fingerprint, selected_pos, selected_neg)
    if "raw" in annotations:
        print("  [Warning] JSON parse failed:", annotations["raw"])
    else:
        print(f"  Got {len(annotations.get('positives',[]))} pos annotations, "
              f"{len(annotations.get('negatives',[]))} neg annotations")

    # ── Assemble skill ────────────────────────────────────────────────────────
    print("\nAssembling skill file...")
    skill_text = assemble_skill(
        TARGET_RESEARCHER, fingerprint,
        selected_pos, selected_neg, annotations
    )
    skill_name  = TARGET_RESEARCHER.replace(" ", "_").lower() + "_abstract_skill.md"
    skill_path  = os.path.join(SKILLS_DIR, skill_name)
    with open(skill_path, "w") as f:
        f.write(skill_text)
    print(f"  Saved: {skill_path} ({len(skill_text.splitlines())} lines)")

    # ── Evaluation: ROUGE on held-out papers ──────────────────────────────────
    print(f"\n{'='*60}")
    print(f"ROUGE EVALUATION — {len(eval_papers)} held-out papers")
    print(f"{'='*60}")

    results = []
    for i, paper in enumerate(eval_papers):
        print(f"\n[{i+1}/{len(eval_papers)}] {paper['title'][:70]}...")

        # Zero-shot
        gen_zero = generate_abstract_zero_shot(paper["title"], paper.get("intro", ""), TARGET_RESEARCHER)
        time.sleep(0.5)

        # Skill-based
        gen_skill = generate_abstract(skill_text, paper["title"], paper.get("intro", ""), TARGET_RESEARCHER)
        time.sleep(0.5)

        scores_zero  = rouge_scores(gen_zero,  paper["abstract"])
        scores_skill = rouge_scores(gen_skill, paper["abstract"])

        results.append({
            "title":       paper["title"],
            "zero_shot":   scores_zero,
            "skill_based": scores_skill,
        })

        print(f"  zero-shot:  R1={scores_zero['r1_f']:.4f}  "
              f"R2={scores_zero['r2_f']:.4f}  RL={scores_zero['rL_f']:.4f}")
        print(f"  skill:      R1={scores_skill['r1_f']:.4f}  "
              f"R2={scores_skill['r2_f']:.4f}  RL={scores_skill['rL_f']:.4f}")
        delta_r1 = scores_skill["r1_f"] - scores_zero["r1_f"]
        print(f"  Δ ROUGE-1:  {delta_r1:+.4f}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"SUMMARY — {TARGET_RESEARCHER} abstract style induction")
    print(f"Signal=E  Mode=G  N_induction={len(induction_papers)}  N_eval={len(eval_papers)}")
    print(f"{'='*60}")

    def avg(key, subkey):
        return sum(r[key][subkey] for r in results) / len(results)

    print(f"{'Config':<12} | {'ROUGE-1':>8} | {'ROUGE-2':>8} | {'ROUGE-L':>8}")
    print("-" * 46)
    for cfg in ("zero_shot", "skill_based"):
        label = "zero-shot" if cfg == "zero_shot" else "skill"
        print(f"{label:<12} | {avg(cfg,'r1_f'):>8.4f} | {avg(cfg,'r2_f'):>8.4f} | {avg(cfg,'rL_f'):>8.4f}")
    print("=" * 46)
    delta_r1_avg = avg("skill_based", "r1_f") - avg("zero_shot", "r1_f")
    delta_r2_avg = avg("skill_based", "r2_f") - avg("zero_shot", "r2_f")
    print(f"{'Δ (skill-zero)':<12} | {delta_r1_avg:>+8.4f} | {delta_r2_avg:>+8.4f}")
    print()
    if delta_r1_avg > 0:
        print("✓ Skill improves ROUGE-1 — E+G path validated")
    else:
        print("✗ No ROUGE improvement — review fingerprint section 5")

    # ── Save results ──────────────────────────────────────────────────────────
    out_path = os.path.join(os.path.dirname(__file__),
                            f"evaluation_results_abstract_{TARGET_RESEARCHER.replace(' ','_').lower()}.json")
    payload = {
        "researcher": TARGET_RESEARCHER,
        "signal":     "E",
        "mode":       "G",
        "n_induction": len(induction_papers),
        "n_eval":      len(eval_papers),
        "papers": results,
        "summary": {
            "zero_shot":   {"r1": avg("zero_shot","r1_f"), "r2": avg("zero_shot","r2_f"), "rL": avg("zero_shot","rL_f")},
            "skill_based": {"r1": avg("skill_based","r1_f"), "r2": avg("skill_based","r2_f"), "rL": avg("skill_based","rL_f")},
        },
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Results saved: {out_path}")


if __name__ == "__main__":
    main()
