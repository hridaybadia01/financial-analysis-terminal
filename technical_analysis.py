"""Deterministic price-based technical analysis for the Technical Analysis page."""

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from asset_capabilities import (
    annualization_periods,
    get_asset_capabilities,
    normalize_asset_class,
)


RETURN_HORIZONS = (
    ("1D", 1, 4),
    ("1W", 7, 10),
    ("1M", 30, 14),
    ("3M", 91, 18),
    ("6M", 182, 25),
    ("1Y", 365, 35),
)

INTRADAY_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}


def _clean_close(history):
    if isinstance(history, pd.Series):
        close = history.copy()
    elif isinstance(history, pd.DataFrame) and "Close" in history.columns:
        close = history["Close"].copy()
    else:
        return pd.Series(dtype=float, name="Close")

    close = pd.to_numeric(close, errors="coerce")
    try:
        close.index = pd.to_datetime(close.index, errors="coerce")
    except (TypeError, ValueError):
        return pd.Series(dtype=float, name="Close")

    close = close[~close.index.isna()]
    close = close[close.index.notna()]
    close = close[np.isfinite(close.to_numpy(dtype=float, na_value=np.nan))]
    close = close[close > 0]
    close = close[~close.index.duplicated(keep="last")].sort_index()
    close.name = "Close"
    return close.astype(float)


def _last_value(series):
    if series is None:
        return None
    values = series.dropna()
    if values.empty:
        return None
    value = float(values.iloc[-1])
    return value if math.isfinite(value) else None


def _return_for_horizon(close, days, max_staleness_days):
    if len(close) < 2:
        return None
    target = close.index[-1] - pd.Timedelta(days=days)
    position = close.index.searchsorted(target, side="right") - 1
    if position < 0:
        return None
    anchor_date = close.index[position]
    staleness = (target - anchor_date).total_seconds() / 86400
    if staleness > max_staleness_days:
        return None
    anchor = float(close.iloc[position])
    latest = float(close.iloc[-1])
    if anchor <= 0:
        return None
    return latest / anchor - 1


def _rsi(close, window=14):
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    average_gain = gains.ewm(
        alpha=1 / window, min_periods=window, adjust=False
    ).mean()
    average_loss = losses.ewm(
        alpha=1 / window, min_periods=window, adjust=False
    ).mean()
    relative_strength = average_gain / average_loss.replace(0, np.nan)
    values = 100 - (100 / (1 + relative_strength))
    values = values.mask((average_loss == 0) & (average_gain > 0), 100)
    values = values.mask((average_gain == 0) & (average_loss > 0), 0)
    values = values.mask((average_gain == 0) & (average_loss == 0), 50)
    return values


def _macd(close, fast=12, slow=26, signal=9):
    fast_average = close.ewm(
        span=fast, min_periods=fast, adjust=False
    ).mean()
    slow_average = close.ewm(
        span=slow, min_periods=slow, adjust=False
    ).mean()
    line = fast_average - slow_average
    signal_line = line.ewm(
        span=signal, min_periods=signal, adjust=False
    ).mean()
    return line, signal_line, line - signal_line


def _cross_state(short_average, long_average, up_name, down_name):
    paired = pd.concat(
        [short_average.rename("short"), long_average.rename("long")], axis=1
    ).dropna()
    if len(paired) < 2:
        return "DATA NOT AVAILABLE"
    previous = paired.iloc[-2]
    current = paired.iloc[-1]
    if previous["short"] < previous["long"] and current["short"] >= current["long"]:
        return up_name
    if previous["short"] > previous["long"] and current["short"] <= current["long"]:
        return down_name
    return "No crossover on latest observation"


