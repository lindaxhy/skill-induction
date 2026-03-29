"""
Strategy E: Combined Rubric + Annotated Examples

Combines the qualitative rubric from Strategy A with scored calibration examples
(Strategy D) and LLM-generated annotations that bridge rubric vocabulary to
actual essay scores.

Structure of the output skill file:
  1. Header + dimension definitions
  2. Scoring Rubric (cleaned from few_shot_skill.md)
  3. Score Distribution (population statistics from train)
  4. Annotated Calibration Examples (15 examples with "Why:" annotations)
  5. Scoring Instructions

LLM calls: 1 (batch annotation of all 15 examples via INDUCTION_MODEL)
"""

import json
import os
import re
import sys

import pandas as pd

TRAIN_PATH  = os.path.join(os.path.dirname(__file__), "../../skill_construction_dataset/splits/train.tsv")
RUBRIC_PATH = os.path.join(os.path.dirname(__file__), "../skills/few_shot_skill.md")
SKILLS_DIR  = os.path.join(os.path.dirname(__file__), "../skills")
OUTPUT_PATH = os.path.join(SKILLS_DIR, "combined_skill.md")

N_PER_QUINTILE = 3   # 15 total examples
ESSAY_CHARS    = 600
RANDOM_STATE   = 42

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from llm_client import chat, INDUCTION_MODEL
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))


# ---------------------------------------------------------------------------
# Rubric loading and cleaning
# ---------------------------------------------------------------------------

def load_clean_rubric() -> str:
    """Load few_shot_skill.md, strip essay-number refs and Scoring Instructions section."""
    with open(RUBRIC_PATH) as f:
        rubric = f.read()
    # Drop the terminal "## Scoring Instructions" block
    rubric = rubric.split("\n## Scoring Instructions")[0].rstrip()
    # Remove parenthetical essay-number references like "(e.g., Essays #26, #28)"
    rubric = re.sub(r'\s*\(e\.g\.,\s*Essays?\s*#[\d,\s#]+\)', '', rubric)
    return rubric


# ---------------------------------------------------------------------------
# Example selection
# ---------------------------------------------------------------------------

def select_examples(df: pd.DataFrame, n_per_quintile: int) -> pd.DataFrame:
    """Select representative examples across 5 score quintiles.

    Within each quintile:
      - Prefer essays from different prompts (diversity)
      - Prefer essays where at least two dimension scores differ by ≥ 0.5
        (diagnostic spread — helps model learn dimension distinctions)
    """
    df = df.dropna(subset=["essay"]).copy()
    df["quintile"] = pd.qcut(df["total"], q=5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])

    # Score spread: max diff between any two dimension scores
    df["dim_spread"] = (df[["content", "organization", "language"]]
                        .apply(lambda r: r.max() - r.min(), axis=1))

    chosen = []
    for q in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        bucket = df[df["quintile"] == q].copy()
        k = min(n_per_quintile, len(bucket))

        # Prefer essays with dimensional spread ≥ 0.5
        spread_ok = bucket[bucket["dim_spread"] >= 0.5]
        pool = spread_ok if len(spread_ok) >= k else bucket

        # Prefer essays from different prompts
        unique_prompts = pool.drop_duplicates(subset=["prompt"])
        n_unique = min(k, len(unique_prompts))
        sample = unique_prompts.sample(n_unique, random_state=RANDOM_STATE)

        # Fill remainder if needed
        if len(sample) < k:
            remaining = pool[~pool.index.isin(sample.index)]
            extra = remaining.sample(min(k - len(sample), len(remaining)),
                                     random_state=RANDOM_STATE)
            sample = pd.concat([sample, extra])

        # If still short (pool was small), fall back to full bucket
        if len(sample) < k:
            remaining = bucket[~bucket.index.isin(sample.index)]
            extra = remaining.sample(min(k - len(sample), len(remaining)),
                                     random_state=RANDOM_STATE)
            sample = pd.concat([sample, extra])

        chosen.append(sample)

    return pd.concat(chosen).sort_values("total").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Population statistics
# ---------------------------------------------------------------------------

def compute_stats(df: pd.DataFrame) -> dict:
    """Compute score distribution statistics from the training set."""
    stats = {
        "total_mean": df["total"].mean(),
        "total_std":  df["total"].std(),
        "total_min":  df["total"].min(),
        "total_max":  df["total"].max(),
        "total_q10":  df["total"].quantile(0.10),
        "total_q25":  df["total"].quantile(0.25),
        "total_q50":  df["total"].quantile(0.50),
        "total_q75":  df["total"].quantile(0.75),
        "total_q90":  df["total"].quantile(0.90),
    }
    for dim in ["content", "organization", "language"]:
        stats[f"{dim}_mean"]      = df[dim].mean()
        stats[f"{dim}_pct_weak"]  = (df[dim] <= 2.0).mean() * 100
        stats[f"{dim}_pct_mid"]   = ((df[dim] > 2.0) & (df[dim] < 4.0)).mean() * 100
        stats[f"{dim}_pct_excel"] = (df[dim] >= 4.0).mean() * 100
    return stats


