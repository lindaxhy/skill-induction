#!/usr/bin/env python3
"""
Signal E + Mode G: Collaboration-specific abstract style induction.
Target: Yejin Choi + Taylor Sorensen co-authored papers (pluralistic alignment, N=4).

Pipeline: E1 (load) → E2 (fingerprint) → E3 (select all, N<5) → E4 (annotate) → eval ROUGE
Validation: Leave-One-Out (LOO) across all 4 papers.

Two-tier negatives:
  A: Greg Durrett (different researcher, same NLP era)
  B: Early Yejin Choi commonsense papers (same author, different topic/era)
  → Fingerprint distinguishes Choi+Sorensen style from BOTH.
"""

import json, os, re, sys, time

from dotenv import load_dotenv
from openai import OpenAI
from rouge_score import rouge_scorer

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    timeout=120,
)
MODEL     = "openai/gpt-4o"
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
DATA_PATH  = os.path.join(os.path.dirname(__file__), "data", "arxiv_abstracts.json")
os.makedirs(SKILLS_DIR, exist_ok=True)

# ─── Target + negative IDs ────────────────────────────────────────────────────

TARGET_IDS = ["2402.05070", "2410.03868", "2510.06084", "2510.07105"]

NEG_DURRETT_IDS  = {"2310.16049", "2504.11381", "2602.16699"}
NEG_CHOI_OLD_IDS = {"1905.07830", "1908.05739", "2110.07178"}

AUTHOR_LABEL = "Yejin Choi and Taylor Sorensen"

# ─── E1: Load data ────────────────────────────────────────────────────────────

def load_data():
    with open(DATA_PATH) as f:
        data = json.load(f)
    all_choi    = {p["arxiv_id"]: p for p in data["yejin_choi"]}
    all_durrett = {p["arxiv_id"]: p for p in data["greg_durrett"]}

    target_papers = [all_choi[i] for i in TARGET_IDS if i in all_choi]
    neg_durrett   = [all_durrett[i] for i in NEG_DURRETT_IDS if i in all_durrett]
    neg_choi_old  = [all_choi[i] for i in NEG_CHOI_OLD_IDS if i in all_choi]

    print(f"E1: Loaded {len(target_papers)} target papers, "
          f"{len(neg_durrett)} Durrett negatives, "
          f"{len(neg_choi_old)} early-Choi negatives")
    return target_papers, neg_durrett, neg_choi_old


# ─── E2: Extract collaboration-specific fingerprint ──────────────────────────

def extract_fingerprint(induction_papers, neg_durrett, neg_choi_old):
    pos_block = "\n\n".join(
        f"[Positive {i+1}] {p['title']} ({p['year']})\n{p['abstract']}"
        for i, p in enumerate(induction_papers)
    )
    neg_a_block = "\n\n".join(
        f"[Negative-A {i+1}] {p['title']} ({p['year']})\n{p['abstract']}"
        for i, p in enumerate(neg_durrett)
    )
    neg_b_block = "\n\n".join(
        f"[Negative-B {i+1}] {p['title']} ({p['year']})\n{p['abstract']}"
        for i, p in enumerate(neg_choi_old)
    )
    prompt = f"""You are a style analysis expert. The following are research paper abstracts \
co-authored by {AUTHOR_LABEL}, all focused on pluralistic alignment, distributional AI, \
and personalized preference learning:

{pos_block}

---
Negative-A: Abstracts by Greg Durrett (DIFFERENT researcher, same NLP era, for contrast):
{neg_a_block}

---
Negative-B: Abstracts by Yejin Choi writing WITHOUT Taylor Sorensen (commonsense-benchmark era, \
same author but different topic/era):
{neg_b_block}

---
Extract a STYLE FINGERPRINT describing how {AUTHOR_LABEL} write abstracts in their \
collaborative alignment papers. Focus on what distinguishes their style from BOTH \
negative sets. Be specific — do NOT use vague adjectives like "clear" or "rigorous."

1. **Opening patterns** — how do they open? Quote 2 opening sentences. Name the pattern.

2. **Problem framing** — how do they frame the AI alignment / personalization challenge? \
List 2–3 specific phrases or templates they reuse.

3. **Methodology description** — how do they describe their approach? Specific verbs, \
sentence templates, structural choices.

4. **Claims and hedging** — how do they present results/positions? \
(position papers vs. empirical papers may differ)

5. **MOST IMPORTANT — unique fingerprint mechanisms** \
List 3–4 specific patterns that appear in the Choi+Sorensen papers \
but are absent from BOTH negative sets. \
For each: name the mechanism, quote ≥2 actual phrases, explain the effect. \
Think about: normative language, pluralism vocabulary, stance on AI values, \
rhetorical strategies specific to alignment position papers.

6. **What this collaboration avoids** — constructions absent from their style."""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


