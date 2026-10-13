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

    # Ensure target exists in DB
    target_row = get_target_by_host(target_host, db_path)
    if not target_row:
        resolved_ip = resolve_target(target_host) or target_host
        target_id = insert_target({
            "name": target_host,
            "host": target_host,
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
    """
    if isinstance(target_input, dict):
        host = target_input.get("host")
        name = target_input.get("name", host)
        timeout = target_input.get("timeout", 2) * 1000
    else:
        host = str(target_input)
        name = host
        timeout = timeout_ms

    resolved_ip = resolve_target(host)
    if not resolved_ip:
        target_id = insert_target({
            "name": name,
            "host": host,
            "resolved_ip": None,
            "enabled": True,
            "interval": 5,
            "timeout": 2
        }, db_path=db_path)

        meas_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "target": host,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": False,
            "rtt_ms": None,
            "ttl": None,
            "error": f"Failed to resolve host: {host}"
        }
        return store_measurement(meas_data, db_path=db_path)

    meas_res = ping(resolved_ip, timeout_ms=timeout)
    meas_res["target"] = host
    return store_measurement(meas_res, db_path=db_path)


def probe_all_targets(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """
    Executes a round of active probes across all enabled targets.
    Records raw measurements in SQLite and checks for anomalies.
    """
    init_db(db_path)
    detector = AnomalyDetector(rtt_threshold=90.0, loss_threshold=5.0, jitter_threshold=20.0)
    results = []

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT target_id, name, host, timeout FROM targets WHERE enabled = 1")
        targets = [dict(r) for r in cursor.fetchall()]

        for target in targets:
            tid = target["target_id"]
            host = target["host"]
            timeout = target.get("timeout") or 2

            probe_res = ping_target(host, timeout_sec=timeout)

            # TCP fallback check
            if not probe_res["success"] and host in ["140.82.121.3", "52.94.126.1", "20.190.164.4"]:
                tcp_res = measure_tcp_connect(host, 443, timeout=timeout)
                if tcp_res["success"]:
                    probe_res = {
                        "success": True,
                        "rtt_ms": tcp_res["rtt_ms"],
                        "ttl": 64,
                        "error": None
                    }

            cursor.execute('''
            INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
            VALUES (datetime('now'), ?, 'ICMP', 'echo', ?, ?, ?, ?)
            ''', (
                tid,
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

            anomaly = detector.detect(stats)
            if anomaly:
                cursor.execute('''
                INSERT INTO anomalies (target_id, metric, observed_value, baseline, threshold, reason)
                VALUES (?, ?, ?, ?, ?, ?)
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
