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
    authenticate_user,
    create_user,
    get_user_by_username,
    DB_PATH
)
from telemetry.collector import probe_all_targets, collect_icmp_target
from telemetry.metrics import calculate_rolling_statistics
from analytics.anomaly_detector import AnomalyDetector
from dashboard.styles import get_custom_css
from dashboard.components import (
    render_top_header,
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
    get_brand_icon,
    clean_html
)

# 1. Page Configuration
st.set_page_config(
    layout="wide",
    page_title="NetTelemetry",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# 2. Initialize Database Exactly Once
@st.cache_resource
def initialize_database():
    seed_default_data()
    return True

initialize_database()

# 3. Session State Initialization
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"
if "trend_timeframe" not in st.session_state:
    st.session_state["trend_timeframe"] = "1h"
if "map_view" not in st.session_state:
    st.session_state["map_view"] = "World View"
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""
if "thresh_rtt" not in st.session_state:
    st.session_state["thresh_rtt"] = 90.0
if "thresh_loss" not in st.session_state:
    st.session_state["thresh_loss"] = 5.0
if "thresh_jitter" not in st.session_state:
    st.session_state["thresh_jitter"] = 20.0
if "auto_probe" not in st.session_state:
    st.session_state["auto_probe"] = False
if "probe_cadence" not in st.session_state:
    st.session_state["probe_cadence"] = "5s (Fast)"
if "status_filter" not in st.session_state:
    st.session_state["status_filter"] = "All"

# Default pre-seeded authenticated user (Dhanumithra)
if "user" not in st.session_state:
    st.session_state["user"] = get_user_by_username("dhanumithra") or {
        "id": 1,
        "username": "dhanumithra",
        "full_name": "Dhanumithra",
        "email": "dhanu@telemetry.noc",
        "role": "NOC Lead / Administrator"
    }

is_dark = st.session_state["dark_mode"]

# 4. Inject Design System & CSS
st.markdown(get_custom_css(dark_mode=is_dark), unsafe_allow_html=True)


# ==========================================
# AUTHENTICATION PORTAL (When Logged Out)
# ==========================================
def render_auth_portal():
    st.html("""
    <div style="text-align:center; margin-top:2.5rem; margin-bottom:1.5rem;">
        <div style="display:inline-flex; align-items:center; justify-content:center; width:52px; height:52px; background:rgba(16, 185, 129, 0.15); border-radius:12px; margin-bottom:0.75rem;">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
        </div>
        <h1 style="font-size:1.85rem; font-weight:800; color:var(--text-primary); margin:0;">NetTelemetry</h1>
        <div style="font-size:0.875rem; color:var(--text-secondary); margin-top:4px;">Enterprise Network Operation Center (NOC) Portal</div>
    </div>
    """)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 1.4, 1])
    with auth_col2:
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["🔐 Operator Sign In", "📝 Register New Account"])

            with tab_login:
                st.markdown("##### Sign in to access live telemetry")
                login_user = st.text_input("Username", value="dhanumithra", key="login_username")
                login_pwd = st.text_input("Password", type="password", value="admin", key="login_password")

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🔐 Sign In", use_container_width=True, type="primary"):
                        user = authenticate_user(login_user, login_pwd)
                        if user:
                            st.session_state["user"] = user
                            st.toast(f"Welcome back, {user['full_name']}!", icon="👋")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
                with col_btn2:
                    if st.button("⚡ Demo Login", use_container_width=True):
                        st.session_state["user"] = get_user_by_username("dhanumithra") or {
                            "id": 1,
                            "username": "dhanumithra",
                            "full_name": "Dhanumithra",
                            "email": "dhanu@telemetry.noc",
                            "role": "NOC Lead / Administrator"
                        }
                        st.toast("Signed in as Dhanumithra (NOC Lead)", icon="✅")
                        st.rerun()

                st.markdown("---")
                if st.button("👤 Continue as Guest Observer (Read-Only)", use_container_width=True):
                    st.session_state["user"] = {
                        "id": 99,
                        "username": "guest",
                        "full_name": "Guest Observer",
                        "email": "guest@telemetry.noc",
                        "role": "Guest / Read-Only Observer"
                    }
                    st.toast("Guest session active", icon="👀")
                    st.rerun()

            with tab_register:
                st.markdown("##### Create new NOC Operator profile")
                reg_name = st.text_input("Full Name", placeholder="e.g. Alex Morgan")
                reg_user = st.text_input("Username", placeholder="e.g. alex")
                reg_email = st.text_input("Email", placeholder="e.g. alex@telemetry.noc")
                reg_pwd = st.text_input("Password", type="password")
                reg_role = st.selectbox("Role", ["NOC Operator", "Network Engineer", "Security Analyst", "Systems Architect"])

                if st.button("Create Account & Access NOC", use_container_width=True):
                    if reg_name and reg_user and reg_pwd:
                        uid = create_user(reg_user, reg_name, reg_pwd, email=reg_email, role=reg_role)
                        if uid:
                            st.session_state["user"] = {
                                "id": uid,
                                "username": reg_user,
                                "full_name": reg_name,
                                "email": reg_email,
                                "role": reg_role
                            }
                            st.toast("Account created successfully!", icon="🎉")
                            st.rerun()
                        else:
                            st.error("Username already taken. Please choose another.")
                    else:
                        st.error("Please fill in Full Name, Username, and Password.")


