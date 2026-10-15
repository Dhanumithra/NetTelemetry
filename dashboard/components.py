"""
UI Components and Visual Visualizations for NetTelemetry Dashboard.
Provides high-fidelity renders matching the NOC mockup image_1.png.
"""

import plotly.graph_objects as go
import pandas as pd
import datetime
from typing import List, Dict, Any, Optional

import base64
from database.db import DEFAULT_DB_PATH

SVG_NET_LOGO = """
<svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="36" height="36" rx="9" fill="#0D2E32" stroke="#14B8A6" stroke-width="1.5"/>
  <line x1="5" y1="18" x2="31" y2="18" stroke="#134E4A" stroke-width="1.2" stroke-dasharray="2 2"/>
  <polyline points="6,18 10,18 14,9 18.5,27 23,12 26.5,18 30,18" fill="none" stroke="#2DD4BF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="14" cy="9" r="2.4" fill="#14B8A6" stroke="#0B1F24" stroke-width="1.4"/>
  <circle cx="18.5" cy="27" r="2.4" fill="#10B981" stroke="#0B1F24" stroke-width="1.4"/>
  <circle cx="23" cy="12" r="2" fill="#34D399" stroke="#0B1F24" stroke-width="1.2"/>
</svg>
"""

def render_sidebar_brand() -> str:
    return """
    <div class="sidebar-brand-container">
        <div class="brand-logo-symbol">&nbsp;</div>
        <div class="brand-text-block">
            <div class="brand-title">NetTelemetry</div>
            <div class="brand-subtitle">Observe • Analyze • Stay Ahead</div>
        </div>
    </div>
    """

SVG_GOOGLE = """
<svg width="18" height="18" viewBox="0 0 24 24">
  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
</svg>
"""

SVG_CLOUDFLARE = """
<svg width="18" height="18" viewBox="0 0 24 24" fill="#F38020">
  <path d="M18.5 10c-.3 0-.5.1-.8.1C17.1 7.6 14.8 6 12 6c-3.2 0-5.8 2.2-6.4 5.2-.2 0-.4-.1-.6-.1-2.2 0-4 1.8-4 4s1.8 4 4 4h13.5c1.9 0 3.5-1.6 3.5-3.5s-1.6-3.6-3.5-3.6z"/>
</svg>
"""

SVG_GITHUB = """
<svg width="18" height="18" viewBox="0 0 24 24" fill="#24292F">
  <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
</svg>
"""

SVG_AMAZON = """
<svg width="18" height="18" viewBox="0 0 24 24" fill="#FF9900">
  <path d="M13.9 12.4c-1.3 0-2.3.3-2.3 1.5 0 1 .7 1.4 1.7 1.4 1 0 1.7-.6 2.1-1.2v-1.7h-1.5zm3.6 4.4h-1.8v-.8c-.7.6-1.6 1-2.7 1-2 0-3.3-1.3-3.3-3.2 0-2.5 1.9-3.4 4.3-3.4h1.7v-.5c0-1-.6-1.5-1.8-1.5-1 0-1.7.3-2.3.8l-.9-1.4c.9-.7 2.1-1.1 3.6-1.1 2.3 0 3.4 1.2 3.4 3.4v6.7zM20.9 19.5c-4.2 2.7-10.4 3.5-15.6 1-.3-.1-.3-.6 0-.8 5-2.6 11.2-1.9 15.2.4.4.2.4.4.4.4z"/>
</svg>
"""

SVG_MICROSOFT = """
<svg width="18" height="18" viewBox="0 0 24 24">
  <path fill="#F25022" d="M1 1h10v10H1z"/>
  <path fill="#7FBA00" d="M13 1h10v10H13z"/>
  <path fill="#00A4EF" d="M1 13h10v10H1z"/>
  <path fill="#FFB900" d="M13 13h10v10H13z"/>
</svg>
"""

def get_brand_icon(name: str) -> str:
    n = name.lower()
    if "google" in n:
        return SVG_GOOGLE
    elif "cloudflare" in n:
        return SVG_CLOUDFLARE
    elif "github" in n:
        return SVG_GITHUB
    elif "amazon" in n or "aws" in n:
        return SVG_AMAZON
    elif "microsoft" in n or "azure" in n:
        return SVG_MICROSOFT
    return SVG_NET_LOGO

# --- Top Header & Greeting ---

def render_top_header_actions() -> str:
    html = """
    <div class="top-header-actions-bar">
        <div class="top-action-btn" title="Light / Dark mode">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
        </div>
        <div class="top-action-btn" title="Alerts & Notifications">
            <span class="notification-dot"></span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
        </div>
        <div class="user-profile-capsule">
            <div class="user-avatar-circle">DM</div>
            <span class="user-name-text">Dhanumithra</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.5">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        </div>
    </div>
    """
    return clean_html(html)

def render_hero_greeting(user_name: str = "Dhanumithra", is_live: bool = False, interval_sec: int = 5) -> str:
    now = datetime.datetime.now()
    formatted_date = now.strftime("%a, %b %d, %Y")
    formatted_time = now.strftime("%I:%M:%S %p")
    hour = now.hour
    greeting_prefix = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")

    live_badge = (
        f'<span class="live-badge-pill" style="background:#ecfdf5; color:#059669; border:1px solid rgba(16,185,129,0.3);">'
        f'● Live Probing ({interval_sec}s)</span>'
        if is_live else
        '<span class="live-badge-pill" style="background:#f1f5f9; color:#64748b;">⏸️ Monitoring Paused</span>'
    )

    html = f"""
    <div class="hero-greeting-container" style="margin-top: 0.5rem; margin-bottom: 1.25rem;">
        <div>
            <div class="hero-subtitle-tag">NETWORK TELEMETRY OPERATION CENTER</div>
            <div class="hero-main-title">{greeting_prefix}, {user_name}!</div>
            <div class="hero-subtext">Real-time network telemetry, anomaly inspection, and packet latency tracking.</div>
        </div>
        <div class="hero-meta-badge">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span style="font-size:0.775rem; color:#475569; font-weight:500;">{formatted_date}</span>
            <span style="font-size:0.775rem; color:#64748b; font-weight:600;">{formatted_time}</span>
            {live_badge}
        </div>
    </div>
    """
    return clean_html(html)

def render_top_header(search_val: str = "") -> str:
    return render_top_header_actions() + render_hero_greeting()

# --- Sparkline SVG Generator ---

