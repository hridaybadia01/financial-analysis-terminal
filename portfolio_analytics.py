"""
Portfolio Intelligence Engine
==============================

Deterministic portfolio analytics.
No AI calls are made in this module.

The module calculates:
- portfolio return
- volatility
- Sharpe / Sortino
- maximum drawdown
- historical VaR
- concentration / HHI
- diversification
- risk contribution
- sector / geography / currency exposure
- correlation
- stress testing
- scenario analysis
- rebalancing
"""

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def clean_series(series):
    s = pd.to_numeric(series, errors="coerce")
    return s.replace([np.inf, -np.inf], np.nan).dropna()


def build_portfolio_returns(price_series, weights):
    """
    Build weighted daily portfolio returns from aligned price series.
    """
    frames = []

    for ticker, prices in price_series.items():
        if ticker not in weights:
            continue

        s = clean_series(prices)
        if len(s) < 2:
            continue

        r = s.pct_change()
        r.name = ticker
        frames.append(r)

    if not frames:
        return pd.Series(dtype=float)

    returns_df = pd.concat(frames, axis=1).sort_index().ffill()
    returns_df = returns_df.dropna(how="all")

    weight_series = pd.Series(weights, dtype=float)
    available = [c for c in returns_df.columns if c in weight_series.index]

    if not available:
        return pd.Series(dtype=float)

    weight_series = weight_series.loc[available]

    if weight_series.sum() <= 0:
        return pd.Series(dtype=float)

    weight_series = weight_series / weight_series.sum()

    portfolio_returns = returns_df[available].mul(weight_series, axis=1).sum(axis=1)
    return clean_series(portfolio_returns)


def annualized_return(returns):
    """
    Historical annualized return proxy.
    This is NOT a forward forecast.
    """
    r = clean_series(returns)

    if len(r) < 2:
        return None

    cumulative = (1.0 + r).prod()

    if cumulative <= 0:
        return None

    years = len(r) / TRADING_DAYS

    if years <= 0:
        return None

    return float(cumulative ** (1.0 / years) - 1.0)


def annualized_volatility(returns):
    r = clean_series(returns)

    if len(r) < 2:
        return None

    return float(r.std(ddof=1) * np.sqrt(TRADING_DAYS))


def sharpe_ratio(returns, risk_free=0.0):
    r = clean_series(returns)

    if len(r) < 2:
        return None

    daily_rf = (1.0 + risk_free) ** (1.0 / TRADING_DAYS) - 1.0
    excess = r - daily_rf

    volatility = r.std(ddof=1)

    if volatility == 0 or pd.isna(volatility):
        return None

    return float(excess.mean() / volatility * np.sqrt(TRADING_DAYS))


def sortino_ratio(returns, risk_free=0.0):
    r = clean_series(returns)

    if len(r) < 2:
        return None

    daily_rf = (1.0 + risk_free) ** (1.0 / TRADING_DAYS) - 1.0
    excess = r - daily_rf

    downside = excess[excess < 0]

    if len(downside) < 2:
        return None

    downside_deviation = np.sqrt(np.mean(downside ** 2)) * np.sqrt(TRADING_DAYS)

    if downside_deviation == 0:
        return None

    return float(excess.mean() * TRADING_DAYS / downside_deviation)


def maximum_drawdown(returns):
    r = clean_series(returns)

    if len(r) < 2:
        return None, pd.Series(dtype=float)

    wealth = (1.0 + r).cumprod()
    running_peak = wealth.cummax()
    drawdown = wealth / running_peak - 1.0

    return float(drawdown.min()), drawdown


def historical_var(returns, confidence=0.95):
    r = clean_series(returns)

    if len(r) < 2:
        return None

    return float(-np.quantile(r, 1.0 - confidence))


def expected_shortfall(returns, confidence=0.95):
    r = clean_series(returns)

    if len(r) < 2:
        return None

    threshold = np.quantile(r, 1.0 - confidence)
    tail = r[r <= threshold]

    if tail.empty:
        return None

    return float(-tail.mean())