# Check if user is logged in
if st.session_state.get("user") is None:
    render_auth_portal()
    st.stop()

# Active logged-in user details
curr_user = st.session_state["user"]
curr_user_name = curr_user.get("full_name", "Dhanumithra")
curr_role = curr_user.get("role", "NOC Lead / Administrator")


# ==========================================
# SIDEBAR NAVIGATION & TELEMETRY CONTROLS
# ==========================================
with st.sidebar:
    # Brand Header
    st.html(clean_html("""
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
    """))

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

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Real-Time Telemetry Engine Controls
    st.markdown("##### ⚡ Telemetry Engine")
    live_toggle = st.toggle("🔴 Real-Time Monitoring", value=st.session_state["auto_probe"], help="Automatically probes network targets on schedule and refreshes metrics")
    st.session_state["auto_probe"] = live_toggle

    if live_toggle:
        cadence_opts = ["5s (Fast)", "10s (Standard)", "30s (Eco)"]
        cadence_val = st.selectbox(
            "Probe Cadence",
            cadence_opts,
            index=cadence_opts.index(st.session_state.get("probe_cadence", "5s (Fast)"))
        )
        st.session_state["probe_cadence"] = cadence_val

    # Quick Probe & Refresh Actions
    if st.button("⚡ Probe All Targets Now", use_container_width=True, help="Executes live parallel network probes to targets immediately"):
        with st.spinner("Probing targets in parallel..."):
            probe_all_targets()
            st.session_state["last_probe_time"] = datetime.datetime.now().strftime("%I:%M:%S %p")
            st.toast("⚡ Active probes completed successfully!", icon="✅")
            st.rerun()

    if st.button("🔄 Refresh Data", use_container_width=True, help="Reload fresh metrics from SQLite"):
        st.rerun()

    st.markdown("---")

    # Ambient soundwave graphic & Status pill at bottom
    cadence_label = st.session_state.get("probe_cadence", "5s").split()[0]
    status_text = f"Live Engine ({cadence_label})" if live_toggle else "Monitoring Paused"
    sub_status = "Autonomous probing active" if live_toggle else "Manual refresh mode"
    st.html(clean_html(f"""
    <div class="sidebar-bottom-container">
        <svg viewBox="0 0 260 40" style="width:100%; height:32px; opacity:0.35; margin-bottom:8px;">
            <path d="M0,20 Q30,5 60,20 T120,20 T180,20 T240,20" fill="none" stroke="#10b981" stroke-width="1.5"/>
            <path d="M0,20 Q40,35 80,20 T160,20 T240,20" fill="none" stroke="#06b6d4" stroke-width="1"/>
        </svg>
        <div class="sidebar-status-card">
            <div class="status-dot-pulse"></div>
            <div>
                <div class="status-text-title">{status_text}</div>
                <div class="status-text-sub">{sub_status}</div>
            </div>
        </div>
        <div class="sidebar-footer-version">NetTelemetry v1.0.0 • {curr_user_name}</div>
    </div>
    """))


