"""
CSS and Visual Design System for NetTelemetry NOC Dashboard.
Strictly translates image_1.png into modern, enterprise-grade styles.
"""

DARK_MODE_CSS = """
<style>
/* High-Contrast Enterprise NOC Dark Theme System */
:root {
    --bg-main: #090e17;
    --sidebar-bg: #070e1b;
    --sidebar-card: #0f172a;
    --card-bg: #111827;
    --card-border: rgba(255, 255, 255, 0.14);
    --card-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    --text-primary: #ffffff;
    --text-secondary: #cbd5e1;
    --text-muted: #94a3b8;
    --accent-teal: #14b8a6;
    --accent-mint: #34d399;
}

body, .stApp {
    background-color: #090e17 !important;
    color: #f8fafc !important;
}

/* Card Containers in Dark Mode */
[data-testid="stVerticalBlockBorderWrapper"], .kpi-card, .noc-card {
    background: #111827 !important;
    border-color: rgba(255, 255, 255, 0.14) !important;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5) !important;
}

/* All Headings - Crisp Pure White */
h1, h2, h3, h4, h5, h6,
.hero-main-title, .card-title-text, .kpi-value, .brand-title {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* General Text & Paragraphs */
p, span, label,
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stText"] {
    color: #e2e8f0 !important;
}

/* Subtitles, Captions & Meta Labels - High-Contrast Light Slate */
.hero-subtext, .target-ip, .alert-meta-reason, .activity-time,
.metric-lbl, .meta-subtext,
div[data-testid="stCaptionContainer"] p,
div[data-testid="stMarkdownContainer"] small {
    color: #cbd5e1 !important;
}

/* High-Contrast Metric Numbers */
.metric-v, .stat-highlight, .activity-name {
    color: #ffffff !important;
    font-weight: 700 !important;
}

.activity-rtt, .latency-value-tag {
    color: #38bdf8 !important;
    font-weight: 700 !important;
}

.latency-host-title, .target-name, .alert-target-title {
    color: #ffffff !important;
    font-weight: 600 !important;
}

.latency-track {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
}

.latency-fill {
    background: linear-gradient(90deg, #0d9488, #10b981) !important;
}

/* KPI Card Typography & Sparklines in Dark Mode */
.kpi-title {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}

.kpi-value {
    color: #ffffff !important;
    font-weight: 800 !important;
}

.kpi-subtext {
    font-weight: 600 !important;
}

.kpi-subtext-green { color: #34d399 !important; }
.kpi-subtext-blue { color: #60a5fa !important; }
.kpi-subtext-amber { color: #fbbf24 !important; }
.kpi-subtext-purple { color: #c084fc !important; }

/* Status Badges in Dark Mode */
.badge-online {
    background: #064e3b !important;
    color: #34d399 !important;
    border: 1px solid rgba(52, 211, 153, 0.4) !important;
}

.badge-degraded {
    background: #451a03 !important;
    color: #fbbf24 !important;
    border: 1px solid rgba(251, 191, 36, 0.4) !important;
}

.badge-offline, .badge-critical {
    background: #450a0a !important;
    color: #f87171 !important;
    border: 1px solid rgba(248, 113, 113, 0.4) !important;
}

.badge-warning {
    background: #451a03 !important;
    color: #fbbf24 !important;
    border: 1px solid rgba(251, 191, 36, 0.4) !important;
}

/* Native Buttons in Dark Mode */
.stButton > button,
div[data-testid="stBaseButton-secondary"] {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #475569 !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
}

.stButton > button:hover,
div[data-testid="stBaseButton-secondary"]:hover {
    background-color: #334155 !important;
    color: #ffffff !important;
    border-color: #94a3b8 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35) !important;
}

/* Top Navbar Buttons in Dark Mode */
button[key="top_theme_btn"],
div[data-testid="column"]:has(button[key="top_theme_btn"]) button {
    background: #1e293b !important;
    border: 1px solid #475569 !important;
    color: #fbbf24 !important;
}

button[key="top_theme_btn"]:hover,
div[data-testid="column"]:has(button[key="top_theme_btn"]) button:hover {
    background: #334155 !important;
    border-color: #94a3b8 !important;
    color: #fde047 !important;
}

/* Popover Buttons & Menus in Dark Mode */
div[data-testid="stPopover"] > button,
div[data-testid="column"]:last-child div[data-testid="stPopover"] > button {
    background: #1e293b !important;
    border: 1px solid #475569 !important;
    color: #ffffff !important;
}

div[data-testid="stPopover"] > button:hover,
div[data-testid="column"]:last-child div[data-testid="stPopover"] > button:hover {
    background: #334155 !important;
    border-color: #94a3b8 !important;
    color: #ffffff !important;
}

div[data-testid="stPopoverBody"],
div[data-testid="stPopoverContent"] {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    color: #f8fafc !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6) !important;
}

div[data-testid="stPopoverBody"] p,
div[data-testid="stPopoverBody"] span,
div[data-testid="stPopoverBody"] strong {
    color: #f8fafc !important;
}

/* Search Input in Dark Mode */
div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stTextInput"] div[data-baseweb="base-input"],
div[data-testid="stTextInput"] input {
    background-color: #1e293b !important;
    border-color: #475569 !important;
    color: #ffffff !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #94a3b8 !important;
}

/* Radio Group Segmented Pills in Dark Mode */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
    color: #cbd5e1 !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover p {
    color: #ffffff !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"],
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background: #0d9488 !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] p,
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Dataframe in Dark Mode */
[data-testid="stDataFrame"] {
    background: #111827 !important;
    border: 1px solid #334155 !important;
}

/* Code & Highlights */
code {
    background: #1e293b !important;
    color: #38bdf8 !important;
    border: 1px solid #334155 !important;
}

/* Select, Number inputs & Expanders */
div[data-baseweb="select"] > div,
div[data-testid="stNumberInput"] div[data-baseweb="input"] {
    background-color: #1e293b !important;
    border-color: #475569 !important;
    color: #ffffff !important;
}

[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid #334155 !important;
}

/* Auto-adapt SVG icon strokes to crisp white */
svg path[stroke="#0e2428"],
svg circle[stroke="#0e2428"],
svg line[stroke="#0e2428"],
svg polyline[stroke="#0e2428"],
svg rect[stroke="#0e2428"] {
    stroke: #f8fafc !important;
}
</style>
"""

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Root CSS Variables */
:root {
    --bg-main: #f0f4f8;
    --sidebar-bg: #0e2428;
    --sidebar-card: #153238;
    --card-bg: #ffffff;
    --card-border: rgba(226, 232, 240, 0.85);
    --card-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04), 0 2px 6px -2px rgba(15, 23, 42, 0.02);
    --text-primary: #0f172a;
    --text-secondary: #64748b;
    --text-muted: #94a3b8;
    --accent-mint: #10b981;
    --accent-teal: #0d9488;
    --accent-blue: #3b82f6;
    --accent-amber: #f59e0b;
    --accent-rose: #f43f5e;
    --accent-purple: #8b5cf6;
}

