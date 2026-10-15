import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import sys

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
import database.db
import dashboard.styles
import dashboard.components
import network.target_manager
import network.settings_manager
import telemetry.collector
import telemetry.monitor_service
importlib.reload(database.db)
importlib.reload(dashboard.styles)
importlib.reload(dashboard.components)
importlib.reload(network.target_manager)
importlib.reload(network.settings_manager)
importlib.reload(telemetry.collector)
importlib.reload(telemetry.monitor_service)

from network.settings_manager import (
    DEFAULT_THRESHOLDS,
    validate_thresholds,
    load_thresholds,
    save_thresholds,
    reset_thresholds
)

from database.db import (
    seed_default_data,
    get_all_targets,
    get_target_latest_status,
    get_recent_measurements,
    get_active_anomalies,
    get_connection,
    insert_target,
    add_target_validated,
    target_exists,
    clear_measurements,
    get_measurements_count,
    clear_anomalies,
    get_anomalies_count,
    get_network_performance_summary,
    generate_performance_interpretation,
    authenticate_user,
    create_user,
    get_user_by_username,
    DB_PATH
)
from network.target_manager import validate_hostname_or_ip
from telemetry.monitor_service import (
    get_monitor_service,
    start_monitoring,
    stop_monitoring,
    is_monitoring_running,
    get_monitoring_status
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
    clean_html,
    render_sidebar_brand,
    fetch_analytics_measurements,
    fetch_analytics_window_metrics,
    compute_analytics_summary_kpis,
    create_rtt_timeline_chart,
    create_packet_loss_chart,
    create_availability_chart,
    create_jitter_chart,
    create_p95_p99_comparison_chart,
    fetch_anomaly_records,
    create_anomaly_timeline_chart
)

