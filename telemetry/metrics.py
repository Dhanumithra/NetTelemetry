from typing import List, Dict, Any
import math

from database.db import DEFAULT_DB_PATH, get_measurements_for_window


def _parse_success(probe):
    """
    Safely extract boolean success status from probe input.
    Returns True for success, False for failure, None if invalid.
    """
    if isinstance(probe, dict):
        val = probe.get("success")
    elif hasattr(probe, "keys") and "success" in probe:
        val = probe["success"]
    elif isinstance(probe, bool):
        val = probe
    elif isinstance(probe, int):
        val = probe
    else:
        val = getattr(probe, "success", None)

    if val is True or val == 1:
        return True
    elif val is False or val == 0:
        return False
    else:
        return None


def calculate_window_metrics(measurements):
    """
    Calculate aggregated window metrics including packet loss
    and availability.
    """
    if not measurements:
        return {
            "total_probes": 0,
            "successful_probes": 0,
            "failed_probes": 0,
            "packet_loss_pct": None,
            "availability_pct": None
        }

    successful = 0
    failed = 0

    for probe in measurements:
        status = _parse_success(probe)

        if status is True:
            successful += 1
        else:
            failed += 1

    total = successful + failed

    if total == 0:
        return {
            "total_probes": 0,
            "successful_probes": 0,
            "failed_probes": 0,
            "packet_loss_pct": None,
            "availability_pct": None
        }

    packet_loss_pct = (failed / total) * 100.0
    availability_pct = (successful / total) * 100.0

    return {
        "total_probes": total,
        "successful_probes": successful,
        "failed_probes": failed,
        "packet_loss_pct": round(packet_loss_pct, 4),
        "availability_pct": round(availability_pct, 4)
    }


def calculate_packet_loss(measurements):
    """
    Calculate Packet Loss %.

    Formula:
        failed_probes / total_probes * 100
    """
    metrics = calculate_window_metrics(measurements)
    return metrics["packet_loss_pct"]


def calculate_availability(measurements):
    """
    Calculate Availability %.

    Formula:
        successful_probes / total_probes * 100
    """
    metrics = calculate_window_metrics(measurements)
    return metrics["availability_pct"]


def calculate_jitter(rtt_list: List[float]) -> float:
    """
    Calculate jitter as the average absolute difference
    between consecutive successful RTT values.
    """
    if len(rtt_list) < 2:
        return 0.0

    differences = [
        abs(rtt_list[i] - rtt_list[i - 1])
        for i in range(1, len(rtt_list))
    ]

    return sum(differences) / len(differences)


def calculate_percentile(data: List[float], percentile: int) -> float:
    """
    Calculate the given percentile of the data.
    """
    if not data:
        return 0.0

    sorted_data = sorted(data)

    k = (len(sorted_data) - 1) * (percentile / 100.0)
    f = math.floor(k)
    c = math.ceil(k)

    if f == c:
        return sorted_data[int(k)]

    d0 = sorted_data[int(f)] * (c - k)
    d1 = sorted_data[int(c)] * (k - f)

    return d0 + d1


def calculate_rolling_statistics(
    rtt_list: List[float],
    total_probes: int,
    successful_probes: int
) -> Dict[str, Any]:
    """
    Calculate rolling network statistics including:

    - packet loss
    - availability
    - jitter
    - P95 RTT
    - P99 RTT
    """

    loss_pct = (
        (total_probes - successful_probes) / total_probes * 100
        if total_probes > 0
        else 0.0
    )

    availability_pct = (
        successful_probes / total_probes * 100
        if total_probes > 0
        else 0.0
    )

    jitter = calculate_jitter(rtt_list)
    p95 = calculate_percentile(rtt_list, 95)
    p99 = calculate_percentile(rtt_list, 99)

    return {
        "loss_pct": round(loss_pct, 2),
        "availability_pct": round(availability_pct, 2),
        "jitter_ms": round(jitter, 2),
        "p95_ms": round(p95, 2),
        "p99_ms": round(p99, 2)
    }


def get_window_metrics_from_db(
    target_id=None,
    start_time=None,
    end_time=None,
    db_path=DEFAULT_DB_PATH
):
    """
    Query the database for measurements in a time window
    and calculate packet-loss/availability metrics.
    """
    measurements = get_measurements_for_window(
        target_id=target_id,
        start_time=start_time,
        end_time=end_time,
        db_path=db_path
    )

    return calculate_window_metrics(measurements)