# ==========================================
# UNIVERSAL TOP NAVBAR (Available on ALL pages)
# ==========================================
def render_universal_top_navbar():
    is_dark = st.session_state.get("dark_mode", False)
    u_info = st.session_state.get("user", {})
    u_name = u_info.get("full_name", "Dhanumithra")
    u_role = u_info.get("role", "NOC Lead / Administrator")
    u_uname = u_info.get("username", "dhanumithra")
    u_email = u_info.get("email", "dhanu@telemetry.noc")

    anomalies = get_active_anomalies(limit=5)
    anom_count = len(anomalies)

    search_col, actions_col = st.columns([1.1, 1.9], gap="small")
    with search_col:
        search_query = st.text_input(
            "Search target",
            placeholder="🔍 Search target (IP or hostname)...",
            value=st.session_state.get("search_query", ""),
            label_visibility="collapsed",
            key="universal_search_input"
        )
        st.session_state["search_query"] = search_query

    with actions_col:
        act_c1, act_c2, act_c3 = st.columns([0.8, 1.0, 2.5], gap="small")
        with act_c1:
            theme_icon = "☀️" if is_dark else "🌙"
            if st.button(theme_icon, key="top_theme_btn", help="Toggle Light / Dark NOC Mode"):
                st.session_state["dark_mode"] = not is_dark
                st.rerun()
        with act_c2:
            bell_label = f"🔔 ({anom_count})" if anom_count > 0 else "🔔"
            with st.popover(bell_label, help="Active Alerts & Quick Notifications"):
                st.markdown("#### 🔔 System Notifications")
                if anomalies:
                    for a in anomalies:
                        st.markdown(f"- **{a.get('name', 'Host')}**: {a.get('reason', 'Network anomaly')}")
                    if st.button("🧹 Clear Notifications", key="pop_clear_all_notifs", use_container_width=True):
                        with get_connection() as conn:
                            conn.execute("DELETE FROM anomalies")
                            conn.commit()
                        st.toast("Notifications cleared.", icon="✅")
                        st.rerun()
                else:
                    st.success("All systems optimal. 0 active alerts.")
                if st.button("View Incident Log →", key="pop_goto_alerts", use_container_width=True):
                    st.session_state["current_page"] = "Alerts"
                    st.rerun()
        with act_c3:
            with st.popover(f"👤 {u_name} ▾", help="Operator Profile & Account Settings"):
                st.markdown("### 🛡️ Operator Session")
                st.markdown(f"**Name:** {u_name}")
                st.markdown(f"**Username:** `@{u_uname}`")
                st.markdown(f"**Role:** `{u_role}`")
                st.markdown(f"**Email:** {u_email}")
                st.markdown("**Session:** 🟢 Active NOC Authorization")
                st.divider()
                if st.button("🚪 Sign Out", key="btn_logout", use_container_width=True):
                    st.session_state["user"] = None
                    st.toast("Signed out successfully.", icon="👋")
                    st.rerun()

render_universal_top_navbar()


# ==========================================
# REAL-TIME DASHBOARD VIEW FRAGMENT
# ==========================================
cadence_raw = st.session_state.get("probe_cadence", "5s")
interval_sec = 5 if "5" in cadence_raw else (10 if "10" in cadence_raw else 30)
frag_interval = f"{interval_sec}s" if st.session_state.get("auto_probe", False) else None

