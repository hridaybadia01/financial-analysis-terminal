from pathlib import Path
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import numpy as np
import yfinance as yf

from asset_capabilities import (
    direct_provider_metrics,
    get_asset_capabilities,
    normalize_asset_class,
    return_observation_periods,
)
from universe import load_universe
from technical_analysis import calculate_technical_analysis


BASE_DIR = Path(__file__).resolve().parents[1]


def _float(value):
    try:
        value = float(value)
        return value if np.isfinite(value) else None
    except Exception:
        return None


def _context_value(value):
    if value is None:
        return "DATA NOT AVAILABLE"
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        return "DATA NOT AVAILABLE"
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, str) and value.strip().lower() in {"none", "nan", "inf", "-inf"}:
        return "DATA NOT AVAILABLE"
    try:
        if pd.isna(value):
            return "DATA NOT AVAILABLE"
    except (TypeError, ValueError):
        pass
    return value


@lru_cache(maxsize=1)
def _universe():
    df = load_universe().copy()

    for col in [
        "ticker",
        "name",
        "asset_class",
        "region",
        "country",
        "instrument_type",
    ]:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df


# ============================================================
# MASTER UNIVERSE
# ============================================================

def get_universe_overview() -> dict:
    """Returns the complete master-universe structure and counts used by the Financial Analysis Terminal."""

    df = _universe()

    return {
        "source": "yahoo_global_universe.csv",
        "total_securities": int(len(df)),
        "asset_classes": df["asset_class"].map(normalize_asset_class).value_counts().to_dict(),
        "regions": df["region"].value_counts().to_dict(),
        "countries": df["country"].value_counts().to_dict(),
        "asset_class_capabilities": {
            asset_class: get_asset_capabilities(asset_class)
            for asset_class in ("EQUITY", "FIXED_INCOME", "COMMODITY", "INDEX", "CRYPTO", "FX")
        },
        "columns": list(df.columns),
    }


def search_terminal_universe(
    query: str = "",
    asset_class: str = "",
    country: str = "",
    region: str = "",
    limit: int = 50,
) -> dict:
    """Searches the entire master security universe by name or ticker."""

    df = _universe().copy()

    if asset_class:
        canonical_filter = normalize_asset_class(asset_class)
        df = df[
            df["asset_class"].map(normalize_asset_class)
            == canonical_filter
        ]

    if country:
        df = df[
            df["country"].str.lower()
            == country.strip().lower()
        ]

    if region:
        df = df[
            df["region"].str.lower()
            == region.strip().lower()
        ]

    q = (query or "").strip().lower()

    if q:
        df = df[
            df["ticker"]
            .str.lower()
            .str.contains(q, regex=False)
            |
            df["name"]
            .str.lower()
            .str.contains(q, regex=False)
        ]

    limit = max(
        1,
        min(int(limit or 50), 200)
    )

    rows = df.head(limit)

    return {
        "source": "yahoo_global_universe.csv",
        "total_matching": int(len(df)),
        "returned": int(len(rows)),
        "securities": rows[
            [
                "ticker",
                "name",
                "asset_class",
                "region",
                "country",
                "instrument_type",
                "currency",
            ]
        ].to_dict("records"),
    }


# ============================================================
# YAHOO HISTORY
# ============================================================

