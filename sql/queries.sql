-- Named analytical queries. Each is pulled out individually by
-- src/sql_queries.py and run against the SQLite database built from
-- data/processed/clean.csv. Written to be readable as standalone SQL too.

-- name: default_rate_by_age_group
SELECT
    age_group,
    COUNT(*)                                   AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2)    AS default_rate_pct,
    ROUND(AVG(utilization), 3)                 AS avg_utilization,
    ROUND(AVG(months_delinquent), 2)           AS avg_months_delinquent
FROM clients
GROUP BY age_group
ORDER BY age_group;

-- name: default_rate_by_education
SELECT
    education,
    COUNT(*)                                   AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2)    AS default_rate_pct,
    ROUND(AVG(credit_limit), 0)                AS avg_credit_limit
FROM clients
GROUP BY education
ORDER BY default_rate_pct DESC;

-- name: default_rate_by_marriage_sex
SELECT
    marriage,
    sex,
    COUNT(*)                                   AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2)    AS default_rate_pct
FROM clients
GROUP BY marriage, sex
ORDER BY default_rate_pct DESC;

-- name: default_rate_by_credit_limit_decile
WITH deciles AS (
    SELECT *,
           NTILE(10) OVER (ORDER BY credit_limit) AS limit_decile
    FROM clients
)
SELECT
    limit_decile,
    MIN(credit_limit)                          AS min_limit,
    MAX(credit_limit)                          AS max_limit,
    COUNT(*)                                   AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2)    AS default_rate_pct
FROM deciles
GROUP BY limit_decile
ORDER BY limit_decile;

-- name: default_rate_by_delinquency_count
SELECT
    months_delinquent,
    COUNT(*)                                   AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2)    AS default_rate_pct,
    ROUND(AVG(utilization), 3)                 AS avg_utilization
FROM clients
GROUP BY months_delinquent
ORDER BY months_delinquent;

-- name: utilization_band_summary
SELECT
    CASE
        WHEN utilization < 0.3 THEN '0-30%'
        WHEN utilization < 0.6 THEN '30-60%'
        WHEN utilization < 0.9 THEN '60-90%'
        ELSE '90%+'
    END                                         AS utilization_band,
    COUNT(*)                                   AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2)    AS default_rate_pct
FROM clients
GROUP BY utilization_band
ORDER BY utilization_band;

-- name: severe_lateness_summary
SELECT
    ever_severely_late,
    COUNT(*)                                   AS n_clients,
    ROUND(AVG(default_next_month) * 100, 2)    AS default_rate_pct,
    ROUND(AVG(payment_ratio), 2)               AS avg_payment_ratio
FROM clients
GROUP BY ever_severely_late;