def generate_sparkline_svg(color: str, points: List[float], fill: bool = True) -> str:
    """Generates an inline SVG sparkline curve with smooth bezier interpolation."""
    if not points or len(points) < 2:
        points = [10, 15, 12, 18, 14, 20, 19, 25]
    
    min_val = min(points)
    max_val = max(points)
    span = max_val - min_val if max_val != min_val else 1.0
    
    width = 180
    height = 28
    
    coords = []
    for i, p in enumerate(points):
        x = (i / (len(points) - 1)) * width
        y = height - ((p - min_val) / span) * (height - 6) - 3
        coords.append((x, y))
    
    # Path string
    path_d = f"M {coords[0][0]:.1f} {coords[0][1]:.1f}"
    for i in range(1, len(coords)):
        cx = (coords[i-1][0] + coords[i][0]) / 2
        path_d += f" Q {coords[i-1][0]:.1f} {coords[i-1][1]:.1f}, {cx:.1f} {(coords[i-1][1] + coords[i][1])/2:.1f}"
    path_d += f" T {coords[-1][0]:.1f} {coords[-1][1]:.1f}"
    
    fill_d = f"{path_d} L {coords[-1][0]:.1f} {height} L {coords[0][0]:.1f} {height} Z"
    
    fill_tag = f'<path d="{fill_d}" fill="{color}" fill-opacity="0.12" />' if fill else ""
    return f"""
    <svg class="sparkline-svg" viewBox="0 0 {width} {height}" preserveAspectRatio="none">
        {fill_tag}
        <path d="{path_d}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """

# --- 4 KPI Cards ---

def render_kpi_card_1(total_targets: int = 5, online: int = 2, offline: int = 0) -> str:
    spark = generate_sparkline_svg("#10b981", [10, 12, 11, 14, 13, 16, 15, 18, 16, 20])
    html = f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-icon-title">
                <div class="kpi-icon-circle kpi-icon-green">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <circle cx="12" cy="12" r="10"></circle>
                        <circle cx="12" cy="12" r="6"></circle>
                        <circle cx="12" cy="12" r="2"></circle>
                    </svg>
                </div>
                <span class="kpi-title">Total Targets</span>
            </div>
            <span class="live-badge-pill" style="font-size:0.65rem; padding:2px 6px;">Live</span>
        </div>
        <div class="kpi-value">{total_targets}</div>
        <div class="kpi-subtext kpi-subtext-green">
            <span>↑</span> {online} online • {offline} offline
        </div>
        {spark}
    </div>
    """
    return clean_html(html)

def render_kpi_card_2(avg_rtt: Optional[float] = 32.0, change_pct: float = -18.0) -> str:
    spark = generate_sparkline_svg("#3b82f6", [38, 35, 36, 34, 35, 33, 31, 32])
    val_str = f"{int(round(avg_rtt))} ms" if avg_rtt is not None else "N/A"
    html = f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-icon-title">
                <div class="kpi-icon-circle kpi-icon-blue">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                </div>
                <span class="kpi-title">Avg. RTT</span>
            </div>
            <span class="live-badge-pill" style="font-size:0.65rem; padding:2px 6px; background:#eff6ff; color:#2563eb;">RTT</span>
        </div>
        <div class="kpi-value">{val_str}</div>
        <div class="kpi-subtext kpi-subtext-blue">
            <span>↓</span> {abs(int(change_pct))}% (vs. last hour)
        </div>
        {spark}
    </div>
    """
    return clean_html(html)

def render_kpi_card_3(loss_pct: float = 2.4, change_pct: float = -6.0) -> str:
    spark = generate_sparkline_svg("#f59e0b", [4.0, 3.8, 3.2, 3.5, 2.9, 2.7, 2.4])
    html = f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-icon-title">
                <div class="kpi-icon-circle kpi-icon-amber">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                </div>
                <span class="kpi-title">Packet Loss</span>
            </div>
            <span class="live-badge-pill" style="font-size:0.65rem; padding:2px 6px; background:#fef3c7; color:#d97706;">Loss</span>
        </div>
        <div class="kpi-value">{loss_pct:.1f}%</div>
        <div class="kpi-subtext kpi-subtext-amber">
            <span>↓</span> {abs(int(change_pct))}% (vs. last hour)
        </div>
        {spark}
    </div>
    """
    return clean_html(html)

def render_kpi_card_4(avail_pct: float = 97.6, change_pct: float = 2.1) -> str:
    spark = generate_sparkline_svg("#8b5cf6", [95.0, 95.8, 96.2, 96.5, 97.1, 97.6])
    html = f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-icon-title">
                <div class="kpi-icon-circle kpi-icon-purple">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    </svg>
                </div>
                <span class="kpi-title">Availability</span>
            </div>
            <span class="live-badge-pill" style="font-size:0.65rem; padding:2px 6px; background:#f5f3ff; color:#7c3aed;">SLA</span>
        </div>
        <div class="kpi-value">{avail_pct:.1f}%</div>
        <div class="kpi-subtext kpi-subtext-purple">
            <span>↑</span> {change_pct:.1f}% (vs. last hour)
        </div>
        {spark}
    </div>
    """
    return clean_html(html)

# --- Network Topology Map ---

def create_topology_map_figure(targets: List[Dict[str, Any]], view_mode: str = "World View", is_dark: bool = False) -> go.Figure:
    fig = go.Figure()

    # Predefined node coordinates
    coord_map = {
        "google": {"lat": 37.4220, "lon": -122.0841, "name": "Google", "ip": "8.8.8.8"},
        "cloudflare": {"lat": 51.5074, "lon": -0.1278, "name": "Cloudflare", "ip": "1.1.1.1"},
        "github": {"lat": 38.9586, "lon": -77.3570, "name": "GitHub", "ip": "140.82.121.3"},
        "amazon": {"lat": 19.0760, "lon": 72.8777, "name": "Amazon", "ip": "52.94.126.1"},
        "microsoft": {"lat": 35.6762, "lon": 139.6503, "name": "Microsoft", "ip": "20.190.164.4"},
    }

    # Interconnecting Great Circle telemetry links matching mockup
    connections = [
        ("google", "github"),
        ("github", "cloudflare"),
        ("google", "cloudflare"),
        ("cloudflare", "amazon"),
        ("cloudflare", "microsoft"),
        ("amazon", "microsoft"),
    ]

    for src_id, dst_id in connections:
        if src_id in coord_map and dst_id in coord_map:
            src = coord_map[src_id]
            dst = coord_map[dst_id]
            fig.add_trace(go.Scattergeo(
                lon=[src["lon"], dst["lon"]],
                lat=[src["lat"], dst["lat"]],
                mode="lines",
                line=dict(width=1.6, color="rgba(16, 185, 129, 0.45)"),
                hoverinfo="none",
                showlegend=False
            ))

    # Add Target Nodes with custom status pins
    for t in targets:
        tid = str(t.get("target_id", "")).lower()
        tname = str(t.get("name", "")).lower()
        coords = coord_map.get(tid) or coord_map.get(tname)
        if not coords:
            for k in coord_map:
                if k in tname or k in str(t.get("host", "")):
                    coords = coord_map[k]
                    break
        if not coords:
            coords = {
                "lat": float(t.get("lat") or 0.0),
                "lon": float(t.get("lon") or 0.0),
                "name": t.get("name", "Target"),
                "ip": t.get("host", "")
            }

        status = t.get("status", "Online")
        if status == "Online":
            color = "#10b981"
        elif status == "Degraded":
            color = "#f59e0b"
        elif status == "Unknown":
            color = "#94a3b8"
        else:
            color = "#ef4444"
        text_color = "#f8fafc" if is_dark else "#1e293b"

        rtt_val = t.get("rtt_ms")
        rtt_str = f"{round(rtt_val, 1)} ms" if rtt_val is not None else "N/A"

        # Pin marker
        fig.add_trace(go.Scattergeo(
            lon=[coords["lon"]],
            lat=[coords["lat"]],
            mode="markers+text",
            marker=dict(
                size=12,
                color=color,
                line=dict(width=2, color="#ffffff")
            ),
            text=[f"  <b>{coords['name']}</b><br>  {coords['ip']}"],
            textposition="top right",
            textfont=dict(family="Inter, sans-serif", size=10, color=text_color),
            hoverinfo="text",
            hovertext=f"<b>{coords['name']}</b> ({coords['ip']})<br>Status: {status}<br>RTT: {rtt_str}<br>Loss: {t.get('loss_pct', 0)}%",
            showlegend=False
        ))

    # Adaptive theme and projection
    proj_type = "conic conformal" if view_mode == "Region" else "natural earth"
    land_c = "#1e293b" if is_dark else "#dbe4ed"
    ocean_c = "#0f172a" if is_dark else "#f8fafc"
    country_c = "#334155" if is_dark else "#cbd5e1"
    bg_c = "#111827" if is_dark else "#ffffff"

    fig.update_geos(
        projection_type=proj_type,
        showland=True,
        landcolor=land_c,
        showocean=True,
        oceancolor=ocean_c,
        showcountries=True,
        countrycolor=country_c,
        countrywidth=0.6,
        showcoastlines=True,
        coastlinecolor=country_c,
        showframe=False,
        bgcolor=bg_c
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=320,
        paper_bgcolor=bg_c,
        plot_bgcolor=bg_c,
        dragmode=False,
        uirevision="topology_map"
    )

    return fig