@lru_cache(maxsize=2048)
def _history_snapshot(ticker: str):

    ticker = str(ticker).strip().upper()
    matches = _universe()
    security_rows = matches[matches["ticker"].str.upper() == ticker]
    asset_class = normalize_asset_class(
        security_rows.iloc[0]["asset_class"] if not security_rows.empty else ""
    )
    capabilities = get_asset_capabilities(asset_class)
    return_periods = return_observation_periods(asset_class)
    annualization_sessions = capabilities["annualization_sessions"]

    try:
        t = yf.Ticker(ticker)

        hist = t.history(
            period="1y",
            interval="1d",
            auto_adjust=False,
            timeout=10,
        )

        if hist is None or hist.empty:
            return None

        hist = hist.dropna(
            subset=["Close"]
        )

        if hist.empty:
            return None

        close = hist["Close"].astype(float)

        latest = float(close.iloc[-1])

        low_1y = float(close.min())

        high_1y = float(close.max())

        def ret(days):

            if days is None or len(close) <= days:
                return "DATA NOT AVAILABLE"

            base = float(close.iloc[-days - 1])

            if base == 0:
                return "DATA NOT AVAILABLE"

            return (
                (latest / base) - 1.0
            ) * 100.0

        daily_returns = (
            close
            .pct_change()
            .dropna()
        )

        volatility = None

        if len(daily_returns) > 1 and annualization_sessions is not None:
            volatility = float(
                daily_returns.std()
                * np.sqrt(annualization_sessions)
                * 100.0
            )

        analysis = calculate_technical_analysis(hist, asset_class, "1d")

        def snapshot_value(value, multiplier=1.0):
            if value is None:
                return "DATA NOT AVAILABLE"
            try:
                numeric = float(value) * multiplier
            except (TypeError, ValueError):
                return "DATA NOT AVAILABLE"
            return numeric if np.isfinite(numeric) else "DATA NOT AVAILABLE"

        macd_line, macd_signal, macd_histogram = analysis["macd_values"]
        sma_values = analysis["sma_values"]
        risk_metrics = {
            "daily_volatility_pct": snapshot_value(analysis["daily_volatility"], 100),
            "annualized_volatility_pct": snapshot_value(analysis["annualized_volatility"], 100),
            "rolling_volatility_regime": analysis["volatility_regime"],
            "maximum_drawdown_pct": snapshot_value(analysis["max_drawdown"], 100),
        }
        technical_metrics = {
            "sma_20": snapshot_value(sma_values.get(20)),
            "sma_50": snapshot_value(sma_values.get(50)),
            "sma_200": snapshot_value(sma_values.get(200)),
            "trend": analysis["trend"],
            "sma_50_200_cross": analysis["sma_cross"],
            "rsi_14": snapshot_value(analysis["rsi_value"]),
            "rsi_state": analysis["rsi_state"],
            "macd": snapshot_value(macd_line),
            "macd_signal": snapshot_value(macd_signal),
            "macd_histogram": snapshot_value(macd_histogram),
            "macd_cross": analysis["macd_cross"],
            "bollinger_upper": snapshot_value(analysis["bb_values"][0]),
            "bollinger_middle": snapshot_value(analysis["bb_values"][1]),
            "bollinger_lower": snapshot_value(analysis["bb_values"][2]),
            "bollinger_bandwidth_pct": snapshot_value(analysis["bb_bandwidth"]),
            "signal_score": snapshot_value(analysis["score"]),
            "signal": analysis["score_signal"],
            "score_components": [
                {
                    "rule": item["rule"],
                    "contribution": _context_value(item["contribution"]),
                    "evidence": item["evidence"],
                }
                for item in analysis["score_components"]
            ],
        }

        return {
            "current_price": latest,

            "52_week_low": low_1y,

            "52_week_high": high_1y,

            "distance_from_52_week_low_pct":
                (
                    (latest / low_1y) - 1.0
                ) * 100.0
                if low_1y
                else None,

            "distance_from_52_week_high_pct":
                (
                    (latest / high_1y) - 1.0
                ) * 100.0
                if high_1y
                else None,

            "asset_class": asset_class,

            "annualization_sessions": annualization_sessions,

            "return_1d_pct": ret(return_periods.get("1D")),

            "return_1w_pct": ret(return_periods.get("1W")),

            "return_1m_pct": ret(return_periods.get("1M")),

            "return_3m_pct": ret(return_periods.get("3M")),

            "return_6m_pct": ret(return_periods.get("6M")),

            "return_1y_pct": ret(return_periods.get("1Y")),

            "annualized_volatility_pct":
                snapshot_value(volatility),

            "risk_metrics": risk_metrics,

            "technical_metrics": technical_metrics,

            "historical_data": {
                "period": "1y",
                "interval": "1d",
                "observations": int(len(close)),
                "first_date": str(close.index[0].date()),
                "last_date": str(close.index[-1].date()),
            },

            "observations":
                int(len(close)),

            "first_date":
                str(close.index[0].date()),

            "last_date":
                str(close.index[-1].date()),
        }

    except Exception:
        return None


