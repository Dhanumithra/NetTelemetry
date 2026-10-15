import os
import tempfile
import unittest
import sqlite3
import pandas as pd
import datetime
import plotly.graph_objects as go

from database.db import (
    init_db,
    get_connection,
    insert_target,
    clear_anomalies,
    get_anomalies_count
)
from dashboard.components import (
    fetch_anomaly_records,
    create_anomaly_timeline_chart
)


class TestAnomalyTimeline(unittest.TestCase):
    """
    Comprehensive tests for the Anomaly Timeline Visualization:
    1. Empty anomaly history handling (chart returns friendly message without exception).
    2. Multiple metrics grouping (loss_pct, p95_ms, jitter_ms, timeout).
    3. Multiple targets with accurate target name/IP mapping (no guessing).
    4. Target and metric filtering data consistency.
    5. Invalid or missing optional fields (None threshold, None baseline, invalid timestamp strings).
    6. Both 'magnitude' and 'swimlane' views generate valid figures.
    7. Integration with Streamlit AppTest: confirms chart renders, filters work, and clearing history still requires confirmation.
    """

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(self.db_path)

        # Seed 2 targets
        self.t1_id = insert_target({
            "name": "Cloudflare Edge",
            "host": "1.1.1.1",
            "resolved_ip": "1.1.1.1",
            "enabled": True,
            "interval": 5,
            "timeout": 2
        }, db_path=self.db_path)

        self.t2_id = insert_target({
            "name": "Google DNS",
            "host": "8.8.8.8",
            "resolved_ip": "8.8.8.8",
            "enabled": True,
            "interval": 5,
            "timeout": 2
        }, db_path=self.db_path)

        # Seed multiple anomalies across targets and metrics
        now = datetime.datetime.now()
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            # Anomaly 1: Target 1, loss_pct
            cursor.execute("""
                INSERT INTO anomalies (timestamp, target_id, metric, observed_value, baseline, threshold, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ((now - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
                  str(self.t1_id), "loss_pct", 25.0, 0.0, 5.0, "High packet loss detected"))

            # Anomaly 2: Target 1, p95_ms
            cursor.execute("""
                INSERT INTO anomalies (timestamp, target_id, metric, observed_value, baseline, threshold, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ((now - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                  str(self.t1_id), "p95_ms", 185.5, 20.0, 90.0, "P95 Latency spike detected"))

            # Anomaly 3: Target 2, jitter_ms
            cursor.execute("""
                INSERT INTO anomalies (timestamp, target_id, metric, observed_value, baseline, threshold, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ((now - datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
                  str(self.t2_id), "jitter_ms", 35.2, 5.0, 20.0, "High jitter/unstable delay detected"))

            # Anomaly 4: Unmapped target ID 999 (target does not exist in targets table)
            cursor.execute("""
                INSERT INTO anomalies (timestamp, target_id, metric, observed_value, baseline, threshold, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ((now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
                  "999", "timeout", 1.0, 0.0, 0.0, "No response (timeout)"))

            conn.commit()

    def tearDown(self):
        import gc
        gc.collect()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_01_empty_anomaly_history(self):
        """1. Empty database yields empty dataframe and valid friendly chart figure without exception."""
        clear_anomalies(self.db_path)
        self.assertEqual(get_anomalies_count(self.db_path), 0)

        df = fetch_anomaly_records(db_path=self.db_path)
        self.assertTrue(df.empty)

        # Generating chart on empty dataframe must return a valid Plotly Figure without crashing
        fig = create_anomaly_timeline_chart(df)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 0, "Empty chart must have 0 scatter traces")
        self.assertTrue(len(fig.layout.annotations) > 0, "Empty chart must have friendly annotation text")
        self.assertIn("No anomaly records", fig.layout.annotations[0].text)

    def test_02_fetch_records_target_mapping(self):
        """2. Records are correctly joined with targets, using real names/IPs without guessing."""
        df = fetch_anomaly_records(db_path=self.db_path)
        self.assertEqual(len(df), 4)

        # Check Target 1 mapping
        t1_rows = df[df["target_id"] == str(self.t1_id)]
        self.assertEqual(len(t1_rows), 2)
        for _, r in t1_rows.iterrows():
            self.assertEqual(r["target_name"], "Cloudflare Edge")
            self.assertEqual(r["target_host"], "1.1.1.1")

        # Check Target 2 mapping
        t2_rows = df[df["target_id"] == str(self.t2_id)]
        self.assertEqual(len(t2_rows), 1)
        self.assertEqual(t2_rows.iloc[0]["target_name"], "Google DNS")
        self.assertEqual(t2_rows.iloc[0]["target_host"], "8.8.8.8")

        # Check unmapped target ID 999
        unmapped_rows = df[df["target_id"] == "999"]
        self.assertEqual(len(unmapped_rows), 1)
        self.assertEqual(unmapped_rows.iloc[0]["target_name"], "Target #999")

    def test_03_multiple_metrics_grouping_in_chart(self):
        """3. Chart creates distinct traces for each metric with appropriate colors and labels."""
        df = fetch_anomaly_records(db_path=self.db_path)
        fig = create_anomaly_timeline_chart(df, view_mode="magnitude")

        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 4, "Must have 4 traces for 4 distinct metrics")

        trace_names = [trace.name for trace in fig.data]
        self.assertTrue(any("loss_pct" in name for name in trace_names))
        self.assertTrue(any("p95_ms" in name for name in trace_names))
        self.assertTrue(any("jitter_ms" in name for name in trace_names))
        self.assertTrue(any("timeout" in name for name in trace_names))

        # Check that hovertemplate includes rich information
        for trace in fig.data:
            self.assertIn("Observed Value", trace.hovertemplate)
            self.assertIn("Threshold", trace.hovertemplate)
            self.assertIn("Reason", trace.hovertemplate)

    def test_04_target_and_metric_filtering(self):
        """4. Filtering by target and metric returns properly isolated records."""
        # Filter by Target 1
        df_t1 = fetch_anomaly_records(target_id=self.t1_id, db_path=self.db_path)
        self.assertEqual(len(df_t1), 2)
        self.assertTrue(all(r == "Cloudflare Edge" for r in df_t1["target_name"]))

        # Filter by metric 'loss_pct'
        df_loss = fetch_anomaly_records(metric="loss_pct", db_path=self.db_path)
        self.assertEqual(len(df_loss), 1)
        self.assertEqual(df_loss.iloc[0]["metric"], "loss_pct")
        self.assertEqual(df_loss.iloc[0]["observed_value"], 25.0)

        # Combined filter: Target 1 + p95_ms
        df_combined = fetch_anomaly_records(target_id=self.t1_id, metric="p95_ms", db_path=self.db_path)
        self.assertEqual(len(df_combined), 1)
        self.assertEqual(df_combined.iloc[0]["observed_value"], 185.5)

    def test_05_invalid_and_missing_optional_fields_safety(self):
        """5. Safely handles missing/NaN observed values, thresholds, reasons, and invalid timestamp strings."""
        dirty_records = pd.DataFrame([
            {
                "id": 101,
                "timestamp": "invalid-timestamp-string",
                "target_id": None,
                "target_name": None,
                "target_host": None,
                "resolved_ip": None,
                "metric": "loss_pct",
                "observed_value": None,
                "baseline": None,
                "threshold": None,
                "reason": None
            },
            {
                "id": 102,
                "timestamp": "2026-10-15 12:00:00",
                "target_id": "42",
                "target_name": "Test Host",
                "target_host": "",
                "resolved_ip": None,
                "metric": "p95_ms",
                "observed_value": 150.0,
                "baseline": None,
                "threshold": 90.0,
                "reason": None
            }
        ])

        # Chart generation must not raise exception
        fig = create_anomaly_timeline_chart(dirty_records, view_mode="magnitude")
        self.assertIsInstance(fig, go.Figure)
        # Only the valid row (id: 102) should be plotted
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(len(fig.data[0].x), 1)

    def test_06_swimlane_view_mode(self):
        """6. View mode 'swimlane' uses target_name on Y-axis and sets appropriate axis title."""
        df = fetch_anomaly_records(db_path=self.db_path)
        fig_swim = create_anomaly_timeline_chart(df, view_mode="swimlane")

        self.assertIsInstance(fig_swim, go.Figure)
        self.assertEqual(fig_swim.layout.yaxis.title.text, "Monitored Network Targets")
        for trace in fig_swim.data:
            # Y values in swimlane must be target names
            for y_val in trace.y:
                self.assertIn(y_val, ["Cloudflare Edge", "Google DNS", "Target #999"])

    def test_07_streamlit_dashboard_integration(self):
        """7. Streamlit AppTest verifies timeline renders on Alerts page and clearing history retains confirmation dialog."""
        from streamlit.testing.v1 import AppTest

        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py"))
        at = AppTest.from_file(app_path, default_timeout=30)
        at.run()
        self.assertEqual(len(at.exception), 0)

        # Navigate to Alerts page
        at.session_state["current_page"] = "Alerts"
        at.run()
        self.assertEqual(len(at.exception), 0)

        # Verify filters and chart elements
        self.assertTrue(any(s.key == "alert_target_filter" for s in at.selectbox))
        self.assertTrue(any(s.key == "alert_metric_filter" for s in at.selectbox))
        self.assertTrue(any(r.key == "alert_view_mode" for r in at.radio))

        # Verify Clear Anomalies button triggers confirmation dialog
        trigger_btn = at.button(key="btn_clear_anomalies_trigger")
        self.assertIsNotNone(trigger_btn)
        trigger_btn.click().run()
        self.assertEqual(len(at.exception), 0)

        # Verify confirmation dialog buttons are present and require explicit confirmation
        cancel_btn = at.button(key="btn_cancel_clear_anomalies")
        confirm_btn = at.button(key="btn_confirm_clear_anomalies")
        self.assertIsNotNone(cancel_btn)
        self.assertIsNotNone(confirm_btn)
        self.assertEqual(confirm_btn.label, "Clear History")

        # Click Cancel and confirm dialog closes without error
        cancel_btn.click().run()
        self.assertEqual(len(at.exception), 0)


if __name__ == "__main__":
    unittest.main()
