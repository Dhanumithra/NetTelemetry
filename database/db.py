import os
import sqlite3
import datetime
import random
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DATA_DIR, "telemetry.db")
DB_PATH = DEFAULT_DB_PATH
DEFAULT_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

class DBConnectionWrapper:
    """Wrapper that works both directly as a connection and as a context manager."""
    def __init__(self, db_path=DEFAULT_DB_PATH):
        db_dir = os.path.dirname(os.path.abspath(db_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self._conn = sqlite3.connect(db_path, timeout=30.0)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def cursor(self):
        return self._conn.cursor()

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def execute(self, *args, **kwargs):
        return self._conn.execute(*args, **kwargs)

    def executescript(self, *args, **kwargs):
        return self._conn.executescript(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self._conn.executemany(*args, **kwargs)

    def __getattr__(self, item):
        return getattr(self._conn, item)

def get_connection(db_path=DEFAULT_DB_PATH):
    return DBConnectionWrapper(db_path)

def init_db(db_path=DEFAULT_DB_PATH, schema_path=DEFAULT_SCHEMA_PATH):
    """Initialize the SQLite database using schema.sql."""
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection(db_path) as conn:
        conn.executescript(schema_sql)
        conn.commit()

def insert_target(target, db_path=DEFAULT_DB_PATH):
    """
    Insert a target into the targets table.
    If target host already exists, update and return existing target_id.
    """
    name = target.get("name", target.get("host", "Unknown Target"))
    host = target["host"]
    resolved_ip = target.get("resolved_ip")
    lat = target.get("lat", 0.0)
    lon = target.get("lon", 0.0)
    enabled = 1 if target.get("enabled", True) else 0
    interval = int(target.get("interval", 5))
    timeout = int(target.get("timeout", 2))

    sql = """
        INSERT INTO targets (name, host, resolved_ip, lat, lon, enabled, interval, timeout)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(host) DO UPDATE SET
            name = excluded.name,
            resolved_ip = excluded.resolved_ip,
            lat = excluded.lat,
            lon = excluded.lon,
            enabled = excluded.enabled,
            interval = excluded.interval,
            timeout = excluded.timeout
        RETURNING target_id;
    """

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (name, host, resolved_ip, lat, lon, enabled, interval, timeout))
            row = cursor.fetchone()
            target_id = row["target_id"] if row else None
        except sqlite3.OperationalError:
            cursor.execute("""
                INSERT OR REPLACE INTO targets (name, host, resolved_ip, lat, lon, enabled, interval, timeout)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (name, host, resolved_ip, lat, lon, enabled, interval, timeout))
            cursor.execute("SELECT target_id FROM targets WHERE host = ?", (host,))
            target_id = cursor.fetchone()["target_id"]
        conn.commit()
        return target_id

def get_target_by_host(host, db_path=DEFAULT_DB_PATH):
    """Retrieve a target by host or resolved_ip."""
    sql = "SELECT * FROM targets WHERE host = ? OR resolved_ip = ? LIMIT 1;"
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (host, host))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_target_by_id(target_id, db_path=DEFAULT_DB_PATH):
    """Retrieve a target by target_id."""
    sql = "SELECT * FROM targets WHERE target_id = ?;"
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (target_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def insert_measurement(measurement, db_path=DEFAULT_DB_PATH):
    """
    Insert a telemetry measurement using parameterized SQL.
    Measurement dict must include target_id or target (host/ip).
    """
    target_id = measurement.get("target_id")
    if target_id is None and "target" in measurement:
        target_row = get_target_by_host(measurement["target"], db_path)
        if target_row:
            target_id = target_row["target_id"]
        else:
            target_id = insert_target({"name": measurement["target"], "host": measurement["target"]}, db_path)

    if target_id is None:
        raise ValueError("Measurement must specify target_id or a valid target host.")

    timestamp = measurement["timestamp"] or datetime.datetime.now().isoformat()
    protocol = measurement.get("protocol", "ICMP")
    test_type = measurement.get("test_type", "echo")
    success = 1 if measurement.get("success") else 0
    rtt_ms = measurement.get("rtt_ms")
    ttl = measurement.get("ttl")
    error = measurement.get("error")

    sql = """
        INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error))
        measurement_id = cursor.lastrowid
        conn.commit()
        return measurement_id

def get_measurements(target_id=None, limit=100, db_path=DEFAULT_DB_PATH):
    """Retrieve stored measurements."""
    if target_id is not None:
        sql = "SELECT * FROM measurements WHERE target_id = ? ORDER BY id DESC LIMIT ?;"
        params = (target_id, limit)
    else:
        sql = "SELECT * FROM measurements ORDER BY id DESC LIMIT ?;"
        params = (limit,)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_measurements_for_window(target_id=None, start_time=None, end_time=None, limit=1000, db_path=DEFAULT_DB_PATH):
    """Retrieve measurements for a specific target and optional time window."""
    query_parts = ["SELECT * FROM measurements WHERE 1=1"]
    params = []

    if target_id is not None:
        query_parts.append("AND target_id = ?")
        params.append(target_id)

    if start_time is not None:
        query_parts.append("AND timestamp >= ?")
        params.append(start_time)

    if end_time is not None:
        query_parts.append("AND timestamp <= ?")
        params.append(end_time)

    query_parts.append("ORDER BY timestamp ASC LIMIT ?")
    params.append(limit)

    sql = " ".join(query_parts)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_all_targets(db_path=DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM targets")
        rows = [dict(row) for row in cursor.fetchall()]
        return rows

def seed_default_data(db_path=DEFAULT_DB_PATH):
    """
    Populates database with default targets, realistic measurements,
    aggregated metrics, and active anomalies aligned with the NOC mockup.
    """
    init_db(db_path)
    
    default_targets = [
        {"name": "Google", "host": "8.8.8.8", "resolved_ip": "8.8.8.8", "lat": 37.4220, "lon": -122.0841, "enabled": True, "interval": 5, "timeout": 2},
        {"name": "Cloudflare", "host": "1.1.1.1", "resolved_ip": "1.1.1.1", "lat": 51.5074, "lon": -0.1278, "enabled": True, "interval": 5, "timeout": 2},
        {"name": "GitHub", "host": "140.82.121.3", "resolved_ip": "140.82.121.3", "lat": 38.9586, "lon": -77.3570, "enabled": True, "interval": 5, "timeout": 2},
        {"name": "Amazon", "host": "52.94.126.1", "resolved_ip": "52.94.126.1", "lat": 19.0760, "lon": 72.8777, "enabled": True, "interval": 5, "timeout": 2},
        {"name": "Microsoft", "host": "20.190.164.4", "resolved_ip": "20.190.164.4", "lat": 35.6762, "lon": 139.6503, "enabled": True, "interval": 5, "timeout": 2},
    ]

    for t in default_targets:
        insert_target(t, db_path)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM measurements")
        m_count = cursor.fetchone()[0]

        now = datetime.datetime.now()
        targets_rows = get_all_targets(db_path)
        tid_map = {t["host"]: t["target_id"] for t in targets_rows}

        if m_count < 10:
            for i in range(60, -1, -1):
                ts = (now - datetime.timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S")

                # Google
                if "8.8.8.8" in tid_map:
                    rtt_g = max(18.0, random.gauss(24.0, 2.5))
                    cursor.execute('''
                    INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
                    VALUES (?, ?, 'ICMP', 'echo', 1, ?, 118, NULL)
                    ''', (ts, tid_map["8.8.8.8"], round(rtt_g, 2)))

                # Cloudflare
                if "1.1.1.1" in tid_map:
                    rtt_cf = max(22.0, random.gauss(28.0, 2.0))
                    cursor.execute('''
                    INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
                    VALUES (?, ?, 'ICMP', 'echo', 1, ?, 58, NULL)
                    ''', (ts, tid_map["1.1.1.1"], round(rtt_cf, 2)))

                # GitHub
                if "140.82.121.3" in tid_map:
                    github_success = 0 if (i in [15, 38]) else 1
                    rtt_gh = max(35.0, random.gauss(41.0, 4.0)) if github_success else 0.0
                    cursor.execute('''
                    INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
                    VALUES (?, ?, 'ICMP', 'echo', ?, ?, 54, ?)
                    ''', (ts, tid_map["140.82.121.3"], github_success, round(rtt_gh, 2), None if github_success else "Packet dropped"))

                # Amazon
                if "52.94.126.1" in tid_map:
                    amz_success = 1 if i > 20 else 0
                    rtt_amz = round(max(30.0, random.gauss(65.0, 15.0)), 2) if amz_success else 0.0
                    cursor.execute('''
                    INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
                    VALUES (?, ?, 'ICMP', 'echo', ?, ?, 48, ?)
                    ''', (ts, tid_map["52.94.126.1"], amz_success, rtt_amz, None if amz_success else "100% Packet Loss / Destination Unreachable"))

                # Microsoft
                if "20.190.164.4" in tid_map:
                    ms_success = 0 if i in [5, 12, 13, 29] else 1
                    rtt_ms = round(max(20.0, random.gauss(38.0, 5.0)), 2) if ms_success else 0.0
                    cursor.execute('''
                    INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
                    VALUES (?, ?, 'ICMP', 'echo', ?, ?, 112, ?)
                    ''', (ts, tid_map["20.190.164.4"], ms_success, rtt_ms, None if ms_success else "Request timed out"))

        cursor.execute("SELECT COUNT(*) FROM window_metrics")
        w_count = cursor.fetchone()[0]
        if w_count < 10:
            for i in range(30, -1, -1):
                st_time = (now - datetime.timedelta(minutes=i*2 + 2)).strftime("%Y-%m-%d %H:%M:%S")
                et_time = (now - datetime.timedelta(minutes=i*2)).strftime("%Y-%m-%d %H:%M:%S")
                loss = round(random.uniform(1.0, 3.5), 1)
                avail = round(100.0 - loss, 1)
                jitter = round(random.uniform(2.0, 6.5), 2)
                rtt = round(random.uniform(28.0, 36.0), 1)
                p95 = round(rtt * 1.35, 1)
                p99 = round(rtt * 1.7, 1)
                tput = round(random.uniform(45.0, 95.0), 2)
                cursor.execute('''
                INSERT INTO window_metrics (target_id, start_time, end_time, loss_pct, availability_pct, jitter_ms, p95_ms, p99_ms, throughput_mbps)
                VALUES ('global', ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (st_time, et_time, loss, avail, jitter, p95, p99, tput))

        cursor.execute("SELECT COUNT(*) FROM anomalies")
        a_count = cursor.fetchone()[0]
        if a_count < 3:
            anomalies_data = [
                ((now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
                 "Amazon", "loss_pct", 100.0, 2.0, 5.0, "Packet loss 100%"),
                ((now - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
                 "Microsoft", "timeout", 1.0, 0.0, 0.0, "No response (timeout)"),
                ((now - datetime.timedelta(minutes=84)).strftime("%Y-%m-%d %H:%M:%S"),
                 "GitHub", "p95_ms", 120.0, 41.0, 100.0, "High latency (avg 120ms)")
            ]
            cursor.executemany('''
            INSERT INTO anomalies (timestamp, target_id, metric, observed_value, baseline, threshold, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', anomalies_data)

        conn.commit()

def get_target_latest_status(db_path=DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Returns the latest status, RTT, loss, and reachability for each target."""
    targets = get_all_targets(db_path)
    results = []

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for t in targets:
            tid = t["target_id"]
            cursor.execute('''
            SELECT rtt_ms, success, error, timestamp FROM measurements
            WHERE target_id = ?
            ORDER BY id DESC LIMIT 20
            ''', (tid,))
            recent = cursor.fetchall()

            if recent:
                latest = recent[0]
                total_probes = len(recent)
                failed_probes = sum(1 for r in recent if r["success"] == 0)
                loss_pct = round((failed_probes / total_probes) * 100, 1)
                successful_rtts = [r["rtt_ms"] for r in recent if r["success"] == 1 and r["rtt_ms"] is not None]
                avg_rtt = round(sum(successful_rtts) / len(successful_rtts), 1) if successful_rtts else 0.0
                latest_rtt = latest["rtt_ms"] if latest["success"] == 1 else 0.0

                if loss_pct >= 80:
                    status = "Degraded"
                    status_color = "#f59e0b"
                elif loss_pct > 10:
                    status = "Degraded"
                    status_color = "#f59e0b"
                else:
                    status = "Online"
                    status_color = "#10b981"
            else:
                latest_rtt = 0.0
                loss_pct = 0.0
                avg_rtt = 0.0
                status = "Online"
                status_color = "#10b981"

            results.append({
                "target_id": tid,
                "name": t["name"],
                "host": t["host"],
                "resolved_ip": t["resolved_ip"] or t["host"],
                "lat": t["lat"] if "lat" in t and t["lat"] else 0.0,
                "lon": t["lon"] if "lon" in t and t["lon"] else 0.0,
                "rtt_ms": latest_rtt,
                "avg_rtt_ms": avg_rtt,
                "loss_pct": loss_pct,
                "status": status,
                "status_color": status_color
            })

    return results

def get_recent_measurements(db_path=DEFAULT_DB_PATH, limit: int = 15) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT m.id, m.timestamp, m.target_id, t.name, m.protocol, m.success, m.rtt_ms, m.error
        FROM measurements m
        LEFT JOIN targets t ON m.target_id = t.target_id
        ORDER BY m.id DESC LIMIT ?
        ''', (limit,))
        rows = [dict(row) for row in cursor.fetchall()]
        return rows

def get_active_anomalies(db_path=DEFAULT_DB_PATH, limit: int = 10) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT a.id, a.timestamp, a.target_id, t.name, t.host, a.metric, a.observed_value, a.reason
        FROM anomalies a
        LEFT JOIN targets t ON a.target_id = t.target_id
        ORDER BY a.id DESC LIMIT ?
        ''', (limit,))
        rows = [dict(row) for row in cursor.fetchall()]
        return rows
