"""
Evaluate only Strategy D (example-based) and E (combined) on the held-out test set.
Merges results into evaluation_results.json alongside A/B/C.
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
from llm_client import chat, EVAL_MODEL

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
TEST_PATH = os.path.join(os.path.dirname(__file__), "../skill_construction_dataset/splits/test.tsv")
DIMS = ["content", "organization", "language"]


def round_half(x: float) -> float:
    return round(float(x) * 2) / 2


def score_essay(skill_text: str, prompt: str, essay: str) -> dict | None:
    prompt = str(prompt) if pd.notna(prompt) else ""
    essay = str(essay) if pd.notna(essay) else ""
    user_msg = f"Prompt: {prompt}\n\nEssay: {essay[:800]}"
    try:
        response = chat(system=skill_text, user=user_msg, model=EVAL_MODEL, temperature=0.0)
        match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if match:
            raw = json.loads(match.group())
            return {dim: round_half(raw.get(dim, 3.0)) for dim in DIMS}
    except Exception as e:
        print(f"  [warn] scoring error: {e}")
    return None


def evaluate_skill(skill_name: str, skill_text: str, test_df: pd.DataFrame) -> dict:
    preds = {dim: [] for dim in DIMS}
    trues = {dim: [] for dim in DIMS}
    failures = 0

    print(f"\n  Scoring {len(test_df)} test essays with '{skill_name}'...")
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
        p_int = np.round(p * 2).astype(int)
        t_int = np.round(t * 2).astype(int)
        all_labels = list(range(1, 11))
        qwk = cohen_kappa_score(t_int, p_int, weights="quadratic",
                                labels=[l for l in all_labels
                                        if l in t_int or l in p_int])
        pearson_r, _ = pearsonr(t, p)
        mae = float(np.mean(np.abs(p - t)))
        metrics[dim] = {"qwk": round(qwk, 3), "pearson": round(pearson_r, 3), "mae": round(mae, 3)}

    p_total = np.array([sum(preds[d][i] for d in DIMS) for i in range(len(test_df))])
    t_total = np.array([sum(trues[d][i] for d in DIMS) for i in range(len(test_df))])
    pearson_total, _ = pearsonr(t_total, p_total)
    mae_total = float(np.mean(np.abs(p_total - t_total)))
    metrics["total"] = {
        "pearson": round(pearson_total, 3),
        "mae": round(mae_total, 3),
        "pred_mean": round(float(p_total.mean()), 3),
        "pred_std":  round(float(p_total.std()), 3),
        "true_mean": round(float(t_total.mean()), 3),
        "true_std":  round(float(t_total.std()), 3),
    }
    for dim in DIMS:
        p = np.array(preds[dim])
        t = np.array(trues[dim])
        metrics[dim]["pred_mean"] = round(float(p.mean()), 3)
        metrics[dim]["pred_std"]  = round(float(p.std()), 3)
        metrics[dim]["true_mean"] = round(float(t.mean()), 3)
        metrics[dim]["true_std"]  = round(float(t.std()), 3)

    return metrics


def main():
    test_df = pd.read_csv(TEST_PATH, sep="\t")
    print(f"Loaded {len(test_df)} test essays")

    skills = {
        "D_example":  "example_based_skill.md",
        "E_combined": "combined_skill.md",
    }

    all_metrics = {}
    for name, fname in skills.items():
        path = os.path.join(SKILLS_DIR, fname)
        with open(path) as f:
            skill_text = f.read()
        all_metrics[name] = evaluate_skill(name, skill_text, test_df)

    # Print results table
    print("\n" + "=" * 78)
    print("EVALUATION RESULTS ON TEST SET (n=228) — Strategies D & E  [Sonnet 4.6]")
    print("=" * 78)

    header = f"{'Strategy':<16} | {'Content':>10} | {'Org':>10} | {'Language':>10} | {'Total':>10}"
    subhdr = f"{'':16} | {'QWK / Pear':>10} | {'QWK / Pear':>10} | {'QWK / Pear':>10} | {'Pearson':>10}"
    print(header)
    print(subhdr)
    print("-" * 78)

    for name, m in all_metrics.items():
        c = m["content"];  o = m["organization"];  l = m["language"];  t = m["total"]
        row = (
            f"{name:<16} | "
            f"{c['qwk']:.3f}/{c['pearson']:.3f} | "
            f"{o['qwk']:.3f}/{o['pearson']:.3f} | "
            f"{l['qwk']:.3f}/{l['pearson']:.3f} | "
            f"{t['pearson']:.3f}"
        )
        print(row)

    print("=" * 78)
    print("\n--- Prediction mean / std (pred vs true) ---")
    for name, m in all_metrics.items():
        t = m["total"]
        print(f"{name:<16}  total pred={t['pred_mean']:.2f}±{t['pred_std']:.2f}  "
              f"true={t['true_mean']:.2f}±{t['true_std']:.2f}")
        for dim in DIMS:
            d = m[dim]
            print(f"  {dim:<12}  pred={d['pred_mean']:.2f}±{d['pred_std']:.2f}  "
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
