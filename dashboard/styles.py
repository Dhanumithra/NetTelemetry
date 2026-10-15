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

/* KPI Icon Circles in Dark Mode - Vibrant with High Contrast */
.kpi-icon-green {
    background: rgba(16, 185, 129, 0.25) !important;
    color: #34d399 !important;
}
.kpi-icon-blue {
    background: rgba(59, 130, 246, 0.25) !important;
    color: #60a5fa !important;
}
.kpi-icon-amber {
    background: rgba(245, 158, 11, 0.25) !important;
    color: #fbbf24 !important;
}
.kpi-icon-purple {
    background: rgba(139, 92, 246, 0.25) !important;
    color: #c084fc !important;
}

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

.badge-unknown {
    background: #1e293b !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(148, 163, 184, 0.4) !important;
}

.badge-warning {
    background: #451a03 !important;
    color: #fbbf24 !important;
    border: 1px solid rgba(251, 191, 36, 0.4) !important;
}

/* ALL Secondary Buttons in Dark Mode (no jarring white boxes) */
button[data-testid="stBaseButton-secondary"],
.stButton > button,
div[data-testid="stButton"] > button,
div[data-testid="column"] button {
    background-color: #162032 !important;
    background: #162032 !important;
    color: #f1f5f9 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.15s ease !important;
}

button[data-testid="stBaseButton-secondary"]:hover,
.stButton > button:hover,
div[data-testid="stButton"] > button:hover,
div[data-testid="column"] button:hover {
    background-color: #1e293b !important;
    background: #1e293b !important;
    border-color: #64748b !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45) !important;
}

/* Primary Highlight Buttons in Dark Mode */
button[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: #0d9488 !important;
    background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%) !important;
    color: #ffffff !important;
    border: 1px solid #14b8a6 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(13, 148, 136, 0.4) !important;
    font-weight: 700 !important;
}

button[data-testid="stBaseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%) !important;
    border-color: #2dd4bf !important;
    box-shadow: 0 4px 14px rgba(20, 184, 166, 0.6) !important;
}

/* Popover Trigger Buttons in Dark Mode */
div[data-testid="stPopover"] > button,
.top-header-actions-bar div[data-testid="stPopover"] > button {
    background: #162032 !important;
    background-color: #162032 !important;
    border: 1px solid #334155 !important;
    color: #f8fafc !important;
    border-radius: 20px !important;
}

div[data-testid="stPopover"] > button:hover,
.top-header-actions-bar div[data-testid="stPopover"] > button:hover {
    background: #25334d !important;
    background-color: #25334d !important;
    border-color: #64748b !important;
    color: #ffffff !important;
}

/* FLOATING POPOVER CONTAINER IN DARK MODE (BaseWeb Portal) */
/* Force dark background on portal and eliminate white-on-white text */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] [data-testid="stPopoverBody"],
div[data-testid="stPopoverBody"],
div[data-testid="stPopoverContent"],
div[data-baseweb="popover"] div[role="dialog"] {
    background: #0f172a !important;
    background-color: #0f172a !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
    box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.85) !important;
}

/* Transparent nested inner blocks inside popover so background is solid #0f172a */
div[data-baseweb="popover"] div[data-testid="stVerticalBlock"],
div[data-baseweb="popover"] div[data-testid="stElementContainer"],
div[data-baseweb="popover"] div[data-testid="stMarkdownContainer"],
div[data-testid="stPopoverBody"] div[data-testid="stVerticalBlock"],
div[data-testid="stPopoverBody"] div[data-testid="stElementContainer"],
div[data-testid="stPopoverBody"] div[data-testid="stMarkdownContainer"] {
    background: transparent !important;
    background-color: transparent !important;
}

div[data-baseweb="popover"] p,
div[data-baseweb="popover"] span,
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] label,
div[data-testid="stPopoverBody"] p,
div[data-testid="stPopoverBody"] span,
div[data-testid="stPopoverBody"] li,
div[data-testid="stPopoverBody"] label {
    color: #e2e8f0 !important;
}

div[data-baseweb="popover"] strong,
div[data-baseweb="popover"] b,
div[data-testid="stPopoverBody"] strong,
div[data-testid="stPopoverBody"] b {
    color: #ffffff !important;
    font-weight: 700 !important;
}

