"""
NetTelemetry Settings & Thresholds Manager
Handles validation, persistence, loading, and resetting of operational anomaly thresholds.
"""
import os
import json
import math
from typing import Dict, Any, Tuple, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")

DEFAULT_THRESHOLDS: Dict[str, float] = {
    "rtt_ms": 90.0,
    "loss_pct": 5.0,
    "jitter_ms": 20.0
}


def validate_thresholds(
    rtt_ms: Any,
    loss_pct: Any,
    jitter_ms: Any
) -> Tuple[bool, List[str]]:
    """
    Validates operational telemetry thresholds:
    - RTT threshold must be a valid positive number (> 0 ms).
    - Packet-loss threshold must be between 0% and 100% (inclusive).
    - Jitter threshold must be a valid non-negative number (>= 0 ms).
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []

    # 1. RTT validation (> 0)
    try:
        if rtt_ms is None or isinstance(rtt_ms, bool):
            errors.append("RTT threshold must be a valid positive number greater than 0 ms.")
        else:
            rtt_val = float(rtt_ms)
            if math.isnan(rtt_val) or math.isinf(rtt_val):
                errors.append("RTT threshold cannot be NaN or infinite.")
            elif rtt_val <= 0.0:
                errors.append("RTT threshold must be a valid positive number greater than 0 ms.")
    except (ValueError, TypeError):
        errors.append("RTT threshold must be a valid numeric value.")

    # 2. Packet loss validation (0 <= loss <= 100)
    try:
        if loss_pct is None or isinstance(loss_pct, bool):
            errors.append("Packet-loss threshold must be a number between 0% and 100%.")
        else:
            loss_val = float(loss_pct)
            if math.isnan(loss_val) or math.isinf(loss_val):
                errors.append("Packet-loss threshold cannot be NaN or infinite.")
            elif loss_val < 0.0 or loss_val > 100.0:
                errors.append("Packet-loss threshold must be between 0% and 100%.")
    except (ValueError, TypeError):
        errors.append("Packet-loss threshold must be a valid numeric value.")

    # 3. Jitter validation (>= 0)
    try:
        if jitter_ms is None or isinstance(jitter_ms, bool):
            errors.append("Jitter threshold must be a non-negative number (0 ms or greater).")
        else:
            jitter_val = float(jitter_ms)
            if math.isnan(jitter_val) or math.isinf(jitter_val):
                errors.append("Jitter threshold cannot be NaN or infinite.")
            elif jitter_val < 0.0:
                errors.append("Jitter threshold must be a non-negative number (0 ms or greater).")
    except (ValueError, TypeError):
        errors.append("Jitter threshold must be a valid numeric value.")

    return len(errors) == 0, errors


def load_thresholds(config_path: Optional[str] = None) -> Dict[str, float]:
    """
    Loads persisted thresholds from config.json.
    Falls back gracefully to default thresholds if the file or keys are missing or invalid.
    """
    path = config_path or DEFAULT_CONFIG_PATH
    if not os.path.isabs(path) and not os.path.exists(path):
        candidate = os.path.join(PROJECT_ROOT, path)
        if os.path.exists(candidate):
            path = candidate

    thresholds = dict(DEFAULT_THRESHOLDS)

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    config = json.loads(content)
                    raw_thresh = config.get("thresholds", {})
                    if isinstance(raw_thresh, dict):
                        if "rtt_ms" in raw_thresh:
                            try:
                                r_val = float(raw_thresh["rtt_ms"])
                                if r_val > 0 and not math.isnan(r_val) and not math.isinf(r_val):
                                    thresholds["rtt_ms"] = r_val
                            except (ValueError, TypeError):
                                pass
                        if "loss_pct" in raw_thresh:
                            try:
                                l_val = float(raw_thresh["loss_pct"])
                                if 0.0 <= l_val <= 100.0 and not math.isnan(l_val) and not math.isinf(l_val):
                                    thresholds["loss_pct"] = l_val
                            except (ValueError, TypeError):
                                pass
                        if "jitter_ms" in raw_thresh:
                            try:
                                j_val = float(raw_thresh["jitter_ms"])
                                if j_val >= 0.0 and not math.isnan(j_val) and not math.isinf(j_val):
                                    thresholds["jitter_ms"] = j_val
                            except (ValueError, TypeError):
                                pass
        except Exception:
            pass

    return thresholds


def save_thresholds(
    thresholds: Dict[str, Any],
    config_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Validates and persists threshold settings to config.json.
    Preserves all other configuration sections (e.g. 'targets').
    Returns (success, message).
    """
    path = config_path or DEFAULT_CONFIG_PATH
    if not os.path.isabs(path) and not os.path.exists(path) and os.path.exists(os.path.join(PROJECT_ROOT, path)):
        path = os.path.join(PROJECT_ROOT, path)

    rtt = thresholds.get("rtt_ms")
    loss = thresholds.get("loss_pct")
    jitter = thresholds.get("jitter_ms")

    is_valid, errors = validate_thresholds(rtt, loss, jitter)
    if not is_valid:
        return False, "Validation failed: " + "; ".join(errors)

    try:
        config = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        config = json.loads(content)
            except Exception:
                config = {}

        if not isinstance(config, dict):
            config = {}

        config["thresholds"] = {
            "rtt_ms": round(float(rtt), 2),
            "loss_pct": round(float(loss), 2),
            "jitter_ms": round(float(jitter), 2)
        }

        dir_path = os.path.dirname(os.path.abspath(path))
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        return True, "Settings saved successfully."
    except Exception as e:
        return False, f"Failed to persist settings to file: {str(e)}"


def reset_thresholds(config_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Restores the project default thresholds and persists them to configuration storage.
    Returns (success, message).
    """
    return save_thresholds(DEFAULT_THRESHOLDS, config_path=config_path)
