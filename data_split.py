"""
Split DREsS_New.tsv into stratified train/val/test splits (80/10/10).
Stratification is on discretized total score (3 buckets of equal size via qcut).
Splits are saved to skill_construction_dataset/splits/{train,val,test}.tsv.

Run ONCE before any induction scripts.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "../skill_construction_dataset/DREsS_New.tsv"
)
SPLITS_DIR = os.path.join(
    os.path.dirname(__file__),
    "../skill_construction_dataset/splits"
)
RANDOM_STATE = 42


def main():
    df = pd.read_csv(DATASET_PATH, sep="\t")
    print(f"Loaded {len(df)} essays")

    # 167 rows have component scores but NaN total — recompute from components
    missing_total = df["total"].isna()
    df.loc[missing_total, "total"] = (
        df.loc[missing_total, "content"]
        + df.loc[missing_total, "organization"]
        + df.loc[missing_total, "language"]
    )
    print(f"Recomputed total for {missing_total.sum()} rows with missing total")
    print(f"Total score range: {df['total'].min()} – {df['total'].max()}")

    # Stratify on discretized total score (3 equal-frequency bins)
    df["score_bin"] = pd.qcut(df["total"], q=3, labels=["low", "mid", "high"]).astype(str)
    print("\nScore bin distribution:")
    print(df["score_bin"].value_counts().sort_index())

    # Split: 80 / 10 / 10
    train, temp = train_test_split(
        df, test_size=0.20, stratify=df["score_bin"], random_state=RANDOM_STATE
    )
    val, test = train_test_split(
        temp, test_size=0.50, stratify=temp["score_bin"], random_state=RANDOM_STATE
    )

    # Drop the helper column before saving
    for split in (train, val, test):
        split.drop(columns=["score_bin"], inplace=True)

    os.makedirs(SPLITS_DIR, exist_ok=True)
    train.to_csv(os.path.join(SPLITS_DIR, "train.tsv"), sep="\t", index=False)
    val.to_csv(os.path.join(SPLITS_DIR, "val.tsv"), sep="\t", index=False)
    test.to_csv(os.path.join(SPLITS_DIR, "test.tsv"), sep="\t", index=False)

    print(f"\nSplits saved to {SPLITS_DIR}")
    print(f"  train: {len(train)} essays")
    print(f"  val:   {len(val)} essays")
    print(f"  test:  {len(test)} essays")

    # Verify score distribution is balanced across splits
    print("\nTotal score mean per split:")
    print(f"  train: {train['total'].mean():.2f}")
    print(f"  val:   {val['total'].mean():.2f}")
    print(f"  test:  {test['total'].mean():.2f}")


if __name__ == "__main__":
    main()
