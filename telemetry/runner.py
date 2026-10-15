import argparse
import os
import sys
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import DEFAULT_DB_PATH, get_all_targets
from network.target_manager import load_targets
from telemetry.collector import collect_icmp_target, probe_all_targets


def run_single_cycle(targets, db_path=DEFAULT_DB_PATH, collector_func=collect_icmp_target):
    """
    Execute one collection cycle across all enabled targets.
    Fault-tolerant: a failure on one target or collector error will not crash the cycle.
    Returns a dict with processed target counts and results.
    """
    processed = 0
    skipped = 0
    results = []

    from network.target_manager import validate_hostname_or_ip

    for target in targets:
        if not target.get("enabled", True):
            skipped += 1
            continue

        host = target.get("host", "")
        is_valid, _ = validate_hostname_or_ip(host)
        if not is_valid:
            skipped += 1
            continue

        try:
            res = collector_func(target, db_path=db_path)
            results.append({"target": host, "result": res})
            processed += 1
        except Exception as e:
            print(f"[Runner Warning] Error collecting target '{target.get('host')}': {e}")
            results.append({"target": target.get("host"), "error": str(e)})

    return {
        "processed": processed,
        "skipped": skipped,
        "results": results
    }


def run_telemetry_loop(config_path="config.json",
                       db_path=DEFAULT_DB_PATH,
                       count=None,
                       interval_override=None,
                       sleep_func=time.sleep,
                       collector_func=collect_icmp_target,
                       stop_event=None,
                       source="auto"):
    """
    Continuous telemetry loop that probes enabled targets at configured intervals.
    - count: Number of cycles to run (None for infinite loop).
    - interval_override: Override sleep interval (useful for tests).
    - sleep_func: Function used to pause between cycles (useful for mocking).
    - stop_event: Optional threading.Event to cleanly stop the loop.
    - source: 'db', 'config', or 'auto' (prefers DB targets if available).
    """
    cycles_completed = 0

    print(f"[Runner] Starting NetTelemetry ICMP runner (Source: '{source}', DB: '{db_path}')...")

    try:
        while True:
            if stop_event and stop_event.is_set():
                print("[Runner] Stop event signaled. Exiting loop.")
                break

            # 1. Load targets from database or configuration file
            if source == "db":
                raw_targets = [t for t in get_all_targets(db_path) if t.get("enabled", True)]
            elif source == "config":
                raw_targets = load_targets(config_path)
            else:  # auto
                db_targets = [t for t in get_all_targets(db_path) if t.get("enabled", True)]
                if db_targets:
                    raw_targets = db_targets
                elif os.path.exists(config_path):
                    raw_targets = load_targets(config_path)
                else:
                    raw_targets = []

            # 2. Run one measurement cycle
            cycle_summary = run_single_cycle(raw_targets, db_path=db_path, collector_func=collector_func)
            cycles_completed += 1

            # Determine sleep interval (use minimum interval of enabled targets or override)
            enabled_targets = [t for t in raw_targets if t.get("enabled", True)]
            if interval_override is not None:
                sleep_seconds = interval_override
            elif enabled_targets:
                sleep_seconds = min(t.get("interval", 5) for t in enabled_targets)
            else:
                sleep_seconds = 5

            now_str = time.strftime("%H:%M:%S")
            print(f"[{now_str}] Cycle #{cycles_completed}: Processed {cycle_summary['processed']} targets (Skipped {cycle_summary['skipped']}). Next in {sleep_seconds}s.")

            # 3. Check loop exit condition
            if count is not None and cycles_completed >= count:
                print(f"[Runner] Completed {cycles_completed} cycle(s). Stopping.")
                break

            # 4. Wait for next interval
            if sleep_seconds > 0:
                if stop_event:
                    if stop_event.wait(timeout=sleep_seconds):
                        break
                else:
                    sleep_func(sleep_seconds)

    except KeyboardInterrupt:
        print("\n[Runner] Received Ctrl+C / Stop signal. Exiting cleanly.")
    except Exception as e:
        print(f"\n[Runner Error] Unexpected error in telemetry loop: {e}")

    return cycles_completed


def main():
    parser = argparse.ArgumentParser(description="NetTelemetry Continuous Network Monitoring Runner")
    parser.add_argument("--source", choices=["db", "config", "auto"], default="db", help="Target source: 'db' (SQLite targets), 'config' (config.json), or 'auto'")
    parser.add_argument("--config", default="config.json", help="Path to configuration JSON file")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to SQLite database file")
    parser.add_argument("--count", type=int, default=None, help="Number of measurement cycles to run before stopping")
    parser.add_argument("--interval", type=float, default=None, help="Override sleep interval between cycles (seconds)")

    args = parser.parse_args()

    try:
        run_telemetry_loop(
            config_path=args.config,
            db_path=args.db,
            count=args.count,
            interval_override=args.interval,
            source=args.source
        )
    except KeyboardInterrupt:
        print("\n[Runner] Exiting cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
