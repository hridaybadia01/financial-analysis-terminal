"""
Financial Analysis Terminal
============================
A Streamlit-based equity research terminal for Indian (NSE-focused) markets,
built on free Yahoo Finance data via yfinance.

Modules: Dashboard, Company Analysis, Stock Screener, Financial Statements,
Valuation, Market Data, Peer Comparison, Portfolio, Risk Analysis,
Technical Analysis, AI Research.

Data source:Yahoo Finance (delayed, not tick-by-tick real-time). All figures
are either pulled directly from Yahoo Finance or calculated from that data
with a Python function you can see in this file. Nothing is fabricated -
unavailable fields display "N/A".
"""

import streamlit as st
from html import escape
from apex_theme import apply_apex_theme, render_apex_page_header, render_terminal_table, apply_apex_terminal_polish
from apex_shell import apply_apex_shell
from dashboard_system_map import render_dashboard_system_map
from technical_analysis import render_technical_analysis_results
from asset_capabilities import (
    annualization_periods,
    direct_provider_metrics,
    get_asset_capabilities,
    metric_state,
    normalize_asset_class,
    supports_metric,
)
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, timezone
from ai.gemini_engine import generate_analysis

from universe import (
    load_universe,
)

from urllib.parse import quote
import xml.etree.ElementTree as ET
import requests



# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Financial Analysis Terminal",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# APEX TERMINAL GLOBAL UI THEME
# ============================================================

apply_apex_theme(st)


apply_apex_terminal_polish(st)
apply_apex_shell(st)


# ============================================================
# FINAL_UNIVERSAL_TABLE_WRAP_OVERRIDE_V1
# Universal table visibility / wrapping fix
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       TABLE CONTAINER
       ======================================================== */

    .terminal-table-wrapper {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
        overflow-y: visible !important;
        box-sizing: border-box !important;
    }


    /* ========================================================
       TABLE ITSELF
       Force the complete table to stay inside its block.
       ======================================================== */

    .terminal-data-table {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;

        table-layout: fixed !important;

        border-collapse: separate !important;
        border-spacing: 0 !important;

        box-sizing: border-box !important;
    }


    /* ========================================================
       EVERY HEADER + EVERY CELL
       No clipping.
       No ellipsis.
       No nowrap.
       Everything wraps.
       ======================================================== */

    .terminal-data-table th,
    .terminal-data-table td {

        white-space: normal !important;

        overflow-wrap: anywhere !important;

        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: visible !important;

        min-width: 0 !important;

        box-sizing: border-box !important;

        vertical-align: top !important;
    }


    /* ========================================================
       HEADERS
       ======================================================== */

    .terminal-data-table thead th {

        white-space: normal !important;

        overflow-wrap: anywhere !important;

        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: visible !important;

        min-width: 0 !important;

        line-height: 1.35 !important;

        height: auto !important;
    }


    /* ========================================================
       BODY CELLS
       ======================================================== */

    .terminal-data-table tbody td {

        white-space: normal !important;

        overflow-wrap: anywhere !important;

        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: visible !important;

        min-width: 0 !important;

        max-width: none !important;

        line-height: 1.45 !important;

        height: auto !important;
    }


    /* ========================================================
       DESCRIPTIVE CELLS
       ======================================================== */

    .terminal-data-table .terminal-descriptive {

        white-space: normal !important;

        overflow-wrap: anywhere !important;

        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: visible !important;

        min-width: 0 !important;

        max-width: none !important;

        text-align: left !important;
    }


    /* ========================================================
       NUMERIC CELLS
       ======================================================== */

    .terminal-data-table .terminal-numeric {

        white-space: normal !important;

        overflow-wrap: anywhere !important;

        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: visible !important;

        min-width: 0 !important;

        max-width: none !important;

        text-align: right !important;
    }


    /* ========================================================
       FIRST COLUMN
       This is especially important for:
       - Particulars
       - Metric
       - Company
       - Industry
       - Sector
       ======================================================== */

    .terminal-data-table th:first-child,
    .terminal-data-table td:first-child {

        width: 28% !important;

        min-width: 0 !important;

        max-width: 35% !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;

        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: visible !important;

        text-align: left !important;
    }


    /* ========================================================
       ALL REMAINING COLUMNS
       ======================================================== */

    .terminal-data-table th:not(:first-child),
    .terminal-data-table td:not(:first-child) {

        min-width: 0 !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;

        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: visible !important;
    }


    /* ========================================================
       FINANCIAL STATEMENT TABLES
       Keep row labels comfortably readable.
       ======================================================== */

    .terminal-financial-statements .terminal-data-table th:first-child,
    .terminal-financial-statements .terminal-data-table td:first-child {

        width: 36% !important;

        max-width: 40% !important;

        min-width: 0 !important;

        text-align: left !important;

        font-weight: 600 !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;

        word-break: break-word !important;
    }


    /* ========================================================
       MOBILE / SMALL WINDOWS
       ======================================================== */

    @media (max-width: 900px) {

        .terminal-data-table {

            width: 100% !important;

            min-width: 100% !important;

            table-layout: fixed !important;
        }

        .terminal-data-table th,
        .terminal-data-table td {

            padding: 8px 9px !important;

            font-size: 12px !important;

            white-space: normal !important;

            overflow-wrap: anywhere !important;

            word-break: break-word !important;
        }

        .terminal-data-table th:first-child,
        .terminal-data-table td:first-child {

            width: 38% !important;

            max-width: 42% !important;
        }
    }


    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# END FINAL_UNIVERSAL_TABLE_WRAP_OVERRIDE_V1
# ============================================================

# ============================================================
# CONSTANTS
# ============================================================

IST = timezone(timedelta(hours=5, minutes=30))

TIMEFRAMES = {
    "5M": ("1d", "1m"),
    "15M": ("1d", "1m"),
    "30M": ("1d", "1m"),
    "1H": ("1d", "1m"),
    "1D": ("1d", "5m"),
    "5D": ("5d", "15m"),
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1d"),
    "1Y": ("1y", "1d"),
    "2Y": ("2y", "1d"),
    "5Y": ("5y", "1wk"),
    "10Y": ("10y", "1wk"),
    "MAX": ("max", "1mo"),
}

INDICES = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW JONES": "^DJI",
}

BENCHMARKS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY Bank": "^NSEBANK",
    "S&P 500": "^GSPC",
    "NASDAQ Composite": "^IXIC",
    "Dow Jones Industrial Average": "^DJI",
    "FTSE 100": "^FTSE",
}

RETURN_WINDOWS = [
    ("1D", 1), ("1W", 5), ("1M", 21), ("3M", 63),
    ("6M", 126), ("1Y", 252), ("3Y", 756), ("5Y", 1260),
]

NAV_MODULES = [
    "Dashboard",
    "Company Analysis",
    "Stock Screener",
    "Financial Statements",
    "Valuation",
    "Peer Comparison",
    "Market Data",
    "Market News",
    "Technical Analysis",
    "Portfolio",
    "Risk Analysis",
    "AI Research",
]

# ------------------------------------------------------------
# COMPANY SEARCH / NAME RESOLUTION
# ------------------------------------------------------------
# Local aliases make the search bar human-friendly while the actual market
# data continues to come live from Yahoo Finance. Grouped by broad sector so
# the same structure can double as a peer-comparison map (SECTOR_GROUPS
# below) without extra API calls.

SECTOR_GROUPS = {
    "Energy & Conglomerates": {
        "Reliance Industries Limited": "RELIANCE.NS",
        "Adani Enterprises Limited": "ADANIENT.NS",
        "Adani Ports and Special Economic Zone Limited": "ADANIPORTS.NS",
        "Adani Green Energy Limited": "ADANIGREEN.NS",
        "Adani Energy Solutions Limited": "ADANIENSOL.NS",
        "Adani Power Limited": "ADANIPOWER.NS",
        "Oil & Natural Gas Corporation Limited": "ONGC.NS",
        "Indian Oil Corporation Limited": "IOC.NS",
        "Bharat Petroleum Corporation Limited": "BPCL.NS",
        "Hindustan Petroleum Corporation Limited": "HINDPETRO.NS",
        "Power Grid Corporation of India Limited": "POWERGRID.NS",
        "NTPC Limited": "NTPC.NS",
    },
    "Banks & Financials": {
        "HDFC Bank Limited": "HDFCBANK.NS",
        "ICICI Bank Limited": "ICICIBANK.NS",
        "State Bank of India": "SBIN.NS",
        "Axis Bank Limited": "AXISBANK.NS",
        "Kotak Mahindra Bank Limited": "KOTAKBANK.NS",
        "IndusInd Bank Limited": "INDUSINDBK.NS",
        "Bajaj Finance Limited": "BAJFINANCE.NS",
        "Bajaj Finserv Limited": "BAJAJFINSV.NS",
        "Bajaj Housing Finance Limited": "BAJAJHFL.NS",
        "Jio Financial Services Limited": "JIOFIN.NS",
        "Cholamandalam Investment and Finance Company Limited": "CHOLAFIN.NS",
        "LIC of India": "LICI.NS",
        "SBI Life Insurance Company Limited": "SBILIFE.NS",
        "HDFC Life Insurance Company Limited": "HDFCLIFE.NS",
        "ICICI Lombard General Insurance Company Limited": "ICICIGI.NS",
        "ICICI Prudential Life Insurance Company Limited": "ICICIPRULI.NS",
    },
    "Tata Group": {
        "Tata Consultancy Services Limited": "TCS.NS",
        "Tata Motors Limited": "TMCV.NS",
        "Tata Steel Limited": "TATASTEEL.NS",
        "Tata Consumer Products Limited": "TATACONSUM.NS",
        "Tata Power Company Limited": "TATAPOWER.NS",
        "Tata Chemicals Limited": "TATACHEM.NS",
        "Tata Elxsi Limited": "TATAELXSI.NS",
        "Indian Hotels Company Limited": "INDHOTEL.NS",
        "Titan Company Limited": "TITAN.NS",
        "Trent Limited": "TRENT.NS",
    },
    "Bajaj Group": {
        "Bajaj Auto Limited": "BAJAJ-AUTO.NS",
        "Bajaj Holdings & Investment Limited": "BAJAJHLDNG.NS",
        "Bajaj Finance Limited ": "BAJFINANCE.NS",
        "Bajaj Finserv Limited ": "BAJAJFINSV.NS",
    },
    "Information Technology": {
        "Infosys Limited": "INFY.NS",
        "Wipro Limited": "WIPRO.NS",
        "HCL Technologies Limited": "HCLTECH.NS",
        "Tech Mahindra Limited": "TECHM.NS",
        "LTIMindtree Limited": "LTM.NS",
        "Persistent Systems Limited": "PERSISTENT.NS",
        "Mphasis Limited": "MPHASIS.NS",
        "Oracle Financial Services Software Limited": "OFSS.NS",
    },
    "FMCG & Consumer": {
        "Hindustan Unilever Limited": "HINDUNILVR.NS",
        "ITC Limited": "ITC.NS",
        "Nestle India Limited": "NESTLEIND.NS",
        "Britannia Industries Limited": "BRITANNIA.NS",
        "Varun Beverages Limited": "VBL.NS",
        "Godrej Consumer Products Limited": "GODREJCP.NS",
        "Dabur India Limited": "DABUR.NS",
        "Marico Limited": "MARICO.NS",
        "United Spirits Limited": "UNITDSPR.NS",
    },
    "Pharma & Healthcare": {
        "Sun Pharmaceutical Industries Limited": "SUNPHARMA.NS",
        "Dr. Reddy's Laboratories Limited": "DRREDDY.NS",
        "Cipla Limited": "CIPLA.NS",
        "Divi's Laboratories Limited": "DIVISLAB.NS",
        "Apollo Hospitals Enterprise Limited": "APOLLOHOSP.NS",
        "Max Healthcare Institute Limited": "MAXHEALTH.NS",
    },
    "Automobiles": {
        "Maruti Suzuki India Limited": "MARUTI.NS",
        "Mahindra & Mahindra Limited": "M&M.NS",
        "Eicher Motors Limited": "EICHERMOT.NS",
        "Hero MotoCorp Limited": "HEROMOTOCO.NS",
        "TVS Motor Company Limited": "TVSMOTOR.NS",
    },
    "Industrials & Infrastructure": {
        "Larsen & Toubro Limited": "LT.NS",
        "Siemens Limited": "SIEMENS.NS",
        "ABB India Limited": "ABB.NS",
        "Bharat Heavy Electricals Limited": "BHEL.NS",
        "Bharat Electronics Limited": "BEL.NS",
        "Hindustan Aeronautics Limited": "HAL.NS",
        "UltraTech Cement Limited": "ULTRACEMCO.NS",
        "Grasim Industries Limited": "GRASIM.NS",
        "Shree Cement Limited": "SHREECEM.NS",
    },
    "Telecom & New-age": {
        "Bharti Airtel Limited": "BHARTIARTL.NS",
        "Vodafone Idea Limited": "IDEA.NS",
        "Zomato Limited": "ETERNAL.NS",
        "Eternal Limited": "ETERNAL.NS",
        "One 97 Communications Limited": "PAYTM.NS",
        "Info Edge (India) Limited": "NAUKRI.NS",
        "Indian Railway Catering and Tourism Corporation Limited": "IRCTC.NS",
        "Indian Railway Finance Corporation Limited": "IRFC.NS",
    },
}



# ============================================================
# MASTER UNIVERSE INTEGRATION
# ============================================================
#
# yahoo_global_universe.csv is the SINGLE SOURCE OF TRUTH.
#
# Every usable Yahoo Finance security available to the terminal
# comes from this file.
#
# No hardcoded security list is used for application-wide
# security selection.
# ============================================================

UNIVERSE_DF = load_universe()

# ------------------------------------------------------------
# TICKER -> METADATA
# ------------------------------------------------------------

UNIVERSE_BY_TICKER = (
    UNIVERSE_DF
    .drop_duplicates(subset=["ticker"])
    .set_index("ticker")
    .to_dict("index")
)


# ------------------------------------------------------------
# SECURITY OPTIONS
# ------------------------------------------------------------

def get_security_label(ticker):
    """Return Name • Ticker display label."""

    ticker = str(ticker).strip()

    record = UNIVERSE_BY_TICKER.get(ticker)

    if record:
        name = str(record.get("name", ticker)).strip()

        if name:
            return f"{name} • {ticker}"

    return ticker


def get_security_tickers(
    asset_class=None,
    region=None,
    country=None,
):
    """Return tickers from the master Yahoo universe."""

    df = UNIVERSE_DF

    if asset_class:
        df = df[
            df["asset_class"].str.upper()
            == str(asset_class).upper()
        ]

    if region:
        df = df[
            df["region"].str.lower()
            == str(region).lower()
        ]

    if country:
        df = df[
            df["country"].str.lower()
            == str(country).lower()
        ]

    return df["ticker"].tolist()


def get_security_labels(
    asset_class=None,
    region=None,
    country=None,
):
    """Return Name • Ticker labels from the master universe."""

    tickers = get_security_tickers(
        asset_class=asset_class,
        region=region,
        country=country,
    )

    return [
        get_security_label(ticker)
        for ticker in tickers
    ]


# ------------------------------------------------------------
# SEARCH
# ------------------------------------------------------------

def search_companies(query, limit=12):
    """Search the master Yahoo universe by security name or ticker."""

    q = str(query).strip().lower()

    if not q:
        return []

    results = []

    for _, row in UNIVERSE_DF.iterrows():

        name = str(row["name"]).strip()
        ticker = str(row["ticker"]).strip()

        searchable = f"{name} {ticker}".lower()

        if q in searchable:
            results.append((name, ticker))

    results.sort(
        key=lambda x: (
            x[0].lower().find(q)
            if q in x[0].lower()
            else 9999,
            x[0].lower()
        )
    )

    # Remove duplicate tickers while preserving best result
    unique = []
    seen = set()

    for name, ticker in results:

        if ticker not in seen:
            unique.append((name, ticker))
            seen.add(ticker)

        if len(unique) >= limit:
            break

    return unique


def resolve_company_input(value):
    """Resolve a security name or ticker using the master universe."""

    value = str(value).strip()

    if not value:
        return ""

    upper = value.upper()

    # Exact ticker
    if upper in UNIVERSE_BY_TICKER:
        return upper

    # Exact security name
    for ticker, record in UNIVERSE_BY_TICKER.items():

        name = str(
            record.get("name", "")
        ).strip()

        if name.casefold() == value.casefold():
            return ticker

    # Partial name / ticker search
    matches = search_companies(value, limit=1)

    if matches:
        return matches[0][1]

    # Preserve unknown Yahoo ticker rather than fabricating .NS
    return upper


def normalize_ticker(ticker):
    return resolve_company_input(ticker)


def display_ticker(ticker):
    return str(ticker)

def security_dropdown(
    label="Select Security",
    asset_class=None,
    region=None,
    country=None,
    key=None,
):
    """
    Reusable searchable security selector.

    The user sees ONLY the actual company/security name.
    The Yahoo Finance ticker remains hidden internally and is
    returned by this function.
    """

    options_df = UNIVERSE_DF.copy()

    if asset_class:
        options_df = options_df[
            options_df["asset_class"].astype(str).str.upper()
            == str(asset_class).upper()
        ]

    if region:
        options_df = options_df[
            options_df["region"].astype(str).str.lower()
            == str(region).lower()
        ]

    if country:
        options_df = options_df[
            options_df["country"].astype(str).str.lower()
            == str(country).lower()
        ]

    options_df = (
        options_df
        .sort_values(["name", "ticker"])
        .drop_duplicates("ticker")
    )

    if options_df.empty:
        return ""

    # Internal values remain Yahoo Finance tickers.
    options = options_df["ticker"].astype(str).tolist()

    # User-facing labels are ONLY company/security names.
    labels = {}

    for _, row in options_df.iterrows():
        ticker = str(row["ticker"]).strip()
        name = str(row["name"]).strip()

        if not name or name.lower() == "nan":
            name = ticker

        labels[ticker] = name

    selected = st.selectbox(
        label,
        options,
        format_func=lambda ticker: labels.get(
            ticker,
            str(ticker)
        ),
        key=key,
    )

    return selected


# ------------------------------------------------------------
# LEGACY SECTOR MAPPING
# ------------------------------------------------------------

TICKER_TO_SECTOR_GROUP = {}

for _group, _members in SECTOR_GROUPS.items():

    for _name, _ticker in _members.items():

        TICKER_TO_SECTOR_GROUP[_ticker] = _group


# ============================================================
# NEWS FEED
# ============================================================

@st.cache_data(ttl=600, show_spinner=False)
def get_news_feed(query, limit=6):
    """
    Fetch financial news from the public Google News RSS feed.
    No API key required.
    """
    try:
        encoded_query = quote(query)

        feed_url = (
            "https://news.google.com/rss/search"
            f"?q={encoded_query}"
            "&hl=en-IN"
            "&gl=IN"
            "&ceid=IN:en"
        )

        response = requests.get(
            feed_url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(response.content)

        news_items = []

        for item in root.findall(".//item")[:limit]:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "").strip()

            if title and link:
                news_items.append({
                    "title": title,
                    "link": link,
                    "published": pub_date,
                })

        return news_items

    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def get_sidebar_news():
    """
    Fetch sidebar news with one combined Google News RSS request.
    This avoids making four sequential network requests on every cold load.
    """
    query = (
        "NSE OR Nifty OR Sensex OR "
        "Indian stocks OR Indian companies OR "
        "Indian banks OR RBI OR "
        "global markets"
    )

    try:
        encoded_query = quote(query)

        feed_url = (
            "https://news.google.com/rss/search"
            f"?q={encoded_query}"
            "&hl=en-IN"
            "&gl=IN"
            "&ceid=IN:en"
        )

        response = requests.get(
            feed_url,
            timeout=6,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()

        root = ET.fromstring(response.content)

        news_items = []

        for item in root.findall(".//item")[:8]:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "").strip()

            if title and link:
                news_items.append({
                    "title": title,
                    "link": link,
                    "published": pub_date,
                })

        return news_items

    except Exception:
        return []


# ============================================================
# DATA LAYER  (all live calls funnel through these functions)
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_history(ticker, period="max", interval="1d"):
    """Fetch OHLCV history. Never raises - returns an empty DataFrame on failure."""
    try:
        data = yf.Ticker(ticker).history(
            period=period,
            interval=interval,
            auto_adjust=False
        )

        if data is None or data.empty:
            return pd.DataFrame()

        # Remove rows where Yahoo Finance did not return a valid closing price
        data = data.dropna(subset=["Close"])

        if data.empty:
            return pd.DataFrame()

        return data

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=30, show_spinner=False)
def get_intraday_history(ticker, period="1d", interval="1m"):
    """Fetch short-term intraday OHLCV data with a 30-second cache."""
    try:
        data = yf.Ticker(ticker).history(
            period=period,
            interval=interval,
            auto_adjust=False
        )

        if data is None or data.empty:
            return pd.DataFrame()

        data = data.dropna(subset=["Close"])

        return data if not data.empty else pd.DataFrame()

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=180, show_spinner=False)
def get_company_info(ticker):

    """Fetch the Yahoo Finance 'info' dict (quote + fundamentals snapshot)."""
    try:
        info = yf.Ticker(ticker).info
        return info if isinstance(info, dict) else {}
    except Exception:
        return {}

@st.cache_data(ttl=300, show_spinner=False)
def get_dashboard_market_data(watchlist):
    """
    Fetch Dashboard market data efficiently.
    Uses one Yahoo Finance download for all market/index history
    instead of making separate history requests for every ticker.
    """

    all_tickers = list(INDICES.values()) + list(watchlist)

    try:
        batch_data = yf.download(
            tickers=all_tickers,
            period="5d",
            interval="1d",
            auto_adjust=False,
            progress=False,
            group_by="column",
            threads=True,
        )
    except Exception:
        batch_data = pd.DataFrame()

    data = {
        "indices": {},
        "watchlist": {},
    }

    # ------------------------------------------------------------
    # Extract index history from the single Yahoo download
    # ------------------------------------------------------------
    for label, symbol in INDICES.items():

        try:
            if batch_data.empty:
                hist = pd.DataFrame()

            elif isinstance(batch_data.columns, pd.MultiIndex):
                hist = batch_data.xs(symbol, axis=1, level=1).copy()

            else:
                hist = batch_data.copy()

            if not hist.empty and "Close" in hist.columns:
                hist = hist.dropna(subset=["Close"])

            data["indices"][label] = hist

        except Exception:
            data["indices"][label] = pd.DataFrame()

    # ------------------------------------------------------------
    # Extract watchlist history
    # ------------------------------------------------------------
    for ticker in watchlist:

        try:
            if batch_data.empty:
                hist = pd.DataFrame()

            elif isinstance(batch_data.columns, pd.MultiIndex):
                hist = batch_data.xs(ticker, axis=1, level=1).copy()

            else:
                hist = batch_data.copy()

            if not hist.empty and "Close" in hist.columns:
                hist = hist.dropna(subset=["Close"])

        except Exception:
            hist = pd.DataFrame()

        # Company info remains separately cached.
        # This is required for company names and other snapshot fields.
        info = get_company_info(ticker)

        data["watchlist"][ticker] = {
            "history": hist,
            "info": info,
        }

    return data


@st.cache_data(ttl=600, show_spinner=False)
def get_income_statement(ticker):
    try:
        df = yf.Ticker(ticker).income_stmt
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def get_balance_sheet(ticker):
    try:
        df = yf.Ticker(ticker).balance_sheet
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def get_cashflow(ticker):
    try:
        df = yf.Ticker(ticker).cashflow
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def safe_value(info, key, default=None):
    if not info:
        return default
    value = info.get(key, default)
    if value is None:
        return default
    if isinstance(value, float) and np.isnan(value):
        return default
    return value


def get_statement_value(df, possible_names):
    """Find the first available financial-statement row from a list of possible names."""
    if df is None or df.empty:
        return None
    for name in possible_names:
        if name in df.index:
            row = df.loc[name]
            if len(row) > 0:
                value = row.iloc[0]
                if pd.notna(value):
                    return value
    return None


def get_statement_series(df, possible_names):
    """Return the full historical row (across all reported periods) as a Series."""
    if df is None or df.empty:
        return pd.Series(dtype=float)
    for name in possible_names:
        if name in df.index:
            row = df.loc[name].dropna()
            if len(row) > 0:
                return row
    return pd.Series(dtype=float)


# ------------------------------------------------------------
# FORMATTING HELPERS (Indian Cr/Lakh scale + generic fallback)
# ------------------------------------------------------------

