"""Strategy B: Contrastive Pair Synthesis for essay scoring skill induction."""

import sys
import os

# Ensure skill_induction is importable
sys.path.insert(0, '/home/xhy/skill_induction')

# Load environment variables
try:
    import dotenv
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-dotenv', '-q'])

from dotenv import load_dotenv
load_dotenv('/home/xhy/skill_induction/.env')

import pandas as pd
from llm_client import chat

TRAIN_PATH = '/home/xhy/skill_construction_dataset/splits/train.tsv'
SKILLS_DIR = '/home/xhy/skill_induction/skills'
OUTPUT_PATH = os.path.join(SKILLS_DIR, 'contrastive_skill.md')

DIMENSIONS = ['content', 'organization', 'language']


def format_essays(essays_df: pd.DataFrame, dim: str) -> str:
    """Format essays for inclusion in prompt, truncating to 800 chars."""
    parts = []
    for i, (_, row) in enumerate(essays_df.iterrows(), 1):
        essay_text = str(row['essay'])[:800]
        score = row[dim]
        parts.append(f"Essay {i} (score: {score}):\n{essay_text}")
    return "\n\n---\n\n".join(parts)


def analyze_dimension(df: pd.DataFrame, dim: str) -> str:
    """Sample top/bottom essays for a dimension and get LLM analysis."""
    high = df[df[dim] >= 4.0].sample(n=min(5, len(df[df[dim] >= 4.0])), random_state=42)
    low = df[df[dim] <= 2.0].sample(n=min(5, len(df[df[dim] <= 2.0])), random_state=42)

    high_essays_str = format_essays(high, dim)
    low_essays_str = format_essays(low, dim)

    system = (
        "You are an expert English essay evaluator. You will analyze contrasting examples "
        "to identify what distinguishes high-quality from low-quality writing on a specific dimension."
    )

    user = f"""I need you to analyze what distinguishes high-scoring from low-scoring student essays on the "{dim}" dimension.

Dimension definition:
- Content: How well-developed and relevant the argument is, supported with strong reasons and examples.
- Organization: How effectively structured and developed the argument is; coherence, paragraph focus.
- Language: Sophistication of vocabulary, grammar correctness, spelling and punctuation.

HIGH-SCORING ESSAYS (score ≥ 4.0 on {dim}):
{high_essays_str}

LOW-SCORING ESSAYS (score ≤ 2.0 on {dim}):
{low_essays_str}

Based on these contrasting examples, write detailed scoring criteria for the "{dim}" dimension:
1. What specific features distinguish high-scoring (4.0–5.0) essays?
2. What specific features characterize mid-range (2.5–3.5) essays?
3. What specific features characterize low-scoring (0.5–2.0) essays?

Be concrete and reference patterns you observed in the examples above."""

    print(f"  Calling LLM for dimension: {dim}...")
    return chat(system=system, user=user)


def combine_rubrics(content_criteria: str, organization_criteria: str, language_criteria: str) -> str:
    """Combine the three dimension rubrics into a unified skill document."""
    system = (
        "You are an expert rubric writer synthesizing scoring criteria into a unified skill document."
    )

    user = f"""I have developed scoring criteria for three dimensions of essay evaluation. Please combine them into a single, well-formatted scoring rubric document.

CONTENT CRITERIA:
{content_criteria}

ORGANIZATION CRITERIA:
{organization_criteria}

LANGUAGE CRITERIA:
{language_criteria}

Format the output as a Markdown document with:
- A title: "# Essay Scoring Rubric"
- One section per dimension with clear sub-sections for score ranges
- End with this exact section:

## Scoring Instructions
Given an essay and its prompt, evaluate it on each dimension and output a JSON object on a single line:
{{"content": X, "organization": Y, "language": Z}}
where each value is a float from 0.5 to 5.0 in 0.5 increments."""

    print("  Calling LLM to combine rubrics...")
    return chat(system=system, user=user)


def main():
    try:
        # Ensure skills directory exists
        os.makedirs(SKILLS_DIR, exist_ok=True)

        # Load training data
        print("Loading training data...")
        df = pd.read_csv(TRAIN_PATH, sep='\t')
        print(f"  Loaded {len(df)} training examples.")

        # Analyze each dimension
        criteria = {}
        for dim in DIMENSIONS:
            print(f"Analyzing dimension: {dim}")
            criteria[dim] = analyze_dimension(df, dim)
            print(f"  Done with {dim}.")

        # Combine into unified rubric
        print("Combining rubrics into unified skill document...")
        combined = combine_rubrics(
            content_criteria=criteria['content'],
            organization_criteria=criteria['organization'],
            language_criteria=criteria['language'],
        )

        # Save to file
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write(combined)

        print(f"Strategy B complete. Skill saved.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
