"""
Skill Induction — Resume Screening (binary: select / reject)

Pipeline:
1. Cluster Reason_for_decision to form select/reject rubric criteria
2. Select balanced calibration examples (full resume, no truncation)
3. Generate annotations via 1 LLM batch call
4. Assemble skills/resume_screening_skill.md
"""

import json
import os
import re
import sys

import pandas as pd
from collections import Counter
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from llm_client import chat, INDUCTION_MODEL

TRAIN_PATH = os.path.join(os.path.dirname(__file__),
    "../../skill_construction_dataset/splits/resume_train.tsv")
SKILL_OUT = os.path.join(os.path.dirname(__file__),
    "../skills/resume_screening_skill.md")

N_EXAMPLES = 10   # 5 select + 5 reject, full resume text


# ---------------------------------------------------------------------------
# Step 1: Induce rubric from Reason_for_decision
# ---------------------------------------------------------------------------

def induce_rubric(train_df: pd.DataFrame) -> str:
    select_reasons = train_df[train_df["Decision"] == "select"]["Reason_for_decision"].tolist()
    reject_reasons = train_df[train_df["Decision"] == "reject"]["Reason_for_decision"].tolist()

    # Sample up to 60 of each to stay within token budget
    import random
    random.seed(42)
    sel_sample = random.sample(select_reasons, min(60, len(select_reasons)))
    rej_sample = random.sample(reject_reasons, min(60, len(reject_reasons)))

    sel_text = "\n".join(f"- {r}" for r in sel_sample)
    rej_text = "\n".join(f"- {r}" for r in rej_sample)

    system = (
        "You are an expert recruiter and job screening analyst. "
        "Your task is to synthesize a concise, actionable rubric for resume screening "
        "from a list of actual hiring decisions and reasons."
    )
    user = f"""Below are hiring decisions with their reasons from a resume screening dataset.

## SELECT reasons (candidate was hired):
{sel_text}

## REJECT reasons (candidate was rejected):
{rej_text}

Synthesize these into a structured screening rubric with:
1. **Key SELECT criteria** (5-7 bullet points: what makes a candidate stand out)
2. **Key REJECT criteria** (5-7 bullet points: common disqualifying factors)
3. **Edge case guidance** (2-3 points: situations that require closer judgment)

Be concrete and specific. Use language that maps directly to resume content."""

    print("  [Step 1] Inducing rubric from reasons...")
    rubric = chat(system=system, user=user, model=INDUCTION_MODEL, temperature=0.3)
    return rubric


# ---------------------------------------------------------------------------
# Step 2: Select calibration examples (balanced, diverse roles)
# ---------------------------------------------------------------------------

def select_examples(train_df: pd.DataFrame, n_each: int = 5) -> list[dict]:
    """Select n_each select + n_each reject examples, diverse roles, full text."""
    examples = []

    for decision in ["select", "reject"]:
        subset = train_df[train_df["Decision"] == decision].copy()
        # Prefer diversity across roles
        subset = subset.sample(frac=1, random_state=42)
        seen_roles = set()
        chosen = []
        for _, row in subset.iterrows():
            if len(chosen) >= n_each:
                break
            # Prefer a new role for diversity; fall back if needed
            if row["Role"] not in seen_roles or len(chosen) < n_each:
                chosen.append(row)
                seen_roles.add(row["Role"])
        examples.extend(chosen[:n_each])

    return examples


# ---------------------------------------------------------------------------
# Step 3: Batch-annotate examples
# ---------------------------------------------------------------------------

def annotate_examples(rubric: str, examples: list[dict]) -> dict[int, str]:
    blocks = []
    for i, row in enumerate(examples, 1):
        blocks.append(
            f"### Example {i}\n"
            f"Role: {row['Role']}\n"
            f"Decision: {row['Decision'].upper()}\n"
            f"Reason: {row['Reason_for_decision']}\n"
            f"Resume (excerpt — first 400 chars):\n{str(row['Resume'])[:400]}"
        )
    examples_text = "\n\n".join(blocks)

    system = (
        "You are an expert recruiter annotator. "
        "Write 2 concise sentences explaining why each resume received its decision, "
        "referencing specific rubric criteria. Be concrete."
    )
    user = f"""## Rubric Summary
{rubric[:1500]}

## Examples to annotate
{examples_text}

Return ONLY a JSON object: {{"1": "annotation", "2": "annotation", ..., "{len(examples)}": "annotation"}}"""

    print("  [Step 3] Generating annotations (1 LLM call)...")
    response = chat(system=system, user=user, model=INDUCTION_MODEL, temperature=0.3)

    # Parse JSON
    match = re.search(r'\{[^{}]+\}', response, re.DOTALL)
    if match:
        try:
            return {int(k): v for k, v in json.loads(match.group()).items()}
        except Exception:
            pass
    # Fallback: empty annotations
    print("  [warn] Failed to parse annotations JSON; using reason as annotation")
    return {}


