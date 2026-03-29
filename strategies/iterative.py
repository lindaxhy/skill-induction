"""Strategy C: Iterative Refinement
Phase 1: Bootstrap via contrastive synthesis (Strategy B internally).
Phase 2: Iteratively refine the rubric using validation errors.
"""

import sys
import os
import json
import re

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
from llm_client import chat, INDUCTION_MODEL, EVAL_MODEL

TRAIN_TSV = '/home/xhy/skill_construction_dataset/splits/train.tsv'
VAL_TSV = '/home/xhy/skill_construction_dataset/splits/val.tsv'
SKILLS_DIR = '/home/xhy/skill_induction/skills'
OUTPUT_FILE = os.path.join(SKILLS_DIR, 'iterative_skill.md')

MAX_ROUNDS = 3
MIN_IMPROVEMENT = 0.05
VAL_SAMPLE_SIZE = 50


# ---------------------------------------------------------------------------
# Phase 1: Bootstrap (Strategy B contrastive synthesis)
# ---------------------------------------------------------------------------

DIMENSIONS = ['content', 'organization', 'language']

DIM_DESCRIPTIONS = {
    'content': (
        "Content: How well-developed and relevant the argument is, "
        "supported with strong reasons and examples."
    ),
    'organization': (
        "Organization: How effectively structured and developed the argument is; "
        "coherence, paragraph focus."
    ),
    'language': (
        "Language: Sophistication of vocabulary, grammar correctness, "
        "spelling and punctuation."
    ),
}


def build_contrastive_prompt(dim: str, top_essays: pd.DataFrame, bottom_essays: pd.DataFrame) -> str:
    lines = [
        f"You are an expert English essay evaluator. Your task is to analyze "
        f"HIGH-scoring and LOW-scoring essays on the '{dim}' dimension, then write "
        f"a detailed rubric section for that dimension.",
        "",
        DIM_DESCRIPTIONS[dim],
        "",
        "=== HIGH-SCORING ESSAYS (score >= 4.0) ===",
    ]
    for i, (_, row) in enumerate(top_essays.iterrows(), start=1):
        lines += [
            f"--- High Essay {i} ---",
            f"Prompt: {row['prompt']}",
            f"Essay: {str(row['essay'])[:800]}",
            f"Score ({dim}): {row[dim]}",
            "",
        ]

    lines += ["=== LOW-SCORING ESSAYS (score <= 2.0) ==="]
    for i, (_, row) in enumerate(bottom_essays.iterrows(), start=1):
        lines += [
            f"--- Low Essay {i} ---",
            f"Prompt: {row['prompt']}",
            f"Essay: {str(row['essay'])[:800]}",
            f"Score ({dim}): {row[dim]}",
            "",
        ]

    lines += [
        "Based on these contrasting examples, write a rubric section for the "
        f"'{dim}' dimension that:",
        "- Describes characteristics of essays scoring 4.0–5.0 (Excellent)",
        "- Describes characteristics of essays scoring 2.5–3.5 (Adequate)",
        "- Describes characteristics of essays scoring 0.5–2.0 (Weak)",
        "",
        "Be specific and concrete — reference patterns you actually observed in the examples above.",
    ]
    return "\n".join(lines)


