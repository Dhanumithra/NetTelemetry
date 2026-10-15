import os
import sqlite3
import tempfile
import unittest
from database.db import get_connection, init_db, migrate_db, insert_target, insert_measurement, get_measurements, get_target_by_host, get_target_latest_status

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # TEST 8: Use temporary SQLite database for clean test isolation
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        import gc
        gc.collect()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

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

    def test_08_fresh_db_initialization_schema(self):
        """TEST 8 — Fresh database initialization creates targets table with lat and lon columns."""
        init_db(db_path=self.db_path)
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(targets);")
            columns = [row["name"] for row in cursor.fetchall()]
            self.assertIn("lat", columns)
            self.assertIn("lon", columns)
            self.assertIn("resolved_ip", columns)

        # Verify insertion and retrieval of target with explicit lat and lon
        target_id = insert_target({
            "name": "Geo Target",
            "host": "93.184.216.34",
            "lat": 42.3601,
            "lon": -71.0589
        }, db_path=self.db_path)
        self.assertIsNotNone(target_id)

        target = get_target_by_host("93.184.216.34", db_path=self.db_path)
        self.assertIsNotNone(target)
        self.assertAlmostEqual(target["lat"], 42.3601)
        self.assertAlmostEqual(target["lon"], -71.0589)

        # Verify insertion without lat and lon defaults to 0.0
        target_id_default = insert_target({
            "name": "Default Target",
            "host": "198.51.100.1"
        }, db_path=self.db_path)
        target_default = get_target_by_host("198.51.100.1", db_path=self.db_path)
        self.assertEqual(target_default["lat"], 0.0)
        self.assertEqual(target_default["lon"], 0.0)

    def test_09_migration_from_legacy_schema(self):
        """TEST 9 — Migration adds missing lat/lon columns to older schema and preserves data."""
        # 1. Create a legacy database without lat and lon columns
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript("""
                CREATE TABLE targets (
                    target_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    host TEXT NOT NULL UNIQUE,
                    resolved_ip TEXT,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    interval INTEGER NOT NULL DEFAULT 5,
                    timeout INTEGER NOT NULL DEFAULT 2
                );
                CREATE TABLE measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    target_id INTEGER NOT NULL,
                    protocol TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    rtt_ms REAL,
                    ttl INTEGER,
                    error TEXT,
                    FOREIGN KEY (target_id) REFERENCES targets (target_id) ON DELETE CASCADE
                );
                INSERT INTO targets (name, host, resolved_ip, enabled, interval, timeout)
                VALUES ('Legacy Target 1', '10.0.0.1', '10.0.0.1', 1, 5, 2);
                INSERT INTO targets (name, host, resolved_ip, enabled, interval, timeout)
                VALUES ('Legacy Target 2', '8.8.8.8', '8.8.8.8', 1, 5, 2);

                INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
                VALUES ('2026-10-04T10:00:00', 1, 'ICMP', 'echo', 1, 24.5, 64, NULL);
                INSERT INTO measurements (timestamp, target_id, protocol, test_type, success, rtt_ms, ttl, error)
                VALUES ('2026-10-04T10:01:00', 2, 'ICMP', 'echo', 1, 15.2, 118, NULL);
            """)
            conn.commit()
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(targets);")
            cols_before = [row[1] for row in cursor.fetchall()]
            self.assertNotIn("lat", cols_before)
            self.assertNotIn("lon", cols_before)
        finally:
            conn.close()

        # 2. Run migration via init_db
        init_db(db_path=self.db_path)

        # 3. Verify columns now exist
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(targets);")
            cols_after = [row["name"] for row in cursor.fetchall()]
            self.assertIn("lat", cols_after)
            self.assertIn("lon", cols_after)

        # 4. Verify existing legacy data is preserved
        t1 = get_target_by_host("10.0.0.1", db_path=self.db_path)
        self.assertIsNotNone(t1)
        self.assertEqual(t1["name"], "Legacy Target 1")
        self.assertEqual(t1["target_id"], 1)
        self.assertEqual(t1["lat"], 0.0)
        self.assertEqual(t1["lon"], 0.0)

        t2 = get_target_by_host("8.8.8.8", db_path=self.db_path)
        self.assertIsNotNone(t2)
        self.assertEqual(t2["target_id"], 2)

        # Verify existing measurements are preserved
        meas_1 = get_measurements(target_id=1, db_path=self.db_path)
        self.assertEqual(len(meas_1), 1)
        self.assertEqual(meas_1[0]["rtt_ms"], 24.5)

        meas_2 = get_measurements(target_id=2, db_path=self.db_path)
        self.assertEqual(len(meas_2), 1)
        self.assertEqual(meas_2[0]["rtt_ms"], 15.2)

        # 5. Verify updating existing target preserves target_id and updates lat/lon
        updated_id = insert_target({
            "name": "Google DNS",
            "host": "8.8.8.8",
            "lat": 37.4220,
            "lon": -122.0841
        }, db_path=self.db_path)
        self.assertEqual(updated_id, 2)
        t2_updated = get_target_by_host("8.8.8.8", db_path=self.db_path)
        self.assertEqual(t2_updated["name"], "Google DNS")
        self.assertAlmostEqual(t2_updated["lat"], 37.4220)
        self.assertAlmostEqual(t2_updated["lon"], -122.0841)

    def test_10_migration_idempotent(self):
        """TEST 10 — Migration and initialization are idempotent and safe to run multiple times."""
        init_db(db_path=self.db_path)
        insert_target({"name": "Target", "host": "1.1.1.1", "lat": 51.5, "lon": -0.12}, db_path=self.db_path)

        # Repeated runs of migrate_db and init_db must not raise errors
        migrate_db(self.db_path)
        migrate_db(self.db_path)
        init_db(db_path=self.db_path)
        init_db(db_path=self.db_path)

        t = get_target_by_host("1.1.1.1", db_path=self.db_path)
        self.assertIsNotNone(t)
        self.assertAlmostEqual(t["lat"], 51.5)
        self.assertAlmostEqual(t["lon"], -0.12)

    def test_11_insert_target_on_unmigrated_db(self):
        """TEST 11 — insert_target auto-migrates if called on an unmigrated database."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript("""
                CREATE TABLE targets (
                    target_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    host TEXT NOT NULL UNIQUE,
                    resolved_ip TEXT,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    interval INTEGER NOT NULL DEFAULT 5,
                    timeout INTEGER NOT NULL DEFAULT 2
                );
            """)
            conn.commit()
        finally:
            conn.close()

        # Call insert_target directly without calling init_db or migrate_db first
        target_id = insert_target({
            "name": "Auto Migrate Target",
            "host": "1.0.0.1",
            "lat": -33.8688,
            "lon": 151.2093
        }, db_path=self.db_path)
        self.assertIsNotNone(target_id)

        t = get_target_by_host("1.0.0.1", db_path=self.db_path)
        self.assertIsNotNone(t)
        self.assertAlmostEqual(t["lat"], -33.8688)
        self.assertAlmostEqual(t["lon"], 151.2093)

    def test_12_target_with_no_measurements_is_marked_unknown(self):
        """TEST 12 — Target with no measurements has status Unknown, neutral color #94a3b8, and None RTT."""
        init_db(db_path=self.db_path)
        insert_target({"name": "Unmeasured Target", "host": "192.0.2.55", "lat": 10.0, "lon": 20.0}, db_path=self.db_path)
        statuses = get_target_latest_status(db_path=self.db_path)
        self.assertEqual(len(statuses), 1)
        st = statuses[0]
        self.assertEqual(st["name"], "Unmeasured Target")
        self.assertEqual(st["status"], "Unknown")
        self.assertEqual(st["status_color"], "#94a3b8")
        self.assertIsNone(st["rtt_ms"])
        self.assertIsNone(st["avg_rtt_ms"])
        self.assertEqual(st["loss_pct"], 0.0)

    def test_13_failed_latest_probe_displays_no_rtt(self):
        """TEST 13 — Failed latest measurement represents RTT as None rather than 0.0."""
        init_db(db_path=self.db_path)
        target_id = insert_target({"name": "Test Host", "host": "192.0.2.100"}, db_path=self.db_path)
        
        # 1. Insert an earlier successful measurement
        insert_measurement({
            "timestamp": "2026-10-14T10:00:00",
            "target_id": target_id,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": True,
            "rtt_ms": 28.5,
            "ttl": 64,
            "error": None
        }, db_path=self.db_path)
        
        # 2. Insert latest measurement as failed (unsuccessful probe)
        insert_measurement({
            "timestamp": "2026-10-14T10:01:00",
            "target_id": target_id,
            "protocol": "ICMP",
            "test_type": "echo",
            "success": False,
            "rtt_ms": None,
            "ttl": None,
            "error": "Request timed out"
        }, db_path=self.db_path)

        statuses = get_target_latest_status(db_path=self.db_path)
        self.assertEqual(len(statuses), 1)
        st = statuses[0]
        self.assertIsNone(st["rtt_ms"])
        self.assertNotEqual(st["rtt_ms"], 0.0)
        self.assertEqual(st["avg_rtt_ms"], 28.5)
        # Verify all target fields preserved
        for field in ["target_id", "name", "host", "resolved_ip", "lat", "lon", "rtt_ms", "avg_rtt_ms", "loss_pct", "status", "status_color"]:
            self.assertIn(field, st)

    def test_14_packet_loss_calculation(self):
        """TEST 14 — Packet loss calculation based on latest 20 measurements."""
        init_db(db_path=self.db_path)
        target_id = insert_target({"name": "Loss Test", "host": "192.0.2.200"}, db_path=self.db_path)

        # Insert 15 successful and 5 failed measurements (total 20 measurements -> 25% loss)
        for i in range(15):
            insert_measurement({
                "timestamp": f"2026-10-14T10:{i:02d}:00",
                "target_id": target_id,
                "protocol": "ICMP",
                "test_type": "echo",
                "success": True,
                "rtt_ms": 20.0,
                "ttl": 64,
                "error": None
            }, db_path=self.db_path)
        
        for i in range(15, 20):
            insert_measurement({
                "timestamp": f"2026-10-14T10:{i:02d}:00",
                "target_id": target_id,
                "protocol": "ICMP",
                "test_type": "echo",
                "success": False,
                "rtt_ms": None,
                "ttl": None,
                "error": "Destination Unreachable"
            }, db_path=self.db_path)

        statuses = get_target_latest_status(db_path=self.db_path)
        self.assertEqual(len(statuses), 1)
        st = statuses[0]
        self.assertEqual(st["loss_pct"], 25.0)
        self.assertIsNone(st["rtt_ms"])  # latest was failed
        self.assertEqual(st["avg_rtt_ms"], 20.0)

        # Now insert 5 more successful measurements (total 25 measurements in DB)
        # Window size is 20, so the oldest 5 successful will roll out.
        # Latest 20 will be: 10 successful (from first batch) + 5 failed (second batch) + 5 successful (third batch)
        # Total in window: 5 failed / 20 = 25.0% loss, but latest measurement is now successful!
        for i in range(20, 25):
            insert_measurement({
                "timestamp": f"2026-10-14T10:{i:02d}:00",
                "target_id": target_id,
                "protocol": "ICMP",
                "test_type": "echo",
                "success": True,
                "rtt_ms": 30.0,
                "ttl": 64,
                "error": None
            }, db_path=self.db_path)

        statuses2 = get_target_latest_status(db_path=self.db_path)
        st2 = statuses2[0]
        self.assertEqual(st2["loss_pct"], 25.0)
        self.assertEqual(st2["rtt_ms"], 30.0)

if __name__ == "__main__":
    unittest.main()

