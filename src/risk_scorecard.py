"""A rule-based credit risk scorecard - the analytics alternative to a
trained ML classifier.

This is deliberately NOT a fitted model: there is no .fit(), no train/test
split, no learned coefficients. Each factor's weight and threshold is set
by a human, informed by the EDA (see src/eda.py and the SQL queries), the
same way a risk/credit analytics team builds a scorecard before (or
instead of) a data science team builds a classifier on top of it.

The actual historical outcome (`default_next_month`) is used ONLY at the
very end, to check how well the scorecard's bands line up with real
default rates - a validation step, never an input to the score itself.
"""
import numpy as np
import pandas as pd

from src.config import TARGET

# Each factor contributes points on a 0-100 scale. Thresholds come directly
# from the SQL/EDA output (e.g. the utilization-band and delinquency-count
# queries) - adjust these numbers after you've looked at your own EDA charts.
WEIGHTS = {
    "utilization": 35,          # heaviest single factor - industry standard
    "months_delinquent": 30,
    "worst_delinquency": 20,
    "payment_ratio": 15,
}


def _score_utilization(u: pd.Series) -> pd.Series:
    # higher utilization = higher risk points
    return pd.cut(
        u, bins=[-0.01, 0.3, 0.6, 0.9, np.inf],
        labels=[0, 1, 2, 3],
    ).astype(int) / 3 * WEIGHTS["utilization"]


def _score_delinquency_count(m: pd.Series) -> pd.Series:
    return m.clip(upper=6) / 6 * WEIGHTS["months_delinquent"]


def _score_worst_delinquency(w: pd.Series) -> pd.Series:
    # worst_delinquency ranges roughly -2..8 in this dataset; clip & rescale
    clipped = w.clip(lower=0, upper=8)
    return clipped / 8 * WEIGHTS["worst_delinquency"]


def _score_payment_ratio(p: pd.Series) -> pd.Series:
    # LOW payment ratio (paying little of the bill) = higher risk, so invert
    inverted = (1 - p.clip(0, 1))
    return inverted * WEIGHTS["payment_ratio"]


def compute_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["score_utilization"] = _score_utilization(df["utilization"])
    df["score_delinquency_count"] = _score_delinquency_count(df["months_delinquent"])
    df["score_worst_delinquency"] = _score_worst_delinquency(df["worst_delinquency"])
    df["score_payment_ratio"] = _score_payment_ratio(df["payment_ratio"])

    df["risk_score"] = (
        df["score_utilization"] + df["score_delinquency_count"]
        + df["score_worst_delinquency"] + df["score_payment_ratio"]
    ).round(1)

    df["risk_band"] = pd.cut(
        df["risk_score"], bins=[-0.1, 25, 50, 75, 100],
        labels=["Low", "Medium", "High", "Very High"],
    )
    return df


def validate_against_actuals(df: pd.DataFrame) -> pd.DataFrame:
    """The ONE place actual outcomes are used: checking whether higher
    risk bands really do default more often. If they don't line up
    monotonically, the scorecard's weights/thresholds need revisiting."""
    summary = (
        df.groupby("risk_band", observed=True)
        .agg(n_clients=(TARGET, "size"),
             actual_default_rate_pct=(TARGET, lambda s: round(s.mean() * 100, 2)),
             avg_risk_score=("risk_score", lambda s: round(s.mean(), 1)))
        .reset_index()
    )
    return summary
