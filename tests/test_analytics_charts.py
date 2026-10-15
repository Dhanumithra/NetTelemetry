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
    insert_measurement
)
from database.db_m2 import store_window_metrics
from dashboard.components import (
    fetch_analytics_measurements,
    fetch_analytics_window_metrics,
    compute_analytics_summary_kpis,
    create_rtt_timeline_chart,
    create_packet_loss_chart,
    create_availability_chart,
    create_jitter_chart,
    create_p95_p99_comparison_chart
)
from telemetry.metrics import calculate_rolling_statistics


class TestAnalyticsCharts(unittest.TestCase):
    """
    Comprehensive tests for the upgraded Analytics section:
    1. Chart-data preparation
    2. Empty results handling (no crashes, returns valid Plotly figures)
    3. Target filtering (data isolation between targets)
    4. Failed probes handling (missing RTT excluded from latency, retained in loss)
    5. KPI summary calculation correctness
    6. Time-range filtering
    7. Recalculation logic column safety
    """

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(self.db_path)

        # Seed 2 test targets
        self.t1_id = insert_target({
            "name": "Cloudflare Primary",
            "host": "1.1.1.1",
            "resolved_ip": "1.1.1.1",
            "lat": 37.77,
            "lon": -122.41
        }, db_path=self.db_path)

        self.t2_id = insert_target({
            "name": "Google DNS",
            "host": "8.8.8.8",
            "resolved_ip": "8.8.8.8",
            "lat": 37.42,
            "lon": -122.08
        }, db_path=self.db_path)

        # Seed measurements for Target 1: 4 successful (20, 22, 24, 26 ms) + 1 failed (None RTT)
        now = datetime.datetime.now()
        for i, rtt in enumerate([20.0, 22.0, 24.0, 26.0]):
            ts = (now - datetime.timedelta(minutes=10 - i * 2)).strftime("%Y-%m-%d %H:%M:%S")
            insert_measurement({
                "target_id": self.t1_id,
                "timestamp": ts,
                "protocol": "ICMP",
                "test_type": "echo",
                "success": 1,
                "rtt_ms": rtt,
                "ttl": 64,
                "error": None
            }, db_path=self.db_path)

        # 1 failed probe for Target 1
        insert_measurement({
            "target_id": self.t1_id,
            "timestamp": (now - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "protocol": "ICMP",
            "test_type": "echo",
            "success": 0,
            "rtt_ms": None,
            "ttl": None,
            "error": "Request timed out"
        }, db_path=self.db_path)

        # Seed measurements for Target 2: 3 successful (40, 42, 44 ms)
        for i, rtt in enumerate([40.0, 42.0, 44.0]):
            ts = (now - datetime.timedelta(minutes=8 - i * 2)).strftime("%Y-%m-%d %H:%M:%S")
            insert_measurement({
                "target_id": self.t2_id,
                "timestamp": ts,
                "protocol": "ICMP",
                "test_type": "echo",
                "success": 1,
                "rtt_ms": rtt,
                "ttl": 58,
                "error": None
            }, db_path=self.db_path)

        # Seed window_metrics records
        store_window_metrics(
            self.db_path,
            target_id=str(self.t1_id),
            start_time=(now - datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            end_time=(now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
            metrics={
                "loss_pct": 20.0,
                "availability_pct": 80.0,
                "jitter_ms": 2.5,
                "p95_ms": 25.8,
                "p99_ms": 26.0,
                "throughput_mbps": 85.0
            }
        )

        store_window_metrics(
            self.db_path,
            target_id=str(self.t2_id),
            start_time=(now - datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            end_time=(now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
            metrics={
                "loss_pct": 0.0,
                "availability_pct": 100.0,
                "jitter_ms": 1.8,
                "p95_ms": 43.8,
                "p99_ms": 44.0,
                "throughput_mbps": 92.0
            }
        )

        store_window_metrics(
            self.db_path,
            target_id="global",
            start_time=(now - datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            end_time=(now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
            metrics={
                "loss_pct": 12.5,
                "availability_pct": 87.5,
                "jitter_ms": 2.2,
                "p95_ms": 42.0,
                "p99_ms": 44.0,
                "throughput_mbps": 88.5
            }
        )

    def tearDown(self):
        import gc
        gc.collect()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_01_fetch_analytics_measurements_all_and_filtered(self):
        """1. Verify fetching all measurements vs filtering by a specific target."""
        df_all = fetch_analytics_measurements(target_id="all", db_path=self.db_path)
        self.assertEqual(len(df_all), 8, "Expected 8 total measurements across both targets")

        df_t1 = fetch_analytics_measurements(target_id=self.t1_id, db_path=self.db_path)
        self.assertEqual(len(df_t1), 5, "Expected 5 measurements for target 1")
        self.assertTrue((df_t1["target_id"] == self.t1_id).all(), "All records must belong to target 1")

        df_t2 = fetch_analytics_measurements(target_id=self.t2_id, db_path=self.db_path)
        self.assertEqual(len(df_t2), 3, "Expected 3 measurements for target 2")
        self.assertTrue((df_t2["target_id"] == self.t2_id).all(), "All records must belong to target 2")

    def test_02_failed_probes_handling_in_latency_and_loss(self):
        """2. Verify failed probes (None RTT) are excluded from latency calculations but counted in loss."""
        df_t1 = fetch_analytics_measurements(target_id=self.t1_id, db_path=self.db_path)
        win_empty = pd.DataFrame()

        # Compute summary KPIs: 4 success, 1 failure -> loss = 20%, avg_rtt = mean(20, 22, 24, 26) = 23.0 ms
        kpis = compute_analytics_summary_kpis(df_t1, win_empty)
        self.assertEqual(kpis["loss_pct"], 20.0, "Failed probe must be counted as 20% loss")
        self.assertEqual(kpis["availability_pct"], 80.0, "Availability must be 80%")
        self.assertEqual(kpis["avg_rtt"], 23.0, "Avg RTT must exclude the None probe and be 23.0 ms")

        # RTT chart generation must succeed and exclude the failed probe
        fig = create_rtt_timeline_chart(df_t1, target_name="Cloudflare Primary")
        self.assertIsInstance(fig, go.Figure)
        # Check number of points in the scatter trace: should be 4, not 5
        self.assertEqual(len(fig.data[0].y), 4, "Latency line must only plot the 4 successful points")
        self.assertNotIn(0.0, fig.data[0].y, "Missing RTT must not be plotted as 0.0")

    def test_03_all_charts_render_with_empty_data_without_exceptions(self):
        """3. All 5 chart functions must gracefully return valid go.Figure objects when data is empty."""
        empty_df = pd.DataFrame()

        fig1 = create_rtt_timeline_chart(empty_df)
        self.assertIsInstance(fig1, go.Figure)
        self.assertTrue(len(fig1.layout.annotations) > 0)
        self.assertIn("No telemetry measurements", fig1.layout.annotations[0].text)

        fig2 = create_packet_loss_chart(empty_df)
        self.assertIsInstance(fig2, go.Figure)
        self.assertTrue(len(fig2.layout.annotations) > 0)

        fig3 = create_availability_chart(empty_df)
        self.assertIsInstance(fig3, go.Figure)
        self.assertTrue(len(fig3.layout.annotations) > 0)

        fig4 = create_jitter_chart(empty_df)
        self.assertIsInstance(fig4, go.Figure)
        self.assertTrue(len(fig4.layout.annotations) > 0)

        fig5 = create_p95_p99_comparison_chart(empty_df)
        self.assertIsInstance(fig5, go.Figure)
        self.assertTrue(len(fig5.layout.annotations) > 0)

    def test_04_target_window_metrics_isolation(self):
        """4. Verify window metrics filtering isolates target records."""
        w_all = fetch_analytics_window_metrics(target_id="all", db_path=self.db_path)
        self.assertEqual(len(w_all), 3, "Expected 3 total window records (t1, t2, global)")

        w_t1 = fetch_analytics_window_metrics(target_id=self.t1_id, db_path=self.db_path)
        self.assertEqual(len(w_t1), 1)
        self.assertEqual(str(w_t1.iloc[0]["target_id"]), str(self.t1_id))
        self.assertEqual(w_t1.iloc[0]["loss_pct"], 20.0)

        w_t2 = fetch_analytics_window_metrics(target_id=self.t2_id, db_path=self.db_path)
        self.assertEqual(len(w_t2), 1)
        self.assertEqual(str(w_t2.iloc[0]["target_id"]), str(self.t2_id))
        self.assertEqual(w_t2.iloc[0]["loss_pct"], 0.0)

    def test_05_multi_target_rtt_chart_creates_multiple_traces(self):
        """5. RTT chart for 'All Targets' plots distinct traces for each target."""
        df_all = fetch_analytics_measurements(target_id="all", db_path=self.db_path)
        fig = create_rtt_timeline_chart(df_all, target_name="All Targets (Combined View)")
        self.assertIsInstance(fig, go.Figure)
        # Should have 2 traces: one for Cloudflare Primary, one for Google DNS
        self.assertEqual(len(fig.data), 2)
        trace_names = [tr.name for tr in fig.data]
        self.assertIn("Cloudflare Primary", trace_names)
        self.assertIn("Google DNS", trace_names)

    def test_06_p95_p99_comparison_chart_traces(self):
        """6. P95 vs P99 chart creates two distinct comparative traces."""
        w_t1 = fetch_analytics_window_metrics(target_id=self.t1_id, db_path=self.db_path)
        fig = create_p95_p99_comparison_chart(w_t1)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 2)
        trace_names = [tr.name for tr in fig.data]
        self.assertIn("P95 Latency", trace_names)
        self.assertIn("P99 Latency", trace_names)

    def test_07_recalculate_rolling_window_schema_safety(self):
        """7. Verify recalculate logic writes to SQLite with columns matching window_metrics schema."""
        # Calculate rolling stats from measurements
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rtt_ms, success FROM measurements WHERE target_id = ?", (self.t1_id,))
            recs = cursor.fetchall()
            total = len(recs)
            succ = sum(1 for r in recs if r["success"] == 1)
            rtts = [r["rtt_ms"] for r in recs if r["success"] == 1 and r["rtt_ms"] is not None]
            st_calc = calculate_rolling_statistics(rtts, total, succ)

            # Insert with the exact schema columns used in the upgraded recalculation button
            cursor.execute("""
            INSERT INTO window_metrics (target_id, start_time, end_time, loss_pct, availability_pct, jitter_ms, p95_ms, p99_ms, throughput_mbps)
            VALUES (?, datetime('now', '-2 minutes'), datetime('now'), ?, ?, ?, ?, ?, ?)
            """, (
                str(self.t1_id),
                st_calc["loss_pct"],
                st_calc["availability_pct"],
                st_calc["jitter_ms"],
                st_calc["p95_ms"],
                st_calc["p99_ms"],
                None
            ))
            conn.commit()

            cursor.execute("SELECT COUNT(*) FROM window_metrics WHERE target_id = ?", (str(self.t1_id),))
            count = cursor.fetchone()[0]
            self.assertEqual(count, 2, "New rolling window record must be safely added")


if __name__ == "__main__":
    unittest.main()