def calculate_technical_analysis(history, asset_class, interval="1d"):
    """Calculate deterministic price indicators and explicit score components."""
    close = _clean_close(history)
    asset_class = normalize_asset_class(asset_class)
    capability = get_asset_capabilities(asset_class)
    annual_sessions = capability["annualization_sessions"]
    asset_note = capability["notes"]
    interval = str(interval or "1d").lower()

    empty = {
        "valid": False,
        "close": close,
        "asset_class": asset_class,
        "asset_note": asset_note,
        "annual_sessions": annual_sessions,
        "returns": {label: None for label, _, _ in RETURN_HORIZONS},
        "cumulative_return": None,
        "cagr": None,
        "smas": {},
        "sma_values": {},
        "price_vs_sma": {},
        "trend": "DATA NOT AVAILABLE",
        "sma_cross": "DATA NOT AVAILABLE",
        "rsi": pd.Series(dtype=float),
        "rsi_value": None,
        "rsi_state": "DATA NOT AVAILABLE",
        "macd": pd.Series(dtype=float),
        "macd_signal": pd.Series(dtype=float),
        "macd_histogram": pd.Series(dtype=float),
        "macd_values": (None, None, None),
        "macd_cross": "DATA NOT AVAILABLE",
        "bb_upper": pd.Series(dtype=float),
        "bb_middle": pd.Series(dtype=float),
        "bb_lower": pd.Series(dtype=float),
        "bb_values": (None, None, None),
        "bb_bandwidth": None,
        "bb_position": None,
        "bb_regime": "DATA NOT AVAILABLE",
        "volatility_returns": pd.Series(dtype=float),
        "volatility_frequency": "DATA NOT AVAILABLE",
        "period_volatility": None,
        "daily_volatility": None,
        "annualized_volatility": None,
        "rolling_volatility": pd.Series(dtype=float),
        "volatility_regime": "DATA NOT AVAILABLE",
        "drawdown": pd.Series(dtype=float),
        "max_drawdown": None,
        "cumulative_series": pd.Series(dtype=float),
        "score_components": [],
        "score": None,
        "score_available": 0,
        "score_signal": "DATA NOT AVAILABLE",
    }
    if close.empty:
        return empty

    result = empty.copy()
    result.update({"valid": True, "close": close})
    result["returns"] = {
        label: _return_for_horizon(close, days, staleness)
        for label, days, staleness in RETURN_HORIZONS
    }

    starting_price = float(close.iloc[0])
    latest_price = float(close.iloc[-1])
    result["cumulative_return"] = latest_price / starting_price - 1
    elapsed_days = (close.index[-1] - close.index[0]).total_seconds() / 86400
    if elapsed_days >= 365 and starting_price > 0 and latest_price > 0:
        result["cagr"] = (latest_price / starting_price) ** (365.25 / elapsed_days) - 1

    result["cumulative_series"] = (close / starting_price - 1) * 100

    smas = {
        window: close.rolling(window=window, min_periods=window).mean()
        for window in (20, 50, 200)
    }
    result["smas"] = smas
    result["sma_values"] = {
        window: _last_value(series) for window, series in smas.items()
    }
    result["price_vs_sma"] = {
        window: (
            latest_price / value - 1
            if value is not None and value > 0
            else None
        )
        for window, value in result["sma_values"].items()
    }

    sma50 = result["sma_values"][50]
    sma200 = result["sma_values"][200]
    if result["sma_values"][20] is not None and sma50 is not None and sma200 is not None:
        if latest_price > sma50 > sma200:
            result["trend"] = "Uptrend"
        elif latest_price < sma50 < sma200:
            result["trend"] = "Downtrend"
        else:
            result["trend"] = "Mixed / transitioning"
    result["sma_cross"] = _cross_state(
        smas[50], smas[200], "Golden Cross", "Death Cross"
    )

    rsi_series = _rsi(close)
    rsi_value = _last_value(rsi_series)
    result["rsi"] = rsi_series
    result["rsi_value"] = rsi_value
    if rsi_value is not None:
        if rsi_value >= 70:
            result["rsi_state"] = "Overbought (>= 70)"
        elif rsi_value <= 30:
            result["rsi_state"] = "Oversold (<= 30)"
        elif rsi_value >= 50:
            result["rsi_state"] = "Positive momentum (50-70)"
        else:
            result["rsi_state"] = "Below-neutral momentum (30-50)"

    macd_line, macd_signal, macd_histogram = _macd(close)
    result.update({
        "macd": macd_line,
        "macd_signal": macd_signal,
        "macd_histogram": macd_histogram,
        "macd_values": (
            _last_value(macd_line),
            _last_value(macd_signal),
            _last_value(macd_histogram),
        ),
        "macd_cross": _cross_state(
            macd_line, macd_signal, "Bullish MACD crossover", "Bearish MACD crossover"
        ),
    })

    bb_middle = close.rolling(window=20, min_periods=20).mean()
    bb_std = close.rolling(window=20, min_periods=20).std(ddof=1)
    bb_upper = bb_middle + 2 * bb_std
    bb_lower = bb_middle - 2 * bb_std
    upper_value = _last_value(bb_upper)
    middle_value = _last_value(bb_middle)
    lower_value = _last_value(bb_lower)
    bandwidth = None
    position = None
    if upper_value is not None and middle_value and lower_value is not None:
        bandwidth = (upper_value - lower_value) / abs(middle_value) * 100
        width = upper_value - lower_value
        if width > 0:
            position = (latest_price - lower_value) / width * 100
    width_series = ((bb_upper - bb_lower) / bb_middle.abs()) * 100
    valid_widths = width_series.dropna()
    bb_regime = "DATA NOT AVAILABLE"
    if len(valid_widths) >= 40 and bandwidth is not None:
        baseline = valid_widths.iloc[:-1].tail(120)
        if not baseline.empty and bandwidth <= float(baseline.quantile(0.1)):
            bb_regime = "Squeeze (lowest 10% of recent bandwidth)"
        elif len(valid_widths) > 1 and bandwidth > float(valid_widths.iloc[-2]) * 1.05:
            bb_regime = "Expanding (>5% wider than prior observation)"
        else:
            bb_regime = "Stable"
    result.update({
        "bb_upper": bb_upper,
        "bb_middle": bb_middle,
        "bb_lower": bb_lower,
        "bb_values": (upper_value, middle_value, lower_value),
        "bb_bandwidth": bandwidth,
        "bb_position": position,
        "bb_regime": bb_regime,
    })

    if interval in INTRADAY_INTERVALS:
        vol_close = close.resample("1D").last().dropna()
        vol_frequency = "Daily close-to-close"
        periods_per_year = annualization_periods(asset_class, "1d")
        daily_close = vol_close
    elif interval in {"1wk", "1w"}:
        vol_close = close
        vol_frequency = "Weekly close-to-close"
        periods_per_year = annualization_periods(asset_class, "1wk")
        daily_close = pd.Series(dtype=float)
    elif interval in {"1mo", "1mth"}:
        vol_close = close
        vol_frequency = "Monthly close-to-close"
        periods_per_year = annualization_periods(asset_class, "1mo")
        daily_close = pd.Series(dtype=float)
    else:
        vol_close = close
        vol_frequency = "Daily close-to-close"
        periods_per_year = annualization_periods(asset_class, "1d")
        daily_close = close

    volatility_returns = vol_close.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    period_volatility = (
        float(volatility_returns.std(ddof=1))
        if len(volatility_returns) >= 2
        else None
    )
    annualized_volatility = (
        period_volatility * math.sqrt(periods_per_year)
        if period_volatility is not None and periods_per_year is not None
        else None
    )
    daily_returns = daily_close.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    daily_volatility = (
        float(daily_returns.std(ddof=1))
        if len(daily_returns) >= 2
        else None
    )
    rolling_volatility = (
        volatility_returns.rolling(window=20, min_periods=20).std(ddof=1)
        * math.sqrt(periods_per_year)
        * 100
        if periods_per_year is not None
        else pd.Series(np.nan, index=volatility_returns.index, dtype=float)
    )
    valid_rolling = rolling_volatility.dropna()
    volatility_regime = "DATA NOT AVAILABLE"
    if len(valid_rolling) >= 11:
        baseline = valid_rolling.iloc[-21:-1]
        typical = float(baseline.median())
        current = float(valid_rolling.iloc[-1])
        if typical > 0 and current > typical * 1.25:
            volatility_regime = "Elevated / rising vs prior 20 observations"
        elif typical > 0 and current < typical * 0.75:
            volatility_regime = "Contracting vs prior 20 observations"
        else:
            volatility_regime = "Near recent 20-observation median"

    drawdown = close / close.cummax() - 1
    result.update({
        "volatility_returns": volatility_returns,
        "volatility_frequency": vol_frequency,
        "period_volatility": period_volatility,
        "daily_volatility": daily_volatility,
        "annualized_volatility": annualized_volatility,
        "rolling_volatility": rolling_volatility,
        "volatility_regime": volatility_regime,
        "drawdown": drawdown,
        "max_drawdown": _last_value(drawdown.cummin()),
    })

    component_specs = (
        ("Price vs SMA 20", result["price_vs_sma"][20], "Price above SMA 20", "Price below SMA 20"),
        ("Price vs SMA 50", result["price_vs_sma"][50], "Price above SMA 50", "Price below SMA 50"),
        ("SMA 50 vs SMA 200", (sma50 / sma200 - 1) if sma50 and sma200 else None, "SMA 50 above SMA 200", "SMA 50 below SMA 200"),
        ("RSI regime", rsi_value, "RSI 50-70", "RSI 30-50"),
        ("MACD vs signal", result["macd_values"][0] - result["macd_values"][1] if result["macd_values"][0] is not None and result["macd_values"][1] is not None else None, "MACD above signal", "MACD below signal"),
    )
    score_components = []
    for name, value, positive_evidence, negative_evidence in component_specs:
        contribution = None
        evidence = "DATA NOT AVAILABLE"
        if value is not None and math.isfinite(float(value)):
            if name == "RSI regime":
                if 50 <= float(value) < 70:
                    contribution, evidence = 1, positive_evidence
                elif 30 < float(value) < 50:
                    contribution, evidence = -1, negative_evidence
                elif value >= 70:
                    contribution, evidence = 0, "Overbought; neutral score contribution"
                elif value <= 30:
                    contribution, evidence = 0, "Oversold; neutral score contribution"
                else:
                    contribution, evidence = 0, "Neutral RSI; zero contribution"
            else:
                contribution = 1 if float(value) > 0 else -1 if float(value) < 0 else 0
                evidence = positive_evidence if contribution > 0 else negative_evidence if contribution < 0 else "Neutral; zero contribution"
        score_components.append({"rule": name, "contribution": contribution, "evidence": evidence})

    available_components = [item for item in score_components if item["contribution"] is not None]
    score = sum(item["contribution"] for item in available_components)
    score_signal = "INSUFFICIENT SIGNAL COVERAGE"
    if len(available_components) >= 3:
        ratio = score / len(available_components)
        if ratio >= 0.4:
            score_signal = "BULLISH"
        elif ratio <= -0.4:
            score_signal = "BEARISH"
        else:
            score_signal = "MIXED"
    result.update({
        "score_components": score_components,
        "score": score if len(available_components) >= 3 else None,
        "score_available": len(available_components),
        "score_signal": score_signal,
    })
    return result


