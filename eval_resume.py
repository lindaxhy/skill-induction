"""
Evaluate resume screening on last 200 rows.
Runs two configurations:
  1. Zero-shot (no skill, Prompt A style)
  2. Skill (resume_screening_skill.md as system prompt) + Prompt A style user message
Metrics: Accuracy, F1, Precision, Recall
"""

import json
import os
import re
import sys
import time

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
sys.path.insert(0, os.path.dirname(__file__))
from llm_client import chat

TEST_PATH  = os.path.join(os.path.dirname(__file__),
    "../skill_construction_dataset/splits/resume_test.tsv")
SKILL_PATH = os.path.join(os.path.dirname(__file__),
    "skills/resume_screening_skill.md")

GPT4O_MODEL = "openai/gpt-4o"


def make_user_msg(role: str, jd: str, resume: str) -> str:
    role    = str(role)    if pd.notna(role)    else ""
    jd      = str(jd)      if pd.notna(jd)      else ""
    resume  = str(resume)  if pd.notna(resume)  else ""
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
    try:
        response = chat(system=system, user=user_msg, model=GPT4O_MODEL, temperature=0.0)
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
        # Fallback: search raw response
        m3 = re.search(r'\b(select|reject)\b', response, re.I)
        if m3:
            return m3.group(1).lower()
    except Exception as e:
        print(f"  [warn] {e}")
    return None


def evaluate(config_name: str, system: str, test_df: pd.DataFrame) -> dict:
    preds = []
    trues = []
    failures = 0

    print(f"\n  Scoring {len(test_df)} resumes — {config_name} ({GPT4O_MODEL})...")
    for i, row in enumerate(test_df.itertuples(), 1):
        pred = predict_one(system, row.Role, row.Job_Description, row.Resume)
        true = row.Decision.lower().strip()
        if pred is None:
            failures += 1
            pred = "reject"  # conservative fallback
        preds.append(pred)
        trues.append(true)

        if i % 50 == 0:
            print(f"    {i}/{len(test_df)} scored...")
        time.sleep(0.1)

    if failures:
        print(f"  [warn] {failures} prediction failures (fallback: reject)")

    # Encode: select=1, reject=0
    y_true = [1 if t == "select" else 0 for t in trues]
    y_pred = [1 if p == "select" else 0 for p in preds]

    acc  = accuracy_score(y_true, y_pred)
    f1   = f1_score(y_true, y_pred, pos_label=1)
    prec = precision_score(y_true, y_pred, pos_label=1)
    rec  = recall_score(y_true, y_pred, pos_label=1)

    n_pred_select = sum(y_pred)
    n_pred_reject = len(y_pred) - n_pred_select
    n_true_select = sum(y_true)

    return {
        "accuracy":  round(acc, 3),
        "f1":        round(f1, 3),
        "precision": round(prec, 3),
        "recall":    round(rec, 3),
        "n_pred_select": n_pred_select,
        "n_pred_reject": n_pred_reject,
        "n_true_select": n_true_select,
        "n_true_reject": len(y_true) - n_true_select,
        "failures":  failures,
    }


def main():
    test_df = pd.read_csv(TEST_PATH, sep="\t")
    print(f"Loaded {len(test_df)} test resumes")
    print(f"True: select={( test_df.Decision=='select').sum()} | reject={(test_df.Decision=='reject').sum()}")
    print(f"Roles: {test_df['Role'].value_counts().to_dict()}")

    with open(SKILL_PATH) as f:
        skill_text = f.read()

    configs = {
        "zero_shot":   "",
        "skill_based": skill_text,
    }

    all_metrics = {}
    for name, system in configs.items():
        m = evaluate(name, system, test_df)
        all_metrics[name] = m

    # Print results table
    print("\n" + "=" * 72)
    print("RESUME SCREENING — GPT-4o  (n=200, last 200 rows)")
    print("True: select=105, reject=95")
    print("=" * 72)
    print(f"{'Config':<16} | {'Accuracy':>8} | {'F1':>6} | {'Precision':>9} | {'Recall':>7} | pred_sel/rej")
    print("-" * 72)
    for name, m in all_metrics.items():
        print(f"{name:<16} | {m['accuracy']:>8.3f} | {m['f1']:>6.3f} | "
              f"{m['precision']:>9.3f} | {m['recall']:>7.3f} | "
              f"{m['n_pred_select']}/{m['n_pred_reject']}")
    print("=" * 72)

    # Save results
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
