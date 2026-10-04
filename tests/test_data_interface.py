import os
import tempfile
import unittest
from database.db import init_db, insert_target, insert_measurement
from telemetry.data_interface import (
    get_recent_measurements,
    get_measurements_for_target,
    get_latest_measurement,
    get_target_measurement_summary
)

class TestDataInterface(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(db_path=self.db_path)

        # Setup deterministic test targets
        self.t1_id = insert_target({"name": "Target 1", "host": "10.0.0.1"}, db_path=self.db_path)
        self.t2_id = insert_target({"name": "Target 2", "host": "10.0.0.2"}, db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_01_recent_measurements(self):
        """TEST 1 — Retrieve recent measurements"""
        insert_measurement({
            "timestamp": "2026-10-04T12:00:00",
            "target_id": self.t1_id,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": True,
            "rtt_ms": 10.0,
            "ttl": 64,
            "error": None
        }, db_path=self.db_path)

        insert_measurement({
            "timestamp": "2026-10-04T12:01:00",
            "target_id": self.t1_id,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": True,
            "rtt_ms": 20.0,
            "ttl": 64,
            "error": None
        }, db_path=self.db_path)

        recent = get_recent_measurements(target_id=self.t1_id, limit=10, db_path=self.db_path)
        self.assertEqual(len(recent), 2)
        # Verify ordering (newest first or properly formatted)
        self.assertIn(recent[0]["rtt_ms"], [10.0, 20.0])

    def test_02_target_filtering(self):
        """TEST 2 — Target filtering"""
        insert_measurement({
            "timestamp": "2026-10-04T12:00:00",
            "target_id": self.t1_id,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": True,
            "rtt_ms": 15.0,
            "ttl": 64,
            "error": None
        }, db_path=self.db_path)

        insert_measurement({
            "timestamp": "2026-10-04T12:00:00",
            "target_id": self.t2_id,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": True,
            "rtt_ms": 25.0,
            "ttl": 64,
            "error": None
        }, db_path=self.db_path)

        t1_meas = get_measurements_for_target(self.t1_id, db_path=self.db_path)
        self.assertEqual(len(t1_meas), 1)
        self.assertEqual(t1_meas[0]["target_id"], self.t1_id)
        self.assertEqual(t1_meas[0]["rtt_ms"], 15.0)

    def test_03_time_window_filtering(self):
        """TEST 3 — Time-window filtering"""
        timestamps = [
            "2026-10-04T10:00:00",
            "2026-10-04T12:00:00",
            "2026-10-04T14:00:00"
        ]
        for ts in timestamps:
            insert_measurement({
                "timestamp": ts,
                "target_id": self.t1_id,
                "protocol": "ICMP",
                "test_type": "echo",
                "success": True,
                "rtt_ms": 10.0,
                "ttl": 64,
                "error": None
            }, db_path=self.db_path)

        window_meas = get_measurements_for_target(
            self.t1_id,
            start_time="2026-10-04T11:00:00",
            end_time="2026-10-04T13:00:00",
            db_path=self.db_path
        )
        self.assertEqual(len(window_meas), 1)
        self.assertEqual(window_meas[0]["timestamp"], "2026-10-04T12:00:00")

    def test_04_latest_measurement(self):
        """TEST 4 — Latest measurement retrieval"""
        insert_measurement({
            "timestamp": "2026-10-04T10:00:00",
            "target_id": self.t1_id,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": True,
            "rtt_ms": 10.0,
            "ttl": 64,
            "error": None
        }, db_path=self.db_path)

        insert_measurement({
            "timestamp": "2026-10-04T15:30:00",
            "target_id": self.t1_id,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": True,
            "rtt_ms": 42.0,
            "ttl": 64,
            "error": None
        }, db_path=self.db_path)

        latest = get_latest_measurement(self.t1_id, db_path=self.db_path)
        self.assertIsNotNone(latest)
        self.assertEqual(latest["timestamp"], "2026-10-04T15:30:00")
        self.assertEqual(latest["rtt_ms"], 42.0)

    def test_05_summary_calculation(self):
        """TEST 5 — Summary calculation with deterministic data"""
        # Insert 3 successful (RTTs: 10, 20, 30 -> Avg 20.0) and 1 failed
        rtts = [10.0, 20.0, 30.0]
        for i, rtt in enumerate(rtts):
            insert_measurement({
                "timestamp": f"2026-10-04T12:0{i}:00",
                "target_id": self.t1_id,
                "protocol": "ICMP",
                "test_type": "echo",
                "success": True,
                "rtt_ms": rtt,
                "ttl": 64,
                "error": None
            }, db_path=self.db_path)

        insert_measurement({
            "timestamp": "2026-10-04T12:05:00",
            "target_id": self.t1_id,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": False,
            "rtt_ms": None,
            "ttl": None,
            "error": "timeout"
        }, db_path=self.db_path)

        summary = get_target_measurement_summary(self.t1_id, db_path=self.db_path)
        self.assertEqual(summary["total_measurements"], 4)
        self.assertEqual(summary["successful_measurements"], 3)
        self.assertEqual(summary["failed_measurements"], 1)
        self.assertEqual(summary["packet_loss_pct"], 25.0)
        self.assertEqual(summary["availability_pct"], 75.0)
        self.assertEqual(summary["avg_rtt_ms"], 20.0)
        self.assertEqual(summary["latest_timestamp"], "2026-10-04T12:05:00")

    def test_06_empty_data_handling(self):
        """TEST 6 — Safe handling of targets with no measurements"""
        latest = get_latest_measurement(self.t1_id, db_path=self.db_path)
        self.assertIsNone(latest)

        summary = get_target_measurement_summary(self.t1_id, db_path=self.db_path)
        self.assertEqual(summary["total_measurements"], 0)
        self.assertEqual(summary["successful_measurements"], 0)
        self.assertEqual(summary["failed_measurements"], 0)
        self.assertIsNone(summary["packet_loss_pct"])
        self.assertIsNone(summary["availability_pct"])
        self.assertIsNone(summary["avg_rtt_ms"])
        self.assertIsNone(summary["latest_timestamp"])

        non_existent_summary = get_target_measurement_summary(99999, db_path=self.db_path)
        self.assertEqual(non_existent_summary["total_measurements"], 0)

if __name__ == "__main__":
    unittest.main()
