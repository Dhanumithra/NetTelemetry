"""
Comprehensive Unit Tests for NetTelemetry Real-Time Network Monitoring System.
Tests target validation, duplicate target prevention, mocked network probing,
metric updates, anomaly evaluation, and monitoring worker start/stop lifecycle.
"""
import os
import sys
import tempfile
import unittest
import threading
import time
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from network.target_manager import validate_hostname_or_ip
from database.db import (
    init_db,
    insert_target,
    get_connection,
    get_all_targets,
    get_target_latest_status,
    get_active_anomalies,
    target_exists,
    add_target_validated
)
from telemetry.collector import probe_all_targets, _probe_single_target
from telemetry.metrics import calculate_rolling_statistics
from analytics.anomaly_detector import AnomalyDetector
from telemetry.monitor_service import TelemetryMonitorService


class TestRealtimeMonitoring(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    # -------------------------------------------------------------
    # 1. Target Validation Tests
    # -------------------------------------------------------------
    def test_01_target_validation_valid_inputs(self):
        """Test valid IPv4, IPv6, and RFC 1123 hostnames pass validation."""
        valid_cases = [
            "8.8.8.8",
            "127.0.0.1",
            "192.168.1.254",
            "::1",
            "2001:4860:4860::8888",
            "google.com",
            "one.one.one.one",
            "router-01.corp.internal",
            "sub.domain.example.org"
        ]
        for host in valid_cases:
            is_valid, msg = validate_hostname_or_ip(host)
            self.assertTrue(is_valid, f"Expected '{host}' to be valid, got: {msg}")

    def test_02_target_validation_dangerous_and_invalid_inputs(self):
        """Test command injection characters and malformed hostnames are rejected."""
        malicious_and_invalid = [
            "8.8.8.8; whoami",
            "google.com | cat /etc/passwd",
            "127.0.0.1 && dir",
            "192.168.1.1`ls`",
            "$(calc.exe)",
            "test<script>",
            "8.8.8.8 1.1.1.1",
            "google.com\n8.8.8.8",
            "",
            "   ",
            "-invalid.com",
            "invalid..domain.com"
        ]
        for bad_host in malicious_and_invalid:
            is_valid, msg = validate_hostname_or_ip(bad_host)
            self.assertFalse(is_valid, f"Expected '{bad_host}' to be rejected as invalid, but it passed.")

    # -------------------------------------------------------------
    # 2. Duplicate Target Prevention Tests
    # -------------------------------------------------------------
    def test_03_duplicate_target_prevention(self):
        """Test that duplicate host additions are detected and prevented."""
        # Add initial target
        res1 = add_target_validated("Cloudflare Primary", "1.1.1.1", db_path=self.db_path)
        self.assertTrue(res1["success"])
        self.assertIsNotNone(res1.get("target"))

        # Verify target exists in DB
        self.assertTrue(target_exists("1.1.1.1", db_path=self.db_path))

        # Attempt to add exact duplicate
        res2 = add_target_validated("Cloudflare Duplicate", "1.1.1.1", db_path=self.db_path)
        self.assertFalse(res2["success"])
        self.assertIn("already being monitored", res2["error"])

        # Attempt to add duplicate with different case
        res3 = add_target_validated("Cloudflare Uppercase", " 1.1.1.1 ", db_path=self.db_path)
        self.assertFalse(res3["success"])

        # Verify only 1 target exists in database
        targets = get_all_targets(db_path=self.db_path)
        self.assertEqual(len(targets), 1)

    # -------------------------------------------------------------
    # 3. Fault Tolerance & Single Probe Failure Resilience
    # -------------------------------------------------------------
    def test_04_single_probe_failure_does_not_mark_target_offline(self):
        """Test that a single failed probe keeps status Online and does NOT mark target offline."""
        tid = insert_target({"name": "Core Router", "host": "10.0.0.1"}, db_path=self.db_path)

        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            # Insert 9 successful probes
            for i in range(9):
                cursor.execute(
                    "INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl) VALUES (?, ?, 'ICMP', 'echo', 1, 15.0, 64)",
                    (f"2026-10-14 10:0{i}:00", tid)
                )
            # Insert 1 latest failed probe
            cursor.execute(
                "INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error) VALUES ('2026-10-14 10:09:00', ?, 'ICMP', 'echo', 0, NULL, NULL, 'Request timed out')",
                (tid,)
            )
            conn.commit()

        statuses = get_target_latest_status(db_path=self.db_path)
        self.assertEqual(len(statuses), 1)
        st = statuses[0]
        # 1 failure out of 10 = 10.0% loss -> must remain Online!
        self.assertEqual(st["status"], "Online")
        self.assertEqual(st["loss_pct"], 10.0)
        self.assertEqual(st["availability_pct"], 90.0)
        self.assertIsNone(st["rtt_ms"])  # Latest failed probe represents RTT as None
        self.assertIsNotNone(st["avg_rtt_ms"])

    def test_05_persistent_failure_marks_offline(self):
        """Test that a target is only marked Offline when all probes in window fail (loss 100%)."""
        tid = insert_target({"name": "Unresponsive Gateway", "host": "192.0.2.1"}, db_path=self.db_path)

        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            for i in range(5):
                cursor.execute(
                    "INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, error) VALUES (?, ?, 'ICMP', 'echo', 0, NULL, 'Host Unreachable')",
                    (f"2026-10-14 11:0{i}:00", tid)
                )
            conn.commit()

        statuses = get_target_latest_status(db_path=self.db_path)
        st = statuses[0]
        self.assertEqual(st["status"], "Offline")
        self.assertEqual(st["loss_pct"], 100.0)
        self.assertEqual(st["availability_pct"], 0.0)
        self.assertIsNone(st["rtt_ms"])

    # -------------------------------------------------------------
    # 4. Mocked Real-Time Probing, Metrics & Anomaly Detection
    # -------------------------------------------------------------
    @patch("telemetry.collector.ping_target")
    def test_06_mocked_network_probing_metrics_and_anomalies(self, mock_ping):
        """Test live parallel probing with mocked network results, verifying metrics and anomalies."""
        # Setup mock network responses
        mock_ping.side_effect = lambda host, timeout_sec: {
            "success": True,
            "rtt_ms": 125.0 if "latency" in host else 18.0,
            "ttl": 58,
            "error": None
        }

        # Insert 2 targets: 1 normal, 1 with latency spike
        insert_target({"name": "Normal Node", "host": "8.8.8.8"}, db_path=self.db_path)
        insert_target({"name": "Slow Node", "host": "latency.test"}, db_path=self.db_path)

        # Run one active probe cycle
        custom_detector = AnomalyDetector(rtt_threshold=90.0, loss_threshold=5.0, jitter_threshold=20.0)
        results = probe_all_targets(db_path=self.db_path, detector=custom_detector)

        self.assertEqual(len(results), 2)

        # Verify measurements table in SQLite has exactly 2 records
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) as cnt FROM measurements")
            self.assertEqual(cursor.fetchone()["cnt"], 2)

            # Verify window_metrics table has records
            cursor.execute("SELECT count(*) as cnt FROM window_metrics")
            self.assertEqual(cursor.fetchone()["cnt"], 2)

        # Verify anomaly detection: latency spike (125ms > 90ms threshold) was detected and saved
        anomalies = get_active_anomalies(db_path=self.db_path)
        self.assertTrue(len(anomalies) >= 1)
        anom = anomalies[0]
        self.assertEqual(anom["metric"], "p95_ms")
        self.assertEqual(anom["observed_value"], 125.0)
        self.assertIn("spike", anom["reason"].lower())

    # -------------------------------------------------------------
    # 5. Monitoring Worker Lifecycle (Start & Stop) Tests
    # -------------------------------------------------------------
    @patch("telemetry.collector.ping_target")
    def test_07_worker_lifecycle_start_and_stop(self, mock_ping):
        """Verify that starting begins worker, and stopping cleanly stops the worker thread."""
        mock_ping.return_value = {"success": True, "rtt_ms": 20.0, "ttl": 64, "error": None}
        insert_target({"name": "Mock Node", "host": "127.0.0.1"}, db_path=self.db_path)

        service = TelemetryMonitorService()
        self.assertFalse(service.is_running())

        # Start monitoring with fast 0.2s interval for testing
        started, msg = service.start(interval_sec=0.2, db_path=self.db_path)
        self.assertTrue(started)
        self.assertTrue(service.is_running())

        # Calling start again must not create duplicate worker
        started_again, _ = service.start(interval_sec=0.2, db_path=self.db_path)
        self.assertTrue(started_again)

        # Wait briefly for worker to complete at least 1 cycle
        time.sleep(0.5)
        status = service.get_status()
        self.assertTrue(status["is_running"])
        self.assertGreaterEqual(status["cycle_count"], 1)

        # Stop monitoring
        stopped, stop_msg = service.stop(timeout=2.0)
        self.assertTrue(stopped)
        self.assertFalse(service.is_running())

        # Verify thread is dead
        self.assertFalse(service.is_running())

    # -------------------------------------------------------------
    # 6. DNS and Network Exception Resilience Tests
    # -------------------------------------------------------------
    def test_08_dns_failure_and_timeout_resilience(self):
        """Test that unresolvable targets do not crash the probing cycle."""
        target = {"target_id": 99, "host": "nonexistent-domain-xyz-404.invalid", "timeout": 1}
        res = _probe_single_target(target)
        self.assertFalse(res["probe"]["success"])
        self.assertIsNone(res["probe"]["rtt_ms"])
        self.assertIn("DNS resolution failed", res["probe"]["error"])


if __name__ == "__main__":
    unittest.main()
