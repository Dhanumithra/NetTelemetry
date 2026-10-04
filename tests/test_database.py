import os
import sqlite3
import tempfile
import unittest
from database.db import get_connection, init_db, insert_target, insert_measurement, get_measurements, get_target_by_host

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # TEST 8: Use temporary SQLite database for clean test isolation
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_01_db_initialization(self):
        """TEST 1 — Database initialization"""
        init_db(db_path=self.db_path)
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row["name"] for row in cursor.fetchall()]
            self.assertIn("targets", tables)
            self.assertIn("measurements", tables)

    def test_02_target_insertion(self):
        """TEST 2 — Target insertion and retrieval"""
        init_db(db_path=self.db_path)
        target = {
            "name": "Test Localhost",
            "host": "127.0.0.1",
            "resolved_ip": "127.0.0.1",
            "enabled": True,
            "interval": 5,
            "timeout": 2
        }
        target_id = insert_target(target, db_path=self.db_path)
        self.assertIsNotNone(target_id)

        retrieved = get_target_by_host("127.0.0.1", db_path=self.db_path)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Test Localhost")
        self.assertEqual(retrieved["host"], "127.0.0.1")

    def test_03_successful_measurement_insertion(self):
        """TEST 3 — Successful measurement insertion"""
        init_db(db_path=self.db_path)
        target_id = insert_target({"name": "Localhost", "host": "127.0.0.1"}, db_path=self.db_path)

        measurement = {
            "timestamp": "2026-10-04T12:00:00",
            "target": "127.0.0.1",
            "protocol": "ICMP",
            "test_type": "echo",
            "success": True,
            "rtt_ms": 1.2,
            "ttl": 128,
            "error": None
        }

        meas_id = insert_measurement(measurement, db_path=self.db_path)
        self.assertIsNotNone(meas_id)

        measurements = get_measurements(target_id=target_id, db_path=self.db_path)
        self.assertEqual(len(measurements), 1)
        m = measurements[0]
        self.assertEqual(m["success"], 1)
        self.assertEqual(m["rtt_ms"], 1.2)
        self.assertEqual(m["ttl"], 128)
        self.assertIsNone(m["error"])

    def test_04_failed_measurement_insertion(self):
        """TEST 4 — Failed measurement insertion"""
        init_db(db_path=self.db_path)

        measurement = {
            "timestamp": "2026-10-04T12:00:05",
            "target": "192.0.2.1",
            "protocol": "ICMP",
            "test_type": "echo",
            "success": False,
            "rtt_ms": None,
            "ttl": None,
            "error": "timeout"
        }

        meas_id = insert_measurement(measurement, db_path=self.db_path)
        self.assertIsNotNone(meas_id)

        measurements = get_measurements(db_path=self.db_path)
        self.assertEqual(len(measurements), 1)
        m = measurements[0]
        self.assertEqual(m["success"], 0)
        self.assertIsNone(m["rtt_ms"])
        self.assertIsNone(m["ttl"])
        self.assertEqual(m["error"], "timeout")

    def test_07_sql_safety(self):
        """TEST 7 — SQL injection safety test using string with SQL metacharacters"""
        init_db(db_path=self.db_path)
        malicious_target = {
            "name": "'; DROP TABLE targets; --",
            "host": "127.0.0.1' OR '1'='1",
            "resolved_ip": "127.0.0.1",
            "enabled": True,
            "interval": 5,
            "timeout": 2
        }
        target_id = insert_target(malicious_target, db_path=self.db_path)
        self.assertIsNotNone(target_id)
        
        # Verify tables still exist and database remains intact
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) as cnt FROM targets;")
            self.assertEqual(cursor.fetchone()["cnt"], 1)

if __name__ == "__main__":
    unittest.main()
