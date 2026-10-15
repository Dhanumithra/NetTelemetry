"""
NetTelemetry Live Monitoring Service
Manages real-time background network probing threads without duplicate workers.
"""
import sys
import threading
import time
import datetime
from typing import Dict, Any, Tuple, Optional, List

from database.db import DEFAULT_DB_PATH
from telemetry.collector import probe_all_targets


class TelemetryMonitorService:
    """
    Singleton service that manages background periodic ICMP/TCP telemetry probing.
    Guarantees thread-safe lifecycle control, graceful stops, and duplicate prevention.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._interval_sec: float = 5.0
        self._db_path: str = DEFAULT_DB_PATH
        self._cycle_count: int = 0
        self._last_probe_time: Optional[str] = None
        self._last_results_count: int = 0
        self._last_error: Optional[str] = None
        self._start_time: Optional[str] = None

    def is_running(self) -> bool:
        """Check if background monitoring worker is actively running."""
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def start(self, interval_sec: float = 5.0, db_path: str = DEFAULT_DB_PATH) -> Tuple[bool, str]:
        """
        Start the background monitoring worker thread.
        Prevents starting duplicate workers if already running.
        """
        with self._lock:
            self._interval_sec = max(1.0, float(interval_sec))
            self._db_path = db_path

            if self._thread is not None and self._thread.is_alive():
                return True, f"Monitoring already running (Interval: {self._interval_sec}s)."

            self._stop_event.clear()
            self._start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._last_error = None

            self._thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name="NetTelemetry-Worker"
            )
            self._thread.start()
            return True, f"Monitoring started (Interval: {self._interval_sec}s)."

    def stop(self, timeout: float = 3.0) -> Tuple[bool, str]:
        """
        Safely signals and terminates the background monitoring worker.
        """
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                return True, "Monitoring is not currently running."

            self._stop_event.set()
            thread_to_stop = self._thread
            self._thread = None

        # Wait for thread to finish outside lock
        if thread_to_stop and thread_to_stop != threading.current_thread():
            thread_to_stop.join(timeout=timeout)

        return True, "Monitoring stopped cleanly."

    def get_status(self) -> Dict[str, Any]:
        """Return real-time diagnostic status of the monitoring engine."""
        with self._lock:
            active = self._thread is not None and self._thread.is_alive()
            return {
                "is_running": active,
                "interval_sec": self._interval_sec,
                "cycle_count": self._cycle_count,
                "start_time": self._start_time,
                "last_probe_time": self._last_probe_time,
                "last_results_count": self._last_results_count,
                "last_error": self._last_error
            }

    def _worker_loop(self):
        """Internal daemon loop executing periodic network telemetry probes."""
        while not self._stop_event.is_set():
            cycle_start = time.time()
            try:
                results = probe_all_targets(db_path=self._db_path)
                with self._lock:
                    self._cycle_count += 1
                    self._last_probe_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self._last_results_count = len(results)
                    self._last_error = None
            except Exception as e:
                with self._lock:
                    self._last_error = str(e)

            # Sleep remaining interval or wake immediately on stop
            elapsed = time.time() - cycle_start
            sleep_time = max(0.1, self._interval_sec - elapsed)
            if self._stop_event.wait(timeout=sleep_time):
                break


def get_monitor_service() -> TelemetryMonitorService:
    """
    Returns the process-wide TelemetryMonitorService singleton instance.
    Attaches to sys to survive module reloads safely.
    """
    if not hasattr(sys, "_net_telemetry_monitor"):
        sys._net_telemetry_monitor = TelemetryMonitorService()
    return sys._net_telemetry_monitor


def start_monitoring(interval_sec: float = 5.0, db_path: str = DEFAULT_DB_PATH) -> Tuple[bool, str]:
    return get_monitor_service().start(interval_sec=interval_sec, db_path=db_path)


def stop_monitoring() -> Tuple[bool, str]:
    return get_monitor_service().stop()


def is_monitoring_running() -> bool:
    return get_monitor_service().is_running()


def get_monitoring_status() -> Dict[str, Any]:
    return get_monitor_service().get_status()