# --- Bottom Grid: Performance Trends Multi-Line Chart ---

def create_performance_trends_figure(df: Optional[pd.DataFrame] = None, timeframe: str = "1h", is_dark: bool = False) -> go.Figure:
    fig = go.Figure()

    if df is None or df.empty:
        if timeframe == "6h":
            timestamps = ["06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00"]
            rtt_vals = [28, 29, 34, 45, 52, 48, 36, 32, 30, 33, 35, 34, 31]
            loss_vals = [1, 1, 2, 6, 8, 5, 2, 1, 1, 2, 2, 1, 1]
            jitter_vals = [3, 4, 6, 12, 15, 9, 5, 4, 3, 5, 4, 3, 3]
            tput_vals = [40, 42, 55, 60, 68, 75, 82, 90, 85, 78, 88, 95, 70]
        elif timeframe == "24h":
            timestamps = ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00", "24:00"]
            rtt_vals = [25, 24, 24, 26, 38, 44, 48, 50, 46, 39, 32, 29, 27]
            loss_vals = [0, 0, 0, 1, 3, 5, 4, 6, 4, 2, 1, 0, 0]
            jitter_vals = [2, 2, 2, 4, 8, 11, 10, 12, 9, 6, 3, 2, 2]
            tput_vals = [30, 25, 20, 35, 70, 95, 110, 105, 98, 85, 65, 45, 35]
        elif timeframe == "7d":
            timestamps = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            rtt_vals = [31, 34, 42, 38, 48, 28, 26]
            loss_vals = [1.8, 2.1, 4.5, 3.2, 5.8, 1.2, 0.9]
            jitter_vals = [3.5, 4.0, 7.8, 5.2, 9.4, 2.5, 2.0]
            tput_vals = [72, 78, 85, 80, 92, 58, 50]
        else: # 1h default
            timestamps = [f"10:{45+i*5}" if 45+i*5 < 60 else f"11:{45+i*5-60:02d}" for i in range(13)]
            rtt_vals = [32, 28, 30, 36, 42, 38, 35, 40, 34, 31, 33, 35, 32]
            loss_vals = [2, 1, 0, 4, 3, 2, 1, 5, 2, 1, 0, 2, 2]
            jitter_vals = [4, 3, 5, 8, 9, 7, 5, 11, 6, 4, 3, 5, 4]
            tput_vals = [45, 52, 60, 48, 70, 85, 62, 90, 75, 68, 80, 115, 65]
    else:
        timestamps = df["time_label"].tolist() if "time_label" in df.columns else df.index.tolist()
        rtt_vals = df["rtt_ms"].tolist()
        loss_vals = df["loss_pct"].tolist()
        jitter_vals = df["jitter_ms"].tolist()
        tput_vals = df["throughput_mbps"].tolist()

    # RTT line (Teal/Cyan)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=rtt_vals,
        name="RTT (ms)",
        mode="lines",
        line=dict(color="#06b6d4", width=2.2, shape="spline"),
        hovertemplate="%{y:.1f} ms"
    ))

    # Packet Loss line (Blue)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=loss_vals,
        name="Packet Loss (%)",
        mode="lines",
        line=dict(color="#3b82f6", width=2.2, shape="spline"),
        hovertemplate="%{y:.1f}%"
    ))

    # Jitter line (Purple)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=jitter_vals,
        name="Jitter (ms)",
        mode="lines",
        line=dict(color="#8b5cf6", width=2.2, shape="spline"),
        hovertemplate="%{y:.1f} ms"
    ))

    # Throughput line (Amber)
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=tput_vals,
        name="Throughput (Mbps)",
        mode="lines",
        line=dict(color="#f59e0b", width=2.2, shape="spline"),
        hovertemplate="%{y:.1f} Mbps"
    ))

    bg_c = "#111827" if is_dark else "#ffffff"
    grid_c = "rgba(255, 255, 255, 0.08)" if is_dark else "#f1f5f9"
    text_c = "#94a3b8" if is_dark else "#64748b"

    fig.update_layout(
        margin=dict(l=25, r=10, t=10, b=25),
        height=220,
        paper_bgcolor=bg_c,
        plot_bgcolor=bg_c,
        hovermode="x unified",
        uirevision="trends",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color=text_c)
        ),
        xaxis=dict(
            showgrid=False,
            color="#94a3b8",
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_c,
            color="#94a3b8",
            range=[0, 150],
            tickfont=dict(size=9)
        )
    )

    return fig

# --- Bottom Grid: Packet Loss & Availability Donut Chart ---

def create_availability_donut_figure(avail_pct: float = 97.6, successful: int = 1217, failed: int = 29, is_dark: bool = False) -> go.Figure:
    fig = go.Figure()

    labels = ["Successful", "Failed"]
    values = [successful, failed]
    colors = ["#10b981", "#f43f5e"]
    bg_c = "#111827" if is_dark else "#ffffff"
    text_c = "#f8fafc" if is_dark else "#0f172a"
    sub_c = "#94a3b8" if is_dark else "#64748b"

    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.74,
        marker=dict(colors=colors),
        textinfo="none",
        hoverinfo="label+value+percent",
        showlegend=False
    ))

    fig.update_layout(
        annotations=[
            dict(
                text=f"<b>{avail_pct:.1f}%</b><br><span style='font-size:11px;color:{sub_c};'>Availability</span>",
                x=0.5, y=0.5,
                font=dict(size=18, family="Inter, sans-serif", color=text_c),
                showarrow=False
            )
        ],
        margin=dict(l=0, r=0, t=0, b=0),
        height=190,
        paper_bgcolor=bg_c,
        uirevision="donut"
    )

    return fig