div[data-baseweb="popover"] h1,
div[data-baseweb="popover"] h2,
div[data-baseweb="popover"] h3,
div[data-baseweb="popover"] h4,
div[data-testid="stPopoverBody"] h1,
div[data-testid="stPopoverBody"] h2,
div[data-testid="stPopoverBody"] h3,
div[data-testid="stPopoverBody"] h4 {
    color: #ffffff !important;
    font-weight: 700 !important;
}

div[data-baseweb="popover"] a,
div[data-testid="stPopoverBody"] a {
    color: #38bdf8 !important;
}

div[data-baseweb="popover"] code,
div[data-testid="stPopoverBody"] code {
    background: #1e293b !important;
    background-color: #1e293b !important;
    color: #38bdf8 !important;
    border: 1px solid #334155 !important;
    font-weight: 600 !important;
}

div[data-baseweb="popover"] button,
div[data-testid="stPopoverBody"] button {
    background-color: #1e293b !important;
    background: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #475569 !important;
    border-radius: 8px !important;
}

div[data-baseweb="popover"] button:hover,
div[data-testid="stPopoverBody"] button:hover {
    background-color: #334155 !important;
    background: #334155 !important;
    color: #ffffff !important;
    border-color: #94a3b8 !important;
}

div[data-baseweb="popover"] hr,
div[data-testid="stPopoverBody"] hr {
    border-color: #334155 !important;
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

/* Dialog / Modal Dark Mode */
div[data-testid="stDialog"] > div {
    background-color: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    color: #f8fafc !important;
}

div[data-testid="stDialog"] h2 {
    color: #ffffff !important;
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

/* Streamlit Header / App Header adjustments */
header[data-testid="stHeader"],
.stAppHeader {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    pointer-events: none !important;
    border: none !important;
    z-index: 99999 !important;
}

/* Ensure sidebar collapse toggle button is permanently visible, stylish & clickable */
[data-testid="collapsedControl"],
header[data-testid="stHeader"] button,
button[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    position: fixed !important;
    top: 0.85rem !important;
    left: 0.85rem !important;
    z-index: 999999 !important;
    background: #0e2428 !important;
    color: #10b981 !important;
    border: 1px solid rgba(16, 185, 129, 0.4) !important;
    border-radius: 8px !important;
    width: 38px !important;
    height: 38px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

[data-testid="collapsedControl"]:hover,
header[data-testid="stHeader"] button:hover,
button[data-testid="stSidebarCollapseButton"]:hover {
    background: #17373c !important;
    border-color: #10b981 !important;
    color: #ffffff !important;
    transform: scale(1.05) !important;
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4) !important;
}

[data-testid="collapsedControl"] svg,
button[data-testid="stSidebarCollapseButton"] svg {
    fill: #10b981 !important;
    stroke: #10b981 !important;
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

/* =========================================================
   NETTELEMETRY SIDEBAR DESIGN SYSTEM (Production SaaS)
   ========================================================= */

/* Sidebar Base Canvas - Deep Blue-Green #0B1F24 */
[data-testid="stSidebar"] {
    background: #0B1F24 !important;
    background-color: #0B1F24 !important;
    color: #F1F5F9 !important;
    border-right: 1px solid rgba(20, 184, 166, 0.15) !important;
    padding-top: 0.6rem !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

/* Force High-Contrast Readable Text for all elements inside Sidebar */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] div[data-testid="stText"] {
    color: #F1F5F9 !important;
}

/* Brand Header */
[data-testid="stSidebar"] .sidebar-brand-container,
.sidebar-brand-container {
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
    padding: 0.35rem 0.25rem 0.5rem 0.25rem !important;
}

[data-testid="stSidebar"] .brand-logo-symbol,
.brand-logo-symbol {
    font-size: 0 !important;
    line-height: 0 !important;
    color: transparent !important;
    display: inline-block !important;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    border-radius: 9px !important;
    background-color: #0D2E32 !important;
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20width%3D%2736%27%20height%3D%2736%27%20viewBox%3D%270%200%2036%2036%27%20fill%3D%27none%27%3E%20%3Crect%20width%3D%2736%27%20height%3D%2736%27%20rx%3D%279%27%20fill%3D%27%230D2E32%27%20stroke%3D%27%2314B8A6%27%20stroke-width%3D%271.5%27/%3E%20%3Cline%20x1%3D%275%27%20y1%3D%2718%27%20x2%3D%2731%27%20y2%3D%2718%27%20stroke%3D%27%23134E4A%27%20stroke-width%3D%271.2%27%20stroke-dasharray%3D%272%202%27/%3E%20%3Cpolyline%20points%3D%276%2C18%2010%2C18%2014%2C9%2018.5%2C27%2023%2C12%2026.5%2C18%2030%2C18%27%20fill%3D%27none%27%20stroke%3D%27%232DD4BF%27%20stroke-width%3D%272.2%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27/%3E%20%3Ccircle%20cx%3D%2714%27%20cy%3D%279%27%20r%3D%272.4%27%20fill%3D%27%2314B8A6%27%20stroke%3D%27%230B1F24%27%20stroke-width%3D%271.4%27/%3E%20%3Ccircle%20cx%3D%2718.5%27%20cy%3D%2727%27%20r%3D%272.4%27%20fill%3D%27%2310B981%27%20stroke%3D%27%230B1F24%27%20stroke-width%3D%271.4%27/%3E%20%3Ccircle%20cx%3D%2723%27%20cy%3D%2712%27%20r%3D%272%27%20fill%3D%27%2334D399%27%20stroke%3D%27%230B1F24%27%20stroke-width%3D%271.2%27/%3E%20%3C/svg%3E") !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    box-shadow: 0 2px 10px rgba(20, 184, 166, 0.28) !important;
    flex-shrink: 0 !important;
}

.brand-text-block {
    display: flex;
    flex-direction: column;
    justify-content: center;
    line-height: 1.15;
}

[data-testid="stSidebar"] .brand-title,
.brand-title {
    font-size: 1.18rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    letter-spacing: -0.02em !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}

[data-testid="stSidebar"] .brand-subtitle,
.brand-subtitle {
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    color: #94A3B8 !important;
    letter-spacing: 0.025em !important;
    margin-top: 2px !important;
}

/* Refined Dark Teal Dividers */
.sidebar-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.07);
    border-bottom: 1px solid rgba(20, 184, 166, 0.12);
    margin: 0.65rem 0 0.75rem 0;
}

/* =========================================================
   PRIMARY SIDEBAR NAVIGATION BUTTONS
   ========================================================= */

/* Force consistent layout and dimensions */
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] {
    margin-bottom: 2px !important;
    width: 100% !important;
}

