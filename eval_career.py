"""
Evaluate resume quality scoring on CareerCorpus test set (n=61).
Configs:
  1. zero_shot: no system prompt
  2. skill_based: career_scoring_skill.md as system prompt
Metrics: Pearson r, MAE, QWK (binned to 0.1 steps → integers 0–10)
"""

import json
import os
import re
import sys
import time

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.metrics import cohen_kappa_score
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
sys.path.insert(0, os.path.dirname(__file__))

TEST_PATH  = os.path.join(os.path.dirname(__file__),
    "../skill_construction_dataset/splits/career_test.tsv")
SKILL_PATH = os.path.join(os.path.dirname(__file__),
    "skills/career_scoring_skill.md")

GPT4O_MODEL     = "openai/gpt-4o"
REQUEST_TIMEOUT = 60
MAX_RETRIES     = 2


def get_client():
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        timeout=REQUEST_TIMEOUT,
    )


def chat(system: str, user: str) -> str:
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    resp = client.chat.completions.create(
        model=GPT4O_MODEL, temperature=0.0, messages=messages)
    return resp.choices[0].message.content


def format_resume(row) -> str:
    return (
        f"Domain: {row.Domain}\n"
        f"Job Type: {row.Job_type}\n\n"
        f"Education:\n{row.Education}\n\n"
        f"Skills and Achievements:\n{getattr(row, 'Skills and Achievements', '')}\n\n"
        f"Experience:\n{row.Experience}"
    )


def make_user_msg(row) -> str:
    return (
        "Please score the resume quality on a 0–1 continuous scale.\n"
        '### Answer format: {"score": 0.XX}\n'
        "Note: the score should be a float between 0.0 and 1.0 (two decimal places).\n"
        "Please answer ONLY in the above JSON format.\n"
        f"### resume:\n{format_resume(row)}"
    )


def predict_one(system: str, row) -> float | None:
    user_msg = make_user_msg(row)
    for attempt in range(MAX_RETRIES):
        try:
            response = chat(system=system, user=user_msg)
            match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if match:
                blob = match.group()
                try:
                    raw = json.loads(blob)
                    score = float(raw.get("score", -1))
                except (json.JSONDecodeError, ValueError):
                    m2 = re.search(r'score\s*[:\s]+([0-9.]+)', blob)
                    score = float(m2.group(1)) if m2 else -1
                if 0.0 <= score <= 1.0:
                    return score
            # Fallback: any float in response
            m3 = re.search(r'\b(0\.[0-9]+|1\.0+)\b', response)
            if m3:
                s = float(m3.group(1))
                if 0.0 <= s <= 1.0:
                    return s
        except Exception as e:
            print(f"  [warn] attempt {attempt+1}/{MAX_RETRIES}: {e}", flush=True)
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)
    return None


def to_bin(x: float) -> int:
    """Convert 0–1 score to integer bin (0–10) for QWK."""
    return int(min(10, max(0, round(x * 10))))


