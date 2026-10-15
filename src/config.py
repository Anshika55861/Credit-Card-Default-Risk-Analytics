"""Central configuration. Import this everywhere instead of hardcoding paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "reports" / "figures"
REPORTS = ROOT / "reports"
SQL_DIR = ROOT / "sql"

for _d in (DATA_RAW, DATA_PROCESSED, FIGURES, REPORTS):
    _d.mkdir(parents=True, exist_ok=True)

# UCI "Default of Credit Card Clients Dataset"
# https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
# Also mirrored on Kaggle as "UCI_Credit_Card.csv"
RAW_FILE = DATA_RAW / "UCI_Credit_Card.csv"
CLEAN_FILE = DATA_PROCESSED / "clean.csv"
SCORED_FILE = DATA_PROCESSED / "scored.csv"
TABLEAU_FILE = DATA_PROCESSED / "tableau_export.csv"

DB_FILE = DATA_PROCESSED / "credit_card.db"
DB_URL = f"sqlite:///{DB_FILE}"
TABLE_NAME = "clients"

TARGET = "default_next_month"   # 1 = defaulted, 0 = did not (historical outcome, used
                                 # only to VALIDATE the rule-based scorecard - never to
                                 # fit a model on)

RANDOM_SEED = 42