def build_technical_charts(analysis, ticker, currency="quote units"):
    """Build the five responsive Plotly figures used by the TA page."""
    close = analysis["close"]
    smas = analysis["smas"]
    dates = close.index
    color = {
        "price": "#d8dee5",
        "sma20": "#c9a875",
        "sma50": "#83a8bd",
        "sma200": "#b17f7f",
        "bb": "#82969f",
        "rsi": "#90b6a2",
        "macd": "#8da7bd",
        "signal": "#c4a47c",
        "positive": "#7ea68b",
        "negative": "#ab7777",
        "volatility": "#8ba5b5",
    }

    def finish(figure, title, y_title, height=340):
        figure.update_layout(
            template="plotly_dark",
            title={"text": title, "font": {"size": 14, "color": "#d8dee5"}},
            height=height,
            autosize=True,
            paper_bgcolor="#0a0d12",
            plot_bgcolor="#0a0d12",
            font={"family": "Inter, sans-serif", "size": 10, "color": "#aab4bd"},
            margin={"l": 58, "r": 18, "t": 44, "b": 38},
            legend={"orientation": "h", "y": 1.08, "x": 0, "font": {"size": 9}},
            xaxis={"title": "Date", "showgrid": False, "rangeslider": {"visible": False}},
            yaxis={"title": y_title, "gridcolor": "rgba(140,155,170,0.12)", "zerolinecolor": "rgba(140,155,170,0.2)"},
            hovermode="x unified",
        )
        return figure

    price_figure = go.Figure()
    price_figure.add_trace(go.Scatter(x=dates, y=close, name="Close", line={"color": color["price"], "width": 1.8}))
    for window, key in ((20, "sma20"), (50, "sma50"), (200, "sma200")):
        price_figure.add_trace(go.Scatter(x=dates, y=smas[window], name=f"SMA {window}", line={"color": color[key], "width": 1.1}))
    price = finish(price_figure, f"{ticker} · Price and Moving Averages", f"Price ({currency})")

    bb_figure = go.Figure()
    bb_figure.add_trace(go.Scatter(x=dates, y=analysis["bb_lower"], name="Lower band", line={"color": "rgba(130,150,165,0.55)", "width": 0.8}, hovertemplate="Lower: %{y:.4f}<extra></extra>"))
    bb_figure.add_trace(go.Scatter(x=dates, y=analysis["bb_upper"], name="Upper band", line={"color": "rgba(130,150,165,0.55)", "width": 0.8}, fill="tonexty", fillcolor="rgba(130,150,165,0.08)", hovertemplate="Upper: %{y:.4f}<extra></extra>"))
    bb_figure.add_trace(go.Scatter(x=dates, y=analysis["bb_middle"], name="Middle (SMA 20)", line={"color": color["bb"], "width": 1.0, "dash": "dot"}))
    bb_figure.add_trace(go.Scatter(x=dates, y=close, name="Close", line={"color": color["price"], "width": 1.7}))
    bollinger = finish(bb_figure, f"{ticker} · Bollinger Bands (20, 2σ)", f"Price ({currency})")

    rsi_figure = go.Figure()
    rsi_figure.add_trace(go.Scatter(x=dates, y=analysis["rsi"], name="RSI (14)", line={"color": color["rsi"], "width": 1.5}))
    rsi_figure.add_hline(y=70, line_dash="dot", line_color="rgba(177,127,127,0.7)")
    rsi_figure.add_hline(y=50, line_dash="dot", line_color="rgba(140,155,170,0.25)")
    rsi_figure.add_hline(y=30, line_dash="dot", line_color="rgba(126,166,139,0.7)")
    rsi_figure.update_yaxes(range=[0, 100], title="RSI")
    rsi_chart = finish(rsi_figure, f"{ticker} · Relative Strength Index", "RSI (0-100)")

    macd_figure = go.Figure()
    histogram = analysis["macd_histogram"]
    macd_figure.add_trace(go.Bar(x=dates, y=histogram, name="Histogram", marker_color=[color["positive"] if value >= 0 else color["negative"] for value in histogram.fillna(0)]))
    macd_figure.add_trace(go.Scatter(x=dates, y=analysis["macd"], name="MACD", line={"color": color["macd"], "width": 1.4}))
    macd_figure.add_trace(go.Scatter(x=dates, y=analysis["macd_signal"], name="Signal", line={"color": color["signal"], "width": 1.2}))
    macd_figure.add_hline(y=0, line_color="rgba(140,155,170,0.25)")
    macd_chart = finish(macd_figure, f"{ticker} · MACD (12, 26, 9)", "MACD")

    volatility_figure = go.Figure()
    volatility_figure.add_trace(go.Scatter(x=analysis["rolling_volatility"].index, y=analysis["rolling_volatility"], name="20-observation annualized volatility", line={"color": color["volatility"], "width": 1.5}, fill="tozeroy", fillcolor="rgba(139,165,181,0.08)"))
    volatility_chart = finish(volatility_figure, f"{ticker} · Rolling Volatility", "Annualized volatility (%)")

    return {
        "price": price,
        "bollinger": bollinger,
        "rsi": rsi_chart,
        "macd": macd_chart,
        "volatility": volatility_chart,
    }