def format_inr_scale(value):
    """Format a rupee amount using Indian Crore/Lakh conventions."""
    if value is None:
        return "N/A"
    try:
        value = float(value)
    except Exception:
        return "N/A"
    if np.isnan(value):
        return "N/A"

    abs_v = abs(value)
    if abs_v >= 1_00_00_00_000:  # >= 1000 Cr
        return f"INR {value / 1_00_00_000:,.0f} Cr"
    if abs_v >= 1_00_00_000:  # >= 1 Cr
        return f"INR {value / 1_00_00_000:,.2f} Cr"
    if abs_v >= 1_00_000:  # >= 1 Lakh
        return f"INR {value / 1_00_000:,.2f} L"
    return f"INR {value:,.2f}"


def format_number(value):
    """Generic large-number formatter (T/B/M/K) - used for global-style figures."""
    if value is None:
        return "N/A"
    try:
        value = float(value)
    except Exception:
        return "N/A"
    if np.isnan(value):
        return "N/A"

    abs_v = abs(value)
    if abs_v >= 1_000_000_000_000:
        return f"INR {value / 1_000_000_000_000:.2f}T"
    if abs_v >= 1_000_000_000:
        return f"INR {value / 1_000_000_000:.2f}B"
    if abs_v >= 1_000_000:
        return f"INR {value / 1_000_000:.2f}M"
    if abs_v >= 1_000:
        return f"INR {value / 1_000:.2f}K"
    return f"INR {value:.2f}"


def format_percent(value, already_pct=False):
    if value is None:
        return "N/A"
    try:
        v = float(value)
    except Exception:
        return "N/A"
    if np.isnan(v):
        return "N/A"
    return f"{v:.2f}%" if already_pct else f"{v * 100:.2f}%"


def format_ratio(value, suffix="x"):
    if value is None:
        return "N/A"
    try:
        v = float(value)
    except Exception:
        return "N/A"
    if np.isnan(v):
        return "N/A"
    return f"{v:.2f}{suffix}"


