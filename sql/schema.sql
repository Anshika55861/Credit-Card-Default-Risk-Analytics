-- Schema for the cleaned credit card client table.
-- Loaded automatically by src/data.py's to_sql() call - this file documents
-- the shape of that table for anyone reading the SQL on its own.

CREATE TABLE IF NOT EXISTS clients (
    ID                  INTEGER PRIMARY KEY,
    credit_limit        REAL,
    age                 INTEGER,
    age_group           TEXT,
    sex                 TEXT,
    education           TEXT,
    marriage            TEXT,
    avg_bill            REAL,
    avg_payment         REAL,
    utilization         REAL,
    months_delinquent   INTEGER,
    worst_delinquency   INTEGER,
    ever_severely_late  INTEGER,
    payment_ratio       REAL,
    PAY_1 INTEGER, PAY_2 INTEGER, PAY_3 INTEGER,
    PAY_4 INTEGER, PAY_5 INTEGER, PAY_6 INTEGER,
    default_next_month  INTEGER
);