[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: left !important;
    width: 100% !important;
    height: 42px !important;
    min-height: 42px !important;
    padding: 0.55rem 0.85rem !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s ease-in-out !important;
}

/* Ensure inner label wrapper is strictly left aligned next to icon */
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button > div,
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: left !important;
    margin: 0 !important;
    padding: 0 !important;
    width: auto !important;
    flex: 1 1 auto !important;
}

[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button div[data-testid="stMarkdownContainer"] p {
    text-align: left !important;
    margin: 0 !important;
    padding: 0 !important;
    white-space: nowrap !important;
}

/* Inactive Navigation Item */
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button[data-testid="stBaseButton-secondary"],
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button:not([data-testid="stBaseButton-primary"]) {
    background: transparent !important;
    background-color: transparent !important;
    color: #E2E8F0 !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button[data-testid="stBaseButton-secondary"] p,
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button:not([data-testid="stBaseButton-primary"]) p {
    color: #E2E8F0 !important;
    font-weight: 500 !important;
    margin: 0 !important;
}

/* Inactive Hover State */
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button[data-testid="stBaseButton-secondary"]:hover,
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button:not([data-testid="stBaseButton-primary"]):hover {
    background: rgba(255, 255, 255, 0.07) !important;
    background-color: rgba(255, 255, 255, 0.07) !important;
    color: #FFFFFF !important;
    border-color: rgba(20, 184, 166, 0.2) !important;
}

[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button[data-testid="stBaseButton-secondary"]:hover p,
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button:not([data-testid="stBaseButton-primary"]):hover p {
    color: #FFFFFF !important;
}

/* Active Navigation Item - Subtle Teal Surface #0F766E */
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button[data-testid="stBaseButton-primary"] {
    background: #0F766E !important;
    background-color: #0F766E !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(20, 184, 166, 0.55) !important;
    font-weight: 600 !important;
    box-shadow: inset 3px 0 0 0 #14B8A6, 0 2px 8px rgba(15, 118, 110, 0.35) !important;
}

[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button[data-testid="stBaseButton-primary"] p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button[data-testid="stBaseButton-primary"]:hover {
    background: #115E59 !important;
    background-color: #115E59 !important;
    border-color: #14B8A6 !important;
    color: #FFFFFF !important;
}

/* Lucide Vector Icons via CSS Mask */
[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button::before {
    content: "";
    display: inline-block;
    width: 18px;
    height: 18px;
    margin-right: 12px;
    flex-shrink: 0;
    background-color: #94A3B8;
    -webkit-mask-size: contain;
    -webkit-mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-size: contain;
    mask-repeat: no-repeat;
    mask-position: center;
    transition: background-color 0.15s ease;
}

[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button:hover::before {
    background-color: #FFFFFF;
}

[data-testid="stSidebar"] div[class*="st-key-sidebar_nav_"] button[data-testid="stBaseButton-primary"]::before {
    background-color: #FFFFFF;
}

/* Individual Lucide Icon Definitions */
.st-key-sidebar_nav_Dashboard button::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='7' height='9' x='3' y='3' rx='1'/%3E%3Crect width='7' height='5' x='14' y='3' rx='1'/%3E%3Crect width='7' height='9' x='14' y='12' rx='1'/%3E%3Crect width='7' height='5' x='3' y='16' rx='1'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='7' height='9' x='3' y='3' rx='1'/%3E%3Crect width='7' height='5' x='14' y='3' rx='1'/%3E%3Crect width='7' height='9' x='14' y='12' rx='1'/%3E%3Crect width='7' height='5' x='3' y='16' rx='1'/%3E%3C/svg%3E");
}

.st-key-sidebar_nav_Targets button::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='12' cy='12' r='6'/%3E%3Ccircle cx='12' cy='12' r='2'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='12' cy='12' r='6'/%3E%3Ccircle cx='12' cy='12' r='2'/%3E%3C/svg%3E");
}

.st-key-sidebar_nav_Measurements button::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='20' x2='18' y2='10'/%3E%3Cline x1='12' y1='20' x2='12' y2='4'/%3E%3Cline x1='6' y1='20' x2='6' y2='14'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='20' x2='18' y2='10'/%3E%3Cline x1='12' y1='20' x2='12' y2='4'/%3E%3Cline x1='6' y1='20' x2='6' y2='14'/%3E%3C/svg%3E");
}

.st-key-sidebar_nav_Analytics button::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'/%3E%3Cpolyline points='17 6 23 6 23 12'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'/%3E%3Cpolyline points='17 6 23 6 23 12'/%3E%3C/svg%3E");
}

.st-key-sidebar_nav_Alerts button::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9'/%3E%3Cpath d='M13.73 21a2 2 0 0 1-3.46 0'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9'/%3E%3Cpath d='M13.73 21a2 2 0 0 1-3.46 0'/%3E%3C/svg%3E");
}

.st-key-sidebar_nav_Reports button::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3Cline x1='16' y1='13' x2='8' y2='13'/%3E%3Cline x1='16' y1='17' x2='8' y2='17'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3Cline x1='16' y1='13' x2='8' y2='13'/%3E%3Cline x1='16' y1='17' x2='8' y2='17'/%3E%3C/svg%3E");
}