# 1. Page Configuration
st.set_page_config(
    layout="wide",
    page_title="NetTelemetry",
    page_icon="dashboard/assets/logo.png",
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
qp_page = st.query_params.get("page")
if qp_page and qp_page in ["Dashboard", "Targets", "Measurements", "Analytics", "Alerts", "Reports", "Settings"]:
    st.session_state["current_page"] = qp_page
elif "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"
if "trend_timeframe" not in st.session_state:
    st.session_state["trend_timeframe"] = "1h"
if "map_view" not in st.session_state:
    st.session_state["map_view"] = "World View"
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""
persisted_thresholds = load_thresholds()
if "thresh_rtt" not in st.session_state:
    st.session_state["thresh_rtt"] = persisted_thresholds.get("rtt_ms", 90.0)
if "thresh_loss" not in st.session_state:
    st.session_state["thresh_loss"] = persisted_thresholds.get("loss_pct", 5.0)
if "thresh_jitter" not in st.session_state:
    st.session_state["thresh_jitter"] = persisted_thresholds.get("jitter_ms", 20.0)
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
    # 1. Brand Header
    logo_col, title_col = st.columns([1, 4], vertical_alignment="center")
    with logo_col:
        st.image("dashboard/assets/logo.png", width=38)
    with title_col:
        st.markdown(
            """
            <div style="line-height:1.15; padding-top:2px;">
                <div class="brand-title">NetTelemetry</div>
                <div class="brand-subtitle">Observe • Analyze • Stay Ahead</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.html('<div class="sidebar-divider"></div>')

    # 2. Primary Navigation
    pages = [
        ("Dashboard", "Dashboard"),
        ("Targets", "Targets"),
        ("Measurements", "Measurements"),
        ("Analytics", "Analytics"),
        ("Alerts", "Alerts"),
        ("Reports", "Reports"),
        ("Settings", "Settings"),
    ]

    anomalies_list = get_active_anomalies(limit=10)
    anom_count = len(anomalies_list)
    curr_page = st.session_state.get("current_page", "Dashboard")

    for p_id, p_label in pages:
        is_active = (curr_page == p_id)
        btn_label = p_label
        if p_id == "Alerts" and anom_count > 0:
            btn_label = f"{p_label}  ({anom_count})"
        if st.button(
            btn_label,
            key=f"sidebar_nav_{p_id}",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            if curr_page != p_id:
                st.session_state["current_page"] = p_id
                st.rerun()

    st.html('<div class="sidebar-divider"></div>')

    # 3. Telemetry Engine Section
    pulse_col, te_col = st.columns([1, 8], vertical_alignment="center")
    with pulse_col:
        st.image("dashboard/assets/pulse.png", width=16)
    with te_col:
        st.markdown(
            '<div style="font-size:0.72rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:#94A3B8; line-height:16px;">Telemetry Engine</div>',
            unsafe_allow_html=True
        )

    mon_running = is_monitoring_running()
    mon_status = get_monitoring_status()
    cadence_raw = st.session_state.get("probe_cadence", "5s (Fast)")
    interval_sec = 3 if "3" in cadence_raw else (5 if "5" in cadence_raw else (10 if "10" in cadence_raw else 30))
    
    status_text = "Monitoring Active" if mon_running else "Monitoring Paused"
    cycle_num = mon_status.get("cycle_count", 0)
    sub_status = (
        f"Probing {mon_status.get('interval_sec', interval_sec)}s • Cycle #{cycle_num}"
        if mon_running else "Manual refresh mode"
    )
    dot_class = "status-dot-active" if mon_running else "status-dot-paused"

    st.html(f"""
    <div class="telemetry-live-card">
        <div class="telemetry-dot {dot_class}"></div>
        <div>
            <div class="telemetry-live-title">{status_text}</div>
            <div class="telemetry-live-sub">{sub_status}</div>
        </div>
    </div>
    """)

    # Primary Start & Stop Monitoring Controls
    sb_btn1, sb_btn2 = st.columns(2)
    with sb_btn1:
        if st.button("▶ Start", key="sidebar_start_btn", type="primary" if not mon_running else "secondary", use_container_width=True, help="Start live background telemetry loop"):
            start_monitoring(interval_sec=interval_sec, db_path=DB_PATH)
            st.session_state["auto_probe"] = True
            st.toast("Real-time monitoring started!", icon="🚀")
            st.rerun()
    with sb_btn2:
        if st.button("⏹ Stop", key="sidebar_stop_btn", type="primary" if mon_running else "secondary", use_container_width=True, help="Stop live background telemetry loop safely"):
            stop_monitoring()
            st.session_state["auto_probe"] = False
            st.toast("Real-time monitoring stopped.", icon="⏹️")
            st.rerun()

    cadence_opts = ["3s (Ultra)", "5s (Fast)", "10s (Standard)", "30s (Eco)"]
    cadence_val = st.selectbox(
        "Probe Cadence",
        cadence_opts,
        index=cadence_opts.index(cadence_raw) if cadence_raw in cadence_opts else 1,
        key="sidebar_cadence_select",
        help="Cadence for periodic telemetry probe cycles"
    )
    if cadence_val != cadence_raw:
        st.session_state["probe_cadence"] = cadence_val
        if mon_running:
            new_sec = 3 if "3" in cadence_val else (5 if "5" in cadence_val else (10 if "10" in cadence_val else 30))
            start_monitoring(interval_sec=new_sec, db_path=DB_PATH)
        st.rerun()

    # Quick Probe & Refresh Actions
    if st.button("⚡ Probe All Targets", key="sidebar_probe_all", type="secondary", use_container_width=True, help="Executes live parallel network probes to targets immediately"):
        with st.spinner("Probing targets in parallel..."):
            probe_all_targets()
            st.session_state["last_probe_time"] = datetime.datetime.now().strftime("%I:%M:%S %p")
            st.toast("⚡ Active probes completed successfully!", icon="✅")
            st.rerun()

    if st.button("🔄 Refresh Data", key="sidebar_refresh_data", type="secondary", use_container_width=True, help="Reload fresh metrics from SQLite"):
        st.rerun()

    st.html('<div class="sidebar-divider" style="margin-top: 0.85rem;"></div>')

    # Ambient soundwave graphic & Status pill at bottom
    st.html(clean_html(f"""
    <div class="sidebar-bottom-container">
        <svg viewBox="0 0 260 36" style="width:100%; height:28px; opacity:0.35; margin-bottom:6px;">
            <path d="M0,18 Q30,4 60,18 T120,18 T180,18 T240,18" fill="none" stroke="#10b981" stroke-width="1.5"/>
            <path d="M0,18 Q40,32 80,18 T160,18 T240,18" fill="none" stroke="#06b6d4" stroke-width="1"/>
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
        act_c1, act_c2, act_c3 = st.columns([0.65, 0.95, 2.6], gap="small")
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

    # Permanent Top Navigation Bar (Always visible on all screens)
    nav_tabs = [
        ("Dashboard", "🏠 Dashboard"),
        ("Targets", "🎯 Targets"),
        ("Measurements", "📊 Measurements"),
        ("Analytics", "📈 Analytics"),
        ("Alerts", "🔔 Alerts"),
        ("Reports", "📄 Reports"),
        ("Settings", "⚙️ Settings"),
    ]
    curr_pg = st.session_state.get("current_page", "Dashboard")
    nav_cols = st.columns(len(nav_tabs), gap="small")
    for idx, (p_id, p_label) in enumerate(nav_tabs):
        with nav_cols[idx]:
            is_active = (curr_pg == p_id)
            if st.button(
                p_label,
                key=f"topnav_btn_{p_id}",
                type="primary" if is_active else "secondary",
                use_container_width=True
            ):
                if curr_pg != p_id:
                    st.session_state["current_page"] = p_id
                    st.query_params["page"] = p_id
                    st.rerun()

render_universal_top_navbar()


# ==========================================
# REAL-TIME DASHBOARD VIEW FRAGMENT
# ==========================================
cadence_raw = st.session_state.get("probe_cadence", "5s (Fast)")
interval_sec = 3 if "3" in cadence_raw else (5 if "5" in cadence_raw else (10 if "10" in cadence_raw else 30))
is_running = is_monitoring_running()
frag_interval = f"{interval_sec}s" if is_running else None

@st.fragment(run_every=frag_interval)
def render_dashboard_content():
    is_dark = st.session_state.get("dark_mode", False)
    is_running = is_monitoring_running()
    mon_status = get_monitoring_status()

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
    unknown_count = sum(1 for t in targets if t["status"] == "Unknown")
    
    valid_rtts = [t["rtt_ms"] for t in targets if t.get("rtt_ms") is not None and t["rtt_ms"] > 0]
    avg_rtt = sum(valid_rtts) / len(valid_rtts) if valid_rtts else None
    
    avg_loss = sum(t["loss_pct"] for t in targets) / total_targets if total_targets else 2.4
    avail_pct = 100.0 - avg_loss

    # Dynamic Greeting Banner with live state
    st.html(render_hero_greeting(
        user_name=curr_user_name,
        is_live=is_running,
        interval_sec=interval_sec
    ))

    # Real-Time Telemetry Engine & Dynamic Target Management Panel
    with st.container(border=True):
        col_ctrl, col_dyn = st.columns([1.15, 1.45], gap="medium")
        
        with col_ctrl:
            st.markdown("##### 📡 Real-Time Telemetry Engine")
            if is_running:
                c_num = mon_status.get("cycle_count", 0)
                last_p = mon_status.get("last_probe_time") or "In progress"
                st.markdown(
                    f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:10px;'>"
                    f"<span style='display:inline-block; width:10px; height:10px; border-radius:50%; background:#10b981; box-shadow:0 0 8px #10b981;'></span>"
                    f"<span style='color:#10b981; font-weight:700; font-size:0.9rem;'>MONITORING ACTIVE</span>"
                    f"<span style='color:var(--text-secondary); font-size:0.8rem;'>• Cadence: {mon_status.get('interval_sec', interval_sec)}s • Cycle #{c_num}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.caption(f"Last probe: {last_p}")
            else:
                st.markdown(
                    f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:10px;'>"
                    f"<span style='display:inline-block; width:10px; height:10px; border-radius:50%; background:#94a3b8;'></span>"
                    f"<span style='color:#94a3b8; font-weight:700; font-size:0.9rem;'>MONITORING PAUSED</span>"
                    f"<span style='color:var(--text-secondary); font-size:0.8rem;'>• Autonomous probing stopped</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.caption("Click 'Start Monitoring' to launch live autonomous probing loop.")
            
            btn_c1, btn_c2, btn_c3 = st.columns([1.25, 1.25, 1.3], gap="small")
            with btn_c1:
                if st.button("▶ Start Monitoring", key="ctrl_start_btn", type="primary" if not is_running else "secondary", use_container_width=True):
                    start_monitoring(interval_sec=interval_sec, db_path=DB_PATH)
                    st.session_state["auto_probe"] = True
                    st.toast("Real-time telemetry engine started!", icon="🚀")
                    st.rerun()
            with btn_c2:
                if st.button("⏹ Stop Monitoring", key="ctrl_stop_btn", type="primary" if is_running else "secondary", use_container_width=True):
                    stop_monitoring()
                    st.session_state["auto_probe"] = False
                    st.toast("Real-time telemetry engine safely stopped.", icon="⏹️")
                    st.rerun()
            with btn_c3:
                cad_choices = ["3s (Ultra)", "5s (Fast)", "10s (Standard)", "30s (Eco)"]
                selected_cad = st.selectbox(
                    "Cadence",
                    cad_choices,
                    index=cad_choices.index(cadence_raw) if cadence_raw in cad_choices else 1,
                    key="ctrl_cadence_select",
                    label_visibility="collapsed"
                )
                if selected_cad != cadence_raw:
                    st.session_state["probe_cadence"] = selected_cad
                    if is_running:
                        n_sec = 3 if "3" in selected_cad else (5 if "5" in selected_cad else (10 if "10" in selected_cad else 30))
                        start_monitoring(interval_sec=n_sec, db_path=DB_PATH)
                    st.rerun()

        with col_dyn:
            st.markdown("##### ➕ Dynamic Target Management")
            with st.form("dash_quick_add_target", clear_on_submit=True):
                inp_c1, inp_c2, inp_c3 = st.columns([1.6, 1.4, 1.1], gap="small")
                with inp_c1:
                    target_host = st.text_input("Host or IP", placeholder="e.g. 1.1.1.1 or dns.google", label_visibility="collapsed")
                with inp_c2:
                    target_label = st.text_input("Label (optional)", placeholder="e.g. Cloudflare DNS", label_visibility="collapsed")
                with inp_c3:
                    add_submit = st.form_submit_button("➕ Add & Monitor", type="primary", use_container_width=True)
                
                if add_submit:
                    if not target_host or not target_host.strip():
                        st.error("Please enter a valid hostname or IP address.")
                    else:
                        lbl = target_label.strip() if (target_label and target_label.strip()) else target_host.strip()
                        add_res = add_target_validated(name=lbl, host=target_host.strip(), db_path=DB_PATH)
                        if not add_res.get("success"):
                            if add_res.get("status") == "exists" or add_res.get("is_duplicate"):
                                st.warning(f"⚠️ {add_res.get('message') or add_res.get('error')}")
                            else:
                                st.error(f"❌ {add_res.get('message') or add_res.get('error')}")
                        else:
                            st.toast(f"✅ Added target '{lbl}' ({target_host.strip()})! Testing...", icon="🎯")
                            collect_icmp_target(target_host.strip())
                            if not is_running:
                                start_monitoring(interval_sec=interval_sec, db_path=DB_PATH)
                                st.session_state["auto_probe"] = True
                            st.rerun()

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
        curr_sf = st.session_state.get("status_filter", "All")
        if unknown_count > 0:
            kf_1, kf_2, kf_3, kf_4, kf_5, kf_6 = st.columns([1.1, 1, 1, 1, 1, 1.2])
            with kf_1:
                if st.button(f"🔍 All ({total_targets})", key="kf_all", type="primary" if curr_sf == "All" else "secondary", use_container_width=True):
                    st.session_state["status_filter"] = "All"
                    st.rerun()
            with kf_2:
                if st.button(f"🟢 Online ({online_count})", key="kf_online", type="primary" if curr_sf == "Online" else "secondary", use_container_width=True):
                    st.session_state["status_filter"] = "Online"
                    st.rerun()
            with kf_3:
                if st.button(f"🟡 Degraded ({degraded_count})", key="kf_deg", type="primary" if curr_sf == "Degraded" else "secondary", use_container_width=True):
                    st.session_state["status_filter"] = "Degraded"
                    st.rerun()
            with kf_4:
                if st.button(f"🔴 Offline ({offline_count})", key="kf_off", type="primary" if curr_sf == "Offline" else "secondary", use_container_width=True):
                    st.session_state["status_filter"] = "Offline"
                    st.rerun()
            with kf_5:
                if st.button(f"⚪ Unknown ({unknown_count})", key="kf_unk", type="primary" if curr_sf == "Unknown" else "secondary", use_container_width=True):
                    st.session_state["status_filter"] = "Unknown"
                    st.rerun()
            with kf_6:
                if st.button("⚡ Probe All", key="kf_probe_all", use_container_width=True):
                    with st.spinner("Probing all targets in parallel..."):
                        probe_all_targets()
                        st.toast("⚡ All targets probed successfully!", icon="✅")
                        st.rerun()
        else:
            kf_1, kf_2, kf_3, kf_4, kf_5 = st.columns([1.1, 1, 1, 1, 1.2])
            with kf_1:
                if st.button(f"🔍 All ({total_targets})", key="kf_all", type="primary" if curr_sf == "All" else "secondary", use_container_width=True):
                    st.session_state["status_filter"] = "All"
                    st.rerun()
            with kf_2:
                if st.button(f"🟢 Online ({online_count})", key="kf_online", type="primary" if curr_sf == "Online" else "secondary", use_container_width=True):
                    st.session_state["status_filter"] = "Online"
                    st.rerun()
            with kf_3:
                if st.button(f"🟡 Degraded ({degraded_count})", key="kf_deg", type="primary" if curr_sf == "Degraded" else "secondary", use_container_width=True):
                    st.session_state["status_filter"] = "Degraded"
                    st.rerun()
            with kf_4:
                if st.button(f"🔴 Offline ({offline_count})", key="kf_off", type="primary" if curr_sf == "Offline" else "secondary", use_container_width=True):
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
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
                    "Host": t["host"],
                    "Resolved IP": t.get("resolved_ip") or t["host"],
                    "Status": t["status"],
                    "RTT (ms)": f"{round(t['rtt_ms'], 1)} ms" if t.get('rtt_ms') is not None else "N/A",
                    "Packet Loss": f"{t['loss_pct']:.1f}%",
                    "Availability": f"{t.get('availability_pct', round(100.0 - t['loss_pct'], 1)):.1f}%",
                    "Last Probed": t.get("last_probe_time") or "N/A",
                    "Coordinates": f"({t.get('lat', 0.0):.2f}, {t.get('lon', 0.0):.2f})"
                } for t in filtered_targets])
                st.dataframe(list_df, use_container_width=True, hide_index=True)

            st.html("""
            <div class="map-legend-bar" style="margin-top: -6px; margin-bottom: 4px; padding-left: 6px;">
                <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div><span>Online</span></div>
                <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div><span>Degraded</span></div>
                <div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div><span>Offline</span></div>
                <div class="legend-item"><div class="legend-dot" style="background:#94a3b8;"></div><span>Unknown</span></div>
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
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
                <div style="font-size: 0.75rem; margin-top:-6px; display:flex; flex-direction:column; gap:4px; padding-left:12px;">
                    <div style="display:flex; align-items:center; gap:6px;"><span style="width:7px; height:7px; border-radius:50%; background:#10b981;"></span><span class="meta-subtext">Successful: <b class="stat-highlight">1,217</b></span></div>
                    <div style="display:flex; align-items:center; gap:6px;"><span style="width:7px; height:7px; border-radius:50%; background:#f43f5e;"></span><span class="meta-subtext">Failed: <b class="stat-highlight">29</b></span></div>
                    <div style="display:flex; align-items:center; gap:6px;"><span style="width:7px; height:7px; border-radius:50%; background:#94a3b8;"></span><span class="meta-subtext">Packet Loss: <b class="stat-highlight">2.4%</b></span></div>
                </div>
                """)

        # Bottom Card 3: Top Targets by Latency
        with bg_col3:
            with st.container(border=True):
                st.html("""
                <div class="card-title-bar" style="margin-bottom: 0.75rem;">
                    <div class="card-title-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="20" x2="18" y2="10"></line>
                            <line x1="12" y1="20" x2="12" y2="4"></line>
                            <line x1="6" y1="20" x2="6" y2="14"></line>
                        </svg>
                        <span class="card-title-text" style="font-size:0.875rem;">Top Targets by Latency</span>
                    </div>
                </div>
                """)
                lat_bars = render_latency_progress_bars(targets)
                if lat_bars and lat_bars.strip():
                    st.html(lat_bars)
                else:
                    st.caption("No target latency metrics available.")

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
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
                    if t["status"] == "Online":
                        status_dot = "🟢"
                    elif t["status"] == "Degraded":
                        status_dot = "🟡"
                    elif t["status"] == "Unknown":
                        status_dot = "⚪"
                    else:
                        status_dot = "🔴"
                    st.markdown(f"{status_dot} **{t['name']}**  \n<span class='meta-subtext' style='font-size:0.75rem;'>{t.get('resolved_ip') or t['host']}</span>", unsafe_allow_html=True)
                with tr_c2:
                    rtt_str = f"**{int(round(t['rtt_ms']))} ms**" if t.get('rtt_ms') is not None else "**N/A**"
                    avail_val = t.get('availability_pct', round(100.0 - t.get('loss_pct', 0.0), 1))
                    last_pr = t.get('last_probe_time') or ""
                    time_snip = f" • {last_pr[-8:]}" if isinstance(last_pr, str) and len(last_pr) >= 8 else ""
                    st.markdown(f"{rtt_str}  \n<span class='meta-subtext' style='font-size:0.75rem;'>Loss: {t.get('loss_pct', 0):.0f}% • Avail: {avail_val:.0f}%{time_snip}</span>", unsafe_allow_html=True)
                with tr_c3:
                    if st.button("⚡ Ping", key=f"r_ping_{t['target_id']}_{idx}", help=f"Probe {t['name']} immediately"):
                        res = collect_icmp_target(t['host'])
                        rtt_v = res.get("data", {}).get("rtt_ms")
                        if rtt_v is not None:
                            st.toast(f"⚡ {t['name']} responded in {round(rtt_v, 1)} ms!", icon="📶")
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
                        st.markdown(f"<span style='color:{badge_color}; font-weight:700;'>●</span> **{a.get('name', 'Host')}**  \n<span class='meta-subtext' style='font-size:0.75rem;'>{a.get('reason', 'Network anomaly')}</span>", unsafe_allow_html=True)
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
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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

            act_rows = render_recent_activity_rows(recent_measurements)
            if act_rows and act_rows.strip():
                st.html(act_rows)
            else:
                st.caption("No recent telemetry activity recorded.")


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
                    is_valid_host, err_msg = validate_hostname_or_ip(sel_target.get("host", ""))
                    if not is_valid_host:
                        st.error(f"❌ Cannot ping target: {err_msg}")
                    else:
                        with st.spinner(f"Pinging {sel_target['name']}..."):
                            res = collect_icmp_target(sel_target["host"])
                            meas = res.get("data", {})
                            if meas.get("rtt_ms"):
                                st.success(f"✅ Host Responded: **{meas['rtt_ms']} ms** (TTL: {meas.get('ttl', 64)})")
                            else:
                                err_detail = res.get("error") or meas.get("error", "Request timed out")
                                st.error(f"❌ Probe Failed: {err_detail}")
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
            
            submitted = st.form_submit_button("Add Target to Network Monitor", type="primary")
            if submitted:
                if t_name and t_host:
                    res = add_target_validated(name=t_name.strip(), host=t_host.strip(), lat=t_lat, lon=t_lon, db_path=DB_PATH)
                    if not res.get("success"):
                        if res.get("status") == "exists" or res.get("is_duplicate"):
                            st.warning(f"⚠️ {res.get('message') or res.get('error')}")
                        else:
                            st.error(f"❌ {res.get('message') or res.get('error')}")
                    else:
                        st.toast(f"Added {t_name} successfully!", icon="✅")
                        st.success(f"Target '{t_name}' ({t_host}) registered in monitor database.")
                        collect_icmp_target(t_host.strip())
                        st.rerun()
                else:
                    st.error("Please provide both target Name and Host IP.")

@st.dialog("Clear Measurement Logs?")
def confirm_clear_measurements_dialog():
    st.write(
        "Are you sure you want to clear the measurement logs? "
        "This action may permanently delete recorded telemetry measurements."
    )
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    col_cancel, col_confirm = st.columns(2)
    with col_cancel:
        if st.button("Cancel", key="btn_cancel_clear_logs", use_container_width=True):
            st.rerun()

    with col_confirm:
        is_clearing = st.session_state.get("is_clearing_measurements", False)
        if st.button(
            "Clear Logs",
            key="btn_confirm_clear_logs",
            type="primary",
            use_container_width=True,
            disabled=is_clearing
        ):
            st.session_state["is_clearing_measurements"] = True
            try:
                clear_measurements(DB_PATH)
                st.session_state["meas_clear_success"] = True
                st.rerun()
            except Exception as e:
                st.session_state["meas_clear_error"] = str(e)
                st.rerun()
            finally:
                st.session_state["is_clearing_measurements"] = False


def render_measurements_view():
    st.html("<h2 style='color:var(--text-primary);'>📊 Telemetry Measurements Log</h2>")
    st.caption("Raw ICMP / TCP packet-level telemetry records stored in SQLite database.")
    
    if st.session_state.pop("meas_clear_success", False):
        st.success("✅ Measurement logs cleared successfully.")
        st.toast("Measurements table cleared.", icon="✅")

    err = st.session_state.pop("meas_clear_error", None)
    if err:
        st.error(f"❌ Failed to clear measurement logs: {err}")

    m_col1, m_col2, m_col3 = st.columns([1.5, 1.5, 1.0])
    with m_col1:
        proto_filter = st.radio("Protocol Filter", ["All", "ICMP", "TCP"], horizontal=True)
    with m_col2:
        rec_limit = st.selectbox("Display Limit", [50, 100, 200, 500], index=1)
    with m_col3:
        if st.button("🧹 Clear Logs", key="btn_clear_logs_trigger", use_container_width=True, help="Clear historical telemetry records"):
            confirm_clear_measurements_dialog()

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
    st.caption("Interactive telemetry performance visualizations: RTT timeline, packet loss, SLA availability, jitter, and P95/P99 latency.")
    
    is_dark = st.session_state.get("dark_mode", False)
    all_targets = get_all_targets()

    # --- Control & Filter Bar ---
    with st.container(border=True):
        f_col1, f_col2, f_col3 = st.columns([1.6, 1.2, 1.2], gap="medium")
        with f_col1:
            target_options = {"all": "🌐 All Targets (Combined View)"}
            for t in all_targets:
                target_options[t["target_id"]] = f"{t['name']} ({t['host']})"
            
            selected_target_id = st.selectbox(
                "🎯 Monitored Target",
                options=list(target_options.keys()),
                format_func=lambda k: target_options[k],
                key="analytics_target_select"
            )
        
        with f_col2:
            time_options = {
                "all": "All Recorded",
                "1h": "Last 1 Hour",
                "6h": "Last 6 Hours",
                "24h": "Last 24 Hours",
                "7d": "Last 7 Days"
            }
            time_hours_map = {
                "all": None,
                "1h": 1.0,
                "6h": 6.0,
                "24h": 24.0,
                "7d": 168.0
            }
            selected_time_key = st.selectbox(
                "⏱️ Time Range",
                options=list(time_options.keys()),
                format_func=lambda k: time_options[k],
                key="analytics_time_select"
            )
            time_range_hours = time_hours_map.get(selected_time_key)
        
        with f_col3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            recalc_btn = st.button("⚡ Recalculate Windows", use_container_width=True, help="Compute rolling window metrics from measurements")

    # --- Recalculate Rolling Statistical Window Action ---
    if recalc_btn:
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
                        INSERT INTO window_metrics (target_id, start_time, end_time, loss_pct, availability_pct, jitter_ms, p95_ms, p99_ms, throughput_mbps)
                        VALUES (?, datetime('now', '-2 minutes'), datetime('now'), ?, ?, ?, ?, ?, ?)
                        """, (
                            str(tid),
                            st_calc["loss_pct"],
                            st_calc["availability_pct"],
                            st_calc["jitter_ms"],
                            st_calc["p95_ms"],
                            st_calc["p99_ms"],
                            None
                        ))

                # Global rollup across all measurements
                cursor.execute("SELECT rtt_ms, success FROM measurements ORDER BY id DESC LIMIT 100")
                g_recs = cursor.fetchall()
                if g_recs:
                    g_total = len(g_recs)
                    g_succ = sum(1 for r in g_recs if r["success"] == 1)
                    g_rtts = [r["rtt_ms"] for r in g_recs if r["success"] == 1 and r["rtt_ms"] is not None]
                    g_calc = calculate_rolling_statistics(g_rtts, g_total, g_succ)
                    cursor.execute("""
                    INSERT INTO window_metrics (target_id, start_time, end_time, loss_pct, availability_pct, jitter_ms, p95_ms, p99_ms, throughput_mbps)
                    VALUES ('global', datetime('now', '-2 minutes'), datetime('now'), ?, ?, ?, ?, ?, ?)
                    """, (
                        g_calc["loss_pct"],
                        g_calc["availability_pct"],
                        g_calc["jitter_ms"],
                        g_calc["p95_ms"],
                        g_calc["p99_ms"],
                        None
                    ))
                conn.commit()
            st.toast("Rolling window statistics updated!", icon="✅")
            st.rerun()

    # --- Fetch Real Database Records ---
    meas_df = fetch_analytics_measurements(
        target_id=selected_target_id,
        time_range_hours=time_range_hours
    )
    win_df = fetch_analytics_window_metrics(
        target_id=selected_target_id,
        time_range_hours=time_range_hours
    )
    kpis = compute_analytics_summary_kpis(meas_df, win_df)

    # --- Compact Metric Summary Cards ---
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)
    with kpi_c1:
        rtt_display = f"{kpis['avg_rtt']} ms" if kpis['avg_rtt'] is not None else "N/A"
        st.metric("Avg RTT Latency", rtt_display, help="Mean round-trip time across successful probes")
    with kpi_c2:
        loss_val = kpis['loss_pct'] if kpis['loss_pct'] is not None else 0.0
        st.metric("Packet Loss", f"{loss_val:.1f}%", help="Percentage of dropped or timed-out probes")
    with kpi_c3:
        avail_val = kpis['availability_pct'] if kpis['availability_pct'] is not None else 100.0
        st.metric("Availability", f"{avail_val:.1f}%", help="Successful probe percentage (SLA)")
    with kpi_c4:
        jitter_val = kpis['jitter_ms'] if kpis['jitter_ms'] is not None else 0.0
        st.metric("Jitter (Delay Var.)", f"{jitter_val:.2f} ms", help="RFC 3550 transit delay variation")
    with kpi_c5:
        p95_val = f"{kpis['p95_ms']} ms" if kpis['p95_ms'] is not None else "N/A"
        p99_val = f"{kpis['p99_ms']} ms" if kpis['p99_ms'] is not None else "N/A"
        st.metric("P95 / P99 Latency", f"{p95_val} / {p99_val}", help="Tail latencies identifying bufferbloat")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # --- 1. RTT / Latency Over Time (Full-Width Featured Chart) ---
    with st.container(border=True):
        st.markdown("##### 📡 RTT / Latency Over Time (Raw Measurements)")
        st.caption("Actual timestamped probe latency from the database. Failed probes are excluded from the latency curve.")
        target_display_name = target_options.get(selected_target_id)
        rtt_fig = create_rtt_timeline_chart(meas_df, is_dark=is_dark, target_name=target_display_name)
        st.plotly_chart(rtt_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    # --- 2 & 3. Reliability Metrics (Packet Loss & SLA Availability) ---
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        with st.container(border=True):
            st.markdown("##### 📉 Packet Loss (%) Over Time")
            st.caption("Rolling-window packet drop percentage (window_metrics).")
            loss_fig = create_packet_loss_chart(win_df, is_dark=is_dark)
            st.plotly_chart(loss_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    
    with r2_c2:
        with st.container(border=True):
            st.markdown("##### 🛡️ Availability (%) Over Time")
            st.caption("Rolling-window uptime availability percentage with 99% SLA benchmark.")
            avail_fig = create_availability_chart(win_df, is_dark=is_dark)
            st.plotly_chart(avail_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    # --- 4 & 5. Stability & Percentiles (Jitter & P95 vs P99 Latency) ---
    r3_c1, r3_c2 = st.columns(2)
    with r3_c1:
        with st.container(border=True):
            st.markdown("##### ⚡ Statistical Jitter Over Time")
            st.caption("RFC 3550 delay variation across successive telemetry probes.")
            jitter_fig = create_jitter_chart(win_df, is_dark=is_dark)
            st.plotly_chart(jitter_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    with r3_c2:
        with st.container(border=True):
            st.markdown("##### 📊 P95 vs P99 Latency Comparison")
            st.caption("Comparison of 95th and 99th percentile latency metrics across windows.")
            p95_p99_fig = create_p95_p99_comparison_chart(win_df, is_dark=is_dark)
            st.plotly_chart(p95_p99_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    # --- Historical Rolling Statistics Table ---
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 📋 Historical Rolling Statistical Windows (SQLite Dataset)")
    st.caption("Inspecting records from the window_metrics table for historical audits.")
    
    conn = get_connection()
    if selected_target_id != "all":
        df_table = pd.read_sql_query(
            "SELECT * FROM window_metrics WHERE (target_id = ? OR target_id = ?) ORDER BY id DESC LIMIT 100",
            conn._conn,
            params=(str(selected_target_id), selected_target_id)
        )
    else:
        df_table = pd.read_sql_query("SELECT * FROM window_metrics ORDER BY id DESC LIMIT 100", conn._conn)
    conn.close()
    
    st.dataframe(df_table, use_container_width=True)

@st.dialog("Clear Anomalies History?")
def confirm_clear_anomalies_dialog():
    st.write(
        "Are you sure you want to clear the recorded anomaly history? "
        "This operation may permanently delete historical anomaly records and cannot be undone."
    )
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    col_cancel, col_confirm = st.columns(2)
    with col_cancel:
        if st.button("Cancel", key="btn_cancel_clear_anomalies", use_container_width=True):
            st.rerun()

    with col_confirm:
        is_clearing = st.session_state.get("is_clearing_anomalies", False)
        if st.button(
            "Clear History",
            key="btn_confirm_clear_anomalies",
            type="primary",
            use_container_width=True,
            disabled=is_clearing
        ):
            if not st.session_state.get("is_clearing_anomalies", False):
                st.session_state["is_clearing_anomalies"] = True
                try:
                    clear_anomalies(DB_PATH)
                    st.session_state["anom_clear_success"] = True
                    st.rerun()
                except Exception as e:
                    st.session_state["anom_clear_error"] = str(e)
                    st.rerun()
                finally:
                    st.session_state["is_clearing_anomalies"] = False

def render_alerts_view():
    st.html("<h2 style='color:var(--text-primary);'>🔔 Anomaly Detection Timeline</h2>")
    st.caption("Autonomous threshold evaluations and historical network degradation flags.")
    
    if st.session_state.pop("anom_clear_success", False):
        st.success("✅ Anomaly history cleared successfully.")
        st.toast("Anomalies cleared successfully!", icon="✅")

    err = st.session_state.pop("anom_clear_error", None)
    if err:
        st.error(f"❌ Failed to clear anomaly history: {err}")

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
        if st.button("🧹 Clear Anomalies History", key="btn_clear_anomalies_trigger", use_container_width=True):
            confirm_clear_anomalies_dialog()

    # Fetch real anomaly records joined with target metadata
    df_all = fetch_anomaly_records(db_path=DB_PATH)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if df_all.empty:
        st.info("ℹ️ No historical anomaly records detected in database. Network telemetry is currently nominal.")
        df_filtered = df_all
    else:
        # Build dynamic filter choices based on actual records
        distinct_targets = sorted(df_all["target_name"].dropna().unique().tolist())
        target_display_options = ["All Targets"] + distinct_targets

        distinct_metrics = sorted(df_all["metric"].dropna().unique().tolist())
        metric_meta = {
            "loss_pct": "Packet Loss (loss_pct)",
            "p95_ms": "P95 Latency (p95_ms)",
            "jitter_ms": "Jitter (jitter_ms)",
            "timeout": "Probe Timeout (timeout)",
            "rtt": "RTT Latency (rtt)"
        }
        metric_label_map = {m: metric_meta.get(m, m) for m in distinct_metrics}
        metric_display_options = ["All Metrics"] + [metric_label_map[m] for m in distinct_metrics]

        f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 1.2])
        with f_col1:
            sel_target = st.selectbox("🎯 Target Filter", target_display_options, key="alert_target_filter")
        with f_col2:
            sel_metric_label = st.selectbox("📊 Metric Filter", metric_display_options, key="alert_metric_filter")
        with f_col3:
            view_mode_choice = st.radio("📐 Y-Axis View", ["Observed Value", "Target Swimlane"], horizontal=True, key="alert_view_mode")

        label_to_metric = {v: k for k, v in metric_label_map.items()}
        sel_metric_key = label_to_metric.get(sel_metric_label, "All Metrics")

        # Apply Filters Consistently to Both Visualization and Table
        df_filtered = df_all.copy()
        if sel_target != "All Targets":
            df_filtered = df_filtered[df_filtered["target_name"] == sel_target].copy()
        if sel_metric_key != "All Metrics":
            df_filtered = df_filtered[df_filtered["metric"] == sel_metric_key].copy()

        # Summary KPIs for Filtered Dataset
        k_c1, k_c2, k_c3, k_c4 = st.columns(4)
        with k_c1:
            st.metric("Total Anomalies", len(df_filtered), help="Number of anomaly events matching active filters")
        with k_c2:
            aff_targets = df_filtered["target_name"].nunique() if not df_filtered.empty else 0
            st.metric("Affected Targets", aff_targets, help="Distinct network targets triggering threshold violations")
        with k_c3:
            prim_metric = df_filtered["metric"].mode()[0] if (not df_filtered.empty and not df_filtered["metric"].empty) else "None"
            st.metric("Primary Metric", metric_meta.get(prim_metric, prim_metric), help="Most frequently violated threshold metric")
        with k_c4:
            latest_ts = df_filtered["timestamp"].iloc[-1] if not df_filtered.empty else "None"
            latest_str = str(latest_ts)[-8:] if latest_ts != "None" else "None"
            st.metric("Latest Event", latest_str, help="Timestamp of the most recent anomaly event")

        # Interactive Anomaly Timeline Visualization
        with st.container(border=True):
            st.markdown("##### 📈 Interactive Anomaly Event Timeline")
            st.caption("Chronological distribution of threshold breaches. Hover over events for deep diagnostic telemetry.")
            v_mode = "swimlane" if view_mode_choice == "Target Swimlane" else "magnitude"
            fig = create_anomaly_timeline_chart(
                df_filtered, 
                is_dark=st.session_state.get("dark_mode", False),
                view_mode=v_mode
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "responsive": True})

    # Historical Anomaly Table Section
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 📋 Historical Anomaly Records Log")
    st.caption("Inspecting raw anomaly audit records stored in SQLite database.")

    # Prepare Display Table
    if not df_filtered.empty:
        display_cols = ["id", "timestamp", "target_name", "target_host", "metric", "observed_value", "threshold", "reason"]
        available_cols = [c for c in display_cols if c in df_filtered.columns]
        table_df = df_filtered[available_cols].sort_values(by="id", ascending=False).reset_index(drop=True)
    else:
        table_df = pd.DataFrame(columns=["id", "timestamp", "target_name", "target_host", "metric", "observed_value", "threshold", "reason"])

    st.dataframe(table_df, use_container_width=True)

def render_reports_view():
    st.html("<h2 style='color:var(--text-primary);'>📄 Network Operations Center (NOC) Executive Report</h2>")
    
    u_info = st.session_state.get("user", {})
    u_name = u_info.get("full_name", "Dhanumithra")
    u_role = u_info.get("role", "NOC Lead / Administrator")

    # Fetch live performance summary from SQLite
    summary = get_network_performance_summary(DB_PATH)
    rtt_display = f"{summary['avg_rtt_ms']:.1f} ms" if summary["avg_rtt_ms"] is not None else "N/A"
    loss_display = f"{summary['packet_loss_pct']:.1f}%" if summary["packet_loss_pct"] is not None else "N/A"
    avail_display = f"{summary['availability_pct']:.1f}%" if summary["availability_pct"] is not None else "N/A"
    reporting_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    interpretation = generate_performance_interpretation(summary)

    st.markdown("#### 📊 Live Network Performance Summary")
    st.caption("Real-time telemetry indicators aggregated from current SQLite database records.")

    # Compact summary cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Registered Targets", summary["num_targets"], help="Configured network endpoints")
    with c2:
        st.metric("Recorded Measurements", summary["total_measurements"], help="Total probe measurement records in SQLite")
    with c3:
        st.metric("Successful Probes", summary["successful_probes"], help="Count of successful probe acknowledgements")
    with c4:
        st.metric("Recorded Anomalies", summary["num_anomalies"], help="Total anomaly threshold breaches logged")

    c5, c6, c7 = st.columns(3)
    with c5:
        st.metric("Average RTT", rtt_display, help="Mean round-trip latency across valid successful probes")
    with c6:
        st.metric("Packet Loss", loss_display, help="Percentage of failed probes out of total probes (failed / total * 100)")
    with c7:
        st.metric("Availability", avail_display, help="Percentage of successful probes out of total probes (successful / total * 100)")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

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
        with get_connection(DB_PATH) as conn:
            conn_obj = getattr(conn, "_conn", conn)
            m_df = pd.read_sql_query("SELECT * FROM measurements ORDER BY id DESC LIMIT 500", conn_obj)
        st.download_button(
            "📥 Download Full Telemetry Dataset (CSV)",
            data=m_df.to_csv(index=False).encode('utf-8'),
            file_name="telemetry_dataset.csv",
            mime="text/csv",
            use_container_width=True
        )

@st.dialog("Reset Thresholds to Defaults?")
def confirm_reset_thresholds_dialog():
    st.write(
        "Are you sure you want to reset all telemetry thresholds to default values? "
        "This will restore the factory default parameters (RTT: 90.0 ms, Packet Loss: 5.0%, Jitter: 20.0 ms)."
    )
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    col_cancel, col_confirm = st.columns(2)
    with col_cancel:
        if st.button("Cancel", key="btn_cancel_reset_thresholds", use_container_width=True):
            st.session_state["show_reset_dialog"] = False
            st.rerun()

    with col_confirm:
        if st.button("Reset", key="btn_confirm_reset_thresholds", type="primary", use_container_width=True):
            st.session_state["show_reset_dialog"] = False
            success, msg = reset_thresholds()
            if success:
                st.session_state["thresh_rtt"] = DEFAULT_THRESHOLDS["rtt_ms"]
                st.session_state["thresh_loss"] = DEFAULT_THRESHOLDS["loss_pct"]
                st.session_state["thresh_jitter"] = DEFAULT_THRESHOLDS["jitter_ms"]
                st.session_state["settings_reset_success"] = True
                st.rerun()
            else:
                st.session_state["settings_reset_error"] = msg
                st.rerun()

def render_settings_view():
    st.html("<h2 style='color:var(--text-primary);'>⚙️ Telemetry Settings & Thresholds</h2>")
    st.caption("Customize autonomous anomaly detection thresholds and operational parameters.")
    
    if st.session_state.get("show_reset_dialog", False):
        confirm_reset_thresholds_dialog()

    if st.session_state.pop("settings_reset_success", False):
        st.success("✅ Telemetry thresholds successfully reset to default parameters.")
        st.toast("Thresholds reset to defaults!", icon="🔄")

    err = st.session_state.pop("settings_reset_error", None)
    if err:
        st.error(f"❌ Failed to reset thresholds: {err}")

    rtt_val = st.number_input(
        "RTT Anomaly Spike Threshold (ms)",
        value=float(st.session_state["thresh_rtt"]),
        help="Mean/P95 latency spike threshold in milliseconds (must be > 0 ms)"
    )
    loss_val = st.number_input(
        "Packet Loss Warning Threshold (%)",
        value=float(st.session_state["thresh_loss"]),
        help="Packet loss warning threshold percentage (must be between 0% and 100%)"
    )
    jitter_val = st.number_input(
        "Jitter Threshold (ms)",
        value=float(st.session_state["thresh_jitter"]),
        help="RFC 3550 delay variation jitter threshold in milliseconds (must be >= 0 ms)"
    )
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("💾 Save Settings", key="btn_save_settings", use_container_width=True):
            is_valid, validation_errors = validate_thresholds(rtt_val, loss_val, jitter_val)
            if not is_valid:
                for verr in validation_errors:
                    st.error(f"⚠️ Validation Error: {verr}")
                st.toast("Invalid settings. Please correct the errors.", icon="⚠️")
            else:
                success, msg = save_thresholds({
                    "rtt_ms": rtt_val,
                    "loss_pct": loss_val,
                    "jitter_ms": jitter_val
                })
                if success:
                    st.session_state["thresh_rtt"] = float(rtt_val)
                    st.session_state["thresh_loss"] = float(loss_val)
                    st.session_state["thresh_jitter"] = float(jitter_val)
                    st.toast("Settings saved successfully!", icon="✅")
                    st.success("✅ Telemetry thresholds updated and persisted successfully.")
                else:
                    st.error(f"❌ Failed to persist settings: {msg}")
    with col_s2:
        if st.button("🔄 Reset to Defaults", key="btn_reset_thresholds_trigger", use_container_width=True):
            st.session_state["show_reset_dialog"] = True
            confirm_reset_thresholds_dialog()


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
