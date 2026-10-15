"""Risk scorecard logic tests - the rule-based alternative to model tests."""
import numpy as np
import pandas as pd
import pytest

from src.risk_scorecard import compute_risk_score, validate_against_actuals
from src.config import TARGET


@pytest.fixture
def toy():
    return pd.DataFrame({
        "utilization": [0.0, 0.5, 1.5],
        "months_delinquent": [0, 3, 6],
        "worst_delinquency": [0, 3, 8],
        "payment_ratio": [1.0, 0.5, 0.0],
        TARGET: [0, 1, 1],
    })


def test_score_is_bounded_0_to_100(toy):
    out = compute_risk_score(toy)
    assert out["risk_score"].between(0, 100).all()


def test_worse_inputs_produce_higher_score(toy):
    out = compute_risk_score(toy)
    # row 0 is the "best" client, row 2 the "worst" on every factor
    assert out["risk_score"].iloc[0] < out["risk_score"].iloc[1] < out["risk_score"].iloc[2]


def test_risk_band_labels_are_ordered_categories(toy):
    out = compute_risk_score(toy)
    assert list(out["risk_band"].cat.categories) == ["Low", "Medium", "High", "Very High"]


def test_validation_never_uses_target_to_compute_score(toy):
    """The target column must play no role in risk_score itself - only in
    the separate validation step."""
    tampered = toy.copy()
    tampered[TARGET] = 1 - tampered[TARGET]   # flip every outcome
    out_a = compute_risk_score(toy)
    out_b = compute_risk_score(tampered)
    pd.testing.assert_series_equal(out_a["risk_score"], out_b["risk_score"])


def test_validate_against_actuals_runs(toy):
    out = compute_risk_score(toy)
    val = validate_against_actuals(out)
    assert "actual_default_rate_pct" in val.columns
    assert val["n_clients"].sum() == len(toy)