.st-key-sidebar_nav_Settings button::before {
    -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z'/%3E%3C/svg%3E");
}

/* =========================================================
   TELEMETRY ENGINE SECTION
   ========================================================= */

[data-testid="stSidebar"] .sidebar-section-header,
.sidebar-section-header {
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #94A3B8 !important;
    margin-bottom: 0.45rem !important;
    padding: 0 0.2rem !important;
}



/* Telemetry Live Status Card */
.telemetry-live-card {
    background: rgba(14, 37, 43, 0.85);
    border: 1px solid rgba(20, 184, 166, 0.25);
    border-radius: 8px;
    padding: 0.55rem 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 0.45rem;
}

.telemetry-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.status-dot-active {
    background-color: #10B981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse-green 2s infinite;
}

.status-dot-paused {
    background-color: #94A3B8;
}

.telemetry-live-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #FFFFFF;
    line-height: 1.2;
}

.telemetry-live-sub {
    font-size: 0.68rem;
    color: #94A3B8;
}

/* Telemetry Actions */
[data-testid="stSidebar"] div.st-key-sidebar_probe_all {
    margin-top: 0.35rem !important;
    margin-bottom: 0.35rem !important;
    width: 100% !important;
}

[data-testid="stSidebar"] div.st-key-sidebar_probe_all button {
    background: #0D9488 !important;
    background-color: #0D9488 !important;
    color: #FFFFFF !important;
    border: 1px solid #14B8A6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.825rem !important;
    height: 38px !important;
    min-height: 38px !important;
    padding: 0.4rem 0.75rem !important;
    box-shadow: 0 2px 6px rgba(13, 148, 136, 0.3) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    width: 100% !important;
}