def _display_number(value, suffix="", decimals=2):
    if value is None or not math.isfinite(float(value)):
        return "DATA NOT AVAILABLE"
    return f"{float(value):,.{decimals}f}{suffix}"


def render_technical_analysis_results(
    history,
    ticker,
    asset_class,
    interval,
    currency,
    timeframe,
):
    """Render the Technical Analysis results without changing app routing."""
    import streamlit as st

    analysis = calculate_technical_analysis(history, asset_class, interval)
    if not analysis["valid"]:
        st.warning(
            "No usable historical closing-price data was returned for this "
            "security and period. Check the selected instrument or try a "
            "different timeframe. Yahoo Finance may also be temporarily unavailable."
        )
        return

    close = analysis["close"]
    latest_price = float(close.iloc[-1])
    currency = str(currency or "quote units").upper()
    st.caption(
        f"{asset_class} · {timeframe} · {analysis['volatility_frequency']} · "
        f"Quote currency: {currency}. {analysis['asset_note']}"
    )

    st.markdown("### Return Analysis")
    for row_start in (0, 2, 4):
        columns = st.columns(2)
        for column, (label, _, _) in zip(columns, RETURN_HORIZONS[row_start:row_start + 2]):
            value = analysis["returns"][label]
            column.metric(label, _display_number(value * 100 if value is not None else None, "%"))

    summary_metrics = (
        ("Latest Close", _display_number(latest_price), f"Yahoo Finance quote units: {currency}"),
        ("Cumulative Return", _display_number(analysis["cumulative_return"] * 100 if analysis["cumulative_return"] is not None else None, "%"), None),
        ("CAGR", _display_number(analysis["cagr"] * 100 if analysis["cagr"] is not None else None, "%"), None),
        ("Maximum Drawdown", _display_number(analysis["max_drawdown"] * 100 if analysis["max_drawdown"] is not None else None, "%"), None),
    )
    for row_start in (0, 2):
        columns = st.columns(2)
        for column, (label, value, help_text) in zip(columns, summary_metrics[row_start:row_start + 2]):
            column.metric(label, value, help=help_text)

    st.markdown("### Price and Trend")
    trend_columns = st.columns(2)
    trend_columns[0].metric("Trend Direction", analysis["trend"])
    trend_columns[1].metric("50 / 200 Observation Cross", analysis["sma_cross"])
    trend_rows = []
    for window in (20, 50, 200):
        average = analysis["sma_values"][window]
        relative = analysis["price_vs_sma"][window]
        if relative is None:
            relationship = "DATA NOT AVAILABLE"
        elif relative > 0:
            relationship = f"Above by {relative * 100:.2f}%"
        elif relative < 0:
            relationship = f"Below by {abs(relative) * 100:.2f}%"
        else:
            relationship = "At the average"
        trend_rows.append({
            "Indicator": f"SMA {window} ({timeframe} observations)",
            "Latest value": _display_number(average),
            "Price relationship": relationship,
        })
    st.dataframe(pd.DataFrame(trend_rows), hide_index=True, width="stretch")

    charts = build_technical_charts(analysis, ticker, currency)
    st.plotly_chart(charts["price"], width="stretch", config={"displaylogo": False, "responsive": True})

    st.markdown("### Bollinger Bands")
    upper, middle, lower = analysis["bb_values"]
    bb_columns = st.columns(4)
    bb_columns[0].metric("Upper Band", _display_number(upper))
    bb_columns[1].metric("Middle Band", _display_number(middle))
    bb_columns[2].metric("Lower Band", _display_number(lower))
    bb_columns[3].metric("Bandwidth", _display_number(analysis["bb_bandwidth"], "%"))
    st.caption(
        f"Price position: {_display_number(analysis['bb_position'], '%')} from the lower to upper band · "
        f"Band state: {analysis['bb_regime']}"
    )
    st.plotly_chart(charts["bollinger"], width="stretch", config={"displaylogo": False, "responsive": True})

    st.markdown("### Momentum")
    momentum_columns = st.columns(3)
    momentum_columns[0].metric("RSI (14)", _display_number(analysis["rsi_value"]), help="Wilder-smoothed 14-observation RSI")
    momentum_columns[1].metric("RSI State", analysis["rsi_state"])
    momentum_columns[2].metric("MACD Cross", analysis["macd_cross"])
    macd_value, macd_signal, macd_histogram = analysis["macd_values"]
    macd_rows = [
        {"Indicator": "MACD line (12, 26)", "Latest value": _display_number(macd_value, decimals=4)},
        {"Indicator": "Signal line (9)", "Latest value": _display_number(macd_signal, decimals=4)},
        {"Indicator": "Histogram", "Latest value": _display_number(macd_histogram, decimals=4)},
    ]
    st.dataframe(pd.DataFrame(macd_rows), hide_index=True, width="stretch")
    st.plotly_chart(charts["rsi"], width="stretch", config={"displaylogo": False, "responsive": True})
    st.plotly_chart(charts["macd"], width="stretch", config={"displaylogo": False, "responsive": True})

    st.markdown("### Volatility")
    volatility_columns = st.columns(3)
    volatility_columns[0].metric(
        "Period Volatility",
        _display_number(analysis["period_volatility"] * 100 if analysis["period_volatility"] is not None else None, "%"),
    )
    volatility_columns[1].metric(
        "Daily volatility",
        _display_number(analysis["daily_volatility"] * 100 if analysis["daily_volatility"] is not None else None, "%"),
    )
    volatility_columns[2].metric(
        "Annualized volatility",
        _display_number(analysis["annualized_volatility"] * 100 if analysis["annualized_volatility"] is not None else None, "%"),
        help=f"Standard deviation × square root of annual observations ({analysis['annual_sessions']} sessions for daily data). Weekly/monthly data use 52/12 observations.",
    )
    st.caption(f"Volatility regime: {analysis['volatility_regime']} · Rolling window: 20 observations")
    if analysis["rolling_volatility"].notna().any():
        st.plotly_chart(charts["volatility"], width="stretch", config={"displaylogo": False, "responsive": True})
    else:
        st.info("Rolling volatility is DATA NOT AVAILABLE until at least 20 return observations exist.")

    st.markdown("### Deterministic Signal")
    score_columns = st.columns(2)
    score_display = (
        f"{analysis['score']:+d} / {analysis['score_available']} rules"
        if analysis["score"] is not None
        else "DATA NOT AVAILABLE"
    )
    score_columns[0].metric("Technical Score", score_display)
    score_columns[1].metric("Signal", analysis["score_signal"])
    st.caption(
        "Rules: price above/below SMA 20 and SMA 50, SMA 50 above/below SMA 200, "
        "and MACD above/below signal each contribute +1/-1 (equal contributes 0). "
        "RSI contributes +1 at 50-<70, -1 at >30-<50, and 0 at <=30 or >=70. "
        "Signal is score ÷ available rules: >= +0.4 Bullish, <= -0.4 Bearish, "
        "otherwise Mixed; fewer than three available rules is insufficient coverage. "
        "Bollinger position is contextual and does not add a directional point."
    )
    score_table = pd.DataFrame([
        {
            "Rule": item["rule"],
            "Contribution": "DATA NOT AVAILABLE" if item["contribution"] is None else f"{item['contribution']:+d}",
            "Evidence": item["evidence"],
        }
        for item in analysis["score_components"]
    ])
    st.dataframe(score_table, hide_index=True, width="stretch")

    st.markdown("### Explain Calculations")
    with st.expander("Definitions, current readings, and limitations", expanded=False):
        explanations = [
            ("Returns", "For each horizon, latest close ÷ the last available close on or before the target date − 1. If history is too short or stale, the result is DATA NOT AVAILABLE. Corporate actions and quote timing can affect comparability."),
            ("Cumulative return", f"Latest close ÷ first close in the selected sample − 1. Current sample result: {_display_number(analysis['cumulative_return'] * 100 if analysis['cumulative_return'] is not None else None, '%')}. It covers only the selected timeframe."),
            ("CAGR", f"(Latest close ÷ first close)^(365.25 ÷ elapsed calendar days) − 1; shown only with at least one year of history. Current result: {_display_number(analysis['cagr'] * 100 if analysis['cagr'] is not None else None, '%')}. It smooths the path and does not represent realized annual returns."),
            ("SMA 20 / 50 / 200", "Arithmetic mean of the latest 20, 50, or 200 closing observations at the selected interval. Current relationship and values appear above. A moving average lags price and its bar count follows the selected chart interval."),
            ("Golden Cross / Death Cross", "Golden Cross: SMA 50 moves from below SMA 200 to at/above it on the latest observation. Death Cross: SMA 50 moves from above SMA 200 to at/below it. These are lagging crossover events; no event is reported unless both averages have sufficient history."),
            ("RSI (14)", f"Wilder-smoothed average gains divided by average losses over 14 observations, scaled 0–100. Current value/state: {_display_number(analysis['rsi_value'])} / {analysis['rsi_state']}. 70/30 are conventional thresholds, not reversal guarantees."),
            ("MACD", f"EMA 12 − EMA 26; the signal is a 9-observation EMA of MACD, and the histogram is MACD − signal. Current MACD crossover: {analysis['macd_cross']}. EMA values depend on available initialization history."),
            ("Bollinger Bands", f"20-observation SMA ± 2 sample standard deviations. Bandwidth is (upper − lower) ÷ |middle| × 100; position is measured from lower to upper band. Current bandwidth/state: {_display_number(analysis['bb_bandwidth'], '%')} / {analysis['bb_regime']}. Band touches can persist during trends."),
            ("Volatility and drawdown", f"Volatility is sample standard deviation of close-to-close returns; annualization multiplies by √N. Daily N is 252 for most classes, 260 for FX, and 365 for crypto; weekly/monthly bars use 52/12. Current annualized result: {_display_number(analysis['annualized_volatility'] * 100 if analysis['annualized_volatility'] is not None else None, '%')}. Drawdown is close ÷ running peak − 1; volatility does not predict future risk."),
            ("Signal score", f"Sum of the five disclosed rule contributions, each −1/0/+1. Signal uses score ÷ available rules: ≥ +0.4 is Bullish, ≤ −0.4 is Bearish, otherwise Mixed. Fewer than three available rules means insufficient coverage. It is a transparent heuristic, not a probability or forecast."),
        ]
        for title, explanation in explanations:
            st.markdown(f"**{title}.** {explanation}")

    st.caption("Price-based technical indicators are descriptive, not investment advice. No unavailable values are estimated or supplied by Gemini.")