/* Global resets & typography */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* Main background */
.stApp {
    background-color: var(--bg-main) !important;
}

/* Streamlit Header / Footer adjustments - completely eliminate mouse interception */
header[data-testid="stHeader"],
.stAppHeader {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    pointer-events: none !important;
    visibility: hidden !important;
    z-index: -9999 !important;
    opacity: 0 !important;
}

footer {
    display: none !important;
}

/* Main content padding - clear top with explicit z-index */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
    position: relative !important;
    z-index: 10 !important;
}

/* Ensure universal top navbar controls are immediately clickable */
div[data-testid="stHorizontalBlock"]:first-child {
    position: relative !important;
    z-index: 999 !important;
}

/* Sidebar styling - Deep Teal matching mockup */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e2428 0%, #091a1d 100%) !important;
    color: #e2e8f0 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    padding-top: 0.5rem !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
}

/* Sidebar Brand Header */
.sidebar-brand-container {
    padding: 1rem 0.5rem 1.25rem 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 1rem;
}

.brand-icon-wrapper {
    width: 36px;
    height: 36px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #10b981;
}

.brand-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.brand-subtitle {
    font-size: 0.7rem;
    color: #7ba2a8;
    font-weight: 500;
    letter-spacing: 0.03em;
}

/* Sidebar Nav Items */
.nav-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 0.85rem;
    border-radius: 8px;
    color: #94a3b8;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.15s ease-in-out;
    margin-bottom: 0.25rem;
    text-decoration: none;
    cursor: pointer;
}

.nav-item:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #f8fafc;
}

.nav-item.active {
    background: #17373c !important;
    color: #ffffff !important;
    font-weight: 600;
    box-shadow: inset 3px 0 0 0 #10b981;
}

.nav-icon-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.nav-badge-red {
    background: #ef4444;
    color: #ffffff;
    font-size: 0.7rem;
    font-weight: 700;
    border-radius: 9999px;
    padding: 2px 7px;
    line-height: 1;
}