def bootstrap_skill(df_train: pd.DataFrame) -> str:
    """Run Strategy B contrastive synthesis to produce an initial skill draft."""
    dim_rubrics = {}

    for dim in DIMENSIONS:
        top = df_train[df_train[dim] >= 4.0].sample(
            n=min(5, len(df_train[df_train[dim] >= 4.0])), random_state=42
        )
        bottom = df_train[df_train[dim] <= 2.0].sample(
            n=min(5, len(df_train[df_train[dim] <= 2.0])), random_state=42
        )

        user_prompt = build_contrastive_prompt(dim, top, bottom)
        system_prompt = (
            "You are an expert rubric writer. Write clear, detailed, and actionable "
            "scoring criteria based on the essay examples provided."
        )
        response = chat(system=system_prompt, user=user_prompt, model=INDUCTION_MODEL)
        dim_rubrics[dim] = response
        print(f"  Bootstrap: '{dim}' rubric generated.")

    # Combine into unified rubric
    combine_system = (
        "You are an expert rubric writer. Combine three separate dimension rubrics "
        "into a single cohesive scoring guide for English essay evaluation."
    )
    combine_user = (
        "Below are three separate rubric sections for scoring student essays. "
        "Combine them into a single, well-organized scoring rubric.\n\n"
        "=== CONTENT RUBRIC ===\n"
        f"{dim_rubrics['content']}\n\n"
        "=== ORGANIZATION RUBRIC ===\n"
        f"{dim_rubrics['organization']}\n\n"
        "=== LANGUAGE RUBRIC ===\n"
        f"{dim_rubrics['language']}\n\n"
        "Create a unified rubric that integrates all three dimensions clearly. "
        "End with this exact section:\n"
        "## Scoring Instructions\n"
        "Given an essay and its prompt, evaluate it on each dimension and output a JSON object on a single line:\n"
        '{"content": X, "organization": Y, "language": Z}\n'
        "where each value is a float from 0.5 to 5.0 in 0.5 increments."
    )
    unified = chat(system=combine_system, user=combine_user, model=INDUCTION_MODEL)
    print("  Bootstrap: unified rubric created.")
    return unified


# ---------------------------------------------------------------------------
# Phase 2: Scoring helper and refinement
# ---------------------------------------------------------------------------

def score_essay(skill_text: str, prompt: str, essay: str) -> dict:
    user_msg = f"Prompt: {prompt}\n\nEssay: {essay[:800]}"
    response = chat(system=skill_text, user=user_msg, model=EVAL_MODEL, temperature=0.0)
    match = re.search(r'\{[^}]+\}', response)
    if match:
        try:
            scores = json.loads(match.group())
            for k in ['content', 'organization', 'language']:
                scores[k] = round(float(scores[k]) * 2) / 2
            return scores
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    return {'content': 3.0, 'organization': 3.0, 'language': 3.0}


def evaluate_on_val(skill_text: str, df_val: pd.DataFrame, round_num: int) -> tuple:
    """Score a sample of val essays and return (mae_per_dim, errors_df, sample_df)."""
    sample = df_val.sample(n=min(VAL_SAMPLE_SIZE, len(df_val)), random_state=42 + round_num)

    pred_content = []
    pred_org = []
    pred_lang = []

    for _, row in sample.iterrows():
        scores = score_essay(skill_text, str(row['prompt']), str(row['essay']))
        pred_content.append(scores.get('content', 3.0))
        pred_org.append(scores.get('organization', 3.0))
        pred_lang.append(scores.get('language', 3.0))

    sample = sample.copy()
    sample['pred_content'] = pred_content
    sample['pred_org'] = pred_org
    sample['pred_lang'] = pred_lang

    sample['abs_err_content'] = (sample['pred_content'] - sample['content']).abs()
    sample['abs_err_org'] = (sample['pred_org'] - sample['organization']).abs()
    sample['abs_err_lang'] = (sample['pred_lang'] - sample['language']).abs()
    sample['total_abs_err'] = (
        sample['abs_err_content'] + sample['abs_err_org'] + sample['abs_err_lang']
    )

    mae = {
        'content': sample['abs_err_content'].mean(),
        'organization': sample['abs_err_org'].mean(),
        'language': sample['abs_err_lang'].mean(),
        'total': sample['total_abs_err'].mean() / 3,  # mean per dimension
    }

    # Top-5 worst cases
    worst = sample.nlargest(5, 'total_abs_err')

    return mae, worst, sample


