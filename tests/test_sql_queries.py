"""Parsing test for sql/queries.sql - catches a broken `-- name:` marker
before it causes a confusing KeyError at pipeline runtime."""
from src.sql_queries import parse_named_queries


def test_all_expected_queries_present():
    queries = parse_named_queries()
    expected = {
        "default_rate_by_age_group", "default_rate_by_education",
        "default_rate_by_marriage_sex", "default_rate_by_credit_limit_decile",
        "default_rate_by_delinquency_count", "utilization_band_summary",
        "severe_lateness_summary",
    }
    assert expected <= set(queries)


def test_every_query_is_nonempty_sql():
    for name, sql in parse_named_queries().items():
        assert "SELECT" in sql.upper(), f"{name} doesn't look like valid SQL"