# ─── E3: Select examples (N<5 → use all) ─────────────────────────────────────

def select_examples(papers):
    return papers   # ultra-sparse: use all induction papers as reference


# ─── E4: Annotate examples ────────────────────────────────────────────────────

def annotate_examples(fingerprint, pos_examples, neg_examples):
    pos_block = "\n\n".join(
        f"[Positive {i+1}: {p['title']}]\n{p['abstract']}"
        for i, p in enumerate(pos_examples)
    )
    neg_block = "\n\n".join(
        f"[Negative {i+1}: {p['title']}]\n{p['abstract']}"
        for i, p in enumerate(neg_examples)
    )
    prompt = f"""Annotate the abstracts below to teach a language model the writing style \
of {AUTHOR_LABEL}.

Style fingerprint (pay special attention to section 5 — unique mechanisms):
{fingerprint}

For each abstract, write a 2-sentence annotation:
- Positive: quote one phrase that demonstrates a mechanism from section 5; name the mechanism.
- Negative: identify the one element that most violates the {AUTHOR_LABEL} style.

{pos_block}

---
{neg_block}

Output JSON:
{{"positives": [{{"title": "...", "annotation": "..."}}],
  "negatives": [{{"title": "...", "annotation": "..."}}]}}"""

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


# ─── Assemble (E, G) skill ────────────────────────────────────────────────────

def assemble_skill(fingerprint, pos_examples, neg_examples, annotations):
    pos_ann = {a["title"]: a["annotation"] for a in annotations.get("positives", [])}
    neg_ann = {a["title"]: a["annotation"] for a in annotations.get("negatives", [])}

    lines = [
        f"# {AUTHOR_LABEL} Abstract Style Skill\n",
        f"You are writing a research paper abstract in the collaborative style of "
        f"{AUTHOR_LABEL}.",
        "Study the style fingerprint and examples carefully, then generate an abstract that "
        "sounds like it was co-authored by both of them.",
        "Do NOT copy content from the examples — reproduce the STYLE "
        "(structure, vocabulary, framing, normative stance), not the subject matter.\n",
        "## Style Fingerprint\n",
        fingerprint, "",
        "## Positive Examples (co-authored by Yejin Choi + Taylor Sorensen)\n",
    ]
    for p in pos_examples:
        lines.append(f"### {p['title']} ({p['year']})")
        lines.append(p["abstract"])
        ann = pos_ann.get(p["title"], "")
        if ann:
            lines.append(f"\n**Style note:** {ann}")
        lines.append("")

    lines.append("## Negative Examples\n")
    for p in neg_examples:
        lines.append(f"### {p['title']} ({p['year']})")
        lines.append(p["abstract"])
        ann = neg_ann.get(p["title"], "")
        if ann:
            lines.append(f"\n**What's missing:** {ann}")
        lines.append("")

    lines += [
        "## Generation Instructions\n",
        "1. Read section 5 of the fingerprint — these mechanisms are what make this "
        "collaboration's writing distinctive.",
        "2. Before writing, choose which 1-2 mechanisms you will use as the backbone.",
        "3. Open with the pattern described in section 1.",
        "4. Use the normative/pluralistic vocabulary from section 2.",
        "5. Do NOT use bullet-pointed contribution lists.",
        "6. Output only the abstract text — no meta-commentary.",
    ]
    return "\n".join(lines)


# ─── Generate + ROUGE ────────────────────────────────────────────────────────

def generate(skill, title, intro):
    intro_block = f"\nOpening of introduction:\n{intro[:400]}..." if intro.strip() else ""
    msg = (f'Write a research paper abstract for the following paper, '
           f'in the writing style of {AUTHOR_LABEL}:\n\n'
           f'Paper title: "{title}"{intro_block}\n\nOutput only the abstract text.')
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": skill},
                  {"role": "user",   "content": msg}],
        temperature=0.5,
    )
    return resp.choices[0].message.content.strip()


def generate_zero_shot(title, intro):
    intro_block = f"\nOpening of introduction:\n{intro[:400]}..." if intro.strip() else ""
    msg = (f'Write a research paper abstract for the following paper, '
           f'in the writing style of {AUTHOR_LABEL}:\n\n'
           f'Paper title: "{title}"{intro_block}\n\nOutput only the abstract text.')
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": msg}],
        temperature=0.5,
    )
    return resp.choices[0].message.content.strip()


def rouge(hyp, ref):
    s = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    r = s.score(ref, hyp)
    return {k: round(v.fmeasure, 4) for k, v in r.items()}


# ─── Main: LOO loop ───────────────────────────────────────────────────────────

