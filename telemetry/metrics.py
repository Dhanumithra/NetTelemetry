from typing import List, Dict, Any
import math

def calculate_jitter(rtt_list: List[float]) -> float:
    """
    Calculates jitter as the average absolute difference between consecutive successful RTT values.
    """
    if len(rtt_list) < 2:
        return 0.0
    
    differences = [abs(rtt_list[i] - rtt_list[i-1]) for i in range(1, len(rtt_list))]
    return sum(differences) / len(differences)

def calculate_percentile(data: List[float], percentile: int) -> float:
    """
    Calculates the given percentile of the data.
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

def calculate_rolling_statistics(rtt_list: List[float], total_probes: int, successful_probes: int) -> Dict[str, Any]:
    """
    Calculates rolling statistics including packet loss, availability, jitter, P95, and P99.
    """
    loss_pct = ((total_probes - successful_probes) / total_probes * 100) if total_probes > 0 else 0.0
    availability_pct = (successful_probes / total_probes * 100) if total_probes > 0 else 0.0
    
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
