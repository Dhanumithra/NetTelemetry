-- NetTelemetry Database Schema for SQLite

CREATE TABLE IF NOT EXISTS targets (
    target_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    host TEXT NOT NULL UNIQUE,
    resolved_ip TEXT,
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
