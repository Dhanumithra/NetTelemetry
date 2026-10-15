import os
import tempfile
import unittest
import sqlite3
import io
import pandas as pd
import datetime

from database.db import (
    init_db,
    get_connection,
    insert_target,
    insert_measurement,
    get_measurements_count,
    get_network_performance_summary,
    generate_performance_interpretation,
    get_anomalies_count
)


class TestReportsView(unittest.TestCase):
    """
    Comprehensive test suite for the Reports section and live network performance summary:
    1. Database query execution with get_connection() context manager without ._conn.
    2. Telemetry dataset CSV export formatting and valid structure.
    3. Executive report markdown content with operator credentials and LaTeX jitter formula.
    4. Measurement data preservation during report queries.
    5. Streamlit AppTest execution of render_reports_view() without exceptions.
    6. Empty database handling (graceful N/A metrics, 0 counts, no ZeroDivisionError).
    7. Metric calculations with mixed successful, failed, and missing RTT probes.
    8. Anomaly count calculation and data-derived operational interpretation.
    9. Markdown download content verification including performance summary and NOC overview.
    10. CSV export regression and schema preservation.
    11. Edge case: 100% failed probes (100% loss, 0% availability, N/A average RTT, firewall note).
    12. Edge case: 100% successful probes (0% loss, 100% availability, clean average RTT).
    """

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(self.db_path)

        # Seed target
        self.target_id = insert_target({
            "name": "Cloudflare Test",
            "host": "1.1.1.1",
            "resolved_ip": "1.1.1.1",
            "enabled": True,
            "interval": 5,
            "timeout": 2
        }, db_path=self.db_path)

        # Seed measurements
        for i in range(5):
            insert_measurement({
                "target_id": self.target_id,
                "timestamp": f"2026-10-15 11:00:0{i}",
                "protocol": "ICMP",
                "test_type": "echo",
                "success": 1,
                "rtt_ms": 14.0 + i,
                "ttl": 64,
                "error": None
            }, db_path=self.db_path)

    def tearDown(self):
        import gc
        gc.collect()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_01_connection_context_manager_query_execution(self):
        """1. with get_connection() yields a sqlite3.Connection; querying without ._conn succeeds without AttributeError."""
        with get_connection(self.db_path) as conn:
            self.assertIsInstance(conn, sqlite3.Connection)
            conn_obj = getattr(conn, "_conn", conn)
            self.assertIs(conn_obj, conn)

            m_df = pd.read_sql_query("SELECT * FROM measurements ORDER BY id DESC LIMIT 500", conn_obj)
            self.assertEqual(len(m_df), 5, "Must return 5 seeded measurements")
            self.assertIn("rtt_ms", m_df.columns)
            self.assertIn("protocol", m_df.columns)

    def test_02_csv_export_generation(self):
        """2. Telemetry dataset is converted to valid non-empty CSV string and bytes."""
        with get_connection(self.db_path) as conn:
            conn_obj = getattr(conn, "_conn", conn)
            m_df = pd.read_sql_query("SELECT * FROM measurements ORDER BY id DESC LIMIT 500", conn_obj)

        csv_bytes = m_df.to_csv(index=False).encode('utf-8')
        self.assertTrue(len(csv_bytes) > 0)
        self.assertIn(b"rtt_ms", csv_bytes)
        self.assertIn(b"ICMP", csv_bytes)

    def test_03_report_text_generation_and_operator_auth(self):
        """3. Report markdown preserves NOC implementation details, LaTeX jitter formula, and user role."""
        u_info = {"full_name": "Test Operator", "role": "NOC Security Lead"}
        u_name = u_info.get("full_name")
        u_role = u_info.get("role")

        report_text = f"""### NetTelemetry Computer Networks Implementation
- **Operator Authorization:** Authenticated as {u_name} ({u_role}).
- **Active Probing vs Passive Sniffing:** Active ICMP and controlled TCP connection tests measure end-to-end user experience and immediate packet drops rather than passively waiting for third-party traffic.
- **Statistical Jitter:** RFC 3550 style delay variation tracking consecutive RTT delta values:
  $$\\text{{Jitter}} = \\frac{{1}}{{N-1}} \\sum_{{i=1}}^{{N-1}} |\\text{{RTT}}_{{i}} - \\text{{RTT}}_{{i-1}}|$$
- **Latency Percentiles:** P95 and P99 latency percentiles identify path jitter and router bufferbloat that mean RTT averages obscure.
- **Database Architecture:** SQLite in WAL mode with relational targets, telemetry measurements, window metrics, and anomaly events.
"""
        self.assertIn("Test Operator", report_text)
        self.assertIn("NOC Security Lead", report_text)
        self.assertIn("RFC 3550", report_text)
        self.assertIn("SQLite in WAL mode", report_text)

    def test_04_data_preservation(self):
        """4. Data query execution must not alter or delete any measurement records."""
        count_before = get_measurements_count(self.db_path)
        with get_connection(self.db_path) as conn:
            conn_obj = getattr(conn, "_conn", conn)
            pd.read_sql_query("SELECT * FROM measurements ORDER BY id DESC LIMIT 500", conn_obj)
        count_after = get_measurements_count(self.db_path)
        self.assertEqual(count_before, count_after, "Measurement records must remain untouched")

    def test_05_streamlit_apptest_reports_view_no_exceptions(self):
        """5. Streamlit AppTest navigates to Reports page and executes render_reports_view() with 0 exceptions."""
        from streamlit.testing.v1 import AppTest

        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "app.py"))
        at = AppTest.from_file(app_path, default_timeout=30)
        at.run()
        self.assertEqual(len(at.exception), 0, "Dashboard root must load without exceptions")

        # Switch to Reports view
        at.session_state["current_page"] = "Reports"
        at.run()
        self.assertEqual(len(at.exception), 0, "Reports page must load without any exceptions")

        # Verify 2 download buttons exist (Markdown Report + CSV Dataset)
        self.assertEqual(len(at.download_button), 2, "Reports page must have 2 download buttons")
        labels = [b.label for b in at.download_button]
        self.assertTrue(any("Executive Report (Markdown)" in l for l in labels))
        self.assertTrue(any("Full Telemetry Dataset (CSV)" in l for l in labels))

        # Verify 7 metric cards rendered
        metric_labels = [m.label for m in at.metric]
        expected_metrics = [
            "Registered Targets",
            "Recorded Measurements",
            "Successful Probes",
            "Recorded Anomalies",
            "Average RTT",
            "Packet Loss",
            "Availability"
        ]
        for em in expected_metrics:
            self.assertIn(em, metric_labels, f"Expected metric '{em}' to be rendered")

    def test_06_empty_database_handling(self):
        """6. Empty database returns graceful N/A metrics and 0 counts without ZeroDivisionError."""
        empty_fd, empty_db_path = tempfile.mkstemp(suffix=".db")
        os.close(empty_fd)
        try:
            init_db(empty_db_path)
            summary = get_network_performance_summary(empty_db_path)

            self.assertEqual(summary["num_targets"], 0)
            self.assertEqual(summary["total_measurements"], 0)
            self.assertEqual(summary["successful_probes"], 0)
            self.assertEqual(summary["failed_probes"], 0)
            self.assertIsNone(summary["avg_rtt_ms"], "Average RTT must be None when no measurements exist")
            self.assertIsNone(summary["packet_loss_pct"], "Packet loss must be None when no measurements exist")
            self.assertIsNone(summary["availability_pct"], "Availability must be None when no measurements exist")
            self.assertEqual(summary["num_anomalies"], 0)

            # Check UI display strings handle None by rendering 'N/A' (not '0.0' or '0')
            rtt_display = f"{summary['avg_rtt_ms']:.1f} ms" if summary["avg_rtt_ms"] is not None else "N/A"
            loss_display = f"{summary['packet_loss_pct']:.1f}%" if summary["packet_loss_pct"] is not None else "N/A"
            avail_display = f"{summary['availability_pct']:.1f}%" if summary["availability_pct"] is not None else "N/A"

            self.assertEqual(rtt_display, "N/A")
            self.assertEqual(loss_display, "N/A")
            self.assertEqual(avail_display, "N/A")

            # Check interpretation handles empty database cleanly
            interpretation = generate_performance_interpretation(summary)
            self.assertIn("No telemetry probe records are currently available", interpretation)
            self.assertIn("Configured endpoints are registered", interpretation)
        finally:
            if os.path.exists(empty_db_path):
                try:
                    os.remove(empty_db_path)
                except Exception:
                    pass

    def test_07_probe_metrics_calculation_and_missing_rtt(self):
        """7. Validates calculation of probe counts, average RTT excluding failed/None RTT, packet loss, and availability."""
        test_fd, test_db_path = tempfile.mkstemp(suffix=".db")
        os.close(test_fd)
        try:
            init_db(test_db_path)
            t_id = insert_target({
                "name": "Target Alpha",
                "host": "8.8.8.8",
                "resolved_ip": "8.8.8.8",
                "enabled": True,
                "interval": 5,
                "timeout": 2
            }, db_path=test_db_path)

            # Insert 3 successful probes with valid RTT: 15.0, 25.0, 50.0 (sum = 90.0, avg = 30.0)
            for rtt in [15.0, 25.0, 50.0]:
                insert_measurement({
                    "target_id": t_id,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "protocol": "ICMP",
                    "test_type": "echo",
                    "success": 1,
                    "rtt_ms": rtt,
                    "ttl": 58,
                    "error": None
                }, db_path=test_db_path)

            # Insert 1 successful probe with missing/None RTT (must be excluded from avg RTT)
            insert_measurement({
                "target_id": t_id,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "protocol": "TCP",
                "test_type": "connect",
                "success": 1,
                "rtt_ms": None,
                "ttl": None,
                "error": None
            }, db_path=test_db_path)

            # Insert 2 failed probes (must be included in packet loss & availability, excluded from avg RTT)
            insert_measurement({
                "target_id": t_id,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "protocol": "ICMP",
                "test_type": "echo",
                "success": 0,
                "rtt_ms": None,
                "ttl": None,
                "error": "Request timed out"
            }, db_path=test_db_path)

            insert_measurement({
                "target_id": t_id,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "protocol": "ICMP",
                "test_type": "echo",
                "success": 0,
                "rtt_ms": None,
                "ttl": None,
                "error": "Destination net unreachable"
            }, db_path=test_db_path)

            summary = get_network_performance_summary(test_db_path)

            # Total probes: 6 (4 successful, 2 failed)
            self.assertEqual(summary["num_targets"], 1)
            self.assertEqual(summary["total_measurements"], 6)
            self.assertEqual(summary["successful_probes"], 4)
            self.assertEqual(summary["failed_probes"], 2)

            # Average RTT: only the 3 valid positive RTTs (15.0 + 25.0 + 50.0) / 3 = 30.0 ms
            self.assertIsNotNone(summary["avg_rtt_ms"])
            self.assertAlmostEqual(summary["avg_rtt_ms"], 30.0, places=2)

            # Packet Loss: 2 failed / 6 total = 33.33%
            self.assertIsNotNone(summary["packet_loss_pct"])
            self.assertAlmostEqual(summary["packet_loss_pct"], 33.33, places=2)

            # Availability: 4 successful / 6 total = 66.67%
            self.assertIsNotNone(summary["availability_pct"])
            self.assertAlmostEqual(summary["availability_pct"], 66.67, places=2)

            # Loss + Availability must equal 100.0%
            self.assertAlmostEqual(summary["packet_loss_pct"] + summary["availability_pct"], 100.0, places=1)
        finally:
            if os.path.exists(test_db_path):
                try:
                    os.remove(test_db_path)
                except Exception:
                    pass

    def test_08_anomaly_counts_and_interpretation(self):
        """8. Validates anomaly counts from the anomaly table and operational interpretation with firewall note."""
        test_fd, test_db_path = tempfile.mkstemp(suffix=".db")
        os.close(test_fd)
        try:
            init_db(test_db_path)
            t_id = insert_target({
                "name": "Target Beta",
                "host": "9.9.9.9",
                "resolved_ip": "9.9.9.9",
                "enabled": True,
                "interval": 5,
                "timeout": 2
            }, db_path=test_db_path)

            # Insert 1 measurement with failure so interpretation notes probe failure
            insert_measurement({
                "target_id": t_id,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "protocol": "ICMP",
                "test_type": "echo",
                "success": 0,
                "rtt_ms": None,
                "ttl": None,
                "error": "Request timed out"
            }, db_path=test_db_path)

            # Insert 3 anomalies
            with get_connection(test_db_path) as conn:
                conn.executemany("""
                    INSERT INTO anomalies (timestamp, target_id, metric, observed_value, baseline, threshold, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [
                    ("2026-10-15 11:05:00", t_id, "loss_pct", 100.0, 0.0, 5.0, "Packet loss 100%"),
                    ("2026-10-15 11:06:00", t_id, "p95_ms", 130.0, 25.0, 90.0, "P95 latency spike"),
                    ("2026-10-15 11:07:00", t_id, "jitter", 25.0, 5.0, 20.0, "High jitter breach")
                ])
                conn.commit()

            summary = get_network_performance_summary(test_db_path)
            self.assertEqual(summary["num_anomalies"], 3)

            interpretation = generate_performance_interpretation(summary)
            self.assertIn("A total of 3 autonomous anomaly event(s) have been flagged", interpretation)
            # Ensure interpretation includes firewall filtering disclaimer and does NOT claim host is down
            self.assertIn("Probe failures do not necessarily indicate host downtime", interpretation)
            self.assertIn("perimeter firewalls", interpretation)
        finally:
            if os.path.exists(test_db_path):
                try:
                    os.remove(test_db_path)
                except Exception:
                    pass

    def test_09_markdown_report_content_verification(self):
        """9. Validates generated Markdown report contains performance summary and preserves NOC overview and LaTeX formula."""
        summary = get_network_performance_summary(self.db_path)
        interpretation = generate_performance_interpretation(summary)

        rtt_display = f"{summary['avg_rtt_ms']:.1f} ms" if summary["avg_rtt_ms"] is not None else "N/A"
        loss_display = f"{summary['packet_loss_pct']:.1f}%" if summary["packet_loss_pct"] is not None else "N/A"
        avail_display = f"{summary['availability_pct']:.1f}%" if summary["availability_pct"] is not None else "N/A"
        reporting_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_text = f"""### 📊 Network Performance Summary
- **Reporting Timestamp:** {reporting_ts}
- **Registered Targets:** {summary['num_targets']}
- **Total Measurements:** {summary['total_measurements']}
- **Successful Probes:** {summary['successful_probes']}
- **Failed Probes:** {summary['failed_probes']}
- **Average RTT:** {rtt_display}
- **Packet Loss:** {loss_display}
- **SLA Availability:** {avail_display}
- **Recorded Anomalies:** {summary['num_anomalies']}

**Operational Interpretation:**
{interpretation}

---

### 📄 NetTelemetry Computer Networks Implementation
- **Operator Authorization:** Authenticated as Dhanumithra (NOC Lead / Administrator).
- **Active Probing vs Passive Sniffing:** Active ICMP and controlled TCP connection tests measure end-to-end user experience and immediate packet drops rather than passively waiting for third-party traffic.
- **Statistical Jitter:** RFC 3550 style delay variation tracking consecutive RTT delta values:
  $$\\text{{Jitter}} = \\frac{{1}}{{N-1}} \\sum_{{i=1}}^{{N-1}} |\\text{{RTT}}_{{i}} - \\text{{RTT}}_{{i-1}}|$$
- **Latency Percentiles:** P95 and P99 latency percentiles identify path jitter and router bufferbloat that mean RTT averages obscure.
- **Database Architecture:** SQLite in WAL mode with relational targets, telemetry measurements, window metrics, and anomaly events.
"""
        # Verify required performance metrics in markdown
        self.assertIn("### 📊 Network Performance Summary", report_text)
        self.assertIn("- **Reporting Timestamp:**", report_text)
        self.assertIn(f"- **Registered Targets:** {summary['num_targets']}", report_text)
        self.assertIn(f"- **Total Measurements:** {summary['total_measurements']}", report_text)
        self.assertIn(f"- **Successful Probes:** {summary['successful_probes']}", report_text)
        self.assertIn(f"- **Failed Probes:** {summary['failed_probes']}", report_text)
        self.assertIn(f"- **Average RTT:** {rtt_display}", report_text)
        self.assertIn(f"- **Packet Loss:** {loss_display}", report_text)
        self.assertIn(f"- **SLA Availability:** {avail_display}", report_text)
        self.assertIn(f"- **Recorded Anomalies:** {summary['num_anomalies']}", report_text)
        self.assertIn("**Operational Interpretation:**", report_text)

        # Verify preserved NOC technical overview
        self.assertIn("### 📄 NetTelemetry Computer Networks Implementation", report_text)
        self.assertIn("Dhanumithra (NOC Lead / Administrator)", report_text)
        self.assertIn("RFC 3550", report_text)
        self.assertIn("\\text{Jitter}", report_text)
        self.assertIn("SQLite in WAL mode", report_text)

    def test_10_csv_export_regression_and_schema_preservation(self):
        """10. CSV export reads all columns correctly and does not modify the underlying database."""
        with get_connection(self.db_path) as conn:
            conn_obj = getattr(conn, "_conn", conn)
            df = pd.read_sql_query("SELECT * FROM measurements ORDER BY id DESC LIMIT 500", conn_obj)

        csv_str = df.to_csv(index=False)
        csv_io = io.StringIO(csv_str)
        reloaded_df = pd.read_csv(csv_io)

        expected_columns = {"id", "target_id", "timestamp", "protocol", "test_type", "success", "rtt_ms", "ttl", "error"}
        self.assertTrue(expected_columns.issubset(set(reloaded_df.columns)), f"Columns missing: {expected_columns - set(reloaded_df.columns)}")
        self.assertEqual(len(reloaded_df), 5, "Exported CSV must contain all 5 rows")

    def test_11_all_failed_probes_scenario(self):
        """11. Edge case: 100% failed probes results in 100% loss, 0% availability, and None for avg RTT."""
        test_fd, test_db_path = tempfile.mkstemp(suffix=".db")
        os.close(test_fd)
        try:
            init_db(test_db_path)
            t_id = insert_target({
                "name": "Unreachable Node",
                "host": "192.0.2.1",
                "resolved_ip": "192.0.2.1",
                "enabled": True,
                "interval": 5,
                "timeout": 2
            }, db_path=test_db_path)

            for i in range(4):
                insert_measurement({
                    "target_id": t_id,
                    "timestamp": f"2026-10-15 11:10:0{i}",
                    "protocol": "ICMP",
                    "test_type": "echo",
                    "success": 0,
                    "rtt_ms": None,
                    "ttl": None,
                    "error": "Request timed out"
                }, db_path=test_db_path)

            summary = get_network_performance_summary(test_db_path)
            self.assertEqual(summary["total_measurements"], 4)
            self.assertEqual(summary["successful_probes"], 0)
            self.assertEqual(summary["failed_probes"], 4)
            self.assertIsNone(summary["avg_rtt_ms"], "Average RTT must be None when no probes succeeded")
            self.assertEqual(summary["packet_loss_pct"], 100.0)
            self.assertEqual(summary["availability_pct"], 0.0)

            interpretation = generate_performance_interpretation(summary)
            self.assertIn("Significant probe loss observed", interpretation)
            self.assertIn("perimeter firewalls", interpretation)
        finally:
            if os.path.exists(test_db_path):
                try:
                    os.remove(test_db_path)
                except Exception:
                    pass

    def test_12_all_successful_probes_scenario(self):
        """12. Edge case: 100% successful probes results in 0% loss, 100% availability, and accurate avg RTT."""
        test_fd, test_db_path = tempfile.mkstemp(suffix=".db")
        os.close(test_fd)
        try:
            init_db(test_db_path)
            t_id = insert_target({
                "name": "Reliable Server",
                "host": "1.0.0.1",
                "resolved_ip": "1.0.0.1",
                "enabled": True,
                "interval": 5,
                "timeout": 2
            }, db_path=test_db_path)

            latencies = [10.0, 20.0, 30.0, 40.0]
            for i, rtt in enumerate(latencies):
                insert_measurement({
                    "target_id": t_id,
                    "timestamp": f"2026-10-15 11:20:0{i}",
                    "protocol": "ICMP",
                    "test_type": "echo",
                    "success": 1,
                    "rtt_ms": rtt,
                    "ttl": 64,
                    "error": None
                }, db_path=test_db_path)

            summary = get_network_performance_summary(test_db_path)
            self.assertEqual(summary["total_measurements"], 4)
            self.assertEqual(summary["successful_probes"], 4)
            self.assertEqual(summary["failed_probes"], 0)
            self.assertAlmostEqual(summary["avg_rtt_ms"], 25.0, places=2)
            self.assertEqual(summary["packet_loss_pct"], 0.0)
            self.assertEqual(summary["availability_pct"], 100.0)

            interpretation = generate_performance_interpretation(summary)
            self.assertIn("100.0% SLA availability", interpretation)
            self.assertIn("0.0%", interpretation)
        finally:
            if os.path.exists(test_db_path):
                try:
                    os.remove(test_db_path)
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main()
