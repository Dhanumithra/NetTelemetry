-- NetTelemetry Database Schema for SQLite
-- Defines targets, raw measurements, aggregated metrics, and anomaly events

CREATE TABLE IF NOT EXISTS targets (
    target_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    host TEXT NOT NULL UNIQUE,
    resolved_ip TEXT,
    lat REAL DEFAULT 0.0,
    lon REAL DEFAULT 0.0,
    enabled INTEGER NOT NULL DEFAULT 1,
    interval INTEGER NOT NULL DEFAULT 5,
    timeout INTEGER NOT NULL DEFAULT 2
);

CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    protocol TEXT NOT NULL,
    test_type TEXT NOT NULL,
    success INTEGER NOT NULL,
    rtt_ms REAL,
    ttl INTEGER,
    error TEXT,
    FOREIGN KEY (target_id) REFERENCES targets (target_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS window_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id TEXT,
    start_time DATETIME,
    end_time DATETIME,
    loss_pct REAL,
    availability_pct REAL,
    jitter_ms REAL,
    p95_ms REAL,
    p99_ms REAL,
    throughput_mbps REAL
);

CREATE TABLE IF NOT EXISTS anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    target_id TEXT,
    metric TEXT,
    observed_value REAL,
    baseline REAL,
    threshold REAL,
    reason TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'NOC Operator',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