# ==========================================
# ADVANCED ANALYTICS CHARTING & DATA HELPERS
# ==========================================

def fetch_analytics_measurements(
    target_id: Optional[Any] = None,
    time_range_hours: Optional[float] = None,
    db_path: str = DEFAULT_DB_PATH
) -> pd.DataFrame:
    """
    Fetches raw telemetry measurements joined with target names and hosts.
    Excludes no records prematurely so packet loss can be accurately computed.
    """
    from database.db import get_connection
    query = """
    SELECT 
        m.id,
        m.timestamp,
        m.target_id,
        COALESCE(t.name, 'Target ' || m.target_id) AS target_name,
        COALESCE(t.host, '') AS host,
        m.protocol,
        m.test_type,
        m.success,
        m.rtt_ms,
        m.ttl,
        m.error
    FROM measurements m
    LEFT JOIN targets t ON m.target_id = t.target_id
    """
    params = []
    if target_id is not None and str(target_id).strip().lower() not in ("all", "none", ""):
        query += " WHERE m.target_id = ?"
        try:
            params.append(int(target_id))
        except (ValueError, TypeError):
            params.append(str(target_id))
    
    query += " ORDER BY m.id ASC"

    with get_connection(db_path) as conn:
        c = getattr(conn, "_conn", conn)
        df = pd.read_sql_query(query, c, params=params if params else None)

    if not df.empty and time_range_hours and time_range_hours > 0:
        parsed_ts = pd.to_datetime(df['timestamp'], errors='coerce')
        cutoff = datetime.datetime.now() - datetime.timedelta(hours=time_range_hours)
        df = df[parsed_ts >= cutoff].copy()

    return df


def fetch_analytics_window_metrics(
    target_id: Optional[Any] = None,
    time_range_hours: Optional[float] = None,
    db_path: str = DEFAULT_DB_PATH
) -> pd.DataFrame:
    """
    Fetches aggregated rolling statistical windows from window_metrics table.
    Filters by target_id and time_range_hours when specified.
    """
    from database.db import get_connection
    query = """
    SELECT 
        w.id,
        w.target_id,
        COALESCE(t.name, CASE WHEN w.target_id = 'global' THEN 'Global (All Targets)' ELSE 'Target ' || w.target_id END) AS target_name,
        w.start_time,
        w.end_time,
        w.loss_pct,
        w.availability_pct,
        w.jitter_ms,
        w.p95_ms,
        w.p99_ms,
        w.throughput_mbps
    FROM window_metrics w
    LEFT JOIN targets t ON CAST(w.target_id AS INTEGER) = t.target_id
    """
    params = []
    if target_id is not None and str(target_id).strip().lower() not in ("all", "none", ""):
        query += " WHERE (w.target_id = ? OR w.target_id = ?)"
        params.extend([str(target_id), target_id])
    
    query += " ORDER BY w.id ASC"

    with get_connection(db_path) as conn:
        c = getattr(conn, "_conn", conn)
        df = pd.read_sql_query(query, c, params=params if params else None)

    if not df.empty and time_range_hours and time_range_hours > 0:
        ts_col = df['end_time'].fillna(df['start_time'])
        parsed_ts = pd.to_datetime(ts_col, errors='coerce')
        cutoff = datetime.datetime.now() - datetime.timedelta(hours=time_range_hours)
        df = df[parsed_ts >= cutoff].copy()

    return df


