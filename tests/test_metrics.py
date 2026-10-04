import os
import tempfile
import unittest
from database.db import init_db, insert_target, insert_measurement
from telemetry.metrics import (
    calculate_packet_loss,
    calculate_availability,
    calculate_window_metrics,
    get_window_metrics_from_db
)

class TestMetrics(unittest.TestCase):

    def test_01_all_successful_probes(self):
        """TEST 1: 10 successful probes -> loss = 0%, avail = 100%"""
        probes = [{"success": True} for _ in range(10)]
        metrics = calculate_window_metrics(probes)
        self.assertEqual(metrics["total_probes"], 10)
        self.assertEqual(metrics["successful_probes"], 10)
        self.assertEqual(metrics["failed_probes"], 0)
        self.assertEqual(metrics["packet_loss_pct"], 0.0)
        self.assertEqual(metrics["availability_pct"], 100.0)
        self.assertEqual(calculate_packet_loss(probes), 0.0)
        self.assertEqual(calculate_availability(probes), 100.0)

    def test_02_all_failed_probes(self):
        """TEST 2: 10 failed probes -> loss = 100%, avail = 0%"""
        probes = [{"success": False} for _ in range(10)]
        metrics = calculate_window_metrics(probes)
        self.assertEqual(metrics["total_probes"], 10)
        self.assertEqual(metrics["successful_probes"], 0)
        self.assertEqual(metrics["failed_probes"], 10)
        self.assertEqual(metrics["packet_loss_pct"], 100.0)
        self.assertEqual(metrics["availability_pct"], 0.0)

    def test_03_mixed_probes_8_2(self):
        """TEST 3: 8 successful + 2 failed -> loss = 20%, avail = 80%"""
        probes = [{"success": True} for _ in range(8)] + [{"success": False} for _ in range(2)]
        metrics = calculate_window_metrics(probes)
        self.assertEqual(metrics["total_probes"], 10)
        self.assertEqual(metrics["successful_probes"], 8)
        self.assertEqual(metrics["failed_probes"], 2)
        self.assertEqual(metrics["packet_loss_pct"], 20.0)
        self.assertEqual(metrics["availability_pct"], 80.0)

    def test_04_mixed_probes_1_1(self):
        """TEST 4: 1 successful + 1 failed -> loss = 50%, avail = 50%"""
        probes = [{"success": True}, {"success": False}]
        metrics = calculate_window_metrics(probes)
        self.assertEqual(metrics["total_probes"], 2)
        self.assertEqual(metrics["successful_probes"], 1)
        self.assertEqual(metrics["failed_probes"], 1)
        self.assertEqual(metrics["packet_loss_pct"], 50.0)
        self.assertEqual(metrics["availability_pct"], 50.0)

    def test_05_no_measurements(self):
        """TEST 5: No measurements -> loss = None, avail = None (no zero division)"""
        metrics = calculate_window_metrics([])
        self.assertEqual(metrics["total_probes"], 0)
        self.assertEqual(metrics["successful_probes"], 0)
        self.assertEqual(metrics["failed_probes"], 0)
        self.assertIsNone(metrics["packet_loss_pct"])
        self.assertIsNone(metrics["availability_pct"])
        self.assertIsNone(calculate_packet_loss([]))
        self.assertIsNone(calculate_availability([]))

    def test_invalid_missing_values(self):
        """Edge Case: Missing or invalid success field handling"""
        probes = [{"success": True}, {"success": "invalid"}, {}]
        metrics = calculate_window_metrics(probes)
        self.assertEqual(metrics["total_probes"], 3)
        self.assertEqual(metrics["successful_probes"], 1)
        self.assertEqual(metrics["failed_probes"], 2)

    def test_single_measurement(self):
        """Edge Case: Single measurement probe"""
        metrics = calculate_window_metrics([{"success": True}])
        self.assertEqual(metrics["packet_loss_pct"], 0.0)
        self.assertEqual(metrics["availability_pct"], 100.0)

        metrics_fail = calculate_window_metrics([{"success": False}])
        self.assertEqual(metrics_fail["packet_loss_pct"], 100.0)
        self.assertEqual(metrics_fail["availability_pct"], 0.0)

    def test_06_database_backed_window(self):
        """TEST 6: Database-backed measurement window calculation"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        db_path = temp_db.name

        try:
            init_db(db_path=db_path)
            target_id = insert_target({"name": "Test Host", "host": "10.0.0.1"}, db_path=db_path)

            # Insert 3 successful and 1 failed measurement
            for i in range(3):
                insert_measurement({
                    "timestamp": f"2026-10-04T12:00:0{i}",
                    "target_id": target_id,
                    "protocol": "ICMP",
                    "test_type": "echo",
                    "success": True,
                    "rtt_ms": 15.0,
                    "ttl": 64,
                    "error": None
                }, db_path=db_path)

            insert_measurement({
                "timestamp": "2026-10-04T12:00:04",
                "target_id": target_id,
                "protocol": "ICMP",
                "test_type": "echo",
                "success": False,
                "rtt_ms": None,
                "ttl": None,
                "error": "timeout"
            }, db_path=db_path)

            metrics = get_window_metrics_from_db(target_id=target_id, db_path=db_path)
            self.assertEqual(metrics["total_probes"], 4)
            self.assertEqual(metrics["successful_probes"], 3)
            self.assertEqual(metrics["failed_probes"], 1)
            self.assertEqual(metrics["packet_loss_pct"], 25.0)
            self.assertEqual(metrics["availability_pct"], 75.0)
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

if __name__ == "__main__":
    unittest.main()