@st.fragment(run_every=frag_interval)
def render_dashboard_content():
    is_dark = st.session_state.get("dark_mode", False)

    # If Real-Time Monitoring is ON, actively execute a parallel probe cycle
    if st.session_state.get("auto_probe", False):
        probe_all_targets()

    # Fetch latest metrics from SQLite
    targets = get_target_latest_status()
    recent_measurements = get_recent_measurements(limit=5)
    anomalies = get_active_anomalies(limit=3)

    # Filter targets if search entered
    q = st.session_state.get("search_query", "").strip().lower()
    if q:
        filtered_targets = [t for t in targets if q in t["name"].lower() or q in t["host"].lower()]
    else:
        filtered_targets = targets

    # Status filter from KPI operational bar
    sf = st.session_state.get("status_filter", "All")
    if sf != "All":
        filtered_targets = [t for t in filtered_targets if t["status"] == sf]

    # Summary calculations
    total_targets = len(targets)
    online_count = sum(1 for t in targets if t["status"] == "Online")
    degraded_count = sum(1 for t in targets if t["status"] == "Degraded")
    offline_count = sum(1 for t in targets if t["status"] == "Offline")
    
    valid_rtts = [t["rtt_ms"] for t in targets if t["rtt_ms"] > 0]
    avg_rtt = sum(valid_rtts) / len(valid_rtts) if valid_rtts else 32.0
    
    avg_loss = sum(t["loss_pct"] for t in targets) / total_targets if total_targets else 2.4
    avail_pct = 100.0 - avg_loss

    # Dynamic Greeting Banner with live state
    st.html(render_hero_greeting(
        user_name=curr_user_name,
        is_live=st.session_state.get("auto_probe", False),
        interval_sec=interval_sec
    ))

    # 2-Column Responsive Layout
    col_main, col_side = st.columns([2.15, 1.0], gap="medium")

    # ==========================
    # COLUMN 1: MAIN METRICS & MAP (WIDE)
    # ==========================
    with col_main:
        # 1. 4 KPI Cards Row
        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.html(render_kpi_card_1(total_targets=total_targets, online=online_count, offline=offline_count))
        with kpi_cols[1]:
            st.html(render_kpi_card_2(avg_rtt=avg_rtt, change_pct=-18.0))
        with kpi_cols[2]:
            st.html(render_kpi_card_3(loss_pct=avg_loss, change_pct=-6.0))
        with kpi_cols[3]:
            st.html(render_kpi_card_4(avail_pct=avail_pct, change_pct=2.1))

        # Operational Quick-Filter Pill Row
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        kf_1, kf_2, kf_3, kf_4, kf_5 = st.columns([1.1, 1, 1, 1, 1.2])
        with kf_1:
            if st.button(f"🔍 All ({total_targets})", key="kf_all", use_container_width=True):
                st.session_state["status_filter"] = "All"
                st.rerun()
        with kf_2:
            if st.button(f"🟢 Online ({online_count})", key="kf_online", use_container_width=True):
                st.session_state["status_filter"] = "Online"
                st.rerun()
        with kf_3:
            if st.button(f"🟡 Degraded ({degraded_count})", key="kf_deg", use_container_width=True):
                st.session_state["status_filter"] = "Degraded"
                st.rerun()
        with kf_4:
            if st.button(f"🔴 Offline ({offline_count})", key="kf_off", use_container_width=True):
                st.session_state["status_filter"] = "Offline"
                st.rerun()
        with kf_5:
            if st.button("⚡ Probe All", key="kf_probe_all", use_container_width=True):
                with st.spinner("Probing all targets in parallel..."):
                    probe_all_targets()
                    st.toast("⚡ All targets probed successfully!", icon="✅")
                    st.rerun()

        # 2. Network Topology Card
        with st.container(border=True):
            map_hdr_l, map_hdr_r = st.columns([1.8, 1.2])
            with map_hdr_l:
                st.html("""
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
                """)
            with map_hdr_r:
                map_tabs = st.radio(
                    "Topology View",
                    ["World View", "Region", "List"],
                    index=["World View", "Region", "List"].index(st.session_state["map_view"]),
                    horizontal=True,
                    label_visibility="collapsed"
                )
                st.session_state["map_view"] = map_tabs

            if map_tabs in ["World View", "Region"]:
                map_fig = create_topology_map_figure(filtered_targets, view_mode=map_tabs, is_dark=is_dark)
                st.plotly_chart(map_fig, use_container_width=True, config={"displayModeBar": False, "staticPlot": False})
            else:
                list_df = pd.DataFrame([{
                    "Target": t["name"],
                    "IP Address": t["host"],
                    "Status": t["status"],
                    "Current RTT (ms)": f"{t['rtt_ms']} ms",
                    "Packet Loss (%)": f"{t['loss_pct']}%",
                    "Coordinates": f"({t['lat']:.2f}, {t['lon']:.2f})"
                } for t in filtered_targets])
                st.dataframe(list_df, use_container_width=True, hide_index=True)

            st.html("""
            <div class="map-legend-bar" style="margin-top: -6px; margin-bottom: 4px; padding-left: 6px;">
                <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div><span>Online</span></div>
                <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div><span>Degraded</span></div>
                <div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div><span>Offline</span></div>
            </div>
            """)

        # 3. Bottom Grid: 3 Cards (Performance Trends, Packet Loss & Availability, Top Targets by Latency)
        bg_col1, bg_col2, bg_col3 = st.columns([1.35, 1.0, 1.0], gap="small")

        # Bottom Card 1: Performance Trends
        with bg_col1:
            with st.container(border=True):
                perf_hdr_l, perf_hdr_r = st.columns([1.3, 1.1])
                with perf_hdr_l:
                    st.html("""
                    <div style="display:flex; align-items:center; gap:6px; padding-top:4px;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                            <polyline points="17 6 23 6 23 12"></polyline>
                        </svg>
                        <span class="card-title-text" style="font-size:0.875rem;">Performance Trends</span>
                    </div>
                    """)
                with perf_hdr_r:
                    tf_tabs = st.radio(
                        "Trend Timeframe",
                        ["1h", "6h", "24h", "7d"],
                        index=["1h", "6h", "24h", "7d"].index(st.session_state["trend_timeframe"]),
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                    st.session_state["trend_timeframe"] = tf_tabs

                trend_fig = create_performance_trends_figure(timeframe=tf_tabs, is_dark=is_dark)
                st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})

        # Bottom Card 2: Packet Loss & Availability Donut
        with bg_col2:
            with st.container(border=True):
                st.html("""
                <div class="card-title-bar">
                    <div class="card-title-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                            <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                            <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                        </svg>
                        <span class="card-title-text" style="font-size:0.875rem;">Packet Loss & Availability</span>
                    </div>
                </div>
                """)

                donut_fig = create_availability_donut_figure(avail_pct=avail_pct, successful=1217, failed=29, is_dark=is_dark)
                st.plotly_chart(donut_fig, use_container_width=True, config={"displayModeBar": False})

                st.html("""
                <div style="font-size: 0.75rem; color:#64748b; margin-top:-6px; display:flex; flex-direction:column; gap:4px; padding-left:12px;">
                    <div style="display:flex; align-items:center; gap:6px;"><span style="width:7px; height:7px; border-radius:50%; background:#10b981;"></span><span>Successful: <b style="color:#1e293b;">1,217</b></span></div>
                    <div style="display:flex; align-items:center; gap:6px;"><span style="width:7px; height:7px; border-radius:50%; background:#f43f5e;"></span><span>Failed: <b style="color:#1e293b;">29</b></span></div>
                    <div style="display:flex; align-items:center; gap:6px;"><span style="width:7px; height:7px; border-radius:50%; background:#94a3b8;"></span><span>Packet Loss: <b style="color:#1e293b;">2.4%</b></span></div>
                </div>
                """)

        # Bottom Card 3: Top Targets by Latency
        with bg_col3:
            with st.container(border=True):
                st.html("""
                <div class="card-title-bar" style="margin-bottom: 0.75rem;">
                    <div class="card-title-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                            <line x1="18" y1="20" x2="18" y2="10"></line>
                            <line x1="12" y1="20" x2="12" y2="4"></line>
                            <line x1="6" y1="20" x2="6" y2="14"></line>
                        </svg>
                        <span class="card-title-text" style="font-size:0.875rem;">Top Targets by Latency</span>
                    </div>
                </div>
                """)
                st.html(render_latency_progress_bars(targets))

    # ==========================
    # COLUMN 2: FULLY INTERACTIVE RIGHT PANEL (~30%)
    # ==========================
    with col_side:
        # Card 1: Live Target Status (WITH INTERACTIVE PING BUTTONS)
        with st.container(border=True):
            tgt_h_l, tgt_h_r = st.columns([2.3, 1.2])
            with tgt_h_l:
                st.html("""
                <div class="card-title-bar" style="margin-bottom:0;">
                    <div class="card-title-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                            <rect x="2" y="2" width="20" height="20" rx="4"></rect>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                        <span class="card-title-text">Live Target Status</span>
                    </div>
                </div>
                """)
            with tgt_h_r:
                if st.button("View All →", key="view_all_targets", help="Open Targets Page"):
                    st.session_state["current_page"] = "Targets"
                    st.rerun()

            for idx, t in enumerate(targets):
                tr_c1, tr_c2, tr_c3 = st.columns([2.2, 1.6, 1.2], gap="small")
                with tr_c1:
                    status_dot = "🟢" if t["status"] == "Online" else ("🟡" if t["status"] == "Degraded" else "🔴")
                    st.markdown(f"{status_dot} **{t['name']}**  \n<span style='font-size:0.75rem; color:#64748b;'>{t.get('resolved_ip') or t['host']}</span>", unsafe_allow_html=True)
                with tr_c2:
                    st.markdown(f"**{int(round(t.get('rtt_ms', 0)))} ms**  \n<span style='font-size:0.75rem; color:#64748b;'>Loss: {t.get('loss_pct', 0):.1f}%</span>", unsafe_allow_html=True)
                with tr_c3:
                    if st.button("⚡ Ping", key=f"r_ping_{t['target_id']}_{idx}", help=f"Probe {t['name']} immediately"):
                        res = collect_icmp_target(t['host'])
                        rtt_v = res.get("data", {}).get("rtt_ms")
                        if rtt_v:
                            st.toast(f"⚡ {t['name']} responded in {rtt_v} ms!", icon="📶")
                        else:
                            st.toast(f"⚠️ {t['name']} probe timed out.", icon="⚠️")
                        st.rerun()
                st.markdown("<div style='height:2px; border-bottom:1px solid rgba(226, 232, 240, 0.4); margin:4px 0;'></div>", unsafe_allow_html=True)

        # Card 2: Active Alerts (WITH INTERACTIVE ACKNOWLEDGE / CLEAR BUTTONS)
        with st.container(border=True):
            alr_h_l, alr_h_r = st.columns([2.3, 1.2])
            with alr_h_l:
                st.html("""
                <div class="card-title-bar" style="margin-bottom:0;">
                    <div class="card-title-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2">
                            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                        </svg>
                        <span class="card-title-text">Active Alerts</span>
                    </div>
                </div>
                """)
            with alr_h_r:
                if st.button("View All →", key="view_all_alerts", help="Open Alerts Page"):
                    st.session_state["current_page"] = "Alerts"
                    st.rerun()

            if anomalies:
                for idx, a in enumerate(anomalies):
                    al_c1, al_c2 = st.columns([3.2, 1.4], gap="small")
                    with al_c1:
                        is_crit = "100%" in a.get("reason", "") or "timeout" in a.get("reason", "").lower()
                        badge_color = "#ef4444" if is_crit else "#f59e0b"
                        st.markdown(f"<span style='color:{badge_color}; font-weight:700;'>●</span> **{a.get('name', 'Host')}**  \n<span style='font-size:0.75rem; color:#64748b;'>{a.get('reason', 'Network anomaly')}</span>", unsafe_allow_html=True)
                    with al_c2:
                        if st.button("✅ Clear", key=f"r_ack_{a.get('id', idx)}", help="Acknowledge & resolve alert"):
                            with get_connection() as conn:
                                conn.execute("DELETE FROM anomalies WHERE id = ?", (a["id"],))
                                conn.commit()
                            st.toast(f"Alert #{a['id']} acknowledged and cleared.", icon="✅")
                            st.rerun()
                    st.markdown("<div style='height:2px; border-bottom:1px solid rgba(226, 232, 240, 0.4); margin:4px 0;'></div>", unsafe_allow_html=True)
            else:
                st.success("✅ Nominal status. 0 active alerts.")
                if st.button("🔍 Run Anomaly Audit", key="r_run_audit_now", use_container_width=True):
                    st.session_state["current_page"] = "Alerts"
                    st.rerun()

        # Card 3: Recent Activity (WITH LINK TO PACKET LOG)
        with st.container(border=True):
            act_h_l, act_h_r = st.columns([2.3, 1.2])
            with act_h_l:
                st.html("""
                <div class="card-title-bar" style="margin-bottom:0;">
                    <div class="card-title-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0e2428" stroke-width="2">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                        </svg>
                        <span class="card-title-text">Recent Activity</span>
                    </div>
                </div>
                """)
            with act_h_r:
                if st.button("View All →", key="view_all_activity", help="Open Measurements Page"):
                    st.session_state["current_page"] = "Measurements"
                    st.rerun()

            st.html(render_recent_activity_rows(recent_measurements))


