"""Load the cleaned data into SQLite and run the named queries in sql/queries.sql.

Why SQLite: zero setup (no server to install), but real SQL - window
functions, CTEs, GROUP BY - running against an actual database file, not a
pandas groupby pretending to be SQL. The queries in sql/queries.sql are
plain, portable SQL that would run unchanged against Postgres/MySQL too.
"""
import re

import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DB_URL, TABLE_NAME, SQL_DIR

QUERIES_FILE = SQL_DIR / "queries.sql"


def get_engine():
    return create_engine(DB_URL)


def load_to_sql(df: pd.DataFrame, if_exists: str = "replace") -> None:
    """Write the cleaned dataframe into the SQLite database as `clients`."""
    engine = get_engine()
    df.to_sql(TABLE_NAME, engine, if_exists=if_exists, index=False)
    print(f"Loaded {len(df):,} rows into {TABLE_NAME} ({DB_URL})")


def parse_named_queries(path=QUERIES_FILE) -> dict[str, str]:
    """Split queries.sql into {name: sql_text} using the `-- name: xxx` markers."""
    raw = path.read_text()
    chunks = re.split(r"--\s*name:\s*(\w+)\s*\n", raw)
    # chunks = ['', name1, sql1, name2, sql2, ...]
    queries = {}
    for i in range(1, len(chunks), 2):
        name, sql = chunks[i], chunks[i + 1]
        queries[name] = sql.strip().rstrip(";")
    return queries


def run_query(name: str) -> pd.DataFrame:
    queries = parse_named_queries()
    if name not in queries:
        raise KeyError(f"No query named '{name}' in {QUERIES_FILE}. "
                        f"Available: {list(queries)}")
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(queries[name]), conn)


def run_all_queries() -> dict[str, pd.DataFrame]:
    return {name: run_query(name) for name in parse_named_queries()}


if __name__ == "__main__":
    for name, result in run_all_queries().items():
        print(f"\n=== {name} ===")
        print(result.to_string(index=False))