def concentration_metrics(weights):
    """
    HHI and effective number of holdings.
    """
    if not weights:
        return {
            "hhi": None,
            "effective_holdings": None,
            "concentration_score": None,
        }

    w = pd.Series(weights, dtype=float)
    w = w[w > 0]

    if w.empty:
        return {
            "hhi": None,
            "effective_holdings": None,
            "concentration_score": None,
        }

    w = w / w.sum()

    hhi = float((w ** 2).sum())
    effective = float(1.0 / hhi) if hhi > 0 else None

    # 0 = extremely concentrated, 100 = highly diversified.
    concentration_score = float(max(0.0, min(100.0, (1.0 - hhi) * 100.0)))

    return {
        "hhi": hhi,
        "effective_holdings": effective,
        "concentration_score": concentration_score,
    }


def diversification_score(weights, metadata):
    """
    Composite diversification score based on:
    - security concentration
    - number of securities
    - asset-class diversity
    - geographic diversity
    - currency diversity
    """
    if not weights:
        return None

    concentration = concentration_metrics(weights)
    security_score = concentration["concentration_score"]

    positive = [w for w in weights.values() if w > 0]

    if not positive:
        return None

    records = []

    for ticker, weight in weights.items():
        record = metadata.get(ticker, {})
        records.append({
            "weight": float(weight),
            "asset_class": str(record.get("asset_class", "")).upper(),
            "country": str(record.get("country", "")).strip(),
            "currency": str(record.get("currency", "")).upper(),
        })

    def category_score(field):
        category_weights = {}

        for row in records:
            category = row[field] or "UNKNOWN"
            category_weights[category] = (
                category_weights.get(category, 0.0)
                + row["weight"]
            )

        if not category_weights:
            return 0.0

        shares = np.array(list(category_weights.values()), dtype=float)
        total = shares.sum()

        if total <= 0:
            return 0.0

        shares = shares / total
        hhi = float((shares ** 2).sum())

        return max(0.0, min(100.0, (1.0 - hhi) * 100.0))

    asset_score = category_score("asset_class")
    country_score = category_score("country")
    currency_score = category_score("currency")

    final = (
        security_score * 0.45
        + asset_score * 0.25
        + country_score * 0.15
        + currency_score * 0.15
    )

    return float(max(0.0, min(100.0, final)))


def portfolio_risk_score(
    volatility,
    max_drawdown,
    concentration_score,
    diversification,
    crypto_weight=0.0,
):
    """
    Deterministic 0-100 risk score.

    Higher = more risky.
    """
    vol_component = (
        min(100.0, max(0.0, volatility * 250.0))
        if volatility is not None
        else 50.0
    )

    drawdown_component = (
        min(100.0, max(0.0, abs(max_drawdown) * 250.0))
        if max_drawdown is not None
        else 50.0
    )

    concentration_risk = (
        100.0 - concentration_score
        if concentration_score is not None
        else 50.0
    )

    diversification_risk = (
        100.0 - diversification
        if diversification is not None
        else 50.0
    )

    crypto_component = min(100.0, max(0.0, crypto_weight * 500.0))

    score = (
        vol_component * 0.30
        + drawdown_component * 0.20
        + concentration_risk * 0.20
        + diversification_risk * 0.15
        + crypto_component * 0.15
    )

    return float(max(0.0, min(100.0, score)))


def risk_label(score):
    if score is None:
        return "DATA NOT AVAILABLE"

    if score <= 30:
        return "CONSERVATIVE"

    if score <= 50:
        return "MODERATE"

    if score <= 70:
        return "MODERATELY AGGRESSIVE"

    if score <= 85:
        return "AGGRESSIVE"

    return "VERY AGGRESSIVE"


def risk_color_label(score):
    label = risk_label(score)

    if label in {"CONSERVATIVE", "MODERATE"}:
        return "LOW / MODERATE"

    if label == "MODERATELY AGGRESSIVE":
        return "MODERATE-HIGH"

    return "HIGH"


def scenario_returns(base_return, volatility):
    """
    Historical scenario framework.

    Bear = historical return - volatility
    Base = historical return
    Bull = historical return + volatility

    These are scenario estimates, NOT guaranteed forecasts.
    """
    if base_return is None:
        return {
            "Bear": None,
            "Base": None,
            "Bull": None,
        }

    vol = volatility or 0.0

    return {
        "Bear": float(base_return - vol),
        "Base": float(base_return),
        "Bull": float(base_return + vol),
    }


