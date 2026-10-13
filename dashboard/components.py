"""
UI Components and Visual Visualizations for NetTelemetry Dashboard.
Provides high-fidelity renders matching the NOC mockup image_1.png.
"""

import plotly.graph_objects as go
import pandas as pd
import datetime
from typing import List, Dict, Any, Optional

# --- High Quality SVG Brand Icons ---

SVG_NET_LOGO = """
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
</svg>
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
    return """
    <div style="display: flex; align-items: center; justify-content: flex-end; gap: 1rem; padding-top: 2px;">
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

def render_hero_greeting() -> str:
    now = datetime.datetime.now()
    formatted_date = now.strftime("%a, %b %d, %Y")
    formatted_time = now.strftime("%I:%M %p")

    return f"""
    <div class="hero-greeting-container" style="margin-top: 0.5rem; margin-bottom: 1.25rem;">
        <div>
            <div class="hero-subtitle-tag">NETWORK TELEMETRY</div>
            <div class="hero-main-title">Good Morning, Dhanumithra!</div>
            <div class="hero-subtext">Here's what's happening with your network targets today.</div>
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
            <span class="live-badge-pill">Live</span>
        </div>
    </div>
    """

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
    return f"""
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
            <span class="kpi-dots">···</span>
        </div>
        <div class="kpi-value">{total_targets}</div>
        <div class="kpi-subtext kpi-subtext-green">
            <span>↑</span> {online} online • {offline} offline
        </div>
        {spark}
    </div>
    """

def render_kpi_card_2(avg_rtt: float = 32.0, change_pct: float = -18.0) -> str:
    spark = generate_sparkline_svg("#3b82f6", [38, 35, 36, 34, 35, 33, 31, 32])
    return f"""
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
            <span class="kpi-dots">···</span>
        </div>
        <div class="kpi-value">{int(round(avg_rtt))} ms</div>
        <div class="kpi-subtext kpi-subtext-blue">
            <span>↓</span> {abs(int(change_pct))}% (vs. last hour)
        </div>
        {spark}
    </div>
    """

def render_kpi_card_3(loss_pct: float = 2.4, change_pct: float = -6.0) -> str:
    spark = generate_sparkline_svg("#f59e0b", [4.0, 3.8, 3.2, 3.5, 2.9, 2.7, 2.4])
    return f"""
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
            <span class="kpi-dots">···</span>
        </div>
        <div class="kpi-value">{loss_pct:.1f}%</div>
        <div class="kpi-subtext kpi-subtext-amber">
            <span>↓</span> {abs(int(change_pct))}% (vs. last hour)
        </div>
        {spark}
    </div>
    """

def render_kpi_card_4(avail_pct: float = 97.6, change_pct: float = 2.1) -> str:
    spark = generate_sparkline_svg("#8b5cf6", [95.0, 95.8, 96.2, 96.5, 97.1, 97.6])
    return f"""
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
            <span class="kpi-dots">···</span>
        </div>
        <div class="kpi-value">{avail_pct:.1f}%</div>
        <div class="kpi-subtext kpi-subtext-purple">
            <span>↑</span> {change_pct:.1f}% (vs. last hour)
        </div>
        {spark}
    </div>
    """

# --- Network Topology Map ---

def create_topology_map_figure(targets: List[Dict[str, Any]]) -> go.Figure:
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
        color = "#10b981" if status == "Online" else ("#f59e0b" if status == "Degraded" else "#ef4444")

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
            textfont=dict(family="Inter, sans-serif", size=10, color="#1e293b"),
            hoverinfo="text",
            hovertext=f"<b>{coords['name']}</b> ({coords['ip']})<br>Status: {status}<br>RTT: {t.get('rtt_ms', 0)} ms<br>Loss: {t.get('loss_pct', 0)}%",
            showlegend=False
        ))

    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="#dbe4ed",
        showocean=True,
        oceancolor="#f8fafc",
        showcountries=True,
        countrycolor="#cbd5e1",
        countrywidth=0.6,
        showcoastlines=True,
        coastlinecolor="#cbd5e1",
        showframe=False,
        bgcolor="#ffffff"
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=320,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        dragmode=False
    )

    return fig

# --- Bottom Grid: Performance Trends Multi-Line Chart ---

def create_performance_trends_figure(df: Optional[pd.DataFrame] = None) -> go.Figure:
    fig = go.Figure()

    if df is None or df.empty:
        # Default mock 1h trend matching mockup
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

    fig.update_layout(
        margin=dict(l=25, r=10, t=10, b=25),
        height=220,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#64748b")
        ),
        xaxis=dict(
            showgrid=False,
            color="#94a3b8",
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f1f5f9",
            color="#94a3b8",
            range=[0, 150],
            tickfont=dict(size=9)
        )
    )

    return fig

# --- Bottom Grid: Packet Loss & Availability Donut Chart ---

