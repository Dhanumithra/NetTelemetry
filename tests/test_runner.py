import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock
from database.db import init_db, get_measurements
from telemetry.runner import run_single_cycle, run_telemetry_loop

class TestRunner(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "config.json")
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        init_db(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_disabled_target(self):
        """TEST 1 — Disabled target is skipped and no measurement is attempted."""
        targets = [
            {"name": "Disabled Target", "host": "10.0.0.1", "enabled": False, "interval": 5, "timeout": 2}
        ]
        mock_collector = MagicMock()

        summary = run_single_cycle(targets, db_path=self.db_path, collector_func=mock_collector)

        self.assertEqual(summary["processed"], 0)
        self.assertEqual(summary["skipped"], 1)
        mock_collector.assert_not_called()

    def test_02_single_enabled_target(self):
        """TEST 2 — Single enabled target is measured and passed to collector."""
        targets = [
            {"name": "Enabled Target", "host": "127.0.0.1", "enabled": True, "interval": 5, "timeout": 2}
        ]
        mock_collector = MagicMock(return_value={"success": True, "measurement_id": 1})

        summary = run_single_cycle(targets, db_path=self.db_path, collector_func=mock_collector)

        self.assertEqual(summary["processed"], 1)
        self.assertEqual(summary["skipped"], 0)
        mock_collector.assert_called_once_with(targets[0], db_path=self.db_path)

    def test_03_multiple_targets(self):
        """TEST 3 — Enabled targets are processed, disabled targets are ignored."""
        targets = [
            {"name": "Enabled 1", "host": "127.0.0.1", "enabled": True, "interval": 5, "timeout": 2},
            {"name": "Disabled 1", "host": "10.0.0.1", "enabled": False, "interval": 5, "timeout": 2},
            {"name": "Enabled 2", "host": "8.8.8.8", "enabled": True, "interval": 5, "timeout": 2}
        ]
        mock_collector = MagicMock(return_value={"success": True})

        summary = run_single_cycle(targets, db_path=self.db_path, collector_func=mock_collector)

        self.assertEqual(summary["processed"], 2)
        self.assertEqual(summary["skipped"], 1)
        self.assertEqual(mock_collector.call_count, 2)

    def test_04_collector_failure_resilience(self):
        """TEST 4 — Collector/database failure does not crash the runner."""
        targets = [
            {"name": "Failing Target", "host": "127.0.0.1", "enabled": True, "interval": 5, "timeout": 2}
        ]
        mock_collector = MagicMock(side_effect=Exception("Database connection error"))

        summary = run_single_cycle(targets, db_path=self.db_path, collector_func=mock_collector)

        self.assertEqual(summary["processed"], 0)
        self.assertIn("error", summary["results"][0])

    def test_05_stop_behavior_and_keyboard_interrupt(self):
        """TEST 5 — Runner stops cleanly and handles Ctrl+C without raising traceback."""
        config_data = {
            "targets": [
                {"name": "Localhost", "host": "127.0.0.1", "enabled": True, "interval": 1, "timeout": 1}
            ]
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        mock_collector = MagicMock(return_value={"success": True})
        mock_sleep = MagicMock()

        # Test count-limited run
        cycles = run_telemetry_loop(
            config_path=self.config_path,
            db_path=self.db_path,
            count=2,
            interval_override=0,
            sleep_func=mock_sleep,
            collector_func=mock_collector
        )
        self.assertEqual(cycles, 2)
        self.assertEqual(mock_collector.call_count, 2)

        # Test KeyboardInterrupt clean exit (does not raise unhandled exception)
        interrupt_collector = MagicMock(side_effect=KeyboardInterrupt)
        cycles_ki = run_telemetry_loop(
            config_path=self.config_path,
            db_path=self.db_path,
            count=None,
            interval_override=0,
            sleep_func=mock_sleep,
            collector_func=interrupt_collector
        )
        self.assertEqual(cycles_ki, 0)

if __name__ == "__main__":
    unittest.main()