def group_exposure(weights, metadata, field):
    grouped = {}

    for ticker, weight in weights.items():
        record = metadata.get(ticker, {})
        value = str(record.get(field, "") or "").strip()

        if not value:
            value = "DATA NOT AVAILABLE"

        grouped[value] = grouped.get(value, 0.0) + float(weight)

    return (
        pd.DataFrame(
            [
                {"Category": k, "Weight %": v * 100.0}
                for k, v in grouped.items()
            ]
        )
        .sort_values("Weight %", ascending=False)
        .reset_index(drop=True)
    )


def risk_contribution(returns_df, weights):
    """
    Marginal volatility contribution approximation.

    Uses covariance matrix:
    contribution_i = weight_i * marginal_contribution_i
    """
    if returns_df.empty:
        return pd.DataFrame(columns=["Ticker", "Weight %", "Risk Contribution %"])

    available = [
        ticker for ticker in returns_df.columns
        if ticker in weights
    ]

    if len(available) < 1:
        return pd.DataFrame(columns=["Ticker", "Weight %", "Risk Contribution %"])

    data = returns_df[available].dropna(how="all").ffill().dropna()

    if len(data) < 2:
        return pd.DataFrame(columns=["Ticker", "Weight %", "Risk Contribution %"])

    w = pd.Series(
        {ticker: float(weights[ticker]) for ticker in available},
        dtype=float,
    )

    w = w / w.sum()

    cov = data.cov() * TRADING_DAYS

    portfolio_variance = float(w.T @ cov @ w)

    if portfolio_variance <= 0:
        return pd.DataFrame(
            {
                "Ticker": available,
                "Weight %": w.values * 100.0,
                "Risk Contribution %": np.zeros(len(available)),
            }
        )

    portfolio_vol = np.sqrt(portfolio_variance)
    marginal = cov @ w / portfolio_vol
    contribution = w * marginal

    total_contribution = contribution.sum()

    if total_contribution != 0:
        contribution_pct = contribution / total_contribution * 100.0
    else:
        contribution_pct = contribution * 0.0

    result = pd.DataFrame(
        {
            "Ticker": available,
            "Weight %": w.values * 100.0,
            "Risk Contribution %": contribution_pct.values,
        }
    )

    return result.sort_values(
        "Risk Contribution %",
        ascending=False,
    ).reset_index(drop=True)


def correlation_matrix(returns_df):
    if returns_df.empty:
        return pd.DataFrame()

    data = returns_df.dropna(how="all").ffill().dropna()

    if data.shape[1] < 2 or len(data) < 2:
        return pd.DataFrame()

    return data.corr()


def stress_test(
    weights,
    metadata,
    total_value,
    scenario,
):
    """
    Simple deterministic asset-class stress testing.

    Returns estimated portfolio percentage and INR impact.
    """
    shocks = {
        "Global Equity Crash": {
            "EQUITY": -0.20,
            "INDEX": -0.18,
            "CRYPTO": -0.35,
            "FIXED_INCOME": 0.03,
            "COMMODITY": -0.10,
            "FX": 0.00,
        },
        "Interest Rate Shock": {
            "EQUITY": -0.08,
            "INDEX": -0.08,
            "CRYPTO": -0.15,
            "FIXED_INCOME": -0.08,
            "COMMODITY": 0.02,
            "FX": 0.00,
        },
        "Inflation Shock": {
            "EQUITY": -0.10,
            "INDEX": -0.10,
            "CRYPTO": -0.15,
            "FIXED_INCOME": -0.12,
            "COMMODITY": 0.15,
            "FX": 0.03,
        },
        "Crypto Crash": {
            "EQUITY": 0.00,
            "INDEX": 0.00,
            "CRYPTO": -0.50,
            "FIXED_INCOME": 0.01,
            "COMMODITY": 0.00,
            "FX": 0.00,
        },
        "USD Strengthening": {
            "EQUITY": 0.02,
            "INDEX": 0.01,
            "CRYPTO": -0.08,
            "FIXED_INCOME": 0.00,
            "COMMODITY": -0.04,
            "FX": 0.03,
        },
    }

    selected = shocks.get(scenario, shocks["Global Equity Crash"])

    impact = 0.0

    for ticker, weight in weights.items():
        record = metadata.get(ticker, {})
        asset_class = str(record.get("asset_class", "")).upper()

        shock = selected.get(asset_class, 0.0)
        impact += float(weight) * shock

    rupee_impact = float(total_value * impact)

    return {
        "impact_pct": float(impact),
        "impact_value": rupee_impact,
        "shocks": selected,
    }