[data-testid="stSidebar"] div.st-key-sidebar_probe_all button p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] div.st-key-sidebar_probe_all button:hover {
    background: #14B8A6 !important;
    background-color: #14B8A6 !important;
    border-color: #2DD4BF !important;
    box-shadow: 0 3px 10px rgba(20, 184, 166, 0.45) !important;
}

[data-testid="stSidebar"] div.st-key-sidebar_refresh_data {
    margin-bottom: 0.35rem !important;
    width: 100% !important;
}

[data-testid="stSidebar"] div.st-key-sidebar_refresh_data button {
    background: rgba(255, 255, 255, 0.04) !important;
    background-color: rgba(255, 255, 255, 0.04) !important;
    color: #CBD5E1 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.825rem !important;
    height: 38px !important;
    min-height: 38px !important;
    padding: 0.4rem 0.75rem !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    width: 100% !important;
}

[data-testid="stSidebar"] div.st-key-sidebar_refresh_data button p {
    color: #CBD5E1 !important;
    font-weight: 500 !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] div.st-key-sidebar_refresh_data button:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
    border-color: rgba(255, 255, 255, 0.22) !important;
}

/* Sidebar Toggle & Select Input Styling */
[data-testid="stSidebar"] div[data-testid="stCheckbox"] label p {
    color: #E2E8F0 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] div[data-testid="stSelectbox"] label p {
    color: #94A3B8 !important;
    font-size: 0.725rem !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #0E2A30 !important;
    border: 1px solid rgba(20, 184, 166, 0.25) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: #E2E8F0 !important;
}

/* Bottom Soundwave & Status Card */
.sidebar-bottom-container {
    margin-top: 0.85rem;
    padding-top: 0.35rem;
    position: relative;
}

.sidebar-status-card {
    background: rgba(14, 37, 43, 0.85);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}

.status-dot-pulse {
    width: 9px;
    height: 9px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse-green 2s infinite;
}

.status-text-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #FFFFFF;
    line-height: 1.2;
}

.status-text-sub {
    font-size: 0.68rem;
    color: #94A3B8;
}