# ==========================================
# SUPPLEMENTARY VIEWS (When Menu Items Clicked)
# ==========================================

def render_targets_view():
    st.html("<h2 style='color:var(--text-primary);'>🎯 Network Targets Management</h2>")
    st.caption("Inspect, probe, and register network monitoring targets stored in SQLite.")
    
    t_act_col1, t_act_col2 = st.columns([1.2, 2.8])
    with t_act_col1:
        if st.button("⚡ Probe All Targets Now", use_container_width=True):
            with st.spinner("Probing targets in parallel..."):
                res = probe_all_targets()
                st.toast(f"Probed {len(res)} targets successfully!", icon="✅")
                st.rerun()
    with t_act_col2:
        t_search = st.text_input("Filter targets table", placeholder="Type name or host to filter...", label_visibility="collapsed")

    conn = get_connection()
    query = "SELECT target_id, name, host, resolved_ip, lat, lon, enabled, interval, timeout FROM targets"
    if t_search.strip():
        query += f" WHERE name LIKE '%{t_search.strip()}%' OR host LIKE '%{t_search.strip()}%'"
    df = pd.read_sql_query(query, conn._conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)

    # Interactive Target Management Card
    with st.container(border=True):
        st.markdown("#### ⚡ Individual Target Actions")
        targets_list = get_all_targets()
        if targets_list:
            target_names = {f"{t['name']} ({t['host']})": t for t in targets_list}
            selected_label = st.selectbox("Select Target to Test or Manage", list(target_names.keys()))
            sel_target = target_names[selected_label]

            ac_1, ac_2 = st.columns(2)
            with ac_1:
                if st.button(f"⚡ Ping {sel_target['name']} Now", use_container_width=True):
                    with st.spinner(f"Pinging {sel_target['name']}..."):
                        res = collect_icmp_target(sel_target["host"])
                        meas = res.get("data", {})
                        if meas.get("rtt_ms"):
                            st.success(f"✅ Host Responded: **{meas['rtt_ms']} ms** (TTL: {meas.get('ttl', 64)})")
                        else:
                            st.error(f"❌ Probe Failed: {meas.get('error', 'Request timed out')}")
            with ac_2:
                if st.button(f"🗑️ Delete {sel_target['name']}", use_container_width=True):
                    with get_connection() as conn:
                        conn.execute("DELETE FROM targets WHERE target_id = ?", (sel_target["target_id"],))
                        conn.commit()
                    st.toast(f"Target '{sel_target['name']}' removed from database.", icon="🗑️")
                    st.rerun()

    with st.expander("➕ Add New Monitored Target", expanded=False):
        with st.form("new_target_form"):
            t_name = st.text_input("Name (e.g. Quad9 DNS)")
            t_host = st.text_input("Host IP/Domain (e.g. 9.9.9.9)")
            col1, col2 = st.columns(2)
            with col1:
                t_lat = st.number_input("Latitude", value=40.7128)
            with col2:
                t_lon = st.number_input("Longitude", value=-74.0060)
            
            submitted = st.form_submit_button("Add Target to Network Monitor")
            if submitted:
                if t_name and t_host:
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
                    st.toast(f"Added {t_name} successfully!", icon="✅")
                    st.success(f"Target '{t_name}' ({t_host}) registered in monitor database.")
                    st.rerun()
                else:
                    st.error("Please provide both target Name and Host IP.")

