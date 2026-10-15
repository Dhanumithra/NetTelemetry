import os
import tempfile
import unittest
import sqlite3
from unittest.mock import patch, MagicMock

from database.db import (
    init_db,
    get_connection,
    get_all_targets,
    target_exists,
    add_target_validated,
    insert_target,
    get_target_by_id
)
from network.target_manager import (
    validate_hostname_or_ip,
    normalize_target_host,
    validate_target
)
from telemetry.collector import (
    collect_icmp_target,
    store_measurement,
    _probe_single_target,
    probe_all_targets
)
from telemetry.runner import run_single_cycle


class TestTargetValidationAndSecurity(unittest.TestCase):
    """
    Comprehensive regression tests for IP address and hostname validation,
    ensuring strict rejection of invalid inputs (such as numeric '1234'),
    safe handling of unreachable hosts, and prevention of side effects.
    """

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # ---------------------------------------------------------
    # Format Validation Unit Tests
    # ---------------------------------------------------------
    def test_01_valid_ipv4_accepted(self):
        """Valid IPv4 addresses must be accepted."""
        for ip in ["1.1.1.1", "8.8.8.8", "127.0.0.1", "192.168.1.1", "10.0.0.254"]:
            is_valid, msg = validate_hostname_or_ip(ip)
            self.assertTrue(is_valid, f"Expected {ip} to be valid, got: {msg}")

    def test_02_valid_ipv6_accepted(self):
        """Valid IPv6 addresses must be accepted."""
        ipv6_samples = [
            "::1",
            "2001:4860:4860::8888",
            "2606:4700:4700::1111",
            "fe80::1ff:fe23:4567:890a",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        ]
        for ip in ipv6_samples:
            is_valid, msg = validate_hostname_or_ip(ip)
            self.assertTrue(is_valid, f"Expected {ip} to be valid, got: {msg}")

    def test_03_valid_dns_hostnames_accepted(self):
        """Valid DNS hostnames must be accepted without requiring live DNS resolution."""
        valid_hosts = [
            "www.google.com",
            "google.com",
            "dns.quad9.net",
            "one.one.one.one",
            "router.internal",
            "host-123.subnet-a.example.org",
            "a.co",
            "my-server-01.local"
        ]
        for host in valid_hosts:
            is_valid, msg = validate_hostname_or_ip(host)
            self.assertTrue(is_valid, f"Expected {host} to be valid, got: {msg}")

    def test_04_numeric_only_rejected(self):
        """Numeric-only strings like '1234' must be strictly rejected."""
        numeric_samples = ["1234", "8080", "0", "99999", "123456789"]
        for num in numeric_samples:
            is_valid, msg = validate_hostname_or_ip(num)
            self.assertFalse(is_valid, f"Expected numeric string '{num}' to be rejected.")
            self.assertIn("numeric", msg.lower())

    def test_05_malformed_ipv4_rejected(self):
        """Malformed IPv4 addresses must be strictly rejected."""
        malformed_ips = [
            "999.999.999.999",
            "256.1.1.1",
            "1.2.3.4.5",
            "1.1.1",
            "1.1.1.01",  # leading zero octet rejected by strict ipaddress
            "300.0.0.1",
            "1.1.1.-1"
        ]
        for bad_ip in malformed_ips:
            is_valid, msg = validate_hostname_or_ip(bad_ip)
            self.assertFalse(is_valid, f"Expected malformed IP '{bad_ip}' to be rejected.")

    def test_06_empty_and_whitespace_rejected(self):
        """Empty, None, and whitespace strings must be rejected."""
        empty_samples = ["", "   ", "\t", "\n", None]
        for sample in empty_samples:
            is_valid, msg = validate_hostname_or_ip(sample)
            self.assertFalse(is_valid, f"Expected sample '{sample}' to be rejected.")

    def test_07_shell_metacharacters_and_malformed_hostnames_rejected(self):
        """Hostnames with shell characters, invalid punctuation, or malformed labels must be rejected."""
        invalid_hosts = [
            "google.com; rm -rf /",
            "1.1.1.1 && cat /etc/passwd",
            "`whoami`.com",
            "$(id).example.com",
            "-leading-hyphen.com",
            "trailing-hyphen-.com",
            "label..double-dot.com",
            ".leading-dot.com",
            "host with spaces.com",
            "host@domain.com",
            "http://google.com",
            "https://1.1.1.1"
        ]
        for bad in invalid_hosts:
            is_valid, msg = validate_hostname_or_ip(bad)
            self.assertFalse(is_valid, f"Expected invalid target '{bad}' to be rejected.")

    # ---------------------------------------------------------
    # Normalization & Duplicate Prevention
    # ---------------------------------------------------------
    def test_08_normalization(self):
        """Target host normalization trims whitespace and lowercases hostnames/IPs."""
        self.assertEqual(normalize_target_host("  8.8.8.8  "), "8.8.8.8")
        self.assertEqual(normalize_target_host("WWW.GOOGLE.COM."), "www.google.com")
        self.assertEqual(normalize_target_host("2001:0DB8::1"), "2001:db8::1")

    def test_09_duplicate_prevention(self):
        """Duplicate target registration must be prevented even with case/whitespace variations."""
        res1 = add_target_validated(name="Primary DNS", host="8.8.8.8", db_path=self.db_path)
        self.assertTrue(res1["success"])

        # Attempt to add exact same target
        res2 = add_target_validated(name="Duplicate DNS", host="8.8.8.8", db_path=self.db_path)
        self.assertFalse(res2["success"])
        self.assertEqual(res2["status"], "exists")

        # Attempt with whitespace
        res3 = add_target_validated(name="Spaced DNS", host="  8.8.8.8  ", db_path=self.db_path)
        self.assertFalse(res3["success"])
        self.assertEqual(res3["status"], "exists")

        # Domain duplicate check (case insensitive)
        add_d1 = add_target_validated(name="Google", host="Google.Com", db_path=self.db_path)
        self.assertTrue(add_d1["success"])
        add_d2 = add_target_validated(name="Google Lower", host="google.com", db_path=self.db_path)
        self.assertFalse(add_d2["success"])
        self.assertEqual(add_d2["status"], "exists")

    # ---------------------------------------------------------
    # Side Effects Prevention
    # ---------------------------------------------------------
    def test_10_invalid_input_not_inserted_into_db(self):
        """Invalid targets like '1234' must never be inserted into the database."""
        res = add_target_validated(name="Bogus Target", host="1234", db_path=self.db_path)
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "error")

        # Verify no target exists in database
        targets = get_all_targets(db_path=self.db_path)
        self.assertEqual(len(targets), 0)

    @patch("network.icmp_monitor.ping")
    @patch("network.icmp_monitor.ping_target")
    def test_11_invalid_input_does_not_trigger_probe(self, mock_ping_target, mock_ping):
        """Calling collect_icmp_target with '1234' must not probe the network or insert target."""
        res = collect_icmp_target("1234", db_path=self.db_path)
        self.assertFalse(res["success"])
        self.assertIn("error", res)
        self.assertIn("numeric", res["error"].lower())

        # Verify ping functions were never called
        mock_ping.assert_not_called()
        mock_ping_target.assert_not_called()

        # Verify database has zero targets and zero measurements
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS cnt FROM targets;")
            self.assertEqual(cursor.fetchone()["cnt"], 0)
            cursor.execute("SELECT COUNT(*) AS cnt FROM measurements;")
            self.assertEqual(cursor.fetchone()["cnt"], 0)

    def test_12_validate_target_config(self):
        """validate_target in target_manager must reject invalid targets."""
        valid_t = {"name": "Valid", "host": "1.1.1.1", "enabled": True, "interval": 5, "timeout": 2}
        self.assertTrue(validate_target(valid_t))

        invalid_t = {"name": "Invalid", "host": "1234", "enabled": True, "interval": 5, "timeout": 2}
        self.assertFalse(validate_target(invalid_t))

        malformed_t = {"name": "Bad IP", "host": "999.999.999.999", "enabled": True, "interval": 5, "timeout": 2}
        self.assertFalse(validate_target(malformed_t))

    # ---------------------------------------------------------
    # Handling Unreachable Targets vs Format Validation
    # ---------------------------------------------------------
    def test_13_valid_unreachable_target_handled_as_resolution_failure(self):
        """
        Valid hostname that cannot be resolved (unreachable) passes format validation,
        and is recorded as a DNS/probe resolution failure rather than format validation error.
        """
        unreachable_host = "nonexistent-telemetry-domain-xyz123.internal"
        is_valid, msg = validate_hostname_or_ip(unreachable_host)
        self.assertTrue(is_valid, f"Format validation should pass for syntactically valid host: {msg}")

        # Adding it via add_target_validated succeeds in format validation and inserts record
        add_res = add_target_validated(name="Unreachable Node", host=unreachable_host, db_path=self.db_path)
        self.assertTrue(add_res["success"])
        self.assertIsNone(add_res["target"]["resolved_ip"])

        # Probing via collect_icmp_target records resolution failure in measurements
        res = collect_icmp_target(unreachable_host, db_path=self.db_path)
        self.assertTrue(res["success"])
        meas = res["data"]
        self.assertEqual(meas["success"], 0)
        self.assertIn("Failed to resolve host", meas["error"])

    # ---------------------------------------------------------
    # Handling Existing Invalid Entries in DB (e.g. Target ID 168)
    # ---------------------------------------------------------
    @patch("network.icmp_monitor.ping_target")
    @patch("network.tcp_monitor.measure_tcp_connect")
    def test_14_existing_invalid_entry_blocked_from_new_probes(self, mock_tcp, mock_ping_target):
        """
        Simulate an existing invalid target in SQLite (such as '1234').
        Verify that probe_all_targets and runner skip it and never dispatch network packets.
        """
        # Directly insert invalid target into DB without validation (simulating pre-fix state)
        with get_connection(self.db_path) as conn:
            conn.execute("""
                INSERT INTO targets (target_id, name, host, resolved_ip, enabled, interval, timeout)
                VALUES (168, '1234', '1234', NULL, 1, 5, 2);
            """)
            conn.commit()

        # 1. Single probe check
        probe_res = _probe_single_target({"target_id": 168, "host": "1234", "timeout": 2})
        self.assertFalse(probe_res["probe"]["success"])
        self.assertIn("Invalid target address", probe_res["probe"]["error"])
        mock_ping_target.assert_not_called()
        mock_tcp.assert_not_called()

        # 2. probe_all_targets check: it should filter out the invalid target
        results = probe_all_targets(db_path=self.db_path)
        self.assertEqual(len(results), 0)
        mock_ping_target.assert_not_called()

        # 3. run_single_cycle check: it should skip invalid target
        all_targets = get_all_targets(db_path=self.db_path)
        cycle_res = run_single_cycle(all_targets, db_path=self.db_path)
        self.assertEqual(cycle_res["processed"], 0)
        self.assertEqual(cycle_res["skipped"], 1)
        mock_ping_target.assert_not_called()


if __name__ == "__main__":
    unittest.main()
