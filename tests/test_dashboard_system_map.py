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
            "region": ["Asia", "Asia", "Global", "Global", "Asia", "Global", "Global"],
            "country": ["India", "India", "US", "US", "India", "US", "US"],
        }
    )

    monkeypatch.setattr(dashboard_system_map, "load_universe", lambda: df)

    details = dashboard_system_map._asset_details()
    counts = {item["key"]: item["count"] for item in details}

    assert set(counts) == {"equity", "fixed_income", "commodity", "index", "crypto", "fx"}
    assert counts["equity"] == 2
    assert counts["fixed_income"] == 1
    assert counts["commodity"] == 1
    assert counts["index"] == 1
    assert counts["crypto"] == 1
    assert counts["fx"] == 1
