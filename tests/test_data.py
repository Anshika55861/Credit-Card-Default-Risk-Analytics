"""Data cleaning correctness tests."""
import numpy as np
import pandas as pd
import pytest

from src.data import clean, RENAME
from src.config import TARGET


@pytest.fixture
def raw():
    n = 200
    rng = np.random.default_rng(1)
    df = pd.DataFrame({
        "ID": range(1, n + 1),
        "LIMIT_BAL": rng.choice([10000, 50000, 200000], n),
        "SEX": rng.choice([1, 2], n),
        "EDUCATION": rng.choice([0, 1, 2, 3, 4], n),
        "MARRIAGE": rng.choice([0, 1, 2], n),
        "AGE": rng.integers(21, 70, n),
    })
    for i in range(1, 7):
        df[f"BILL_AMT{i}"] = rng.uniform(0, 20000, n)
        df[f"PAY_AMT{i}"] = rng.uniform(0, 10000, n)
    df["PAY_0"] = rng.choice([-1, 0, 1, 2, 3], n)
    for i in range(2, 7):
        df[f"PAY_{i}"] = rng.choice([-1, 0, 1, 2, 3], n)
    df["default.payment.next.month"] = rng.choice([0, 1], n)
    return df.rename(columns=RENAME)


def test_undocumented_education_codes_collapse_to_other(raw):
    out = clean(raw)
    assert set(out["education"].unique()) <= {
        "Graduate school", "University", "High school", "Other/Unknown"
    }


def test_utilization_has_no_missing_values(raw):
    out = clean(raw)
    assert out["utilization"].notna().all()


def test_months_delinquent_bounded_0_to_6(raw):
    out = clean(raw)
    assert out["months_delinquent"].between(0, 6).all()


def test_pay_0_renamed_to_pay_1(raw):
    assert "PAY_0" not in raw.columns
    assert "PAY_1" in raw.columns


def test_no_duplicate_ids(raw):
    dup = pd.concat([raw, raw.iloc[[0]]], ignore_index=True)
    out = clean(dup)
    assert out["ID"].is_unique


def test_target_column_renamed(raw):
    out = clean(raw)
    assert TARGET in out.columns
    assert "default.payment.next.month" not in out.columns
