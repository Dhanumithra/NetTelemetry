import unittest
from network.icmp_monitor import ping, ip_to_dword

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

if __name__ == "__main__":
    unittest.main()
