import unittest

from asset_capabilities import (
    DATA_STATES,
    annualization_periods,
    direct_provider_metrics,
    get_asset_capabilities,
    metric_state,
    normalize_asset_class,
    return_observation_periods,
    supports_metric,
)


class AssetCapabilityTests(unittest.TestCase):
    def test_aliases_normalize_to_the_six_canonical_classes(self):
        aliases = {
            "Equities": "EQUITY",
            "Fixed Income": "FIXED_INCOME",
            "Commodities": "COMMODITY",
            "Indices / Benchmarks": "INDEX",
            "Cryptocurrencies": "CRYPTO",
            "Currency Pair": "FX",
        }
        for raw, expected in aliases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_asset_class(raw), expected)

    def test_capabilities_do_not_apply_corporate_ratios_to_non_equities(self):
        self.assertTrue(supports_metric("EQUITY", "P/E", "fundamental_metrics"))
        for asset_class in ("FIXED_INCOME", "COMMODITY", "INDEX", "CRYPTO", "FX"):
            with self.subTest(asset_class=asset_class):
                self.assertFalse(supports_metric(asset_class, "P/E", "fundamental_metrics"))
                self.assertEqual(metric_state(asset_class, "P/E", 12, category="fundamental_metrics"), "NOT APPLICABLE")

    def test_conditional_bond_metrics_require_provider_values(self):
        self.assertTrue(supports_metric("FIXED_INCOME", "Duration", "conditional_metrics"))
        self.assertEqual(metric_state("FIXED_INCOME", "Duration", None, category="conditional_metrics"), "DATA NOT AVAILABLE")
        self.assertEqual(metric_state("FIXED_INCOME", "Duration", 5.4, category="conditional_metrics"), "AVAILABLE")

    def test_direct_instrument_fields_never_derive_values(self):
        missing = direct_provider_metrics("FIXED_INCOME", {"Close": 98.5})
        self.assertEqual(missing["Yield"], "DATA NOT AVAILABLE")
        self.assertEqual(missing["Duration"], "DATA NOT AVAILABLE")

        reported = direct_provider_metrics(
            "FIXED_INCOME",
            {"yieldToMaturity": 0.047, "effectiveDuration": 6.2, "creditRating": "AA"},
        )
        self.assertEqual(reported["Yield"], 0.047)
        self.assertEqual(reported["Duration"], 6.2)
        self.assertEqual(reported["Credit Category"], "AA")

    def test_standard_states_and_annualization(self):
        self.assertEqual(
            DATA_STATES,
            ("AVAILABLE", "DATA NOT AVAILABLE", "NOT APPLICABLE", "INSUFFICIENT HISTORY", "DATA ERROR"),
        )
        expected = {"EQUITY": 252, "FIXED_INCOME": 252, "COMMODITY": 252, "INDEX": 252, "CRYPTO": 365, "FX": 260}
        for asset_class, sessions in expected.items():
            with self.subTest(asset_class=asset_class):
                self.assertEqual(annualization_periods(asset_class), sessions)
                self.assertEqual(return_observation_periods(asset_class)["1Y"], sessions)
        self.assertEqual(annualization_periods("CRYPTO", "1wk"), 52)
        self.assertEqual(annualization_periods("FX", "1mo"), 12)
        self.assertIsNone(annualization_periods("UNKNOWN"))

    def test_history_and_error_states_are_not_conflated(self):
        self.assertEqual(metric_state("EQUITY", "Sharpe", None), "DATA NOT AVAILABLE")
        self.assertEqual(metric_state("EQUITY", "Sharpe", None, insufficient_history=True), "INSUFFICIENT HISTORY")
        self.assertEqual(metric_state("EQUITY", "Sharpe", None, data_error=True), "DATA ERROR")
        self.assertEqual(metric_state("EQUITY", "Sharpe", 0.7), "AVAILABLE")

    def test_unknown_class_has_no_equity_fallback(self):
        unknown = get_asset_capabilities("unknown category")
        self.assertEqual(unknown["asset_class"], "UNKNOWN")
        self.assertIsNone(unknown["annualization_sessions"])
        self.assertFalse(supports_metric("unknown category", "P/E"))


if __name__ == "__main__":
    unittest.main()
