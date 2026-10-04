import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from network.tcp_monitor import measure_tcp_connect
from telemetry.metrics import calculate_rolling_statistics

class TestTransportMonitor(unittest.TestCase):
    def test_tcp_connect_success(self):
        result = measure_tcp_connect("google.com", 80)
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["rtt_ms"])
        self.assertIsNone(result["error"])

    def test_tcp_connect_timeout(self):
        # 192.0.2.1 is reserved for documentation and typically drops traffic
        result = measure_tcp_connect("192.0.2.1", 80, timeout=1)
        self.assertFalse(result["success"])
        self.assertIsNone(result["rtt_ms"])
        self.assertEqual(result["error"], "timeout")

class TestMetrics(unittest.TestCase):
    def test_rolling_statistics(self):
        rtt_list = [10.0, 12.0, 15.0, 11.0, 14.0]
        stats = calculate_rolling_statistics(rtt_list, 5, 5)
        self.assertEqual(stats["loss_pct"], 0.0)
        self.assertEqual(stats["availability_pct"], 100.0)
        self.assertTrue(stats["jitter_ms"] > 0)
        self.assertTrue(stats["p95_ms"] > 0)

from analytics.anomaly_detector import AnomalyDetector
from database.db_m2 import init_m2_db, store_window_metrics, store_anomaly
import sqlite3

class TestAnalyticsAndDB(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_telemetry.db"
        init_m2_db(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_anomaly_detection_and_storage(self):
        detector = AnomalyDetector(loss_threshold=5.0)
        metrics = {"loss_pct": 10.0, "p95_ms": 50.0, "jitter_ms": 5.0}
        
        # Test detection
        anomaly = detector.detect(metrics)
        self.assertIsNotNone(anomaly)
        self.assertEqual(anomaly["reason"], "High packet loss detected")
        
        # Test storage
        store_anomaly(self.db_path, "target_1", anomaly)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM anomalies")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][3], "loss_pct") # metric
        conn.close()

if __name__ == "__main__":
    unittest.main()
