import argparse
import os
import sys
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import DEFAULT_DB_PATH
from network.target_manager import load_targets
from telemetry.collector import collect_icmp_target


def run_single_cycle(targets, db_path=DEFAULT_DB_PATH, collector_func=collect_icmp_target):
    """
    Execute one collection cycle across all enabled targets.
    Fault-tolerant: a failure on one target or collector error will not crash the cycle.
    Returns a dict with processed target counts and results.
    """
    processed = 0
    skipped = 0
    results = []

    for target in targets:
        if not target.get("enabled", True):
            skipped += 1
            continue

        try:
            res = collector_func(target, db_path=db_path)
            results.append({"target": target.get("host"), "result": res})
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
                       collector_func=collect_icmp_target):
    """
    Continuous telemetry loop that probes enabled targets at configured intervals.
    - count: Number of cycles to run (None for infinite loop).
    - interval_override: Override sleep interval (useful for tests).
    - sleep_func: Function used to pause between cycles (useful for mocking).
    """
    cycles_completed = 0

    print(f"[Runner] Starting NetTelemetry ICMP runner (Config: '{config_path}')...")

    try:
        while True:
            # 1. Load targets from configuration
            raw_targets = load_targets(config_path)

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

            # 3. Check loop exit condition
            if count is not None and cycles_completed >= count:
                print(f"[Runner] Completed {cycles_completed} cycle(s). Stopping.")
                break

            # 4. Wait for next interval
            if sleep_seconds > 0:
                sleep_func(sleep_seconds)

    except KeyboardInterrupt:
        print("\n[Runner] Received Ctrl+C / Stop signal. Exiting cleanly.")
    except Exception as e:
        print(f"\n[Runner Error] Unexpected error in telemetry loop: {e}")

    return cycles_completed


def main():
    parser = argparse.ArgumentParser(description="NetTelemetry ICMP Continuous Collection Runner")
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
            interval_override=args.interval
        )
    except KeyboardInterrupt:
        print("\n[Runner] Exiting cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