def target_allocation(profile):
    """
    Model allocation templates.
    These are educational portfolio frameworks, not personal advice.
    """
    profiles = {
        "Conservative": {
            "EQUITY": 0.35,
            "FIXED_INCOME": 0.45,
            "COMMODITY": 0.15,
            "CRYPTO": 0.05,
            "INDEX": 0.00,
            "FX": 0.00,
        },
        "Moderate": {
            "EQUITY": 0.50,
            "FIXED_INCOME": 0.25,
            "COMMODITY": 0.10,
            "CRYPTO": 0.05,
            "INDEX": 0.10,
            "FX": 0.00,
        },
        "Aggressive": {
            "EQUITY": 0.65,
            "FIXED_INCOME": 0.10,
            "COMMODITY": 0.05,
            "CRYPTO": 0.10,
            "INDEX": 0.10,
            "FX": 0.00,
        },
    }

    return profiles.get(profile, profiles["Moderate"])


def rebalance_plan(weights, metadata, total_value, profile):
    targets = target_allocation(profile)

    current = {}

    for ticker, weight in weights.items():
        record = metadata.get(ticker, {})
        asset_class = str(record.get("asset_class", "")).upper()

        if not asset_class:
            asset_class = "OTHER"

        current[asset_class] = current.get(asset_class, 0.0) + float(weight)

    rows = []

    for asset_class in [
        "EQUITY",
        "FIXED_INCOME",
        "COMMODITY",
        "INDEX",
        "CRYPTO",
        "FX",
    ]:
        current_weight = current.get(asset_class, 0.0)
        target_weight = targets.get(asset_class, 0.0)
        difference = target_weight - current_weight

        rows.append(
            {
                "Asset Class": asset_class,
                "Current %": current_weight * 100.0,
                "Target %": target_weight * 100.0,
                "Difference %": difference * 100.0,
                "Approx. ₹ Change": difference * total_value,
            }
        )

    return pd.DataFrame(rows)


def portfolio_summary(
    returns,
    weights,
    metadata,
    total_value,
    risk_free=0.0,
):
    volatility = annualized_volatility(returns)
    annual_return = annualized_return(returns)
    sharpe = sharpe_ratio(returns, risk_free)
    sortino = sortino_ratio(returns, risk_free)
    max_dd, drawdown = maximum_drawdown(returns)

    var95 = historical_var(returns, 0.95)
    var99 = historical_var(returns, 0.99)
    es95 = expected_shortfall(returns, 0.95)

    concentration = concentration_metrics(weights)
    diversification = diversification_score(weights, metadata)

    crypto_weight = sum(
        float(weight)
        for ticker, weight in weights.items()
        if str(metadata.get(ticker, {}).get("asset_class", "")).upper() == "CRYPTO"
    )

    risk_score = portfolio_risk_score(
        volatility,
        max_dd,
        concentration["concentration_score"],
        diversification,
        crypto_weight,
    )

    return {
        "annual_return": annual_return,
        "volatility": volatility,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": max_dd,
        "var95": var95,
        "var99": var99,
        "expected_shortfall": es95,
        "hhi": concentration["hhi"],
        "effective_holdings": concentration["effective_holdings"],
        "concentration_score": concentration["concentration_score"],
        "diversification_score": diversification,
        "risk_score": risk_score,
        "risk_label": risk_label(risk_score),
        "risk_level": risk_color_label(risk_score),
        "scenarios": scenario_returns(annual_return, volatility),
        "drawdown_series": drawdown,
    }
