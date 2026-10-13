import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import sys

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import (
    seed_default_data,
    get_all_targets,
    get_target_latest_status,
    get_recent_measurements,
    get_active_anomalies,
    get_connection,
    insert_target,
    DB_PATH
)
from telemetry.collector import probe_all_targets
from dashboard.styles import get_custom_css
from dashboard.components import (
    render_top_header,
    render_top_header_actions,
    render_hero_greeting,
    render_kpi_card_1,
    render_kpi_card_2,
    render_kpi_card_3,
    render_kpi_card_4,
    create_topology_map_figure,
    create_performance_trends_figure,
    create_availability_donut_figure,
    render_latency_progress_bars,
    render_live_target_status_list,
    render_active_alerts_list,
    render_recent_activity_rows,
    get_brand_icon
)

# 1. Page Configuration
st.set_page_config(
    layout="wide",
    page_title="NetTelemetry",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# 2. Inject Design System & CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# 3. Ensure Database is seeded
seed_default_data()

# 4. Session State for Navigation & Filters
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"
if "trend_timeframe" not in st.session_state:
    st.session_state["trend_timeframe"] = "1h"
if "map_view" not in st.session_state:
    st.session_state["map_view"] = "World View"
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

# --- Sidebar UI Matching Mockup ---
with st.sidebar:
    # Brand Header
    st.markdown("""
    <div class="sidebar-brand-container">
        <div class="brand-icon-wrapper">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
        </div>
        <div>
            <div class="brand-title">NetTelemetry</div>
            <div class="brand-subtitle">Observe • Analyze • Stay Ahead</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Menu
    pages = [
        ("Dashboard", "🏠"),
        ("Targets", "🎯"),
        ("Measurements", "📊"),
        ("Analytics", "📈"),
        ("Alerts", "🔔"),
        ("Reports", "📄"),
        ("Settings", "⚙️")
    ]

    selected_nav = st.radio(
        "Navigation",
        [p[0] for p in pages],
        index=[p[0] for p in pages].index(st.session_state["current_page"]),
        label_visibility="collapsed"
    )
    st.session_state["current_page"] = selected_nav

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Quick Probe Action
    if st.button("⚡ Probe Active Targets", use_container_width=True, help="Executes live network ping probes to targets immediately"):
        with st.spinner("Probing targets via ICMP/TCP..."):
            probe_all_targets()
            st.success("Telemetry updated!")
            st.rerun()

    st.markdown("---")

    # Ambient soundwave graphic & Status pill at bottom
    st.markdown("""
    <div class="sidebar-bottom-container">
        <svg viewBox="0 0 260 40" style="width:100%; height:32px; opacity:0.35; margin-bottom:8px;">
            <path d="M0,20 Q30,5 60,20 T120,20 T180,20 T240,20" fill="none" stroke="#10b981" stroke-width="1.5"/>
            <path d="M0,20 Q40,35 80,20 T160,20 T240,20" fill="none" stroke="#06b6d4" stroke-width="1"/>
        </svg>
        <div class="sidebar-status-card">
            <div class="status-dot-pulse"></div>
            <div>
                <div class="status-text-title">System Online</div>
                <div class="status-text-sub">All services running</div>
            </div>
        </div>
        <div class="sidebar-footer-version">NetTelemetry v1.0.0</div>
    </div>
    """, unsafe_allow_html=True)


# --- Real-Time Dashboard View Fragment ---
@st.fragment(run_every="10s")
def render_dashboard_content():
    # Fetch latest data from SQLite
    targets = get_target_latest_status()
    recent_measurements = get_recent_measurements(limit=5)
    anomalies = get_active_anomalies(limit=3)

    # Filter targets if search entered
    q = st.session_state.get("search_query", "").strip().lower()
    if q:
        filtered_targets = [t for t in targets if q in t["name"].lower() or q in t["host"].lower()]
    else:
        filtered_targets = targets

    # Summary calculations
    total_targets = len(targets)
    online_count = sum(1 for t in targets if t["status"] == "Online")
    offline_count = sum(1 for t in targets if t["status"] == "Offline")
    
    valid_rtts = [t["rtt_ms"] for t in targets if t["rtt_ms"] > 0]
    avg_rtt = sum(valid_rtts) / len(valid_rtts) if valid_rtts else 32.0
    
    avg_loss = sum(t["loss_pct"] for t in targets) / total_targets if total_targets else 2.4
    avail_pct = 100.0 - avg_loss

    # Top utility row: Interactive Search bar on left, action controls on right
    search_col, actions_col = st.columns([1.1, 1.9])
    with search_col:
        search_query = st.text_input(
            "Search target",
            placeholder="🔍 Search target (IP or hostname)...",
            value=st.session_state.get("search_query", ""),
            label_visibility="collapsed"
        )
        st.session_state["search_query"] = search_query
    with actions_col:
        st.markdown(render_top_header_actions(), unsafe_allow_html=True)

    # Greeting Banner
    st.markdown(render_hero_greeting(), unsafe_allow_html=True)

    # 2-Column Responsive Layout
    col_main, col_side = st.columns([2.15, 1.0], gap="medium")

    # ==========================
    # COLUMN 1: MAIN METRICS & MAP (WIDE)
    # ==========================
    with col_main:
        # 1. 4 KPI Cards Row
        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.markdown(render_kpi_card_1(total_targets=total_targets, online=online_count, offline=offline_count), unsafe_allow_html=True)
        with kpi_cols[1]:
            st.markdown(render_kpi_card_2(avg_rtt=avg_rtt, change_pct=-18.0), unsafe_allow_html=True)
        with kpi_cols[2]:
            st.markdown(render_kpi_card_3(loss_pct=avg_loss, change_pct=-6.0), unsafe_allow_html=True)
        with kpi_cols[3]:
            st.markdown(render_kpi_card_4(avail_pct=avail_pct, change_pct=2.1), unsafe_allow_html=True)

        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

        # 2. Network Topology Card
        st.markdown('<div class="noc-card" style="padding-bottom: 0.5rem; margin-bottom: 0.75rem;">', unsafe_allow_html=True)
        map_hdr_l, map_hdr_r = st.columns([1.8, 1.2])
        with map_hdr_l:
            st.markdown("""
            <div style="display:flex; align-items:center; gap:8px; padding-top:4px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                    <circle cx="18" cy="5" r="3"></circle>
                    <circle cx="6" cy="12" r="3"></circle>
                    <circle cx="18" cy="19" r="3"></circle>
                    <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                    <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                </svg>
                <span class="card-title-text" style="font-size:1rem;">Network Topology</span>
                <span class="live-badge-pill">Live</span>
            </div>
            """, unsafe_allow_html=True)
        with map_hdr_r:
            map_tabs = st.radio(
                "Topology View",
                ["World View", "Region", "List"],
                index=["World View", "Region", "List"].index(st.session_state["map_view"]),
                horizontal=True,
                label_visibility="collapsed"
            )
            st.session_state["map_view"] = map_tabs

        if map_tabs == "World View" or map_tabs == "Region":
            map_fig = create_topology_map_figure(filtered_targets)
            st.plotly_chart(map_fig, use_container_width=True, config={"displayModeBar": False, "staticPlot": False})
        else:
            # List View
            list_df = pd.DataFrame([{
                "Target": t["name"],
                "IP Address": t["host"],
                "Status": t["status"],
                "Current RTT (ms)": f"{t['rtt_ms']} ms",
                "Packet Loss (%)": f"{t['loss_pct']}%",
                "Coordinates": f"({t['lat']:.2f}, {t['lon']:.2f})"
            } for t in filtered_targets])
            st.dataframe(list_df, use_container_width=True, hide_index=True)

        # Map Legend
        st.markdown("""
        <div class="map-legend-bar" style="margin-top: -10px; margin-bottom: 10px; padding-left: 10px;">
            <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div><span>Online</span></div>
            <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div><span>Degraded</span></div>
            <div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div><span>Offline</span></div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Bottom Grid: 3 Cards (Performance Trends, Packet Loss & Availability, Top Targets by Latency)
        bg_col1, bg_col2, bg_col3 = st.columns([1.35, 1.0, 1.0], gap="small")

        # Bottom Card 1: Performance Trends
        with bg_col1:
            st.markdown('<div class="noc-card" style="height: 100%;">', unsafe_allow_html=True)
            perf_hdr_l, perf_hdr_r = st.columns([1.3, 1.1])
            with perf_hdr_l:
                st.markdown("""
                <div style="display:flex; align-items:center; gap:6px; padding-top:4px;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                        <polyline points="17 6 23 6 23 12"></polyline>
                    </svg>
                    <span class="card-title-text" style="font-size:0.875rem;">Performance Trends</span>
                </div>
                """, unsafe_allow_html=True)
            with perf_hdr_r:
                tf_tabs = st.radio(
                    "Trend Timeframe",
                    ["1h", "6h", "24h", "7d"],
                    index=["1h", "6h", "24h", "7d"].index(st.session_state["trend_timeframe"]),
                    horizontal=True,
                    label_visibility="collapsed"
                )
                st.session_state["trend_timeframe"] = tf_tabs

            trend_fig = create_performance_trends_figure()
            st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        # Bottom Card 2: Packet Loss & Availability Donut
        with bg_col2:
            st.markdown("""
            <div class="noc-card" style="height: 100%;">
                <div class="card-title-bar">
                    <div class="card-title-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                            <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                            <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                        </svg>
                        <span class="card-title-text" style="font-size:0.875rem;">Packet Loss & Availability</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            donut_fig = create_availability_donut_figure(avail_pct=avail_pct, successful=1217, failed=29)
            st.plotly_chart(donut_fig, use_container_width=True, config={"displayModeBar": False})

            st.markdown("""
            <div style="font-size: 0.75rem; color:#64748b; margin-top:-10px; display:flex; flex-direction:column; gap:4px; padding-left:12px;">
                <div style="display:flex; align-items:center; gap:6px;"><span style="width:7px; height:7px; border-radius:50%; background:#10b981;"></span><span>Successful: <b style="color:#1e293b;">1,217</b></span></div>
                <div style="display:flex; align-items:center; gap:6px;"><span style="width:7px; height:7px; border-radius:50%; background:#f43f5e;"></span><span>Failed: <b style="color:#1e293b;">29</b></span></div>
                <div style="display:flex; align-items:center; gap:6px;"><span style="width:7px; height:7px; border-radius:50%; background:#94a3b8;"></span><span>Packet Loss: <b style="color:#1e293b;">2.4%</b></span></div>
            </div>
            """, unsafe_allow_html=True)

        # Bottom Card 3: Top Targets by Latency
        with bg_col3:
            st.markdown("""
            <div class="noc-card" style="height: 100%;">
                <div class="card-title-bar">
                    <div class="card-title-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                            <line x1="18" y1="20" x2="18" y2="10"></line>
                            <line x1="12" y1="20" x2="12" y2="4"></line>
                            <line x1="6" y1="20" x2="6" y2="14"></line>
                        </svg>
                        <span class="card-title-text" style="font-size:0.875rem;">Top Targets by Latency</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            latency_bars_html = render_latency_progress_bars(targets)
            st.markdown(f"""
            <div style="background:#ffffff; border-radius:10px; padding:0.5rem;">
                {latency_bars_html}
            </div>
            """, unsafe_allow_html=True)

    # ==========================
    # COLUMN 2: COMPACT RIGHT PANEL (~30%)
    # ==========================
    with col_side:
        # Card 1: Live Target Status
        target_list_html = render_live_target_status_list(targets)
        st.markdown(f"""
        <div class="noc-card">
            <div class="card-title-bar">
                <div class="card-title-left">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                        <rect x="2" y="2" width="20" height="20" rx="4"></rect>
                        <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                    <span class="card-title-text">Live Target Status</span>
                </div>
                <span class="view-all-link">View All →</span>
            </div>
            <div>
                {target_list_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card 2: Active Alerts
        alerts_html = render_active_alerts_list(anomalies)
        st.markdown(f"""
        <div class="noc-card">
            <div class="card-title-bar">
                <div class="card-title-left">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                    </svg>
                    <span class="card-title-text">Active Alerts</span>
                </div>
                <span class="view-all-link">View All →</span>
            </div>
            <div>
                {alerts_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card 3: Recent Activity
        activity_html = render_recent_activity_rows(recent_measurements)
        st.markdown(f"""
        <div class="noc-card">
            <div class="card-title-bar">
                <div class="card-title-left">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    <span class="card-title-text">Recent Activity</span>
                </div>
                <span class="view-all-link">View All →</span>
            </div>
            <div>
                {activity_html}
            </div>
        </div>
        """, unsafe_allow_html=True)


# --- Supplementary Views (When sidebar menu is clicked) ---

def render_targets_view():
    st.markdown("<h2 style='color:#0f172a;'>🎯 Network Targets Management</h2>", unsafe_allow_html=True)
    st.caption("Inspect and configure active network monitoring targets stored in SQLite.")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM targets", conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)

    with st.expander("Add New Monitored Target"):
        with st.form("new_target_form"):
            t_id = st.text_input("Target ID (e.g. quad9)")
            t_name = st.text_input("Name (e.g. Quad9 DNS)")
            t_host = st.text_input("Host IP/Domain (e.g. 9.9.9.9)")
            col1, col2 = st.columns(2)
            with col1:
                t_lat = st.number_input("Latitude", value=40.7128)
            with col2:
                t_lon = st.number_input("Longitude", value=-74.0060)
            
            submitted = st.form_submit_button("Add Target to Network Monitor")
            if submitted and t_name and t_host:
                insert_target({
                    "name": t_name,
                    "host": t_host,
                    "resolved_ip": t_host,
                    "lat": t_lat,
                    "lon": t_lon,
                    "enabled": True,
                    "interval": 5,
                    "timeout": 2
                })
                st.success(f"Added {t_name} successfully!")
                st.rerun()

def render_measurements_view():
    st.markdown("<h2 style='color:#0f172a;'>📊 Telemetry Measurements Log</h2>", unsafe_allow_html=True)
    st.caption("Raw ICMP / TCP packet-level telemetry records stored in SQLite database.")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM measurements ORDER BY id DESC LIMIT 200", conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)

def render_analytics_view():
    st.markdown("<h2 style='color:#0f172a;'>📈 Performance Analytics & Aggregated Windows</h2>", unsafe_allow_html=True)
    st.caption("Rolling statistical windows: Jitter, Availability, P95, and P99 percentiles.")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM window_metrics ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)

def render_alerts_view():
    st.markdown("<h2 style='color:#0f172a;'>🔔 Anomaly Detection Timeline</h2>", unsafe_allow_html=True)
    st.caption("Autonomous threshold evaluations and historical network degradation flags.")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM anomalies ORDER BY id DESC LIMIT 50", conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)

def render_reports_view():
    st.markdown("<h2 style='color:#0f172a;'>📄 Network Operations Center (NOC) Executive Report</h2>", unsafe_allow_html=True)
    st.markdown("""
    ### NetTelemetry Computer Networks Implementation
    - **Active Probing vs Passive Sniffing:** Active ICMP and controlled TCP connection tests measure end-to-end user experience and immediate packet drops rather than passively waiting for third-party traffic.
    - **Statistical Jitter:** RFC 3550 style delay variation tracking consecutive RTT delta values:
      $$\\text{Jitter} = \\frac{1}{N-1} \\sum_{i=1}^{N-1} |\\text{RTT}_i - \\text{RTT}_{i-1}|$$
    - **Latency Percentiles:** P95 and P99 latency percentiles identify path jitter and router bufferbloat that mean RTT averages obscure.
    """)

def render_settings_view():
    st.markdown("<h2 style='color:#0f172a;'>⚙️ Telemetry Settings & Thresholds</h2>", unsafe_allow_html=True)
    st.number_input("RTT Anomaly Spike Threshold (ms)", value=90.0)
    st.number_input("Packet Loss Warning Threshold (%)", value=5.0)
    st.number_input("Jitter Threshold (ms)", value=20.0)
    st.button("Save Settings")


# --- Main Router ---
if st.session_state["current_page"] == "Dashboard":
    render_dashboard_content()
elif st.session_state["current_page"] == "Targets":
    render_targets_view()
elif st.session_state["current_page"] == "Measurements":
    render_measurements_view()
elif st.session_state["current_page"] == "Analytics":
    render_analytics_view()
elif st.session_state["current_page"] == "Alerts":
    render_alerts_view()
elif st.session_state["current_page"] == "Reports":
    render_reports_view()
elif st.session_state["current_page"] == "Settings":
    render_settings_view()