/* Sidebar bottom status & wave */
.sidebar-bottom-container {
    margin-top: 2rem;
    padding-top: 1rem;
    position: relative;
}

.sidebar-status-card {
    background: rgba(14, 45, 50, 0.85);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 10px;
    padding: 0.75rem 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}

.status-dot-pulse {
    width: 10px;
    height: 10px;
    background-color: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse-green 2s infinite;
}

@keyframes pulse-green {
    0% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

.status-text-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #ffffff;
    line-height: 1.2;
}

.status-text-sub {
    font-size: 0.7rem;
    color: #7ba2a8;
}

.sidebar-footer-version {
    font-size: 0.7rem;
    color: #52757a;
    padding-left: 0.25rem;
}

/* Top Navbar in Main Content */
.top-navbar-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}

.search-bar-box {
    display: flex;
    align-items: center;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 0.45rem 1rem;
    width: 380px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    gap: 0.6rem;
}

.search-bar-box input {
    border: none;
    outline: none;
    font-size: 0.85rem;
    color: #334155;
    width: 100%;
    background: transparent;
}

.search-bar-box input::placeholder {
    color: #94a3b8;
}

/* Explicit Streamlit text input styling override for search */
div[data-testid="stTextInput"] div[data-baseweb="input"],
div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    height: 38px !important;
}

div[data-testid="stTextInput"] input {
    background-color: #ffffff !important;
    color: #1e293b !important;
    font-size: 0.85rem !important;
    border-radius: 20px !important;
    padding: 0.35rem 0.85rem !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #94a3b8 !important;
}

.top-navbar-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.top-action-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    position: relative;
}

.notification-dot {
    position: absolute;
    top: 7px;
    right: 8px;
    width: 6px;
    height: 6px;
    background: #ef4444;
    border-radius: 50%;
}

.user-profile-capsule {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 0.25rem 0.75rem 0.25rem 0.35rem;
    border-radius: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    cursor: default;
}

.user-avatar-circle {
    width: 28px;
    height: 28px;
    background: #0e2428;
    color: #ffffff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
}

.user-name-text {
    font-size: 0.825rem;
    font-weight: 600;
    color: #1e293b;
}

/* Hero Greeting Section */
.hero-greeting-container {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}

.hero-subtitle-tag {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #64748b;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

.hero-main-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
    margin-bottom: 0.25rem;
}

.hero-subtext {
    font-size: 0.875rem;
    color: #64748b;
}

.hero-meta-badge {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 0.45rem 0.85rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.live-badge-pill {
    background: #ecfdf5;
    color: #059669;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.live-badge-pill::before {
    content: "";
    width: 6px;
    height: 6px;
    background: #10b981;
    border-radius: 50%;
}

/* Card Base */
.noc-card {
    background: var(--card-bg);
    border-radius: 12px;
    border: 1px solid var(--card-border);
    box-shadow: var(--card-shadow);
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.noc-card:hover {
    box-shadow: 0 6px 20px -2px rgba(15, 23, 42, 0.06);
}

/* KPI Cards */
.kpi-card {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid var(--card-border);
    box-shadow: var(--card-shadow);
    padding: 1rem 1.15rem 0.85rem 1.15rem;
    position: relative;
    overflow: hidden;
    height: 100%;
}

.kpi-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
}

.kpi-icon-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.kpi-icon-circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.kpi-icon-green {
    background: rgba(16, 185, 129, 0.12);
    color: #10b981;
}

.kpi-icon-blue {
    background: rgba(59, 130, 246, 0.12);
    color: #3b82f6;
}

.kpi-icon-amber {
    background: rgba(245, 158, 11, 0.12);
    color: #f59e0b;
}

.kpi-icon-purple {
    background: rgba(139, 92, 246, 0.12);
    color: #8b5cf6;
}

.kpi-title {
    font-size: 0.825rem;
    font-weight: 600;
    color: #475569;
}

.kpi-dots {
    color: #cbd5e1;
    cursor: default;
    font-size: 1rem;
    line-height: 1;
}

.kpi-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    margin-bottom: 0.35rem;
}

.kpi-subtext {
    font-size: 0.75rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 3px;
    margin-bottom: 0.5rem;
}

