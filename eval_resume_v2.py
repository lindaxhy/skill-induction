"""
eval_resume_v2.py — Resume screening evaluation with 60s timeout + retry.
Same logic as eval_resume.py but adds:
  - 60s per-request timeout
  - 1 automatic retry on timeout/error
  - Per-role breakdown in output
"""

import json
import os
import re
import sys
import time

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
sys.path.insert(0, os.path.dirname(__file__))

TEST_PATH  = os.path.join(os.path.dirname(__file__),
    "../skill_construction_dataset/splits/resume_test.tsv")
SKILL_PATH = os.path.join(os.path.dirname(__file__),
    "skills/resume_screening_skill.md")

GPT4O_MODEL  = "openai/gpt-4o"
REQUEST_TIMEOUT = 60   # seconds per API call
MAX_RETRIES     = 2


def get_client() -> OpenAI:
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
    response = client.chat.completions.create(
        model=GPT4O_MODEL,
        temperature=0.0,
        messages=messages,
    )
    return response.choices[0].message.content


def make_user_msg(role: str, jd: str, resume: str) -> str:
    role   = str(role)   if pd.notna(role)   else ""
    jd     = str(jd)     if pd.notna(jd)     else ""
    resume = str(resume) if pd.notna(resume) else ""
    return (
        "Please screen the following resume and decide: select or reject.\n"
        '### Answer format: {"decision": "select"} or {"decision": "reject"}\n'
        "Please answer ONLY in the above JSON format.\n"
        f"### role: {role}\n"
        f"### job_description: {jd}\n"
        f"### resume: {resume}"
    )


def predict_one(system: str, role: str, jd: str, resume: str) -> str | None:
    user_msg = make_user_msg(role, jd, resume)
    for attempt in range(MAX_RETRIES):
        try:
            response = chat(system=system, user=user_msg)
            match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if match:
                blob = match.group()
                try:
                    raw = json.loads(blob)
                    dec = raw.get("decision", "").lower().strip()
                except json.JSONDecodeError:
                    m2 = re.search(r'decision\s*[:\s]+["\']?(select|reject)["\']?', blob, re.I)
                    dec = m2.group(1).lower() if m2 else None
                if dec in ("select", "reject"):
                    return dec
            # Search raw response as fallback
            m3 = re.search(r'\b(select|reject)\b', response, re.I)
            if m3:
                return m3.group(1).lower()
        except Exception as e:
            print(f"  [warn] attempt {attempt+1}/{MAX_RETRIES}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)
    return None


def evaluate(config_name: str, system: str, test_df: pd.DataFrame) -> dict:
    preds, trues = [], []
    failures = 0

    print(f"\n  Scoring {len(test_df)} resumes — {config_name} ({GPT4O_MODEL})...")
    for i, row in enumerate(test_df.itertuples(), 1):
        pred = predict_one(system, row.Role, row.Job_Description, row.Resume)
        true = row.Decision.lower().strip()
        if pred is None:
            failures += 1
            pred = "reject"
        preds.append(pred)
        trues.append(true)

        if i % 25 == 0:
            correct_so_far = sum(p == t for p, t in zip(preds, trues))
            print(f"    {i}/200  acc_so_far={correct_so_far/i:.3f}", flush=True)
        time.sleep(0.1)

    if failures:
        print(f"  [warn] {failures} failures (fallback: reject)")

    y_true = [1 if t == "select" else 0 for t in trues]
    y_pred = [1 if p == "select" else 0 for p in preds]

    # Per-role breakdown
    role_metrics = {}
    for role in test_df["Role"].unique():
        idx = [i for i, r in enumerate(test_df["Role"].tolist()) if r == role]
        yt = [y_true[i] for i in idx]
        yp = [y_pred[i] for i in idx]
        role_metrics[role] = {
            "n": len(idx),
            "accuracy": round(accuracy_score(yt, yp), 3),
            "f1": round(f1_score(yt, yp, pos_label=1, zero_division=0), 3),
        }

    return {
        "accuracy":        round(accuracy_score(y_true, y_pred), 3),
        "f1":              round(f1_score(y_true, y_pred, pos_label=1), 3),
        "precision":       round(precision_score(y_true, y_pred, pos_label=1), 3),
        "recall":          round(recall_score(y_true, y_pred, pos_label=1), 3),
        "n_pred_select":   sum(y_pred),
        "n_pred_reject":   len(y_pred) - sum(y_pred),
        "n_true_select":   sum(y_true),
        "n_true_reject":   len(y_true) - sum(y_true),
        "failures":        failures,
        "per_role":        role_metrics,
    }


def main():
    test_df = pd.read_csv(TEST_PATH, sep="\t")
    print(f"Loaded {len(test_df)} test resumes (v2 — timeout={REQUEST_TIMEOUT}s, retries={MAX_RETRIES})")
    print(f"True: select={(test_df.Decision=='select').sum()} | reject={(test_df.Decision=='reject').sum()}")
    print(f"Roles: {test_df['Role'].value_counts().to_dict()}")

    with open(SKILL_PATH) as f:
        skill_text = f.read()

    configs = {
        "zero_shot_v2":   "",
        "skill_based_v2": skill_text,
    }

    all_metrics = {}
    for name, system in configs.items():
        m = evaluate(name, system, test_df)
        all_metrics[name] = m

    print("\n" + "=" * 72)
    print("RESUME SCREENING v2 — GPT-4o  (n=200, timeout=60s)")
    print(f"True distribution: select=105 / reject=95")
    print("=" * 72)
    print(f"{'Config':<18} | {'Accuracy':>8} | {'F1':>6} | {'Precision':>9} | {'Recall':>7} | pred sel/rej")
    print("-" * 72)
    for name, m in all_metrics.items():
        print(f"{name:<18} | {m['accuracy']:>8.3f} | {m['f1']:>6.3f} | "
              f"{m['precision']:>9.3f} | {m['recall']:>7.3f} | "
              f"{m['n_pred_select']}/{m['n_pred_reject']}")
    print("=" * 72)

    print("\n--- Per-role breakdown (skill_based_v2) ---")
    for role, rm in all_metrics.get("skill_based_v2", {}).get("per_role", {}).items():
        print(f"  {role:<28} n={rm['n']:>3}  acc={rm['accuracy']:.3f}  f1={rm['f1']:.3f}")

    out_path = os.path.join(os.path.dirname(__file__), "evaluation_results_resume.json")
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
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
