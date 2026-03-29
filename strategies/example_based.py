"""
Strategy D: Example-Based Skill

Instead of inducing a natural-language rubric, this strategy selects
representative scored essays from the training set and embeds them
directly into the skill file as calibration anchors.

No LLM call is needed for induction — the skill is purely constructed
from data. The LLM only reads the examples at scoring time.
"""

import os
import sys
import pandas as pd

TRAIN_PATH = os.path.join(os.path.dirname(__file__), "../../skill_construction_dataset/splits/train.tsv")
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "../skills")
N_PER_BUCKET = 2   # examples per score quintile = 10 total
ESSAY_CHARS  = 600  # max chars per essay excerpt
RANDOM_STATE = 42


def select_examples(df: pd.DataFrame, n_per_bucket: int) -> pd.DataFrame:
    """Select representative examples spread across 5 score quintiles."""
    df = df.dropna(subset=["essay"]).copy()
    df["quintile"] = pd.qcut(df["total"], q=5, labels=["Q1","Q2","Q3","Q4","Q5"])

    chosen = []
    for q in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        bucket = df[df["quintile"] == q]
        k = min(n_per_bucket, len(bucket))
        # Prefer essays from different prompts for diversity
        sample = (bucket.drop_duplicates(subset=["prompt"])
                        .sample(min(k, len(bucket.drop_duplicates(subset=["prompt"]))),
                                random_state=RANDOM_STATE))
        if len(sample) < k:
            extra = bucket[~bucket.index.isin(sample.index)].sample(
                k - len(sample), random_state=RANDOM_STATE)
            sample = pd.concat([sample, extra])
        chosen.append(sample)

    return pd.concat(chosen).sort_values("total").reset_index(drop=True)


def build_skill(examples: pd.DataFrame) -> str:
    """Build the skill Markdown from selected examples."""
    lines = [
        "# Essay Scoring Skill (Example-Based)",
        "",
        "You are an expert scorer for ESL (English as a Second Language) student essays.",
        "Score each essay on three dimensions using a scale from **0.5 to 5.0** (0.5 increments).",
        "",
        "- **Content**: How well-developed and relevant the argument is; quality of support and examples.",
        "- **Organization**: How effectively the argument is structured; coherence and paragraph focus.",
        "- **Language**: Vocabulary range, grammar, spelling, and punctuation.",
        "",
        "## Calibration Examples",
        "",
        "These are real scored essays from the same population. Use them to calibrate your scores.",
        "",
    ]

    for i, (_, row) in enumerate(examples.iterrows(), 1):
        essay_excerpt = str(row["essay"])[:ESSAY_CHARS]
        if len(str(row["essay"])) > ESSAY_CHARS:
            essay_excerpt += "..."
        label = f"(total={row['total']:.1f})"
        lines += [
            f"### Example {i} {label}",
            f"**Prompt:** {str(row['prompt'])[:200]}",
            f"**Essay:** {essay_excerpt}",
            f"**Scores:** {{\"content\": {row['content']}, \"organization\": {row['organization']}, \"language\": {row['language']}}}",
            "",
        ]

    lines += [
        "## Scoring Instructions",
        "",
        "Compare the new essay against the examples above to calibrate your judgment.",
        "Output a single JSON line — nothing else:",
        "{\"content\": X, \"organization\": Y, \"language\": Z}",
        "where each value is a float from 0.5 to 5.0 in 0.5 increments.",
    ]

    return "\n".join(lines)


def main():
    train = pd.read_csv(TRAIN_PATH, sep="\t")
    print(f"Loaded {len(train)} train essays")

    examples = select_examples(train, N_PER_BUCKET)
    print(f"Selected {len(examples)} examples across 5 score quintiles:")
    for _, r in examples.iterrows():
        print(f"  total={r['total']:.1f}  C={r['content']} O={r['organization']} L={r['language']}")

    skill_text = build_skill(examples)

    os.makedirs(SKILLS_DIR, exist_ok=True)
    out_path = os.path.join(SKILLS_DIR, "example_based_skill.md")
    with open(out_path, "w") as f:
        f.write(skill_text)

    print(f"\nSkill saved to {out_path}")
    print(f"Skill length: {len(skill_text)} chars, ~{len(skill_text)//4} tokens")
    print("\nStrategy D complete. No LLM calls needed for induction.")


if __name__ == "__main__":
    main()
