"""Canonical, deterministic asset-class analytics capabilities."""

import math
import re
from datetime import date, datetime, timezone


CANONICAL_ASSET_CLASSES = (
    "EQUITY",
    "FIXED_INCOME",
    "COMMODITY",
    "INDEX",
    "CRYPTO",
    "FX",
)

DATA_STATES = (
    "AVAILABLE",
    "DATA NOT AVAILABLE",
    "NOT APPLICABLE",
    "INSUFFICIENT HISTORY",
    "DATA ERROR",
)

_ALIASES = {
    "EQUITIES": "EQUITY",
    "STOCK": "EQUITY",
    "STOCKS": "EQUITY",
    "FIXEDINCOME": "FIXED_INCOME",
    "BOND": "FIXED_INCOME",
    "BONDS": "FIXED_INCOME",
    "BOND_ETF": "FIXED_INCOME",
    "COMMODITIES": "COMMODITY",
    "FUTURES": "COMMODITY",
    "INDICES": "INDEX",
    "INDEXES": "INDEX",
    "BENCHMARK": "INDEX",
    "BENCHMARKS": "INDEX",
    "INDICES_BENCHMARKS": "INDEX",
    "CRYPTOCURRENCY": "CRYPTO",
    "CRYPTOCURRENCIES": "CRYPTO",
    "DIGITAL_ASSET": "CRYPTO",
    "FOREX": "FX",
    "FOREIGN_EXCHANGE": "FX",
    "FX_CURRENCIES": "FX",
    "CURRENCY": "FX",
    "CURRENCIES": "FX",
    "CURRENCY_PAIR": "FX",
}

_PRICE_INDICATORS = (
    "SMA 20",
    "SMA 50",
    "SMA 200",
    "RSI",
    "MACD",
    "Bollinger Bands",
    "Golden Cross",
    "Death Cross",
    "Momentum",
)
_CORPORATE_FUNDAMENTALS = (
    "Market Cap",
    "P/E",
    "P/B",
    "ROE",
    "Debt/Equity",
    "Revenue Growth",
    "Profit Margin",
    "Dividend Yield",
)
_NONCORPORATE_FUNDAMENTALS = (
    "Yield",
    "Duration",
    "Maturity",
    "Credit Category",
)

_DIRECT_PROVIDER_FIELDS = {
    "FIXED_INCOME": {
        "Yield": ("yield", "yieldToMaturity", "yieldToWorst"),
        "Duration": ("duration", "effectiveDuration", "modifiedDuration"),
        "Maturity": ("maturityDate", "maturity", "maturityDateTimestamp"),
        "Credit Category": ("creditRating", "rating", "bondRating"),
        "Rate Sensitivity": ("rateSensitivity", "interestRateSensitivity"),
    },
    "INDEX": {
        "P/E (index-level, provider-reported)": ("trailingPE", "indexPE"),
        "P/B (index-level, provider-reported)": ("priceToBook", "indexPB"),
    },
    "CRYPTO": {
        "Market Cap": ("marketCap", "market_cap"),
        "Circulating Supply": ("circulatingSupply", "circulating_supply"),
        "Liquidity": ("volume24Hr", "volume24h", "volume_24h"),
    },
    "COMMODITY": {
        "Contract Expiry": ("expireDate", "expiry", "expiration"),
        "Contract Size": ("contractSize", "contract_size"),
    },
}

