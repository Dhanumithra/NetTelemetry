import os
import sqlite3
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DATA_DIR, "telemetry.db")
DEFAULT_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


@contextmanager
def get_connection(db_path=DEFAULT_DB_PATH):
    """Context manager that yields a database connection and ensures it is closed."""
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()


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
    enabled = 1 if target.get("enabled", True) else 0
    interval = int(target.get("interval", 5))
    timeout = int(target.get("timeout", 2))

    sql = """
        INSERT INTO targets (name, host, resolved_ip, enabled, interval, timeout)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(host) DO UPDATE SET
            name = excluded.name,
            resolved_ip = excluded.resolved_ip,
            enabled = excluded.enabled,
            interval = excluded.interval,
            timeout = excluded.timeout
        RETURNING target_id;
    """

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (name, host, resolved_ip, enabled, interval, timeout))
            row = cursor.fetchone()
            target_id = row["target_id"] if row else None
        except sqlite3.OperationalError:
            cursor.execute("""
                INSERT OR REPLACE INTO targets (name, host, resolved_ip, enabled, interval, timeout)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (name, host, resolved_ip, enabled, interval, timeout))
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

    timestamp = measurement["timestamp"]
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