# ============================================================
# YAHOO FUNDAMENTALS
# ============================================================

@lru_cache(maxsize=2048)
def _market_info(ticker: str):

    ticker = str(ticker).strip().upper()

    t = yf.Ticker(ticker)

    result = {}

    try:

        fast_info = t.fast_info

        try:
            result["market_cap"] = _float(
                fast_info.get("market_cap")
            )

        except Exception:

            try:
                result["market_cap"] = _float(
                    fast_info["market_cap"]
                )

            except Exception:
                pass

    except Exception:
        pass

    try:

        info = t.info or {}

        if result.get("market_cap") is None:
            result["market_cap"] = _float(
                info.get("marketCap")
            )

        fields = [
            "trailingPE",
            "forwardPE",
            "priceToBook",
            "enterpriseValue",
            "enterpriseToEbitda",
            "beta",
            "dividendYield",
            "returnOnEquity",
            "returnOnAssets",
            "profitMargins",
            "operatingMargins",
            "revenueGrowth",
            "earningsGrowth",
            "yield",
            "yieldToMaturity",
            "yieldToWorst",
            "duration",
            "effectiveDuration",
            "modifiedDuration",
            "maturityDate",
            "maturity",
            "maturityDateTimestamp",
            "creditRating",
            "rating",
            "bondRating",
            "rateSensitivity",
            "interestRateSensitivity",
            "expireDate",
            "expiry",
            "expiration",
            "contractSize",
            "circulatingSupply",
            "volume24Hr",
        ]

        for field in fields:
            value = info.get(field)
            if field in {
                "maturityDate",
                "maturity",
                "creditRating",
                "rating",
                "bondRating",
                "expireDate",
                "expiry",
                "expiration",
            }:
                result[field] = str(value).strip() if value not in (None, "") else None
            else:
                result[field] = _float(value)

        result["longName"] = (
            info.get("longName")
            or info.get("shortName")
        )

        result["sector"] = info.get("sector")

        result["industry"] = info.get("industry")

        result["currency"] = info.get("currency")

    except Exception:
        pass

    return result


# ============================================================
# SECURITY SNAPSHOT
# ============================================================