def evaluate(config_name: str, system: str, test_df: pd.DataFrame) -> dict:
    preds, trues = [], []
    failures = 0

    print(f"\n  Scoring {len(test_df)} resumes — {config_name}...", flush=True)
    for i, row in enumerate(test_df.itertuples(), 1):
        pred = predict_one(system, row)
        true = float(row.score)
        if pred is None:
            failures += 1
            pred = 0.75   # fallback = training mean
        preds.append(pred)
        trues.append(true)

        if i % 20 == 0:
            p = np.array(preds); t = np.array(trues)
            r, _ = pearsonr(t, p) if len(set(p)) > 1 else (0, 0)
            mae = np.mean(np.abs(p - t))
            print(f"    {i}/{len(test_df)}  pearson={r:.3f}  mae={mae:.3f}  "
                  f"pred_mean={p.mean():.3f}", flush=True)
        time.sleep(0.15)

    if failures:
        print(f"  [warn] {failures} failures (fallback=0.75)")

    p = np.array(preds)
    t = np.array(trues)

    pearson_r, _ = pearsonr(t, p)
    mae = float(np.mean(np.abs(p - t)))

    # QWK on 0–10 bins
    p_bin = np.array([to_bin(x) for x in preds])
    t_bin = np.array([to_bin(x) for x in trues])
    all_labels = list(range(0, 11))
    obs_labels = [l for l in all_labels if l in t_bin or l in p_bin]
    qwk = cohen_kappa_score(t_bin, p_bin, weights="quadratic", labels=obs_labels)

    # Per-domain
    per_domain = {}
    for domain in test_df['Domain'].unique():
        idx = [i for i, r in enumerate(test_df['Domain'].tolist()) if r == domain]
        pt = [preds[i] for i in idx]; tt = [trues[i] for i in idx]
        if len(set(pt)) > 1:
            r_d, _ = pearsonr(tt, pt)
        else:
            r_d = 0.0
        per_domain[domain] = {
            "n": len(idx),
            "pearson": round(r_d, 3),
            "mae":     round(float(np.mean(np.abs(np.array(pt)-np.array(tt)))), 3),
            "pred_mean": round(float(np.mean(pt)), 3),
            "true_mean": round(float(np.mean(tt)), 3),
        }

    return {
        "pearson":    round(float(pearson_r), 3),
        "mae":        round(mae, 3),
        "qwk":        round(float(qwk), 3),
        "pred_mean":  round(float(p.mean()), 3),
        "pred_std":   round(float(p.std()), 3),
        "true_mean":  round(float(t.mean()), 3),
        "true_std":   round(float(t.std()), 3),
        "failures":   failures,
        "per_domain": per_domain,
    }


def main():
    test_df = pd.read_csv(TEST_PATH, sep="\t")
    print(f"Loaded {len(test_df)} test resumes")
    print(f"Score: mean={test_df['score'].mean():.3f}  std={test_df['score'].std():.3f}")
    print(f"Domains: {test_df['Domain'].value_counts().to_dict()}")

    with open(SKILL_PATH) as f:
        skill_text = f.read()

    configs = {"zero_shot": "", "skill_based": skill_text}
    all_metrics = {}
    for name, system in configs.items():
        all_metrics[name] = evaluate(name, system, test_df)

    print("\n" + "=" * 68)
    print("CAREER CORPUS QUALITY SCORING — GPT-4o (n=61)")
    print(f"True: mean={test_df['score'].mean():.3f} ± {test_df['score'].std():.3f}")
    print("=" * 68)
    print(f"{'Config':<14} | {'Pearson':>7} | {'QWK':>6} | {'MAE':>6} | pred mean±std")
    print("-" * 68)
    for name, m in all_metrics.items():
        print(f"{name:<14} | {m['pearson']:>7.3f} | {m['qwk']:>6.3f} | {m['mae']:>6.3f} | "
              f"{m['pred_mean']:.3f}±{m['pred_std']:.3f}")
    print("=" * 68)

    print("\n--- Per-domain (skill_based) ---")
    zm = all_metrics.get("zero_shot", {}).get("per_domain", {})
    sm = all_metrics.get("skill_based", {}).get("per_domain", {})
    print(f"{'Domain':<22} | {'n':>3} | Zero Pear | Skill Pear | pred→true")
    print("-" * 65)
    for domain in test_df['Domain'].unique():
        zd = zm.get(domain, {}); sd = sm.get(domain, {})
        print(f"{domain:<22} | {sd.get('n',0):>3} | "
              f"{zd.get('pearson',0):>9.3f} | {sd.get('pearson',0):>10.3f} | "
              f"{sd.get('pred_mean',0):.3f}→{sd.get('true_mean',0):.3f}")

    out_path = os.path.join(os.path.dirname(__file__), "evaluation_results_career.json")
    existing = {}
    if os.path.exists(out_path):
        with open(out_path) as f:
            try: existing = json.load(f)
            except: pass
    existing.update(all_metrics)
    with open(out_path, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