def main():
    target_papers, neg_durrett, neg_choi_old = load_data()

    if len(target_papers) < 4:
        print(f"[Error] Need 4 target papers, got {len(target_papers)}")
        sys.exit(1)

    all_negatives = neg_durrett + neg_choi_old
    fold_results  = []

    print(f"\nRunning LOO across {len(target_papers)} folds...\n")

    for fold_i, eval_paper in enumerate(target_papers):
        induction = [p for p in target_papers if p["arxiv_id"] != eval_paper["arxiv_id"]]
        print(f"{'='*60}")
        print(f"Fold {fold_i} — eval: {eval_paper['title'][:55]}")
        print(f"  induction: {[p['arxiv_id'] for p in induction]}")

        # E2
        print("  E2: Extracting fingerprint...")
        fingerprint = extract_fingerprint(induction, neg_durrett, neg_choi_old)

        # E3 + E4
        print("  E4: Annotating examples...")
        annotations = annotate_examples(fingerprint, induction, all_negatives[:4])
        n_pos = len(annotations.get("positives", []))
        print(f"  Got {n_pos} pos annotations")

        # Assemble
        skill_text = assemble_skill(fingerprint, induction, all_negatives[:4], annotations)
        skill_path = os.path.join(SKILLS_DIR, f"choi_sorensen_fold{fold_i}.md")
        with open(skill_path, "w") as f:
            f.write(skill_text)
        print(f"  Saved: {skill_path}")

        # Eval
        title = eval_paper["title"]
        intro = eval_paper.get("intro", "")
        ref   = eval_paper["abstract"]

        print("  Generating zero-shot...")
        gen_zero  = generate_zero_shot(title, intro)
        time.sleep(0.5)

        print("  Generating skill-based...")
        gen_skill = generate(skill_text, title, intro)
        time.sleep(0.5)

        scores_zero  = rouge(gen_zero,  ref)
        scores_skill = rouge(gen_skill, ref)

        print(f"  zero-shot: R1={scores_zero['rouge1']:.4f}  "
              f"R2={scores_zero['rouge2']:.4f}  RL={scores_zero['rougeL']:.4f}")
        print(f"  skill:     R1={scores_skill['rouge1']:.4f}  "
              f"R2={scores_skill['rouge2']:.4f}  RL={scores_skill['rougeL']:.4f}")
        print(f"  Δ ROUGE-1: {scores_skill['rouge1'] - scores_zero['rouge1']:+.4f}")

        fold_results.append({
            "fold":     fold_i,
            "eval_id":  eval_paper["arxiv_id"],
            "title":    title,
            "zero_shot":   scores_zero,
            "skill_based": scores_skill,
        })

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"LOO SUMMARY — {AUTHOR_LABEL}")
    print(f"Signal=E  Mode=G  N_induction=3 (per fold)  Folds={len(fold_results)}")
    print(f"{'='*60}")

    def avg(cfg, k):
        return sum(r[cfg][k] for r in fold_results) / len(fold_results)

    print(f"{'Config':<12} | {'ROUGE-1':>8} | {'ROUGE-2':>8} | {'ROUGE-L':>8}")
    print("-" * 46)
    for cfg in ("zero_shot", "skill_based"):
        label = "zero-shot" if cfg == "zero_shot" else "skill"
        print(f"{label:<12} | {avg(cfg,'rouge1'):>8.4f} | "
              f"{avg(cfg,'rouge2'):>8.4f} | {avg(cfg,'rougeL'):>8.4f}")
    print("=" * 46)
    dr1 = avg("skill_based", "rouge1") - avg("zero_shot", "rouge1")
    dr2 = avg("skill_based", "rouge2") - avg("zero_shot", "rouge2")
    print(f"{'Δ (skill-zero)':<12} | {dr1:>+8.4f} | {dr2:>+8.4f}")

    print()
    print("✓ Skill improves ROUGE-1" if dr1 > 0 else "✗ No ROUGE-1 improvement")

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = os.path.join(os.path.dirname(__file__),
                            "evaluation_results_choi_sorensen.json")
    with open(out_path, "w") as f:
        json.dump({
            "authors":    AUTHOR_LABEL,
            "signal":     "E",
            "mode":       "G",
            "validation": "LOO",
            "n_folds":    len(fold_results),
            "folds":      fold_results,
            "summary": {
                "zero_shot":   {k: avg("zero_shot",   k) for k in ("rouge1","rouge2","rougeL")},
                "skill_based": {k: avg("skill_based", k) for k in ("rouge1","rouge2","rougeL")},
            },
        }, f, indent=2, ensure_ascii=False)
    print(f"Results saved: {out_path}")


if __name__ == "__main__":
    main()
