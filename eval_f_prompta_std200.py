"""
Evaluate only Strategy F on the held-out test set.
Uses GPT-4o (openai/gpt-4o) via OpenRouter with NO essay truncation.
Merges results into evaluation_results.json.
"""

import json
import os
import re
import sys
import time

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
sys.path.insert(0, os.path.dirname(__file__))
from llm_client import chat

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
TEST_PATH  = os.path.join(os.path.dirname(__file__), "../skill_construction_dataset/splits/std_200.tsv")
DIMS = ["content", "organization", "language"]

GPT4O_MODEL = "openai/gpt-4o"

# Valid score values per dimension
VALID_SCORES = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]


def snap_to_valid(x: float) -> float:
    """Snap a predicted value to the nearest valid score."""
    return min(VALID_SCORES, key=lambda v: abs(v - float(x)))


def score_essay(skill_text: str, prompt: str, essay: str) -> dict | None:
    prompt = str(prompt) if pd.notna(prompt) else ""
    essay  = str(essay)  if pd.notna(essay)  else ""
    # F skill as system prompt + Prompt A format in user message
    user_msg = (
        "Please score the essay with three rubrics: content, organization, and language.\n"
        "### Answer format: {content: Float, organization: Float, language: Float}\n"
        "Note that the float values of scores are within [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0].\n"
        "Please answer only in the above JSON format.\n"
        f"### prompt: {prompt}\n"
        f"### essay: {essay}"
    )
    try:
        response = chat(system=skill_text, user=user_msg, model=GPT4O_MODEL, temperature=0.0)
        match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if match:
            raw = json.loads(match.group())
            return {dim: snap_to_valid(raw.get(dim, 3.0)) for dim in DIMS}
    except Exception as e:
        print(f"  [warn] scoring error: {e}")
    return None


def evaluate_skill(skill_name: str, skill_text: str, test_df: pd.DataFrame) -> dict:
    preds    = {dim: [] for dim in DIMS}
    trues    = {dim: [] for dim in DIMS}
    failures = 0

    print(f"\n  Scoring {len(test_df)} test essays with '{skill_name}' ({GPT4O_MODEL})...")
    for i, row in enumerate(test_df.itertuples(), 1):
        result = score_essay(skill_text, row.prompt, row.essay)
        if result is None:
            failures += 1
            for dim in DIMS:
                preds[dim].append(3.0)
                trues[dim].append(getattr(row, dim))
        else:
            for dim in DIMS:
                preds[dim].append(result[dim])
                trues[dim].append(getattr(row, dim))

        if i % 50 == 0:
            print(f"    {i}/{len(test_df)} scored...")
        time.sleep(0.1)

    if failures:
        print(f"  [warn] {failures} scoring failures (used fallback 3.0)")

    metrics = {}
    for dim in DIMS:
        p = np.array(preds[dim])
        t = np.array(trues[dim])
        # QWK: multiply by 2 to convert 0.5-step scores to integers (1.0→2, 1.5→3, ..., 5.0→10)
        p_int = np.round(p * 2).astype(int)
        t_int = np.round(t * 2).astype(int)
        all_labels = list(range(2, 11))  # 2..10 (1.0..5.0)
        qwk = cohen_kappa_score(t_int, p_int, weights="quadratic",
                                labels=[l for l in all_labels
                                        if l in t_int or l in p_int])
        pearson_r, _ = pearsonr(t, p)
        mae = float(np.mean(np.abs(p - t)))
        metrics[dim] = {
            "qwk":       round(qwk, 3),
            "pearson":   round(pearson_r, 3),
            "mae":       round(mae, 3),
            "pred_mean": round(float(p.mean()), 3),
            "pred_std":  round(float(p.std()), 3),
            "true_mean": round(float(t.mean()), 3),
            "true_std":  round(float(t.std()), 3),
        }

    p_total = np.array([sum(preds[d][i] for d in DIMS) for i in range(len(test_df))])
    t_total = np.array([sum(trues[d][i] for d in DIMS) for i in range(len(test_df))])
    pearson_total, _ = pearsonr(t_total, p_total)
    mae_total = float(np.mean(np.abs(p_total - t_total)))
    metrics["total"] = {
        "pearson":   round(pearson_total, 3),
        "mae":       round(mae_total, 3),
        "pred_mean": round(float(p_total.mean()), 3),
        "pred_std":  round(float(p_total.std()), 3),
        "true_mean": round(float(t_total.mean()), 3),
        "true_std":  round(float(t_total.std()), 3),
    }
    return metrics


def main():
    test_df = pd.read_csv(TEST_PATH, sep="\t")
    print(f"Loaded {len(test_df)} test essays")

    skill_path = os.path.join(SKILLS_DIR, "strategy_f_skill.md")
    with open(skill_path) as f:
        skill_text = f.read()

    metrics = evaluate_skill("F_skill_promptA_std200", skill_text, test_df)
    all_metrics = {"F_skill_promptA_std200": metrics}

    # Print results
    print("\n" + "=" * 78)
    print("EVALUATION RESULTS — Strategy F (GPT-4o, no truncation, n=200 (DREsS_Std))")
    print("=" * 78)
    header = f"{'Strategy':<18} | {'Content':>10} | {'Org':>10} | {'Language':>10} | {'Total':>10}"
    subhdr = f"{'':18} | {'QWK / Pear':>10} | {'QWK / Pear':>10} | {'QWK / Pear':>10} | {'Pearson':>10}"
    print(header)
    print(subhdr)
    print("-" * 78)
    m = metrics
    c = m["content"]; o = m["organization"]; l = m["language"]; t = m["total"]
    print(f"{'F_rubric_5shot':<18} | "
          f"{c['qwk']:.3f}/{c['pearson']:.3f} | "
          f"{o['qwk']:.3f}/{o['pearson']:.3f} | "
          f"{l['qwk']:.3f}/{l['pearson']:.3f} | "
          f"{t['pearson']:.3f}")
    print("=" * 78)
    print("\n--- Prediction mean / std (pred vs true) ---")
    print(f"  total   pred={t['pred_mean']:.2f}±{t['pred_std']:.2f}  "
          f"true={t['true_mean']:.2f}±{t['true_std']:.2f}")
    for dim in DIMS:
        d = m[dim]
        print(f"  {dim:<12} pred={d['pred_mean']:.2f}±{d['pred_std']:.2f}  "
              f"true={d['true_mean']:.2f}±{d['true_std']:.2f}")

    # Merge into evaluation_results.json
    out_path = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    existing = {}
    if os.path.exists(out_path):
        with open(out_path) as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                pass
    existing.update(all_metrics)
    with open(out_path, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"\nResults merged into {out_path}")


if __name__ == "__main__":
    main()
