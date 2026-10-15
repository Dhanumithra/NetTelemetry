import time
import datetime
from typing import Dict, Any, List
from database.db import DEFAULT_DB_PATH, DB_PATH, insert_measurement, insert_target, get_target_by_host, get_connection, init_db
from network.icmp_monitor import ping, ping_target
from network.target_manager import resolve_target
from network.tcp_monitor import measure_tcp_connect
from telemetry.metrics import calculate_rolling_statistics
from analytics.anomaly_detector import AnomalyDetector


def store_measurement(measurement_dict: Dict[str, Any], db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Store a structured measurement dictionary into SQLite.
    Resolves/registers the target host/IP in the targets table if necessary.
    """
    target_host = measurement_dict.get("target")
    if not target_host:
        return {"success": False, "error": "Measurement dict missing 'target' field"}

    from network.target_manager import validate_hostname_or_ip, normalize_target_host
    is_valid, val_err = validate_hostname_or_ip(target_host)
    if not is_valid:
        return {"success": False, "error": f"Invalid target address: {val_err}"}

    clean_host = normalize_target_host(target_host)

    # Ensure target exists in DB
    target_row = get_target_by_host(clean_host, db_path)
    if not target_row:
        resolved_ip = resolve_target(clean_host) or clean_host
        target_id = insert_target({
            "name": clean_host,
            "host": clean_host,
            "resolved_ip": resolved_ip,
            "enabled": True,
            "interval": 5,
            "timeout": 2
        }, db_path=db_path)
    else:
        target_id = target_row["target_id"]

    meas_data = dict(measurement_dict)
    meas_data["target_id"] = target_id

    try:
        measurement_id = insert_measurement(meas_data, db_path=db_path)
        return {
            "success": True,
            "measurement_id": measurement_id,
            "target_id": target_id,
            "data": meas_data
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def collect_icmp_target(target_input, timeout_ms=1000, db_path=DEFAULT_DB_PATH):
    """
    Bridge function: executes ICMP ping for a target host/dict and stores result in SQLite.
    Strictly validates target host format before inserting or probing.
    """
    if isinstance(target_input, dict):
        host = target_input.get("host")
        name = target_input.get("name", host)
        timeout = target_input.get("timeout", 2) * 1000
    else:
        host = str(target_input)
        name = host
        timeout = timeout_ms

    from network.target_manager import validate_hostname_or_ip, normalize_target_host
    is_valid, val_err = validate_hostname_or_ip(host)
    if not is_valid:
        return {
            "success": False,
            "error": val_err,
            "target": host
        }

    clean_host = normalize_target_host(host)
    resolved_ip = resolve_target(clean_host)
    if not resolved_ip:
        target_row = get_target_by_host(clean_host, db_path)
        if target_row:
            target_id = target_row["target_id"]
        else:
            target_id = insert_target({
                "name": name,
                "host": clean_host,
                "resolved_ip": None,
                "enabled": True,
                "interval": 5,
                "timeout": 2
            }, db_path=db_path)

        meas_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "target": clean_host,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": False,
            "rtt_ms": None,
            "ttl": None,
            "error": f"Failed to resolve host: {clean_host}"
        }
        return store_measurement(meas_data, db_path=db_path)

    meas_res = ping(resolved_ip, timeout_ms=timeout)
    meas_res["target"] = clean_host
    return store_measurement(meas_res, db_path=db_path)


from concurrent.futures import ThreadPoolExecutor

def _probe_single_target(target: Dict[str, Any]) -> Dict[str, Any]:
    tid = target.get("target_id")
    host = target.get("host", "")
    timeout = min(float(target.get("timeout") or 1.2), 1.2)

    from network.target_manager import validate_hostname_or_ip
    is_valid, val_err = validate_hostname_or_ip(host)
    if not is_valid:
        return {
            "target_id": tid,
            "host": host,
            "probe": {
                "success": False,
                "rtt_ms": None,
                "ttl": None,
                "error": f"Invalid target address: {val_err}",
                "protocol": "ICMP"
            }
        }

    try:
        probe_res = ping_target(host, timeout_sec=timeout)
        proto = "ICMP"

        # Safe TCP connect check for web/cloud targets if ICMP ping failed
        if not probe_res.get("success"):
            try:
                tcp_res = measure_tcp_connect(host, 443, timeout=min(timeout, 1.0))
                if tcp_res.get("success"):
                    probe_res = {
                        "success": True,
                        "rtt_ms": tcp_res["rtt_ms"],
                        "ttl": 64,
                        "error": None
                    }
                    proto = "TCP"
            except Exception:
                pass

        probe_res["protocol"] = proto
        return {
            "target_id": tid,
            "host": host,
            "probe": probe_res
        }
    except Exception as e:
        return {
            "target_id": tid,
            "host": host,
            "probe": {
                "success": False,
                "rtt_ms": None,
                "ttl": None,
                "error": str(e),
                "protocol": "ICMP"
            }
        }


def probe_all_targets(db_path: str = DEFAULT_DB_PATH, detector: Any = None) -> List[Dict[str, Any]]:
    """
    Executes a round of active probes across all enabled targets concurrently.
    Records raw measurements and window statistics in SQLite, and flags real anomalies.
    Skips any targets with invalid hostname/IP formats (e.g. legacy invalid entries).
    """
    init_db(db_path)
    if detector is None:
        detector = AnomalyDetector()
    results = []

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT target_id, name, host, timeout FROM targets WHERE enabled = 1")
        raw_targets = [dict(r) for r in cursor.fetchall()]

        from network.target_manager import validate_hostname_or_ip
        targets = [t for t in raw_targets if validate_hostname_or_ip(t.get("host", ""))[0]]

        if not targets:
            return []

        # Execute network pings in parallel
        max_workers = min(len(targets), 8)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            probed_list = list(executor.map(_probe_single_target, targets))

        now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in probed_list:
            tid = item["target_id"]
            host = item["host"]
            probe_res = item["probe"]
            proto = probe_res.get("protocol", "ICMP")

            cursor.execute('''
            INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
            VALUES (?, ?, ?, 'echo', ?, ?, ?, ?)
            ''', (
                now_ts,
                tid,
                proto,
                1 if probe_res["success"] else 0,
                probe_res.get("rtt_ms"),
                probe_res.get("ttl"),
                probe_res.get("error")
            ))

            cursor.execute('''
            SELECT rtt_ms, success FROM measurements
            WHERE target_id = ?
            ORDER BY id DESC LIMIT 20
            ''', (tid,))
            recent = cursor.fetchall()
            total = len(recent)
            successful = sum(1 for r in recent if r["success"] == 1)
            rtt_list = [r["rtt_ms"] for r in recent if r["success"] == 1 and r["rtt_ms"] is not None]

            stats = calculate_rolling_statistics(rtt_list, total, successful)

            # Record window metrics into SQLite
            cursor.execute('''
            INSERT INTO window_metrics (target_id, start_time, end_time, loss_pct, availability_pct, jitter_ms, p95_ms, p99_ms)
            VALUES (?, datetime('now', '-1 minute'), datetime('now'), ?, ?, ?, ?, ?)
            ''', (
                str(tid),
                stats["loss_pct"],
                stats["availability_pct"],
                stats["jitter_ms"],
                stats["p95_ms"],
                stats["p99_ms"]
            ))

            # Evaluate real anomalies against configured detection rules
            anomaly = detector.detect(stats)
            if anomaly:
                cursor.execute('''
                SELECT id FROM anomalies 
                WHERE target_id = ? AND metric = ? AND timestamp >= datetime('now', '-60 seconds')
                LIMIT 1
                ''', (str(tid), anomaly["metric"]))
                if not cursor.fetchone():
                    cursor.execute('''
                    INSERT INTO anomalies (timestamp, target_id, metric, observed_value, baseline, threshold, reason)
                    VALUES (datetime('now'), ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(tid),
                        anomaly["metric"],
                        anomaly["observed_value"],
                        anomaly["baseline"],
                        anomaly["threshold"],
                        anomaly["reason"]
                    ))

            results.append({
                "target_id": tid,
                "host": host,
                "probe": probe_res,
                "stats": stats
            })

        conn.commit()

    return results
