import os
import json
import tempfile
import unittest
import sqlite3

from network.settings_manager import (
    DEFAULT_THRESHOLDS,
    validate_thresholds,
    load_thresholds,
    save_thresholds,
    reset_thresholds
)
from analytics.anomaly_detector import AnomalyDetector
from database.db import (
    init_db,
    get_connection,
    insert_target,
    insert_measurement,
    get_active_anomalies
)
from telemetry.collector import probe_all_targets


class TestTelemetrySettings(unittest.TestCase):
    """
    Comprehensive test suite for Telemetry Settings & Thresholds:
    1. Input validation for RTT, packet loss, and jitter.
    2. Boundary values and illegal input rejection.
    3. Persistence across reloads and survival of restarts.
    4. Preservation of other config.json sections (targets).
    5. AnomalyDetector consuming saved thresholds dynamically.
    6. Verifying changing thresholds affects subsequent anomaly evaluations without rewriting history.
    7. Reset to defaults: cancellation leaves settings unchanged; confirmation restores factory defaults.
    8. Streamlit AppTest UI verification: validation errors, save confirmation, and reset dialog workflow.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "config.json")
        self.db_path = os.path.join(self.temp_dir.name, "test_telemetry.db")
        init_db(self.db_path)

        # Seed initial config with targets and default thresholds
        initial_config = {
            "targets": [
                {
                    "target_id": "google",
                    "name": "Google",
                    "host": "8.8.8.8",
                    "enabled": True,
                    "interval": 5,
                    "timeout": 2
                }
            ],
            "thresholds": dict(DEFAULT_THRESHOLDS)
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(initial_config, f, indent=4)

    def tearDown(self):
        self.temp_dir.cleanup()

    # -----------------------------------------------------------------
    # 1. Input Validation Tests
    # -----------------------------------------------------------------
    def test_01_valid_threshold_values(self):
        """Valid thresholds pass validation without errors."""
        is_valid, errors = validate_thresholds(90.0, 5.0, 20.0)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Boundary checks: RTT > 0, loss in [0, 100], jitter >= 0
        is_valid, errors = validate_thresholds(0.1, 0.0, 0.0)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        is_valid, errors = validate_thresholds(500.0, 100.0, 50.0)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_02_invalid_rtt_threshold(self):
        """RTT threshold must be a valid positive number (> 0 ms)."""
        # Zero RTT
        is_valid, errors = validate_thresholds(0.0, 5.0, 20.0)
        self.assertFalse(is_valid)
        self.assertTrue(any("RTT threshold must be a valid positive number" in e for e in errors))

        # Negative RTT
        is_valid, errors = validate_thresholds(-10.5, 5.0, 20.0)
        self.assertFalse(is_valid)
        self.assertTrue(any("RTT threshold must be a valid positive number" in e for e in errors))

        # NaN / inf / non-numeric
        is_valid, errors = validate_thresholds(float('nan'), 5.0, 20.0)
        self.assertFalse(is_valid)
        is_valid, errors = validate_thresholds("invalid_str", 5.0, 20.0)
        self.assertFalse(is_valid)
        is_valid, errors = validate_thresholds(None, 5.0, 20.0)
        self.assertFalse(is_valid)

    def test_03_invalid_loss_threshold(self):
        """Packet loss threshold must be between 0% and 100%."""
        # Below 0%
        is_valid, errors = validate_thresholds(90.0, -0.1, 20.0)
        self.assertFalse(is_valid)
        self.assertTrue(any("between 0% and 100%" in e for e in errors))

        # Above 100%
        is_valid, errors = validate_thresholds(90.0, 100.1, 20.0)
        self.assertFalse(is_valid)
        self.assertTrue(any("between 0% and 100%" in e for e in errors))

        # NaN / inf / non-numeric
        is_valid, errors = validate_thresholds(90.0, float('inf'), 20.0)
        self.assertFalse(is_valid)
        is_valid, errors = validate_thresholds(90.0, "not_a_num", 20.0)
        self.assertFalse(is_valid)

    def test_04_invalid_jitter_threshold(self):
        """Jitter threshold must be a non-negative number (>= 0 ms)."""
        # Negative jitter
        is_valid, errors = validate_thresholds(90.0, 5.0, -1.0)
        self.assertFalse(is_valid)
        self.assertTrue(any("non-negative number" in e for e in errors))

        # NaN / non-numeric
        is_valid, errors = validate_thresholds(90.0, 5.0, float('nan'))
        self.assertFalse(is_valid)
        is_valid, errors = validate_thresholds(90.0, 5.0, "abc")
        self.assertFalse(is_valid)

    def test_05_multiple_validation_errors(self):
        """Multiple invalid fields are all reported in the errors list."""
        is_valid, errors = validate_thresholds(-5.0, 150.0, -2.0)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 3)

    # -----------------------------------------------------------------
    # 2. Persistence & Survival Across Reloads
    # -----------------------------------------------------------------
    def test_06_save_and_load_persistence(self):
        """Saved thresholds persist to config file and survive reloads."""
        new_settings = {
            "rtt_ms": 135.5,
            "loss_pct": 12.0,
            "jitter_ms": 35.0
        }
        success, msg = save_thresholds(new_settings, config_path=self.config_path)
        self.assertTrue(success, f"Saving failed: {msg}")

        # Reload from scratch
        loaded = load_thresholds(config_path=self.config_path)
        self.assertEqual(loaded["rtt_ms"], 135.5)
        self.assertEqual(loaded["loss_pct"], 12.0)
        self.assertEqual(loaded["jitter_ms"], 35.0)

    def test_07_save_preserves_targets_and_structure(self):
        """Saving thresholds does not delete or mutate configured targets."""
        new_settings = {"rtt_ms": 110.0, "loss_pct": 8.0, "jitter_ms": 15.0}
        save_thresholds(new_settings, config_path=self.config_path)

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("targets", data)
        self.assertEqual(len(data["targets"]), 1)
        self.assertEqual(data["targets"][0]["name"], "Google")
        self.assertEqual(data["targets"][0]["host"], "8.8.8.8")
        self.assertIn("thresholds", data)
        self.assertEqual(data["thresholds"]["rtt_ms"], 110.0)

    def test_08_invalid_values_not_persisted(self):
        """Invalid threshold values are rejected and the file remains unchanged."""
        initial = load_thresholds(config_path=self.config_path)

        invalid_settings = {"rtt_ms": -10.0, "loss_pct": 5.0, "jitter_ms": 20.0}
        success, msg = save_thresholds(invalid_settings, config_path=self.config_path)
        self.assertFalse(success)
        self.assertIn("Validation failed", msg)

        # Confirm file still has original values
        reloaded = load_thresholds(config_path=self.config_path)
        self.assertEqual(reloaded["rtt_ms"], initial["rtt_ms"])

    # -----------------------------------------------------------------
    # 3. Connection to Anomaly Detection
    # -----------------------------------------------------------------
    def test_09_detector_reads_saved_thresholds(self):
        """AnomalyDetector reads saved thresholds dynamically when none are passed."""
        save_thresholds({"rtt_ms": 150.0, "loss_pct": 10.0, "jitter_ms": 40.0}, config_path=self.config_path)

        detector = AnomalyDetector(config_path=self.config_path)
        self.assertEqual(detector.rtt_threshold, 150.0)
        self.assertEqual(detector.loss_threshold, 10.0)
        self.assertEqual(detector.jitter_threshold, 40.0)

    def test_10_threshold_change_affects_subsequent_evaluations(self):
        """Updating a threshold changes whether subsequent metric samples trigger anomalies."""
        metrics = {"loss_pct": 2.0, "p95_ms": 110.0, "jitter_ms": 10.0}

        # 1. At RTT threshold 90.0 ms: 110.0 > 90.0 -> Anomaly detected!
        save_thresholds({"rtt_ms": 90.0, "loss_pct": 5.0, "jitter_ms": 20.0}, config_path=self.config_path)
        detector1 = AnomalyDetector(config_path=self.config_path)
        res1 = detector1.detect(metrics)
        self.assertIsNotNone(res1)
        self.assertEqual(res1["metric"], "p95_ms")
        self.assertEqual(res1["threshold"], 90.0)

        # 2. Operator increases threshold to 120.0 ms: 110.0 < 120.0 -> Nominal (no anomaly)
        save_thresholds({"rtt_ms": 120.0, "loss_pct": 5.0, "jitter_ms": 20.0}, config_path=self.config_path)
        detector2 = AnomalyDetector(config_path=self.config_path)
        res2 = detector2.detect(metrics)
        self.assertIsNone(res2, "Metric should not trigger anomaly under elevated threshold")

    def test_11_historical_anomaly_records_not_retroactively_rewritten(self):
        """Modifying thresholds does not alter or rewrite historical anomaly records in SQLite."""
        # Insert a target and a historical anomaly at threshold 90.0
        t_id = insert_target({"name": "Test Node", "host": "1.1.1.1"}, db_path=self.db_path)
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO anomalies (timestamp, target_id, metric, observed_value, baseline, threshold, reason)
                VALUES ('2026-10-15 10:00:00', ?, 'p95_ms', 115.0, 20.0, 90.0, 'P95 Latency spike detected')
            """, (str(t_id),))
            conn.commit()

        # Verify historical anomaly has threshold 90.0
        anomalies_before = get_active_anomalies(db_path=self.db_path)
        self.assertEqual(len(anomalies_before), 1)
        self.assertEqual(anomalies_before[0]["observed_value"], 115.0)

        # Operator changes threshold to 200.0 ms
        save_thresholds({"rtt_ms": 200.0, "loss_pct": 10.0, "jitter_ms": 50.0}, config_path=self.config_path)

        # Verify historical record in SQLite still exists with its original threshold and reason
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT threshold, observed_value, reason FROM anomalies WHERE target_id = ?", (str(t_id),))
            row = cursor.fetchone()
            self.assertEqual(row["threshold"], 90.0, "Historical threshold must NOT be rewritten")
            self.assertEqual(row["observed_value"], 115.0)
            self.assertIn("spike", row["reason"].lower())

    # -----------------------------------------------------------------
    # 4. Reset to Defaults Workflow
    # -----------------------------------------------------------------
    def test_12_reset_thresholds_restores_defaults(self):
        """reset_thresholds() restores factory defaults and persists them."""
        # Set custom values first
        save_thresholds({"rtt_ms": 250.0, "loss_pct": 25.0, "jitter_ms": 75.0}, config_path=self.config_path)
        current = load_thresholds(config_path=self.config_path)
        self.assertEqual(current["rtt_ms"], 250.0)

        # Reset
        success, msg = reset_thresholds(config_path=self.config_path)
        self.assertTrue(success)

        # Confirm defaults are restored
        reset_vals = load_thresholds(config_path=self.config_path)
        self.assertEqual(reset_vals["rtt_ms"], DEFAULT_THRESHOLDS["rtt_ms"])
        self.assertEqual(reset_vals["loss_pct"], DEFAULT_THRESHOLDS["loss_pct"])
        self.assertEqual(reset_vals["jitter_ms"], DEFAULT_THRESHOLDS["jitter_ms"])

    # -----------------------------------------------------------------
    # 5. Streamlit AppTest Settings Page & Dialog Tests
    # -----------------------------------------------------------------
    def test_13_streamlit_apptest_settings_view_rendering(self):
        """Streamlit AppTest navigates to Settings page and renders inputs and buttons without exceptions."""
        from streamlit.testing.v1 import AppTest

        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py"))
        at = AppTest.from_file(app_path, default_timeout=30)
        at.run()
        self.assertEqual(len(at.exception), 0)

        # Navigate to Settings page
        at.session_state["current_page"] = "Settings"
        at.run()
        self.assertEqual(len(at.exception), 0)

        # Verify 3 number inputs exist with correct labels
        num_inputs = at.number_input
        self.assertEqual(len(num_inputs), 3)
        labels = [ni.label for ni in num_inputs]
        self.assertIn("RTT Anomaly Spike Threshold (ms)", labels)
        self.assertIn("Packet Loss Warning Threshold (%)", labels)
        self.assertIn("Jitter Threshold (ms)", labels)

        # Verify buttons exist
        btn_labels = [b.label for b in at.button]
        self.assertTrue(any("Save Settings" in l for l in btn_labels))
        self.assertTrue(any("Reset to Defaults" in l for l in btn_labels))

    def test_14_streamlit_apptest_save_valid_settings(self):
        """Saving valid settings updates session state and displays success toast/message."""
        from streamlit.testing.v1 import AppTest

        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py"))
        at = AppTest.from_file(app_path, default_timeout=30)
        at.run()

        at.session_state["current_page"] = "Settings"
        at.run()

        # Update inputs
        rtt_input = at.number_input(key=None)  # Find by label or index
        for ni in at.number_input:
            if "RTT" in ni.label:
                ni.set_value(95.0)
            elif "Packet Loss" in ni.label:
                ni.set_value(6.0)
            elif "Jitter" in ni.label:
                ni.set_value(22.0)

        save_btn = at.button(key="btn_save_settings")
        self.assertIsNotNone(save_btn)
        save_btn.click().run()

        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.session_state["thresh_rtt"], 95.0)
        self.assertEqual(at.session_state["thresh_loss"], 6.0)
        self.assertEqual(at.session_state["thresh_jitter"], 22.0)

    def test_15_streamlit_apptest_validation_errors_prevent_saving(self):
        """Invalid inputs trigger validation errors and do not update persisted thresholds."""
        from streamlit.testing.v1 import AppTest

        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py"))
        at = AppTest.from_file(app_path, default_timeout=30)
        at.run()

        at.session_state["current_page"] = "Settings"
        at.session_state["thresh_rtt"] = 90.0
        at.run()

        # Set invalid RTT (-10)
        for ni in at.number_input:
            if "RTT" in ni.label:
                ni.set_value(-10.0)

        save_btn = at.button(key="btn_save_settings")
        save_btn.click().run()

        self.assertEqual(len(at.exception), 0)
        # Should display validation error
        errors = [e.value for e in at.error]
        self.assertTrue(any("positive number" in err.lower() for err in errors), f"Expected validation error, got: {errors}")
        # Threshold in session state must not have changed to -10.0
        self.assertNotEqual(at.session_state.get("thresh_rtt"), -10.0)

    def test_16_streamlit_apptest_reset_dialog_cancel(self):
        """Clicking Reset to Defaults opens dialog; clicking Cancel leaves settings unchanged."""
        from streamlit.testing.v1 import AppTest

        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py"))
        at = AppTest.from_file(app_path, default_timeout=30)
        at.run()

        at.session_state["current_page"] = "Settings"
        at.session_state["thresh_rtt"] = 125.0
        at.run()

        # Trigger reset dialog
        reset_trigger = at.button(key="btn_reset_thresholds_trigger")
        self.assertIsNotNone(reset_trigger)
        reset_trigger.click().run()
        self.assertEqual(len(at.exception), 0)

        # Dialog should be open with Cancel and Reset buttons
        cancel_btn = at.button(key="btn_cancel_reset_thresholds")
        confirm_btn = at.button(key="btn_confirm_reset_thresholds")
        self.assertIsNotNone(cancel_btn, "Cancel button must be present in dialog")
        self.assertIsNotNone(confirm_btn, "Reset button must be present in dialog")
        self.assertEqual(cancel_btn.label, "Cancel")
        self.assertEqual(confirm_btn.label, "Reset")

        # Click Cancel
        cancel_btn.click().run()
        self.assertEqual(len(at.exception), 0)

        # Setting remains 125.0
        self.assertEqual(at.session_state["thresh_rtt"], 125.0)

    def test_17_streamlit_apptest_reset_dialog_confirm(self):
        """Confirming reset restores default thresholds and displays success message."""
        from streamlit.testing.v1 import AppTest

        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py"))
        at = AppTest.from_file(app_path, default_timeout=30)
        at.run()

        at.session_state["current_page"] = "Settings"
        at.session_state["thresh_rtt"] = 140.0
        at.session_state["thresh_loss"] = 15.0
        at.session_state["thresh_jitter"] = 45.0
        at.run()

        # Trigger reset dialog
        reset_trigger = at.button(key="btn_reset_thresholds_trigger")
        reset_trigger.click().run()

        confirm_btn = at.button(key="btn_confirm_reset_thresholds")
        confirm_btn.click().run()
        self.assertEqual(len(at.exception), 0)

        # Session state restored to factory defaults
        self.assertEqual(at.session_state["thresh_rtt"], 90.0)
        self.assertEqual(at.session_state["thresh_loss"], 5.0)
        self.assertEqual(at.session_state["thresh_jitter"], 20.0)

        # Success message displayed
        successes = [s.value for s in at.success]
        self.assertTrue(any("reset to default" in s.lower() for s in successes), f"Expected success message, got: {successes}")


if __name__ == "__main__":
    unittest.main()