.kpi-subtext-green { color: #10b981; }
.kpi-subtext-blue { color: #0284c7; }
.kpi-subtext-amber { color: #d97706; }
.kpi-subtext-purple { color: #7c3aed; }

.sparkline-svg {
    width: 100%;
    height: 32px;
    overflow: visible;
}

/* Card Headers */
.card-title-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.card-title-left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-title-text {
    font-size: 0.95rem;
    font-weight: 700;
    color: #0f172a;
}

.view-all-link {
    font-size: 0.775rem;
    font-weight: 600;
    color: #0d9488;
    text-decoration: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 2px;
}

.view-all-link:hover {
    color: #047857;
    text-decoration: underline;
}

/* Target Status Items */
.target-status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.7rem 0.5rem;
    border-bottom: 1px solid #f1f5f9;
    transition: background 0.15s ease;
}

.target-status-row:last-child {
    border-bottom: none;
}

.target-status-row:hover {
    background: #f8fafc;
    border-radius: 8px;
}

.target-info-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.brand-logo-img {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.target-name-ip {
    display: flex;
    flex-direction: column;
}

.target-name {
    font-size: 0.825rem;
    font-weight: 600;
    color: #1e293b;
}

.target-ip {
    font-size: 0.725rem;
    color: #64748b;
}

.target-metric-capsule {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.metric-label-val {
    display: flex;
    flex-direction: column;
    text-align: right;
}

.metric-lbl {
    font-size: 0.65rem;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
}

.metric-v {
    font-size: 0.8rem;
    font-weight: 600;
    color: #334155;
}

/* Badges */
.badge-status {
    font-size: 0.725rem;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 12px;
    line-height: 1.2;
}

.badge-online {
    background: #ecfdf5;
    color: #059669;
}

.badge-degraded {
    background: #fef3c7;
    color: #d97706;
}

.badge-offline {
    background: #fee2e2;
    color: #dc2626;
}

.badge-critical {
    background: #fee2e2;
    color: #dc2626;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 12px;
}

.badge-warning {
    background: #fef3c7;
    color: #d97706;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 12px;
}

/* Alert Items */
.alert-item-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 0.65rem 0.25rem;
    border-bottom: 1px solid #f1f5f9;
}

.alert-item-row:last-child {
    border-bottom: none;
}

.alert-left-group {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
}

.alert-indicator-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}

.alert-dot-critical { background: #ef4444; }
.alert-dot-warning { background: #f59e0b; }

.alert-desc-group {
    display: flex;
    flex-direction: column;
}

.alert-target-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #1e293b;
}

.alert-meta-reason {
    font-size: 0.725rem;
    color: #64748b;
}

/* Recent Activity Micro Table */
.activity-row {
    display: grid;
    grid-template-columns: 45px 1fr 60px 50px 24px;
    align-items: center;
    padding: 0.45rem 0.25rem;
    font-size: 0.75rem;
    border-bottom: 1px solid #f8fafc;
}

.activity-row:last-child {
    border-bottom: none;
}

.activity-time { color: #64748b; font-weight: 500; }
.activity-name { color: #1e293b; font-weight: 600; }
.activity-rtt { color: #334155; font-weight: 500; text-align: right; }
.activity-loss { color: #64748b; text-align: right; }
.activity-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin: 0 auto;
}

/* Latency Horizontal Bar */
.latency-bar-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}

.latency-bar-row:last-child {
    margin-bottom: 0;
}

.latency-logo-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100px;
}

.latency-host-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #1e293b;
}

.latency-track {
    flex: 1;
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
}

.latency-fill {
    height: 100%;
    background: #0d9488;
    border-radius: 4px;
}

.latency-value-tag {
    width: 48px;
    text-align: right;
    font-size: 0.8rem;
    font-weight: 600;
    color: #475569;
}

/* Streamlit Horizontal Radio to Segmented Pills */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    background: #f1f5f9 !important;
    border-radius: 8px !important;
    padding: 3px !important;
    gap: 4px !important;
    width: fit-content !important;
    margin-left: auto !important;
    margin-bottom: 6px !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background: transparent !important;
    border-radius: 6px !important;
    padding: 4px 10px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}

/* Hide native radio circle */
div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Text inside radio label */
div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    margin: 0 !important;
}

/* Selected state */
div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"],
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background: #0e2428 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] p,
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p {
    color: #ffffff !important;
}

/* Sidebar Radio items styling */
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    background: transparent !important;
    width: 100% !important;
    gap: 4px !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    padding: 8px 12px !important;
    border-radius: 8px !important;
    width: 100% !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
    font-size: 0.85rem !important;
    color: #94a3b8 !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"],
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background: #17373c !important;
    box-shadow: inset 3px 0 0 0 #10b981 !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] p,
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Topology Map Container */
.map-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
}

.map-view-pills {
    display: flex;
    background: #f1f5f9;
    border-radius: 6px;
    padding: 2px;
}

.map-view-btn {
    font-size: 0.75rem;
    padding: 4px 12px;
    border-radius: 5px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    background: transparent;
    color: #64748b;
}

.map-view-btn.active {
    background: #0e2428;
    color: #ffffff;
}

.map-legend-bar {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.5rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

/* Streamlit Container (border=True) as Modern NOC Card */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid rgba(226, 232, 240, 0.85) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04), 0 2px 6px -2px rgba(15, 23, 42, 0.02) !important;
    padding: 1rem 1.15rem !important;
    margin-bottom: 0.85rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 6px 20px -2px rgba(15, 23, 42, 0.06) !important;
}