def render_measurements_view():
    st.html("<h2 style='color:var(--text-primary);'>📊 Telemetry Measurements Log</h2>")
    st.caption("Raw ICMP / TCP packet-level telemetry records stored in SQLite database.")
    
    m_col1, m_col2, m_col3 = st.columns([1.5, 1.5, 1.0])
    with m_col1:
        proto_filter = st.radio("Protocol Filter", ["All", "ICMP", "TCP"], horizontal=True)
    with m_col2:
        rec_limit = st.selectbox("Display Limit", [50, 100, 200, 500], index=1)
    with m_col3:
        if st.button("🧹 Clear Logs", use_container_width=True, help="Clear historical telemetry records"):
            with get_connection() as conn:
                conn.execute("DELETE FROM measurements")
                conn.commit()
            st.toast("Measurements table cleared.", icon="✅")
            st.rerun()

    conn = get_connection()
    if proto_filter == "All":
        df = pd.read_sql_query(f"SELECT * FROM measurements ORDER BY id DESC LIMIT {rec_limit}", conn._conn)
    else:
        df = pd.read_sql_query(f"SELECT * FROM measurements WHERE protocol = '{proto_filter}' ORDER BY id DESC LIMIT {rec_limit}", conn._conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Measurements to CSV",
        data=csv_data,
        file_name="telemetry_measurements.csv",
        mime="text/csv",
        use_container_width=True
    )