_ASSET_CAPABILITIES = {
    "EQUITY": {
        "annualization_sessions": 252,
        "technical_indicators": _PRICE_INDICATORS,
        "risk_metrics": (
            "Volatility",
            "Rolling Volatility",
            "Sharpe",
            "Sortino",
            "Downside Risk",
            "Maximum Drawdown",
            "Beta",
            "Value at Risk",
        ),
        "fundamental_metrics": _CORPORATE_FUNDAMENTALS,
        "conditional_metrics": (),
        "metadata": (
            "Sector",
            "Industry",
            "Exchange",
            "Country",
            "Currency",
        ),
        "notes": "Corporate fundamentals are applicable when the provider reports them. Beta requires a compatible benchmark and currency; Sharpe/Sortino require a matching-currency risk-free rate.",
    },
    "FIXED_INCOME": {
        "annualization_sessions": 252,
        "technical_indicators": _PRICE_INDICATORS,
        "risk_metrics": (
            "Price Volatility",
            "Rolling Volatility",
            "Maximum Drawdown",
            "Value at Risk",
        ),
        "fundamental_metrics": (),
        "conditional_metrics": _NONCORPORATE_FUNDAMENTALS,
        "metadata": (
            "Instrument Type",
            "Issuer",
            "Maturity",
            "Credit Category",
            "Currency",
        ),
        "notes": "Price-based indicators describe the security or fund price only. Yield, duration, maturity, credit, and rate sensitivity require direct provider data and are not inferred from price.",
    },
    "COMMODITY": {
        "annualization_sessions": 252,
        "technical_indicators": _PRICE_INDICATORS,
        "risk_metrics": (
            "Price Volatility",
            "Rolling Volatility",
            "Maximum Drawdown",
            "Value at Risk",
            "Trend",
        ),
        "fundamental_metrics": (),
        "conditional_metrics": (),
        "metadata": (
            "Contract",
            "Exchange",
            "Expiry",
            "Currency",
        ),
        "notes": "Price analytics apply to the retrieved contract. Futures rolls and contract changes can affect continuity; corporate fundamentals are not applicable.",
    },
    "INDEX": {
        "annualization_sessions": 252,
        "technical_indicators": _PRICE_INDICATORS,
        "risk_metrics": (
            "Volatility",
            "Rolling Volatility",
            "Maximum Drawdown",
            "Value at Risk",
            "Benchmark Risk",
        ),
        "fundamental_metrics": (),
        "conditional_metrics": ("Index-level valuation when directly reported",),
        "metadata": (
            "Index Name",
            "Region",
            "Country",
            "Currency",
            "Benchmark",
        ),
        "notes": "Price indicators apply to the index level. Company-specific fundamentals are not applicable; index valuation is shown only when explicitly supplied as an index-level provider field.",
    },
    "CRYPTO": {
        "annualization_sessions": 365,
        "technical_indicators": _PRICE_INDICATORS,
        "risk_metrics": (
            "Volatility",
            "Rolling Volatility",
            "Downside Risk",
            "Maximum Drawdown",
            "Value at Risk",
        ),
        "fundamental_metrics": (),
        "conditional_metrics": ("Market Cap", "Circulating Supply", "Liquidity"),
        "metadata": (
            "Asset Name",
            "Network",
            "Currency",
        ),
        "notes": "Crypto annualization uses 365 daily observations. Corporate earnings, ROE, leverage, and dividend metrics are not applicable unless the instrument itself reports them.",
    },
    "FX": {
        "annualization_sessions": 260,
        "technical_indicators": _PRICE_INDICATORS,
        "risk_metrics": (
            "Volatility",
            "Rolling Volatility",
            "Maximum Drawdown",
            "Value at Risk",
            "Currency Movement",
            "Relative Strength",
        ),
        "fundamental_metrics": (),
        "conditional_metrics": (),
        "metadata": (
            "Base Currency",
            "Quote Currency",
            "Currency Pair",
            "Region",
        ),
        "notes": "FX annualization uses 260 daily observations. The quote currency is the Yahoo instrument currency; the ticker identifies the pair. Corporate fundamentals are not applicable.",
    },
}


def normalize_asset_class(value):
    """Normalize CSV/display aliases to one of the six canonical classes."""
    text = str(value or "").strip().upper()
    compact = re.sub(r"[^A-Z0-9]+", "_", text).strip("_")
    if compact in CANONICAL_ASSET_CLASSES:
        return compact
    return _ALIASES.get(compact, "UNKNOWN")


