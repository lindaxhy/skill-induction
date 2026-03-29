"""
Skill Induction — Resume Category Classification (24 classes)

Pipeline:
1. Induce per-category descriptions from training examples (1 LLM call per batch)
2. Select 1 representative example per category (full text, no truncation)
3. Assemble skills/resume_category_skill.md
"""

import json
import os
import re
import sys

import pandas as pd
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from llm_client import chat, INDUCTION_MODEL

TRAIN_PATH = os.path.join(os.path.dirname(__file__),
    "../../skill_construction_dataset/splits/resume2_train.tsv")
SKILL_OUT = os.path.join(os.path.dirname(__file__),
    "../skills/resume_category_skill.md")

CATEGORIES = [
    "INFORMATION-TECHNOLOGY", "BUSINESS-DEVELOPMENT", "ADVOCATE", "CHEF",
    "FINANCE", "ENGINEERING", "ACCOUNTANT", "FITNESS", "AVIATION", "SALES",
    "HEALTHCARE", "CONSULTANT", "BANKING", "CONSTRUCTION", "PUBLIC-RELATIONS",
    "HR", "DESIGNER", "ARTS", "TEACHER", "APPAREL", "DIGITAL-MEDIA",
    "AGRICULTURE", "AUTOMOBILE", "BPO",
]


# ---------------------------------------------------------------------------
# Step 1: Induce category descriptions (batched, 1 LLM call per 8 categories)
# ---------------------------------------------------------------------------

def induce_category_descriptions(train_df: pd.DataFrame) -> dict[str, str]:
    """For each category, generate a 3-4 sentence description using training examples."""
    descriptions = {}
    # Process in batches of 8 to stay within token budget
    batch_size = 8
    cats = [c for c in CATEGORIES if c in train_df["Category"].unique()]

    for batch_start in range(0, len(cats), batch_size):
        batch = cats[batch_start: batch_start + batch_size]
        print(f"  Inducing descriptions for: {batch}")

        # For each category in batch, get 3 short excerpts (first 400 chars each)
        blocks = []
        for cat in batch:
            subset = train_df[train_df["Category"] == cat]
            excerpts = []
            for _, row in subset.head(3).iterrows():
                text = str(row["Resume_str"])[:400].replace("\n", " ")
                excerpts.append(f"  - {text}")
            excerpt_text = "\n".join(excerpts)
            blocks.append(f"### {cat}\n{excerpt_text}")

        batched_text = "\n\n".join(blocks)

        system = (
            "You are an expert career counselor and resume analyst. "
            "Given resume excerpts from a specific job category, write a precise 3-4 sentence "
            "description of what characterizes resumes in that category: "
            "typical job titles, key skills, certifications, experience patterns, and terminology."
        )
        user = (
            f"For each category below, write a 3-4 sentence description capturing "
            f"what distinguishes resumes in that category.\n\n"
            f"{batched_text}\n\n"
            f"Return ONLY a JSON object: "
            + "{"
            + ", ".join(f'"{c}": "description"' for c in batch)
            + "}"
        )

        response = chat(system=system, user=user, model=INDUCTION_MODEL, temperature=0.3)

        # Parse JSON
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                descriptions.update(parsed)
                continue
            except Exception:
                pass
        # Fallback: extract per-category via regex
        for cat in batch:
            m = re.search(rf'"{cat}"\s*:\s*"([^"]+)"', response)
            if m:
                descriptions[cat] = m.group(1)
            else:
                descriptions[cat] = f"Resumes in the {cat} category."

    return descriptions


# ---------------------------------------------------------------------------
# Step 2: Select 1 representative example per category (full text)
# ---------------------------------------------------------------------------

def select_examples(train_df: pd.DataFrame) -> dict[str, dict]:
    """Pick the longest (most complete) resume per category as the example."""
    examples = {}
    for cat in CATEGORIES:
        subset = train_df[train_df["Category"] == cat]
        if subset.empty:
            continue
        # Pick median-length resume (not too short, not anomalously long)
        subset = subset.copy()
        subset["len"] = subset["Resume_str"].str.len()
        subset = subset.sort_values("len")
        mid_idx = len(subset) // 2
        row = subset.iloc[mid_idx]
        examples[cat] = {
            "category": cat,
            "resume":   str(row["Resume_str"]),
        }
    return examples


# ---------------------------------------------------------------------------
# Step 3: Assemble skill file
# ---------------------------------------------------------------------------

def assemble_skill(descriptions: dict[str, str], examples: dict[str, dict],
                   train_df: pd.DataFrame) -> str:
    parts = []

    parts.append("# Resume Category Classification Skill\n")
    parts.append(
        "You are an expert resume classifier. Given a resume, assign it to exactly one "
        "of the 24 job categories listed below. Use the category descriptions and calibration "
        "examples to guide your decision.\n"
    )

    # Category list
    parts.append("## The 24 Categories\n")
    parts.append(", ".join(CATEGORIES))
    parts.append("\n")

    # Distribution stats
    dist = train_df["Category"].value_counts()
    parts.append("## Category Distribution (Training Data)\n")
    for cat in CATEGORIES:
        n = dist.get(cat, 0)
        parts.append(f"- {cat}: {n} examples")
    parts.append("\n")

    # Category descriptions
    parts.append("## Category Descriptions\n")
    for cat in CATEGORIES:
        desc = descriptions.get(cat, f"Resumes in the {cat} category.")
        parts.append(f"### {cat}\n{desc}\n")

    # Calibration examples (1 per category, full resume)
    parts.append("## Calibration Examples (1 per category)\n")
    parts.append(
        "Each example shows a real resume from that category. "
        "Full text is provided — do not truncate your reading.\n"
    )
    for cat in CATEGORIES:
        if cat not in examples:
            continue
        ex = examples[cat]
        parts.append(f"### Example: {cat}")
        parts.append(ex["resume"])
        parts.append("")

    # Scoring instructions
    parts.append("## Classification Instructions\n")
    parts.append(
        "1. Read the resume carefully.\n"
        "2. Identify key skills, job titles, industry terms, and experience patterns.\n"
        "3. Match against the category descriptions above.\n"
        "4. Use the calibration examples for additional anchoring.\n"
        "5. Output ONLY a JSON object on a single line — nothing else:\n"
        '   `{"category": "CATEGORY_NAME"}`\n'
        "   where CATEGORY_NAME is exactly one of the 24 categories listed above.\n"
    )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Loading training data...")
    train_df = pd.read_csv(TRAIN_PATH, sep="\t")
    print(f"  {len(train_df)} rows | {train_df['Category'].nunique()} categories")

    print("\n[Step 1] Inducing category descriptions (batched LLM calls)...")
    descriptions = induce_category_descriptions(train_df)
    print(f"  Got descriptions for {len(descriptions)} categories")

    print("\n[Step 2] Selecting 1 example per category (full resume)...")
    examples = select_examples(train_df)
    print(f"  Selected {len(examples)} examples")

    print("\n[Step 3] Assembling skill file...")
    skill_text = assemble_skill(descriptions, examples, train_df)

    with open(SKILL_OUT, "w") as f:
        f.write(skill_text)

    chars = len(skill_text)
    tokens_est = chars // 4
    print(f"\nSkill saved to {SKILL_OUT}")
    print(f"  Size: {chars:,} chars (~{tokens_est:,} tokens est.)")
    print(f"\n--- Category description sample (AVIATION) ---")
    print(descriptions.get("AVIATION", "N/A"))


if __name__ == "__main__":
    main()