/* Ensure inner blocks don't add redundant margins */
[data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
}

.top-header-actions-bar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.85rem;
    padding-top: 2px;
}

/* Responsiveness Media Queries */
@media (max-width: 1200px) {
    .block-container {
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }
}

@media (max-width: 1024px) {
    /* Top action bar adapts */
    .top-header-actions-bar {
        justify-content: flex-start !important;
        margin-top: 0.25rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Responsive Horizontal Layout Wraps */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.75rem !important;
    }

    /* Stack main 2 columns (70% and 30%) on tablets & laptops */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
        margin-bottom: 0.5rem !important;
    }

    /* 4 KPI cards adapt to a neat 2x2 grid on tablets */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) > div[data-testid="column"] {
        width: calc(50% - 0.5rem) !important;
        flex: 1 1 calc(50% - 0.5rem) !important;
        min-width: calc(50% - 0.5rem) !important;
        max-width: calc(50% - 0.5rem) !important;
    }

    .top-navbar-wrapper {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 0.75rem !important;
    }

    .search-bar-box {
        width: 100% !important;
    }

    .hero-greeting-container {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 0.75rem !important;
    }
}

@media (max-width: 640px) {
    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        padding-top: 1rem !important;
    }

    /* All columns become 100% stacked on mobile phones */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) > div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
    }

    .top-header-actions-bar {
        justify-content: space-between !important;
        width: 100% !important;
    }

    .user-name-text {
        display: none !important; /* compact profile avatar on phones */
    }

    .hero-main-title {
        font-size: 1.35rem !important;
    }

    .kpi-value {
        font-size: 1.45rem !important;
    }

    .card-title-text {
        font-size: 0.85rem !important;
    }

    .target-status-row {
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }

    .target-metric-capsule {
        gap: 0.5rem !important;
        margin-left: auto !important;
    }
}

/* Circular Top Action Header Buttons (Theme & Bell icon) */
div[data-testid="column"]:has(button[key="top_theme_btn"]) button {
    width: 38px !important;
    height: 38px !important;
    min-height: 38px !important;
    max-height: 38px !important;
    min-width: 38px !important;
    max-width: 38px !important;
    border-radius: 50% !important;
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    font-size: 1.1rem !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}

div[data-testid="column"]:has(button[key="top_theme_btn"]) button:hover {
    border-color: #cbd5e1 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08) !important;
}

/* Popover Buttons */
div[data-testid="stPopover"] > button {
    cursor: pointer !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
}

/* User Profile Capsule Popover Button in Header */
.top-header-actions-bar div[data-testid="stPopover"] > button,
div[data-testid="column"]:last-child div[data-testid="stPopover"] > button {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 0.25rem 0.85rem !important;
    font-size: 0.825rem !important;
    font-weight: 600 !important;
    color: #1e293b !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    height: 38px !important;
    min-height: 38px !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    cursor: pointer !important;
}

.top-header-actions-bar div[data-testid="stPopover"] > button:hover,
div[data-testid="column"]:last-child div[data-testid="stPopover"] > button:hover {
    border-color: #cbd5e1 !important;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06) !important;
}

/* Card Header 'View All →' Links */
button[key^="view_all_"] {
    background: transparent !important;
    border: none !important;
    color: #0d9488 !important;
    font-size: 0.775rem !important;
    font-weight: 600 !important;
    padding: 0 !important;
    box-shadow: none !important;
    height: auto !important;
    min-height: unset !important;
    cursor: pointer !important;
}

button[key^="view_all_"]:hover {
    color: #047857 !important;
    text-decoration: underline !important;
    background: transparent !important;
}
</style>
"""

def get_custom_css(dark_mode: bool = False) -> str:
    if dark_mode:
        return BASE_CSS + "\n" + DARK_MODE_CSS
    return BASE_CSS