def build_refinement_prompt(current_skill: str, n_val: int, worst_df: pd.DataFrame) -> str:
    error_cases_lines = []
    for i, (_, row) in enumerate(worst_df.iterrows(), start=1):
        essay_preview = str(row['essay'])[:600]
        error_cases_lines += [
            f"--- Error Case {i} ---",
            f"Prompt: {row['prompt']}",
            f"Essay (first 600 chars): {essay_preview}",
            f"True scores  → content={row['content']}, organization={row['organization']}, language={row['language']}",
            f"Pred scores  → content={row['pred_content']}, organization={row['pred_org']}, language={row['pred_lang']}",
            f"Total error: {row['total_abs_err']:.2f}",
            "",
        ]
    error_cases = "\n".join(error_cases_lines)

    user = (
        f"Here is the current scoring rubric:\n{current_skill}\n\n"
        f"I tested this rubric on {n_val} validation essays and found these 5 cases where predictions were most wrong:\n\n"
        f"{error_cases}"
        "Please revise the rubric to better handle these cases. Keep the overall structure but improve the criteria that led to these errors.\n"
        "End the revised rubric with:\n"
        "## Scoring Instructions\n"
        "Given an essay and its prompt, evaluate it on each dimension and output a JSON object on a single line:\n"
        '{"content": X, "organization": Y, "language": Z}\n'
        "where each value is a float from 0.5 to 5.0 in 0.5 increments."
    )
    return user


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        # Load data
        df_train = pd.read_csv(TRAIN_TSV, sep='\t')
        df_val = pd.read_csv(VAL_TSV, sep='\t')
        print(f"Loaded {len(df_train)} train essays, {len(df_val)} val essays.")

        # Phase 1: Bootstrap
        print("\n=== Phase 1: Bootstrap (contrastive synthesis) ===")
        current_skill = bootstrap_skill(df_train)
        print("Bootstrap complete.")

        # Phase 2: Iterative refinement
        print("\n=== Phase 2: Iterative Refinement ===")

        # Evaluate initial skill
        print("Evaluating initial (bootstrap) skill on validation set...")
        mae, worst, _ = evaluate_on_val(current_skill, df_val, round_num=0)
        prev_total_mae = mae['total']
        print(
            f"Initial val MAE → content={mae['content']:.3f}, "
            f"organization={mae['organization']:.3f}, "
            f"language={mae['language']:.3f}, "
            f"avg={prev_total_mae:.3f}"
        )

        for round_num in range(1, MAX_ROUNDS + 1):
            print(f"\n--- Round {round_num} ---")

            # Build refinement prompt
            refinement_system = (
                "You are an expert rubric writer improving a scoring rubric based on prediction errors."
            )
            refinement_user = build_refinement_prompt(
                current_skill, VAL_SAMPLE_SIZE, worst
            )

            # Refine the skill
            refined_skill = chat(
                system=refinement_system,
                user=refinement_user,
                model=INDUCTION_MODEL,
            )

            # Evaluate refined skill
            mae_new, worst_new, _ = evaluate_on_val(refined_skill, df_val, round_num=round_num)
            new_total_mae = mae_new['total']

            print(
                f"Round {round_num}: val MAE before={prev_total_mae:.3f}, after={new_total_mae:.3f}"
            )
            print(
                f"  Per-dim → content={mae_new['content']:.3f}, "
                f"organization={mae_new['organization']:.3f}, "
                f"language={mae_new['language']:.3f}"
            )

            # Accept new skill
            current_skill = refined_skill
            worst = worst_new

            improvement = prev_total_mae - new_total_mae
            if improvement < MIN_IMPROVEMENT:
                print(
                    f"  Improvement {improvement:.3f} < {MIN_IMPROVEMENT} threshold. Stopping early."
                )
                break

            prev_total_mae = new_total_mae

        # Save final skill
        os.makedirs(SKILLS_DIR, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(current_skill)

        print("\nStrategy C complete. Skill saved.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