def create_availability_donut_figure(avail_pct: float = 97.6, successful: int = 1217, failed: int = 29) -> go.Figure:
    fig = go.Figure()

    labels = ["Successful", "Failed"]
    values = [successful, failed]
    colors = ["#10b981", "#f43f5e"]

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
                text=f"<b>{avail_pct:.1f}%</b><br><span style='font-size:11px;color:#64748b;'>Availability</span>",
                x=0.5, y=0.5,
                font=dict(size=18, family="Inter, sans-serif", color="#0f172a"),
                showarrow=False
            )
        ],
        margin=dict(l=0, r=0, t=0, b=0),
        height=190,
        paper_bgcolor="#ffffff"
    )

    return fig

# --- Bottom Grid: Top Targets by Latency Progress Bars ---

def render_latency_progress_bars(targets: List[Dict[str, Any]]) -> str:
    rows_html = ""
    max_ms = 60.0

    for t in targets:
        name = t.get("name", "Target")
        rtt = t.get("rtt_ms", 0.0)
        pct = min(100.0, (rtt / max_ms) * 100) if max_ms > 0 else 0
        icon = get_brand_icon(name)

        rows_html += f"""
        <div class="latency-bar-row">
            <div class="latency-logo-group">
                {icon}
                <span class="latency-host-title">{name}</span>
            </div>
            <div class="latency-track">
                <div class="latency-fill" style="width: {pct:.1f}%;"></div>
            </div>
            <span class="latency-value-tag">{int(round(rtt))} ms</span>
        </div>
        """
    return rows_html

# --- Column 2: Live Target Status Card ---

def render_live_target_status_list(targets: List[Dict[str, Any]]) -> str:
    rows_html = ""
    for t in targets:
        name = t.get("name", "Host")
        ip = t.get("resolved_ip") or t.get("host")
        rtt = t.get("rtt_ms", 0.0)
        loss = t.get("loss_pct", 0.0)
        status = t.get("status", "Online")
        badge_cls = "badge-online" if status == "Online" else ("badge-degraded" if status == "Degraded" else "badge-offline")
        icon = get_brand_icon(name)

        rows_html += f"""
        <div class="target-status-row">
            <div class="target-info-group">
                <div class="brand-logo-img">{icon}</div>
                <div class="target-name-ip">
                    <span class="target-name">{name}</span>
                    <span class="target-ip">{ip}</span>
                </div>
            </div>
            <div class="target-metric-capsule">
                <div class="metric-label-val">
                    <span class="metric-lbl">RTT</span>
                    <span class="metric-v">{int(round(rtt))} ms</span>
                </div>
                <div class="metric-label-val">
                    <span class="metric-lbl">Loss</span>
                    <span class="metric-v">{loss:.1f}%</span>
                </div>
                <span class="badge-status {badge_cls}">{status}</span>
            </div>
        </div>
        """
    return rows_html

# --- Column 2: Active Alerts Card ---

def render_active_alerts_list(anomalies: List[Dict[str, Any]]) -> str:
    rows_html = ""
    for a in anomalies:
        name = a.get("name") or a.get("target_id") or "Target"
        host = a.get("host") or ""
        reason = a.get("reason", "Network issue detected")
        ts = a.get("timestamp", "")
        # Format time to e.g. 11:37 AM
        try:
            dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            time_str = dt.strftime("%I:%M %p")
        except Exception:
            time_str = "Recently"

        is_critical = "100%" in reason or "timeout" in reason.lower()
        badge_cls = "badge-critical" if is_critical else "badge-warning"
        dot_cls = "alert-dot-critical" if is_critical else "alert-dot-warning"
        badge_text = "Critical" if is_critical else "Warning"

        rows_html += f"""
        <div class="alert-item-row">
            <div class="alert-left-group">
                <div class="alert-indicator-dot {dot_cls}"></div>
                <div class="alert-desc-group">
                    <span class="alert-target-title">{name} ({host})</span>
                    <span class="alert-meta-reason">{time_str} • {reason}</span>
                </div>
            </div>
            <span class="{badge_cls}">{badge_text}</span>
        </div>
        """
    return rows_html

# --- Column 2: Recent Activity Micro Table ---

def render_recent_activity_rows(measurements: List[Dict[str, Any]]) -> str:
    rows_html = ""
    for m in measurements:
        ts = m.get("timestamp", "")
        try:
            dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            time_str = dt.strftime("%H:%M")
        except Exception:
            time_str = "11:42"

        name = m.get("name") or m.get("target_id") or "Target"
        rtt = m.get("rtt_ms") or 0.0
        success = m.get("success", 1)
        loss = "0.0%" if success else "100.0%"
        dot_color = "#10b981" if success else "#ef4444"

        rows_html += f"""
        <div class="activity-row">
            <span class="activity-time">{time_str}</span>
            <span class="activity-name">{name}</span>
            <span class="activity-rtt">{int(round(rtt))} ms</span>
            <span class="activity-loss">{loss}</span>
            <div class="activity-status-dot" style="background-color: {dot_color};"></div>
        </div>
        """
    return rows_html