def compute_analytics_summary_kpis(
    measurements_df: pd.DataFrame,
    window_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Computes summary KPI metrics from measurement and window records.
    Safely handles empty datasets and failed probes without crashing or coercing missing to 0.0.
    """
    from telemetry.metrics import calculate_jitter, calculate_percentile

    # 1. RTT Latency KPI (only successful probes with valid RTT)
    avg_rtt = None
    if not measurements_df.empty:
        valid_rtts = measurements_df.loc[
            (measurements_df["success"] == 1) & 
            (measurements_df["rtt_ms"].notna()) & 
            (measurements_df["rtt_ms"] > 0), 
            "rtt_ms"
        ]
        if not valid_rtts.empty:
            avg_rtt = round(float(valid_rtts.mean()), 1)

    # 2. Packet Loss & Availability KPIs
    loss_pct = 0.0
    avail_pct = 100.0
    if not window_df.empty and "loss_pct" in window_df.columns and window_df["loss_pct"].notna().any():
        loss_pct = round(float(window_df["loss_pct"].dropna().iloc[-1]), 1)
        if "availability_pct" in window_df.columns and window_df["availability_pct"].notna().any():
            avail_pct = round(float(window_df["availability_pct"].dropna().iloc[-1]), 1)
        else:
            avail_pct = round(100.0 - loss_pct, 1)
    elif not measurements_df.empty:
        total = len(measurements_df)
        succ = int((measurements_df["success"] == 1).sum())
        loss_pct = round(((total - succ) / total) * 100, 1) if total > 0 else 0.0
        avail_pct = round((succ / total) * 100, 1) if total > 0 else 100.0

    # 3. Jitter KPI
    jitter_ms = 0.0
    if not window_df.empty and "jitter_ms" in window_df.columns and window_df["jitter_ms"].notna().any():
        jitter_ms = round(float(window_df["jitter_ms"].dropna().iloc[-1]), 2)
    elif not measurements_df.empty:
        valid_rtts = measurements_df.loc[
            (measurements_df["success"] == 1) & (measurements_df["rtt_ms"].notna()), 
            "rtt_ms"
        ].tolist()
        if len(valid_rtts) >= 2:
            jitter_ms = round(float(calculate_jitter(valid_rtts)), 2)

    # 4. P95 & P99 KPIs
    p95_ms = None
    p99_ms = None
    if not window_df.empty and "p95_ms" in window_df.columns and window_df["p95_ms"].notna().any():
        p95_ms = round(float(window_df["p95_ms"].dropna().iloc[-1]), 1)
        if "p99_ms" in window_df.columns and window_df["p99_ms"].notna().any():
            p99_ms = round(float(window_df["p99_ms"].dropna().iloc[-1]), 1)
    elif not measurements_df.empty:
        valid_rtts = measurements_df.loc[
            (measurements_df["success"] == 1) & (measurements_df["rtt_ms"].notna()), 
            "rtt_ms"
        ].tolist()
        if valid_rtts:
            p95_ms = round(float(calculate_percentile(valid_rtts, 95)), 1)
            p99_ms = round(float(calculate_percentile(valid_rtts, 99)), 1)

    return {
        "avg_rtt": avg_rtt,
        "loss_pct": loss_pct,
        "availability_pct": avail_pct,
        "jitter_ms": jitter_ms,
        "p95_ms": p95_ms,
        "p99_ms": p99_ms
    }


def create_rtt_timeline_chart(
    df: pd.DataFrame,
    is_dark: bool = False,
    target_name: Optional[str] = None
) -> go.Figure:
    """
    Renders an interactive line chart of RTT / Latency over time.
    Excludes failed probes (missing RTT values) from the latency line.
    Never displays missing values as 0.0.
    """
    fig = go.Figure()
    bg_c = "#111827" if is_dark else "#ffffff"
    grid_c = "rgba(255, 255, 255, 0.08)" if is_dark else "#f1f5f9"
    text_c = "#94a3b8" if is_dark else "#64748b"

    if df.empty:
        fig.add_annotation(
            text="No telemetry measurements recorded for this selection.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=280, margin=dict(l=20, r=20, t=30, b=20)
        )
        return fig

    # Filter out failed probes with missing RTT values
    valid_df = df[
        (df["success"] == 1) & 
        (df["rtt_ms"].notna()) & 
        (df["rtt_ms"] > 0)
    ].copy()

    if valid_df.empty:
        fig.add_annotation(
            text="No successful latency probes recorded (all probes failed or timed out).",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color="#ef4444")
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=280, margin=dict(l=20, r=20, t=30, b=20)
        )
        return fig

    # Palette for multi-target lines
    palette = ["#06b6d4", "#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899", "#14b8a6", "#f97316"]

    # Check if multiple targets exist in valid_df
    distinct_targets = valid_df["target_name"].dropna().unique().tolist()
    if len(distinct_targets) > 1 and (target_name is None or "all" in str(target_name).lower()):
        for idx, t_name in enumerate(distinct_targets):
            sub_df = valid_df[valid_df["target_name"] == t_name]
            color = palette[idx % len(palette)]
            fig.add_trace(go.Scatter(
                x=sub_df["timestamp"],
                y=sub_df["rtt_ms"],
                name=t_name,
                mode="lines+markers",
                marker=dict(size=4),
                line=dict(color=color, width=2.0, shape="spline"),
                hovertemplate=f"<b>{t_name}</b><br>%{{x}}<br>RTT: %{{y:.2f}} ms<extra></extra>"
            ))
    else:
        # Single target line
        t_label = target_name or (distinct_targets[0] if distinct_targets else "RTT")
        fig.add_trace(go.Scatter(
            x=valid_df["timestamp"],
            y=valid_df["rtt_ms"],
            name="RTT Latency",
            mode="lines+markers",
            marker=dict(size=4, color="#06b6d4"),
            line=dict(color="#06b6d4", width=2.2, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(6, 182, 212, 0.08)",
            hovertemplate=f"<b>{t_label}</b><br>%{{x}}<br>RTT: %{{y:.2f}} ms<extra></extra>"
        ))

    fig.update_layout(
        margin=dict(l=45, r=20, t=25, b=35),
        height=280,
        paper_bgcolor=bg_c,
        plot_bgcolor=bg_c,
        hovermode="x unified" if len(distinct_targets) > 1 else "closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=text_c)
        ),
        xaxis=dict(
            title=dict(text="Timestamp", font=dict(size=11, color=text_c)),
            showgrid=False,
            color=text_c,
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            title=dict(text="RTT Latency (ms)", font=dict(size=11, color=text_c)),
            showgrid=True,
            gridcolor=grid_c,
            color=text_c,
            tickfont=dict(size=9)
        )
    )
    return fig


def create_packet_loss_chart(df: pd.DataFrame, is_dark: bool = False) -> go.Figure:
    """
    Visualizes packet loss rate (%) over rolling windows.
    """
    fig = go.Figure()
    bg_c = "#111827" if is_dark else "#ffffff"
    grid_c = "rgba(255, 255, 255, 0.08)" if is_dark else "#f1f5f9"
    text_c = "#94a3b8" if is_dark else "#64748b"

    if df.empty or "loss_pct" not in df.columns:
        fig.add_annotation(
            text="No rolling statistical window records available for packet loss.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=230, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    valid_df = df[df["loss_pct"].notna()].copy()
    if valid_df.empty:
        fig.add_annotation(
            text="No packet loss data in window records.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=230, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    ts_series = valid_df["end_time"].fillna(valid_df["start_time"])
    max_loss = float(valid_df["loss_pct"].max())

    fig.add_trace(go.Scatter(
        x=ts_series,
        y=valid_df["loss_pct"],
        name="Packet Loss (%)",
        mode="lines+markers",
        marker=dict(size=5, color="#f43f5e"),
        line=dict(color="#f43f5e", width=2.0, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(244, 63, 94, 0.08)",
        hovertemplate="<b>%{x}</b><br>Packet Loss: %{y:.1f}%<extra></extra>"
    ))

    fig.update_layout(
        margin=dict(l=45, r=15, t=15, b=30),
        height=230,
        paper_bgcolor=bg_c,
        plot_bgcolor=bg_c,
        hovermode="closest",
        xaxis=dict(
            title=dict(text="Window Time", font=dict(size=10, color=text_c)),
            showgrid=False,
            color=text_c,
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            title=dict(text="Loss (%)", font=dict(size=10, color=text_c)),
            showgrid=True,
            gridcolor=grid_c,
            color=text_c,
            range=[0, max(5.0, max_loss * 1.15)],
            tickfont=dict(size=9)
        )
    )
    return fig


def create_availability_chart(df: pd.DataFrame, is_dark: bool = False) -> go.Figure:
    """
    Visualizes network availability (%) over rolling windows with an SLA target benchmark.
    """
    fig = go.Figure()
    bg_c = "#111827" if is_dark else "#ffffff"
    grid_c = "rgba(255, 255, 255, 0.08)" if is_dark else "#f1f5f9"
    text_c = "#94a3b8" if is_dark else "#64748b"

    if df.empty or "availability_pct" not in df.columns:
        fig.add_annotation(
            text="No rolling statistical window records available for availability.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=230, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    valid_df = df[df["availability_pct"].notna()].copy()
    if valid_df.empty:
        fig.add_annotation(
            text="No availability metrics in window records.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=230, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    ts_series = valid_df["end_time"].fillna(valid_df["start_time"])
    min_avail = float(valid_df["availability_pct"].min())

    fig.add_trace(go.Scatter(
        x=ts_series,
        y=valid_df["availability_pct"],
        name="Availability (%)",
        mode="lines+markers",
        marker=dict(size=5, color="#10b981"),
        line=dict(color="#10b981", width=2.0, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.08)",
        hovertemplate="<b>%{x}</b><br>Availability: %{y:.1f}%<extra></extra>"
    ))

    # Add SLA Benchmark line (99%)
    fig.add_hline(
        y=99.0,
        line_dash="dot",
        line_color="#059669",
        line_width=1.2,
        annotation_text="99% SLA",
        annotation_position="bottom right",
        annotation_font=dict(size=9, color="#059669")
    )

    fig.update_layout(
        margin=dict(l=45, r=15, t=15, b=30),
        height=230,
        paper_bgcolor=bg_c,
        plot_bgcolor=bg_c,
        hovermode="closest",
        xaxis=dict(
            title=dict(text="Window Time", font=dict(size=10, color=text_c)),
            showgrid=False,
            color=text_c,
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            title=dict(text="Availability (%)", font=dict(size=10, color=text_c)),
            showgrid=True,
            gridcolor=grid_c,
            color=text_c,
            range=[min(85.0, min_avail - 2.0), 101.0],
            tickfont=dict(size=9)
        )
    )
    return fig


def create_jitter_chart(df: pd.DataFrame, is_dark: bool = False) -> go.Figure:
    """
    Visualizes statistical jitter (ms) over rolling windows.
    """
    fig = go.Figure()
    bg_c = "#111827" if is_dark else "#ffffff"
    grid_c = "rgba(255, 255, 255, 0.08)" if is_dark else "#f1f5f9"
    text_c = "#94a3b8" if is_dark else "#64748b"

    if df.empty or "jitter_ms" not in df.columns:
        fig.add_annotation(
            text="No rolling statistical window records available for jitter.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=230, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    valid_df = df[df["jitter_ms"].notna()].copy()
    if valid_df.empty:
        fig.add_annotation(
            text="No jitter metrics recorded in window records.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=230, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    ts_series = valid_df["end_time"].fillna(valid_df["start_time"])
    max_jitter = float(valid_df["jitter_ms"].max())

    fig.add_trace(go.Scatter(
        x=ts_series,
        y=valid_df["jitter_ms"],
        name="Jitter (ms)",
        mode="lines+markers",
        marker=dict(size=5, color="#8b5cf6"),
        line=dict(color="#8b5cf6", width=2.0, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(139, 92, 246, 0.08)",
        hovertemplate="<b>%{x}</b><br>Jitter: %{y:.2f} ms<extra></extra>"
    ))

    fig.update_layout(
        margin=dict(l=45, r=15, t=15, b=30),
        height=230,
        paper_bgcolor=bg_c,
        plot_bgcolor=bg_c,
        hovermode="closest",
        xaxis=dict(
            title=dict(text="Window Time", font=dict(size=10, color=text_c)),
            showgrid=False,
            color=text_c,
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            title=dict(text="Jitter (ms)", font=dict(size=10, color=text_c)),
            showgrid=True,
            gridcolor=grid_c,
            color=text_c,
            range=[0, max(5.0, max_jitter * 1.2)],
            tickfont=dict(size=9)
        )
    )
    return fig


def create_p95_p99_comparison_chart(df: pd.DataFrame, is_dark: bool = False) -> go.Figure:
    """
    Compares P95 vs P99 percentile latencies across measurement windows.
    """
    fig = go.Figure()
    bg_c = "#111827" if is_dark else "#ffffff"
    grid_c = "rgba(255, 255, 255, 0.08)" if is_dark else "#f1f5f9"
    text_c = "#94a3b8" if is_dark else "#64748b"

    if df.empty or ("p95_ms" not in df.columns and "p99_ms" not in df.columns):
        fig.add_annotation(
            text="No rolling statistical window records available for P95/P99 latency.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=230, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    valid_df = df[df["p95_ms"].notna() | df["p99_ms"].notna()].copy()
    if valid_df.empty:
        fig.add_annotation(
            text="No percentile latency metrics recorded in window records.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=230, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    ts_series = valid_df["end_time"].fillna(valid_df["start_time"])

    # P95 trace
    if "p95_ms" in valid_df.columns:
        fig.add_trace(go.Scatter(
            x=ts_series,
            y=valid_df["p95_ms"],
            name="P95 Latency",
            mode="lines+markers",
            marker=dict(size=4, color="#f59e0b"),
            line=dict(color="#f59e0b", width=2.0, shape="spline"),
            hovertemplate="P95: %{y:.1f} ms"
        ))

    # P99 trace
    if "p99_ms" in valid_df.columns:
        fig.add_trace(go.Scatter(
            x=ts_series,
            y=valid_df["p99_ms"],
            name="P99 Latency",
            mode="lines+markers",
            marker=dict(size=4, color="#f43f5e"),
            line=dict(color="#f43f5e", width=2.0, dash="dash", shape="spline"),
            hovertemplate="P99: %{y:.1f} ms"
        ))

    fig.update_layout(
        margin=dict(l=45, r=15, t=25, b=30),
        height=230,
        paper_bgcolor=bg_c,
        plot_bgcolor=bg_c,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=text_c)
        ),
        xaxis=dict(
            title=dict(text="Window Time", font=dict(size=10, color=text_c)),
            showgrid=False,
            color=text_c,
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            title=dict(text="Latency (ms)", font=dict(size=10, color=text_c)),
            showgrid=True,
            gridcolor=grid_c,
            color=text_c,
            tickfont=dict(size=9)
        )
    )
    return fig


import textwrap

def clean_html(text: str) -> str:
    """Removes all leading indentation so markdown parsers never mistake HTML for code blocks."""
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)

# --- Bottom Grid: Top Targets by Latency Progress Bars ---

def render_latency_progress_bars(targets: List[Dict[str, Any]]) -> str:
    if not targets:
        return '<div style="text-align:center; padding:1rem; color:var(--text-secondary); font-size:0.825rem;">No monitored targets registered.</div>'
    rows = []
    max_ms = 60.0

    for t in targets:
        name = t.get("name", "Target")
        rtt = t.get("rtt_ms")
        if rtt is not None and rtt > 0:
            pct = min(100.0, (rtt / max_ms) * 100) if max_ms > 0 else 0
            val_tag = f"{int(round(rtt))} ms"
        else:
            pct = 0.0
            val_tag = "N/A"
        icon = get_brand_icon(name)

        row = (
            f'<div class="latency-bar-row">'
            f'<div class="latency-logo-group">{icon}<span class="latency-host-title">{name}</span></div>'
            f'<div class="latency-track"><div class="latency-fill" style="width: {pct:.1f}%;"></div></div>'
            f'<span class="latency-value-tag">{val_tag}</span>'
            f'</div>'
        )
        rows.append(row)
    res = clean_html("\n".join(rows))
    if not res or not res.strip():
        return '<div style="text-align:center; padding:1rem; color:var(--text-secondary); font-size:0.825rem;">No monitored targets registered.</div>'
    return res

# --- Column 2: Live Target Status Card ---

def render_live_target_status_list(targets: List[Dict[str, Any]]) -> str:
    if not targets:
        return '<div style="text-align:center; padding:1rem; color:var(--text-secondary); font-size:0.825rem;">No targets configured.</div>'
    rows = []
    for t in targets:
        name = t.get("name", "Host")
        ip = t.get("resolved_ip") or t.get("host")
        rtt = t.get("rtt_ms")
        rtt_str = f"{int(round(rtt))} ms" if rtt is not None else "N/A"
        loss = t.get("loss_pct", 0.0)
        avail = t.get("availability_pct", round(100.0 - loss, 1))
        status = t.get("status", "Online")
        if status == "Online":
            badge_cls = "badge-online"
        elif status == "Degraded":
            badge_cls = "badge-degraded"
        elif status == "Unknown":
            badge_cls = "badge-unknown"
        else:
            badge_cls = "badge-offline"
        icon = get_brand_icon(name)

        row = (
            f'<div class="target-status-row">'
            f'<div class="target-info-group">'
            f'<div class="brand-logo-img">{icon}</div>'
            f'<div class="target-name-ip"><span class="target-name">{name}</span><span class="target-ip">{ip}</span></div>'
            f'</div>'
            f'<div class="target-metric-capsule">'
            f'<div class="metric-label-val"><span class="metric-lbl">RTT</span><span class="metric-v">{rtt_str}</span></div>'
            f'<div class="metric-label-val"><span class="metric-lbl">Loss</span><span class="metric-v">{loss:.1f}%</span></div>'
            f'<div class="metric-label-val"><span class="metric-lbl">Avail</span><span class="metric-v">{avail:.0f}%</span></div>'
            f'<span class="badge-status {badge_cls}">{status}</span>'
            f'</div>'
            f'</div>'
        )
        rows.append(row)
    res = clean_html("\n".join(rows))
    if not res or not res.strip():
        return '<div style="text-align:center; padding:1rem; color:var(--text-secondary); font-size:0.825rem;">No targets configured.</div>'
    return res

# --- Column 2: Active Alerts Card ---

def render_active_alerts_list(anomalies: List[Dict[str, Any]]) -> str:
    if not anomalies:
        return '<div style="text-align:center; padding:1rem; color:#10b981; font-size:0.825rem;">✅ All systems nominal. 0 active alerts.</div>'
    rows = []
    for a in anomalies:
        name = a.get("name") or a.get("target_id") or "Target"
        host = a.get("host") or ""
        reason = a.get("reason", "Network issue detected")
        ts = a.get("timestamp", "")
        try:
            dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            time_str = dt.strftime("%I:%M %p")
        except Exception:
            time_str = "Recently"

        is_critical = "100%" in reason or "timeout" in reason.lower()
        badge_cls = "badge-critical" if is_critical else "badge-warning"
        dot_cls = "alert-dot-critical" if is_critical else "alert-dot-warning"
        badge_text = "Critical" if is_critical else "Warning"

        row = (
            f'<div class="alert-item-row">'
            f'<div class="alert-left-group">'
            f'<div class="alert-indicator-dot {dot_cls}"></div>'
            f'<div class="alert-desc-group"><span class="alert-target-title">{name} ({host})</span><span class="alert-meta-reason">{time_str} • {reason}</span></div>'
            f'</div>'
            f'<span class="{badge_cls}">{badge_text}</span>'
            f'</div>'
        )
        rows.append(row)
    res = clean_html("\n".join(rows))
    if not res or not res.strip():
        return '<div style="text-align:center; padding:1rem; color:#10b981; font-size:0.825rem;">✅ All systems nominal. 0 active alerts.</div>'
    return res

# --- Column 2: Recent Activity Micro Table ---

def render_recent_activity_rows(measurements: List[Dict[str, Any]]) -> str:
    if not measurements:
        return (
            '<div style="text-align:center; padding:1.25rem 0.5rem; color:var(--text-secondary); font-size:0.825rem;">'
            'No recent activity recorded.<br><span style="font-size:0.75rem; color:var(--text-muted);">'
            'Start monitoring or click Probe All Targets to record new activity.'
            '</span></div>'
        )
    rows = []
    for m in measurements:
        ts = m.get("timestamp", "")
        try:
            dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            time_str = dt.strftime("%H:%M")
        except Exception:
            time_str = "11:42"

        name = m.get("name") or m.get("target_id") or "Target"
        rtt = m.get("rtt_ms")
        success = m.get("success", 1)
        rtt_str = f"{int(round(rtt))} ms" if (rtt is not None and success) else "N/A"
        loss = "0.0%" if success else "100.0%"
        dot_color = "#10b981" if success else "#ef4444"

        row = (
            f'<div class="activity-row">'
            f'<span class="activity-time">{time_str}</span>'
            f'<span class="activity-name">{name}</span>'
            f'<span class="activity-rtt">{rtt_str}</span>'
            f'<span class="activity-loss">{loss}</span>'
            f'<div class="activity-status-dot" style="background-color: {dot_color};"></div>'
            f'</div>'
        )
        rows.append(row)
    res = clean_html("\n".join(rows))
    if not res or not res.strip():
        return (
            '<div style="text-align:center; padding:1.25rem 0.5rem; color:var(--text-secondary); font-size:0.825rem;">'
            'No recent activity recorded.<br><span style="font-size:0.75rem; color:var(--text-muted);">'
            'Start monitoring or click Probe All Targets to record new activity.'
            '</span></div>'
        )
    return res


# --- Anomaly Timeline Visualization ---

def fetch_anomaly_records(
    target_id: Optional[Any] = None,
    metric: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH
) -> pd.DataFrame:
    """
    Safely reads anomaly records from the SQLite database joined with targets.
    Maps target IDs/names to actual targets (name, host, resolved_ip).
    Filters by target_id and metric when specified.
    Handles missing values and invalid timestamps safely.
    """
    from database.db import get_connection
    query = """
    SELECT 
        a.id,
        a.timestamp,
        a.target_id,
        COALESCE(t.name, CASE WHEN a.target_id IS NOT NULL AND a.target_id != '' THEN 'Target #' || a.target_id ELSE 'Unknown Target' END) AS target_name,
        COALESCE(t.host, t.resolved_ip, '') AS target_host,
        t.resolved_ip,
        a.metric,
        a.observed_value,
        a.baseline,
        a.threshold,
        a.reason
    FROM anomalies a
    LEFT JOIN targets t ON (
        a.target_id = t.target_id 
        OR a.target_id = CAST(t.target_id AS TEXT) 
        OR a.target_id = t.name 
        OR a.target_id = t.host
    )
    """
    conditions = []
    params = []

    if target_id is not None and str(target_id).strip().lower() not in ("all", "none", ""):
        conditions.append("(a.target_id = ? OR a.target_id = ? OR t.name = ? OR t.host = ?)")
        params.extend([str(target_id), target_id, str(target_id), str(target_id)])

    if metric is not None and str(metric).strip().lower() not in ("all", "none", ""):
        conditions.append("a.metric = ?")
        params.append(str(metric).strip())

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY a.timestamp ASC, a.id ASC"

    with get_connection(db_path) as conn:
        c = getattr(conn, "_conn", conn)
        df = pd.read_sql_query(query, c, params=params if params else None)

    if df.empty:
        return df

    # Safe timestamp parsing
    df["parsed_timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", errors="coerce")
    
    # Fill missing optional text fields safely
    df["target_name"] = df["target_name"].fillna("Unknown Target")
    df["target_host"] = df["target_host"].fillna("")
    df["metric"] = df["metric"].fillna("unknown")
    df["reason"] = df["reason"].fillna("Threshold breach detected")

    return df


def create_anomaly_timeline_chart(
    df: pd.DataFrame, 
    is_dark: bool = False,
    view_mode: str = "magnitude"
) -> go.Figure:
    """
    Creates an interactive Plotly timeline chart for autonomous anomaly detection events.
    X-axis: anomaly timestamp
    Grouped and colored by metric (e.g. loss_pct, p95_ms, jitter_ms, timeout).
    Supports view_mode='magnitude' (Y = observed value) or 'swimlane' (Y = target name).
    Includes rich hover details (target name/IP, metric, observed, threshold, baseline, reason).
    Safely handles empty datasets and missing fields without exceptions.
    """
    fig = go.Figure()
    bg_c = "#111827" if is_dark else "#ffffff"
    grid_c = "rgba(255, 255, 255, 0.08)" if is_dark else "#f1f5f9"
    text_c = "#94a3b8" if is_dark else "#64748b"

    if df.empty or "metric" not in df.columns:
        fig.add_annotation(
            text="No anomaly records found matching the active filter criteria.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=280, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    # Filter out rows with unparseable timestamps
    valid_df = df.copy()
    if "parsed_timestamp" not in valid_df.columns:
        valid_df["parsed_timestamp"] = pd.to_datetime(valid_df["timestamp"], format="mixed", errors="coerce")
    
    valid_df = valid_df[valid_df["parsed_timestamp"].notna()].copy()

    if valid_df.empty:
        fig.add_annotation(
            text="No valid timestamped anomaly records available to display.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=text_c)
        )
        fig.update_layout(
            paper_bgcolor=bg_c, plot_bgcolor=bg_c,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=280, margin=dict(l=20, r=20, t=25, b=20)
        )
        return fig

    # Metric metadata configuration
    metric_meta = {
        "loss_pct": {"label": "Packet Loss (loss_pct)", "unit": "%", "color": "#f43f5e", "symbol": "circle"},
        "p95_ms": {"label": "P95 Latency (p95_ms)", "unit": "ms", "color": "#f59e0b", "symbol": "diamond"},
        "jitter_ms": {"label": "Jitter (jitter_ms)", "unit": "ms", "color": "#8b5cf6", "symbol": "square"},
        "timeout": {"label": "Probe Timeout (timeout)", "unit": "sec", "color": "#ef4444", "symbol": "triangle-up"},
        "rtt": {"label": "RTT Latency (rtt)", "unit": "ms", "color": "#06b6d4", "symbol": "circle-open"}
    }
    fallback_colors = ["#ec4899", "#14b8a6", "#3b82f6", "#6366f1", "#10b981", "#d97706"]

    distinct_metrics = valid_df["metric"].dropna().unique().tolist()
    is_swimlane = (view_mode == "swimlane")

    for idx, metric_key in enumerate(distinct_metrics):
        sub_df = valid_df[valid_df["metric"] == metric_key].copy()
        if sub_df.empty:
            continue

        meta = metric_meta.get(metric_key, {
            "label": f"{str(metric_key).replace('_', ' ').title()} ({metric_key})",
            "unit": "ms" if ("ms" in str(metric_key).lower() or "rtt" in str(metric_key).lower()) else (
                "%" if ("pct" in str(metric_key).lower() or "loss" in str(metric_key).lower()) else ""
            ),
            "color": fallback_colors[idx % len(fallback_colors)],
            "symbol": "circle"
        })

        unit = meta["unit"]
        label = meta["label"]
        color = meta["color"]
        symbol = meta["symbol"]

        # Build customdata array for rich hover
        customdata_rows = []
        for _, row in sub_df.iterrows():
            t_name = str(row.get("target_name") or "Unknown Target")
            host_val = row.get("target_host") or row.get("resolved_ip") or "N/A"
            host_str = str(host_val) if str(host_val).strip() else "N/A"
            
            obs_val = row.get("observed_value")
            obs_str = f"{float(obs_val):.2f}".rstrip("0").rstrip(".") if pd.notna(obs_val) else "0"
            
            thresh_val = row.get("threshold")
            thresh_str = f"{float(thresh_val):.2f}".rstrip("0").rstrip(".") if pd.notna(thresh_val) else "N/A"
            
            base_val = row.get("baseline")
            base_str = f"{float(base_val):.2f}".rstrip("0").rstrip(".") if pd.notna(base_val) else "N/A"
            
            reason_str = str(row.get("reason") or "Threshold breach")
            
            customdata_rows.append([t_name, host_str, label, unit, obs_str, thresh_str, base_str, reason_str])

        y_data = sub_df["target_name"] if is_swimlane else sub_df["observed_value"].fillna(0.0)

        hovertemplate = (
            "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
            "<b>Metric:</b> %{customdata[2]}<br>"
            "<b>Observed Value:</b> %{customdata[4]} %{customdata[3]}<br>"
            "<b>Threshold:</b> %{customdata[5]} %{customdata[3]}<br>"
            "<b>Baseline:</b> %{customdata[6]} %{customdata[3]}<br>"
            "<b>Reason:</b> %{customdata[7]}<br>"
            "<b>Timestamp:</b> %{x|%Y-%m-%d %H:%M:%S}<extra></extra>"
        )

        trace_name = f"{label} ({len(sub_df)})"

        fig.add_trace(go.Scatter(
            x=sub_df["parsed_timestamp"],
            y=y_data,
            name=trace_name,
            mode="markers",
            marker=dict(
                size=11,
                symbol=symbol,
                color=color,
                line=dict(width=1.5, color="#ffffff" if is_dark else "#0e2428")
            ),
            customdata=customdata_rows,
            hovertemplate=hovertemplate
        ))

    # Determine Y-axis title
    if is_swimlane:
        y_title = "Monitored Network Targets"
    elif len(distinct_metrics) == 1:
        single_meta = metric_meta.get(distinct_metrics[0], {})
        unit = single_meta.get("unit", "")
        y_title = f"Observed Value ({unit})" if unit else "Observed Value"
    else:
        y_title = "Observed Metric Magnitude"

    fig.update_layout(
        margin=dict(l=55, r=20, t=30, b=40),
        height=320,
        paper_bgcolor=bg_c,
        plot_bgcolor=bg_c,
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=10, color=text_c)
        ),
        xaxis=dict(
            title=dict(text="Anomaly Timestamp", font=dict(size=11, color=text_c)),
            showgrid=True,
            gridcolor=grid_c,
            color=text_c,
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(size=11, color=text_c)),
            showgrid=True,
            gridcolor=grid_c,
            color=text_c,
            tickfont=dict(size=9)
        )
    )
    return fig

