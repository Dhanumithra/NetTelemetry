from database.db import DEFAULT_DB_PATH, insert_measurement, insert_target, get_target_by_host
from network.icmp_monitor import ping
from network.target_manager import resolve_target


def store_measurement(measurement_dict, db_path=DEFAULT_DB_PATH):
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
        # Auto-register target
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

    # Copy measurement dict and set target_id
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
        # Handle unresolvable host
        target_id = insert_target({
            "name": name,
            "host": host,
            "resolved_ip": None,
            "enabled": True,
            "interval": 5,
            "timeout": 2
        }, db_path=db_path)

        meas_data = {
            "timestamp": None,
            "target": host,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": False,
            "rtt_ms": None,
            "ttl": None,
            "error": f"Failed to resolve host: {host}"
        }
        return store_measurement(meas_data, db_path=db_path)

    # Perform ping
    meas_res = ping(resolved_ip, timeout_ms=timeout)
    # Standardize target to original host/IP requested
    meas_res["target"] = host

    # Store in database
    return store_measurement(meas_res, db_path=db_path)