def pct_change_str(value):
    """Colour-tagged HTML string for a percent change (used inline)."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return '<span class="neutral">N/A</span>'
    cls = "positive" if value >= 0 else "negative"
    sign = "+" if value >= 0 else ""
    return f'<span class="{cls}">{sign}{value:.2f}%</span>'


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

def sma(series, window):
    return series.rolling(window=window, min_periods=window).mean()


def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def bollinger_bands(series, window=20, num_std=2):
    mid = sma(series, window)
    std = series.rolling(window=window, min_periods=window).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    return upper, mid, lower


def rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50)


def macd(series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def vwap(data):
    typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
    cum_vol = data["Volume"].cumsum().replace(0, np.nan)
    return (typical_price * data["Volume"]).cumsum() / cum_vol


# ============================================================
# CHART BUILDERS
# ============================================================

def create_price_chart(data, ticker, overlays=None, show_volume=True,
                       show_rsi=False, show_macd=False):
    """Interactive professional multi-panel financial chart."""

    overlays = overlays or []

    chart_data = data.copy()

    if chart_data.empty:
        return go.Figure()

    required_columns = ["Open", "High", "Low", "Close"]
    chart_data = chart_data.dropna(subset=required_columns)

    if chart_data.empty:
        return go.Figure()

    close = chart_data["Close"]

    # ---------------------------------------------------------
    # Determine number of chart panels
    # ---------------------------------------------------------
    rows = 1
    row_heights = [0.62]
    subplot_titles = ["Price"]

    if show_volume:
        rows += 1
        row_heights.append(0.14)
        subplot_titles.append("Volume")

    if show_rsi:
        rows += 1
        row_heights.append(0.12)
        subplot_titles.append("RSI (14)")

    if show_macd:
        rows += 1
        row_heights.append(0.12)
        subplot_titles.append("MACD")

    # ---------------------------------------------------------
    # Create shared interactive chart
    # ---------------------------------------------------------
    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=row_heights,
        subplot_titles=subplot_titles
    )

    # ---------------------------------------------------------
    # Candlestick price chart
    # ---------------------------------------------------------
    fig.add_trace(
        go.Candlestick(
            x=chart_data.index,
            open=chart_data["Open"],
            high=chart_data["High"],
            low=chart_data["Low"],
            close=chart_data["Close"],
            name=ticker,
            increasing_line_color="#32d583",
            decreasing_line_color="#ff6b6b",
            increasing_fillcolor="#32d583",
            decreasing_fillcolor="#ff6b6b",
            whiskerwidth=0.5,
            hoverlabel=dict(namelength=-1)
        ),
        row=1,
        col=1
    )

    # ---------------------------------------------------------
    # Moving-average / overlay colours
    # ---------------------------------------------------------
    overlay_colors = {
        "SMA 20": "#f5a623",
        "SMA 50": "#4a9eff",
        "SMA 100": "#c792ea",
        "SMA 200": "#ff6b6b",
        "EMA 20": "#32d583",
        "EMA 50": "#00d4ff",
        "VWAP": "#e0e0e0",
    }

    # ---------------------------------------------------------
    # Moving averages
    # ---------------------------------------------------------
    if "SMA 20" in overlays:
        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=sma(close, 20),
                name="SMA 20",
                mode="lines",
                line=dict(width=1.2, color=overlay_colors["SMA 20"]),
                hovertemplate="SMA 20: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

    if "SMA 50" in overlays:
        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=sma(close, 50),
                name="SMA 50",
                mode="lines",
                line=dict(width=1.2, color=overlay_colors["SMA 50"]),
                hovertemplate="SMA 50: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

    if "SMA 100" in overlays:
        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=sma(close, 100),
                name="SMA 100",
                mode="lines",
                line=dict(width=1.2, color=overlay_colors["SMA 100"]),
                hovertemplate="SMA 100: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

    if "SMA 200" in overlays:
        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=sma(close, 200),
                name="SMA 200",
                mode="lines",
                line=dict(width=1.2, color=overlay_colors["SMA 200"]),
                hovertemplate="SMA 200: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

    if "EMA 20" in overlays:
        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=ema(close, 20),
                name="EMA 20",
                mode="lines",
                line=dict(width=1.2, color=overlay_colors["EMA 20"]),
                hovertemplate="EMA 20: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

    if "EMA 50" in overlays:
        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=ema(close, 50),
                name="EMA 50",
                mode="lines",
                line=dict(width=1.2, color=overlay_colors["EMA 50"]),
                hovertemplate="EMA 50: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

    # ---------------------------------------------------------
    # Bollinger Bands
    # ---------------------------------------------------------
    if "Bollinger Bands" in overlays:
        upper, mid, lower = bollinger_bands(close)

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=upper,
                name="BB Upper",
                mode="lines",
                line=dict(width=1, color="#7d8590", dash="dot"),
                hovertemplate="BB Upper: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=lower,
                name="BB Lower",
                mode="lines",
                line=dict(width=1, color="#7d8590", dash="dot"),
                fill="tonexty",
                fillcolor="rgba(125,133,144,0.08)",
                hovertemplate="BB Lower: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=mid,
                name="BB Middle",
                mode="lines",
                line=dict(width=1, color="#9aa0a6", dash="dash"),
                hovertemplate="BB Middle: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

    # ---------------------------------------------------------
    # VWAP
    # ---------------------------------------------------------
    if "VWAP" in overlays:
        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=vwap(chart_data),
                name="VWAP",
                mode="lines",
                line=dict(
                    width=1.2,
                    color=overlay_colors["VWAP"],
                    dash="dash"
                ),
                hovertemplate="VWAP: %{y:.2f}<extra></extra>"
            ),
            row=1,
            col=1
        )

    # ---------------------------------------------------------
    # Volume
    # ---------------------------------------------------------
    current_row = 1

    if show_volume:
        current_row += 1

        volume_colors = np.where(
            chart_data["Close"] >= chart_data["Open"],
            "#32d583",
            "#ff6b6b"
        )

        fig.add_trace(
            go.Bar(
                x=chart_data.index,
                y=chart_data["Volume"],
                name="Volume",
                marker_color=volume_colors,
                showlegend=False,
                hovertemplate="Volume: %{y:,.0f}<extra></extra>"
            ),
            row=current_row,
            col=1
        )

    # ---------------------------------------------------------
    # RSI
    # ---------------------------------------------------------
    if show_rsi:
        current_row += 1

        rsi_series = rsi(close)

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=rsi_series,
                name="RSI",
                mode="lines",
                line=dict(width=1.3, color="#c792ea"),
                showlegend=False,
                hovertemplate="RSI: %{y:.2f}<extra></extra>"
            ),
            row=current_row,
            col=1
        )

        fig.add_hline(
            y=70,
            line_dash="dot",
            line_color="#ff6b6b",
            row=current_row,
            col=1
        )

        fig.add_hline(
            y=30,
            line_dash="dot",
            line_color="#32d583",
            row=current_row,
            col=1
        )

        fig.update_yaxes(
            range=[0, 100],
            row=current_row,
            col=1
        )

    # ---------------------------------------------------------
    # MACD
    # ---------------------------------------------------------
    if show_macd:
        current_row += 1

        macd_line, signal_line, hist = macd(close)

        hist_colors = np.where(
            hist >= 0,
            "#32d583",
            "#ff6b6b"
        )

        fig.add_trace(
            go.Bar(
                x=chart_data.index,
                y=hist,
                name="Histogram",
                marker_color=hist_colors,
                showlegend=False,
                hovertemplate="Histogram: %{y:.3f}<extra></extra>"
            ),
            row=current_row,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=macd_line,
                name="MACD",
                mode="lines",
                line=dict(width=1.2, color="#4a9eff"),
                hovertemplate="MACD: %{y:.3f}<extra></extra>"
            ),
            row=current_row,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=signal_line,
                name="Signal",
                mode="lines",
                line=dict(width=1.2, color="#f5a623"),
                hovertemplate="Signal: %{y:.3f}<extra></extra>"
            ),
            row=current_row,
            col=1
        )

    # ---------------------------------------------------------
    # Professional interactive layout
    # ---------------------------------------------------------
    fig.update_layout(
        template="plotly_dark",
        height=520 + 120 * (rows - 1),
        margin=dict(l=20, r=20, t=55, b=20),
        dragmode="pan",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0
        ),
        autosize=True,
        modebar_remove=[
            "lasso2d",
            "select2d"
        ],
        hoverdistance=50,
        spikedistance=1000
    )

    # ---------------------------------------------------------
    # X-axis interaction
    # ---------------------------------------------------------
    for r in range(1, rows + 1):
        fig.update_xaxes(
            row=r,
            col=1,
            fixedrange=False,
            rangeslider_visible=False,
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            showline=True,
            type="date"
        )

    # ---------------------------------------------------------
    # Y-axis interaction
    # ---------------------------------------------------------
    for r in range(1, rows + 1):
        fig.update_yaxes(
            row=r,
            col=1,
            fixedrange=False,
            showspikes=True,
            spikemode="across",
            spikesnap="cursor"
        )

    # ---------------------------------------------------------
    # Candlestick hover information
    # ---------------------------------------------------------
    fig.update_traces(
        selector=dict(type="candlestick"),
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b>"
            "<br>Open: %{open:.2f}"
            "<br>High: %{high:.2f}"
            "<br>Low: %{low:.2f}"
            "<br>Close: %{close:.2f}"
            "<extra></extra>"
        )
    )

    return fig


def create_trend_chart(series, title, y_title="Value (INR )"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[str(c)[:10] for c in series.index][::-1], y=series.values[::-1],
        mode="lines+markers", line=dict(width=2, color="#4a9eff"),
        marker=dict(size=6),
    ))
    fig.update_layout(
        title=title, template="plotly_dark", height=320,
        yaxis_title=y_title, margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def create_allocation_pie(labels, values, title="Portfolio Allocation"):
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.45)])
    fig.update_layout(template="plotly_dark", height=380, title=title,
                       margin=dict(l=20, r=20, t=40, b=20))
    return fig


def create_bar_comparison(categories, series_dict, title, y_title=""):
    fig = go.Figure()
    for name, values in series_dict.items():
        fig.add_trace(go.Bar(name=name, x=categories, y=values))
    fig.update_layout(template="plotly_dark", height=380, title=title,
                       barmode="group", yaxis_title=y_title,
                       margin=dict(l=20, r=20, t=40, b=20))
    return fig


# ============================================================
# FINANCIAL CALCULATIONS
# ============================================================

def compute_returns_table(history):
    """Return a dict of {label: pct_return} for the standard lookback windows."""
    out = {}
    if history is None or history.empty:
        return out
    close = history["Close"].dropna()
    last = close.iloc[-1]
    for label, periods in RETURN_WINDOWS:
        if len(close) > periods:
            base = close.iloc[-(periods + 1)]
            out[label] = (last / base - 1) * 100 if base else None
        else:
            out[label] = None

    # YTD
    this_year = close[close.index.year == close.index[-1].year]
    if len(this_year) > 1:
        out["YTD"] = (last / this_year.iloc[0] - 1) * 100
    else:
        out["YTD"] = None

    return out


def compute_fundamental_ratios(info, income_df, balance_df, cashflow_df, asset_class="EQUITY"):
    """Assemble a dict of ratio categories from info + statements (N/A when missing)."""
    if not supports_metric(asset_class, "P/E", "fundamental_metrics"):
        return {
            "valuation": {key: None for key in ("Market Cap", "Enterprise Value", "P/E (TTM)", "Forward P/E", "P/B", "P/S", "EV/EBITDA", "EV/Revenue", "PEG Ratio")},
            "profitability": {key: None for key in ("Gross Margin", "Operating Margin", "Net Margin", "ROE", "ROA", "ROIC")},
            "growth": {key: None for key in ("Revenue Growth (YoY)", "Earnings Growth (YoY)", "EPS (TTM)", "EPS (Forward)")},
            "health": {key: None for key in ("Total Debt", "Cash", "Net Debt", "Debt/Equity", "Current Ratio", "Quick Ratio", "Interest Coverage")},
            "per_share": {key: None for key in ("EPS", "Book Value/Share", "Revenue/Share", "Dividend/Share")},
            "efficiency": {key: None for key in ("Asset Turnover", "Debt/Assets")},
        }

    ratios = {}

    revenue = safe_value(info, "totalRevenue") or get_statement_value(income_df, ["Total Revenue", "TotalRevenue"])
    net_income = safe_value(info, "netIncomeToCommon") or get_statement_value(income_df, ["Net Income", "NetIncome"])
    gross_profit = get_statement_value(income_df, ["Gross Profit", "GrossProfit"])
    ebit = get_statement_value(income_df, ["EBIT", "Ebit", "Operating Income"])
    ebitda = safe_value(info, "ebitda") or get_statement_value(income_df, ["EBITDA"])

    total_assets = get_statement_value(balance_df, ["Total Assets", "TotalAssets"])
    total_equity = get_statement_value(balance_df, ["Total Equity Gross Minority Interest",
                                                      "Stockholders Equity", "Common Stock Equity"])
    total_liabilities = get_statement_value(balance_df, ["Total Liabilities Net Minority Interest",
                                                           "Total Liab"])
    current_assets = get_statement_value(balance_df, ["Current Assets", "Total Current Assets"])
    current_liabilities = get_statement_value(balance_df, ["Current Liabilities", "Total Current Liabilities"])
    inventory = get_statement_value(balance_df, ["Inventory"])
    total_debt = safe_value(info, "totalDebt") or get_statement_value(balance_df, ["Total Debt"])
    cash = safe_value(info, "totalCash") or get_statement_value(balance_df, ["Cash And Cash Equivalents"])

    interest_expense = get_statement_value(income_df, ["Interest Expense"])

    def ratio(a, b):
        try:
            if a is None or b is None or b == 0:
                return None
            return a / b
        except Exception:
            return None

    ratios["valuation"] = {
        "Market Cap": safe_value(info, "marketCap"),
        "Enterprise Value": safe_value(info, "enterpriseValue"),
        "P/E (TTM)": safe_value(info, "trailingPE"),
        "Forward P/E": safe_value(info, "forwardPE"),
        "P/B": safe_value(info, "priceToBook"),
        "P/S": safe_value(info, "priceToSalesTrailing12Months"),
        "EV/EBITDA": safe_value(info, "enterpriseToEbitda"),
        "EV/Revenue": safe_value(info, "enterpriseToRevenue"),
        "PEG Ratio": safe_value(info, "pegRatio"),
    }

    ratios["profitability"] = {
        "Gross Margin": ratio(gross_profit, revenue),
        "Operating Margin": safe_value(info, "operatingMargins") or ratio(ebit, revenue),
        "Net Margin": safe_value(info, "profitMargins") or ratio(net_income, revenue),
        "ROE": safe_value(info, "returnOnEquity") or ratio(net_income, total_equity),
        "ROA": safe_value(info, "returnOnAssets") or ratio(net_income, total_assets),
        "ROIC": ratio(ebit, (total_debt or 0) + (total_equity or 0)) if (total_debt or total_equity) else None,
    }

    ratios["growth"] = {
        "Revenue Growth (YoY)": safe_value(info, "revenueGrowth"),
        "Earnings Growth (YoY)": safe_value(info, "earningsGrowth"),
        "EPS (TTM)": safe_value(info, "trailingEps"),
        "EPS (Forward)": safe_value(info, "forwardEps"),
    }

    ratios["health"] = {
        "Total Debt": total_debt,
        "Cash": cash,
        "Net Debt": (total_debt - cash) if (total_debt is not None and cash is not None) else None,
        "Debt/Equity": ratio(total_debt, total_equity),
        "Current Ratio": ratio(current_assets, current_liabilities),
        "Quick Ratio": ratio((current_assets - (inventory or 0)) if current_assets is not None else None,
                              current_liabilities),
        "Interest Coverage": ratio(ebit, interest_expense),
    }

    ratios["per_share"] = {
        "EPS": safe_value(info, "trailingEps"),
        "Book Value/Share": safe_value(info, "bookValue"),
        "Revenue/Share": safe_value(info, "revenuePerShare"),
        "Dividend/Share": safe_value(info, "lastDividendValue"),
    }

    ratios["efficiency"] = {
        "Asset Turnover": ratio(revenue, total_assets),
        "Debt/Assets": ratio(total_debt, total_assets),
    }

    return ratios


def calculate_var_history(returns, confidence=0.95):
    if returns is None or len(returns) == 0:
        return None
    return returns.quantile(1 - confidence)


def calculate_max_drawdown(close):
    cumulative = close / close.cummax()
    drawdown = cumulative - 1
    return drawdown.min(), drawdown


def calculate_sharpe(returns, risk_free_annual=0.065, periods_per_year=252):
    if (
        returns is None
        or len(returns) < 2
        or returns.std() == 0
        or risk_free_annual is None
        or periods_per_year is None
    ):
        return None
    excess = returns.mean() * periods_per_year - risk_free_annual
    return excess / (returns.std() * np.sqrt(periods_per_year))


def calculate_sortino(returns, risk_free_annual=0.065, periods_per_year=252):
    if (
        returns is None
        or len(returns) < 2
        or risk_free_annual is None
        or periods_per_year is None
    ):
        return None
    downside = returns[returns < 0]
    if len(downside) == 0 or downside.std() == 0:
        return None
    excess = returns.mean() * periods_per_year - risk_free_annual
    downside_dev = downside.std() * np.sqrt(periods_per_year)
    return excess / downside_dev


def calculate_beta(stock_returns, market_returns):
    combined = pd.concat([stock_returns, market_returns], axis=1).dropna()
    if len(combined) < 10:
        return None
    covariance = np.cov(combined.iloc[:, 0], combined.iloc[:, 1])[0][1]
    market_variance = np.var(combined.iloc[:, 1])
    if market_variance == 0:
        return None
    return covariance / market_variance


def run_dcf(revenue, ebitda_margin, tax_rate, capex_pct, wacc, terminal_growth,
            growth_rate, years, net_debt, shares_outstanding, da_pct=0.04, wc_pct=0.02):
    """Simple 5-10yr FCFF DCF. Returns dict with EV, equity value, fair value/share."""
    if not revenue or not shares_outstanding or wacc <= terminal_growth:
        return None

    projected_fcff = []
    rev = revenue
    for year in range(1, years + 1):
        rev = rev * (1 + growth_rate)
        ebitda = rev * ebitda_margin
        da = rev * da_pct
        ebit = ebitda - da
        nopat = ebit * (1 - tax_rate)
        capex = rev * capex_pct
        delta_wc = rev * wc_pct
        fcff = nopat + da - capex - delta_wc
        discount_factor = (1 + wacc) ** year
        projected_fcff.append({
            "year": year, "revenue": rev, "ebitda": ebitda, "fcff": fcff,
            "discounted_fcff": fcff / discount_factor,
        })

    terminal_fcff = projected_fcff[-1]["fcff"] * (1 + terminal_growth)
    terminal_value = terminal_fcff / (wacc - terminal_growth)
    discounted_terminal_value = terminal_value / ((1 + wacc) ** years)

    enterprise_value = sum(p["discounted_fcff"] for p in projected_fcff) + discounted_terminal_value
    equity_value = enterprise_value - (net_debt or 0)
    fair_value_per_share = equity_value / shares_outstanding

    return {
        "projections": projected_fcff,
        "terminal_value": terminal_value,
        "discounted_terminal_value": discounted_terminal_value,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "fair_value_per_share": fair_value_per_share,
    }


def dcf_sensitivity(revenue, ebitda_margin, tax_rate, capex_pct, growth_rate, years,
                     net_debt, shares_outstanding, wacc_range, tg_range):
    """Grid of fair-value-per-share across WACC x terminal-growth combinations."""
    grid = []
    for wacc in wacc_range:
        row = []
        for tg in tg_range:
            if wacc <= tg:
                row.append(None)
                continue
            result = run_dcf(revenue, ebitda_margin, tax_rate, capex_pct, wacc, tg,
                              growth_rate, years, net_debt, shares_outstanding)
            row.append(result["fair_value_per_share"] if result else None)
        grid.append(row)
    return grid


# ============================================================
# SESSION STATE
# ============================================================

if "ticker" not in st.session_state:
    st.session_state["ticker"] = "RELIANCE.NS"
if "active_module" not in st.session_state:
    st.session_state["active_module"] = "Dashboard"
elif st.session_state["active_module"] == "Watchlist":
    st.session_state["active_module"] = "Dashboard"
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
if "recently_viewed" not in st.session_state:
    st.session_state["recently_viewed"] = []
if "chart_timeframe" not in st.session_state:
    st.session_state["chart_timeframe"] = "1Y"
if "portfolio_rows" not in st.session_state:
    st.session_state["portfolio_rows"] = [
        {"ticker": "RELIANCE", "qty": 10},
        {"ticker": "TCS", "qty": 5},
    ]


def remember_ticker(ticker):
    st.session_state["ticker"] = ticker
    rv = st.session_state["recently_viewed"]
    if ticker in rv:
        rv.remove(ticker)
    rv.insert(0, ticker)
    st.session_state["recently_viewed"] = rv[:8]


def go_to_module(name):
    st.session_state["active_module"] = name


def get_active_alerts():
    alerts = []
    current_module = st.session_state.get("active_module", "Dashboard")

    try:
        selected_ticker = st.session_state.get("ticker")
        if selected_ticker:
            hist = get_history(selected_ticker, "5d", "1d")
            if not hist.empty and len(hist) > 1:
                last = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                move = ((last - prev) / prev * 100) if prev else 0.0
                if abs(move) >= 2.5:
                    alerts.append({
                        "level": "warning" if move > 0 else "negative",
                        "message": f"{display_ticker(selected_ticker)} moved {move:+.2f}% over the last 5 sessions."
                    })
    except Exception:
        pass

    if current_module == "Portfolio":
        try:
            portfolio = st.session_state.get("portfolio_rows", [])
            if portfolio:
                alerts.append({
                    "level": "warning",
                    "message": "Portfolio contains active holdings and should be reviewed before major risk changes."
                })
        except Exception:
            pass

    return alerts


def render_terminal_action_popovers():
    current_module = st.session_state.get("active_module", "Dashboard")
    selected_ticker = st.session_state.get("ticker")
    alerts = get_active_alerts()

    with st.container(key="apex-fixed-workspace"):
        with st.popover("WORKSPACE", use_container_width=False):
            st.markdown("<div class='apex-popover-title'>WORKSPACE</div>", unsafe_allow_html=True)
            st.caption("Current module")
            st.write(current_module)
            st.caption("Selected ticker")
            st.write(selected_ticker or "No ticker selected")
            if st.button("Open Dashboard", key="workspace_dashboard", width="stretch"):
                go_to_module("Dashboard")
                st.rerun()

    with st.container(key="apex-fixed-alerts"):
        with st.popover(f"ALERTS ({len(alerts)})", use_container_width=False):
            st.markdown("<div class='apex-popover-title'>ALERTS</div>", unsafe_allow_html=True)
            if alerts:
                for alert in alerts:
                    message = escape(str(alert.get("message", "")))
                    st.markdown(f"<div class='apex-alert-item'>{message}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='apex-alert-empty'>NO ACTIVE ALERTS</div>", unsafe_allow_html=True)

    with st.container(key="apex-fixed-user"):
        with st.popover(" ", use_container_width=False):
            st.markdown("<div class='apex-popover-title'>SESSION</div>", unsafe_allow_html=True)
            st.write(f"Session module: {current_module}")
            st.write(f"Selected ticker: {selected_ticker or 'N/A'}")
            st.write("Yahoo Finance: selected security loaded" if selected_ticker else "Yahoo Finance: ready")
            st.write("Gemini status: not verified in this session")


# ============================================================

# ============================================================
# FINAL_TABLE_VISIBILITY_RENDERER_V2
# Professional universal table renderer
# ============================================================

def render_dataframe(data, *args, **kwargs):
    """
    Professional universal table renderer.

    Purpose:
    - Prevent text clipping.
    - Wrap long values inside cells.
    - Preserve complete financial statement labels.
    - Preserve complete reporting periods.
    - Make Industry / Sector / Company / Particulars readable.
    - Keep numeric columns compact.
    - Allow horizontal scrolling only when genuinely required.
    - Maintain a clean terminal-style appearance.
    """

    if data is None:
        st.info("No table data available.")
        return

    try:
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
    except Exception:
        st.info("Unable to display this table.")
        return

    if data.empty:
        st.info("No data available.")
        return

    df = data.copy()

    # --------------------------------------------------------
    # INDEX / PARTICULARS
    # --------------------------------------------------------

    hide_index = kwargs.get("hide_index", False)

    if hide_index:
        df = df.reset_index(drop=True)
    else:
        index_name = df.index.name

        if index_name is None or str(index_name).strip() == "":
            index_name = "Particulars"

        df = df.reset_index()

        first_column = str(df.columns[0])

        if first_column == "index":
            df = df.rename(
                columns={
                    df.columns[0]: str(index_name)
                }
            )

    # --------------------------------------------------------
    # CLEAN COLUMN NAMES
    # --------------------------------------------------------

    cleaned_columns = []

    for column in df.columns:
        name = str(column)

        if name.strip().lower() == "index":
            name = "Particulars"

        cleaned_columns.append(name)

    df.columns = cleaned_columns

    # --------------------------------------------------------
    # HTML ESCAPE
    # --------------------------------------------------------

    _html = __import__("html")

    # --------------------------------------------------------
    # COLUMN CLASSIFICATION
    # --------------------------------------------------------

    descriptive_keywords = (
        "particular",
        "industry",
        "sector",
        "company",
        "security",
        "instrument",
        "description",
        "name",
        "business",
        "category",
        "classification",
        "exchange",
        "country",
        "region",
        "currency",
        "employee",
        "type",
        "status",
        "comment",
        "reason",
        "signal",
        "analysis",
        "message",
        "metric",
        "factor",
        "criterion",
        "criteria",
        "company name",
        "security name",
    )

    def _is_descriptive(column_name):
        text = str(column_name).strip().lower()
        return any(keyword in text for keyword in descriptive_keywords)

    # --------------------------------------------------------
    # DISPLAY VALUES
    # --------------------------------------------------------

    def _display_value(value):

        try:
            if pd.isna(value):
                return "N/A"
        except Exception:
            pass

        if isinstance(value, pd.Timestamp):
            return value.strftime("%Y-%m-%d")

        if isinstance(value, float):
            if value != value:
                return "N/A"

            # Keep existing numeric precision sensible.
            if abs(value) >= 1000000:
                return f"{value:,.0f}"

            if abs(value) >= 1000:
                return f"{value:,.2f}"

            if abs(value) >= 1:
                return f"{value:,.4f}"

            return f"{value:.6f}"

        if isinstance(value, int):
            return f"{value:,}"

        return str(value)

    # --------------------------------------------------------
    # TABLE HTML
    # --------------------------------------------------------

    headers = []

    for column in df.columns:

        label = _html.escape(str(column))

        if _is_descriptive(column):
            headers.append(
                f'<th class="terminal-th terminal-descriptive">{label}</th>'
            )
        else:
            headers.append(
                f'<th class="terminal-th terminal-numeric">{label}</th>'
            )

    rows = []

    for _, row in df.iterrows():

        cells = []

        for column in df.columns:

            value = _html.escape(
                _display_value(row[column])
            )

            if _is_descriptive(column):
                cell_class = "terminal-td terminal-descriptive"
            else:
                cell_class = "terminal-td terminal-numeric"

            cells.append(
                f'<td class="{cell_class}">{value}</td>'
            )

        rows.append(
            "<tr>" + "".join(cells) + "</tr>"
        )

    table_html = f"""
    <style>

    .terminal-table-wrapper {{
        width: 100%;
        max-width: 100%;
        overflow-x: auto;
        overflow-y: visible;
        margin: 8px 0 18px 0;
        border: 1px solid rgba(148,163,184,0.20);
        border-radius: 10px;
        background: rgba(15,23,42,0.42);
        -webkit-overflow-scrolling: touch;
    }}

    .terminal-data-table {{
        border-collapse: separate;
        border-spacing: 0;
        width: max-content;
        min-width: 100%;
        table-layout: auto;
        font-family: Inter, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
        font-size: 13px;
        line-height: 1.45;
        color: #E5E7EB;
    }}

    .terminal-data-table thead th {{
        position: sticky;
        top: 0;
        z-index: 2;
        background: #111827;
        color: #F8FAFC;
        font-weight: 700;
        font-size: 11px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        border-bottom: 1px solid rgba(148,163,184,0.30);
        padding: 11px 13px;
        text-align: left;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: normal;
        vertical-align: middle;
    }}

    .terminal-data-table tbody td {{
        padding: 10px 13px;
        border-bottom: 1px solid rgba(148,163,184,0.12);
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: normal;
        vertical-align: top;
        max-width: none;
    }}

    .terminal-data-table tbody tr:last-child td {{
        border-bottom: none;
    }}

    .terminal-data-table tbody tr:hover td {{
        background: rgba(59,130,246,0.08);
    }}

    .terminal-data-table .terminal-descriptive {{
        min-width: 220px;
        width: 300px;
        max-width: 420px;
        text-align: left;
    }}

    .terminal-data-table .terminal-numeric {{
        min-width: 115px;
        width: 150px;
        text-align: right;
        white-space: normal;
        overflow-wrap: anywhere;
    }}

    /* Financial statement row labels */
    .terminal-data-table th:first-child,
    .terminal-data-table td:first-child {{
        min-width: 250px;
        width: 320px;
        max-width: 430px;
        text-align: left;
        font-weight: 600;
    }}

    /* Prevent extremely long strings from creating giant cells */
    .terminal-data-table td {{
        overflow-wrap: anywhere;
        word-break: break-word;
    }}

    @media (max-width: 1100px) {{

        .terminal-data-table {{
            font-size: 12px;
        }}

        .terminal-data-table .terminal-descriptive {{
            min-width: 190px;
            width: 240px;
        }}

        .terminal-data-table .terminal-numeric {{
            min-width: 105px;
            width: 125px;
        }}

        .terminal-data-table th:first-child,
        .terminal-data-table td:first-child {{
            min-width: 210px;
            width: 260px;
        }}
    }}

    @media (max-width: 700px) {{

        .terminal-data-table {{
            font-size: 12px;
        }}

        .terminal-data-table thead th {{
            padding: 9px 10px;
            font-size: 10px;
        }}

        .terminal-data-table tbody td {{
            padding: 9px 10px;
        }}

        .terminal-data-table .terminal-descriptive {{
            min-width: 180px;
            width: 220px;
        }}

        .terminal-data-table .terminal-numeric {{
            min-width: 100px;
            width: 120px;
        }}

        .terminal-data-table th:first-child,
        .terminal-data-table td:first-child {{
            min-width: 200px;
            width: 240px;
        }}
    }}

    </style>

    <div class="terminal-table-wrapper">

        <table class="terminal-data-table">

            <thead>
                <tr>
                    {"".join(headers)}
                </tr>
            </thead>

            <tbody>
                {"".join(rows)}
            </tbody>

        </table>

    </div>
    """

    st.markdown(
        table_html,
        unsafe_allow_html=True
    )


# ============================================================
# END FINAL_TABLE_VISIBILITY_RENDERER_V2
# ============================================================


# SIDEBAR NAVIGATION AND MARKET STATUS
# ============================================================

st.sidebar.title(" Terminal")
st.sidebar.markdown("### Navigate")

module = st.sidebar.radio(
    "Select module",
    NAV_MODULES,
    index=NAV_MODULES.index(st.session_state.get("active_module", "Dashboard")),
    label_visibility="collapsed",
    key="nav_radio",
)
st.session_state["active_module"] = module

st.sidebar.divider()
st.sidebar.markdown("### Quick Search")
quick_ticker = st.sidebar.text_input(
    "Enter Ticker / Company",
    placeholder="e.g. Bajaj, Tata Consultancy Services, INFY",
    key="quick_search_input",
    label_visibility="collapsed",
)
quick_matches = search_companies(quick_ticker)
quick_selected_ticker = ""
if quick_ticker.strip() and quick_matches:
    quick_labels = [f"{name}  •  {display_ticker(ticker)}" for name, ticker in quick_matches]
    quick_choice = st.sidebar.selectbox("Matching companies", quick_labels, key="quick_search_matches")
    quick_selected_ticker = quick_matches[quick_labels.index(quick_choice)][1]
elif quick_ticker.strip():
    st.sidebar.caption("No match in the local catalog - you can still enter a raw Yahoo/NSE ticker.")

if st.sidebar.button("Analyze", width="stretch", type="primary") and quick_ticker:
    remember_ticker(quick_selected_ticker or normalize_ticker(quick_ticker))
    go_to_module("Company Analysis")
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("### Market News")
if st.sidebar.button("Refresh news", key="refresh_sidebar_market_news", width="stretch"):
    get_news_feed.clear()
    st.rerun()

for news_section, news_query in [
    ("Indian Markets", "NSE OR Nifty OR Sensex stock market India"),
    ("Corporate News", "Indian companies earnings stocks corporate"),
]:
    st.sidebar.caption(news_section)
    sidebar_news_items = get_news_feed(news_query, limit=2)
    if sidebar_news_items:
        for article in sidebar_news_items:
            st.sidebar.markdown(
                f"<a href='{escape(article['link'])}' target='_blank' "
                f"class='apex-sidebar-news-link'>{escape(article['title'])}</a>",
                unsafe_allow_html=True,
            )
    else:
        st.sidebar.caption("No recent news available.")

now_ist = datetime.now(IST)
market_open = (now_ist.weekday() < 5) and (
    (now_ist.hour > 9 or (now_ist.hour == 9 and now_ist.minute >= 15))
    and (now_ist.hour < 15 or (now_ist.hour == 15 and now_ist.minute <= 30))
)

render_terminal_action_popovers()

def get_listing_currency(ticker):
    """
    Determine the currency used by the listing/market represented
    by the Yahoo Finance ticker.

    Indian .NS/.BO securities -> INR
    US securities -> USD
    Japanese .T securities -> JPY
    UK .L securities -> GBP
    Hong Kong .HK securities -> HKD
    European Yahoo suffixes -> EUR where appropriate
    Crypto/commodity/fixed-income symbols have explicit handling.
    """

    t = str(ticker or "").strip().upper()

    # Indian listings
    if t.endswith(".NS") or t.endswith(".BO"):
        return "INR"

    # Japan
    if t.endswith(".T"):
        return "JPY"

    # United Kingdom
    if t.endswith(".L"):
        return "GBP"

    # Hong Kong
    if t.endswith(".HK"):
        return "HKD"

    # Australia
    if t.endswith(".AX"):
        return "AUD"

    # Canada
    if t.endswith(".TO") or t.endswith(".V"):
        return "CAD"

    # Germany
    if t.endswith(".DE"):
        return "EUR"

    # France
    if t.endswith(".PA"):
        return "EUR"

    # Netherlands
    if t.endswith(".AS"):
        return "EUR"

    # Switzerland
    if t.endswith(".SW"):
        return "CHF"

    # South Korea
    if t.endswith(".KS") or t.endswith(".KQ"):
        return "KRW"

    # Singapore
    if t.endswith(".SI"):
        return "SGD"

    # Brazil
    if t.endswith(".SA"):
        return "BRL"

    # Crypto INR assets
    if t.endswith("-INR"):
        return "INR"

    # Crypto USD assets
    if t.endswith("-USD"):
        return "USD"

    # Yahoo commodities are normally quoted in USD
    if t.endswith("=F"):
        return "USD"

    # Yahoo US securities generally have no suffix
    return "USD"


def currency_symbol(currency):
    symbols = {
        "INR": "INR ",
        "USD": "$",
        "JPY": "¥",
        "GBP": "£",
        "EUR": "EUR ",
        "HKD": "HK$",
        "AUD": "A$",
        "CAD": "C$",
        "CHF": "CHF ",
        "KRW": "KRW ",
        "SGD": "S$",
        "BRL": "R$",
    }
    return symbols.get(currency, currency + " ")


def format_master_currency(value, ticker, decimals=2):
    """Format a security price in its master-universe currency, without fallback guesses."""
    record = UNIVERSE_BY_TICKER.get(str(ticker or "").strip(), {})
    currency = str(record.get("currency", "") or "").strip().upper()
    if not currency:
        return "DATA NOT AVAILABLE"
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "DATA NOT AVAILABLE"
    if not np.isfinite(amount):
        return "DATA NOT AVAILABLE"
    return f"{currency_symbol(currency)}{amount:,.{decimals}f}"


def format_master_currency_scale(value, ticker):
    """Scale a financial amount using its master-universe quote currency."""
    record = UNIVERSE_BY_TICKER.get(str(ticker or "").strip(), {})
    currency = str(record.get("currency", "") or "").strip().upper()
    if not currency:
        return "DATA NOT AVAILABLE"
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "DATA NOT AVAILABLE"
    if not np.isfinite(amount):
        return "DATA NOT AVAILABLE"
    prefix = currency_symbol(currency)
    abs_amount = abs(amount)
    for threshold, divisor, suffix in (
        (1_000_000_000_000, 1_000_000_000_000, "T"),
        (1_000_000_000, 1_000_000_000, "B"),
        (1_000_000, 1_000_000, "M"),
        (1_000, 1_000, "K"),
    ):
        if abs_amount >= threshold:
            return f"{prefix}{amount / divisor:,.2f} {suffix}"
    return f"{prefix}{amount:,.2f}"


def format_local_money(value, ticker, decimals=2):
    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"
    except Exception:
        pass

    try:
        amount = float(value)
    except Exception:
        return "N/A"

    curr = get_listing_currency(ticker)
    sym = currency_symbol(curr)

    return f"{sym}{amount:,.{decimals}f}"


def format_local_scale(value, ticker):
    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"
    except Exception:
        pass

    try:
        amount = float(value)
    except Exception:
        return "N/A"

    curr = get_listing_currency(ticker)
    sym = currency_symbol(curr)

    abs_amount = abs(amount)

    if abs_amount >= 1_000_000_000_000:
        return f"{sym}{amount / 1_000_000_000_000:,.2f} T"
    elif abs_amount >= 1_000_000_000:
        return f"{sym}{amount / 1_000_000_000:,.2f} B"
    elif abs_amount >= 1_000_000:
        return f"{sym}{amount / 1_000_000:,.2f} M"
    elif abs_amount >= 1_000:
        return f"{sym}{amount / 1_000:,.2f} K"

    return f"{sym}{amount:,.2f}"


def generate_genai_analysis(title, facts):
    """
    Generate an AI interpretation from the actual numbers produced
    by the terminal.

    Uses OPENAI_API_KEY from the environment or Streamlit secrets.
    The calculation itself remains deterministic; GenAI only explains
    the calculated results.
    """

    try:
        import os
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY")
            except Exception:
                api_key = None

        if not api_key:
            st.info(
                "GenAI analysis is ready, but OPENAI_API_KEY is not configured. "
                "Add your OpenAI API key to enable the AI interpretation."
            )
            return

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are the financial-analysis assistant inside a financial analysis terminal.

Generate a concise but useful analyst-style interpretation based ONLY on
the supplied calculations and data.

Do not invent numbers.
Do not fabricate company facts.
Do not present the answer as a buy/sell recommendation.

Explain:
1. What the numbers indicate.
2. Relative valuation / DCF implications.
3. The strongest positive signals.
4. The biggest risks or warning signals.
5. What an analyst should investigate further.

Clearly distinguish calculated outputs from interpretation.

TITLE:
{title}

CALCULATED DATA:
{facts}
"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a disciplined financial analysis assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=700,
        )

        answer = response.choices[0].message.content

        if answer:
            st.markdown("#### GenAI Analysis")
            st.markdown(answer)

    except ImportError:
        return None

    except Exception:
        return None



if module == "Dashboard":

    render_apex_page_header(
        "Dashboard",
        "Live market overview, watchlist and sector performance",
        "NSE Market Open" if market_open else "NSE Market Closed",
        datetime.now(IST).strftime("%a %d %b %Y • %H:%M IST")
    )

    render_dashboard_system_map()

    dashboard_data = get_dashboard_market_data(
        tuple(st.session_state["watchlist"])
    )

    snapshot_cards = []
    for label, symbol in INDICES.items():
        hist = dashboard_data["indices"].get(label, pd.DataFrame())
        if hist.empty or "Close" not in hist.columns:
            continue

        last = float(hist["Close"].iloc[-1])
        change_html = "<span class='dashboard-index-change muted'>CHANGE N/A</span>"
        tone = "flat"
        if len(hist) > 1:
            previous = float(hist["Close"].iloc[-2])
            change = last - previous
            change_pct = (change / previous * 100) if previous else 0
            tone = "positive" if change_pct > 0 else "negative" if change_pct < 0 else "flat"
            change_html = (
                f"<span class='dashboard-index-change {tone}'>"
                f"{change:+,.2f} &nbsp; {change_pct:+.2f}%</span>"
            )

        snapshot_cards.append(
            f"""
            <div class='dashboard-index-card'>
                <div class='dashboard-index-label'>{escape(label)}</div>
                <div class='dashboard-index-symbol'>{escape(symbol)}</div>
                <div class='dashboard-index-value'>{last:,.2f}</div>
                {change_html}
            </div>
            """
        )

    with st.container(key="dashboard-snapshot"):
        st.markdown(
            """
            <div class='dashboard-section-heading'>
                <div>
                    <div class='dashboard-section-kicker'>PRIMARY MARKET SNAPSHOT</div>
                    <div class='dashboard-section-title'>Index monitor</div>
                </div>
                <div class='dashboard-section-meta'>YAHOO FINANCE / DELAYED</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if snapshot_cards:
            for start in range(0, len(snapshot_cards), 4):
                snapshot_columns = st.columns(4, gap="small")
                for column, card_html in zip(snapshot_columns, snapshot_cards[start:start + 4]):
                    with column:
                        st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.markdown("<div class='dashboard-empty'>No index data available.</div>", unsafe_allow_html=True)

    dashboard_sections = st.container(key="dashboard_sections")
    left, right = dashboard_sections.columns([1.25, 1], gap="medium")

    with left:
        with st.container(key="dashboard-watchlist-panel"):
            st.markdown(
                """
                <div class='dashboard-section-heading'>
                    <div>
                        <div class='dashboard-section-kicker'>WATCHLIST</div>
                        <div class='dashboard-section-title'>Tracked securities</div>
                    </div>
                    <div class='dashboard-section-meta'>LIVE SET</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            wl_rows = []
            for wt in st.session_state["watchlist"]:
                watch_data = dashboard_data["watchlist"].get(
                    wt,
                    {"history": pd.DataFrame(), "info": {}}
                )

                hist = watch_data["history"]
                info = watch_data["info"]
                name = safe_value(info, "shortName", display_ticker(wt))
                if not hist.empty and len(hist) > 0:
                    last = hist["Close"].iloc[-1]
                    previous = hist["Close"].iloc[-2] if len(hist) > 1 else last
                    change = last - previous
                    change_pct = (change / previous * 100) if previous else 0
                    wl_rows.append({
                        "Company": name,
                        "Ticker": display_ticker(wt),
                        "Price": f"INR {last:,.2f}",
                        "Chg": f"{change:+.2f}",
                        "Chg %": f"{change_pct:+.2f}%",
                    })
                else:
                    wl_rows.append({
                        "Company": name,
                        "Ticker": display_ticker(wt),
                        "Price": "N/A",
                        "Chg": "N/A",
                        "Chg %": "N/A",
                    })

            render_terminal_table(pd.DataFrame(wl_rows), empty_message="No watchlist data available.")

            st.markdown("<div class='dashboard-control-label'>WATCHLIST ACTIONS</div>", unsafe_allow_html=True)
            wcol1, wcol2 = st.columns([2, 1], gap="small")
            with wcol1:
                selected_watchlist_ticker = security_dropdown(
                    label="Add to watchlist",
                    key="dashboard_watchlist_security_dropdown",
                )

            with wcol2:
                if st.button(
                    "＋  ADD",
                    key="dashboard_watchlist_add_button",
                    width="stretch",
                    type="secondary",
                ):
                    resolved = selected_watchlist_ticker or ""
                    if resolved and resolved not in st.session_state["watchlist"]:
                        st.session_state["watchlist"].append(resolved)
                        st.rerun()

            if st.session_state["watchlist"]:
                remove_choice = st.selectbox(
                    "Remove from watchlist",
                    ["-"] + [display_ticker(t) for t in st.session_state["watchlist"]],
                    key="remove_watchlist_choice",
                )
                if remove_choice != "-" and st.button("Remove selected"):
                    st.session_state["watchlist"] = [
                        t for t in st.session_state["watchlist"] if display_ticker(t) != remove_choice
                    ]
                    st.rerun()

    with right:
        with st.container(key="dashboard-sector-panel"):
            st.markdown(
                """
                <div class='dashboard-section-heading'>
                    <div>
                        <div class='dashboard-section-kicker'>SECTOR PERFORMANCE</div>
                        <div class='dashboard-section-title'>Five-session movement</div>
                    </div>
                    <div class='dashboard-section-meta'>EQUAL WEIGHTED</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            sector_rows = []
            for sector_name, companies in SECTOR_GROUPS.items():
                sector_changes = []
                for company_name, ticker in companies.items():
                    hist = get_history(ticker, "5d", "1d")
                    if not hist.empty and len(hist) > 1:
                        last = float(hist["Close"].iloc[-1])
                        previous = float(hist["Close"].iloc[-2])
                        if previous:
                            change_pct = ((last / previous) - 1) * 100
                            sector_changes.append(change_pct)

                if sector_changes:
                    sector_performance = np.mean(sector_changes)
                    sector_rows.append({
                        "Sector": sector_name,
                        "Performance": f"{sector_performance:+.2f}%",
                    })

            render_terminal_table(
                pd.DataFrame(sector_rows),
                empty_message="No sector performance available.",
            )

    with st.container(key="dashboard-terminal-note"):
        st.markdown(
            "<span class='dashboard-note-label'>DATA NOTE</span> "
            "Free, delayed Yahoo Finance data. Coverage currently spans "
            f"{len(UNIVERSE_DF)} major NSE-listed securities within the existing universe.",
            unsafe_allow_html=True,
        )


# ============================================================

elif module == "Company Analysis":

    render_apex_page_header(
        "Company Analysis",
        "Security profile, valuation context, chart workstation and fundamentals",
        "LIVE DATA",
        datetime.now(IST).strftime("%a %d %b %Y • %H:%M IST")
    )

    # --------------------------------------------------------
    # SECURITY SELECTION
    # --------------------------------------------------------

    with st.container(key="company-analysis-selector"):
        st.markdown(
            """
            <div class='company-analysis-section-heading'>
                <div>
                    <div class='company-analysis-kicker'>SECURITY WORKSTATION</div>
                    <div class='company-analysis-section-title'>Select instrument</div>
                </div>
                <div class='company-analysis-section-meta'>NSE / YAHOO FINANCE</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        security_options = get_security_labels()

        if not security_options:
            st.error("No securities are available in the master universe.")
            st.stop()

        current_ticker = st.session_state.get(
            "ticker",
            UNIVERSE_DF.iloc[0]["ticker"]
        )

        current_label = get_security_label(current_ticker)

        if current_label not in security_options:
            current_label = security_options[0]

        selected_label = st.selectbox(
            "Select Security",
            security_options,
            index=security_options.index(current_label),
            key="company_analysis_security"
        )

        ticker = selected_label.rsplit(" • ", 1)[-1]

        load_clicked = st.button(
            "LOAD SECURITY",
            type="primary"
        )

    if load_clicked:
        remember_ticker(ticker)

    active_ticker = (
        ticker
        if load_clicked
        else st.session_state.get("ticker", ticker)
    )

    if load_clicked or st.session_state.get("ticker"):
        active_ticker = ticker if load_clicked else st.session_state["ticker"]

        with st.spinner(f"Loading {active_ticker}..."):
            info = get_company_info(active_ticker)
            snapshot_hist = get_history(active_ticker, "1y", "1d")

        if snapshot_hist.empty:
            st.error(f"No market data was found for {active_ticker}. Check the ticker and try again.")
        else:
            active_security = UNIVERSE_BY_TICKER.get(active_ticker, {})
            active_asset_class = normalize_asset_class(active_security.get("asset_class"))
            active_currency = str(active_security.get("currency", "") or "").strip().upper()
            if not active_currency:
                active_currency = str(safe_value(info, "currency", "") or "").strip().upper()
            fundamentals_applicable = supports_metric(
                active_asset_class,
                "P/E",
                "fundamental_metrics",
            )

            def fundamental_display(value, formatter):
                if not fundamentals_applicable:
                    return "NOT APPLICABLE"
                if value is None:
                    return "DATA NOT AVAILABLE"
                try:
                    if not np.isfinite(float(value)):
                        return "DATA NOT AVAILABLE"
                except (TypeError, ValueError):
                    return "DATA NOT AVAILABLE"
                formatted = formatter(value)
                return "DATA NOT AVAILABLE" if str(formatted).strip().upper() in {"N/A", "NONE", "NAN", "INF"} else formatted

            company_name = safe_value(info, "longName", active_ticker)
            sector = safe_value(info, "sector", "N/A")
            industry = safe_value(info, "industry", "N/A")
            exchange = safe_value(info, "exchange", "N/A")
            country = safe_value(info, "country", "N/A")
            website = safe_value(info, "website", None)

            latest_close = snapshot_hist["Close"].iloc[-1]
            previous_close = safe_value(info, "previousClose") or (
                snapshot_hist["Close"].iloc[-2] if len(snapshot_hist) > 1 else latest_close
            )
            current_price = safe_value(info, "currentPrice", latest_close)
            daily_change = current_price - previous_close
            daily_change_pct = (daily_change / previous_close) if previous_close else 0

            # ------------------------------------------------
            # STITCH-STYLE COMPANY HEADER
            # ------------------------------------------------
            with st.container(key="company-analysis-security-header"):
                st.markdown(
                    "<div class='company-analysis-kicker'>SECURITY HEADER</div>",
                    unsafe_allow_html=True,
                )
                title_col, price_col, action_col = st.columns([2.1, 1.35, 1])
                with title_col:
                    st.markdown(f"<div class='company-analysis-company-name'>{escape(company_name)}</div>", unsafe_allow_html=True)
                    st.caption(
                        f"{display_ticker(active_ticker)}  •  {exchange}  •  {sector}  •  {country}"
                    )
                    if website:
                        st.caption(website)
                with price_col:
                    st.caption(f"{exchange} DELAYED · {active_currency or 'DATA NOT AVAILABLE'}")
                    st.metric(
                        "Last Price",
                        format_master_currency(current_price, active_ticker),
                        f"{format_master_currency(daily_change, active_ticker)} ({daily_change_pct * 100:+.2f}%)",
                    )
                with action_col:
                    st.caption("WATCHLIST")
                    if st.button(
                        "REMOVE FROM WATCHLIST" if active_ticker in st.session_state["watchlist"] else "ADD TO WATCHLIST",
                        key="company_watchlist_action",
                        width="stretch",
                    ):
                        if active_ticker in st.session_state["watchlist"]:
                            st.session_state["watchlist"].remove(active_ticker)
                        else:
                            st.session_state["watchlist"].append(active_ticker)
                        st.rerun()

                header_metrics = st.columns(6, gap="small")
                day_low = safe_value(info, "dayLow")
                day_high = safe_value(info, "dayHigh")
                week_low = safe_value(info, "fiftyTwoWeekLow")
                week_high = safe_value(info, "fiftyTwoWeekHigh")
                header_values = [
                    ("PREVIOUS CLOSE", format_master_currency(previous_close, active_ticker)),
                    ("DAY RANGE", f"{format_master_currency(day_low, active_ticker)} - {format_master_currency(day_high, active_ticker)}" if day_low is not None and day_high is not None else "DATA NOT AVAILABLE"),
                    ("52W LOW - HIGH", f"{format_master_currency(week_low, active_ticker)} - {format_master_currency(week_high, active_ticker)}" if week_low is not None and week_high is not None else "DATA NOT AVAILABLE"),
                    ("MKT CAP", fundamental_display(safe_value(info, "marketCap"), lambda value: format_master_currency_scale(value, active_ticker))),
                    ("P/E", fundamental_display(safe_value(info, "trailingPE"), format_ratio)),
                    ("BETA", fundamental_display(safe_value(info, "beta"), format_ratio)),
                ]
                for metric_col, (label, value) in zip(header_metrics, header_values):
                    with metric_col:
                        st.caption(label)
                        st.markdown(f"**{value}**")

            st.caption("Prices below reflect the latest data available from Yahoo Finance - "
                       "delayed, not live tick-by-tick exchange data.")

            if fundamentals_applicable:
                income_df = get_income_statement(active_ticker)
                balance_df = get_balance_sheet(active_ticker)
                cashflow_df = get_cashflow(active_ticker)
            else:
                income_df = pd.DataFrame()
                balance_df = pd.DataFrame()
                cashflow_df = pd.DataFrame()
            ratios = compute_fundamental_ratios(
                info,
                income_df,
                balance_df,
                cashflow_df,
                asset_class=active_asset_class,
            )

            st.divider()

            tabs = st.tabs([
                "Overview", "Price Performance", "Price Chart", "Fundamentals",
                "Ratio Analysis", "Investment Summary"
            ])

            # ---------------- OVERVIEW ----------------
            with tabs[0]:
                st.markdown("#### Company Snapshot / Quality & Solvency")
                ov1, ov2 = st.columns([1, 1])
                with ov1:
                    st.caption("BUSINESS PROFILE")
                    snapshot_rows = {
                        "Asset Class": active_asset_class,
                        "Instrument Type": active_security.get("instrument_type") or "DATA NOT AVAILABLE",
                        "Currency": active_currency or "DATA NOT AVAILABLE",
                        "Sector": sector,
                        "Industry": industry,
                        "Exchange": exchange,
                        "Country": country,
                        "Employees": f"{safe_value(info, 'fullTimeEmployees'):,.0f}" if safe_value(info, "fullTimeEmployees") else "N/A",
                    }
                    render_terminal_table(pd.DataFrame([snapshot_rows]))
                    if not fundamentals_applicable:
                        direct_metrics = direct_provider_metrics(active_asset_class, info)
                        st.caption("DIRECT INSTRUMENT DATA")
                        st.caption("Fields below are provider-reported values; units are not estimated or converted.")
                        direct_rows = [
                            {"Metric": label, "Value": value}
                            for label, value in direct_metrics.items()
                        ] or [{"Metric": "Instrument metrics", "Value": "NOT APPLICABLE"}]
                        render_terminal_table(pd.DataFrame(direct_rows))
                with ov2:
                    st.caption("QUALITY / SOLVENCY")
                    health = ratios["health"]
                    profitability = ratios["profitability"]
                    quality_cols = st.columns(3)
                    quality_values = [
                        ("DEBT / EQUITY", fundamental_display(health["Debt/Equity"], format_ratio)),
                        ("NET DEBT", fundamental_display(health["Net Debt"], lambda value: format_master_currency_scale(value, active_ticker))),
                        ("CURRENT RATIO", fundamental_display(health["Current Ratio"], format_ratio)),
                        ("INTEREST COVER", fundamental_display(health["Interest Coverage"], format_ratio)),
                        ("ROE", fundamental_display(profitability["ROE"], format_percent)),
                        ("ROA", fundamental_display(profitability["ROA"], format_percent)),
                    ]
                    for index, (label, value) in enumerate(quality_values):
                        quality_col = quality_cols[index % 3]
                        with quality_col:
                            st.caption(label)
                            st.markdown(f"**{value}**")

                description = safe_value(info, "longBusinessSummary")
                st.caption("BUSINESS DESCRIPTION")
                if description:
                    st.write(description)
                else:
                    st.caption("No business description available for this security.")

            # ---------------- PRICE PERFORMANCE ----------------
            with tabs[1]:
                st.markdown("#### Price Performance")
                perf_hist = get_history(active_ticker, "5y", "1d")
                returns = compute_returns_table(perf_hist)
                perf_cols = st.columns(4)
                for i, (label, val) in enumerate(returns.items()):
                    with perf_cols[i % 4]:
                        st.metric(label, format_percent(val, already_pct=True) if val is not None else "N/A")

                st.markdown("#### 52-Week Range")
                wk_high = safe_value(info, "fiftyTwoWeekHigh")
                wk_low = safe_value(info, "fiftyTwoWeekLow")
                if wk_high and wk_low:
                    drawdown_from_high = (current_price / wk_high - 1) * 100
                    range_pct = (current_price - wk_low) / (wk_high - wk_low) * 100 if wk_high != wk_low else None
                    rc1, rc2, rc3 = st.columns(3)
                    with rc1:
                        st.metric("52W High", format_master_currency(wk_high, active_ticker))
                    with rc2:
                        st.metric("52W Low", format_master_currency(wk_low, active_ticker))
                    with rc3:
                        st.metric("Drawdown from 52W High", f"{drawdown_from_high:.2f}%")
                    if range_pct is not None:
                        st.progress(min(max(range_pct / 100, 0.0), 1.0),
                                    text=f"Currently {range_pct:.1f}% up the 52-week range")
                else:
                    st.caption("52-week range unavailable for this security.")

            # ---------------- PRICE CHART ----------------
            with tabs[2]:
                st.markdown("#### Price / Chart Workstation")
                st.caption("TIMEFRAME  ·  OHLCV  ·  INDICATORS")
                primary_timeframes = ["1D", "1W", "1M", "1Y", "5Y"]
                tf_cols = st.columns(len(primary_timeframes))
                for i, tf in enumerate(primary_timeframes):
                    with tf_cols[i]:
                        if st.button(tf, key=f"tf_{tf}",
                                     type="primary" if st.session_state["chart_timeframe"] == tf else "secondary",
                                     width="stretch"):
                            st.session_state["chart_timeframe"] = tf
                            st.rerun()

                extended_timeframes = [tf for tf in TIMEFRAMES if tf not in primary_timeframes]
                extended_tf = st.selectbox(
                    "Extended timeframe",
                    ["Use primary timeframe"] + extended_timeframes,
                    key="company_extended_timeframe",
                    label_visibility="collapsed",
                )
                if extended_tf != "Use primary timeframe":
                    st.session_state["chart_timeframe"] = extended_tf

                chosen_tf = st.session_state["chart_timeframe"]

                if chosen_tf in {"5M", "15M", "30M", "1H"}:
                    minutes = {
                        "5M": 5,
                        "15M": 15,
                        "30M": 30,
                        "1H": 60,
                    }[chosen_tf]

                    chart_hist = get_intraday_history(
                        active_ticker,
                        period="1d",
                        interval="1m"
                    )

                    if not chart_hist.empty:
                        chart_hist = chart_hist.tail(minutes)
                else:
                    period, interval = TIMEFRAMES[chosen_tf]
                    chart_hist = get_history(
                        active_ticker,
                        period,
                        interval
                    )

                overlay_choices = st.multiselect(
                    "Overlays / EMA / VWAP",
                    ["SMA 20", "SMA 50", "SMA 100", "SMA 200", "EMA 20", "EMA 50", "Bollinger Bands", "VWAP"],
                    default=["SMA 50"],
                    key="company_chart_overlays",
                )
                ind_col1, ind_col2 = st.columns(2)
                with ind_col1:
                    show_rsi_toggle = st.checkbox("Show RSI", value=False, key="company_show_rsi")
                with ind_col2:
                    show_macd_toggle = st.checkbox("Show MACD", value=False, key="company_show_macd")

                if chart_hist.empty:
                    st.warning(f"No historical data is available for {chosen_tf}.")
                else:
                    st.plotly_chart(
                        create_price_chart(chart_hist, display_ticker(active_ticker),
                                            overlays=overlay_choices, show_volume=True,
                                            show_rsi=show_rsi_toggle, show_macd=show_macd_toggle),
                        width="stretch",
                    )
                    csv_data = chart_hist.to_csv().encode("utf-8")
                    st.download_button("Download chart data (CSV)", csv_data,
                                        file_name=f"{display_ticker(active_ticker)}_{chosen_tf}.csv")

            # ---------------- FUNDAMENTALS ----------------
            with tabs[3]:
                if not fundamentals_applicable:
                    st.info(
                        f"NOT APPLICABLE: corporate valuation, profitability, growth, "
                        f"and leverage metrics are not defined for {active_asset_class}. "
                        "Direct instrument-level fields are shown only when the provider reports them."
                    )
                else:
                    st.markdown("#### Financial Data / Key Fundamentals")

                    st.markdown("**Valuation**")
                    v = ratios["valuation"]
                    vcols = st.columns(4)
                    vcols[0].metric("Market Cap", fundamental_display(v["Market Cap"], lambda value: format_master_currency_scale(value, active_ticker)))
                    vcols[1].metric("Enterprise Value", fundamental_display(v["Enterprise Value"], lambda value: format_master_currency_scale(value, active_ticker)))
                    vcols[2].metric("P/E (TTM)", fundamental_display(v["P/E (TTM)"], format_ratio))
                    vcols[3].metric("Forward P/E", fundamental_display(v["Forward P/E"], format_ratio))
                    vcols = st.columns(4)
                    vcols[0].metric("P/B", fundamental_display(v["P/B"], format_ratio))
                    vcols[1].metric("P/S", fundamental_display(v["P/S"], format_ratio))
                    vcols[2].metric("EV/EBITDA", fundamental_display(v["EV/EBITDA"], format_ratio))
                    vcols[3].metric("PEG Ratio", fundamental_display(v["PEG Ratio"], format_ratio))

                    st.markdown("**Profitability**")
                    p = ratios["profitability"]
                    pcols = st.columns(4)
                    pcols[0].metric("Gross Margin", fundamental_display(p["Gross Margin"], format_percent))
                    pcols[1].metric("Operating Margin", fundamental_display(p["Operating Margin"], format_percent))
                    pcols[2].metric("Net Margin", fundamental_display(p["Net Margin"], format_percent))
                    pcols[3].metric("ROE", fundamental_display(p["ROE"], format_percent))
                    pcols = st.columns(2)
                    pcols[0].metric("ROA", fundamental_display(p["ROA"], format_percent))
                    pcols[1].metric("ROIC", fundamental_display(p["ROIC"], format_percent))

                    st.markdown("**Growth**")
                    g = ratios["growth"]
                    gcols = st.columns(4)
                    gcols[0].metric("Revenue Growth", fundamental_display(g["Revenue Growth (YoY)"], format_percent))
                    gcols[1].metric("Earnings Growth", fundamental_display(g["Earnings Growth (YoY)"], format_percent))
                    gcols[2].metric("EPS (TTM)", fundamental_display(g["EPS (TTM)"], lambda value: format_master_currency(value, active_ticker)))
                    gcols[3].metric("EPS (Forward)", fundamental_display(g["EPS (Forward)"], lambda value: format_master_currency(value, active_ticker)))

                    st.markdown("**Financial Health**")
                    h = ratios["health"]
                    hcols = st.columns(4)
                    hcols[0].metric("Total Debt", fundamental_display(h["Total Debt"], lambda value: format_master_currency_scale(value, active_ticker)))
                    hcols[1].metric("Cash", fundamental_display(h["Cash"], lambda value: format_master_currency_scale(value, active_ticker)))
                    hcols[2].metric("Net Debt", fundamental_display(h["Net Debt"], lambda value: format_master_currency_scale(value, active_ticker)))
                    hcols[3].metric("Debt/Equity", fundamental_display(h["Debt/Equity"], format_ratio))
                    hcols = st.columns(2)
                    hcols[0].metric("Current Ratio", fundamental_display(h["Current Ratio"], format_ratio))
                    hcols[1].metric("Interest Coverage", fundamental_display(h["Interest Coverage"], format_ratio))

                    st.markdown("#### Reported Statements")
                    statement_tabs = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
                    statement_frames = [income_df, balance_df, cashflow_df]
                    for statement_tab, statement_df in zip(statement_tabs, statement_frames):
                        with statement_tab:
                            if statement_df is None or statement_df.empty:
                                st.caption("DATA NOT AVAILABLE: no reported statement data was returned by the provider.")
                            else:
                                display_df = statement_df.head(12).copy().T
                                display_df.index = display_df.index.astype(str)
                                render_terminal_table(display_df)

            # ---------------- RATIO ANALYSIS ----------------
            with tabs[4]:
                if not fundamentals_applicable:
                    st.info(f"NOT APPLICABLE: corporate ratio analysis is not defined for {active_asset_class}.")
                else:
                    st.markdown("#### Ratio Analysis")
                    st.caption("DATA NOT AVAILABLE indicates that the provider did not report the underlying figure.")
                    for category, label in [("valuation", "Valuation"), ("profitability", "Profitability"),
                                             ("growth", "Growth"), ("health", "Liquidity & Solvency"),
                                             ("efficiency", "Efficiency"), ("per_share", "Per Share")]:
                        with st.expander(label, expanded=(category == "profitability")):
                            rows = []
                            for metric_name, value in ratios[category].items():
                                if any(token in metric_name for token in ("Margin", "ROE", "ROA", "ROIC", "Growth")):
                                    formatter = format_percent
                                elif any(token in metric_name for token in ("Cap", "Value", "Debt", "Cash")):
                                    formatter = lambda number: format_master_currency_scale(number, active_ticker)
                                elif "EPS" in metric_name or "Share" in metric_name:
                                    formatter = lambda number: format_master_currency(number, active_ticker)
                                else:
                                    formatter = format_ratio
                                display_val = fundamental_display(value, formatter)
                                rows.append({"Metric": metric_name, "Value": display_val})
                            render_terminal_table(pd.DataFrame(rows))

            # ---------------- INVESTMENT SUMMARY ----------------
            with tabs[5]:
                st.markdown("#### Investment Summary")
                if not fundamentals_applicable:
                    st.info(
                        f"NOT APPLICABLE: the corporate valuation and profitability assessment is not defined for {active_asset_class}. "
                        "Use the price-based return and risk analyses for this instrument."
                    )
                assessment = []
                pe_val = ratios["valuation"]["P/E (TTM)"]
                roe_val = ratios["profitability"]["ROE"]
                de_val = ratios["health"]["Debt/Equity"]
                rev_growth = ratios["growth"]["Revenue Growth (YoY)"]

                if pe_val is not None:
                    if pe_val < 15:
                        assessment.append("P/E is relatively low compared with many growth-oriented companies.")
                    elif pe_val > 30:
                        assessment.append("P/E is relatively high, indicating the market may be pricing in strong future growth.")
                    else:
                        assessment.append("P/E is in a moderate range relative to the broader market.")
                if roe_val is not None:
                    if roe_val > 0.15:
                        assessment.append("ROE is above 15%, indicating relatively strong profitability on shareholder equity.")
                    else:
                        assessment.append("ROE is below 15%; profitability relative to equity should be examined further.")
                if de_val is not None:
                    if de_val > 1.5:
                        assessment.append("Debt/Equity is elevated - leverage and interest-coverage should be reviewed.")
                    else:
                        assessment.append("Debt/Equity is at a manageable level.")
                if rev_growth is not None:
                    if rev_growth > 0:
                        assessment.append(f"Revenue grew {rev_growth * 100:.1f}% year-over-year.")
                    else:
                        assessment.append(f"Revenue declined {abs(rev_growth) * 100:.1f}% year-over-year.")
                if daily_change_pct > 0:
                    assessment.append("The security closed higher in the latest available session.")
                elif daily_change_pct < 0:
                    assessment.append("The security closed lower in the latest available session.")

                for point in assessment:
                    st.write("• " + point)
                if not assessment:
                    st.caption("Insufficient data to generate a summary for this security.")
                st.caption("This is quantitative screening based on retrieved data - not investment advice.")


# ============================================================
# STOCK SCREENER
# ============================================================

elif module == "Watchlist":

    render_apex_page_header(
        "Watchlist",
        "Live security tracker across the terminal universe",
        "WATCHLIST",
        datetime.now(IST).strftime("%a %d %b %Y • %H:%M IST")
    )

    watchlist_data = get_dashboard_market_data(tuple(st.session_state["watchlist"]))
    st.markdown(
        "<div class='module-section-kicker'>TRACKED SECURITIES</div>",
        unsafe_allow_html=True,
    )
    watch_rows = []
    for watch_ticker in st.session_state["watchlist"]:
        watch_item = watchlist_data["watchlist"].get(watch_ticker, {})
        watch_hist = watch_item.get("history", pd.DataFrame())
        watch_info = watch_item.get("info", {})
        row = {
            "Company": safe_value(watch_info, "shortName", display_ticker(watch_ticker)),
            "Ticker": display_ticker(watch_ticker),
            "Market": safe_value(watch_info, "exchange", "N/A"),
            "Country": safe_value(watch_info, "country", "N/A"),
            "Price": "N/A",
            "Chg %": "N/A",
        }
        if not watch_hist.empty and "Close" in watch_hist.columns:
            current = float(watch_hist["Close"].iloc[-1])
            previous = float(watch_hist["Close"].iloc[-2]) if len(watch_hist) > 1 else current
            change_pct = ((current - previous) / previous * 100) if previous else 0
            row["Price"] = f"INR {current:,.2f}"
            row["Chg %"] = f"{change_pct:+.2f}%"
        watch_rows.append(row)

    render_terminal_table(pd.DataFrame(watch_rows), empty_message="No securities in the watchlist.")
    w_add, w_remove = st.columns([2, 1], gap="small")
    with w_add:
        watch_add = security_dropdown("Add security", key="watchlist_module_add")
        if st.button("+ ADD", key="watchlist_module_add_button", width="stretch"):
            if watch_add and watch_add not in st.session_state["watchlist"]:
                st.session_state["watchlist"].append(watch_add)
                st.rerun()
    with w_remove:
        watch_remove = st.selectbox(
            "Remove security",
            ["-"] + [display_ticker(item) for item in st.session_state["watchlist"]],
            key="watchlist_module_remove",
        )
        if watch_remove != "-" and st.button("REMOVE", key="watchlist_module_remove_button", width="stretch"):
            st.session_state["watchlist"] = [
                item for item in st.session_state["watchlist"]
                if display_ticker(item) != watch_remove
            ]
            st.rerun()


# ============================================================

elif module == "Market News":

    render_apex_page_header(
        "Market News",
        "Current market and company headlines from the existing RSS feed",
        "RSS FEED",
        datetime.now(IST).strftime("%a %d %b %Y • %H:%M IST")
    )
    news_query_options = {
        "Indian Markets": "NSE OR Nifty OR Sensex stock market India",
        "Corporate News": "Indian companies earnings stocks corporate",
        "Banking & Finance": "Indian banks financial stocks RBI",
        "Global Markets": "global stock markets India investors",
    }
    news_topic = st.selectbox("News topic", list(news_query_options), key="market_news_topic")
    if st.button("REFRESH NEWS", key="market_news_refresh"):
        get_news_feed.clear()
        st.rerun()
    news_items = get_news_feed(news_query_options[news_topic], limit=8)
    if news_items:
        for article in news_items:
            st.markdown(
                f"<div class='market-news-item'><a href='{escape(article['link'])}' target='_blank'>"
                f"{escape(article['title'])}</a><span>{escape(article['published'])}</span></div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown("<div class='apex-empty-state'>No recent news available.</div>", unsafe_allow_html=True)


# ============================================================

elif module == "Stock Screener":

    render_apex_page_header(
        "Stock Screener",
        "Multi-factor screening across the terminal's master security universe",
        "UNIVERSE: " + str(len(UNIVERSE_DF)),
        "Yahoo Finance + Master Universe"
    )


    st.caption(
        f"Screens the terminal's master coverage universe of "
        f"{len(UNIVERSE_DF)} securities using Yahoo Finance data. "
        "Results are limited to securities available in the project's "
        "validated master universe."
    )

    with st.form("screener_form"):

        st.markdown("#### Screening Criteria")
        st.caption("Choose > or < for each metric. Market Cap uses Crores for INR securities and Millions for all other currencies. Set the value to 0 to ignore that filter.")

        f1, f2, f3 = st.columns(3)

        with f1:
            st.markdown("**Market Cap (INR  Cr)**")
            op_col, val_col = st.columns([1, 2])

            with op_col:
                mcap_operator = st.selectbox(
                    "Operator",
                    [">", "<"],
                    key="mcap_operator",
                    label_visibility="collapsed"
                )

            with val_col:
                mcap_value = st.number_input(
                    "Value",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    key="mcap_value",
                    label_visibility="collapsed"
                )

        with f2:
            st.markdown("**ROE (%)**")
            op_col, val_col = st.columns([1, 2])

            with op_col:
                roe_operator = st.selectbox(
                    "Operator",
                    [">", "<"],
                    key="roe_operator",
                    label_visibility="collapsed"
                )

            with val_col:
                roe_value = st.number_input(
                    "Value",
                    value=0.0,
                    step=1.0,
                    key="roe_value",
                    label_visibility="collapsed"
                )

        with f3:
            st.markdown("**Revenue Growth (%)**")
            op_col, val_col = st.columns([1, 2])

            with op_col:
                rev_operator = st.selectbox(
                    "Operator",
                    [">", "<"],
                    key="rev_operator",
                    label_visibility="collapsed"
                )

            with val_col:
                rev_value = st.number_input(
                    "Value",
                    value=0.0,
                    step=1.0,
                    key="rev_value",
                    label_visibility="collapsed"
                )

        f4, f5, f6 = st.columns(3)

        with f4:
            st.markdown("**P/E**")
            op_col, val_col = st.columns([1, 2])

            with op_col:
                pe_operator = st.selectbox(
                    "Operator",
                    [">", "<"],
                    index=1,
                    key="pe_operator",
                    label_visibility="collapsed"
                )

            with val_col:
                pe_value = st.number_input(
                    "Value",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key="pe_value",
                    label_visibility="collapsed"
                )

        with f5:
            st.markdown("**Debt / Equity**")
            op_col, val_col = st.columns([1, 2])

            with op_col:
                de_operator = st.selectbox(
                    "Operator",
                    [">", "<"],
                    index=1,
                    key="de_operator",
                    label_visibility="collapsed"
                )

            with val_col:
                de_value = st.number_input(
                    "Value",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    key="de_value",
                    label_visibility="collapsed"
                )

        with f6:
            st.markdown("**Dividend Yield (%)**")
            op_col, val_col = st.columns([1, 2])

            with op_col:
                div_operator = st.selectbox(
                    "Operator",
                    [">", "<"],
                    key="div_operator",
                    label_visibility="collapsed"
                )

            with val_col:
                div_value = st.number_input(
                    "Value",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    key="div_value",
                    label_visibility="collapsed"
                )

        st.markdown("#### Additional Filter")

        sector_filter = st.selectbox(
            "Sector",
            ["All"] + list(SECTOR_GROUPS.keys())
        )

        run_screen = st.form_submit_button(
            "Run Screener",
            type="primary",
            width="stretch"
        )

    if st.button("CLEAR FILTERS", key="screener_clear_filters"):
        for filter_key in (
            "mcap_operator", "mcap_value", "roe_operator", "roe_value",
            "rev_operator", "rev_value", "pe_operator", "pe_value",
            "de_operator", "de_value", "div_operator", "div_value",
        ):
            st.session_state.pop(filter_key, None)
        st.rerun()

    if run_screen:
        universe = [
            (
                str(row["ticker"]).strip(),
                str(row["name"]).strip()
            )
            for _, row in UNIVERSE_DF.iterrows()
            if str(row["ticker"]).strip()
        ]

        if sector_filter != "All":
            universe = [
                (t, n)
                for t, n in universe
                if TICKER_TO_SECTOR_GROUP.get(t) == sector_filter
            ]

        rows = []

        progress = st.progress(0.0, text="Fetching screener universe...")

        @st.cache_data(ttl=180, show_spinner=False)
        def fetch_screener_company(ticker):
            """
            Dedicated Stock Screener data fetch.

            Uses one Yahoo Ticker object per security. Lightweight
            fast_info supplies price and market cap, while .info
            supplies the fundamental fields required by the screener.
            """
            try:
                ticker = str(ticker).strip()

                yahoo_ticker = yf.Ticker(ticker)

                fast_info = yahoo_ticker.fast_info

                market_cap = getattr(
                    fast_info,
                    "market_cap",
                    None,
                )

                current_price = getattr(
                    fast_info,
                    "last_price",
                    None,
                )

                try:
                    info = yahoo_ticker.info
                except Exception:
                    info = {}

                if not isinstance(info, dict):
                    info = {}

                if info.get("marketCap") is None and market_cap is not None:
                    info["marketCap"] = market_cap

                if info.get("currentPrice") is None and current_price is not None:
                    info["currentPrice"] = current_price

                return info

            except Exception:
                return {}

        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_map = {
                executor.submit(fetch_screener_company, t): (t, n)
                for t, n in universe
            }

            completed = 0

            for future in as_completed(future_map):
                completed += 1

                t, n = future_map[future]

                try:
                    info = future.result()
                except Exception:
                    progress.progress(
                        completed / max(len(universe), 1),
                        text=f"Fetching screener data... {completed}/{len(universe)}"
                    )
                    continue

                progress.progress(
                    completed / max(len(universe), 1),
                    text=f"Fetching screener data... {completed}/{len(universe)}"
                )

                if not info:
                    continue

                # Yahoo returns marketCap in the security's
                # own listing currency. Keep that value unchanged.
                # Only the screener display/filter unit is normalized:
                # INR -> Crores, all other currencies -> Millions.
                mcap = safe_value(info, "marketCap")
                listing_currency = get_listing_currency(t)

                if listing_currency == "INR":
                    mcap_display_value = (
                        mcap / 1_00_00_000
                        if mcap is not None
                        else None
                    )
                    mcap_display_unit = "Cr"
                else:
                    mcap_display_value = (
                        mcap / 1_000_000
                        if mcap is not None
                        else None
                    )
                    mcap_display_unit = "M"

                pe = safe_value(info, "trailingPE")
                roe = safe_value(info, "returnOnEquity")
                de = safe_value(info, "debtToEquity")

                if de and de > 10:
                    de = de / 100

                rev_g = safe_value(info, "revenueGrowth")
                div_y = safe_value(info, "dividendYield")
                price = safe_value(info, "currentPrice")

                passes = True

                # Market Cap
                # Filter in the security's own display currency:
                # INR securities -> Crores
                # Foreign securities -> Millions
                if mcap_value > 0:
                    if mcap_display_value is None:
                        passes = False
                    else:
                        if (
                            mcap_operator == ">"
                            and mcap_display_value <= mcap_value
                        ):
                            passes = False

                        elif (
                            mcap_operator == "<"
                            and mcap_display_value >= mcap_value
                        ):
                            passes = False

                # P/E
                if pe_value > 0:
                    if pe is None:
                        passes = False
                    else:
                        if pe_operator == ">" and pe <= pe_value:
                            passes = False
                        elif pe_operator == "<" and pe >= pe_value:
                            passes = False

                # ROE
                if roe_value != 0:
                    if roe is None:
                        passes = False
                    else:
                        roe_pct = roe * 100

                        if roe_operator == ">" and roe_pct <= roe_value:
                            passes = False
                        elif roe_operator == "<" and roe_pct >= roe_value:
                            passes = False

                # Debt / Equity
                if de_value > 0:
                    if de is None:
                        passes = False
                    else:
                        if de_operator == ">" and de <= de_value:
                            passes = False
                        elif de_operator == "<" and de >= de_value:
                            passes = False

                # Revenue Growth
                if rev_value != 0:
                    if rev_g is None:
                        passes = False
                    else:
                        rev_pct = rev_g * 100

                        if rev_operator == ">" and rev_pct <= rev_value:
                            passes = False
                        elif rev_operator == "<" and rev_pct >= rev_value:
                            passes = False

                # Dividend Yield
                if div_value != 0:
                    if div_y is None:
                        passes = False
                    else:
                        div_pct = div_y * 100

                        if div_operator == ">" and div_pct <= div_value:
                            passes = False
                        elif div_operator == "<" and div_pct >= div_value:
                            passes = False

                if passes:
                    rows.append({
                        "Company": n,
                        "Ticker": display_ticker(t),
                        "Price": price,
                        "Market Cap": (
                            f"INR {mcap_display_value:,.2f} Cr"
                            if listing_currency == "INR"
                            and mcap_display_value is not None
                            else (
                                f"{currency_symbol(listing_currency)}"
                                f"{mcap_display_value:,.2f}M"
                                if mcap_display_value is not None
                                else "N/A"
                            )
                        ),
                        "P/E": format_ratio(pe),
                        "ROE": format_percent(roe) if roe else "N/A",
                        "D/E": format_ratio(de),
                        "Rev Growth": format_percent(rev_g) if rev_g else "N/A",
                        "Div Yield": format_percent(div_y) if div_y else "N/A",
                    })

        progress.empty()

        st.success(
            f"{len(rows)} companies matched out of {len(universe)} screened."
        )

        if rows:
            result_df = pd.DataFrame(rows)

            render_terminal_table(result_df, empty_message="No companies matched the criteria.")

            st.download_button(
                "Download results (CSV)",
                result_df.to_csv(index=False).encode("utf-8"),
                file_name="screener_results.csv"
            )

        else:
            st.info(
                "No companies in the local universe matched every filter. "
                "Try loosening a constraint."
            )


# ============================================================
# FINANCIAL STATEMENTS
# ============================================================

elif module == "Financial Statements":

    render_apex_page_header(
        "Financial Statements",
        "Income statement, balance sheet and cash-flow reporting by security",
        "STATEMENTS",
        "Yahoo Finance"
    )

    ticker = security_dropdown(
        "Select Security",
        key="security_selector_1"
    )

    statement = st.selectbox(
        "Select Statement",
        ["Income Statement", "Balance Sheet", "Cash Flow Statement"]
    )

    if st.button("Load Statement", type="primary"):
        remember_ticker(ticker)
        with st.spinner("Loading financial statements..."):
            if statement == "Income Statement":
                data = get_income_statement(ticker)
            elif statement == "Balance Sheet":
                data = get_balance_sheet(ticker)
            else:
                data = get_cashflow(ticker)

        if data.empty:
            st.warning("Financial statement data is not available for this security.")
        else:
            st.success(f"{statement} loaded for {display_ticker(ticker)}")

            display_data = data.copy()

            # Professional row-label name for financial statements.
            display_data.index.name = "Particulars"

            # Preserve complete financial statement period labels.
            display_data.columns = [str(c) for c in display_data.columns]
            for column in display_data.columns:
                try:
                    display_data[column] = display_data[column].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                except Exception:
                    pass
            # Convert the financial-statement index into a real
            # visible column so every row label is displayed.
            display_data = display_data.reset_index()

            # Make absolutely sure the first column is named Particulars.
            if len(display_data.columns) > 0:
                display_data = display_data.rename(
                    columns={
                        display_data.columns[0]: "Particulars"
                    }
                )

            # Render the visible row labels together with all periods.
            with st.container():
                st.markdown(
                    '<div class="terminal-financial-statements">',
                    unsafe_allow_html=True
                )
                render_terminal_table(display_data)
                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            st.download_button("Download statement (CSV)", data.to_csv().encode("utf-8"),
                                file_name=f"{display_ticker(ticker)}_{statement.replace(' ', '_')}.csv")

            st.divider()
            st.markdown("#### Trends")

            income_df = get_income_statement(ticker)
            balance_df = get_balance_sheet(ticker)
            cashflow_df = get_cashflow(ticker)

            trend_specs = [
                ("Revenue", get_statement_series(income_df, ["Total Revenue", "TotalRevenue"])),
                ("Net Income", get_statement_series(income_df, ["Net Income", "NetIncome"])),
                ("EBITDA", get_statement_series(income_df, ["EBITDA"])),
                ("EPS (Diluted)", get_statement_series(income_df, ["Diluted EPS"])),
                ("Operating Cash Flow", get_statement_series(cashflow_df, ["Operating Cash Flow",
                                                                             "Cash Flow From Continuing Operating Activities"])),
                ("Free Cash Flow", get_statement_series(cashflow_df, ["Free Cash Flow"])),
                ("Total Debt", get_statement_series(balance_df, ["Total Debt"])),
            ]

            trend_cols = st.columns(2)
            i = 0
            for label, series in trend_specs:
                if series is not None and len(series) > 1:
                    with trend_cols[i % 2]:
                        st.plotly_chart(create_trend_chart(series, f"{label} Trend"), width="stretch")
                    i += 1
            if i == 0:
                st.caption("Not enough historical periods reported to build trend charts for this security.")


# ============================================================
# VALUATION
# ============================================================

elif module == "Valuation":

    render_apex_page_header(
        "Valuation",
        "Relative multiples, DCF assumptions and fair value context",
        "VALUATION",
        "Yahoo Finance"
    )

    ticker = security_dropdown(
        "Select Security",
        key="security_selector_2"
    )

    if not ticker:
        st.info("Enter a company name or ticker to begin.")
    else:

        remember_ticker(ticker)

        info = get_company_info(ticker)

        if not info:
            st.error("Could not retrieve company information.")
        else:

            company_name = safe_value(
                info,
                "longName",
                safe_value(info, "shortName", ticker)
            )

            local_currency = get_listing_currency(ticker)

            st.markdown(f"### {company_name}")
            st.caption(
                f"Ticker: {ticker}  •  Listing currency: {local_currency}"
            )

            val_tabs = st.tabs([
                "Relative Valuation",
                "DCF"
            ])

            # ====================================================
            # RELATIVE VALUATION
            # ====================================================

            with val_tabs[0]:

                st.markdown("#### Current Valuation Factors")

                pe = safe_value(info, "trailingPE")
                fpe = safe_value(info, "forwardPE")
                pb = safe_value(info, "priceToBook")
                ps = safe_value(info, "priceToSalesTrailing12Months")
                ev_ebitda = safe_value(info, "enterpriseToEbitda")
                ev_rev = safe_value(info, "enterpriseToRevenue")
                roe = safe_value(info, "returnOnEquity")
                de = safe_value(info, "debtToEquity")
                revenue_growth = safe_value(info, "revenueGrowth")
                dividend_yield = safe_value(info, "dividendYield")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("P/E (TTM)", format_ratio(pe))
                c2.metric("Forward P/E", format_ratio(fpe))
                c3.metric("P/B", format_ratio(pb))
                c4.metric("P/S", format_ratio(ps))

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("EV/EBITDA", format_ratio(ev_ebitda))
                c2.metric("EV/Revenue", format_ratio(ev_rev))
                c3.metric(
                    "ROE",
                    format_percent(roe) if roe is not None else "N/A"
                )
                c4.metric("Debt/Equity", format_ratio(de))

                c1, c2 = st.columns(2)
                c1.metric(
                    "Revenue Growth",
                    format_percent(revenue_growth)
                    if revenue_growth is not None else "N/A"
                )
                c2.metric(
                    "Dividend Yield",
                    format_percent(dividend_yield)
                    if dividend_yield is not None else "N/A"
                )

                # ------------------------------------------------
                # PEER UNIVERSE
                # ------------------------------------------------

                st.markdown("#### Comparable Company Valuation")

                base_record = UNIVERSE_BY_TICKER.get(ticker)

                peer_pes = []
                comparable_tickers = []

                if base_record:
                    base_asset_class = str(
                        base_record.get("asset_class", "")
                    ).strip()

                    base_region = str(
                        base_record.get("region", "")
                    ).strip()

                    peer_df = UNIVERSE_DF.copy()

                    if base_asset_class:
                        peer_df = peer_df[
                            peer_df["asset_class"]
                            .astype(str)
                            .str.strip()
                            .str.upper()
                            == base_asset_class.upper()
                        ]

                    if base_region:
                        peer_df = peer_df[
                            peer_df["region"]
                            .astype(str)
                            .str.strip()
                            .str.lower()
                            == base_region.lower()
                        ]

                    comparable_tickers = [
                        str(t).strip()
                        for t in peer_df["ticker"].tolist()
                        if str(t).strip() != ticker
                    ]

                    for t in comparable_tickers[:20]:
                        peer_info = get_company_info(t)
                        p = safe_value(peer_info, "trailingPE")

                        if p is not None:
                            try:
                                if float(p) > 0:
                                    peer_pes.append(float(p))
                            except Exception:
                                pass

                if peer_pes:

                    avg_peer_pe = float(np.mean(peer_pes))
                    median_peer_pe = float(np.median(peer_pes))
                    eps = safe_value(info, "trailingEps")
                    current_price = safe_value(info, "currentPrice")

                    st.markdown("#### Peer P/E Statistics")

                    c1, c2, c3 = st.columns(3)
                    c1.metric(
                        "Comparable Avg P/E",
                        f"{avg_peer_pe:.2f}x"
                    )
                    c2.metric(
                        "Comparable Median P/E",
                        f"{median_peer_pe:.2f}x"
                    )
                    c3.metric(
                        "Company P/E",
                        format_ratio(pe)
                    )

                    if eps is not None and eps > 0:

                        implied_avg = avg_peer_pe * eps
                        implied_median = median_peer_pe * eps

                        st.markdown("#### Implied Fair Value")

                        c1, c2, c3 = st.columns(3)

                        c1.metric(
                            "Current Price",
                            format_local_money(
                                current_price,
                                ticker
                            )
                        )

                        c2.metric(
                            "Fair Value @ Avg P/E",
                            format_local_money(
                                implied_avg,
                                ticker
                            )
                        )

                        c3.metric(
                            "Fair Value @ Median P/E",
                            format_local_money(
                                implied_median,
                                ticker
                            )
                        )

                        if current_price:
                            avg_upside = (
                                implied_avg / current_price - 1
                            ) * 100

                            median_upside = (
                                implied_median / current_price - 1
                            ) * 100

                            c1, c2 = st.columns(2)

                            c1.metric(
                                "Upside / Downside - Avg",
                                f"{avg_upside:+.2f}%"
                            )

                            c2.metric(
                                "Upside / Downside - Median",
                                f"{median_upside:+.2f}%"
                            )

                        ai_facts = f"""
Company: {company_name}
Ticker: {ticker}
Listing currency: {local_currency}

Current P/E: {pe}
Forward P/E: {fpe}
P/B: {pb}
P/S: {ps}
EV/EBITDA: {ev_ebitda}
EV/Revenue: {ev_rev}
ROE: {roe}
Debt/Equity: {de}
Revenue Growth: {revenue_growth}
Dividend Yield: {dividend_yield}

Comparable average P/E: {avg_peer_pe}
Comparable median P/E: {median_peer_pe}
Trailing EPS: {eps}
Current price: {current_price}
Fair value using average P/E: {implied_avg}
Fair value using median P/E: {implied_median}
Average-P/E implied upside/downside: {avg_upside if current_price else "N/A"}%
Median-P/E implied upside/downside: {median_upside if current_price else "N/A"}%
"""

                        generate_genai_analysis(
                            "Relative Valuation Interpretation",
                            ai_facts
                        )

                    else:
                        st.info(
                            "Trailing EPS is not positive/available, "
                            "so P/E-based implied fair value cannot be calculated."
                        )

                else:
                    st.info(
                        "No sufficient comparable P/E data was found "
                        "for this security's asset class and region."
                    )

            # ====================================================
            # DCF
            # ====================================================

            with val_tabs[1]:

                st.caption(
                    "FCFF DCF model. All key assumptions are visible and editable."
                )

                default_revenue = (
                    safe_value(info, "totalRevenue", 0) or 0
                )

                default_shares = (
                    safe_value(info, "sharesOutstanding", 0) or 0
                )

                default_net_debt = (
                    (safe_value(info, "totalDebt", 0) or 0)
                    -
                    (safe_value(info, "totalCash", 0) or 0)
                )

                default_price = safe_value(
                    info,
                    "currentPrice",
                    None
                )

                st.markdown("#### DCF Assumptions")

                a1, a2, a3 = st.columns(3)

                with a1:
                    growth_rate = st.slider(
                        "Revenue Growth Rate",
                        0.0,
                        0.40,
                        0.10,
                        0.01,
                        key="valuation_growth_rate"
                    )

                    years = st.slider(
                        "Forecast Horizon (years)",
                        3,
                        10,
                        5,
                        key="valuation_years"
                    )

                with a2:
                    ebitda_margin = st.slider(
                        "EBITDA Margin",
                        0.05,
                        0.60,
                        0.20,
                        0.01,
                        key="valuation_ebitda_margin"
                    )

                    tax_rate = st.slider(
                        "Tax Rate",
                        0.10,
                        0.40,
                        0.25,
                        0.01,
                        key="valuation_tax_rate"
                    )

                with a3:
                    capex_pct = st.slider(
                        "Capex (% Revenue)",
                        0.01,
                        0.25,
                        0.06,
                        0.01,
                        key="valuation_capex_pct"
                    )

                    wc_pct = st.slider(
                        "Working Capital (% Revenue)",
                        0.0,
                        0.10,
                        0.02,
                        0.01,
                        key="valuation_wc_pct"
                    )

                a4, a5 = st.columns(2)

                with a4:
                    wacc = st.slider(
                        "WACC",
                        0.06,
                        0.20,
                        0.12,
                        0.005,
                        key="valuation_wacc"
                    )

                with a5:
                    terminal_growth = st.slider(
                        "Terminal Growth Rate",
                        0.0,
                        0.06,
                        0.04,
                        0.005,
                        key="valuation_terminal_growth"
                    )

                st.markdown("#### Base Financial Inputs")

                c1, c2, c3 = st.columns(3)

                with c1:
                    revenue_input = st.number_input(
                        f"Base Revenue ({local_currency})",
                        min_value=0.0,
                        value=float(default_revenue),
                        step=100_000_000.0,
                        key="valuation_revenue"
                    )

                with c2:
                    shares_input = st.number_input(
                        "Shares Outstanding",
                        min_value=0.0,
                        value=float(default_shares),
                        step=1_000_000.0,
                        key="valuation_shares"
                    )

                with c3:
                    net_debt_input = st.number_input(
                        f"Net Debt ({local_currency})",
                        value=float(default_net_debt),
                        step=100_000_000.0,
                        key="valuation_net_debt"
                    )

                if st.button(
                    "Run DCF",
                    type="primary",
                    key="valuation_run_dcf"
                ):

                    if wacc <= terminal_growth:

                        st.error(
                            "WACC must be greater than terminal growth."
                        )

                    elif revenue_input <= 0 or shares_input <= 0:

                        st.error(
                            "Revenue and shares outstanding must be greater than zero."
                        )

                    else:

                        result = run_dcf(
                            revenue_input,
                            ebitda_margin,
                            tax_rate,
                            capex_pct,
                            wacc,
                            terminal_growth,
                            growth_rate,
                            years,
                            net_debt_input,
                            shares_input,
                            wc_pct=wc_pct
                        )

                        if result is None:

                            st.error(
                                "DCF could not be computed with these inputs."
                            )

                        else:

                            st.markdown("#### DCF Outputs")

                            r1, r2, r3, r4 = st.columns(4)

                            r1.metric(
                                "Enterprise Value",
                                format_local_scale(
                                    result["enterprise_value"],
                                    ticker
                                )
                            )

                            r2.metric(
                                "Equity Value",
                                format_local_scale(
                                    result["equity_value"],
                                    ticker
                                )
                            )

                            r3.metric(
                                "Fair Value / Share",
                                format_local_money(
                                    result["fair_value_per_share"],
                                    ticker
                                )
                            )

                            if default_price:
                                dcf_upside = (
                                    result["fair_value_per_share"]
                                    / default_price
                                    - 1
                                ) * 100

                                r4.metric(
                                    "Current Price",
                                    format_local_money(
                                        default_price,
                                        ticker
                                    ),
                                    f"{dcf_upside:+.2f}%"
                                )
                            else:
                                r4.metric(
                                    "Current Price",
                                    "N/A"
                                )

                            proj_df = pd.DataFrame(
                                result["projections"]
                            )

                            proj_df["year"] = proj_df["year"].apply(
                                lambda y: f"Year {y}"
                            )

                            proj_df = proj_df.rename(
                                columns={
                                    "year": "Period",
                                    "revenue": "Revenue",
                                    "ebitda": "EBITDA",
                                    "fcff": "FCFF",
                                    "discounted_fcff": "Discounted FCFF",
                                }
                            )

                            for c in [
                                "Revenue",
                                "EBITDA",
                                "FCFF",
                                "Discounted FCFF"
                            ]:
                                proj_df[c] = proj_df[c].apply(
                                    lambda v: format_local_scale(
                                        v,
                                        ticker
                                    )
                                )

                            st.markdown(
                                "#### FCFF Projection"
                            )

                            render_terminal_table(proj_df)

                            st.markdown(
                                "#### Sensitivity - Fair Value / Share"
                            )

                            wacc_range = [
                                round(wacc + d, 3)
                                for d in [
                                    -0.02,
                                    -0.01,
                                    0,
                                    0.01,
                                    0.02
                                ]
                            ]

                            tg_range = [
                                round(terminal_growth + d, 3)
                                for d in [
                                    -0.01,
                                    -0.005,
                                    0,
                                    0.005,
                                    0.01
                                ]
                            ]

                            wacc_range = [
                                w for w in wacc_range
                                if w > 0
                            ]

                            tg_range = [
                                t for t in tg_range
                                if t >= 0
                            ]

                            grid = dcf_sensitivity(
                                revenue_input,
                                ebitda_margin,
                                tax_rate,
                                capex_pct,
                                growth_rate,
                                years,
                                net_debt_input,
                                shares_input,
                                wacc_range,
                                tg_range
                            )

                            sens_df = pd.DataFrame(
                                grid,
                                index=[
                                    f"WACC {w * 100:.1f}%"
                                    for w in wacc_range
                                ],
                                columns=[
                                    f"g {t * 100:.1f}%"
                                    for t in tg_range
                                ],
                            )

                            sens_df_display = sens_df.map(
                                lambda v:
                                format_local_money(
                                    v,
                                    ticker,
                                    0
                                )
                                if v is not None
                                else "N/A"
                            )

                            render_terminal_table(sens_df_display)

                            st.caption(
                                "Rows = WACC. Columns = terminal growth. "
                                "Each cell shows the resulting fair value "
                                "per share with other assumptions held constant."
                            )

                            ai_facts = f"""
Company: {company_name}
Ticker: {ticker}
Listing currency: {local_currency}

DCF assumptions:
Revenue growth: {growth_rate:.2%}
Forecast horizon: {years} years
EBITDA margin: {ebitda_margin:.2%}
Tax rate: {tax_rate:.2%}
Capex / Revenue: {capex_pct:.2%}
Working Capital / Revenue: {wc_pct:.2%}
WACC: {wacc:.2%}
Terminal growth: {terminal_growth:.2%}

Base revenue: {revenue_input}
Shares outstanding: {shares_input}
Net debt: {net_debt_input}

Enterprise value: {result["enterprise_value"]}
Equity value: {result["equity_value"]}
Fair value / share: {result["fair_value_per_share"]}
Current price: {default_price}
DCF implied upside/downside: {dcf_upside if default_price else "N/A"}%
"""

                            generate_genai_analysis(
                                "DCF Interpretation",
                                ai_facts
                            )



elif module == "Peer Comparison":

    render_apex_page_header(
        "Peer Comparison",
        "Comparable analysis across sector peers and selected benchmarks",
        "BENCHMARK",
        "Master Universe"
    )

    ticker = security_dropdown(
        "Select Security",
        key="security_selector_3"
    )

    if ticker:

        company_info = get_company_info(ticker)

        company_name = safe_value(
            company_info,
            "longName",
            safe_value(
                company_info,
                "shortName",
                ticker
            )
        )

        listing_currency = get_listing_currency(
            ticker
        )

        st.caption(
            f"{company_name}  •  "
            f"Listing currency: {listing_currency}"
        )

        # --------------------------------------------------------
        # MANUAL PEER SELECTION FROM THE ENTIRE MASTER UNIVERSE
        # --------------------------------------------------------
        #
        # Peer selection is intentionally manual.
        # No automatic sector, region, country, or asset-class
        # filtering is applied. The user can compare the selected
        # security with any securities available in the master
        # universe.
        # --------------------------------------------------------

        primary_ticker = str(ticker).strip()

        peer_universe = UNIVERSE_DF.copy()

        if "ticker" in peer_universe.columns:
            peer_universe["ticker"] = (
                peer_universe["ticker"]
                .astype(str)
                .str.strip()
            )

        # Never allow the primary security to appear as a peer.
        peer_universe = peer_universe[
            peer_universe["ticker"] != primary_ticker
        ].copy()

        # Build searchable display labels directly from the master
        # universe. No Yahoo lookup is required just to populate the
        # peer selector.
        peer_name_map = {}

        for _, record in peer_universe.iterrows():

            peer_ticker = str(
                record.get("ticker", "")
            ).strip()

            if not peer_ticker:
                continue

            peer_name = str(
                record.get("name", "")
            ).strip()

            if not peer_name or peer_name.lower() == "nan":
                peer_name = peer_ticker

            label = f"{peer_name} " + chr(8226) + f" {peer_ticker}"

            # Ensure labels remain unique even if the universe
            # contains duplicate security names.
            if label in peer_name_map:
                label = f"{peer_name} " + chr(8226) + f" {peer_ticker}"

            peer_name_map[label] = peer_ticker

        peer_options = list(peer_name_map.keys())

        peer_choices = st.multiselect(
            "Peers to compare",
            options=peer_options,
            default=[],
            key="peer_comparison_peer_names",
            placeholder="Search and select any securities from the master universe"
        )

        compare_clicked = st.button(
            "Compare",
            type="primary",
            key="peer_comparison_compare"
        )

        if compare_clicked:
            st.session_state["peer_comparison_active"] = True

        if (
            compare_clicked
            or st.session_state.get(
                "peer_comparison_active",
                False
            )
        ):

            remember_ticker(ticker)

            tickers_to_compare = [ticker] + [
                peer_name_map[name]
                for name in peer_choices
                if name in peer_name_map
            ]

            rows = []

            # ------------------------------------------------
            # DETERMINISTIC METRIC HELPERS
            # ------------------------------------------------

            def _peer_float(value):
                try:
                    if value is None:
                        return None

                    value = float(value)

                    if not np.isfinite(value):
                        return None

                    return value

                except Exception:
                    return None

            def _peer_percent(value):
                value = _peer_float(value)

                if value is None:
                    return "N/A"

                return f"{value:,.2f}%"

            def _peer_ratio(value):
                value = _peer_float(value)

                if value is None:
                    return "N/A"

                return f"{value:,.2f}"

            def _peer_local_value(value, ticker_value):
                value = _peer_float(value)

                if value is None:
                    return "N/A"

                return format_local_scale(
                    value,
                    ticker_value
                )

            def _peer_asset_class(ticker_value):

                ticker_value = (
                    str(ticker_value)
                    .strip()
                    .upper()
                )

                try:

                    match = UNIVERSE_DF[
                        UNIVERSE_DF["ticker"]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        == ticker_value
                    ]

                    if not match.empty:

                        return str(
                            match.iloc[0].get(
                                "asset_class",
                                ""
                            )
                        ).strip()

                except Exception:
                    pass

                return "Unknown"

            def _peer_history(ticker_value):

                try:

                    history = yf.Ticker(
                        str(ticker_value).strip()
                    ).history(
                        period="2y",
                        interval="1d",
                        auto_adjust=False,
                        timeout=10
                    )

                    if (
                        history is None
                        or history.empty
                        or "Close" not in history.columns
                    ):
                        return pd.Series(
                            dtype=float
                        )

                    close = (
                        history["Close"]
                        .dropna()
                        .astype(float)
                    )

                    return close

                except Exception:

                    return pd.Series(
                        dtype=float
                    )

            def _peer_return(close, days):

                if close is None or len(close) < 2:
                    return None

                try:

                    latest = float(
                        close.iloc[-1]
                    )

                    if len(close) > days:

                        base = float(
                            close.iloc[-days - 1]
                        )

                    else:

                        base = float(
                            close.iloc[0]
                        )

                    if base == 0:
                        return None

                    return (
                        (latest / base) - 1.0
                    ) * 100.0

                except Exception:

                    return None

            def _peer_cagr(close):

                if close is None or len(close) < 2:
                    return None

                try:

                    first = float(
                        close.iloc[0]
                    )

                    last = float(
                        close.iloc[-1]
                    )

                    if first <= 0 or last <= 0:
                        return None

                    days = (
                        close.index[-1]
                        - close.index[0]
                    ).days

                    if days <= 0:
                        return None

                    years = days / 365.25

                    return (
                        (
                            (last / first)
                            ** (1.0 / years)
                        ) - 1.0
                    ) * 100.0

                except Exception:

                    return None

            def _peer_volatility(close):

                if close is None or len(close) < 3:
                    return None

                try:

                    returns = (
                        close
                        .pct_change()
                        .dropna()
                    )

                    if returns.empty:
                        return None

                    return float(
                        returns.std()
                        * np.sqrt(252)
                        * 100.0
                    )

                except Exception:

                    return None

            def _peer_max_drawdown(close):

                if close is None or len(close) < 2:
                    return None

                try:

                    running_max = close.cummax()

                    drawdown = (
                        close / running_max
                    ) - 1.0

                    return float(
                        drawdown.min()
                        * 100.0
                    )

                except Exception:

                    return None

            def _peer_sharpe(close):

                if close is None or len(close) < 3:
                    return None

                try:

                    returns = (
                        close
                        .pct_change()
                        .dropna()
                    )

                    if returns.empty:
                        return None

                    std = float(
                        returns.std()
                    )

                    if std == 0:
                        return None

                    # Zero risk-free-rate proxy.
                    return float(
                        returns.mean()
                        / std
                        * np.sqrt(252)
                    )

                except Exception:

                    return None

            def _peer_sortino(close):

                if close is None or len(close) < 3:
                    return None

                try:

                    returns = (
                        close
                        .pct_change()
                        .dropna()
                    )

                    if returns.empty:
                        return None

                    downside = returns[
                        returns < 0
                    ]

                    if downside.empty:
                        return None

                    downside_std = float(
                        downside.std()
                    )

                    if downside_std == 0:
                        return None

                    # Zero risk-free-rate proxy.
                    return float(
                        returns.mean()
                        / downside_std
                        * np.sqrt(252)
                    )

                except Exception:

                    return None

            # ------------------------------------------------
            # FETCH PRIMARY + MANUALLY SELECTED PEERS
            # ------------------------------------------------

            histories = {}

            for t in tickers_to_compare:

                info = get_company_info(t)

                if not isinstance(info, dict):
                    info = {}

                close = _peer_history(t)

                histories[t] = close

                current_price = _peer_float(
                    info.get("currentPrice")
                )

                if (
                    current_price is None
                    and close is not None
                    and not close.empty
                ):

                    current_price = _peer_float(
                        close.iloc[-1]
                    )

                rows.append({

                    "Company": safe_value(
                        info,
                        "shortName",
                        t
                    ),

                    "Ticker": display_ticker(t),

                    "Currency": get_listing_currency(t),

                    "Asset Class": _peer_asset_class(t),

                    "Price": current_price,

                    "Market Cap": _peer_float(
                        info.get("marketCap")
                    ),

                    "Revenue": _peer_float(
                        info.get("totalRevenue")
                    ),

                    "Net Income": _peer_float(
                        info.get("netIncomeToCommon")
                    ),

                    "P/E": _peer_float(
                        info.get("trailingPE")
                    ),

                    "P/B": _peer_float(
                        info.get("priceToBook")
                    ),

                    "EV/EBITDA": _peer_float(
                        info.get("enterpriseToEbitda")
                    ),

                    "ROE": _peer_float(
                        info.get("returnOnEquity")
                    ),

                    "ROA": _peer_float(
                        info.get("returnOnAssets")
                    ),

                    "Debt/Equity": _peer_float(
                        info.get("debtToEquity")
                    ),

                    "Revenue Growth": _peer_float(
                        info.get("revenueGrowth")
                    ),

                    "Earnings Growth": _peer_float(
                        info.get("earningsGrowth")
                    ),

                    "Net Margin": _peer_float(
                        info.get("profitMargins")
                    ),

                    "Operating Margin": _peer_float(
                        info.get("operatingMargins")
                    ),

                    "Dividend Yield": _peer_float(
                        info.get("dividendYield")
                    ),

                    "Beta": _peer_float(
                        info.get("beta")
                    ),

                    "EPS": _peer_float(
                        info.get("trailingEps")
                    ),

                    "Debt": _peer_float(
                        info.get("totalDebt")
                    ),

                    "Cash": _peer_float(
                        info.get("totalCash")
                    ),

                    "1M Return": _peer_return(
                        close,
                        21
                    ),

                    "3M Return": _peer_return(
                        close,
                        63
                    ),

                    "6M Return": _peer_return(
                        close,
                        126
                    ),

                    "1Y Return": _peer_return(
                        close,
                        252
                    ),

                    "CAGR": _peer_cagr(
                        close
                    ),

                    "Volatility": _peer_volatility(
                        close
                    ),

                    "Max Drawdown": _peer_max_drawdown(
                        close
                    ),

                    "Sharpe": _peer_sharpe(
                        close
                    ),

                    "Sortino": _peer_sortino(
                        close
                    ),
                })

            raw_df = pd.DataFrame(rows)

            if raw_df.empty:

                st.warning(
                    "No comparison data was returned for the selected securities."
                )

            else:

                # --------------------------------------------
                # MAIN COMPARISON TABLE
                # --------------------------------------------

                display_df = raw_df.copy()

                if "Price" in display_df.columns:

                    display_df["Price"] = display_df.apply(
                        lambda row: (
                            format_local_scale(
                                row["Price"],
                                tickers_to_compare[
                                    row.name
                                ]
                            )
                            if _peer_float(
                                row["Price"]
                            ) is not None
                            else "N/A"
                        ),
                        axis=1
                    )

                for col in [
                    "Market Cap",
                    "Revenue",
                    "Net Income",
                    "Debt",
                    "Cash"
                ]:

                    if col in display_df.columns:

                        display_df[col] = display_df.apply(
                            lambda row, c=col: (
                                _peer_local_value(
                                    row[c],
                                    tickers_to_compare[
                                        row.name
                                    ]
                                )
                                if _peer_float(
                                    row[c]
                                ) is not None
                                else "N/A"
                            ),
                            axis=1
                        )

                for col in [
                    "P/E",
                    "P/B",
                    "EV/EBITDA",
                    "Debt/Equity",
                    "Beta",
                    "EPS",
                    "Sharpe",
                    "Sortino"
                ]:

                    if col in display_df.columns:

                        display_df[col] = (
                            display_df[col]
                            .apply(_peer_ratio)
                        )

                for col in [
                    "ROE",
                    "ROA",
                    "Revenue Growth",
                    "Earnings Growth",
                    "Net Margin",
                    "Operating Margin",
                    "Dividend Yield",
                    "1M Return",
                    "3M Return",
                    "6M Return",
                    "1Y Return",
                    "CAGR",
                    "Volatility",
                    "Max Drawdown"
                ]:

                    if col in display_df.columns:

                        display_df[col] = (
                            display_df[col]
                            .apply(_peer_percent)
                        )

                st.markdown(
                    "#### Comparison"
                )

                # ------------------------------------------------
                # VERTICAL COMPARISON TABLE
                # ------------------------------------------------
                # The peer comparison contains many metrics.
                # Keeping every metric as a column makes the table
                # unreadable on normal screens.
                #
                # Instead:
                #   Rows    = metrics
                #   Columns = selected securities
                #
                # This keeps the complete dataset while making the
                # comparison readable.
                vertical_df = (
                    display_df
                    .set_index("Company")
                    .T
                    .reset_index()
                    .rename(
                        columns={
                            "index": "Metric"
                        }
                    )
                )

                render_terminal_table(
                    vertical_df,
                    empty_message=(
                        "No peer comparison data available."
                    )
                )

                st.download_button(
                    "Download Comparison CSV",
                    data=display_df.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="peer_comparison.csv",
                    mime="text/csv",
                    key="peer_comparison_download"
                )

                # --------------------------------------------
                # KPI SNAPSHOT
                # --------------------------------------------

                st.markdown(
                    "#### KPI Snapshot"
                )

                kpi_specs = [
                    ("Price", "Price", "local"),
                    ("Market Cap", "Market Cap", "local"),
                    ("P/E", "P/E", "ratio"),
                    ("P/B", "P/B", "ratio"),
                    ("ROE", "ROE", "percent"),
                    ("Debt / Equity", "Debt/Equity", "ratio"),
                    ("Revenue Growth", "Revenue Growth", "percent"),
                    ("Net Margin", "Net Margin", "percent"),
                    ("Dividend Yield", "Dividend Yield", "percent"),
                    ("Beta", "Beta", "ratio"),
                    ("1Y Return", "1Y Return", "percent"),
                    ("Volatility", "Volatility", "percent"),
                ]

                for row_start in range(
                    0,
                    len(kpi_specs),
                    4
                ):

                    cols = st.columns(4)

                    for idx, (
                        label,
                        metric_key,
                        value_type
                    ) in enumerate(
                        kpi_specs[
                            row_start:row_start + 4
                        ]
                    ):

                        value = _peer_float(
                            raw_df.iloc[0].get(
                                metric_key
                            )
                        )

                        if value is None:

                            shown = "N/A"

                        elif value_type == "local":

                            shown = _peer_local_value(
                                value,
                                tickers_to_compare[0]
                            )

                        elif value_type == "percent":

                            shown = _peer_percent(
                                value
                            )

                        else:

                            shown = _peer_ratio(
                                value
                            )

                        cols[idx].metric(
                            label,
                            shown
                        )

                # --------------------------------------------
                # ====================================================

                # ====================================================
                # DYNAMIC PEER ANALYTICS WORKSPACE
                # ====================================================

                st.markdown("#### Interactive Peer Analytics")

                st.caption(
                    "Switch between analytical views instead of displaying "
                    "six large charts at once. All views use the securities "
                    "manually selected above."
                )

                peer_view_options = [
                    "Risk & Return",
                    "Performance",
                    "Growth & Quality",
                    "Financial Strength",
                    "Returns & Risk Matrix",
                ]

                if (
                    "peer_dynamic_analysis_view"
                    not in st.session_state
                    or st.session_state[
                        "peer_dynamic_analysis_view"
                    ] not in peer_view_options
                ):
                    st.session_state[
                        "peer_dynamic_analysis_view"
                    ] = "Risk & Return"

                peer_view = st.selectbox(
                    "Explore analysis",
                    peer_view_options,
                    key="peer_dynamic_analysis_view",
                )

                # ----------------------------------------------------
                # COMMON DATA PREPARATION
                # ----------------------------------------------------

                visual_df = raw_df.copy()

                visual_numeric_columns = [
                    "1M Return",
                    "3M Return",
                    "6M Return",
                    "1Y Return",
                    "CAGR",
                    "Volatility",
                    "Max Drawdown",
                    "Sharpe",
                    "Sortino",
                    "P/E",
                    "P/B",
                    "ROE",
                    "ROA",
                    "Net Margin",
                    "Operating Margin",
                    "Revenue Growth",
                    "Earnings Growth",
                    "Debt/Equity",
                ]

                for column in visual_numeric_columns:
                    if column in visual_df.columns:
                        visual_df[column] = pd.to_numeric(
                            visual_df[column],
                            errors="coerce",
                        )

                primary_ticker = str(
                    visual_df.iloc[0]["Ticker"]
                ).strip()

                # ====================================================
                # VIEW 1 ? RISK & RETURN
                # ====================================================

                if peer_view == "Risk & Return":

                    st.markdown("##### Risk?Return Map")

                    positioning = visual_df[
                        [
                            "Company",
                            "Ticker",
                            "1Y Return",
                            "Volatility",
                            "Sharpe",
                        ]
                    ].dropna(
                        subset=[
                            "1Y Return",
                            "Volatility",
                        ]
                    ).copy()

                    if not positioning.empty:

                        for column in [
                            "1Y Return",
                            "Volatility",
                        ]:
                            if (
                                positioning[column]
                                .abs()
                                .median()
                                <= 2
                            ):
                                positioning[column] *= 100

                        fig = go.Figure()

                        for _, row in positioning.iterrows():

                            ticker = str(
                                row["Ticker"]
                            ).strip()

                            is_primary = (
                                ticker == primary_ticker
                            )

                            company = str(
                                row["Company"]
                            )

                            sharpe_text = (
                                f"{float(row['Sharpe']):.2f}"
                                if (
                                    "Sharpe" in row.index
                                    and pd.notna(row["Sharpe"])
                                )
                                else "N/A"
                            )

                            fig.add_trace(
                                go.Scatter(
                                    x=[
                                        float(
                                            row["Volatility"]
                                        )
                                    ],
                                    y=[
                                        float(
                                            row["1Y Return"]
                                        )
                                    ],
                                    mode=(
                                        "markers+text"
                                        if is_primary
                                        else "markers"
                                    ),
                                    text=(
                                        [company]
                                        if is_primary
                                        else None
                                    ),
                                    textposition="top center",
                                    name=company,
                                    marker=dict(
                                        size=20
                                        if is_primary
                                        else 13,
                                        line=dict(
                                            width=2
                                            if is_primary
                                            else 0
                                        ),
                                    ),
                                    hovertemplate=(
                                        "<b>%{fullData.name}</b>"
                                        "<br>1Y Return: %{y:.2f}%"
                                        "<br>Volatility: %{x:.2f}%"
                                        "<br>Sharpe: "
                                        + sharpe_text
                                        + "<extra></extra>"
                                    ),
                                    showlegend=False,
                                )
                            )

                        median_return = float(
                            positioning[
                                "1Y Return"
                            ].median()
                        )

                        median_risk = float(
                            positioning[
                                "Volatility"
                            ].median()
                        )

                        fig.add_hline(
                            y=median_return,
                            line_dash="dot",
                            annotation_text="Peer median return",
                            annotation_position="top left",
                        )

                        fig.add_vline(
                            x=median_risk,
                            line_dash="dot",
                            annotation_text="Peer median risk",
                            annotation_position="top right",
                        )

                        fig.update_layout(
                            height=460,
                            margin=dict(
                                l=20,
                                r=20,
                                t=35,
                                b=20,
                            ),
                            xaxis_title="Annualized volatility",
                            yaxis_title="1Y return",
                            hovermode="closest",
                        )

                        st.plotly_chart(
                            fig,
                            width="stretch",
                            config={
                                "displaylogo": False,
                                "responsive": True,
                            },
                        )

                        st.caption(
                            "The primary security is labelled directly. "
                            "Dashed lines represent the selected peer-set "
                            "medians."
                        )

                    else:

                        st.info(
                            "Risk-return data is not sufficiently available."
                        )

                    # ------------------------------------------------
                    # DYNAMIC METRIC EXPLORER
                    # ------------------------------------------------

                    st.markdown("##### Metric Explorer")

                    metric_options = [
                        "1Y Return",
                        "Volatility",
                        "Sharpe",
                        "Max Drawdown",
                        "ROE",
                        "Net Margin",
                        "Revenue Growth",
                        "Debt/Equity",
                    ]

                    available_metrics = [
                        metric
                        for metric in metric_options
                        if (
                            metric in visual_df.columns
                            and visual_df[
                                metric
                            ].notna().sum() > 0
                        )
                    ]

                    if available_metrics:

                        selected_metric = st.selectbox(
                            "Select metric",
                            available_metrics,
                            key="peer_metric_explorer",
                        )

                        metric_df = visual_df[
                            [
                                "Company",
                                "Ticker",
                                selected_metric,
                            ]
                        ].dropna(
                            subset=[
                                selected_metric
                            ]
                        ).copy()

                        if (
                            selected_metric
                            not in [
                                "Sharpe",
                                "Debt/Equity",
                            ]
                            and (
                                not metric_df.empty
                            )
                            and (
                                metric_df[
                                    selected_metric
                                ].abs().median()
                                <= 2
                            )
                        ):
                            metric_df[
                                selected_metric
                            ] *= 100

                        metric_df = metric_df.sort_values(
                            selected_metric
                        )

                        median_value = float(
                            metric_df[
                                selected_metric
                            ].median()
                        )

                        fig_metric = go.Figure()

                        for _, row in metric_df.iterrows():

                            ticker = str(
                                row["Ticker"]
                            ).strip()

                            is_primary = (
                                ticker == primary_ticker
                            )

                            company = str(
                                row["Company"]
                            )

                            value = float(
                                row[selected_metric]
                            )

                            fig_metric.add_trace(
                                go.Scatter(
                                    x=[
                                        median_value,
                                        value,
                                    ],
                                    y=[
                                        company,
                                        company,
                                    ],
                                    mode="lines+markers",
                                    line=dict(
                                        width=4
                                        if is_primary
                                        else 2,
                                    ),
                                    marker=dict(
                                        size=11
                                        if is_primary
                                        else 7,
                                    ),
                                    name=company,
                                    hovertemplate=(
                                        "<b>%{y}</b>"
                                        "<br>"
                                        + selected_metric
                                        + ": %{x:.2f}"
                                        + "<extra></extra>"
                                    ),
                                    showlegend=False,
                                )
                            )

                        fig_metric.add_vline(
                            x=median_value,
                            line_dash="dash",
                            annotation_text="Peer median",
                            annotation_position="top",
                        )

                        fig_metric.update_layout(
                            height=max(
                                340,
                                55 * len(metric_df),
                            ),
                            margin=dict(
                                l=20,
                                r=20,
                                t=35,
                                b=20,
                            ),
                            xaxis_title=selected_metric,
                            yaxis_title="",
                        )

                        st.plotly_chart(
                            fig_metric,
                            width="stretch",
                            config={
                                "displaylogo": False,
                                "responsive": True,
                            },
                        )

                # ====================================================
                # VIEW 2 ? PERFORMANCE
                # ====================================================

                elif peer_view == "Performance":

                    st.markdown("##### Performance Explorer")

                    performance_metrics = [
                        "1M Return",
                        "3M Return",
                        "6M Return",
                        "1Y Return",
                        "CAGR",
                    ]

                    available_performance = [
                        metric
                        for metric in performance_metrics
                        if (
                            metric in visual_df.columns
                            and visual_df[
                                metric
                            ].notna().sum() > 0
                        )
                    ]

                    if available_performance:

                        selected_period = st.selectbox(
                            "Performance period",
                            available_performance,
                            key="peer_performance_period",
                        )

                        perf = visual_df[
                            [
                                "Company",
                                "Ticker",
                                selected_period,
                            ]
                        ].dropna(
                            subset=[
                                selected_period
                            ]
                        ).copy()

                        if (
                            selected_period != "CAGR"
                            and (
                                not perf.empty
                            )
                            and (
                                perf[
                                    selected_period
                                ].abs().median()
                                <= 2
                            )
                        ):
                            perf[
                                selected_period
                            ] *= 100

                        perf = perf.sort_values(
                            selected_period
                        )

                        fig_perf = go.Figure()

                        for _, row in perf.iterrows():

                            ticker = str(
                                row["Ticker"]
                            ).strip()

                            is_primary = (
                                ticker == primary_ticker
                            )

                            fig_perf.add_trace(
                                go.Bar(
                                    x=[
                                        float(
                                            row[
                                                selected_period
                                            ]
                                        )
                                    ],
                                    y=[
                                        str(
                                            row["Company"]
                                        )
                                    ],
                                    orientation="h",
                                    name=str(
                                        row["Company"]
                                    ),
                                    marker=dict(
                                        opacity=1
                                        if is_primary
                                        else 0.60,
                                    ),
                                    hovertemplate=(
                                        "<b>%{y}</b>"
                                        "<br>"
                                        + selected_period
                                        + ": %{x:.2f}%"
                                        + "<extra></extra>"
                                    ),
                                    showlegend=False,
                                )
                            )

                        fig_perf.update_layout(
                            height=max(
                                350,
                                55 * len(perf),
                            ),
                            margin=dict(
                                l=20,
                                r=20,
                                t=35,
                                b=20,
                            ),
                            xaxis_title=selected_period,
                            yaxis_title="",
                            bargap=0.28,
                        )

                        st.plotly_chart(
                            fig_perf,
                            width="stretch",
                            config={
                                "displaylogo": False,
                                "responsive": True,
                            },
                        )

                    else:

                        st.info(
                            "Performance data is not sufficiently available."
                        )

                # ====================================================
                # VIEW 3 ? GROWTH & QUALITY
                # ====================================================

                elif peer_view == "Growth & Quality":

                    st.markdown("##### Growth vs Profitability")

                    growth_df = visual_df[
                        [
                            "Company",
                            "Ticker",
                            "Revenue Growth",
                            "Net Margin",
                        ]
                    ].dropna(
                        subset=[
                            "Revenue Growth",
                            "Net Margin",
                        ]
                    ).copy()

                    if not growth_df.empty:

                        for column in [
                            "Revenue Growth",
                            "Net Margin",
                        ]:
                            if (
                                growth_df[column]
                                .abs()
                                .median()
                                <= 2
                            ):
                                growth_df[column] *= 100

                        fig_growth = go.Figure()

                        for _, row in growth_df.iterrows():

                            ticker = str(
                                row["Ticker"]
                            ).strip()

                            is_primary = (
                                ticker == primary_ticker
                            )

                            company = str(
                                row["Company"]
                            )

                            fig_growth.add_trace(
                                go.Scatter(
                                    x=[
                                        float(
                                            row[
                                                "Revenue Growth"
                                            ]
                                        )
                                    ],
                                    y=[
                                        float(
                                            row[
                                                "Net Margin"
                                            ]
                                        )
                                    ],
                                    mode=(
                                        "markers+text"
                                        if is_primary
                                        else "markers"
                                    ),
                                    text=(
                                        [company]
                                        if is_primary
                                        else None
                                    ),
                                    textposition="top center",
                                    name=company,
                                    marker=dict(
                                        size=20
                                        if is_primary
                                        else 13,
                                    ),
                                    hovertemplate=(
                                        "<b>%{fullData.name}</b>"
                                        "<br>Revenue Growth: %{x:.2f}%"
                                        "<br>Net Margin: %{y:.2f}%"
                                        "<extra></extra>"
                                    ),
                                    showlegend=False,
                                )
                            )

                        median_growth = float(
                            growth_df[
                                "Revenue Growth"
                            ].median()
                        )

                        median_margin = float(
                            growth_df[
                                "Net Margin"
                            ].median()
                        )

                        fig_growth.add_vline(
                            x=median_growth,
                            line_dash="dot",
                            annotation_text="Median growth",
                            annotation_position="top right",
                        )

                        fig_growth.add_hline(
                            y=median_margin,
                            line_dash="dot",
                            annotation_text="Median margin",
                            annotation_position="top left",
                        )

                        fig_growth.update_layout(
                            height=460,
                            margin=dict(
                                l=20,
                                r=20,
                                t=35,
                                b=20,
                            ),
                            xaxis_title="Revenue growth",
                            yaxis_title="Net margin",
                            hovermode="closest",
                        )

                        st.plotly_chart(
                            fig_growth,
                            width="stretch",
                            config={
                                "displaylogo": False,
                                "responsive": True,
                            },
                        )

                    else:

                        st.info(
                            "Growth and profitability data is "
                            "not sufficiently available."
                        )

                    # ------------------------------------------------
                    # QUALITY METRIC SELECTOR
                    # ------------------------------------------------

                    quality_metrics = [
                        "ROE",
                        "ROA",
                        "Operating Margin",
                        "Net Margin",
                        "Earnings Growth",
                    ]

                    available_quality = [
                        metric
                        for metric in quality_metrics
                        if (
                            metric in visual_df.columns
                            and visual_df[
                                metric
                            ].notna().sum() > 0
                        )
                    ]

                    if available_quality:

                        st.markdown("##### Quality Metric")

                        selected_quality = st.selectbox(
                            "Select quality measure",
                            available_quality,
                            key="peer_quality_metric",
                        )

                        quality_df = visual_df[
                            [
                                "Company",
                                "Ticker",
                                selected_quality,
                            ]
                        ].dropna(
                            subset=[
                                selected_quality
                            ]
                        ).copy()

                        if (
                            not quality_df.empty
                            and quality_df[
                                selected_quality
                            ].abs().median()
                            <= 2
                        ):
                            quality_df[
                                selected_quality
                            ] *= 100

                        quality_df = quality_df.sort_values(
                            selected_quality
                        )

                        fig_quality = go.Figure()

                        for _, row in quality_df.iterrows():

                            ticker = str(
                                row["Ticker"]
                            ).strip()

                            is_primary = (
                                ticker == primary_ticker
                            )

                            fig_quality.add_trace(
                                go.Bar(
                                    x=[
                                        float(
                                            row[
                                                selected_quality
                                            ]
                                        )
                                    ],
                                    y=[
                                        str(
                                            row["Company"]
                                        )
                                    ],
                                    orientation="h",
                                    name=str(
                                        row["Company"]
                                    ),
                                    marker=dict(
                                        opacity=1
                                        if is_primary
                                        else 0.60,
                                    ),
                                    hovertemplate=(
                                        "<b>%{y}</b>"
                                        "<br>"
                                        + selected_quality
                                        + ": %{x:.2f}%"
                                        + "<extra></extra>"
                                    ),
                                    showlegend=False,
                                )
                            )

                        fig_quality.update_layout(
                            height=max(
                                340,
                                55 * len(quality_df),
                            ),
                            margin=dict(
                                l=20,
                                r=20,
                                t=35,
                                b=20,
                            ),
                            xaxis_title=selected_quality,
                            yaxis_title="",
                            bargap=0.28,
                        )

                        st.plotly_chart(
                            fig_quality,
                            width="stretch",
                            config={
                                "displaylogo": False,
                                "responsive": True,
                            },
                        )

                # ====================================================
                # VIEW 4 ? FINANCIAL STRENGTH
                # ====================================================

                elif peer_view == "Financial Strength":

                    st.markdown("##### Financial Strength Profile")

                    strength_metrics = [
                        ("ROE", False),
                        ("ROA", False),
                        ("Net Margin", False),
                        ("Revenue Growth", False),
                        ("Earnings Growth", False),
                        ("Debt/Equity", True),
                    ]

                    available_strength = [
                        item
                        for item in strength_metrics
                        if (
                            item[0] in visual_df.columns
                            and visual_df[
                                item[0]
                            ].notna().sum() >= 2
                        )
                    ]

                    if len(available_strength) >= 3:

                        categories = [
                            item[0]
                            for item in available_strength
                        ]

                        scores = pd.DataFrame(
                            index=visual_df.index
                        )

                        for metric, inverse in available_strength:

                            values = pd.to_numeric(
                                visual_df[metric],
                                errors="coerce",
                            )

                            if (
                                metric != "Debt/Equity"
                                and values.abs().median() <= 2
                            ):
                                values *= 100

                            minimum = values.min()
                            maximum = values.max()

                            if (
                                pd.isna(minimum)
                                or pd.isna(maximum)
                                or maximum == minimum
                            ):
                                normalized = pd.Series(
                                    50.0,
                                    index=values.index,
                                )
                            else:
                                normalized = (
                                    values - minimum
                                ) / (
                                    maximum - minimum
                                ) * 100

                            if inverse:
                                normalized = (
                                    100 - normalized
                                )

                            scores[metric] = normalized

                        scores["Company"] = visual_df[
                            "Company"
                        ].astype(str)

                        scores["Ticker"] = visual_df[
                            "Ticker"
                        ].astype(str)

                        fig_radar = go.Figure()

                        primary_rows = scores[
                            scores["Ticker"].str.strip()
                            == primary_ticker
                        ]

                        peer_rows = scores[
                            scores["Ticker"].str.strip()
                            != primary_ticker
                        ]

                        if not primary_rows.empty:

                            row = primary_rows.iloc[0]

                            primary_values = [
                                float(row[metric])
                                for metric in categories
                            ]

                            fig_radar.add_trace(
                                go.Scatterpolar(
                                    r=(
                                        primary_values
                                        + [primary_values[0]]
                                    ),
                                    theta=(
                                        categories
                                        + [categories[0]]
                                    ),
                                    fill="toself",
                                    mode="lines+markers",
                                    name=str(
                                        row["Company"]
                                    ),
                                    line=dict(
                                        width=3
                                    ),
                                    marker=dict(
                                        size=7
                                    ),
                                )
                            )

                        if not peer_rows.empty:

                            peer_median = [
                                float(
                                    peer_rows[
                                        metric
                                    ].median()
                                )
                                for metric in categories
                            ]

                            fig_radar.add_trace(
                                go.Scatterpolar(
                                    r=(
                                        peer_median
                                        + [peer_median[0]]
                                    ),
                                    theta=(
                                        categories
                                        + [categories[0]]
                                    ),
                                    fill="toself",
                                    mode="lines+markers",
                                    name="Peer median",
                                    line=dict(
                                        width=2,
                                        dash="dash",
                                    ),
                                    marker=dict(
                                        size=5
                                    ),
                                )
                            )

                        fig_radar.update_layout(
                            height=520,
                            margin=dict(
                                l=30,
                                r=30,
                                t=40,
                                b=30,
                            ),
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[
                                        0,
                                        100,
                                    ],
                                )
                            ),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="left",
                                x=0,
                            ),
                        )

                        st.plotly_chart(
                            fig_radar,
                            width="stretch",
                            config={
                                "displaylogo": False,
                                "responsive": True,
                            },
                        )

                        st.caption(
                            "Scores are normalized within the selected "
                            "peer set. Debt/Equity is inverted so that "
                            "lower leverage produces a higher relative score."
                        )

                    else:

                        st.info(
                            "Not enough comparable financial-strength "
                            "metrics are available."
                        )

                # ====================================================
                # VIEW 5 ? RETURNS & RISK MATRIX
                # ====================================================

                elif peer_view == "Returns & Risk Matrix":

                    st.markdown("##### Returns & Risk Matrix")

                    matrix_metrics = [
                        "1M Return",
                        "3M Return",
                        "6M Return",
                        "1Y Return",
                        "Volatility",
                        "Max Drawdown",
                        "Sharpe",
                        "Sortino",
                    ]

                    available_matrix = [
                        metric
                        for metric in matrix_metrics
                        if metric in visual_df.columns
                    ]

                    if available_matrix:

                        matrix = visual_df[
                            available_matrix
                        ].copy()

                        for metric in available_matrix:

                            if (
                                metric
                                not in [
                                    "Sharpe",
                                    "Sortino",
                                ]
                                and matrix[
                                    metric
                                ].abs().median() <= 2
                            ):
                                matrix[
                                    metric
                                ] *= 100

                        normalized = pd.DataFrame(
                            index=matrix.index
                        )

                        for metric in available_matrix:

                            values = matrix[metric]

                            minimum = values.min()
                            maximum = values.max()

                            if (
                                pd.isna(minimum)
                                or pd.isna(maximum)
                                or maximum == minimum
                            ):
                                normalized[metric] = 50.0
                            else:
                                normalized[metric] = (
                                    values - minimum
                                ) / (
                                    maximum - minimum
                                ) * 100

                        # Lower risk is treated as stronger relative
                        # positioning for the visual score.
                        for metric in [
                            "Volatility",
                            "Max Drawdown",
                        ]:
                            if metric in normalized.columns:
                                normalized[metric] = (
                                    100
                                    - normalized[metric]
                                )

                        company_labels = (
                            visual_df[
                                "Company"
                            ].astype(str).tolist()
                        )

                        # Exact values shown on hover.
                        custom_values = matrix.copy()

                        for column in custom_values.columns:
                            custom_values[column] = (
                                pd.to_numeric(
                                    custom_values[column],
                                    errors="coerce",
                                )
                            )

                        fig_heatmap = go.Figure(
                            data=go.Heatmap(
                                z=normalized.values,
                                x=available_matrix,
                                y=company_labels,
                                zmin=0,
                                zmax=100,
                                customdata=custom_values.values,
                                hovertemplate=(
                                    "<b>%{y}</b>"
                                    "<br>Metric: %{x}"
                                    "<br>Actual value: %{customdata:.2f}"
                                    "<br>Relative score: %{z:.1f}/100"
                                    "<extra></extra>"
                                ),
                                colorbar=dict(
                                    title="Relative<br>score"
                                ),
                            )
                        )

                        fig_heatmap.update_layout(
                            height=max(
                                380,
                                62 * len(company_labels),
                            ),
                            margin=dict(
                                l=20,
                                r=20,
                                t=40,
                                b=20,
                            ),
                            xaxis_title="Metric",
                            yaxis_title="Security",
                        )

                        st.plotly_chart(
                            fig_heatmap,
                            width="stretch",
                            config={
                                "displaylogo": False,
                                "responsive": True,
                            },
                        )

                        st.caption(
                            "Color shows relative positioning within the "
                            "selected peer set. Hover shows both the exact "
                            "metric value and the normalized visual score."
                        )

                    else:

                        st.info(
                            "Historical return and risk metrics are "
                            "not sufficiently available."
                        )

                # RELATIVE POSITIONING
                # --------------------------------------------

                if len(raw_df) >= 2:

                    st.markdown(
                        "#### Relative Positioning"
                    )

                    primary = raw_df.iloc[0]

                    peer_rows = raw_df.iloc[1:]

                    positioning_specs = [
                        ("P/E", "P/E"),
                        ("P/B", "P/B"),
                        ("EV/EBITDA", "EV/EBITDA"),
                        ("ROE", "ROE"),
                        ("Debt/Equity", "Debt/Equity"),
                        ("Revenue Growth", "Revenue Growth"),
                        ("Net Margin", "Net Margin"),
                        ("1Y Return", "1Y Return"),
                        ("Volatility", "Volatility"),
                        ("Max Drawdown", "Max Drawdown"),
                    ]

                    positioning_rows = []

                    for label, metric_key in positioning_specs:

                        primary_value = _peer_float(
                            primary.get(metric_key)
                        )

                        peer_values = [
                            _peer_float(value)
                            for value in peer_rows[
                                metric_key
                            ].tolist()
                        ]

                        peer_values = [
                            value
                            for value in peer_values
                            if value is not None
                        ]

                        if (
                            primary_value is None
                            or not peer_values
                        ):
                            continue

                        peer_average = float(
                            np.mean(peer_values)
                        )

                        positioning_rows.append({
                            "Metric": label,
                            "Primary": primary_value,
                            "Peer Average": peer_average,
                            "Difference": (
                                primary_value
                                - peer_average
                            ),
                        })

                    positioning_df = pd.DataFrame(
                        positioning_rows
                    )

                    if not positioning_df.empty:

                        render_terminal_table(
                            positioning_df,
                            empty_message=(
                                "No relative positioning data available."
                            )
                        )

                # --------------------------------------------
                # DETERMINISTIC COMPARATIVE SUMMARY
                # --------------------------------------------

                st.markdown(
                    "#### Comparative Analysis"
                )

                if len(raw_df) >= 2:

                    primary = raw_df.iloc[0]

                    peer_rows = raw_df.iloc[1:]

                    summary_items = []

                    for metric_key, label in [
                        ("ROE", "ROE"),
                        ("Revenue Growth", "Revenue growth"),
                        ("Net Margin", "Net margin"),
                        ("1Y Return", "1Y return"),
                        ("Volatility", "Volatility"),
                    ]:

                        primary_value = _peer_float(
                            primary.get(metric_key)
                        )

                        peer_values = [
                            _peer_float(value)
                            for value in peer_rows[
                                metric_key
                            ].tolist()
                        ]

                        peer_values = [
                            value
                            for value in peer_values
                            if value is not None
                        ]

                        if (
                            primary_value is None
                            or not peer_values
                        ):
                            continue

                        peer_average = float(
                            np.mean(peer_values)
                        )

                        if primary_value > peer_average:

                            direction = "above"

                        elif primary_value < peer_average:

                            direction = "below"

                        else:

                            direction = "in line with"

                        summary_items.append(
                            f"**{label}:** "
                            f"{_peer_percent(primary_value)} "
                            f"vs peer average "
                            f"{_peer_percent(peer_average)} "
                            f"({direction})."
                        )

                    if summary_items:

                        for item in summary_items:

                            st.markdown(
                                item
                            )

                    else:

                        st.caption(
                            "Not enough comparable data was available for a deterministic summary."
                        )

                else:

                    st.caption(
                        "Select at least one peer to generate relative analysis."
                    )

                # --------------------------------------------
                # GEMINI INTERPRETATION
                # --------------------------------------------

                ai_context = []

                for _, record in raw_df.iterrows():

                    ai_context.append({

                        "company": record["Company"],
                        "ticker": record["Ticker"],
                        "asset_class": record["Asset Class"],
                        "currency": record["Currency"],
                        "price": record["Price"],
                        "market_cap": record["Market Cap"],
                        "pe": record["P/E"],
                        "pb": record["P/B"],
                        "ev_ebitda": record["EV/EBITDA"],
                        "roe": record["ROE"],
                        "roa": record["ROA"],
                        "debt_equity": record["Debt/Equity"],
                        "revenue_growth": record["Revenue Growth"],
                        "earnings_growth": record["Earnings Growth"],
                        "net_margin": record["Net Margin"],
                        "operating_margin": record["Operating Margin"],
                        "dividend_yield": record["Dividend Yield"],
                        "beta": record["Beta"],
                        "one_year_return": record["1Y Return"],
                        "cagr": record["CAGR"],
                        "volatility": record["Volatility"],
                        "max_drawdown": record["Max Drawdown"],
                        "sharpe": record["Sharpe"],
                        "sortino": record["Sortino"],
                    })

                try:

                    ai_text = (
                        "Interpret this peer comparison using ONLY "
                        "the supplied verified data. "
                        "Do not invent missing values. "
                        "Do not use external or live web information. "
                        "Do not provide a buy/sell recommendation. "
                        "The first security is the primary security. "
                        "All following securities were manually selected "
                        "by the user. "
                        "Discuss valuation, profitability, growth, "
                        "risk and historical performance where data "
                        "is available. "
                        "Clearly distinguish observed data from "
                        "interpretation.\n\n"
                        + str(ai_context)
                    )

                    ai_result = generate_genai_analysis(
                        "Peer Comparison Interpretation",
                        ai_text
                    )

                    if ai_result:

                        st.markdown(
                            ai_result
                        )

                except Exception as exc:

                    st.caption(
                        f"AI interpretation unavailable: {exc}"
                    )

                st.caption(
                    "Peer comparison uses only manually selected securities and available Yahoo Finance data. Historical risk metrics are deterministic calculations using a zero risk-free-rate proxy."
                )



elif module == "Market Data":

    render_apex_page_header(
        "Market Data",
        "Index overview, market explorer and historical price context",
        "MARKET DATA",
        "Yahoo Finance"
    )

    st.markdown("#### Indices Overview")
    idx_rows = []

    for label, symbol in INDICES.items():

        hist = get_history(symbol, "1y", "1d")

        if not hist.empty and "Close" in hist.columns:

            close = hist["Close"].dropna()

            if len(close) >= 2:

                last = float(close.iloc[-1])
                prev = float(close.iloc[-2])

                # Daily percentage change
                chg_pct = (
                    ((last / prev) - 1) * 100
                    if prev != 0
                    else None
                )

                # YTD percentage change
                current_year = close.index[-1].year
                ytd_prices = close[
                    close.index.year == current_year
                ]

                if len(ytd_prices) >= 1:

                    ytd_base = float(ytd_prices.iloc[0])

                    ytd = (
                        ((last / ytd_base) - 1) * 100
                        if ytd_base != 0
                        else None
                    )

                else:

                    ytd = None

                idx_rows.append({
                    "Index": label,
                    "Level": f"{last:,.2f}",
                    "Chg %": (
                        f"{chg_pct:+.2f}%"
                        if chg_pct is not None
                        else "N/A"
                    ),
                    "YTD": (
                        f"{ytd:+.2f}%"
                        if ytd is not None
                        else "N/A"
                    )
                })

            else:

                idx_rows.append({
                    "Index": label,
                    "Level": "N/A",
                    "Chg %": "N/A",
                    "YTD": "N/A"
                })

        else:

            idx_rows.append({
                "Index": label,
                "Level": "N/A",
                "Chg %": "N/A",
                "YTD": "N/A"
            })

    render_terminal_table(pd.DataFrame(idx_rows), empty_message="No index data available.")

    st.divider()

    st.markdown("#### Security Historical Explorer")

    ticker = security_dropdown(
        "Select Security",
        key="security_selector_4"
    )

    period_label = st.selectbox(
        "Historical Period",
        list(TIMEFRAMES.keys()),
        index=5
    )

    if st.button("Load Market Data", type="primary"):

        remember_ticker(ticker)

        if period_label in {"5M", "15M", "30M", "1H"}:
            minutes = {
                "5M": 5,
                "15M": 15,
                "30M": 30,
                "1H": 60,
            }[period_label]

            data = get_intraday_history(
                ticker,
                period="1d",
                interval="1m"
            )

            if not data.empty:
                data = data.tail(minutes)

        else:
            period, interval = TIMEFRAMES[period_label]

            data = get_history(
                ticker,
                period,
                interval
            )

        if data.empty:

            st.error(
                "No market data found for this period."
            )

        else:

            st.success(
                f"Market data loaded for "
                f"{display_ticker(ticker)}"
            )

            st.plotly_chart(
                create_price_chart(
                    data,
                    display_ticker(ticker),
                    show_volume=True
                ),
                width="stretch"
            )

            st.markdown("#### Latest Data")

            render_terminal_table(data.tail(20))

            st.download_button(
                "Download (CSV)",
                data.to_csv().encode("utf-8"),
                file_name=(
                    f"{display_ticker(ticker)}_"
                    f"{period_label}.csv"
                )
            )


# ============================================================
# TECHNICAL ANALYSIS
# ============================================================

elif module == "Technical Analysis":
    render_apex_page_header(
        "Technical Analysis",
        "Deterministic price, trend, momentum and volatility analysis",
        "ANALYTICS",
        datetime.now(IST).strftime("%a %d %b %Y • %H:%M IST")
    )

    ticker = security_dropdown(
        "Select Security",
        key="security_selector_5"
    )

    tf_label = st.selectbox(
        "Analysis Period",
        list(TIMEFRAMES.keys()),
        index=list(TIMEFRAMES.keys()).index("1Y"),
        key="ta_timeframe"
    )

    st.caption("Select a security and period, then run analysis. All values are calculated from Yahoo Finance history; signals are descriptive, not forecasts.")

    if st.button("Run Analysis", type="primary", key="run_ta_analysis"):
        if not ticker:
            st.warning("Select a security before running analysis.")
        else:
            remember_ticker(ticker)
            period, interval = TIMEFRAMES[tf_label]
            with st.spinner("Retrieving historical price data…"):
                history = get_history(ticker, period, interval)

            security_metadata = UNIVERSE_BY_TICKER.get(ticker, {})
            asset_class = str(security_metadata.get("asset_class", "UNKNOWN")).upper()
            currency = security_metadata.get("currency", "")
            render_technical_analysis_results(
                history,
                display_ticker(ticker),
                asset_class,
                interval,
                currency,
                tf_label,
            )

# ============================================================
# PORTFOLIO
# ============================================================

elif module == "Portfolio":

    render_apex_page_header(
        "Portfolio Analysis",
        "Quantitative holdings review, allocation and market-value workstation",
        "PORTFOLIO",
        datetime.now(IST).strftime("%a %d %b %Y • %H:%M IST")
    )

    with st.container(key="portfolio-analysis-page"):
        st.markdown(
            """
            <div class='portfolio-section-heading'>
                <div>
                    <div class='portfolio-kicker'>PORTFOLIO CONTROL CENTER</div>
                    <div class='portfolio-section-title'>Holdings and position sizing</div>
                </div>
                <div class='portfolio-section-meta'>YAHOO FINANCE / DELAYED</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='portfolio-helper-text'>Enter security and quantity. "
        "Current market values are calculated from the retrieved closing data.</div>",
        unsafe_allow_html=True,
    )

    rows = st.session_state["portfolio_rows"]

    for i, row in enumerate(rows):

        c1, c2, c3 = st.columns([2, 1, 0.4])

        with c1:
            selected_pf_ticker = security_dropdown(
                label=f"Company {i + 1}",
                key=f"pf_ticker_dropdown_{i}",
            )

            if selected_pf_ticker:
                row["ticker"] = selected_pf_ticker

        with c2:
            row["qty"] = st.number_input(
                f"Qty {i + 1}",
                min_value=0.0,
                value=float(row.get("qty", 0)),
                key=f"pf_qty_{i}",
            )

        with c3:
            st.write("")

            if st.button(
                "x",
                key=f"pf_remove_{i}",
            ):
                st.session_state["portfolio_rows"].pop(i)
                st.rerun()

    if st.button("+ ADD HOLDING"):
        st.session_state["portfolio_rows"].append(
            {
                "ticker": "",
                "qty": 0,
            }
        )
        st.rerun()

    st.markdown(
        """
        <div class='portfolio-section-heading portfolio-review-heading'>
            <div>
                <div class='portfolio-kicker'>PORTFOLIO REVIEW</div>
                <div class='portfolio-section-title'>Market value and allocation</div>
            </div>
            <div class='portfolio-section-meta'>CALCULATED FROM CURRENT HOLDINGS</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("ANALYZE PORTFOLIO", type="primary"):

        holdings = [
            r for r in rows
            if r.get("ticker", "").strip()
            and r.get("qty", 0) > 0
        ]

        if not holdings:

            st.warning(
                "Add at least one holding with a quantity greater than zero."
            )

        else:

            hold_rows = []
            price_series = {}

            for h in holdings:

                t = normalize_ticker(h["ticker"])
                hist = get_history(t, "1y", "1d")

                if hist.empty:
                    st.warning(
                        f"No data found for {h['ticker']}  skipping."
                    )
                    continue

                current_price = hist["Close"].iloc[-1]

                price_series[t] = hist["Close"]

                market_value = current_price * h["qty"]

                hold_rows.append(
                    {
                        "Ticker": display_ticker(t),
                        "Qty": h["qty"],
                        "Current Price": current_price,
                        "Market Value": market_value,
                    }
                )

            if not hold_rows:

                st.error(
                    "None of the entered holdings returned usable data."
                )

            else:

                pf_df = pd.DataFrame(hold_rows)

                total_mv = pf_df["Market Value"].sum()

                if total_mv:
                    pf_df["Weight %"] = (
                        pf_df["Market Value"]
                        / total_mv
                        * 100
                    )
                else:
                    pf_df["Weight %"] = 0.0

                st.markdown(
                    "<div class='portfolio-subsection-label'>POSITION SUMMARY</div>",
                    unsafe_allow_html=True,
                )

                # ------------------------------------------------
                # SUMMARY
                # ------------------------------------------------

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Portfolio Value",
                    format_inr_scale(total_mv),
                )

                c2.metric(
                    "Holdings",
                    len(pf_df),
                )

                top_holding = pf_df.loc[
                    pf_df["Market Value"].idxmax()
                ]

                c3.metric(
                    "Top Holding",
                    top_holding["Ticker"],
                    format_inr_scale(
                        top_holding["Market Value"]
                    ),
                )

                st.markdown(
                    "<div class='portfolio-subsection-label'>HOLDINGS LEDGER</div>",
                    unsafe_allow_html=True,
                )

                # ------------------------------------------------
                # DISPLAY TABLE
                # ------------------------------------------------

                display_pf = pf_df.copy()

                display_pf["Current Price"] = (
                    display_pf["Current Price"]
                    .apply(lambda v: f"INR {v:,.2f}")
                )

                display_pf["Market Value"] = (
                    display_pf["Market Value"]
                    .apply(lambda v: f"INR {v:,.2f}")
                )

                display_pf["Weight %"] = (
                    display_pf["Weight %"]
                    .apply(lambda v: f"{v:.2f}%")
                )

                render_terminal_table(display_pf, empty_message="No portfolio data available.")

                st.download_button(
                    "Download portfolio (CSV)",
                    pf_df.to_csv(index=False).encode("utf-8"),
                    file_name="portfolio.csv",
                )

                st.markdown(
                    "<div class='portfolio-subsection-label'>ALLOCATION MONITOR</div>",
                    unsafe_allow_html=True,
                )

                # ------------------------------------------------
                # CHARTS
                # ------------------------------------------------

                pc1, pc2 = st.columns(2)

                with pc1:
                    st.plotly_chart(
                        create_allocation_pie(
                            pf_df["Ticker"],
                            pf_df["Market Value"],
                        ),
                        width="stretch",
                    )

                with pc2:
                    st.plotly_chart(
                        create_bar_comparison(
                            pf_df["Ticker"].tolist(),
                            {
                                "Market Value":
                                pf_df["Market Value"].tolist()
                            },
                            "Market Value by Holding",
                        ),
                        width="stretch",
                    )

elif module == "Risk Analysis":

    render_apex_page_header(
        "Risk Analysis",
        "Volatility, drawdown, beta and portfolio risk measurement",
        "RISK",
        "Yahoo Finance"
    )

    ticker = security_dropdown(
        "Select Security",
        key="security_selector_6"
    )

    selected_risk_record = UNIVERSE_BY_TICKER.get(ticker, {})
    selected_risk_class = normalize_asset_class(selected_risk_record.get("asset_class"))
    if supports_metric(selected_risk_class, "Beta", "risk_metrics"):
        benchmark_label = st.selectbox("Benchmark", list(BENCHMARKS.keys()))
    else:
        benchmark_label = None
        st.caption("Benchmark beta is NOT APPLICABLE for this asset class.")
    lookback_label = st.selectbox("Lookback Period", ["1Y", "2Y", "5Y"], index=0)

    if st.button("Calculate Risk Metrics", type="primary"):
        remember_ticker(ticker)
        period, interval = TIMEFRAMES[lookback_label]
        data = get_history(ticker, period, interval)
        record = UNIVERSE_BY_TICKER.get(ticker, {})
        asset_class = normalize_asset_class(record.get("asset_class"))
        currency = str(record.get("currency", "") or "").strip().upper()
        capability = get_asset_capabilities(asset_class)

        if data.empty or "Close" not in data.columns:
            st.warning("DATA NOT AVAILABLE: Yahoo Finance returned no usable price history for this security.")
        else:
            close = pd.to_numeric(data["Close"], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            returns = close.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
            periods_per_year = annualization_periods(asset_class, interval)
            insufficient_history = len(returns) < 2

            if len(close) < 3:
                st.warning("INSUFFICIENT HISTORY: at least three valid closing prices are required for risk analysis.")
                returns = pd.Series(dtype=float)
                insufficient_history = True

            volatility = (
                returns.std(ddof=1) * np.sqrt(periods_per_year)
                if len(returns) >= 2 and periods_per_year is not None
                else None
            )
            max_dd, dd_series = calculate_max_drawdown(close) if len(close) >= 2 else (None, pd.Series(dtype=float))
            var_95 = calculate_var_history(returns, 0.95) if len(returns) >= 2 else None
            var_99 = calculate_var_history(returns, 0.99) if len(returns) >= 2 else None

            risk_free_annual = 0.065 if asset_class == "EQUITY" and currency == "INR" else None
            sharpe = calculate_sharpe(returns, risk_free_annual, periods_per_year)
            sortino = calculate_sortino(returns, risk_free_annual, periods_per_year)

            beta = None
            correlation = None
            benchmark_ticker = BENCHMARKS.get(benchmark_label) if benchmark_label else None
            benchmark_record = UNIVERSE_BY_TICKER.get(benchmark_ticker, {})
            benchmark_currency = str(benchmark_record.get("currency", "") or "").strip().upper()
            if (
                benchmark_ticker
                and
                supports_metric(asset_class, "Beta", "risk_metrics")
                and currency
                and currency == benchmark_currency
            ):
                benchmark_data = get_history(benchmark_ticker, period, interval)
                if not benchmark_data.empty and "Close" in benchmark_data.columns:
                    benchmark_close = pd.to_numeric(benchmark_data["Close"], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
                    bm_returns = benchmark_close.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
                    beta = calculate_beta(returns, bm_returns)
                    combined = pd.concat([returns, bm_returns], axis=1).dropna()
                    if len(combined) > 5:
                        correlation = combined.iloc[:, 0].corr(combined.iloc[:, 1])

            downside = returns[returns < 0]
            downside_dev = (
                downside.std(ddof=1) * np.sqrt(periods_per_year)
                if len(downside) > 1 and periods_per_year is not None
                else None
            )
            rolling_volatility = (
                returns.rolling(20, min_periods=20).std(ddof=1) * np.sqrt(periods_per_year) * 100
                if periods_per_year is not None
                else pd.Series(dtype=float)
            )

            def risk_value(metric, value, suffix="", category="risk_metrics"):
                state = metric_state(
                    asset_class,
                    metric,
                    value,
                    insufficient_history=insufficient_history and value is None,
                    category=category,
                )
                if state != "AVAILABLE":
                    return state
                return f"{float(value) * 100:.2f}{suffix}" if suffix == "%" else f"{float(value):.2f}{suffix}"

            volatility_metric = "Price Volatility" if asset_class in {"FIXED_INCOME", "COMMODITY"} else "Volatility"
            beta_value = risk_value("Beta", beta, category="risk_metrics")
            if asset_class == "EQUITY" and currency and currency != benchmark_currency:
                beta_value = "DATA NOT AVAILABLE"

            risk_columns = st.columns(4)
            risk_columns[0].metric("Annualized Price Volatility", risk_value(volatility_metric, volatility, "%"))
            beta_label = f"Beta vs {benchmark_label}" if benchmark_label else "Beta"
            risk_columns[1].metric(beta_label, beta_value)
            risk_columns[2].metric("Sharpe Ratio", risk_value("Sharpe", sharpe))
            risk_columns[3].metric("Sortino Ratio", risk_value("Sortino", sortino))

            risk_columns = st.columns(4)
            risk_columns[0].metric("Maximum Drawdown", risk_value("Maximum Drawdown", max_dd, "%"))
            risk_columns[1].metric("1-Day VaR (95%)", risk_value("Value at Risk", var_95, "%"))
            risk_columns[2].metric("1-Day VaR (99%)", risk_value("Value at Risk", var_99, "%"))
            correlation_state = metric_state(
                asset_class,
                "Beta",
                correlation,
                insufficient_history=insufficient_history and correlation is None,
                category="risk_metrics",
            )
            if asset_class != "EQUITY":
                correlation_state = "NOT APPLICABLE"
            correlation_value = f"{correlation:.2f}" if correlation is not None and correlation_state == "AVAILABLE" else correlation_state
            risk_columns[3].metric("Correlation vs Benchmark", correlation_value)

            if supports_metric(asset_class, "Downside Risk", "risk_metrics"):
                st.metric("Downside Deviation (annualized)", risk_value("Downside Risk", downside_dev, "%"))

            st.caption(
                f"{asset_class} · {currency or 'DATA NOT AVAILABLE'} · {periods_per_year or 'DATA NOT AVAILABLE'} observations/year. "
                f"{capability['notes']} "
                + ("Sharpe/Sortino use a 6.5% annual Indian G-Sec proxy only for INR equities." if risk_free_annual is not None else "No currency-matched risk-free series is available; Sharpe/Sortino are DATA NOT AVAILABLE.")
            )

            if supports_metric(asset_class, "Rolling Volatility", "risk_metrics") and rolling_volatility.notna().any():
                st.markdown("#### Rolling Volatility")
                volatility_chart = go.Figure()
                volatility_chart.add_trace(go.Scatter(
                    x=rolling_volatility.index,
                    y=rolling_volatility,
                    mode="lines",
                    name="20-observation annualized volatility",
                    line={"color": "#8ba5b5", "width": 1.5},
                ))
                volatility_chart.update_layout(
                    template="plotly_dark",
                    height=320,
                    yaxis_title="Annualized volatility (%)",
                    xaxis_title="Date",
                    margin={"l": 48, "r": 16, "t": 28, "b": 30},
                )
                st.plotly_chart(volatility_chart, width="stretch", config={"responsive": True, "displaylogo": False})
            elif supports_metric(asset_class, "Rolling Volatility", "risk_metrics"):
                st.info("INSUFFICIENT HISTORY: rolling volatility requires 20 return observations.")

            st.markdown("#### Drawdown Over Time")
            if not dd_series.empty:
                dd_chart = go.Figure()
                dd_chart.add_trace(go.Scatter(x=dd_series.index, y=dd_series.values * 100, mode="lines",
                                               fill="tozeroy", line=dict(color="#8b7777", width=1.5),
                                               name="Price drawdown"))
                dd_chart.update_layout(template="plotly_dark", height=350, yaxis_title="Drawdown (%)",
                                        margin=dict(l=20, r=20, t=30, b=20),
                                        xaxis_title="Date")
                st.plotly_chart(dd_chart, width="stretch", config={"responsive": True, "displaylogo": False})


# ============================================================
# AI RESEARCH
# ============================================================

elif module == "AI Research":

    render_apex_page_header(
        "AI Research",
        "Gemini-assisted market and valuation interpretation from live terminal data",
        "AI",
        "Gemini"
    )
    st.caption(
        "Ask follow-up questions naturally. Gemini will use the conversation "
        "and verified Yahoo Finance data to answer."
    )

    # ========================================================
    # AI CHAT SESSION STATE
    # ========================================================

    if "ai_chat_messages" not in st.session_state:
        st.session_state["ai_chat_messages"] = []

    # ========================================================
    # CHAT HEADER
    # ========================================================

    chat_col1, chat_col2 = st.columns([5, 1])

    with chat_col1:
        st.markdown("### Research Chat")

    with chat_col2:
        if st.button(
            "+ New Chat",
            key="ai_new_chat",
            width="stretch"
        ):
            st.session_state["ai_chat_messages"] = []
            st.rerun()

    # ========================================================
    # DISPLAY PREVIOUS CHAT
    # ========================================================

    for message in st.session_state["ai_chat_messages"]:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ========================================================
    # CHAT INPUT
    # ========================================================

    question = st.chat_input(
        "Ask anything about financial markets, companies, valuation, risk, or investing..."
    )

    if question:

        # ----------------------------------------------------
        # DISPLAY USER QUESTION
        # ----------------------------------------------------

        st.session_state["ai_chat_messages"].append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):
            st.markdown(question)
        # ----------------------------------------------------
        # BUILD CONVERSATION CONTEXT
        # ----------------------------------------------------

        conversation_context = ""

        previous_messages = st.session_state["ai_chat_messages"][:-1]

        if previous_messages:
            conversation_context = "\n\nPREVIOUS CONVERSATION:\n"

            for msg in previous_messages:
                role = "USER" if msg["role"] == "user" else "ASSISTANT"

                conversation_context += (
                    f"{role}: {msg['content']}\n\n"
                )


        # ----------------------------------------------------
        # BUILD GENERAL FINANCIAL RESEARCH PROMPT
        # ----------------------------------------------------

        full_question = f"""
You are an intelligent financial research assistant having a
continuous conversation with the user.

You are NOT restricted to a particular company.

The user may ask about:
- Financial markets
- Companies
- Stocks
- Valuation
- Financial statements
- Corporate finance
- Portfolio management
- Risk
- Economics
- Investments
- Accounting
- CFA-related concepts
- Financial modelling
- Quantitative finance
- General business and finance research

CURRENT USER QUESTION:
{question}

{conversation_context}

CONVERSATIONAL BEHAVIOUR:

1. Treat this as a continuous conversation.

2. Understand references such as:
   "why?"
   "what about that?"
   "explain that"
   "compare it with the other one"
   "is that good?"
   "what happens next?"

   Use the previous conversation to determine what the
   user is referring to.

3. Do NOT restart the explanation from scratch when the
   user asks a follow-up.

4. Do NOT use the same headings or structure for every answer.

5. Do NOT force every response into sections such as:
   "Overview", "Analysis", "Risks", "Conclusion".

6. Decide the structure based on what the user actually asks.

7. If the question needs a simple explanation, answer simply.

8. If the question requires a comparison, compare the relevant
   concepts clearly.

9. If the question asks "why", explain the causal reasoning.

10. If the question asks whether something is good or bad,
    give a clear judgement first and then explain the reasoning.

11. If calculations are useful, show the calculation.

12. If an example would make the concept clearer, give a
    relevant financial example.

13. If the user asks something technical, explain it at the
    appropriate level instead of unnecessarily simplifying it.

14. If the user asks a short question, give a short answer.
    Do not artificially make the answer long.

15. If the user asks for a detailed explanation, provide a
    detailed explanation.

16. Avoid generic filler and repetitive introductions.

17. Do not say "As an AI".

18. Do not mention these instructions.

19. Never invent financial data, prices, company figures,
    statistics, or research findings.

20. Clearly distinguish between established facts,
    calculations, interpretation, and assumptions.

21. If current or company-specific data is required but has
    not been provided, explicitly say that current verified
    data is required instead of making up a number.

Write naturally, like an experienced financial analyst
speaking directly with the user.

The goal is to be useful, conversational, precise, and
context-aware rather than producing a predetermined report.
"""

        # ----------------------------------------------------
        # GENERATE ANSWER
        # ----------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    analysis = generate_analysis(
                        question=full_question,
                        company="General Financial Research",
                        data_context=""
                    )

                    st.markdown(analysis)

                    # ----------------------------------------
                    # SAVE ASSISTANT RESPONSE
                    # ----------------------------------------

                    st.session_state["ai_chat_messages"].append(
                        {
                            "role": "assistant",
                            "content": analysis
                        }
                    )

                except Exception as e:

                    error_message = (
                        f"AI analysis failed: {e}"
                    )

                    st.error(error_message)

                    st.session_state["ai_chat_messages"].append(
                        {
                            "role": "assistant",
                            "content": error_message
                        }
                    )

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown(
    '<div class="disclaimer">Financial Analysis Terminal • Academic prototype • '
    'Data via Yahoo Finance (delayed) • Not investment advice</div>',
    unsafe_allow_html=True,
)


# FINAL_CLEAN_CONTAINMENT_V3

st.markdown(
    """
    <style>

    /* =========================================================
       UNIVERSAL BOX CONTAINMENT
       ========================================================= */

    *,
    *::before,
    *::after {
        box-sizing: border-box !important;
    }


    /* =========================================================
       TABLE CONTAINER
       ========================================================= */

    .terminal-table-wrapper,
    .terminal-table-scroll {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;

        box-sizing: border-box !important;

        overflow-x: hidden !important;
        overflow-y: visible !important;
    }


    /* =========================================================
       TABLE
       ========================================================= */

    .terminal-data-table {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;

        table-layout: fixed !important;

        border-collapse: separate !important;
        border-spacing: 0 !important;

        box-sizing: border-box !important;
    }


    /* =========================================================
       TABLE CELLS
       ========================================================= */

    .terminal-data-table th,
    .terminal-data-table td {

        box-sizing: border-box !important;

        min-width: 0 !important;
        max-width: 100% !important;

        height: auto !important;
        max-height: none !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;
        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: hidden !important;

        vertical-align: top !important;

        line-height: 1.4 !important;
    }


    .terminal-data-table th *,
    .terminal-data-table td * {

        box-sizing: border-box !important;

        min-width: 0 !important;
        max-width: 100% !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;
        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: hidden !important;
    }


    /* =========================================================
       FINANCIAL STATEMENTS
       ========================================================= */

    .terminal-financial-statements,
    .terminal-financial-statements * {

        box-sizing: border-box !important;

        min-width: 0 !important;
        max-width: 100% !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;
        word-break: break-word !important;

        text-overflow: clip !important;

        height: auto !important;
        max-height: none !important;
    }

    .terminal-financial-statements .terminal-data-table {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;

        table-layout: fixed !important;
    }


    /* =========================================================
       CUSTOM CARDS / PANELS / BOXES
       ========================================================= */

    [class*="-card"],
    [class*="-panel"],
    [class*="-box"],
    [class*="-tile"],
    [class*="-item"] {

        box-sizing: border-box !important;

        min-width: 0 !important;
        max-width: 100% !important;

        height: auto !important;
        max-height: none !important;

        overflow: hidden !important;
    }


    /* =========================================================
       TEXT INSIDE CUSTOM CONTAINERS
       ========================================================= */

    [class*="-card"] *,
    [class*="-panel"] *,
    [class*="-box"] *,
    [class*="-tile"] *,
    [class*="-item"] * {

        box-sizing: border-box !important;

        min-width: 0 !important;
        max-width: 100% !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;
        word-break: break-word !important;

        text-overflow: clip !important;

        height: auto !important;
        max-height: none !important;

        overflow: hidden !important;
    }


    /* =========================================================
       TITLES / LABELS / VALUES / DESCRIPTIONS
       ========================================================= */

    [class*="-title"],
    [class*="-label"],
    [class*="-value"],
    [class*="-meta"],
    [class*="-heading"],
    [class*="-description"],
    [class*="-analysis"],
    [class*="-note"] {

        min-width: 0 !important;
        max-width: 100% !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;
        word-break: break-word !important;

        text-overflow: clip !important;

        height: auto !important;
        max-height: none !important;

        overflow: hidden !important;
    }


    /* =========================================================
       DASHBOARD INDEX CARDS IN MAIN APP
       ========================================================= */

    .dashboard-index-card {

        box-sizing: border-box !important;

        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;

        height: auto !important;
        max-height: none !important;

        overflow: hidden !important;
    }

    .dashboard-index-card * {

        min-width: 0 !important;
        max-width: 100% !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;
        word-break: break-word !important;

        text-overflow: clip !important;

        overflow: hidden !important;
    }


    /* =========================================================
       STREAMLIT METRICS
       ========================================================= */

    [data-testid="stMetric"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {

        min-width: 0 !important;
        max-width: 100% !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;
        word-break: break-word !important;

        text-overflow: clip !important;

        height: auto !important;
        max-height: none !important;

        overflow: hidden !important;
    }


    /* =========================================================
       MARKDOWN / ALERTS / CAPTIONS
       ========================================================= */

    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] *,
    [data-testid="stAlert"],
    [data-testid="stAlert"] *,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {

        min-width: 0 !important;
        max-width: 100% !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;
        word-break: break-word !important;

        text-overflow: clip !important;
    }


    /* =========================================================
       LONG LINKS / IDENTIFIERS
       ========================================================= */

    a,
    code,
    pre {

        max-width: 100% !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;
        word-break: break-word !important;

        text-overflow: clip !important;
    }


    /* =========================================================
       STREAMLIT COLUMNS
       ========================================================= */

    [data-testid="column"] {

        min-width: 0 !important;
        max-width: 100% !important;

        box-sizing: border-box !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# END_FINAL_CLEAN_CONTAINMENT_V3

