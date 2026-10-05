import unittest

import numpy as np
import pandas as pd

from technical_analysis import (
    build_technical_charts,
    calculate_technical_analysis,
)


class TechnicalAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.index = pd.date_range("2023-01-02", periods=520, freq="B")
        returns = np.sin(np.arange(len(self.index)) / 13) * 0.004 + 0.0003
        close = 100 * np.cumprod(1 + returns)
        self.history = pd.DataFrame({"Close": close}, index=self.index)

    def test_horizons_trend_and_indicators_are_available_with_history(self):
        result = calculate_technical_analysis(self.history, "EQUITY", "1d")

        self.assertTrue(result["valid"])
        self.assertTrue(all(value is not None for value in result["returns"].values()))
        self.assertIsNotNone(result["cagr"])
        self.assertIsNotNone(result["sma_values"][200])
        self.assertIsNotNone(result["rsi_value"])
        self.assertTrue(all(value is not None for value in result["macd_values"]))
        self.assertTrue(all(value is not None for value in result["bb_values"]))
        self.assertIsNotNone(result["score"])

    def test_short_history_marks_unsupported_values_unavailable(self):
        result = calculate_technical_analysis(self.history.iloc[:12], "EQUITY", "1d")

        self.assertIsNone(result["returns"]["1Y"])
        self.assertIsNone(result["cagr"])
        self.assertIsNone(result["sma_values"][20])
        self.assertIsNone(result["sma_values"][200])
        self.assertIsNone(result["score"])
        self.assertEqual(result["score_signal"], "INSUFFICIENT SIGNAL COVERAGE")

    def test_rsi_handles_one_directional_and_flat_series(self):
        rising = pd.DataFrame(
            {"Close": np.arange(1, 81, dtype=float)},
            index=pd.date_range("2024-01-01", periods=80, freq="B"),
        )
        flat = rising.copy()
        flat["Close"] = 10.0

        self.assertEqual(calculate_technical_analysis(rising, "EQUITY")["rsi_value"], 100.0)
        self.assertEqual(calculate_technical_analysis(flat, "EQUITY")["rsi_value"], 50.0)

    def test_asset_class_annualization_and_weekly_frequency(self):
        expected = {"EQUITY": 252, "INDEX": 252, "CRYPTO": 365, "FX": 260, "COMMODITY": 252, "FIXED_INCOME": 252}
        for asset_class, periods in expected.items():
            with self.subTest(asset_class=asset_class):
                result = calculate_technical_analysis(self.history, asset_class, "1d")
                self.assertEqual(result["annual_sessions"], periods)
                self.assertIsNotNone(result["annualized_volatility"])

        weekly = calculate_technical_analysis(self.history, "EQUITY", "1wk")
        self.assertEqual(weekly["volatility_frequency"], "Weekly close-to-close")
        self.assertEqual(weekly["annualized_volatility"], weekly["period_volatility"] * np.sqrt(52))
        self.assertIsNone(weekly["daily_volatility"])

    def test_score_is_deterministic_and_bollinger_is_not_directional_score(self):
        first = calculate_technical_analysis(self.history, "EQUITY", "1d")
        second = calculate_technical_analysis(self.history.copy(), "EQUITY", "1d")

        self.assertEqual(first["score"], second["score"])
        self.assertEqual(first["score_components"], second["score_components"])
        self.assertNotIn("Bollinger", " ".join(item["rule"] for item in first["score_components"]))

    def test_empty_data_is_safe_and_charts_are_complete(self):
        empty = calculate_technical_analysis(pd.DataFrame(), "CRYPTO")
        self.assertFalse(empty["valid"])
        self.assertEqual(empty["score_signal"], "DATA NOT AVAILABLE")

        result = calculate_technical_analysis(self.history, "EQUITY", "1d")
        charts = build_technical_charts(result, "TEST", "USD")
        self.assertEqual(set(charts), {"price", "bollinger", "rsi", "macd", "volatility"})
        self.assertTrue(all(len(figure.data) > 0 for figure in charts.values()))


if __name__ == "__main__":
    unittest.main()
