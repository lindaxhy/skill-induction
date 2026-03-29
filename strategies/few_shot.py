"""Strategy A: Few-Shot Synthesis
Loads training essays, samples 30 across score tiers, and asks an LLM
to synthesize a detailed scoring rubric.
"""

import sys
import os

# Ensure the skill_induction package root is on the path
sys.path.insert(0, '/home/xhy/skill_induction')

# Load API key from .env before any LLM call
try:
    from dotenv import load_dotenv
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-dotenv', '-q'])
    from dotenv import load_dotenv

load_dotenv('/home/xhy/skill_induction/.env')

import pandas as pd
from llm_client import chat

TRAIN_TSV = '/home/xhy/skill_construction_dataset/splits/train.tsv'
SKILLS_DIR = '/home/xhy/skill_induction/skills'
OUTPUT_FILE = os.path.join(SKILLS_DIR, 'few_shot_skill.md')

SYSTEM_PROMPT = (
    "You are an expert English essay evaluator with years of experience scoring student writing.\n"
    "Your task is to analyze a set of student essays and their scores, then synthesize a detailed scoring rubric."
)


def build_user_prompt(essays_df: pd.DataFrame) -> str:
    n = len(essays_df)
    lines = [
        f"Below are {n} student essays with their scores on three dimensions.",
        "Each dimension is scored from 0.5 to 5.0 in 0.5 increments.",
        "",
        "Dimensions:",
        "- Content: How well-developed and relevant the argument is, supported with strong reasons and examples.",
        "- Organization: How effectively structured and developed the argument is; coherence, paragraph focus.",
        "- Language: Sophistication of vocabulary, grammar correctness, spelling and punctuation.",
        "",
        "[EXAMPLES]",
    ]

    for i, (_, row) in enumerate(essays_df.iterrows(), start=1):
        essay_text = str(row['essay'])[:800]  # Truncate to 800 chars
        lines += [
            f"--- Essay {i} ---",
            f"Prompt: {row['prompt']}",
            f"Essay: {essay_text}",
            f"Scores → Content: {row['content']}, Organization: {row['organization']}, Language: {row['language']}, Total: {row['total']}",
            "",
        ]

    lines += [
        "[END EXAMPLES]",
        "",
        f"Based on these {n} examples, write a detailed scoring rubric. For each dimension (Content, Organization, Language):",
        "- Describe characteristics of essays scoring 4.0–5.0 (Excellent)",
        "- Describe characteristics of essays scoring 2.5–3.5 (Adequate)",
        "- Describe characteristics of essays scoring 0.5–2.0 (Weak)",
        "",
        "Be specific and concrete — reference patterns you actually observed in the examples above.",
        "",
        "End your rubric with this exact section:",
        "## Scoring Instructions",
        "Given an essay and its prompt, evaluate it on each dimension and output a JSON object on a single line:",
        '{"content": X, "organization": Y, "language": Z}',
        "where each value is a float from 0.5 to 5.0 in 0.5 increments.",
    ]

    return "\n".join(lines)


def main():
    try:
        # 1. Load training data
        df = pd.read_csv(TRAIN_TSV, sep='\t')

        # 2. Discretize total score into 3 tiers using qcut
        df['tier'] = pd.qcut(df['total'], q=3, labels=['low', 'mid', 'high'])

        # 3. Sample 10 essays per tier (random_state=42)
        sampled = (
            df.groupby('tier', observed=True)
            .apply(lambda g: g.sample(n=10, random_state=42))
            .reset_index(drop=True)
        )

        # 4. Build LLM prompt
        user_prompt = build_user_prompt(sampled)

        # 5. Call LLM
        rubric = chat(system=SYSTEM_PROMPT, user=user_prompt)

        # 6. Save output
        os.makedirs(SKILLS_DIR, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(rubric)

        print("Strategy A complete. Skill saved.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
