import pandas as pd

import dashboard_system_map


def test_asset_details_keeps_master_universe_classes(monkeypatch):
    df = pd.DataFrame(
        {
            "asset_class": [
                "EQUITY",
                "EQUITY",
                "FIXED_INCOME",
                "COMMODITY",
                "INDEX",
                "CRYPTO",
                "FX",
            ],
            "region": [
                "Asia",
                "Asia",
                "Global",
                "Global",
                "Asia",
                "Global",
                "Global",
            ],
            "country": [
                "India",
                "India",
                "US",
                "US",
                "India",
                "US",
                "US",
            ],
        }
    )

    monkeypatch.setattr(dashboard_system_map, "load_universe", lambda: df)

    counts = dashboard_system_map._live_counts()

    assert set(counts.keys()) == {
        "Equities",
        "Fixed Income",
        "Commodities",
        "Indices / Benchmarks",
        "Cryptocurrencies",
        "FX / Currencies",
    }

    assert counts["Equities"] == 2
    assert counts["Fixed Income"] == 1
    assert counts["Commodities"] == 1
    assert counts["Indices / Benchmarks"] == 1
    assert counts["Cryptocurrencies"] == 1
    assert counts["FX / Currencies"] == 1

