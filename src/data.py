"""Load and clean the UCI Default of Credit Card Clients dataset.

Download:
  https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
  (or Kaggle: "Default of Credit Card Clients Dataset", file UCI_Credit_Card.csv)
Place the CSV in data/raw/UCI_Credit_Card.csv

Columns (as shipped):
  ID, LIMIT_BAL, SEX, EDUCATION, MARRIAGE, AGE,
  PAY_0, PAY_2..PAY_6            repayment status each of the last 6 months
                                  (-1=paid duly, 1=1 month late, 2=2 months late, ...)
  BILL_AMT1..BILL_AMT6           bill statement amount, last 6 months
  PAY_AMT1..PAY_AMT6             amount actually paid, last 6 months
  default.payment.next.month     1 = defaulted the following month, 0 = did not
"""
import numpy as np
import pandas as pd

from src.config import RAW_FILE, CLEAN_FILE, TARGET

RENAME = {
    "default.payment.next.month": TARGET,
    "PAY_0": "PAY_1",          # UCI's own column naming is inconsistent (PAY_0 not PAY_1)
}

SEX_MAP = {1: "Male", 2: "Female"}
# UCI documents 1-4 but real data contains 0, 5, 6 too - collapse undocumented codes
EDUCATION_MAP = {1: "Graduate school", 2: "University", 3: "High school"}
MARRIAGE_MAP = {1: "Married", 2: "Single"}

BILL_COLS = [f"BILL_AMT{i}" for i in range(1, 7)]
PAY_AMT_COLS = [f"PAY_AMT{i}" for i in range(1, 7)]
PAY_STATUS_COLS = [f"PAY_{i}" for i in range(1, 7)]


def load_raw(path=RAW_FILE) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Download UCI_Credit_Card.csv from "
            "https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients "
            "(or the Kaggle mirror) into data/raw/."
        )
    df = pd.read_csv(path)
    df = df.rename(columns=RENAME)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset="ID")

    df["sex"] = df["SEX"].map(SEX_MAP)
    df["education"] = df["EDUCATION"].map(EDUCATION_MAP).fillna("Other/Unknown")
    df["marriage"] = df["MARRIAGE"].map(MARRIAGE_MAP).fillna("Other/Unknown")

    # AGE has no documented garbage codes in this dataset, but guard anyway
    df = df[df["AGE"].between(18, 100)]
    df["age_group"] = pd.cut(
        df["AGE"], bins=[17, 25, 35, 45, 55, 65, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"],
    )

    # credit utilisation: how much of the credit limit is actually being used,
    # the single most standard risk signal in consumer credit analytics
    df["avg_bill"] = df[BILL_COLS].mean(axis=1)
    df["avg_payment"] = df[PAY_AMT_COLS].mean(axis=1)
    df["utilization"] = (df["avg_bill"] / df["LIMIT_BAL"]).clip(lower=0)
    df["utilization"] = df["utilization"].replace([np.inf, -np.inf], np.nan)
    df["utilization"] = df["utilization"].fillna(df["utilization"].median())

    # delinquency summary: how many of the last 6 months were late (status >= 1)
    df["months_delinquent"] = (df[PAY_STATUS_COLS] >= 1).sum(axis=1)
    df["worst_delinquency"] = df[PAY_STATUS_COLS].max(axis=1)
    df["ever_severely_late"] = (df[PAY_STATUS_COLS] >= 3).any(axis=1).astype(int)

    # payment ratio: how much of the bill they're actually paying off, on average
    df["payment_ratio"] = (df["avg_payment"] / df["avg_bill"].replace(0, np.nan))
    df["payment_ratio"] = df["payment_ratio"].clip(0, 3).fillna(0)

    df = df.rename(columns={"LIMIT_BAL": "credit_limit", "AGE": "age"})
    keep = ([c for c in df.columns if c not in
             ["SEX", "EDUCATION", "MARRIAGE"] + BILL_COLS + PAY_AMT_COLS])
    return df[keep].reset_index(drop=True)


def build_clean(force: bool = False) -> pd.DataFrame:
    if CLEAN_FILE.exists() and not force:
        return pd.read_csv(CLEAN_FILE)
    df = clean(load_raw())
    df.to_csv(CLEAN_FILE, index=False)
    print(f"Saved {len(df):,} rows -> {CLEAN_FILE}")
    return df


if __name__ == "__main__":
    from src.config import TARGET as _TARGET

    d = build_clean(force=True)
    print(d.head())
    print(f"\nOverall default rate: {d[_TARGET].mean():.2%}")
