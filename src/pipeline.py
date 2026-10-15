"""End-to-end run: clean -> load to SQL -> run SQL analysis -> build the
rule-based risk scorecard -> validate it against actual outcomes -> export
for Tableau/Power BI.

    python -m src.pipeline
"""
import pandas as pd

from src import config as C
from src.data import build_clean
from src.sql_queries import load_to_sql, run_all_queries
from src.risk_scorecard import compute_risk_score, validate_against_actuals


def main():
    print("1/5  Cleaning data ...")
    df = build_clean(force=True)
    print(f"      {len(df):,} rows, overall default rate "
          f"{df[C.TARGET].mean():.2%}")

    print("\n2/5  Loading into SQLite ...")
    load_to_sql(df)

    print("\n3/5  Running SQL analytical queries ...")
    results = run_all_queries()
    for name, out in results.items():
        out.to_csv(C.REPORTS / f"{name}.csv", index=False)
        print(f"      {name}: {len(out)} rows -> reports/{name}.csv")

    print("\n4/5  Building the rule-based risk scorecard ...")
    scored = compute_risk_score(df)
    scored.to_csv(C.SCORED_FILE, index=False)

    validation = validate_against_actuals(scored)
    validation.to_csv(C.REPORTS / "scorecard_validation.csv", index=False)
    print(validation.to_string(index=False))

    monotonic = validation["actual_default_rate_pct"].is_monotonic_increasing
    print(f"\n      Default rate rises monotonically across bands: {monotonic}")
    if not monotonic:
        print("      WARNING: scorecard weights/thresholds may need revisiting - "
              "a good scorecard should show strictly increasing default rates "
              "from Low to Very High.")

    print("\n5/5  Exporting for Tableau / Power BI ...")
    scored.to_csv(C.TABLEAU_FILE, index=False)
    print(f"      -> {C.TABLEAU_FILE}")


if __name__ == "__main__":
    main()
