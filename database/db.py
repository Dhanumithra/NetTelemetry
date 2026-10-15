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
        try:
            self._conn.execute("PRAGMA journal_mode = WAL;")
            self._conn.execute("PRAGMA synchronous = NORMAL;")
        except Exception:
            pass

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

def _apply_migrations(conn):
    """
    Applies schema migrations to ensure existing tables have all required columns.
    Safe to run repeatedly without modifying existing data.
    """
    cursor = conn.cursor()
    # Check if targets table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='targets';")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(targets);")
        rows = cursor.fetchall()
        existing_cols = set()
        for row in rows:
            if isinstance(row, sqlite3.Row):
                existing_cols.add(row["name"])
            elif hasattr(row, "keys"):
                existing_cols.add(row["name"])
            else:
                existing_cols.add(row[1])

        target_columns = [
            ("resolved_ip", "TEXT"),
            ("lat", "REAL DEFAULT 0.0"),
            ("lon", "REAL DEFAULT 0.0"),
            ("enabled", "INTEGER NOT NULL DEFAULT 1"),
            ("interval", "INTEGER NOT NULL DEFAULT 5"),
            ("timeout", "INTEGER NOT NULL DEFAULT 2"),
        ]

        for col_name, col_def in target_columns:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE targets ADD COLUMN {col_name} {col_def};")
                existing_cols.add(col_name)

        if "lat" in existing_cols:
            cursor.execute("UPDATE targets SET lat = 0.0 WHERE lat IS NULL;")
        if "lon" in existing_cols:
            cursor.execute("UPDATE targets SET lon = 0.0 WHERE lon IS NULL;")

    conn.commit()

def migrate_db(db_path=DEFAULT_DB_PATH):
    """
    Public migration function to update an existing SQLite database schema.
    Can accept a database file path or an active connection/wrapper.
    """
    if isinstance(db_path, (str, bytes, os.PathLike)):
        with get_connection(db_path) as conn:
            _apply_migrations(conn)
    else:
        _apply_migrations(db_path)

def init_db(db_path=DEFAULT_DB_PATH, schema_path=DEFAULT_SCHEMA_PATH):
    """Initialize the SQLite database using schema.sql and apply any migrations."""
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection(db_path) as conn:
        conn.executescript(schema_sql)
        _apply_migrations(conn)
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
        except sqlite3.OperationalError as e:
            if "no column named" in str(e).lower():
                _apply_migrations(conn)
                cursor.execute(sql, (name, host, resolved_ip, lat, lon, enabled, interval, timeout))
                row = cursor.fetchone()
                target_id = row["target_id"] if row else None
            else:
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

def target_exists(host: str, db_path=DEFAULT_DB_PATH) -> bool:
    """Check if a target with the given host or resolved_ip already exists."""
    if not host:
        return False
    from network.target_manager import normalize_target_host
    clean_host = normalize_target_host(host)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT target_id, host, resolved_ip FROM targets;")
        rows = cursor.fetchall()
        for r in rows:
            h = normalize_target_host(r["host"] or "")
            rip = normalize_target_host(r["resolved_ip"] or "")
            if h == clean_host or (rip and rip == clean_host):
                return True
    return False

