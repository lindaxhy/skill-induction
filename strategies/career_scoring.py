"""
Skill Induction — CareerCorpus Resume Quality Scoring (0–1 continuous)

Pipeline:
1. Induce rubric from training examples (what makes a high vs low quality resume)
2. Select quintile examples (full fields, no truncation)
3. Generate annotations via 1 LLM batch call
4. Assemble skills/career_scoring_skill.md
"""

import json
import os
import re
import sys

import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from llm_client import chat, INDUCTION_MODEL

TRAIN_PATH = os.path.join(os.path.dirname(__file__),
    "../../skill_construction_dataset/splits/career_train.tsv")
SKILL_OUT = os.path.join(os.path.dirname(__file__),
    "../skills/career_scoring_skill.md")


def format_resume(row) -> str:
    """Combine structured fields into a single resume text block."""
    return (
        f"Domain: {row['Domain']}\n"
        f"Job Type: {row['Job_type']}\n\n"
        f"Education:\n{row['Education']}\n\n"
        f"Skills and Achievements:\n{row['Skills and Achievements']}\n\n"
        f"Experience:\n{row['Experience']}"
    )


# ---------------------------------------------------------------------------
# Step 1: Induce rubric
# ---------------------------------------------------------------------------

def induce_rubric(train_df: pd.DataFrame) -> str:
    # Per-domain: pick 1 high and 1 low example from each domain's own distribution
    domain_high_texts = []
    domain_low_texts  = []
    domain_dist_lines = []
    for domain, grp in train_df.groupby('Domain'):
        grp_s = grp.sort_values('score')
        hi_row = grp_s.iloc[-1]   # highest in domain
        lo_row = grp_s.iloc[0]    # lowest in domain
        domain_high_texts.append(
            f"[{domain}] Score={hi_row['score']:.2f}\n{format_resume(hi_row)[:500]}"
        )
        domain_low_texts.append(
            f"[{domain}] Score={lo_row['score']:.2f}\n{format_resume(lo_row)[:500]}"
        )
        domain_dist_lines.append(
            f"  {domain}: mean={grp['score'].mean():.2f}, "
            f"range={grp['score'].min():.2f}–{grp['score'].max():.2f}"
        )

    high_texts = "\n\n---\n".join(domain_high_texts)
    low_texts  = "\n\n---\n".join(domain_low_texts)
    domain_context = "Domain score distributions (vary significantly — Apparel mean≈0.44, others ≈0.77–0.87):\n" \
                     + "\n".join(domain_dist_lines)

    system = (
        "You are an expert HR evaluator and career counselor. "
        "Analyze resume quality based on structured resume fields and produce a scoring rubric."
    )
    user = (
        f"IMPORTANT CONTEXT: This dataset spans 6 domains with very different score distributions.\n"
        f"{domain_context}\n\n"
        "The rubric MUST work across all domains. Do NOT use domain-specific vocabulary as a proxy "
        "for quality — e.g., having PLM/CAD tools is high quality in Apparel design, while having "
        "GL codes is high quality in Finance. Focus on domain-relative signals:\n"
        "  - Specificity of achievements (quantified % / $ / time)\n"
        "  - Depth of technical skills relative to domain norms\n"
        "  - Evidence of career progression (scope, responsibility, seniority)\n"
        "  - Clarity and concreteness (named tools, projects, outcomes)\n\n"
        "Below are the highest-scoring and lowest-scoring resume from EACH domain:\n\n"
        f"## HIGHEST-SCORING (per domain):\n{high_texts}\n\n"
        f"## LOWEST-SCORING (per domain):\n{low_texts}\n\n"
        "Write a precise scoring rubric with:\n"
        "1. **High Quality (0.75–1.0)**: 4–5 bullet points — domain-agnostic signals of excellence\n"
        "2. **Medium Quality (0.45–0.75)**: 3–4 bullet points — partial evidence of quality\n"
        "3. **Low Quality (0.0–0.45)**: 3–4 bullet points — absence of quality signals\n"
        "4. **Key scoring factors** (5–6): specificity, tool depth, progression, quantified impact, "
        "education relevance, concreteness\n"
        "Be concrete. Each bullet must be verifiable from the resume text."
    )

    print("  [Step 1] Inducing domain-aware rubric...")
    return chat(system=system, user=user, model=INDUCTION_MODEL, temperature=0.3)


# ---------------------------------------------------------------------------
# Step 2: Select quintile examples
# ---------------------------------------------------------------------------

def select_examples(train_df: pd.DataFrame) -> list:
    """Pick Q20 and Q80 example from EACH domain's own distribution (per-domain stratified)."""
    examples = []
    for domain, grp in train_df.groupby('Domain'):
        grp_sorted = grp.sort_values('score').reset_index(drop=True)
        n = len(grp_sorted)
        low_idx  = max(0, int(n * 0.20) - 1)
        high_idx = min(n - 1, int(n * 0.80))
        for idx in sorted({low_idx, high_idx}):
            examples.append(grp_sorted.iloc[idx])
    return examples


# ---------------------------------------------------------------------------
# Step 3: Batch-annotate examples
# ---------------------------------------------------------------------------