def format_stats_section(stats: dict) -> str:
    s = stats
    lines = [
        "## Score Distribution (Training Population)",
        "",
        "**Important calibration note:** Do NOT default scores to 3.0. The actual distribution:",
        "",
        f"- **Total score** (Content + Organization + Language): mean={s['total_mean']:.1f}, "
        f"range={s['total_min']:.1f}–{s['total_max']:.1f}",
        f"  - Bottom 10%: ≤ {s['total_q10']:.1f} | Bottom 25%: ≤ {s['total_q25']:.1f} | "
        f"Median: {s['total_q50']:.1f} | Top 25%: ≥ {s['total_q75']:.1f} | Top 10%: ≥ {s['total_q90']:.1f}",
        "",
        "Per-dimension breakdown:",
        f"- **Content**: mean={s['content_mean']:.2f}  "
        f"(weak ≤2.0: {s['content_pct_weak']:.0f}%,  "
        f"mid 2.5–3.5: {s['content_pct_mid']:.0f}%,  "
        f"excellent ≥4.0: {s['content_pct_excel']:.0f}%)",
        f"- **Organization**: mean={s['organization_mean']:.2f}  "
        f"(weak ≤2.0: {s['organization_pct_weak']:.0f}%,  "
        f"mid 2.5–3.5: {s['organization_pct_mid']:.0f}%,  "
        f"excellent ≥4.0: {s['organization_pct_excel']:.0f}%)",
        f"- **Language**: mean={s['language_mean']:.2f}  "
        f"(weak ≤2.0: {s['language_pct_weak']:.0f}%,  "
        f"mid 2.5–3.5: {s['language_pct_mid']:.0f}%,  "
        f"excellent ≥4.0: {s['language_pct_excel']:.0f}%)",
        "",
        "A score of 3.0 per dimension represents a **below-average** essay in this population. "
        "Most essays score 3.0–4.0 per dimension. Only ~8–9% score ≤2.0 on any dimension.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Annotation generation (single batch LLM call)
# ---------------------------------------------------------------------------

def _fallback_annotation(row) -> str:
    """Generate a minimal annotation from scores when LLM annotation is unavailable."""
    tiers = {
        "content":      ("Excellent" if row["content"] >= 4.0 else
                         "Adequate"  if row["content"] >= 2.5 else "Weak"),
        "organization": ("Excellent" if row["organization"] >= 4.0 else
                         "Adequate"  if row["organization"] >= 2.5 else "Weak"),
        "language":     ("Excellent" if row["language"] >= 4.0 else
                         "Adequate"  if row["language"] >= 2.5 else "Weak"),
    }
    return (f"Content is {tiers['content']} ({row['content']}): "
            f"organization is {tiers['organization']} ({row['organization']}): "
            f"language is {tiers['language']} ({row['language']}).")


def generate_annotations(rubric_text: str, examples: pd.DataFrame) -> dict:
    """Generate 2–3 sentence rubric-based annotations for all examples in one LLM call.

    Returns dict mapping str(1-indexed position) → annotation string.
    """
    system = (
        "You are an expert ESL essay annotator. "
        "Write a brief 2–3 sentence annotation for each scored essay explaining "
        "WHY those specific scores were assigned. "
        "Use vocabulary from the scoring rubric. "
        "Reference specific features from the essay text. "
        "Be concrete — mention specific strengths or weaknesses. "
        "Do not be generic."
    )

    # Build user prompt: rubric + numbered examples
    parts = [
        "SCORING RUBRIC:\n" + rubric_text,
        "\n\nESSAYS TO ANNOTATE:\n",
    ]
    for i, (_, row) in enumerate(examples.iterrows(), 1):
        essay_excerpt = str(row["essay"])[:ESSAY_CHARS]
        if len(str(row["essay"])) > ESSAY_CHARS:
            essay_excerpt += "..."
        parts.append(
            f"Example {i}: total={row['total']:.1f}, "
            f"content={row['content']}, organization={row['organization']}, language={row['language']}\n"
            f"Prompt: {str(row['prompt'])[:200]}\n"
            f"Essay: {essay_excerpt}"
        )

    n = len(examples)
    parts.append(
        f"\n\nOUTPUT: Return a JSON object with keys \"1\" through \"{n}\", "
        "where each value is a 2–3 sentence annotation explaining the scores. "
        "Do not output anything before or after the JSON object."
    )

    user_msg = "\n\n".join(parts)

    print(f"  Calling {INDUCTION_MODEL} for batch annotation of {n} examples...")
    try:
        response = chat(system=system, user=user_msg, model=INDUCTION_MODEL, temperature=0.3)
        # Try strict JSON parse
        try:
            annotations = json.loads(response)
            print(f"  Parsed {len(annotations)} annotations successfully.")
            return {str(k): v for k, v in annotations.items()}
        except json.JSONDecodeError:
            # Fallback: extract JSON object from response
            match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if match:
                annotations = json.loads(match.group())
                print(f"  Extracted {len(annotations)} annotations via regex fallback.")
                return {str(k): v for k, v in annotations.items()}
            print("  [warn] Could not parse annotations JSON. Using fallback annotations.")
            return {}
    except Exception as e:
        print(f"  [warn] Annotation call failed: {e}. Using fallback annotations.")
        return {}


# ---------------------------------------------------------------------------
# Skill file assembly
# ---------------------------------------------------------------------------

def build_skill(rubric_text: str, examples: pd.DataFrame,
                annotations: dict, stats: dict) -> str:
    lines = [
        "# Essay Scoring Skill (Combined Rubric + Examples)",
        "",
        "You are an expert scorer for ESL (English as a Second Language) student essays.",
        "Score each essay on three dimensions using a scale from **0.5 to 5.0** (0.5 increments).",
        "",
        "- **Content**: How well-developed and relevant the argument is; quality of support and examples.",
        "- **Organization**: How effectively the argument is structured; coherence and paragraph focus.",
        "- **Language**: Vocabulary range, grammar, spelling, and punctuation.",
        "",
        "Use the rubric criteria below to identify features, then calibrate against the scored examples.",
        "",
        "---",
        "",
        rubric_text,
        "",
        "---",
        "",
        format_stats_section(stats),
        "",
        "---",
        "",
        "## Calibration Examples",
        "",
        "These are real scored essays from the same population. "
        "Use them to anchor your numeric judgments after assessing features via the rubric.",
        "",
    ]

    for i, (_, row) in enumerate(examples.iterrows(), 1):
        essay_excerpt = str(row["essay"])[:ESSAY_CHARS]
        if len(str(row["essay"])) > ESSAY_CHARS:
            essay_excerpt += "..."

        annotation = annotations.get(str(i), "")
        if not annotation:
            annotation = _fallback_annotation(row)

        lines += [
            f"### Example {i} (total={row['total']:.1f})",
            f"**Prompt:** {str(row['prompt'])[:200]}",
            f"**Essay:** {essay_excerpt}",
            f"**Scores:** {{\"content\": {row['content']}, "
            f"\"organization\": {row['organization']}, "
            f"\"language\": {row['language']}}}",
            f"**Why:** {annotation}",
            "",
        ]

    lines += [
        "---",
        "",
        "## Scoring Instructions",
        "",
        "**Step 1 — Feature assessment:** Using the rubric criteria above, identify the key "
        "strengths and weaknesses of the essay on each dimension.",
        "",
        "**Step 2 — Numeric anchoring:** Compare your assessment against the calibration examples "
        "above to determine the right score. Recall: most essays score 3.0–4.0 per dimension; "
        "only ~9% score ≤2.0 on any dimension.",
        "",
        "Output a single JSON line — nothing else:",
        "{\"content\": X, \"organization\": Y, \"language\": Z}",
        "where each value is a float from 0.5 to 5.0 in 0.5 increments.",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    train = pd.read_csv(TRAIN_PATH, sep="\t")
    print(f"Loaded {len(train)} train essays")

    rubric_text = load_clean_rubric()
    print(f"Loaded rubric ({len(rubric_text)} chars)")

    examples = select_examples(train, N_PER_QUINTILE)
    print(f"Selected {len(examples)} examples across 5 score quintiles:")
    for _, r in examples.iterrows():
        print(f"  total={r['total']:.1f}  C={r['content']} O={r['organization']} "
              f"L={r['language']}  spread={r['dim_spread']:.1f}")

    stats = compute_stats(train)
    print(f"\nPopulation stats: total mean={stats['total_mean']:.2f}, "
          f"median={stats['total_q50']:.2f}, range={stats['total_min']:.1f}–{stats['total_max']:.1f}")

    annotations = generate_annotations(rubric_text, examples)

    skill_text = build_skill(rubric_text, examples, annotations, stats)

    os.makedirs(SKILLS_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(skill_text)

    print(f"\nSkill saved to {OUTPUT_PATH}")
    print(f"Skill length: {len(skill_text)} chars, ~{len(skill_text)//4} tokens")
    print(f"Annotations coverage: {len(annotations)}/{len(examples)} (rest use fallback)")
    print("\nStrategy E complete. LLM calls made: 1 (annotation batch)")


if __name__ == "__main__":
    main()
