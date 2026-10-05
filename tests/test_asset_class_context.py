import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from ai import terminal_tools


class AssetClassContextTests(unittest.TestCase):
    def test_snapshot_marks_fixed_income_corporate_metrics_inapplicable(self):
        with patch.object(terminal_tools, "_history_snapshot", return_value={"current_price": 90.0}), patch.object(
            terminal_tools,
            "_market_info",
            return_value={"trailingPE": None, "yieldToMaturity": None, "duration": None},
        ):
            result = terminal_tools.get_security_snapshot("TLT")

        self.assertEqual(result["asset_class"], "FIXED_INCOME")
        self.assertEqual(result["currency"], "USD")
        self.assertEqual(result["fundamentals"]["corporate_metrics"], "NOT APPLICABLE")
        self.assertEqual(result["fundamentals"]["direct_instrument_fields"]["Yield"], "DATA NOT AVAILABLE")
        self.assertEqual(result["fundamentals"]["direct_instrument_fields"]["Duration"], "DATA NOT AVAILABLE")

    def test_snapshot_keeps_equity_fields_and_real_currency(self):
        with patch.object(terminal_tools, "_history_snapshot", return_value={"current_price": 100.0}), patch.object(
            terminal_tools,
            "_market_info",
            return_value={"trailingPE": 18.0, "returnOnEquity": None},
        ):
            result = terminal_tools.get_security_snapshot("AAPL")

        self.assertEqual(result["asset_class"], "EQUITY")
        self.assertEqual(result["currency"], "USD")
        self.assertEqual(result["fundamentals"]["data"]["trailingPE"], 18.0)
        self.assertEqual(result["fundamentals"]["data"]["returnOnEquity"], "DATA NOT AVAILABLE")

    def test_snapshot_does_not_apply_corporate_metrics_to_crypto_or_fx(self):
        for ticker, asset_class in (("BTC-USD", "CRYPTO"), ("EURUSD=X", "FX"), ("GC=F", "COMMODITY"), ("^NSEI", "INDEX")):
            with self.subTest(ticker=ticker):
                with patch.object(terminal_tools, "_history_snapshot", return_value="DATA NOT AVAILABLE"), patch.object(
                    terminal_tools,
                    "_market_info",
                    return_value={"trailingPE": 0, "market_cap": None},
                ):
                    result = terminal_tools.get_security_snapshot(ticker)
                self.assertEqual(result["asset_class"], asset_class)
                self.assertEqual(result["fundamentals"]["corporate_metrics"], "NOT APPLICABLE")
                if asset_class == "CRYPTO":
                    self.assertEqual(result["fundamentals"]["market_cap"], "DATA NOT AVAILABLE")

    def test_search_accepts_class_aliases_and_returns_master_currency(self):
        result = terminal_tools.search_terminal_universe(asset_class="fixed income", limit=2)
        self.assertGreater(result["returned"], 0)
        self.assertTrue(all(row["asset_class"] == "FIXED_INCOME" for row in result["securities"]))
        self.assertTrue(all("currency" in row for row in result["securities"]))

    def test_history_snapshot_uses_class_annualization_periods(self):
        dates = pd.date_range("2024-01-01", periods=400, freq="D")
        returns = np.linspace(-0.004, 0.005, len(dates))
        prices = 100 * np.cumprod(1 + returns)
        history = pd.DataFrame({"Close": prices}, index=dates)

        class FakeTicker:
            def history(self, **kwargs):
                return history

        expected_daily_std = history["Close"].pct_change().dropna().std() * 100
        with patch.object(terminal_tools.yf, "Ticker", return_value=FakeTicker()):
            terminal_tools._history_snapshot.cache_clear()
            crypto = terminal_tools._history_snapshot("BTC-USD")
            equity = terminal_tools._history_snapshot("AAPL")
            terminal_tools._history_snapshot.cache_clear()

        self.assertEqual(crypto["annualization_sessions"], 365)
        self.assertEqual(equity["annualization_sessions"], 252)
        self.assertAlmostEqual(crypto["annualized_volatility_pct"], expected_daily_std * np.sqrt(365), places=8)
        self.assertAlmostEqual(equity["annualized_volatility_pct"], expected_daily_std * np.sqrt(252), places=8)
        self.assertIn("technical_metrics", crypto)
        self.assertIn("risk_metrics", crypto)


if __name__ == "__main__":
    unittest.main()
