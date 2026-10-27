-- Objetos base del game day, creados desde el código (schema propio para no pisar demo)
CREATE SCHEMA IF NOT EXISTS gameday;

CREATE TABLE IF NOT EXISTS gameday.bronze_customers (
    ingest_ts STRING,
    source STRING,
    raw_payload STRING
);

CREATE TABLE IF NOT EXISTS gameday.ops_event_log (
    run_id STRING,
    event_ts TIMESTAMP,
    stage STRING,
    status STRING,
    details STRING
);

CREATE TABLE IF NOT EXISTS gameday.ops_dq_results (
    run_id STRING,
    checked_ts TIMESTAMP,
    table_name STRING,
    check_name STRING,
    status STRING,
    value DOUBLE,
    details STRING
);

CREATE TABLE IF NOT EXISTS gameday.silver_customers (
    ingest_ts TIMESTAMP,
    customer_id STRING,
    customer_name STRING,
    email STRING,
    status STRING,
    payload STRING,
    dq_is_name_null BOOLEAN,
    dq_is_underage BOOLEAN,
    dq_status STRING
);
