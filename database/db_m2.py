import sqlite3
from typing import Dict, Any

def init_m2_db(db_path: str = "telemetry.db"):
    """
    Initializes the database tables required by Member 2.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # window_metrics table
    cursor.execute('''
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
    )
    ''')
    
    # anomalies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anomalies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        target_id TEXT,
        metric TEXT,
        observed_value REAL,
        baseline REAL,
        threshold REAL,
        reason TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def store_window_metrics(db_path: str, target_id: str, start_time: str, end_time: str, metrics: Dict[str, Any]):
    """
    Stores aggregated network metrics into the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO window_metrics (target_id, start_time, end_time, loss_pct, availability_pct, jitter_ms, p95_ms, p99_ms, throughput_mbps)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        target_id, start_time, end_time,
        metrics.get("loss_pct", 0.0),
        metrics.get("availability_pct", 0.0),
        metrics.get("jitter_ms", 0.0),
        metrics.get("p95_ms", 0.0),
        metrics.get("p99_ms", 0.0),
        metrics.get("throughput_mbps", 0.0)
    ))
    conn.commit()
    conn.close()

def store_anomaly(db_path: str, target_id: str, anomaly: Dict[str, Any]):
    """
    Stores a detected network anomaly reason, baseline, and threshold.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO anomalies (target_id, metric, observed_value, baseline, threshold, reason)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        target_id,
        anomaly["metric"],
        anomaly["observed_value"],
        anomaly["baseline"],
        anomaly["threshold"],
        anomaly["reason"]
    ))
    conn.commit()
    conn.close()