def get_security_snapshot(ticker: str) -> dict:
    """Retrieves current and one-year Yahoo Finance market and fundamental data for a security in the master universe."""

    ticker = (
        ticker or ""
    ).strip().upper()

    if not ticker:
        return {
            "error": "Ticker is required."
        }

    df = _universe()

    match = df[
        df["ticker"].str.upper()
        == ticker
    ]

    if match.empty:
        return {
            "error":
                f"{ticker} is not present in yahoo_global_universe.csv."
        }

    record = {
        key: _context_value(value)
        for key, value in match.iloc[0].to_dict().items()
    }
    asset_class = normalize_asset_class(record.get("asset_class"))
    record["asset_class"] = asset_class
    currency = str(record.get("currency", "") or "").strip().upper()
    record["currency"] = currency or "DATA NOT AVAILABLE"
    capability = get_asset_capabilities(asset_class)

    provider_info = _market_info(ticker)
    provider_data = {key: _context_value(value) for key, value in provider_info.items()}

    if asset_class == "EQUITY":
        equity_fields = (
            "market_cap",
            "trailingPE",
            "forwardPE",
            "priceToBook",
            "dividendYield",
            "returnOnEquity",
            "returnOnAssets",
            "profitMargins",
            "revenueGrowth",
            "earningsGrowth",
        )
        equity_data_available = any(
            provider_data.get(field) != "DATA NOT AVAILABLE"
            for field in equity_fields
        )
        fundamentals = {
            "state": "AVAILABLE" if equity_data_available else "DATA NOT AVAILABLE",
            "applicable_metrics": list(capability["fundamental_metrics"]),
            "data": provider_data,
        }
    elif asset_class == "INDEX":
        index_values = direct_provider_metrics(asset_class, provider_info)
        fundamentals = {
            "state": "AVAILABLE" if any(value != "DATA NOT AVAILABLE" for value in index_values.values()) else "DATA NOT AVAILABLE",
            "applicable_metrics": list(capability["conditional_metrics"]),
            "corporate_metrics": "NOT APPLICABLE",
            "provider_reported_index_values": index_values or "DATA NOT AVAILABLE",
        }
    elif asset_class == "CRYPTO":
        market_cap = provider_info.get("market_cap")
        fundamentals = {
            "state": "AVAILABLE" if market_cap is not None else "DATA NOT AVAILABLE",
            "applicable_metrics": list(capability["conditional_metrics"]),
            "market_cap": market_cap if market_cap is not None else "DATA NOT AVAILABLE",
            "corporate_metrics": "NOT APPLICABLE",
        }
    elif asset_class == "FIXED_INCOME":
        direct_metrics = direct_provider_metrics(asset_class, provider_info)
        fundamentals = {
            "state": "AVAILABLE" if any(value != "DATA NOT AVAILABLE" for value in direct_metrics.values()) else "DATA NOT AVAILABLE",
            "corporate_metrics": "NOT APPLICABLE",
            "direct_instrument_fields": direct_metrics,
        }
    else:
        direct_metrics = direct_provider_metrics(asset_class, provider_info)
        fundamentals = {
            "state": "AVAILABLE" if any(value != "DATA NOT AVAILABLE" for value in direct_metrics.values()) else "NOT APPLICABLE",
            "corporate_metrics": "NOT APPLICABLE",
            "applicable_metrics": list(capability["fundamental_metrics"]),
            "direct_instrument_fields": direct_metrics,
        }

    historical_snapshot = _history_snapshot(ticker)

    return {
        "source":
            "Yahoo Finance + yahoo_global_universe.csv",

        "security":
            record,

        "asset_class":
            asset_class,

        "currency":
            currency or "DATA NOT AVAILABLE",

        "analytics_capabilities":
            capability,

        "market_data":
            historical_snapshot if historical_snapshot is not None else "DATA NOT AVAILABLE",

        "fundamentals":
            fundamentals,
    }


# ============================================================
# SCREENING HELPERS
# ============================================================

@lru_cache(maxsize=4096)
def _fetch_one_market_cap(ticker):

    """
    Lightweight market-cap lookup used ONLY by the screener.

    FastInfo exposes market_cap as an attribute/property, not as a
    normal dictionary key.
    """

    ticker = str(ticker).strip().upper()

    try:

        t = yf.Ticker(ticker)

        fast_info = t.fast_info

        market_cap = getattr(
            fast_info,
            "market_cap",
            None,
        )

        if market_cap is None and hasattr(
            fast_info,
            "get",
        ):
            try:
                market_cap = fast_info.get(
                    "market_cap"
                )
            except Exception:
                market_cap = None

        return (
            ticker,
            _float(market_cap),
        )

    except Exception:
        return ticker, None


def _fetch_one_history(ticker):

    try:
        return (
            ticker,
            _history_snapshot(ticker),
        )

    except Exception:
        return ticker, None


# ============================================================
# SECURITY SCREENING
# ============================================================