def annotate_examples(rubric: str, examples: list) -> dict[int, str]:
    blocks = []
    for i, row in enumerate(examples, 1):
        blocks.append(
            f"### Example {i} (score={row['score']:.2f}, domain={row['Domain']}, "
            f"job={row['Job_type']})\n"
            f"Education: {str(row['Education'])[:300]}\n"
            f"Skills: {str(row['Skills and Achievements'])[:300]}\n"
            f"Experience: {str(row['Experience'])[:300]}"
        )

    system = (
        "You are an expert HR annotator. "
        "Write 2–3 sentence explanations for why each resume received its score, "
        "citing specific features using the rubric vocabulary."
    )
    user = (
        f"## Rubric Summary\n{rubric[:1500]}\n\n"
        f"## Examples\n" + "\n\n".join(blocks) + "\n\n"
        f"Return ONLY JSON: "
        + "{"
        + ", ".join(f'"{i}": "annotation"' for i in range(1, len(examples)+1))
        + "}"
    )

    print("  [Step 3] Generating annotations (1 LLM call)...")
    response = chat(system=system, user=user, model=INDUCTION_MODEL, temperature=0.3)

    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        try:
            return {int(k): v for k, v in json.loads(match.group()).items()}
        except Exception:
            pass
    print("  [warn] Annotation parse failed; using score-based fallback")
    return {}


# ---------------------------------------------------------------------------
# Step 4: Compute distribution stats
# ---------------------------------------------------------------------------

def compute_stats(train_df: pd.DataFrame) -> str:
    s = train_df['score']
    lines = [
        f"- Score range: {s.min():.2f}–{s.max():.2f}",
        f"- Mean: {s.mean():.3f}  Std: {s.std():.3f}",
        f"- Quartiles: Q25={s.quantile(0.25):.3f}  Q50={s.quantile(0.50):.3f}  Q75={s.quantile(0.75):.3f}",
        f"- Top 10% threshold: {s.quantile(0.90):.3f}  Bottom 10%: {s.quantile(0.10):.3f}",
        f"- % Low (≤0.45): {100*(s<=0.45).mean():.1f}%  "
          f"% Medium (0.45–0.75): {100*((s>0.45)&(s<0.75)).mean():.1f}%  "
          f"% High (≥0.75): {100*(s>=0.75).mean():.1f}%",
        "",
        "Per-domain mean scores:",
    ]
    for domain, grp in train_df.groupby('Domain'):
        lines.append(f"  {domain}: mean={grp['score'].mean():.3f}  std={grp['score'].std():.3f}")
    lines += [
        "",
        "Per-job-type mean scores:",
    ]
    for jt, grp in train_df.groupby('Job_type'):
        lines.append(f"  {jt}: mean={grp['score'].mean():.3f}  n={len(grp)}")
    lines.append(
        "\nCalibration note: A score of 0.5 is genuinely below average for this dataset. "
        "Do NOT default to 0.5 — most resumes score 0.7–0.9."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Step 5: Assemble skill file
# ---------------------------------------------------------------------------

def assemble_skill(rubric: str, stats: str, examples: list,
                   annotations: dict[int, str]) -> str:
    parts = [
        "# Resume Quality Scoring Skill\n",
        "You are an expert HR evaluator scoring professional resumes on a 0–1 continuous scale. "
        "Higher scores indicate more qualified, clearer, and better-structured resumes. "
        "Evaluate based on the resume fields: Education, Skills and Achievements, and Experience.\n",

        "## Scoring Rubric\n",
        rubric.strip(), "\n",

        "## Score Distribution (Training Population)\n",
        stats, "\n",

        "## Calibration Examples\n",
        "Full resume fields are shown. Use these to anchor your numeric predictions.\n",
    ]

    for i, row in enumerate(examples, 1):
        annotation = annotations.get(i, f"Score reflects overall quality of education, skills, and experience.")
        parts += [
            f"### Example {i} — score={row['score']:.2f} | {row['Domain']} | {row['Job_type']}",
            format_resume(row),
            f"**Why score={row['score']:.2f}:** {annotation}",
            "",
        ]

    parts += [
        "## Scoring Instructions\n",
        "1. Read all resume fields carefully.\n",
        "2. Assess against the rubric criteria above.\n",
        "3. Compare against calibration examples for numeric anchoring.\n",
        "4. Output ONLY a JSON object on a single line:\n",
        '   `{"score": 0.XX}`\n',
        "   where the value is between 0.0 and 1.0 (two decimal places).\n",
    ]

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading training data...")
    train_df = pd.read_csv(TRAIN_PATH, sep="\t")
    print(f"  {len(train_df)} rows | score mean={train_df['score'].mean():.3f}")

    rubric = induce_rubric(train_df)

    stats = compute_stats(train_df)

    print("  [Step 2] Selecting per-domain stratified examples (full text, no truncation)...")
    examples = select_examples(train_df)
    print(f"  Selected {len(examples)} examples | "
          f"domains: {list(dict.fromkeys(r['Domain'] for r in examples))}")
    for r in examples:
        print(f"    {r['Domain']:<22} score={r['score']:.2f}")

    annotations = annotate_examples(rubric, examples)

    print("  [Step 4] Assembling skill file...")
    skill_text = assemble_skill(rubric, stats, examples, annotations)

    with open(SKILL_OUT, "w") as f:
        f.write(skill_text)

    chars = len(skill_text)
    print(f"\nSkill saved → {SKILL_OUT}")
    print(f"  Size: {chars:,} chars (~{chars//4:,} tokens est.)")
    print(f"\n--- Rubric preview (first 400 chars) ---")
    print(rubric[:400])


if __name__ == "__main__":
    main()
