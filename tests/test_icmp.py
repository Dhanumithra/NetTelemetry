import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from network.icmp_monitor import ping, ip_to_dword, ping_target
from network.target_manager import resolve_target, validate_target
from telemetry.collector import probe_all_targets
from database.db import seed_default_data, get_target_latest_status

class TestIcmpMonitor(unittest.TestCase):

    def test_ip_to_dword(self):
        # 127.0.0.1 in network byte order hex: 0x0100007f
        dword = ip_to_dword("127.0.0.1")
        self.assertIsInstance(dword, int)

    def test_ping_localhost(self):
        res = ping("127.0.0.1", timeout_ms=1000)
        self.assertEqual(res["status"], "Success")
        self.assertIsNotNone(res["rtt_ms"])

    def test_ping_google_dns(self):
        res = ping("8.8.8.8", timeout_ms=2000)
        self.assertEqual(res["status"], "Success")
        self.assertIsNotNone(res["rtt_ms"])
        self.assertGreater(res["ttl"], 0)


class TestICMPAndCollector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = "test_icmp_telemetry.db"
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except Exception:
                pass
        seed_default_data(cls.test_db)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except Exception:
                pass

    def test_target_manager_resolution(self):
        ip = resolve_target("8.8.8.8")
        self.assertEqual(ip, "8.8.8.8")

    def test_target_manager_validation(self):
        valid_t = {"name": "Test", "host": "127.0.0.1", "enabled": True, "interval": 5, "timeout": 2}
        invalid_t = {"name": "Test", "host": "127.0.0.1"}
        self.assertTrue(validate_target(valid_t))
        self.assertFalse(validate_target(invalid_t))

    def test_ping_target_reachable(self):
        res = ping_target("127.0.0.1", timeout_sec=2)
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["rtt_ms"])

    def test_collector_probing(self):
        results = probe_all_targets(db_path=self.test_db)
        self.assertTrue(len(results) > 0)
        statuses = get_target_latest_status(db_path=self.test_db)
        self.assertEqual(len(statuses), 5)


if __name__ == "__main__":
    unittest.main()
