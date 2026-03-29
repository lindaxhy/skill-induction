"""
Evaluate resume category classification on 200 stratified test rows.
Configs:
  1. zero_shot: category list only in user message, no system prompt
  2. skill_based: resume_category_skill.md as system prompt
Metrics: Accuracy, Macro-F1, per-category accuracy
"""

import json
import os
import re
import sys
import time

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
sys.path.insert(0, os.path.dirname(__file__))

TEST_PATH  = os.path.join(os.path.dirname(__file__),
    "../skill_construction_dataset/splits/resume2_test.tsv")
SKILL_PATH = os.path.join(os.path.dirname(__file__),
    "skills/resume_category_skill.md")

GPT4O_MODEL     = "openai/gpt-4o"
REQUEST_TIMEOUT = 60
MAX_RETRIES     = 2

CATEGORIES = [
    "INFORMATION-TECHNOLOGY", "BUSINESS-DEVELOPMENT", "ADVOCATE", "CHEF",
    "FINANCE", "ENGINEERING", "ACCOUNTANT", "FITNESS", "AVIATION", "SALES",
    "HEALTHCARE", "CONSULTANT", "BANKING", "CONSTRUCTION", "PUBLIC-RELATIONS",
    "HR", "DESIGNER", "ARTS", "TEACHER", "APPAREL", "DIGITAL-MEDIA",
    "AGRICULTURE", "AUTOMOBILE", "BPO",
]
CAT_LIST = ", ".join(CATEGORIES)


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
        model=GPT4O_MODEL, temperature=0.0, messages=messages,
    )
    return response.choices[0].message.content


def make_user_msg(resume: str) -> str:
    resume = str(resume) if pd.notna(resume) else ""
    return (
        f"Please classify the following resume into exactly one of these 24 categories:\n"
        f"{CAT_LIST}\n\n"
        '### Answer format: {"category": "CATEGORY_NAME"}\n'
        "Please answer ONLY in the above JSON format.\n"
        f"### resume:\n{resume}"
    )


def predict_one(system: str, resume: str) -> str | None:
    user_msg = make_user_msg(resume)
    for attempt in range(MAX_RETRIES):
        try:
            response = chat(system=system, user=user_msg)
            match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if match:
                blob = match.group()
                try:
                    raw = json.loads(blob)
                    cat = raw.get("category", "").strip().upper()
                except json.JSONDecodeError:
                    m2 = re.search(r'category["\s:]+([A-Z\-]+)', blob)
                    cat = m2.group(1).strip() if m2 else ""
                # Normalize: try exact match, then partial match
                if cat in CATEGORIES:
                    return cat
                for c in CATEGORIES:
                    if c in cat or cat in c:
                        return c
            # Raw text fallback
            for c in CATEGORIES:
                if c in response.upper():
                    return c
        except Exception as e:
            print(f"  [warn] attempt {attempt+1}/{MAX_RETRIES}: {e}", flush=True)
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)
    return None


def evaluate(config_name: str, system: str, test_df: pd.DataFrame) -> dict:
    preds, trues = [], []
    failures = 0

    print(f"\n  Scoring {len(test_df)} resumes — {config_name}...", flush=True)
    for i, row in enumerate(test_df.itertuples(), 1):
        pred = predict_one(system, row.Resume_str)
        true = str(row.Category).strip().upper()
        if pred is None:
            failures += 1
            pred = "INFORMATION-TECHNOLOGY"   # most common fallback
        preds.append(pred)
        trues.append(true)

        if i % 25 == 0:
            correct = sum(p == t for p, t in zip(preds, trues))
            print(f"    {i}/200  acc_so_far={correct/i:.3f}", flush=True)
        time.sleep(0.15)

    if failures:
        print(f"  [warn] {failures} failures (fallback used)")

    acc   = accuracy_score(trues, preds)
    macro = f1_score(trues, preds, average="macro", zero_division=0)
    report = classification_report(trues, preds, zero_division=0, output_dict=True)

    per_cat = {}
    for cat in CATEGORIES:
        if cat in report:
            per_cat[cat] = {
                "precision": round(report[cat]["precision"], 3),
                "recall":    round(report[cat]["recall"], 3),
                "f1":        round(report[cat]["f1-score"], 3),
                "support":   int(report[cat]["support"]),
            }

    return {
        "accuracy":  round(acc, 3),
        "macro_f1":  round(macro, 3),
        "failures":  failures,
        "per_category": per_cat,
    }


def main():
    test_df = pd.read_csv(TEST_PATH, sep="\t")
    print(f"Loaded {len(test_df)} test resumes")
    print(f"Categories: {test_df['Category'].nunique()} unique")
    print(f"Distribution: {test_df['Category'].value_counts().to_dict()}")

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

    # Print results
    print("\n" + "=" * 70)
    print("RESUME CATEGORY CLASSIFICATION — GPT-4o (n=200, 24 classes)")
    print("=" * 70)
    print(f"{'Config':<14} | {'Accuracy':>8} | {'Macro-F1':>8}")
    print("-" * 38)
    for name, m in all_metrics.items():
        print(f"{name:<14} | {m['accuracy']:>8.3f} | {m['macro_f1']:>8.3f}")
    print("=" * 70)

    print("\n--- Per-category F1 (skill_based) ---")
    skill_m = all_metrics.get("skill_based", {})
    zero_m  = all_metrics.get("zero_shot",   {})
    print(f"{'Category':<28} | {'Zero F1':>7} | {'Skill F1':>8} | {'n':>4}")
    print("-" * 56)
    for cat in CATEGORIES:
        zf = zero_m.get("per_category", {}).get(cat, {}).get("f1", 0)
        sf = skill_m.get("per_category", {}).get(cat, {}).get("f1", 0)
        n  = skill_m.get("per_category", {}).get(cat, {}).get("support", 0)
        diff = "+" if sf > zf else (" " if sf == zf else "-")
        print(f"{cat:<28} | {zf:>7.3f} | {sf:>8.3f} {diff} | {n:>4}")

    out_path = os.path.join(os.path.dirname(__file__), "evaluation_results_resume2.json")
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
