"""
Strategy F: Rubric Explanation + 5-Shot Full Examples (GPT-4o evaluation)

Mirrors the paper's best prompting setup:
- Cleaned rubric explanation per dimension
- Population statistics + explicit score list
- 5 complete (untruncated) examples, one per quintile
- No LLM calls needed for induction

Evaluated with GPT-4o (openai/gpt-4o) and no essay truncation.
"""

import os
import re
import sys

import pandas as pd

TRAIN_PATH  = os.path.join(os.path.dirname(__file__), "../../skill_construction_dataset/splits/train.tsv")
RUBRIC_PATH = os.path.join(os.path.dirname(__file__), "../skills/few_shot_skill.md")
SKILLS_DIR  = os.path.join(os.path.dirname(__file__), "../skills")
OUTPUT_PATH = os.path.join(SKILLS_DIR, "strategy_f_skill.md")

RANDOM_STATE = 42


def load_clean_rubric() -> str:
    with open(RUBRIC_PATH) as f:
        rubric = f.read()
    rubric = rubric.split("\n## Scoring Instructions")[0].rstrip()
    rubric = re.sub(r'\s*\(e\.g\.,\s*Essays?\s*#[\d,\s#]+\)', '', rubric)
    return rubric


def select_examples(df: pd.DataFrame) -> pd.DataFrame:
    """Select 1 representative example per quintile (5 total), full essays."""
    df = df.dropna(subset=["essay"]).copy()
    df["quintile"] = pd.qcut(df["total"], q=5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])

    chosen = []
    for q in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        bucket = df[df["quintile"] == q]
        # Prefer essays from different prompts; pick shortest essay that's still complete
        unique = bucket.drop_duplicates(subset=["prompt"])
        sample = unique.sample(1, random_state=RANDOM_STATE)
        chosen.append(sample)

    return pd.concat(chosen).sort_values("total").reset_index(drop=True)


def build_skill(rubric_text: str, examples: pd.DataFrame) -> str:
    lines = [
        "# Essay Scoring Skill (Strategy F: Rubric + 5-Shot Full Examples)",
        "",
        "You are an expert scorer for ESL (English as a Second Language) student essays.",
        "Score each essay on three dimensions.",
        "",
        "---",
        "",
        rubric_text,
        "",
        "---",
        "",
        "## Score Distribution (Training Population)",
        "",
        "**Total score** (Content + Organization + Language): mean=10.3, range=3.5–15.0",
        "  - Bottom 10%: ≤ 7.5 | Bottom 25%: ≤ 9.0 | Median: 10.5 | Top 25%: ≥ 12.0 | Top 10%: ≥ 13.0",
        "",
        "Per-dimension breakdown:",
        "- **Content**: mean=3.48  (weak ≤2.0: 9%,  mid 2.5–3.5: 50%,  excellent ≥4.0: 42%)",
        "- **Organization**: mean=3.51  (weak ≤2.0: 7%,  mid 2.5–3.5: 47%,  excellent ≥4.0: 45%)",
        "- **Language**: mean=3.34  (weak ≤2.0: 7%,  mid 2.5–3.5: 62%,  excellent ≥4.0: 31%)",
        "",
        "**Valid scores per dimension:** [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]",
        "",
        "---",
        "",
        "## 5-Shot Calibration Examples",
        "",
        "Five complete essays from the same population, spanning the full score range.",
        "Use these to calibrate your numeric judgments.",
        "",
    ]

    for i, (_, row) in enumerate(examples.iterrows(), 1):
        lines += [
            f"### Example {i} (total={row['total']:.1f})",
            f"**Prompt:** {str(row['prompt'])}",
            f"**Essay:**",
            f"{str(row['essay'])}",
            f"**Scores:** {{\"content\": {row['content']}, "
            f"\"organization\": {row['organization']}, "
            f"\"language\": {row['language']}}}",
            "",
        ]

    lines += [
        "---",
        "",
        "## Scoring Instructions",
        "",
        "Given the prompt and essay below:",
        "1. Evaluate the essay against the rubric criteria above.",
        "2. Calibrate your scores against the 5 examples.",
        "3. Scores must be chosen from: [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]",
        "",
        "Output a single JSON line — nothing else:",
        "{\"content\": X, \"organization\": Y, \"language\": Z}",
    ]

    return "\n".join(lines)


def main():
    train = pd.read_csv(TRAIN_PATH, sep="\t")
    print(f"Loaded {len(train)} train essays")

    rubric_text = load_clean_rubric()
    examples = select_examples(train)

    print(f"Selected {len(examples)} examples:")
    for _, r in examples.iterrows():
        essay_len = len(str(r['essay']))
        print(f"  total={r['total']:.1f}  C={r['content']} O={r['organization']} "
              f"L={r['language']}  essay_len={essay_len} chars")

    skill_text = build_skill(rubric_text, examples)

    os.makedirs(SKILLS_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(skill_text)

    print(f"\nSkill saved to {OUTPUT_PATH}")
    print(f"Skill length: {len(skill_text)} chars, ~{len(skill_text)//4} tokens")
    print("LLM calls for induction: 0")


if __name__ == "__main__":
    main()