def add_target_validated(name: str, host: str, interval: int = 5, timeout: int = 2, lat: float = 0.0, lon: float = 0.0, db_path=DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Validates host input, checks for duplicates, resolves IP, and inserts target into SQLite.
    Returns a dict with success status and target details or error message.
    """
    from network.target_manager import validate_hostname_or_ip, normalize_target_host, resolve_target

    is_valid, msg = validate_hostname_or_ip(host)
    if not is_valid:
        return {"success": False, "status": "error", "error": msg, "message": msg}

    clean_host = normalize_target_host(host)
    if target_exists(clean_host, db_path=db_path):
        dup_msg = f"Target '{clean_host}' is already being monitored."
        return {"success": False, "status": "exists", "error": dup_msg, "message": dup_msg, "is_duplicate": True}

    resolved_ip = resolve_target(clean_host)
    target_name = name.strip() if name and name.strip() else clean_host

    target_data = {
        "name": target_name,
        "host": clean_host,
        "resolved_ip": resolved_ip,
        "lat": float(lat) if lat else 0.0,
        "lon": float(lon) if lon else 0.0,
        "enabled": True,
        "interval": max(1, int(interval)),
        "timeout": max(1, int(timeout))
    }

    target_id = insert_target(target_data, db_path=db_path)
    target_data["target_id"] = target_id
    return {"success": True, "status": "success", "target": target_data, "message": f"Target '{target_name}' added successfully."}

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
            from network.target_manager import validate_hostname_or_ip, normalize_target_host
            clean_host = normalize_target_host(measurement["target"])
            is_valid, err_msg = validate_hostname_or_ip(clean_host)
            if not is_valid:
                raise ValueError(f"Cannot auto-register target for measurement: {err_msg}")
            target_id = insert_target({"name": clean_host, "host": clean_host}, db_path)

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

    # Seed default NOC users if empty
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            create_user("dhanumithra", "Dhanumithra", "admin", "dhanu@telemetry.noc", "NOC Lead / Administrator", db_path)
            create_user("admin", "Administrator", "admin", "admin@telemetry.noc", "NOC Administrator", db_path)
            create_user("operator", "Network Operator", "noc", "ops@telemetry.noc", "NOC Operator", db_path)

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
                avg_rtt = round(sum(successful_rtts) / len(successful_rtts), 1) if successful_rtts else None
                latest_rtt = latest["rtt_ms"] if (latest["success"] == 1 and latest["rtt_ms"] is not None) else None

                if loss_pct == 100 and total_probes >= 3:
                    status = "Offline"
                    status_color = "#ef4444"
                elif loss_pct > 10:
                    status = "Degraded"
                    status_color = "#f59e0b"
                else:
                    status = "Online"
                    status_color = "#10b981"
            else:
                latest_rtt = None
                loss_pct = 0.0
                avg_rtt = None
                status = "Unknown"
                status_color = "#94a3b8"

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
                "availability_pct": round(100.0 - loss_pct, 1) if recent else 100.0,
                "last_probe_time": latest["timestamp"] if recent else None,
                "status": status,
                "status_color": status_color
            })

    return results

def get_recent_measurements(db_path=DEFAULT_DB_PATH, limit: int = 15) -> List[Dict[str, Any]]:
    if isinstance(db_path, int):
        limit, db_path = db_path, DEFAULT_DB_PATH
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
    if isinstance(db_path, int):
        limit, db_path = db_path, DEFAULT_DB_PATH
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT a.id, a.timestamp, a.target_id, t.name, t.host, a.metric, a.observed_value, a.reason
        FROM anomalies a
        LEFT JOIN targets t ON (a.target_id = t.target_id OR a.target_id = CAST(t.target_id AS TEXT) OR a.target_id = t.name)
        ORDER BY a.id DESC LIMIT ?
        ''', (limit,))
        rows = [dict(row) for row in cursor.fetchall()]
        return rows


# --- Authentication & User Management ---
import hashlib

def hash_password(password: str) -> str:
    """Computes SHA-256 hash of password string."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_user(username: str, full_name: str, password: str, email: str = "", role: str = "NOC Operator", db_path=DEFAULT_DB_PATH) -> Optional[int]:
    """Registers a new user in the users table."""
    init_db(db_path)
    pwd_hash = hash_password(password)
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (username, full_name, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
            """, (username.strip().lower(), full_name.strip(), email.strip(), pwd_hash, role))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    except Exception:
        return None

def authenticate_user(username: str, password: str, db_path=DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Validates user credentials against the users table."""
    init_db(db_path)
    u_name = username.strip().lower()
    pwd_hash = hash_password(password)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, email, role, created_at FROM users WHERE username = ? AND password_hash = ?", (u_name, pwd_hash))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_user_by_username(username: str, db_path=DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Fetches user details by username."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, email, role, created_at FROM users WHERE username = ?", (username.strip().lower(),))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def clear_measurements(db_path=DEFAULT_DB_PATH) -> bool:
    """
    Safely delete all raw measurement records from the measurements table.
    Preserves registered targets, window metrics, anomaly records, and users.
    Returns True on success.
    """
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM measurements")
        conn.commit()
    return True

def get_measurements_count(db_path=DEFAULT_DB_PATH) -> int:
    """Returns the total number of records in the measurements table."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM measurements")
        row = cursor.fetchone()
        return row[0] if row else 0

def clear_anomalies(db_path=DEFAULT_DB_PATH) -> bool:
    """
    Safely delete all anomaly records from the anomalies table.
    Preserves registered targets, raw measurements, window metrics, and users.
    Returns True on success.
    """
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM anomalies")
        conn.commit()
    return True

def get_anomalies_count(db_path=DEFAULT_DB_PATH) -> int:
    """Returns the total number of records in the anomalies table."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM anomalies")
        row = cursor.fetchone()
        return row[0] if row else 0

def get_network_performance_summary(db_path=DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Computes a comprehensive live network performance summary from real SQLite records:
    - Registered Targets: count from targets table
    - Recorded Measurements: total count from measurements table
    - Successful Probes: count where success = 1
    - Failed Probes: count where success = 0 (or total - successful)
    - Average RTT: AVG(rtt_ms) for success = 1 and rtt_ms IS NOT NULL and rtt_ms > 0
    - Packet Loss (%): (failed / total) * 100 if total > 0 else None
    - Availability (%): (successful / total) * 100 if total > 0 else None
    - Recorded Anomalies: count from anomalies table
    """
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Registered Targets
        cursor.execute("SELECT COUNT(*) FROM targets")
        row = cursor.fetchone()
        num_targets = row[0] if row else 0

        # 2, 3, 4. Measurements aggregation
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                COALESCE(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END), 0) AS successful,
                COALESCE(SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END), 0) AS failed,
                AVG(CASE WHEN success = 1 AND rtt_ms IS NOT NULL AND rtt_ms > 0 THEN rtt_ms ELSE NULL END) AS avg_rtt
            FROM measurements
        """)
        m_row = cursor.fetchone()
        total_meas = m_row["total"] if m_row and m_row["total"] is not None else 0
        succ_probes = m_row["successful"] if m_row and m_row["successful"] is not None else 0
        failed_probes = m_row["failed"] if m_row and m_row["failed"] is not None else 0
        raw_avg_rtt = m_row["avg_rtt"] if m_row and m_row["avg_rtt"] is not None else None

        avg_rtt = round(float(raw_avg_rtt), 2) if raw_avg_rtt is not None else None

        # 5 & 6. Packet loss and availability
        if total_meas > 0:
            loss_pct = round((failed_probes / total_meas) * 100.0, 2)
            avail_pct = round((succ_probes / total_meas) * 100.0, 2)
        else:
            loss_pct = None
            avail_pct = None

        # 7. Recorded Anomalies
        cursor.execute("SELECT COUNT(*) FROM anomalies")
        a_row = cursor.fetchone()
        num_anomalies = a_row[0] if a_row else 0

    return {
        "num_targets": num_targets,
        "total_measurements": total_meas,
        "successful_probes": succ_probes,
        "failed_probes": failed_probes,
        "avg_rtt_ms": avg_rtt,
        "packet_loss_pct": loss_pct,
        "availability_pct": avail_pct,
        "num_anomalies": num_anomalies
    }

def generate_performance_interpretation(summary: Dict[str, Any]) -> str:
    """
    Generates a data-derived operational interpretation based on actual observed metrics.
    Avoids false claims that targets are down solely because probes fail (as ICMP/TCP may be blocked).
    """
    total = summary.get("total_measurements", 0)
    if total == 0:
        return (
            "No telemetry probe records are currently available in the database. "
            "Configured endpoints are registered and ready for active monitoring cycles."
        )

    avail = summary.get("availability_pct")
    loss = summary.get("packet_loss_pct")
    avg_rtt = summary.get("avg_rtt_ms")
    anomalies = summary.get("num_anomalies", 0)
    failed = summary.get("failed_probes", 0)

    observations = []

    # Availability & Loss assessment
    if avail is not None and avail >= 99.0:
        observations.append(
            f"Overall network reachability is high at {avail:.1f}% SLA availability with minimal packet loss ({loss:.1f}%)."
        )
    elif avail is not None and avail >= 90.0:
        observations.append(
            f"Moderate probe loss observed: {loss:.1f}% packet drop across test cycles ({avail:.1f}% availability)."
        )
    elif avail is not None:
        observations.append(
            f"Significant probe loss observed: {loss:.1f}% of probe cycles were unacknowledged ({avail:.1f}% availability)."
        )

    # Latency assessment
    if avg_rtt is not None:
        if avg_rtt < 50.0:
            observations.append(f"Mean latency is excellent at {avg_rtt:.1f} ms, indicating responsive path transit.")
        elif avg_rtt < 120.0:
            observations.append(f"Mean latency is nominal at {avg_rtt:.1f} ms across monitored infrastructure.")
        else:
            observations.append(f"Elevated mean latency observed at {avg_rtt:.1f} ms, which may suggest geographic distance or path bufferbloat.")
    else:
        observations.append("Insufficient successful RTT samples to compute mean round-trip latency.")

    # Probe failure & firewall note
    if failed > 0:
        observations.append(
            f"Note: {failed} probe(s) failed or timed out. Probe failures do not necessarily indicate host downtime, "
            "as active ICMP echo or TCP SYN requests may be intentionally filtered or rate-limited by upstream perimeter firewalls."
        )

    # Anomaly records note
    if anomalies > 0:
        observations.append(
            f"A total of {anomalies} autonomous anomaly event(s) have been flagged by the statistical detector for operational review."
        )
    else:
        observations.append("Zero threshold-breaching anomaly events have been logged.")

    return " ".join(observations)




