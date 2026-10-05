import streamlit as st


APEX_SHELL_CSS = r"""
<style>

/* ============================================================
   APEX TERMINAL — GLOBAL SYSTEM
   ============================================================ */

:root {
    --apex-bg: #0A0D12;
    --apex-surface: #111620;
    --apex-surface-2: #171C26;
    --apex-elevated: #181F2C;
    --apex-interactive: #20293A;
    --apex-border: #263248;

    --apex-primary: #38BDF8;
    --apex-primary-dark: #0284C7;

    --apex-positive: #00D287;
    --apex-negative: #F43F5E;
    --apex-warning: #F59E0B;

    --apex-text: #F8FAFC;
    --apex-text-secondary: #94A3B8;
    --apex-text-muted: #475569;

    --apex-topbar: 56px;
    --apex-sidebar: 240px;
}

/* ============================================================
   GLOBAL
   ============================================================ */

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--apex-bg) !important;
    color: var(--apex-text) !important;
}

.stApp {
    font-family: "Inter", Arial, sans-serif !important;
}

/* ============================================================
   STREAMLIT HEADER
   IMPORTANT:
   DO NOT HIDE stHeader.
   The sidebar collapse/re-open button lives here.
   ============================================================ */

[data-testid="stHeader"] {
    height: var(--apex-topbar) !important;
    min-height: var(--apex-topbar) !important;
    background: transparent !important;
    z-index: 1000000 !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

/* Keep the toolbar parent alive for native sidebar state, but remove its
   unrelated Streamlit actions from the APEX header. */
[data-testid="stStatusWidget"],
[data-testid="stToolbarActions"],
[data-testid="stAppDeployButton"],
[data-testid="stMainMenu"] {
    display: none !important;
}

footer {
    display: none !important;
}

/* Keep Streamlit's native sidebar toggles available. */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarExpandButton"],
[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 1000001 !important;
}

[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarExpandButton"],
button[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"] {
    position: fixed !important;
    top: 12px !important;
    left: 12px !important;
    width: 34px !important;
    height: 34px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border: 1px solid rgba(62,72,79,.45) !important;
    border-radius: 6px !important;
    background: rgba(17,22,32,0.96) !important;
    color: var(--apex-primary) !important;
    box-shadow: 0 0 0 1px rgba(56,189,248,.08) !important;
}

[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarExpandButton"] button,
[data-testid="collapsedControl"] button {
    width: 100% !important;
    height: 100% !important;
    border: none !important;
    border-radius: 6px !important;
    background: transparent !important;
    color: var(--apex-primary) !important;
    font-family: Arial, sans-serif !important;
    font-size: 22px !important;
    line-height: 1 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
[data-testid="stSidebarExpandButton"] [data-testid="stIconMaterial"],
[data-testid="collapsedControl"] [data-testid="stIconMaterial"],
button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
    display: none !important;
}

[data-testid="stSidebarCollapseButton"] button::after,
[data-testid="collapsedControl"] button::after,
button[data-testid="stExpandSidebarButton"]::after,
[data-testid="stSidebarExpandButton"] button::after {
    content: "<";
    display: inline-block;
    font-family: Arial, sans-serif !important;
    font-size: 20px !important;
    line-height: 1 !important;
    color: var(--apex-primary) !important;
}

[data-testid="stSidebarExpandButton"] button::after,
button[data-testid="stExpandSidebarButton"]::after {
    content: ">";
}

[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarExpandButton"] button:hover,
[data-testid="collapsedControl"] button:hover,
button[data-testid="stExpandSidebarButton"]:hover {
    background: rgba(56,189,248,.08) !important;
    border-color: rgba(56,189,248,.4) !important;
}

/* ============================================================
   APEX TOP BAR
   ============================================================ */

.apex-topbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;

    height: var(--apex-topbar);

    background: var(--apex-surface);

    border-bottom: 1px solid rgba(62,72,79,.45);

    display: flex;
    align-items: center;

    padding: 0 14px;

    z-index: 999999;

    box-sizing: border-box;
}

.apex-topbar-left {
    width: 310px;
    min-width: 310px;

    display: flex;
    align-items: center;
}

.apex-brand {
    display: flex;
    align-items: center;
    gap: 8px;

    color: var(--apex-text);

    font-size: 12px;
    letter-spacing: 0.08em;
    font-weight: 600;

    white-space: nowrap;
}

.apex-brand-mark {
    display: none;
}

.apex-version {
    display: none;
}

.apex-topbar-center {
    flex: 1;

    display: flex;
    justify-content: center;

    min-width: 0;
}

.apex-market-strip {
    display: flex;
    align-items: center;
    gap: 9px;

    height: 30px;

    padding: 0 12px;

    border: 1px solid rgba(62,72,79,.35);
    border-radius: 4px;

    background: #171C26;

    font-family: "JetBrains Mono", monospace;

    font-size: 10px;

    white-space: nowrap;
}

.apex-live-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: var(--apex-positive);

    box-shadow: 0 0 0 2px rgba(0,210,135,.12);
}

.apex-live {
    color: var(--apex-positive);
    font-weight: 600;
}

.apex-muted {
    color: var(--apex-text-secondary);
}

.apex-primary-text {
    color: var(--apex-primary);
}

.apex-topbar-right {
    width: 240px;
    min-width: 240px;

    display: flex;
    align-items: center;
    justify-content: flex-end;

    gap: 8px;
}

.apex-top-button {
    height: 30px;

    padding: 0 9px;

    display: flex;
    align-items: center;

    border: 1px solid rgba(62,72,79,.40);
    border-radius: 4px;

    background: var(--apex-elevated);

    color: var(--apex-text-secondary);

    font-size: 10px;
    font-weight: 500;
}

.apex-top-button.active {
    border-color: rgba(56,189,248,.45);
    color: var(--apex-primary);
    background: rgba(56,189,248,.08);
}

.apex-user {
    display: flex;
    align-items: center;

    padding-left: 8px;

    border-left: 1px solid rgba(62,72,79,.30);
}

.apex-avatar {
    width: 28px;
    height: 28px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background: var(--apex-primary);

    color: var(--apex-bg);

    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 700;
}

/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    width: var(--apex-sidebar) !important;
    min-width: var(--apex-sidebar) !important;
    max-width: var(--apex-sidebar) !important;

    top: var(--apex-topbar) !important;
    height: calc(100vh - var(--apex-topbar)) !important;

    background: var(--apex-surface-2) !important;

    border-right: 1px solid rgba(62,72,79,.40) !important;

    z-index: 999998 !important;
}

section[data-testid="stSidebar"] > div {
    background: var(--apex-surface-2) !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding-top: 10px !important;
}

section[data-testid="stSidebar"] * {
    font-family: "Inter", Arial, sans-serif;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--apex-text) !important;
}

/* Navigation */

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 2px !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    min-height: 32px !important;

    padding: 0 8px !important;

    border-radius: 4px !important;

    color: var(--apex-text-secondary) !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: var(--apex-interactive) !important;
    color: var(--apex-text) !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: rgba(56,189,248,.08) !important;
    color: var(--apex-text) !important;
    border-left: 2px solid var(--apex-primary) !important;
    box-shadow: inset 0 0 0 1px rgba(56,189,248,.12) !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked):hover {
    background: rgba(56,189,248,.12) !important;
}

.apex-sidebar-news-link {
    display: block;
    margin: 0 0 9px;
    color: var(--apex-text-secondary);
    font-size: 11px;
    line-height: 1.35;
    text-decoration: none;
}

.apex-sidebar-news-link:hover {
    color: var(--apex-primary);
}

/* Hide radio circles */

section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* Sidebar inputs */

section[data-testid="stSidebar"] input {
    background: #090E18 !important;

    color: var(--apex-text) !important;

    border: 1px solid rgba(62,72,79,.45) !important;

    border-radius: 4px !important;

    font-family: "JetBrains Mono", monospace !important;

    font-size: 12px !important;
}

section[data-testid="stSidebar"] input:focus {
    border-color: var(--apex-primary) !important;

    box-shadow: 0 0 0 1px var(--apex-primary) !important;
}

/* Sidebar buttons */

section[data-testid="stSidebar"] button {
    border-radius: 4px !important;

    border: 1px solid rgba(62,72,79,.45) !important;

    background: var(--apex-elevated) !important;

    color: var(--apex-text) !important;
}

section[data-testid="stSidebar"] button:hover {
    background: var(--apex-interactive) !important;

    border-color: var(--apex-primary) !important;
}

section[data-testid="stSidebar"] button[kind="primary"] {
    background: var(--apex-primary) !important;

    border-color: var(--apex-primary) !important;

    color: var(--apex-bg) !important;

    font-weight: 600 !important;
}

/* ============================================================
   MAIN CONTENT
   ============================================================ */

.main {
    background: var(--apex-bg) !important;
}

.main .block-container {
    max-width: none !important;

    padding-top: 72px !important;
    padding-left: 12px !important;
    padding-right: 12px !important;
    padding-bottom: 24px !important;

    margin-left: 0 !important;
}

/* ============================================================
   HEADINGS — PREVENT CLIPPING
   ============================================================ */

h1,
h2,
h3,
h4,
h5,
h6 {
    font-family: "Inter", Arial, sans-serif !important;

    color: var(--apex-text) !important;

    overflow: visible !important;

    clip: auto !important;

    transform: none !important;
}

h1 {
    font-size: 32px !important;
    line-height: 40px !important;

    font-weight: 600 !important;

    letter-spacing: -0.02em !important;

    margin-top: 0 !important;
    margin-bottom: 8px !important;

    padding-top: 4px !important;
}

h2 {
    font-size: 20px !important;
    line-height: 28px !important;

    font-weight: 600 !important;

    margin-top: 16px !important;
}

h3 {
    font-size: 16px !important;
    line-height: 24px !important;
}

/* ============================================================
   BODY
   ============================================================ */

p {
    color: var(--apex-text-secondary);
}

[data-testid="stCaptionContainer"] {
    color: var(--apex-text-secondary) !important;

    font-size: 11px !important;
}

/* ============================================================
   METRICS
   ============================================================ */

[data-testid="stMetric"] {
    background: var(--apex-surface) !important;

    border: 1px solid var(--apex-border) !important;

    border-radius: 6px !important;

    padding: 10px !important;

    min-height: 82px !important;
}

[data-testid="stMetricLabel"] {
    color: var(--apex-text-secondary) !important;

    font-family: "JetBrains Mono", monospace !important;

    font-size: 10px !important;

    font-weight: 600 !important;

    letter-spacing: .08em !important;

    text-transform: uppercase !important;
}

[data-testid="stMetricValue"] {
    color: var(--apex-text) !important;

    font-family: "JetBrains Mono", monospace !important;

    font-size: 20px !important;

    font-weight: 600 !important;

    line-height: 24px !important;
}

/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    min-height: 32px !important;
    height: 32px !important;

    border-radius: 4px !important;

    border: 1px solid var(--apex-border) !important;

    background: var(--apex-elevated) !important;

    color: var(--apex-text) !important;

    font-family: "Inter", Arial, sans-serif !important;

    font-size: 12px !important;

    font-weight: 500 !important;
}

.stButton > button:hover {
    background: var(--apex-interactive) !important;

    border-color: var(--apex-primary) !important;
}

.stButton > button[kind="primary"] {
    background: var(--apex-primary) !important;

    border-color: var(--apex-primary) !important;

    color: var(--apex-bg) !important;

    font-weight: 600 !important;
}

/* ============================================================
   INPUTS
   ============================================================ */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"],
.stMultiSelect [data-baseweb="select"] {
    background: #090E18 !important;

    color: var(--apex-text) !important;

    border: 1px solid var(--apex-border) !important;

    border-radius: 4px !important;

    font-family: "JetBrains Mono", monospace !important;

    font-size: 12px !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--apex-primary) !important;

    box-shadow: 0 0 0 1px var(--apex-primary) !important;
}

/* ============================================================
   TABLES
   ============================================================ */

[data-testid="stDataFrame"] {
    border: 1px solid var(--apex-border) !important;

    border-radius: 6px !important;

    overflow: hidden !important;
}

[data-testid="stDataFrame"] * {
    font-variant-numeric: tabular-nums !important;
}

/* ============================================================
   TABS
   ============================================================ */

.stTabs [data-baseweb="tab-list"] {
    background: var(--apex-surface) !important;

    border-bottom: 1px solid var(--apex-border) !important;

    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--apex-text-secondary) !important;

    font-size: 12px !important;

    font-weight: 500 !important;
}

.stTabs [aria-selected="true"] {
    color: var(--apex-primary) !important;

    border-bottom: 2px solid var(--apex-primary) !important;
}

/* ============================================================
   PLOTLY
   ============================================================ */

[data-testid="stPlotlyChart"] {
    background: var(--apex-surface) !important;

    border: 1px solid var(--apex-border) !important;

    border-radius: 6px !important;

    overflow: hidden !important;
}

/* ============================================================
   EXPANDERS
   ============================================================ */

[data-testid="stExpander"] {
    background: var(--apex-surface) !important;

    border: 1px solid var(--apex-border) !important;

    border-radius: 6px !important;
}

/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 1024px) {

    :root {
        --apex-sidebar: 210px;
    }

    .apex-topbar-center {
        display: none;
    }

    .apex-topbar-left {
        width: auto;
        min-width: auto;
    }

    .apex-topbar-right {
        width: auto;
        min-width: auto;
    }

    h1 {
        font-size: 24px !important;
        line-height: 32px !important;
    }
}

@media (max-width: 700px) {

    section[data-testid="stSidebar"] {
        width: 190px !important;
        min-width: 190px !important;
    }

    .apex-topbar {
        padding: 0 8px;
    }

    .apex-version {
        display: none;
    }

    .apex-user {
        display: none;
    }

    .main .block-container {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }
}

</style>
"""


def apply_apex_shell(st):
    st.markdown(APEX_SHELL_CSS, unsafe_allow_html=True)

    # IMPORTANT:
    # Keep the HTML flush-left inside the markdown string.
    # Otherwise Streamlit interprets it as a code block.
    st.markdown(
        """<div class="apex-topbar">
<div class="apex-topbar-left">
<div class="apex-brand">
<span>FINANCIAL ANALYSIS TERMINAL</span>
</div>
</div>

<div class="apex-topbar-center">
<div class="apex-market-strip">
<span class="apex-live-dot"></span>
<span class="apex-live">LIVE</span>
<span class="apex-muted">NSE / BSE</span>
<span class="apex-muted">&bull;</span>
<span class="apex-primary-text">MARKET DATA</span>
<span class="apex-muted">&bull;</span>
<span class="apex-muted">YAHOO FINANCE</span>
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )
