from pathlib import Path
from html import escape
import streamlit as st
import pandas as pd
import numpy as np

THEME_CSS = r"""
<style>

:root {
    --apex-bg: #0A0D12;
    --apex-surface: #111620;
    --apex-elevated: #181F2C;
    --apex-interactive: #20293A;
    --apex-border: #263248;

    --apex-primary: #38BDF8;
    --apex-primary-dark: #0284C7;

    --apex-positive: #00D287;
    --apex-positive-dark: #10B981;

    --apex-negative: #F43F5E;
    --apex-negative-dark: #EF4444;

    --apex-warning: #F59E0B;

    --apex-text: #F8FAFC;
    --apex-text-secondary: #94A3B8;
    --apex-text-muted: #475569;

    --apex-radius-sm: 4px;
    --apex-radius-md: 6px;
}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

.stApp {
    background: var(--apex-bg);
    color: var(--apex-text);
    font-family: 'Inter', sans-serif;
}

.main,
.block-container {
    color: var(--apex-text);
}

.block-container {
    padding-top: calc(var(--apex-topbar, 56px) + 1rem);
    padding-bottom: 1rem;
    padding-left: 0.75rem;
    padding-right: 0.75rem;
    max-width: none;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: var(--apex-text) !important;
}

h1 {
    font-size: 32px !important;
    line-height: 40px !important;
    font-weight: 600 !important;
}

h2 {
    font-size: 20px !important;
    line-height: 28px !important;
    font-weight: 600 !important;
}

h3 {
    font-size: 16px !important;
    line-height: 24px !important;
    font-weight: 600 !important;
}

p, label, span, div {
    font-family: 'Inter', sans-serif;
}

.apex-number,
.apex-metric,
.apex-price,
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-variant-numeric: tabular-nums;
}

section[data-testid="stSidebar"] {
    background: var(--apex-surface);
    border-right: 1px solid var(--apex-border);
}

section[data-testid="stSidebar"] > div {
    background: var(--apex-surface);
}

section[data-testid="stSidebar"] * {
    color: var(--apex-text);
}

section[data-testid="stSidebar"] button {
    border-radius: var(--apex-radius-sm);
    border: 1px solid transparent;
    background: transparent;
    color: var(--apex-text-secondary);
    transition: all 120ms ease;
}

section[data-testid="stSidebar"] button:hover {
    background: var(--apex-interactive);
    border-color: var(--apex-border);
    color: var(--apex-text);
}

.stButton > button {
    min-height: 32px;
    height: 32px;
    border-radius: var(--apex-radius-sm);
    border: 1px solid var(--apex-border);
    background: var(--apex-elevated);
    color: var(--apex-text);
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    transition: background 120ms ease,
                border-color 120ms ease,
                color 120ms ease;
}

.stButton > button:hover {
    background: var(--apex-interactive);
    border-color: var(--apex-primary);
    color: var(--apex-text);
}

.stButton > button[kind="primary"] {
    background: var(--apex-primary);
    border-color: var(--apex-primary);
    color: var(--apex-bg);
    font-weight: 600;
}

.stButton > button[kind="primary"]:hover {
    background: var(--apex-primary-dark);
    border-color: var(--apex-primary-dark);
}

.stTextInput input,
.stNumberInput input,
.stSelectbox [data-baseweb="select"],
.stMultiSelect [data-baseweb="select"] {
    background: var(--apex-bg) !important;
    border: 1px solid var(--apex-border) !important;
    border-radius: var(--apex-radius-sm) !important;
    color: var(--apex-text) !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 32px;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--apex-primary) !important;
    box-shadow: 0 0 0 1px var(--apex-primary) !important;
}

.stSelectbox *,
.stMultiSelect * {
    color: var(--apex-text) !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: var(--apex-elevated) !important;
    border: 1px solid var(--apex-border) !important;
}

[role="option"] {
    background: var(--apex-elevated) !important;
    color: var(--apex-text) !important;
}

[role="option"]:hover {
    background: var(--apex-interactive) !important;
}

[data-testid="stMetric"] {
    background: var(--apex-surface);
    border: 1px solid var(--apex-border);
    border-radius: 12px;
    padding: 0.85rem 0.9rem;
    background: linear-gradient(180deg, rgba(17,22,32,0.96), rgba(17,22,32,0.9));
    box-shadow: inset 0 1px rgba(255,255,255,0.02);
}

[data-testid="stMetric"]:hover {
    border-color: rgba(56, 189, 248, 0.5);
}

[data-testid="stMetricLabel"] {
    color: var(--apex-text-secondary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: var(--apex-text) !important;
    font-size: 20px !important;
    font-weight: 600 !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--apex-border) !important;
    border-radius: var(--apex-radius-md) !important;
    background: rgba(17, 22, 32, 0.72) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] {
    background: rgba(10, 13, 18, 0.42);
    border-color: rgba(38, 50, 72, 0.85);
    border-radius: var(--apex-radius-sm);
    padding: 0.6rem 0.7rem;
}

[data-testid="stVerticalBlockBorderWrapper"] h3 {
    margin-bottom: 0.15rem;
}

[data-testid="stCaptionContainer"] {
    color: var(--apex-text-secondary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.04em;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--apex-border);
    border-radius: 12px;
    overflow: hidden;
    background: rgba(17,22,32,0.92);
}

/* Keep the Dashboard's two analytical columns shrinkable at narrow widths. */
.st-key-dashboard_sections [data-testid="stColumn"] {
    min-width: 0 !important;
}

.st-key-dashboard_sections [data-testid="stDataFrame"] {
    max-width: 100% !important;
}

@media (max-width: 900px) {
    .st-key-dashboard_sections [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }

    .st-key-dashboard_sections [data-testid="stColumn"] {
        flex-basis: 100% !important;
        width: 100% !important;
    }
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--apex-surface);
    border-bottom: 1px solid var(--apex-border);
}

.stTabs [data-baseweb="tab"] {
    color: var(--apex-text-secondary);
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.stTabs [aria-selected="true"] {
    color: var(--apex-primary) !important;
    border-bottom: 2px solid var(--apex-primary);
}

hr {
    border-color: var(--apex-border) !important;
}

[data-testid="stAlert"] {
    border-radius: var(--apex-radius-sm);
    border: 1px solid var(--apex-border);
}

[data-testid="stExpander"] {
    background: var(--apex-surface);
    border: 1px solid var(--apex-border);
    border-radius: var(--apex-radius-md);
}

.stCheckbox label,
.stRadio label {
    color: var(--apex-text-secondary) !important;
}

.stDownloadButton > button {
    background: var(--apex-elevated);
    border: 1px solid var(--apex-border);
    border-radius: var(--apex-radius-sm);
    color: var(--apex-text);
}

.stDownloadButton > button:hover {
    background: var(--apex-interactive);
    border-color: var(--apex-primary);
}

[data-testid="stPlotlyChart"] {
    background: var(--apex-surface);
    border: 1px solid var(--apex-border);
    border-radius: var(--apex-radius-md);
    overflow: hidden;
}

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--apex-bg);
}

::-webkit-scrollbar-thumb {
    background: var(--apex-border);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--apex-text-muted);
}

@media (max-width: 1024px) {
    h1 {
        font-size: 24px !important;
        line-height: 32px !important;
    }

    .block-container {
        padding-top: calc(var(--apex-topbar, 56px) + 1rem);
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
}

/* ============================================================
   APEX TERMINAL HEADER
   ============================================================ */

.apex-header {
    width: 100%;
    min-height: 76px;
    box-sizing: border-box;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 14px 20px;

    margin: 0 0 18px 0;

    background: #111620;
    border: 1px solid #263248;
    border-radius: 6px;

    overflow: hidden;
}

.apex-header-left {
    display: flex;
    align-items: center;
    min-width: 0;
}

.apex-brand-mark {
    width: 42px;
    height: 42px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin-right: 12px;

    background: #0F172A;
    border: 1px solid #334155;
    border-radius: 8px;

    flex-shrink: 0;
}

.apex-brand-chevron {
    font-family: 'JetBrains Mono', monospace;
    font-size: 21px;
    font-weight: 600;

    background: linear-gradient(
        135deg,
        #38BDF8,
        #0284C7,
        #00D287
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.apex-brand-text {
    min-width: 0;
}

.apex-brand-title {
    color: #F8FAFC;

    font-family: 'Inter', sans-serif;

    font-size: 22px;
    line-height: 28px;

    font-weight: 600;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.apex-brand-subtitle {
    color: #94A3B8;

    font-family: 'Inter', sans-serif;

    font-size: 11px;
    line-height: 17px;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.apex-header-right {
    display: flex;
    align-items: center;
    gap: 18px;

    margin-left: 20px;

    flex-shrink: 0;
}

.apex-market-status {
    display: flex;
    align-items: center;
    gap: 7px;

    color: #94A3B8;

    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;

    white-space: nowrap;
}

.apex-status-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #00D287;

    box-shadow: 0 0 8px rgba(0, 210, 135, 0.45);
}

.apex-header-time {
    color: #475569;

    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;

    white-space: nowrap;
}

@media (max-width: 900px) {

    .apex-header {
        padding: 12px 14px;
    }

    .apex-brand-title {
        font-size: 18px;
    }

    .apex-header-right {
        gap: 8px;
    }

    .apex-header-time {
        display: none;
    }
}

@media (max-width: 600px) {

    .apex-header {
        min-height: 62px;
    }

    .apex-brand-mark {
        width: 34px;
        height: 34px;
        margin-right: 8px;
    }

    .apex-brand-title {
        font-size: 16px;
        line-height: 22px;
    }

    .apex-brand-subtitle {
        font-size: 9px;
    }

    .apex-market-status {
        display: none;
    }
}

.apex-page-header {
    width: 100%;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 12px;
    padding: 4px 0 12px;
    margin: 0 0 12px;
    border-bottom: 1px solid rgba(38, 50, 72, 0.9);
    box-sizing: border-box;
}

.apex-page-kicker {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--apex-primary);
    margin-bottom: 6px;
}

.apex-page-title-wrap {
    min-width: 0;
    flex: 1;
}

.apex-page-title {
    margin: 0;
    font-size: 28px !important;
    line-height: 1.3 !important;
    letter-spacing: -0.02em;
    overflow: visible !important;
    white-space: normal;
}

.apex-page-subtitle {
    margin-top: 4px;
    color: var(--apex-text-secondary);
    font-size: 13px;
    line-height: 1.5;
}

.apex-page-meta {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 8px;
    color: var(--apex-text-secondary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    line-height: 1.5;
    text-transform: uppercase;
    white-space: nowrap;
}

.apex-status-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    border: 1px solid rgba(56, 189, 248, 0.5);
    background: rgba(56, 189, 248, 0.08);
    color: var(--apex-primary);
    padding: 4px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.apex-status-badge.positive {
    border-color: rgba(0, 210, 135, 0.45);
    background: rgba(0, 210, 135, 0.08);
    color: var(--apex-positive);
}

.apex-status-badge.negative {
    border-color: rgba(244, 63, 94, 0.45);
    background: rgba(244, 63, 94, 0.08);
    color: var(--apex-negative);
}

.apex-status-badge.warning {
    border-color: rgba(245, 158, 11, 0.45);
    background: rgba(245, 158, 11, 0.08);
    color: var(--apex-warning);
}

.apex-table-shell {
    width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    border: 1px solid rgba(38, 50, 72, 0.9);
    border-radius: 8px;
    background: rgba(17, 22, 32, 0.88);
    box-sizing: border-box;
}

.apex-terminal-table {
    width: 100%;
    min-width: 720px;
    border-collapse: collapse;
    table-layout: fixed;
    color: var(--apex-text);
}

.apex-terminal-table th,
.apex-terminal-table td {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(38, 50, 72, 0.9);
    text-align: left;
    vertical-align: middle;
    font-size: 12px;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: clip;
}

.apex-terminal-table th {
    background: rgba(24, 31, 44, 0.96);
    color: var(--apex-text-secondary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
}

.apex-terminal-table tbody tr:hover {
    background: rgba(32, 41, 58, 0.45);
}

.apex-terminal-table td {
    color: var(--apex-text);
    font-family: 'Inter', sans-serif;
    background: transparent;
}

.apex-terminal-table td.apex-positive {
    color: var(--apex-positive);
}

.apex-terminal-table td.apex-negative {
    color: var(--apex-negative);
}

.apex-terminal-table td.apex-muted {
    color: var(--apex-text-secondary);
}

.apex-section-panel {
    background: rgba(17, 22, 32, 0.82);
    border: 1px solid rgba(38, 50, 72, 0.9);
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 14px;
}

.apex-panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 10px;
}

.apex-panel-title {
    margin: 0;
    font-size: 16px;
    line-height: 1.4;
    font-weight: 600;
}

.apex-empty-state {
    border: 1px dashed rgba(56, 189, 248, 0.35);
    border-radius: 8px;
    background: rgba(17, 22, 32, 0.62);
    padding: 18px;
    color: var(--apex-text-secondary);
    font-size: 12px;
}

.apex-topbar-popover {
    position: fixed;
    top: 12px;
    right: 18px;
    z-index: 1000002;
}

.apex-topbar-popover .stPopover > button,
.apex-topbar-popover button[kind="popover"] {
    background: rgba(24, 31, 44, 0.94) !important;
    color: var(--apex-text) !important;
    border: 1px solid rgba(56, 189, 248, 0.38) !important;
    border-radius: 6px !important;
    min-height: 30px !important;
    height: 30px !important;
    padding: 0 10px !important;
    font-size: 10px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.apex-user-popover {
    right: 18px;
}

.apex-alerts-popover {
    right: 130px;
}

.apex-workspace-popover {
    right: 238px;
}

.st-key-apex-fixed-workspace,
.st-key-apex-fixed-alerts,
.st-key-apex-fixed-user {
    position: fixed;
    top: 13px;
    margin: 0 !important;
    z-index: 1000002;
    width: max-content !important;
    max-width: max-content !important;
    pointer-events: none;
}

.st-key-apex-fixed-workspace > div,
.st-key-apex-fixed-alerts > div,
.st-key-apex-fixed-user > div {
    width: max-content !important;
    pointer-events: auto;
}

.st-key-apex-fixed-workspace { right: 187px; }
.st-key-apex-fixed-alerts { right: 65px; }
.st-key-apex-fixed-user { right: 18px; }

.st-key-apex-fixed-workspace .stPopover > button,
.st-key-apex-fixed-alerts .stPopover > button,
.st-key-apex-fixed-user .stPopover > button {
    min-height: 30px !important;
    height: 30px !important;
    padding: 0 10px !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.08em !important;
}

.st-key-apex-fixed-user .stPopover > button {
    width: 30px !important;
    min-width: 30px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: var(--apex-primary) !important;
    border-color: var(--apex-primary) !important;
    color: transparent !important;
    font-size: 0 !important;
}

.st-key-apex-fixed-user .stPopover > button::after {
    content: "";
    display: block;
    width: 8px;
    height: 8px;
    margin: 0 auto;
    border: 1px solid var(--apex-bg);
    border-radius: 50%;
    box-shadow: 0 7px 0 -2px var(--apex-bg);
}

.st-key-dashboard-sector-panel .apex-table-shell {
    padding-bottom: 2px;
    margin-bottom: 2px;
}

.st-key-dashboard-sector-panel .apex-terminal-table tbody tr:last-child td {
    border-bottom: 1px solid rgba(38, 50, 72, 0.9);
}

.module-section-kicker {
    margin: 0.25rem 0 0.55rem;
    color: var(--apex-primary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
}

.market-news-item {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.7rem 0;
    border-bottom: 1px solid var(--apex-border);
}

.market-news-item a {
    color: var(--apex-text);
    font-size: 0.84rem;
    line-height: 1.4;
    text-decoration: none;
}

.market-news-item a:hover {
    color: var(--apex-primary);
}

.market-news-item span {
    flex-shrink: 0;
    color: var(--apex-text-secondary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
}

@media (max-width: 700px) {
    .market-news-item {
        display: block;
    }

    .market-news-item span {
        display: block;
        margin-top: 0.25rem;
    }
}

@media (max-width: 700px) {
    .st-key-apex-fixed-workspace { right: 177px; }
    .st-key-apex-fixed-alerts { right: 55px; }
    .st-key-apex-fixed-user { right: 8px; }
    .st-key-apex-fixed-workspace .stPopover > button,
    .st-key-apex-fixed-alerts .stPopover > button,
    .st-key-apex-fixed-user .stPopover > button {
        padding: 0 6px !important;
        font-size: 9px !important;
    }
}

</style>
"""

def _table_html(df):
    if df is None:
        return "<div class='apex-empty-state'>No data available.</div>"

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    if df.empty:
        return "<div class='apex-empty-state'>No data available.</div>"

    columns = [str(col) for col in df.columns]
    header_html = "".join(f"<th>{escape(col)}</th>" for col in columns)

    rows_html = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if value is None or (isinstance(value, float) and pd.isna(value)) or (isinstance(value, str) and value.strip() == ""):
                rendered = "N/A"
                value_class = "apex-muted"
            else:
                rendered = str(value)
                value_class = ""
                if rendered.startswith("-"):
                    value_class = "apex-negative"
                elif rendered.endswith("%") and rendered.replace('%', '').replace('.', '', 1).replace('+', '', 1).replace('-', '', 1).isdigit():
                    numeric = float(rendered.strip('%').replace(',', ''))
                    if numeric > 0:
                        value_class = "apex-positive"
                    elif numeric < 0:
                        value_class = "apex-negative"
            cells.append(f"<td class='{value_class}'>{escape(rendered)}</td>")
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    return (
        "<div class='apex-table-shell'>"
        "<table class='apex-terminal-table'><thead><tr>"
        f"{header_html}</tr></thead><tbody>{''.join(rows_html)}</tbody></table>"
        "</div>"
    )


def render_terminal_table(df, *, empty_message="No data available."):
    if df is None or (hasattr(df, "empty") and df.empty):
        st.markdown(f"<div class='apex-empty-state'>{escape(empty_message)}</div>", unsafe_allow_html=True)
        return
    st.markdown(_table_html(df), unsafe_allow_html=True)


def render_apex_page_header(module_name, subtitle, status_text="", meta_text=""):
    status_html = f"<span class='apex-status-badge'>{escape(status_text)}</span>" if status_text else ""
    meta_html = f"<div class='apex-page-meta'>{status_html}{escape(meta_text)}</div>" if meta_text or status_html else ""
    st.markdown(
        f"""
        <div class='apex-page-header'>
            <div class='apex-page-title-wrap'>
                <div class='apex-page-kicker'>{escape(module_name)}</div>
                <h1 class='apex-page-title'>{escape(module_name)}</h1>
                <div class='apex-page-subtitle'>{escape(subtitle)}</div>
            </div>
            {meta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(label, tone="neutral"):
    st.markdown(f"<span class='apex-status-badge {tone}'>{escape(label)}</span>", unsafe_allow_html=True)


def apply_apex_theme(st):
    """Apply the Apex Terminal global UI theme."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)

# ============================================================
# APEX TERMINAL — GLOBAL UI POLISH LAYER
# ============================================================

def apply_apex_terminal_polish(st):
    """
    Global visual polish layer.

    This function changes presentation only.
    It does not modify financial calculations, retrieved data,
    session-state logic, Gemini behavior, Yahoo Finance logic,
    or the terminal security universe.
    """

    st.markdown(
        """
        <style>

        /* ====================================================
           APEX GLOBAL FOUNDATION
           ==================================================== */

        :root {
            --apex-bg: #070b11;
            --apex-surface: #0d141e;
            --apex-surface-2: #111a26;
            --apex-surface-3: #162131;
            --apex-border: #223247;
            --apex-border-strong: #2d4967;
            --apex-text: #edf4ff;
            --apex-muted: #91a7bf;
            --apex-blue: #35b8ff;
            --apex-blue-2: #1689d8;
            --apex-green: #16d98b;
            --apex-red: #ff5360;
            --apex-yellow: #f2c94c;
        }

        /* ====================================================
           PAGE
           ==================================================== */

        .stApp {
            background:
                radial-gradient(
                    circle at 50% -20%,
                    rgba(31, 104, 160, 0.12),
                    transparent 42%
                ),
                var(--apex-bg);
            color: var(--apex-text);
        }

        [data-testid="stMain"] {
            background: var(--apex-bg);
        }

        [data-testid="stMain"] .block-container {
            max-width: 1600px;
            padding-top: 1.25rem;
            padding-bottom: 3rem;
            padding-left: 1.35rem;
            padding-right: 1.35rem;
        }

        /* ====================================================
           REMOVE GENERIC STREAMLIT VISUAL NOISE
           ==================================================== */

        hr {
            border-color: var(--apex-border) !important;
            opacity: 0.9;
        }

        /* ====================================================
           HEADINGS
           ==================================================== */

        [data-testid="stMain"] h1 {
            color: var(--apex-text) !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em !important;
            line-height: 1.15 !important;
            margin-top: 0.1rem !important;
            margin-bottom: 0.25rem !important;
        }

        [data-testid="stMain"] h2 {
            color: var(--apex-text) !important;
            font-weight: 650 !important;
            letter-spacing: -0.015em !important;
        }

        [data-testid="stMain"] h3 {
            color: var(--apex-text) !important;
            font-weight: 650 !important;
        }

        [data-testid="stMain"] p,
        [data-testid="stMain"] label {
            color: var(--apex-muted);
        }

        /* ====================================================
           STREAMLIT METRIC CARDS
           ==================================================== */

        [data-testid="stMetric"] {
            background: linear-gradient(
                145deg,
                var(--apex-surface-2),
                var(--apex-surface)
            );
            border: 1px solid var(--apex-border);
            border-radius: 8px;
            padding: 0.85rem 0.95rem;
            min-height: 82px;
        }

        [data-testid="stMetricLabel"] {
            color: #8fa8c2 !important;
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.055em;
        }

        [data-testid="stMetricValue"] {
            color: var(--apex-text) !important;
            font-weight: 700 !important;
        }

        /* ====================================================
           DASHBOARD COMMAND CENTER
           ==================================================== */

        .st-key-dashboard-snapshot,
        .st-key-dashboard-watchlist-panel,
        .st-key-dashboard-sector-panel {
            min-width: 0 !important;
            box-sizing: border-box;
            padding: 0.85rem;
            border: 1px solid var(--apex-border);
            border-radius: 6px;
            background: rgba(13, 20, 30, 0.82);
        }

        .st-key-dashboard-snapshot {
            margin-bottom: 0.85rem;
        }

        .st-key-dashboard-watchlist-panel,
        .st-key-dashboard-sector-panel {
            height: 100%;
        }

        .dashboard-section-heading {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.7rem;
        }

        .dashboard-section-kicker,
        .dashboard-control-label,
        .dashboard-note-label {
            color: var(--apex-blue);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            font-weight: 600;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .dashboard-section-title {
            margin-top: 0.18rem;
            color: var(--apex-text);
            font-size: 1rem;
            font-weight: 650;
        }

        .dashboard-section-meta {
            flex-shrink: 0;
            color: var(--apex-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            letter-spacing: 0.07em;
            white-space: nowrap;
        }

        .dashboard-index-card {
            min-height: 101px;
            box-sizing: border-box;
            padding: 0.7rem 0.75rem;
            border: 1px solid #20344a;
            border-radius: 5px;
            background: linear-gradient(145deg, #111d2a, #0c141e);
        }

        .dashboard-index-label {
            overflow: hidden;
            color: var(--apex-text);
            font-size: 0.72rem;
            font-weight: 650;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .dashboard-index-symbol {
            margin-top: 0.12rem;
            overflow: hidden;
            color: var(--apex-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .dashboard-index-value {
            margin-top: 0.5rem;
            color: var(--apex-text);
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.05rem;
            font-weight: 600;
        }

        .dashboard-index-change {
            display: block;
            margin-top: 0.18rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            font-weight: 600;
        }

        .dashboard-index-change.positive,
        .apex-terminal-table td.apex-positive {
            color: var(--apex-green) !important;
        }

        .dashboard-index-change.negative,
        .apex-terminal-table td.apex-negative {
            color: var(--apex-red) !important;
        }

        .dashboard-index-change.muted,
        .dashboard-index-change.flat {
            color: var(--apex-muted);
        }

        .dashboard-control-label {
            margin: 0.85rem 0 0.35rem;
            color: var(--apex-muted);
        }

        .st-key-dashboard-watchlist-panel [data-testid="stButton"] > button {
            min-height: 32px;
            padding: 0.25rem 0.55rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            letter-spacing: 0.04em;
        }

        .dashboard-empty {
            padding: 1rem 0;
            color: var(--apex-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
        }

        .st-key-dashboard-terminal-note {
            margin-top: 0.85rem;
            padding: 0.65rem 0.8rem;
            border-top: 1px solid var(--apex-border);
            color: var(--apex-muted);
            font-size: 0.7rem;
        }

        .st-key-dashboard-terminal-note .dashboard-note-label {
            margin-right: 0.45rem;
            color: var(--apex-yellow);
        }

        /* ====================================================
           COMPANY ANALYSIS WORKSTATION
           ==================================================== */

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) {
            --company-panel: rgba(13, 20, 30, 0.86);
            --company-panel-raised: #111d2a;
        }

        .st-key-company-analysis-selector,
        .st-key-company-analysis-security-header {
            min-width: 0 !important;
            box-sizing: border-box;
            border: 1px solid var(--apex-border);
            border-radius: 6px;
            background: var(--company-panel, rgba(13, 20, 30, 0.86));
        }

        .st-key-company-analysis-selector {
            margin-bottom: 0.8rem;
            padding: 0.75rem 0.85rem 0.25rem;
        }

        .st-key-company-analysis-security-header {
            margin-bottom: 0.85rem;
            padding: 0.75rem 0.85rem 0.85rem;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .company-analysis-section-heading {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.65rem;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .company-analysis-kicker {
            color: var(--apex-blue);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            font-weight: 600;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .company-analysis-section-title {
            margin-top: 0.16rem;
            color: var(--apex-text);
            font-size: 1rem;
            font-weight: 650;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .company-analysis-section-meta {
            color: var(--apex-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            letter-spacing: 0.07em;
            white-space: nowrap;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .company-analysis-company-name {
            overflow-wrap: anywhere;
            color: var(--apex-text);
            font-size: clamp(1.25rem, 2.2vw, 1.85rem);
            font-weight: 700;
            line-height: 1.15;
            margin: 0.2rem 0 0.25rem;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .st-key-company-analysis-security-header [data-testid="stMetric"] {
            min-height: 74px;
            padding: 0.65rem 0.7rem;
            border-radius: 5px;
            background: var(--company-panel-raised);
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .st-key-company-analysis-security-header [data-testid="stMetricValue"] {
            font-size: 1.15rem !important;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .st-key-company-analysis-security-header [data-testid="stButton"] > button {
            min-height: 34px;
            padding: 0.3rem 0.55rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            letter-spacing: 0.04em;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) [data-testid="stTabs"] {
            margin-top: 0.15rem;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) [data-baseweb="tab-list"] {
            gap: 0.15rem;
            border-bottom: 1px solid var(--apex-border);
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) button[data-baseweb="tab"] {
            min-height: 34px;
            padding: 0.3rem 0.65rem;
            color: var(--apex-muted) !important;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--apex-blue) !important;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) [data-testid="stPlotlyChart"] {
            margin-top: 0.35rem;
            border: 1px solid var(--apex-border);
            border-radius: 6px;
            overflow: hidden;
            background: #0b1119;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) [data-testid="stExpander"] {
            border-radius: 5px !important;
            background: var(--company-panel) !important;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .apex-table-shell {
            max-width: 100%;
            overflow-x: auto;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .apex-terminal-table {
            min-width: 640px;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) [data-testid="stMarkdownContainer"] p {
            overflow-wrap: anywhere;
        }

        [data-testid="stMain"]:has(.st-key-company-analysis-security-header) [data-testid="stDownloadButton"] > button {
            min-height: 32px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
        }

        @media (max-width: 700px) {
            [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .company-analysis-section-heading {
                gap: 0.45rem;
            }

            [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .company-analysis-section-meta {
                font-size: 0.5rem;
            }

            [data-testid="stMain"]:has(.st-key-company-analysis-security-header) .st-key-company-analysis-security-header [data-testid="stHorizontalBlock"] {
                gap: 0.55rem !important;
            }

            [data-testid="stMain"]:has(.st-key-company-analysis-security-header) button[data-baseweb="tab"] {
                padding-left: 0.42rem;
                padding-right: 0.42rem;
                font-size: 0.56rem;
            }
        }

        /* ====================================================
           PORTFOLIO ANALYSIS WORKSTATION
           ==================================================== */

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) {
            --portfolio-panel: rgba(13, 20, 30, 0.86);
            --portfolio-panel-raised: #111d2a;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-section-heading {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin: 0.1rem 0 0.7rem;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-kicker,
        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-subsection-label {
            color: var(--apex-blue);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            font-weight: 600;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-section-title {
            margin-top: 0.16rem;
            color: var(--apex-text);
            font-size: 1rem;
            font-weight: 650;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-section-meta {
            flex-shrink: 0;
            color: var(--apex-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            letter-spacing: 0.07em;
            white-space: nowrap;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-helper-text {
            margin: 0 0 0.7rem;
            color: var(--apex-muted);
            font-size: 0.72rem;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-review-heading {
            margin-top: 1.05rem;
            padding-top: 0.85rem;
            border-top: 1px solid var(--apex-border);
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-subsection-label {
            margin: 0.85rem 0 0.45rem;
            color: var(--apex-muted);
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) [data-testid="stMetric"] {
            min-height: 78px;
            padding: 0.7rem 0.8rem;
            border-radius: 5px;
            background: linear-gradient(145deg, var(--portfolio-panel-raised), #0c141e);
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) [data-testid="stMetricValue"] {
            font-size: 1.18rem !important;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) [data-testid="stButton"] > button {
            min-height: 32px;
            padding: 0.25rem 0.55rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.035em;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) [data-testid="stPlotlyChart"] {
            min-width: 0;
            margin-top: 0.2rem;
            border: 1px solid var(--apex-border);
            border-radius: 6px;
            overflow: hidden;
            background: #0b1119;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .apex-table-shell {
            max-width: 100%;
            overflow-x: auto;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .apex-terminal-table {
            min-width: 640px;
        }

        [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) [data-testid="stDownloadButton"] > button {
            min-height: 32px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
        }

        @media (max-width: 700px) {
            [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-section-heading {
                gap: 0.45rem;
            }

            [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) .portfolio-section-meta {
                font-size: 0.5rem;
            }

            [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) [data-testid="stHorizontalBlock"] {
                gap: 0.55rem !important;
            }

            [data-testid="stMain"]:has(.st-key-portfolio-analysis-page) [data-testid="stPlotlyChart"] {
                min-height: 260px;
            }
        }

        /* ====================================================
           BUTTONS
           ==================================================== */

        [data-testid="stButton"] > button {
            border: 1px solid var(--apex-border-strong);
            background: linear-gradient(
                180deg,
                #111c29,
                #0c141e
            );
            color: #dcecff;
            border-radius: 6px;
            min-height: 34px;
            font-weight: 600;
            transition:
                border-color 120ms ease,
                background 120ms ease,
                transform 120ms ease;
        }

        [data-testid="stButton"] > button:hover {
            border-color: var(--apex-blue);
            background: #122234;
            color: white;
        }

        [data-testid="stButton"] > button:active {
            transform: translateY(1px);
        }

        /* ====================================================
           INPUTS / SELECTS
           ==================================================== */

        [data-baseweb="input"],
        [data-baseweb="select"] > div,
        [data-testid="stTextInput"] input {
            background: #0c141f !important;
            border-color: var(--apex-border) !important;
            color: var(--apex-text) !important;
        }

        /* ====================================================
           SIDEBAR
           ==================================================== */

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #101722 0%,
                    #0c131d 100%
                ) !important;
            border-right: 1px solid var(--apex-border) !important;
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 4.7rem !important;
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
        }

        /* Native collapse button */
        [data-testid="stSidebarCollapseButton"] button,
        button[data-testid="stExpandSidebarButton"] {
            width: 42px !important;
            height: 42px !important;
            min-width: 42px !important;
            min-height: 42px !important;
            border-radius: 9px !important;
            border: 1px solid #2a425d !important;
            background: #101a27 !important;
            color: #eaf4ff !important;
            box-shadow: none !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        [data-testid="stSidebarCollapseButton"] button:hover,
        button[data-testid="stExpandSidebarButton"]:hover {
            border-color: var(--apex-blue) !important;
            background: #142438 !important;
            color: white !important;
        }

        /* Never expose raw Material Symbol names */
        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
        button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
            font-size: 0 !important;
        }

        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::after {
            content: "<";
            font-size: 24px;
            font-family: Arial, sans-serif;
            line-height: 1;
        }

        button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"]::after {
            content: ">";
            font-size: 24px;
            font-family: Arial, sans-serif;
            line-height: 1;
        }

        /* ====================================================
           TERMINAL PANELS
           ==================================================== */

        [class*="st-key-"] {
            min-width: 0;
        }

        /* ====================================================
           LOCKED HTML TABLES
           ==================================================== */

        .apex-terminal-table-wrap {
            width: 100%;
            max-width: 100%;
            overflow-x: auto;
            overflow-y: hidden;
            border: 1px solid var(--apex-border);
            border-radius: 7px;
            background: #0b1119;
            scrollbar-width: thin;
            scrollbar-color: #40566d #0b1119;
        }

        .apex-terminal-table-wrap table {
            width: max-content;
            min-width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            font-size: 0.79rem;
            color: #e6eef8;
        }

        .apex-terminal-table-wrap th {
            position: sticky;
            top: 0;
            z-index: 2;
            background: #171f2b;
            color: #9eb3c9;
            border-bottom: 1px solid #2a3b50;
            border-right: 1px solid #26374a;
            padding: 0.55rem 0.65rem;
            text-align: left;
            white-space: nowrap;
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.045em;
        }

        .apex-terminal-table-wrap td {
            height: 38px;
            min-height: 38px;
            padding: 0.5rem 0.65rem;
            border-bottom: 1px solid #1b2838;
            border-right: 1px solid #172333;
            white-space: nowrap;
            overflow: visible;
        }

        .apex-terminal-table-wrap tbody tr:hover td {
            background: rgba(39, 117, 174, 0.08);
        }

        .apex-terminal-table-wrap::-webkit-scrollbar {
            height: 9px;
        }

        .apex-terminal-table-wrap::-webkit-scrollbar-track {
            background: #0b1119;
        }

        .apex-terminal-table-wrap::-webkit-scrollbar-thumb {
            background: #40566d;
            border-radius: 10px;
        }

        /* ====================================================
           NATIVE STREAMLIT DATAFRAME CONTAINERS
           ==================================================== */

        [data-testid="stDataFrame"] {
            width: 100% !important;
            max-width: 100% !important;
            border: 1px solid var(--apex-border);
            border-radius: 7px;
            overflow: hidden;
        }

        /* Prevent the iframe/dataframe itself from pushing the page */
        [data-testid="stDataFrame"] > div {
            max-width: 100% !important;
        }

        /* ====================================================
           TABS
           ==================================================== */

        button[data-baseweb="tab"] {
            color: #8fa7bf !important;
            font-weight: 600 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--apex-blue) !important;
        }

        /* ====================================================
           EXPANDERS
           ==================================================== */

        [data-testid="stExpander"] {
            border: 1px solid var(--apex-border) !important;
            border-radius: 7px !important;
            background: #0d141e !important;
        }

        /* ====================================================
           PLOTLY
           ==================================================== */

        .js-plotly-plot,
        .plot-container {
            max-width: 100% !important;
        }

        /* ====================================================
           NO PAGE HORIZONTAL OVERFLOW
           ==================================================== */

        html,
        body,
        [data-testid="stAppViewContainer"] {
            max-width: 100%;
        }

        /* ====================================================
           RESPONSIVE
           ==================================================== */

        @media (max-width: 1100px) {
            [data-testid="stMain"] .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        @media (max-width: 900px) {
            [data-testid="stMain"] .block-container {
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }

            [data-testid="stMetric"] {
                min-height: 74px;
            }
        }

        @media (max-width: 700px) {
            [data-testid="stMain"] .block-container {
                padding-left: 0.55rem;
                padding-right: 0.55rem;
            }

            [data-testid="stMetricValue"] {
                font-size: 1.15rem !important;
            }

            .dashboard-section-heading {
                gap: 0.5rem;
            }

            .dashboard-section-meta {
                font-size: 0.5rem;
            }

            .st-key-dashboard_sections [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: 0.75rem !important;
            }

            .st-key-dashboard_sections [data-testid="stHorizontalBlock"] > div {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