.sidebar-footer-version {
    font-size: 0.68rem;
    color: #64748B;
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

.badge-unknown {
    background: #f1f5f9;
    color: #64748b;
    border: 1px solid #cbd5e1;
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

/* Secondary & Native Button Base Styles (Light Mode) */
button[data-testid="stBaseButton-secondary"],
.stButton > button {
    background-color: #ffffff !important;
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #1e293b !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.15s ease !important;
}

button[data-testid="stBaseButton-secondary"]:hover,
.stButton > button:hover {
    background-color: #f8fafc !important;
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
}

/* Primary Highlight Buttons (Light Mode) */
button[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: #0e2428 !important;
    background-color: #0e2428 !important;
    color: #ffffff !important;
    border: 1px solid #17373c !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 6px rgba(14, 36, 40, 0.25) !important;
    font-weight: 700 !important;
}

button[data-testid="stBaseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: #17373c !important;
    background-color: #17373c !important;
    color: #ffffff !important;
}

/* Popover Trigger Buttons Base */
div[data-testid="stPopover"] > button,
.top-header-actions-bar div[data-testid="stPopover"] > button {
    cursor: pointer !important;
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
    transition: all 0.15s ease !important;
}

div[data-testid="stPopover"] > button:hover,
.top-header-actions-bar div[data-testid="stPopover"] > button:hover {
    border-color: #cbd5e1 !important;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06) !important;
}

/* FLOATING POPOVER CONTAINER IN LIGHT MODE (BaseWeb Portal) */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] [data-testid="stPopoverBody"],
div[data-testid="stPopoverBody"],
div[data-testid="stPopoverContent"],
div[data-baseweb="popover"] div[role="dialog"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    color: #0f172a !important;
    box-shadow: 0 16px 36px -4px rgba(15, 23, 42, 0.12) !important;
}

div[data-baseweb="popover"] div[data-testid="stVerticalBlock"],
div[data-baseweb="popover"] div[data-testid="stElementContainer"],
div[data-baseweb="popover"] div[data-testid="stMarkdownContainer"],
div[data-testid="stPopoverBody"] div[data-testid="stVerticalBlock"],
div[data-testid="stPopoverBody"] div[data-testid="stElementContainer"],
div[data-testid="stPopoverBody"] div[data-testid="stMarkdownContainer"] {
    background: transparent !important;
    background-color: transparent !important;
}

div[data-baseweb="popover"] p,
div[data-baseweb="popover"] span,
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] label,
div[data-testid="stPopoverBody"] p,
div[data-testid="stPopoverBody"] span,
div[data-testid="stPopoverBody"] li,
div[data-testid="stPopoverBody"] label {
    color: #1e293b !important;
}

div[data-baseweb="popover"] strong,
div[data-baseweb="popover"] b,
div[data-testid="stPopoverBody"] strong,
div[data-testid="stPopoverBody"] b {
    color: #0f172a !important;
    font-weight: 700 !important;
}

div[data-baseweb="popover"] h1,
div[data-baseweb="popover"] h2,
div[data-baseweb="popover"] h3,
div[data-baseweb="popover"] h4,
div[data-testid="stPopoverBody"] h1,
div[data-testid="stPopoverBody"] h2,
div[data-testid="stPopoverBody"] h3,
div[data-testid="stPopoverBody"] h4 {
    color: #0f172a !important;
    font-weight: 700 !important;
}

div[data-baseweb="popover"] code,
div[data-testid="stPopoverBody"] code {
    background: #f1f5f9 !important;
    background-color: #f1f5f9 !important;
    color: #0d9488 !important;
    border: 1px solid #e2e8f0 !important;
    font-weight: 600 !important;
}

div[data-baseweb="popover"] a,
div[data-testid="stPopoverBody"] a {
    color: #0d9488 !important;
}

div[data-baseweb="popover"] button,
div[data-testid="stPopoverBody"] button {
    background-color: #f8fafc !important;
    background: #f8fafc !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
}

div[data-baseweb="popover"] button:hover,
div[data-testid="stPopoverBody"] button:hover {
    background-color: #f1f5f9 !important;
    background: #f1f5f9 !important;
    color: #0f172a !important;
    border-color: #cbd5e1 !important;
}

div[data-baseweb="popover"] hr,
div[data-testid="stPopoverBody"] hr {
    border-color: #e2e8f0 !important;
}

/* Dialog / Modal Confirmation Styling */
div[data-testid="stDialog"] > div {
    border-radius: 12px !important;
    border: 1px solid rgba(226, 232, 240, 0.9) !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05) !important;
}

div[data-testid="stDialog"] h2 {
    font-weight: 700 !important;
    font-size: 1.25rem !important;
    color: var(--text-primary) !important;
}
</style>
"""

def get_custom_css(dark_mode: bool = False) -> str:
    if dark_mode:
        return BASE_CSS + "\n" + DARK_MODE_CSS
    return BASE_CSS