def render_analytics_view():
    st.html("<h2 style='color:var(--text-primary);'>📈 Performance Analytics & Aggregated Windows</h2>")
    st.caption("Rolling statistical windows: Jitter, Availability, P95, and P99 percentiles.")
    
    if st.button("⚡ Recalculate Rolling Statistical Window", use_container_width=True):
        with st.spinner("Computing statistics across telemetry measurements..."):
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT target_id, name, host FROM targets")
                targets = cursor.fetchall()
                for t in targets:
                    tid = t["target_id"]
                    cursor.execute("SELECT rtt_ms, success FROM measurements WHERE target_id = ? ORDER BY id DESC LIMIT 30", (tid,))
                    recs = cursor.fetchall()
                    if recs:
                        total = len(recs)
                        succ = sum(1 for r in recs if r["success"] == 1)
                        rtts = [r["rtt_ms"] for r in recs if r["success"] == 1 and r["rtt_ms"] is not None]
                        st_calc = calculate_rolling_statistics(rtts, total, succ)
                        cursor.execute("""
                        INSERT INTO window_metrics (timestamp, target_id, window_size, mean_rtt_ms, median_rtt_ms, p95_rtt_ms, p99_rtt_ms, jitter_ms, packet_loss_pct, availability_pct)
                        VALUES (datetime('now'), ?, 30, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            tid,
                            st_calc["mean_rtt"],
                            st_calc["median_rtt"],
                            st_calc["p95_rtt"],
                            st_calc["p99_rtt"],
                            st_calc["jitter"],
                            st_calc["packet_loss_pct"],
                            st_calc["availability_pct"]
                        ))
                conn.commit()
            st.toast("Rolling window statistics updated!", icon="✅")
            st.rerun()

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM window_metrics ORDER BY id DESC LIMIT 100", conn._conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)

def render_alerts_view():
    st.html("<h2 style='color:var(--text-primary);'>🔔 Anomaly Detection Timeline</h2>")
    st.caption("Autonomous threshold evaluations and historical network degradation flags.")
    
    al_col1, al_col2 = st.columns([1, 1])
    with al_col1:
        if st.button("🔍 Run Anomaly Audit Scan", use_container_width=True):
            with st.spinner("Auditing recent measurements against thresholds..."):
                detector = AnomalyDetector(
                    rtt_threshold=st.session_state.get("thresh_rtt", 90.0),
                    loss_threshold=st.session_state.get("thresh_loss", 5.0),
                    jitter_threshold=st.session_state.get("thresh_jitter", 20.0)
                )
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT target_id FROM targets")
                    t_ids = [r[0] for r in cursor.fetchall()]
                    found = 0
                    for tid in t_ids:
                        cursor.execute("SELECT rtt_ms, success FROM measurements WHERE target_id = ? ORDER BY id DESC LIMIT 20", (tid,))
                        rows = cursor.fetchall()
                        if rows:
                            tot = len(rows)
                            succ = sum(1 for r in rows if r["success"] == 1)
                            rtts = [r["rtt_ms"] for r in rows if r["success"] == 1 and r["rtt_ms"] is not None]
                            st_calc = calculate_rolling_statistics(rtts, tot, succ)
                            anom = detector.detect(st_calc)
                            if anom:
                                cursor.execute("""
                                INSERT INTO anomalies (target_id, metric, observed_value, baseline, threshold, reason)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """, (str(tid), anom["metric"], anom["observed_value"], anom["baseline"], anom["threshold"], anom["reason"]))
                                found += 1
                    conn.commit()
                st.toast(f"Anomaly audit complete: {found} flagged.", icon="🔔")
                st.rerun()

    with al_col2:
        if st.button("🧹 Clear Anomalies History", use_container_width=True):
            with get_connection() as conn:
                conn.execute("DELETE FROM anomalies")
                conn.commit()
            st.toast("Anomalies cleared successfully!", icon="✅")
            st.rerun()

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM anomalies ORDER BY id DESC LIMIT 50", conn._conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)

def render_reports_view():
    st.html("<h2 style='color:var(--text-primary);'>📄 Network Operations Center (NOC) Executive Report</h2>")
    
    u_info = st.session_state.get("user", {})
    u_name = u_info.get("full_name", "Dhanumithra")
    u_role = u_info.get("role", "NOC Lead / Administrator")
    
    report_text = f"""### NetTelemetry Computer Networks Implementation
- **Operator Authorization:** Authenticated as {u_name} ({u_role}).
- **Active Probing vs Passive Sniffing:** Active ICMP and controlled TCP connection tests measure end-to-end user experience and immediate packet drops rather than passively waiting for third-party traffic.
- **Statistical Jitter:** RFC 3550 style delay variation tracking consecutive RTT delta values:
  $$\\text{{Jitter}} = \\frac{{1}}{{N-1}} \\sum_{{i=1}}^{{N-1}} |\\text{{RTT}}_{{i}} - \\text{{RTT}}_{{i-1}}|$$
- **Latency Percentiles:** P95 and P99 latency percentiles identify path jitter and router bufferbloat that mean RTT averages obscure.
- **Database Architecture:** SQLite in WAL mode with relational targets, telemetry measurements, window metrics, and anomaly events.
"""
    st.markdown(report_text)

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.download_button(
            "📥 Download Executive Report (Markdown)",
            data=report_text,
            file_name="NetTelemetry_Report.md",
            mime="text/markdown",
            use_container_width=True
        )
    with r_col2:
        with get_connection() as conn:
            m_df = pd.read_sql_query("SELECT * FROM measurements ORDER BY id DESC LIMIT 500", conn._conn)
        st.download_button(
            "📥 Download Full Telemetry Dataset (CSV)",
            data=m_df.to_csv(index=False).encode('utf-8'),
            file_name="telemetry_dataset.csv",
            mime="text/csv",
            use_container_width=True
        )

def render_settings_view():
    st.html("<h2 style='color:var(--text-primary);'>⚙️ Telemetry Settings & Thresholds</h2>")
    st.caption("Customize autonomous anomaly detection thresholds and operational parameters.")
    
    rtt_val = st.number_input("RTT Anomaly Spike Threshold (ms)", value=float(st.session_state["thresh_rtt"]))
    loss_val = st.number_input("Packet Loss Warning Threshold (%)", value=float(st.session_state["thresh_loss"]))
    jitter_val = st.number_input("Jitter Threshold (ms)", value=float(st.session_state["thresh_jitter"]))
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("💾 Save Settings", use_container_width=True):
            st.session_state["thresh_rtt"] = rtt_val
            st.session_state["thresh_loss"] = loss_val
            st.session_state["thresh_jitter"] = jitter_val
            st.toast("Settings saved successfully!", icon="✅")
            st.success("✅ Telemetry thresholds updated and persisted in active session state.")
    with col_s2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state["thresh_rtt"] = 90.0
            st.session_state["thresh_loss"] = 5.0
            st.session_state["thresh_jitter"] = 20.0
            st.toast("Reset thresholds to default parameters.", icon="🔄")
            st.rerun()


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
