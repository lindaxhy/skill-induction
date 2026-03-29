"""
Evaluate GPT-4o (latest) on 200 essays from DREsS_Std using Paper's Prompt A.
True scores are continuous (standardized), so primary metric is Pearson + MAE.
QWK computed by rounding both pred and true to nearest 0.5.
"""

import json, os, re, sys, time
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
sys.path.insert(0, os.path.dirname(__file__))
from llm_client import get_client

TEST_PATH = os.path.join(os.path.dirname(__file__),
    "../skill_construction_dataset/splits/std_200.tsv")
DIMS = ["content", "organization", "language"]
GPT4O_MODEL = "openai/gpt-4o"
VALID_SCORES = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]


def snap_to_valid(x):
    return min(VALID_SCORES, key=lambda v: abs(v - float(x)))


def score_essay(prompt, essay):
    prompt = str(prompt) if pd.notna(prompt) else ""
    essay  = str(essay)  if pd.notna(essay)  else ""
    user_msg = (
        "Please score the essay with three rubrics: content, organization, and language.\n"
        "### Answer format: {content: Float, organization: Float, language: Float}\n"
        "Note that the float values of scores are within [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0].\n"
        "Please answer only in the above JSON format.\n"
        f"### prompt: {prompt}\n"
        f"### essay: {essay}"
    )
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=GPT4O_MODEL, temperature=0.0,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = response.choices[0].message.content
        match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if match:
            blob = match.group()
            try:
                raw = json.loads(blob)
            except json.JSONDecodeError:
                raw = {}
                for dim in DIMS:
                    m2 = re.search(rf'{dim}\s*:\s*([0-9.]+)', blob)
                    if m2:
                        raw[dim] = float(m2.group(1))
            return {dim: snap_to_valid(raw.get(dim, 3.0)) for dim in DIMS}
    except Exception as e:
        print(f"  [warn] {e}")
    return None


def round_to_half(x):
    """Round to nearest 0.5 for QWK, clipped to [1.0, 5.0]."""
    return float(np.clip(round(float(x) * 2) / 2, 1.0, 5.0))


def main():
    df = pd.read_csv(TEST_PATH, sep="\t")
    print(f"Loaded {len(df)} essays from DREsS_Std (stratified sample)")
    print(f"Model: {GPT4O_MODEL} | Prompt A (zero-shot) | No system prompt")
    print(f"Sources: { {s: int((df['source']==s).sum()) for s in df['source'].unique()} }")

    preds = {dim: [] for dim in DIMS}
    trues = {dim: [] for dim in DIMS}
    failures = 0

    for i, row in enumerate(df.itertuples(), 1):
        result = score_essay(row.prompt, row.essay)
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
            print(f"  {i}/{len(df)} scored...")
        time.sleep(0.1)

    if failures:
        print(f"  [warn] {failures} failures (fallback 3.0)")

    metrics = {}
    for dim in DIMS:
        p = np.array(preds[dim])
        t = np.array(trues[dim])
        # QWK: round both to nearest 0.5 → ×2 for integer labels
        p_int = np.round(p * 2).astype(int)
        t_int = np.array([round(round_to_half(v) * 2) for v in t])
        all_labels = list(range(2, 11))
        obs = [l for l in all_labels if l in t_int or l in p_int]
        qwk = cohen_kappa_score(t_int, p_int, weights="quadratic", labels=obs)
        pearson_r, _ = pearsonr(t, p)
        mae = float(np.mean(np.abs(p - t)))
        metrics[dim] = {
            "qwk": round(qwk, 3), "pearson": round(pearson_r, 3), "mae": round(mae, 3),
            "pred_mean": round(float(p.mean()), 3), "pred_std": round(float(p.std()), 3),
            "true_mean": round(float(t.mean()), 3), "true_std": round(float(t.std()), 3),
        }

    p_tot = np.array([sum(preds[d][i] for d in DIMS) for i in range(len(df))])
    t_tot = np.array([sum(trues[d][i] for d in DIMS) for i in range(len(df))])
    pearson_tot, _ = pearsonr(t_tot, p_tot)
    metrics["total"] = {
        "pearson": round(pearson_tot, 3), "mae": round(float(np.mean(np.abs(p_tot - t_tot))), 3),
        "pred_mean": round(float(p_tot.mean()), 3), "pred_std": round(float(p_tot.std()), 3),
        "true_mean": round(float(t_tot.mean()), 3), "true_std": round(float(t_tot.std()), 3),
    }

    print("\n" + "=" * 72)
    print("GPT-4o Zero-shot on DREsS_Std (n=200, stratified)")
    print("Note: true scores are continuous; QWK rounds both to nearest 0.5")
    print("=" * 72)
    m = metrics
    c, o, l, t = m["content"], m["organization"], m["language"], m["total"]
    print(f"{'std_200':<12} | {c['qwk']:.3f}/{c['pearson']:.3f} | "
          f"{o['qwk']:.3f}/{o['pearson']:.3f} | "
          f"{l['qwk']:.3f}/{l['pearson']:.3f} | {t['pearson']:.3f}")
    print("=" * 72)
    print("\n--- mean / std ---")
    print(f"  total  pred={t['pred_mean']:.2f}±{t['pred_std']:.2f}  true={t['true_mean']:.2f}±{t['true_std']:.2f}")
    for dim in DIMS:
        d = m[dim]
        print(f"  {dim:<12} pred={d['pred_mean']:.2f}±{d['pred_std']:.2f}  true={d['true_mean']:.2f}±{d['true_std']:.2f}")

    out_path = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    existing = {}
    if os.path.exists(out_path):
        with open(out_path) as f:
            try: existing = json.load(f)
            except: pass
    existing["std_200_gpt4o"] = metrics
    with open(out_path, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"\nSaved to evaluation_results.json")


if __name__ == "__main__":
    main()