def screen_securities(
    asset_class: str = "EQUITY",
    country: str = "",
    region: str = "",
    query: str = "",
    market_cap_category: str = "",
    near_52_week_low_pct: float = -1,
    near_52_week_high_pct: float = -1,
    min_market_cap: float = -1,
    max_market_cap: float = -1,
    limit: int = 50,
) -> dict:
    """Screens the master universe using Yahoo Finance prices and deterministic calculations.

    For India, market_cap_category='large' ranks the filtered Indian equities by
    retrieved market capitalization and selects the top 100 within the terminal universe.

    near_52_week_low_pct=0 means the current price must equal the one-year low.
    near_52_week_low_pct=2 means the current price may be up to 2 percent above it.
    """

    df = _universe().copy()

    if asset_class:
        asset_class = normalize_asset_class(asset_class)

        df = df[
            df["asset_class"].map(normalize_asset_class)
            == asset_class
        ]

    if country:

        df = df[
            df["country"].str.lower()
            == country.strip().lower()
        ]

    if region:

        df = df[
            df["region"].str.lower()
            == region.strip().lower()
        ]

    q = (
        query or ""
    ).strip().lower()

    if q:

        df = df[
            df["ticker"]
            .str.lower()
            .str.contains(
                q,
                regex=False
            )
            |
            df["name"]
            .str.lower()
            .str.contains(
                q,
                regex=False
            )
        ]

    candidates = (
        df["ticker"]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

    if not candidates:

        return {
            "source":
                "yahoo_global_universe.csv + Yahoo Finance",

            "matches": [],
        }

    # --------------------------------------------------------
    # MARKET CAP
    # --------------------------------------------------------

    market_caps = {}

    category = (
        market_cap_category or ""
    ).strip().lower()

    needs_market_caps = (
        category in {
            "large",
            "mid",
            "small",
        }
        or min_market_cap >= 0
        or max_market_cap >= 0
    )

    if needs_market_caps:

        with ThreadPoolExecutor(
            max_workers=8
        ) as pool:

            futures = [
                pool.submit(
                    _fetch_one_market_cap,
                    ticker,
                )
                for ticker in candidates
            ]

            for future in as_completed(
                futures
            ):

                ticker, cap = (
                    future.result()
                )

                if cap is not None:
                    market_caps[ticker] = cap

    # --------------------------------------------------------
    # MARKET-CAP CATEGORY
    # --------------------------------------------------------

    if category:

        ordered = sorted(
            market_caps.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        if category == "large":

            ranked = {
                ticker
                for ticker, _
                in ordered[:100]
            }

        elif category == "mid":

            ranked = {
                ticker
                for ticker, _
                in ordered[100:250]
            }

        else:

            ranked = {
                ticker
                for ticker, _
                in ordered[250:]
            }

        candidates = [
            ticker
            for ticker in candidates
            if ticker in ranked
        ]

    if min_market_cap >= 0:

        candidates = [
            ticker
            for ticker in candidates
            if market_caps.get(
                ticker,
                -1
            ) >= min_market_cap
        ]

    if max_market_cap >= 0:

        candidates = [
            ticker
            for ticker in candidates
            if market_caps.get(
                ticker,
                float("inf")
            ) <= max_market_cap
        ]

    # --------------------------------------------------------
    # PRICE HISTORY
    # --------------------------------------------------------

    needs_history = (
        near_52_week_low_pct >= 0
        or near_52_week_high_pct >= 0
    )

    histories = {}

    if needs_history:

        with ThreadPoolExecutor(
            max_workers=8
        ) as pool:

            futures = [
                pool.submit(
                    _fetch_one_history,
                    ticker,
                )
                for ticker in candidates
            ]

            for future in as_completed(
                futures
            ):

                ticker, snapshot = (
                    future.result()
                )

                if snapshot:
                    histories[ticker] = (
                        snapshot
                    )

    # --------------------------------------------------------
    # APPLY CONDITIONS
    # --------------------------------------------------------

    results = []

    candidate_set = set(
        candidates
    )

    for _, row in df.iterrows():

        ticker = str(
            row["ticker"]
        ).strip()

        if ticker not in candidate_set:
            continue

        snapshot = histories.get(
            ticker
        )

        if needs_history and not snapshot:
            continue

        if (
            snapshot
            and near_52_week_low_pct >= 0
        ):

            distance = snapshot.get(
                "distance_from_52_week_low_pct"
            )

            if (
                distance is None
                or distance
                > float(
                    near_52_week_low_pct
                )
            ):
                continue

        if (
            snapshot
            and near_52_week_high_pct >= 0
        ):

            distance_high = abs(
                float(
                    snapshot.get(
                        "distance_from_52_week_high_pct"
                    )
                    or 0
                )
            )

            if (
                distance_high
                > float(
                    near_52_week_high_pct
                )
            ):
                continue

        result = {

            "ticker":
                ticker,

            "name":
                str(
                    row.get(
                        "name",
                        ""
                    )
                ),

            "asset_class":
                str(
                    row.get(
                        "asset_class",
                        ""
                    )
                ),

            "region":
                str(
                    row.get(
                        "region",
                        ""
                    )
                ),

            "country":
                str(
                    row.get(
                        "country",
                        ""
                    )
                ),

            "instrument_type":
                str(
                    row.get(
                        "instrument_type",
                        ""
                    )
                ),

            "market_cap":
                market_caps.get(
                    ticker
                ),
        }

        if snapshot:
            result.update(
                snapshot
            )

        results.append(
            result
        )

    results.sort(
        key=lambda item:
            item.get(
                "distance_from_52_week_low_pct"
            )
            if item.get(
                "distance_from_52_week_low_pct"
            ) is not None
            else 10**9
    )

    limit = max(
        1,
        min(
            int(limit or 50),
            100
        )
    )

    return {

        "source":
            "Yahoo Finance + yahoo_global_universe.csv",

        "screen": {

            "asset_class":
                asset_class,

            "country":
                country,

            "region":
                region,

            "market_cap_category":
                market_cap_category,

            "near_52_week_low_pct":
                near_52_week_low_pct,

            "near_52_week_high_pct":
                near_52_week_high_pct,
        },

        "candidate_count":
            len(candidates),

        "match_count":
            len(results),

        "matches":
            results[:limit],
    }


# ============================================================
# DETERMINISTIC FINANCIAL MATH
# ============================================================

def calculate_financial_math(
    operation: str,
    value_a: float,
    value_b: float = 0,
    value_c: float = 0,
) -> dict:
    """Performs deterministic financial arithmetic requested by the user."""

    op = (
        operation or ""
    ).strip().lower()

    if op in {
        "return",
        "return_pct",
    }:

        if value_b == 0:
            return {
                "error":
                    "Starting value cannot be zero."
            }

        result = (
            (value_a / value_b)
            - 1.0
        ) * 100.0

    elif op == "cagr_pct":

        if (
            value_b <= 0
            or value_a <= 0
            or value_c <= 0
        ):

            return {
                "error":
                    "CAGR requires positive values and years."
            }

        result = (
            (
                value_a / value_b
            )
            ** (1.0 / value_c)
            - 1.0
        ) * 100.0

    elif op in {
        "percentage_difference",
        "pct_difference",
    }:

        if value_b == 0:
            return {
                "error":
                    "Base value cannot be zero."
            }

        result = (
            (value_a - value_b)
            / abs(value_b)
        ) * 100.0

    elif op == "multiply":

        result = (
            value_a * value_b
        )

    elif op == "divide":

        if value_b == 0:
            return {
                "error":
                    "Cannot divide by zero."
            }

        result = (
            value_a / value_b
        )

    elif op == "add":

        result = (
            value_a + value_b
        )

    elif op == "subtract":

        result = (
            value_a - value_b
        )

    else:

        return {
            "error":
                f"Unsupported operation: {operation}"
        }

    return {

        "operation":
            operation,

        "value_a":
            value_a,

        "value_b":
            value_b,

        "value_c":
            value_c,

        "result":
            result,
    }


# ============================================================
# GEMINI TOOL REGISTRY
# ============================================================

TERMINAL_TOOLS = [

    get_universe_overview,

    search_terminal_universe,

    get_security_snapshot,

    screen_securities,

    calculate_financial_math,

]