# ---------------------------------------------------------------------------
# Step 4: Compute distribution stats
# ---------------------------------------------------------------------------

def compute_stats(train_df: pd.DataFrame) -> str:
    total = len(train_df)
    n_select = (train_df["Decision"] == "select").sum()
    n_reject = (train_df["Decision"] == "reject").sum()
    top_roles = train_df["Role"].value_counts().head(8).to_dict()
    roles_str = ", ".join(f"{r} ({n})" for r, n in top_roles.items())
    return (
        f"- Total training examples: {total} resumes\n"
        f"- Selected: {n_select} ({100*n_select/total:.0f}%)  |  Rejected: {n_reject} ({100*n_reject/total:.0f}%)\n"
        f"- Dataset is roughly balanced — do NOT default to 'reject'; ~43% of applicants are selected\n"
        f"- Top roles in training data: {roles_str}"
    )


# ---------------------------------------------------------------------------
# Step 5: Assemble skill file
# ---------------------------------------------------------------------------

def assemble_skill(rubric: str, stats: str, examples: list[dict],
                   annotations: dict[int, str]) -> str:
    parts = []

    parts.append("# Resume Screening Skill\n")
    parts.append(
        "You are an expert technical recruiter with deep experience screening resumes across "
        "software engineering, data science, product management, and design roles. "
        "Your task: given a job role, job description, and candidate resume, decide whether "
        "to **select** or **reject** the candidate.\n"
    )

    parts.append("## Screening Rubric\n")
    parts.append(rubric.strip())
    parts.append("\n")

    parts.append("## Dataset Distribution (Training Population)\n")
    parts.append(stats)
    parts.append("\n")

    parts.append("## Calibration Examples\n")
    parts.append(
        "Study these examples carefully. Each example includes the full resume "
        "and an explanation of why the decision was made.\n"
    )

    for i, row in enumerate(examples, 1):
        annotation = annotations.get(i, f"Decision based on: {row['Reason_for_decision']}")
        parts.append(f"### Example {i} — {row['Decision'].upper()}")
        parts.append(f"**Role:** {row['Role']}")
        parts.append(f"**Decision:** {row['Decision'].upper()}")
        parts.append(f"**Resume:**\n{row['Resume']}")
        parts.append(f"**Why:** {annotation}")
        parts.append("")

    parts.append("## Scoring Instructions\n")
    parts.append(
        "1. Read the role and job description to understand requirements.\n"
        "2. Assess the resume against the rubric criteria above.\n"
        "3. Compare against the calibration examples for anchoring.\n"
        "4. Output ONLY a JSON object on a single line — nothing else:\n"
        '   `{"decision": "select"}` or `{"decision": "reject"}`\n'
    )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Loading training data from {TRAIN_PATH} ...")
    train_df = pd.read_csv(TRAIN_PATH, sep="\t")
    print(f"  {len(train_df)} rows | "
          f"select={( train_df.Decision=='select').sum()} | "
          f"reject={(train_df.Decision=='reject').sum()}")

    rubric = induce_rubric(train_df)

    stats = compute_stats(train_df)
    print("  [Step 2] Selecting calibration examples...")
    example_rows = select_examples(train_df, n_each=N_EXAMPLES // 2)
    print(f"  Selected {len(example_rows)} examples "
          f"({sum(1 for r in example_rows if r['Decision']=='select')} select, "
          f"{sum(1 for r in example_rows if r['Decision']=='reject')} reject)")

    annotations = annotate_examples(rubric, example_rows)

    print("  [Step 4] Assembling skill file...")
    skill_text = assemble_skill(rubric, stats, example_rows, annotations)

    with open(SKILL_OUT, "w") as f:
        f.write(skill_text)

    chars = len(skill_text)
    tokens_est = chars // 4
    print(f"\nSkill saved to {SKILL_OUT}")
    print(f"  Size: {chars} chars (~{tokens_est} tokens est.)")
    print(f"\n--- Rubric preview (first 400 chars) ---")
    print(rubric[:400])


if __name__ == "__main__":
    main()
