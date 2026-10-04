from database.db import (
    DEFAULT_DB_PATH,
    get_measurements,
    get_measurements_for_window,
    get_target_by_id,
    get_target_by_host
)
from telemetry.metrics import calculate_window_metrics


def _resolve_target_id(target_id, db_path=DEFAULT_DB_PATH):
    """
    Internal helper to resolve a target_id from either integer ID or host string.
    """
    if isinstance(target_id, str) and not target_id.isdigit():
        target_row = get_target_by_host(target_id, db_path=db_path)
        return target_row["target_id"] if target_row else None
    elif target_id is not None:
        return int(target_id)
    return None


def get_recent_measurements(target_id=None, limit=100, db_path=DEFAULT_DB_PATH):
    """
    Return recent raw measurements for a target or all targets.
    """
    resolved_id = _resolve_target_id(target_id, db_path=db_path) if target_id is not None else None
    if target_id is not None and resolved_id is None:
        return []
    return get_measurements(target_id=resolved_id, limit=limit, db_path=db_path)


def get_measurements_for_target(target_id, start_time=None, end_time=None, limit=1000, db_path=DEFAULT_DB_PATH):
    """
    Return measurements for a specific target within a time range.
    """
    resolved_id = _resolve_target_id(target_id, db_path=db_path)
    if resolved_id is None:
        return []
    return get_measurements_for_window(
        target_id=resolved_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        db_path=db_path
    )


def get_latest_measurement(target_id, db_path=DEFAULT_DB_PATH):
    """
    Return the single most recent measurement dict for a target (or None if no measurements exist).
    """
    resolved_id = _resolve_target_id(target_id, db_path=db_path)
    if resolved_id is None:
        return None
    measurements = get_measurements(target_id=resolved_id, limit=1, db_path=db_path)
    return measurements[0] if measurements else None


def get_target_measurement_summary(target_id, start_time=None, end_time=None, db_path=DEFAULT_DB_PATH):
    """
    Return a compact telemetry summary for a target that future analytics can consume.
    Contains total, successful, failed, packet_loss_pct, availability_pct, avg_rtt_ms, latest_timestamp.
    """
    resolved_id = _resolve_target_id(target_id, db_path=db_path)
    if resolved_id is None:
        return {
            "target_id": target_id,
            "target": None,
            "total_measurements": 0,
            "successful_measurements": 0,
            "failed_measurements": 0,
            "packet_loss_pct": None,
            "availability_pct": None,
            "avg_rtt_ms": None,
            "latest_timestamp": None
        }

    target_info = get_target_by_id(resolved_id, db_path=db_path)
    measurements = get_measurements_for_window(
        target_id=resolved_id,
        start_time=start_time,
        end_time=end_time,
        limit=10000,
        db_path=db_path
    )

    if not measurements:
        return {
            "target_id": resolved_id,
            "target": target_info,
            "total_measurements": 0,
            "successful_measurements": 0,
            "failed_measurements": 0,
            "packet_loss_pct": None,
            "availability_pct": None,
            "avg_rtt_ms": None,
            "latest_timestamp": None
        }

    # Calculate window metrics (total, successful, failed, loss%, availability%)
    window_metrics = calculate_window_metrics(measurements)

    # Average RTT for successful measurements with valid RTT values
    successful_rtts = [
        m["rtt_ms"] for m in measurements
        if (m.get("success") == 1 or m.get("success") is True) and m.get("rtt_ms") is not None
    ]
    avg_rtt_ms = round(sum(successful_rtts) / len(successful_rtts), 4) if successful_rtts else None

    # Latest measurement timestamp
    latest = get_latest_measurement(resolved_id, db_path=db_path)
    latest_timestamp = latest["timestamp"] if latest else None

    return {
        "target_id": resolved_id,
        "target": target_info,
        "total_measurements": window_metrics["total_probes"],
        "successful_measurements": window_metrics["successful_probes"],
        "failed_measurements": window_metrics["failed_probes"],
        "packet_loss_pct": window_metrics["packet_loss_pct"],
        "availability_pct": window_metrics["availability_pct"],
        "avg_rtt_ms": avg_rtt_ms,
        "latest_timestamp": latest_timestamp
    }


if __name__ == "__main__":
    import json
    print("--- NetTelemetry Data Interface Manual Verification ---")
    recent = get_recent_measurements(limit=5)
    print(f"\n[Recent Measurements (Limit 5)]:")
    print(json.dumps(recent, indent=2))

    if recent:
        tid = recent[0]["target_id"]
        print(f"\n[Summary for Target ID {tid}]:")
        summary = get_target_measurement_summary(tid)
        print(json.dumps(summary, indent=2))
    else:
        print("\nNo measurements found in database.")

