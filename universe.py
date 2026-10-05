"""
MASTER YAHOO FINANCE UNIVERSE

Single source of truth for the Financial Analysis Terminal.

Every security used by the application comes from:
    yahoo_global_universe.csv

Only securities validated as usable by the discovery process are included.
"""

from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

UNIVERSE_FILE = BASE_DIR / "yahoo_global_universe.csv"


def load_universe():
    """
    Load the complete validated Yahoo Finance universe.

    Returns a DataFrame containing every usable security.
    """

    if not UNIVERSE_FILE.exists():
        raise FileNotFoundError(
            f"Universe file not found: {UNIVERSE_FILE}"
        )

    df = pd.read_csv(UNIVERSE_FILE)

    if df.empty:
        raise ValueError(
            "yahoo_global_universe.csv exists but contains no securities."
        )

    # --------------------------------------------------------
    # STANDARDISE COLUMN NAMES
    # --------------------------------------------------------

    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]

    # symbol -> ticker
    if "ticker" not in df.columns and "symbol" in df.columns:
        df = df.rename(
            columns={
                "symbol": "ticker"
            }
        )

    # --------------------------------------------------------
    # REQUIRED COLUMNS
    # --------------------------------------------------------

    required_columns = [
        "ticker",
        "name",
        "asset_class",
        "region",
        "country",
        "instrument_type",
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = ""

    # --------------------------------------------------------
    # CLEAN TEXT
    # --------------------------------------------------------

    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # --------------------------------------------------------
    # REMOVE INVALID / EMPTY TICKERS
    # --------------------------------------------------------

    df = df[
        df["ticker"].astype(str).str.strip() != ""
    ].copy()

    # --------------------------------------------------------
    # REMOVE DUPLICATE TICKERS
    # --------------------------------------------------------

    df["ticker"] = (
        df["ticker"]
        .astype(str)
        .str.strip()
    )

    df = (
        df
        .drop_duplicates(
            subset=["ticker"],
            keep="first"
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # STANDARDISE ASSET CLASS
    # --------------------------------------------------------

    df["asset_class"] = (
        df["asset_class"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    df = (
        df
        .sort_values(
            [
                "asset_class",
                "region",
                "country",
                "name",
                "ticker",
            ],
            na_position="last"
        )
        .reset_index(drop=True)
    )

    return df


def get_all_tickers():
    """Return every usable Yahoo ticker."""
    return load_universe()["ticker"].tolist()


def get_universe_names():
    """Return ticker -> security name mapping."""
    df = load_universe()

    return dict(
        zip(
            df["ticker"],
            df["name"]
        )
    )


def get_security_options(
    asset_class=None,
    region=None,
    country=None
):
    """
    Return display-ready security options from the master universe.

    Each option:
        Security Name • Ticker

    Optional filters:
        asset_class
        region
        country
    """

    df = load_universe()

    if asset_class:
        df = df[
            df["asset_class"].str.upper()
            == str(asset_class).upper().strip()
        ]

    if region:
        df = df[
            df["region"].str.upper()
            == str(region).upper().strip()
        ]

    if country:
        df = df[
            df["country"].str.upper()
            == str(country).upper().strip()
        ]

    return [
        f"{row['name']} • {row['ticker']}"
        for _, row in df.iterrows()
    ]


def get_security(ticker):
    """Return metadata for one ticker."""

    df = load_universe()

    result = df[
        df["ticker"].str.upper()
        == str(ticker).upper().strip()
    ]

    if result.empty:
        return None

    return result.iloc[0].to_dict()


def get_asset_classes():
    """Return all asset classes in the master universe."""

    df = load_universe()

    return sorted(
        df["asset_class"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


def get_regions(asset_class=None):
    """Return regions, optionally filtered by asset class."""

    df = load_universe()

    if asset_class:
        df = df[
            df["asset_class"].str.upper()
            == str(asset_class).upper().strip()
        ]

    return sorted(
        df["region"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


def get_countries(asset_class=None, region=None):
    """Return countries, optionally filtered."""

    df = load_universe()

    if asset_class:
        df = df[
            df["asset_class"].str.upper()
            == str(asset_class).upper().strip()
        ]

    if region:
        df = df[
            df["region"].str.upper()
            == str(region).upper().strip()
        ]

    return sorted(
        df["country"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


def search_universe(query, asset_class=None):
    """
    Search the master universe by security name or Yahoo ticker.

    Returns a DataFrame containing matching securities.
    """

    df = load_universe()

    if asset_class:
        df = df[
            df["asset_class"].str.upper()
            == str(asset_class).upper().strip()
        ]

    query = str(query).strip().lower()

    if not query:
        return df.copy()

    mask = (
        df["name"].str.lower().str.contains(query, regex=False, na=False)
        |
        df["ticker"].str.lower().str.contains(query, regex=False, na=False)
    )

    return df[mask].copy()


if __name__ == "__main__":

    universe = load_universe()

    print("=" * 100)
    print("MASTER YAHOO FINANCE UNIVERSE")
    print("=" * 100)

    print()
    print(f"TOTAL USABLE SECURITIES : {len(universe)}")

    print()
    print("BY ASSET CLASS")
    print("-" * 60)

    print(
        universe["asset_class"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print("BY REGION")
    print("-" * 60)

    print(
        universe
        .groupby(["asset_class", "region"])
        .size()
        .to_string()
    )

    print()
    print("=" * 100)