def get_asset_capabilities(asset_class):
    """Return one canonical asset capability record, or an empty unknown record."""
    canonical = normalize_asset_class(asset_class)
    if canonical == "UNKNOWN":
        return {
            "asset_class": "UNKNOWN",
            "annualization_sessions": None,
            "technical_indicators": (),
            "risk_metrics": (),
            "fundamental_metrics": (),
            "conditional_metrics": (),
            "provider_fields": {},
            "metadata": (),
            "notes": "DATA NOT AVAILABLE: the security's asset class is not present or recognized.",
        }
    return {
        "asset_class": canonical,
        "provider_fields": _DIRECT_PROVIDER_FIELDS.get(canonical, {}),
        **_ASSET_CAPABILITIES[canonical],
    }


def supports_metric(asset_class, metric, category=None):
    """Whether a metric is appropriate for this canonical asset class."""
    capability = get_asset_capabilities(asset_class)
    categories = (
        (category,)
        if category in {"technical_indicators", "risk_metrics", "fundamental_metrics", "conditional_metrics", "metadata"}
        else ("technical_indicators", "risk_metrics", "fundamental_metrics", "conditional_metrics", "metadata")
    )
    target = str(metric or "").strip().casefold()
    return any(
        target == str(name).casefold()
        for name in categories
        for name in capability[name]
    )


def metric_state(asset_class, metric, value=None, *, insufficient_history=False, data_error=False, category=None):
    """Return one standard availability state without substituting a value."""
    if data_error:
        return "DATA ERROR"
    if not supports_metric(asset_class, metric, category):
        return "NOT APPLICABLE"
    if insufficient_history:
        return "INSUFFICIENT HISTORY"
    if value is None:
        return "DATA NOT AVAILABLE"
    try:
        if not math.isfinite(float(value)):
            return "DATA NOT AVAILABLE"
    except (TypeError, ValueError):
        return "DATA NOT AVAILABLE"
    return "AVAILABLE"


def annualization_periods(asset_class, interval="1d"):
    """Return observations/year for this class and data frequency, if defined."""
    interval = str(interval or "1d").strip().lower()
    if interval in {"1wk", "1w", "wk", "weekly"}:
        return 52
    if interval in {"1mo", "1mth", "monthly"}:
        return 12
    return get_asset_capabilities(asset_class)["annualization_sessions"]


def return_observation_periods(asset_class):
    """Daily-bar lookbacks derived from the class's annual observation count."""
    annual = get_asset_capabilities(asset_class)["annualization_sessions"]
    if annual is None:
        return {}
    return {
        "1D": 1,
        "1W": max(1, round(annual / 52)),
        "1M": max(1, round(annual / 12)),
        "3M": max(1, round(annual / 4)),
        "6M": max(1, round(annual / 2)),
        "1Y": annual,
    }


def direct_provider_metrics(asset_class, provider_values):
    """Extract only documented direct fields; never derive unavailable attributes."""
    capability = get_asset_capabilities(asset_class)
    source = provider_values if isinstance(provider_values, dict) else {}
    result = {}
    for label, aliases in capability.get("provider_fields", {}).items():
        value = None
        for alias in aliases:
            candidate = source.get(alias)
            if candidate is None:
                continue
            if label == "Maturity":
                try:
                    timestamp = float(candidate)
                    if math.isfinite(timestamp) and timestamp > 1_000_000_000:
                        value = datetime.fromtimestamp(timestamp, tz=timezone.utc).date().isoformat()
                        break
                except (TypeError, ValueError, OverflowError, OSError):
                    pass
            if isinstance(candidate, (datetime, date)):
                value = candidate.isoformat()
            elif isinstance(candidate, str):
                value = candidate.strip() or None
            else:
                try:
                    numeric = float(candidate)
                    value = numeric if math.isfinite(numeric) else None
                except (TypeError, ValueError):
                    value = str(candidate).strip() or None
            if value is not None:
                break
        result[label] = value if value is not None else "DATA NOT AVAILABLE"
    return result
