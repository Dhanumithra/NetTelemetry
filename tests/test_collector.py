import os
import tempfile
import unittest
from database.db import init_db, get_measurements, get_target_by_host
from telemetry.collector import collect_icmp_target, store_measurement

class TestCollector(unittest.TestCase):

    def setUp(self):
        # TEST 8: Isolated test database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_05_collector_integration_localhost(self):
        """TEST 5 — Collector integration flow: target -> ICMP monitor -> collector -> SQLite"""
        res = collect_icmp_target("127.0.0.1", timeout_ms=1000, db_path=self.db_path)
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["measurement_id"])

        # Verify target auto-registration
        target = get_target_by_host("127.0.0.1", db_path=self.db_path)
        self.assertIsNotNone(target)

        # Verify measurement record in database
        measurements = get_measurements(target_id=res["target_id"], db_path=self.db_path)
        self.assertEqual(len(measurements), 1)
        meas = measurements[0]
        self.assertEqual(meas["success"], 1)
        self.assertEqual(meas["protocol"], "ICMP")
        self.assertEqual(meas["test_type"], "echo")
        self.assertIsNotNone(meas["rtt_ms"])

    def test_store_structured_measurement_direct(self):
        sample = {
            "timestamp": "2026-10-04T18:00:00",
            "target": "8.8.8.8",
            "protocol": "ICMP",
            "test_type": "echo",
            "success": True,
            "rtt_ms": 25.5,
            "ttl": 115,
            "error": None
        }
        res = store_measurement(sample, db_path=self.db_path)
        self.assertTrue(res["success"])

        measurements = get_measurements(db_path=self.db_path)
        self.assertEqual(len(measurements), 1)
        self.assertEqual(measurements[0]["rtt_ms"], 25.5)

if __name__ == "__main__":
    unittest.main()
