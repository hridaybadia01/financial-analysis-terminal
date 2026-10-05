from __future__ import annotations

"""
Financial Analysis Terminal
Premium Dashboard System Map

Presentation layer only.

The dashboard:
- reads counts from the existing master universe
- does not modify universe.py
- does not modify financial analytics
- does not modify Gemini
- does not fabricate financial data
"""

import html
import json

import streamlit as st
import streamlit.components.v1 as components

try:
    from universe import load_universe
except Exception:
    load_universe = None


ASSET_CLASSES = (
    "Equities",
    "Fixed Income",
    "Commodities",
    "Indices / Benchmarks",
    "Cryptocurrencies",
    "FX / Currencies",
)

CONFIG = {
    "Equities": {
        "label": "EQUITIES",
        "icon": "↗",
        "color": "#2da8ff",
        "summary": "Indian and international listed companies.",
        "analytics": "Fundamentals · valuation · performance · risk",
        "position": "tl",
    },
    "Fixed Income": {
        "label": "FIXED INCOME",
        "icon": "▣",
        "color": "#55d6b0",
        "summary": "Government, corporate and bond-market instruments.",
        "analytics": "Price · yield · duration · credit context",
        "position": "tc",
    },
    "Commodities": {
        "label": "COMMODITIES",
        "icon": "◆",
        "color": "#d7a85c",
        "summary": "Energy, metals and other validated commodities.",
        "analytics": "Price · returns · volatility · futures context",
        "position": "tr",
    },
    "Cryptocurrencies": {
        "label": "CRYPTOCURRENCIES",
        "icon": "₿",
        "color": "#a879ff",
        "summary": "Digital assets across the validated crypto universe.",
        "analytics": "Returns · volatility · momentum · 24/7 markets",
        "position": "bl",
    },
    "FX / Currencies": {
        "label": "FX / CURRENCIES",
        "icon": "¥€",
        "color": "#42c9d8",
        "summary": "Major and emerging-market currency pairs.",
        "analytics": "Returns · volatility · trend · relative strength",
        "position": "bc",
    },
    "Indices / Benchmarks": {
        "label": "INDICES / BENCHMARKS",
        "icon": "⌁",
        "color": "#4d8cff",
        "summary": "Indian and international market benchmarks.",
        "analytics": "Returns · trend · volatility · benchmark context",
        "position": "br",
    },
}


def _normalise(value):
    value = str(value or "").strip().upper()

    aliases = {
        "EQUITY": "Equities",
        "EQUITIES": "Equities",
        "FIXED_INCOME": "Fixed Income",
        "FIXED INCOME": "Fixed Income",
        "BOND": "Fixed Income",
        "BONDS": "Fixed Income",
        "COMMODITY": "Commodities",
        "COMMODITIES": "Commodities",
        "INDEX": "Indices / Benchmarks",
        "INDICES": "Indices / Benchmarks",
        "INDICES / BENCHMARKS": "Indices / Benchmarks",
        "CRYPTO": "Cryptocurrencies",
        "CRYPTOCURRENCY": "Cryptocurrencies",
        "CRYPTOCURRENCIES": "Cryptocurrencies",
        "FX": "FX / Currencies",
        "CURRENCY": "FX / Currencies",
        "CURRENCIES": "FX / Currencies",
        "FX / CURRENCIES": "FX / Currencies",
    }

    return aliases.get(value, str(value or "").strip())


def _live_counts():
    counts = {x: 0 for x in ASSET_CLASSES}

    try:
        if load_universe is None:
            return counts

        df = load_universe()

        if df is None or getattr(df, "empty", True):
            return counts

        column = None

        for candidate in (
            "asset_class",
            "Asset Class",
            "asset class",
            "assetClass",
        ):
            if candidate in df.columns:
                column = candidate
                break

        if column is None:
            return counts

        for value in df[column].dropna().tolist():
            asset = _normalise(value)

            if asset in counts:
                counts[asset] += 1

    except Exception:
        return counts

    return counts


def _details(counts):
    result = {}

    for asset in ASSET_CLASSES:
        cfg = CONFIG[asset]

        result[asset] = {
            "label": cfg["label"],
            "count": counts.get(asset, 0),
            "summary": cfg["summary"],
            "analytics": cfg["analytics"],
            "color": cfg["color"],
        }

    return result


def _build_html(counts):
    details = _details(counts)
    details_json = json.dumps(details, ensure_ascii=False).replace("</", "<\\/")

    total = sum(counts.values())

    nodes = []

    for asset in ASSET_CLASSES:
        cfg = CONFIG[asset]

        nodes.append(
            f"""
            <button
                class="asset {cfg['position']}"
                data-asset="{html.escape(asset)}"
                style="--accent:{cfg['color']}"
                type="button"
            >
                <span class="icon">{html.escape(cfg['icon'])}</span>

                <span class="copy">
                    <span class="title">{("INDICES /<br>BENCHMARKS" if asset == "Indices / Benchmarks" else html.escape(cfg['label']))}</span>

                    <span class="count">
                        {counts.get(asset, 0):,} SECURITIES
                    </span>

                    <span class="description">
                        {html.escape(cfg['summary'])}
                    </span>

                    <span class="open">
                        VIEW ANALYSIS →
                    </span>
                </span>
            </button>
            """
        )

    return f"""
<!doctype html>

<html>

<head>

<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
/>

<style>

* {{
    box-sizing: border-box;
}}

html,
body {{
    margin: 0;
    padding: 0;
    width: 100%;
    background: transparent;
}}

body {{
    color: #eef5fb;
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}}

.terminal {{
    position: relative;
    width: 100%;
    height: 620px;
    overflow: hidden;

    border:
        1px solid rgba(90,130,165,.24);

    border-radius: 18px;

    background:
        radial-gradient(
            circle at 50% 50%,
            rgba(21,83,126,.16),
            transparent 31%
        ),
        linear-gradient(
            180deg,
            #090e14 0%,
            #060a0f 100%
        );

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.025),
        0 20px 60px rgba(0,0,0,.25);
}}

.terminal::before {{
    content: "";

    position: absolute;
    inset: 0;

    background-image:
        linear-gradient(
            rgba(91,127,158,.045) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(91,127,158,.045) 1px,
            transparent 1px
        );

    background-size: 36px 36px;

    pointer-events: none;
}}

.header {{
    position: absolute;
    z-index: 10;

    left: 30px;
    top: 24px;
}}

.eyebrow {{
    color: #2da8ff;

    font-size: 10px;
    font-weight: 800;

    letter-spacing: .25em;
}}

.heading {{
    margin-top: 7px;

    font-size: 25px;
    font-weight: 650;

    letter-spacing: -.025em;
}}

.subtitle {{
    margin-top: 5px;

    color: #71879a;

    font-size: 11px;
}}

.status {{
    position: absolute;
    z-index: 10;

    right: 30px;
    top: 27px;

    color: #72879a;

    font-size: 9px;

    letter-spacing: .15em;
}}

.status-dot {{
    display: inline-block;

    width: 6px;
    height: 6px;

    margin-right: 7px;

    border-radius: 50%;

    background: #17d9a0;

    box-shadow:
        0 0 12px rgba(23,217,160,.8);
}}

.map {{
    position: absolute;

    inset:
        95px
        24px
        25px
        24px;
}}

.connectors {{
    position: absolute;

    left: 5%;
    top: 2%;

    width: 90%;
    height: 92%;

    z-index: 1;

    pointer-events: none;
}}

.connector {{
    fill: none;

    stroke:
        rgba(45,168,255,.28);

    stroke-width: 1.2;
}}

.connector-glow {{
    fill: none;

    stroke:
        rgba(45,168,255,.07);

    stroke-width: 5;
}}

.center {{
    position: absolute;

    z-index: 4;

    left: 50%;
    top: 50%;

    width: 250px;
    height: 250px;

    transform:
        translate(-50%, -50%);

    display: flex;

    align-items: center;
    justify-content: center;
}}

.center-ring {{
    position: absolute;

    inset: 0;

    border:
        1px solid
        rgba(45,168,255,.35);

    border-radius: 50%;

    box-shadow:
        0 0 0 14px rgba(45,168,255,.025),
        0 0 0 28px rgba(45,168,255,.015),
        0 0 55px rgba(20,100,150,.12);
}}

.center-ring::before {{
    content: "";

    position: absolute;

    inset: 25px;

    border:
        1px solid
        rgba(255,255,255,.055);

    border-radius: 50%;
}}

.center-core {{
    width: 166px;
    height: 166px;

    border-radius: 50%;

    display: flex;

    flex-direction: column;

    align-items: center;
    justify-content: center;

    text-align: center;

    background:
        radial-gradient(
            circle at 50% 35%,
            rgba(26,90,133,.24),
            transparent 62%
        ),
        rgba(5,10,15,.96);

    border:
        1px solid
        rgba(45,168,255,.36);

    box-shadow:
        inset 0 0 30px rgba(28,108,163,.10);
}}

.core-kicker {{
    color: #2da8ff;

    font-size: 8px;
    font-weight: 800;

    letter-spacing: .18em;

    margin-bottom: 10px;
}}

.core-title {{
    color: #f3f6f9;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 20px;

    line-height: 1.04;
}}

.core-online {{
    margin-top: 13px;

    color: #13dca0;

    font-size: 8px;
    font-weight: 800;

    letter-spacing: .18em;
}}

.core-total {{
    margin-top: 8px;

    color: #5d7489;

    font-size: 8px;

    letter-spacing: .11em;
}}

.asset {{
    position: absolute;

    z-index: 6;

    width: 270px;
    min-height: 112px;

    padding: 14px;

    display: flex;

    align-items: center;

    gap: 13px;

    text-align: left;

    color: #eef5fb;

    cursor: pointer;

    border:
        1px solid
        rgba(100,135,163,.23);

    border-radius: 15px;

    background:
        linear-gradient(
            145deg,
            rgba(14,22,31,.97),
            rgba(7,12,18,.98)
        );

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.025),
        0 12px 30px rgba(0,0,0,.23);

    transition:
        .18s ease;
}}

.asset:hover,
.asset:focus-visible,
.asset.active {{
    outline: none;

    transform:
        translateY(-3px);

    border-color:
        color-mix(
            in srgb,
            var(--accent) 65%,
            transparent
        );

    box-shadow:
        0 0 0 1px
        color-mix(
            in srgb,
            var(--accent) 22%,
            transparent
        ),
        0 15px 38px rgba(0,0,0,.30),
        0 0 28px
        color-mix(
            in srgb,
            var(--accent) 10%,
            transparent
        );
}}

.tl {{
    left: 1%;
    top: 3%;
}}

.tc {{
    left: 50%;
    top: 0;

    transform:
        translateX(-50%);
}}

.tc:hover,
.tc:focus-visible,
.tc.active {{
    transform:
        translateX(-50%)
        translateY(-3px);
}}

.tr {{
    right: 1%;
    top: 3%;
}}

.bl {{
    left: 1%;
    bottom: 1%;
}}

.bc {{
    left: 50%;
    bottom: 0;

    transform:
        translateX(-50%);
}}

.bc:hover,
.bc:focus-visible,
.bc.active {{
    transform:
        translateX(-50%)
        translateY(-3px);
}}

.br {{
    right: 1%;
    bottom: 1%;
}}

.icon {{
    flex: 0 0 48px;

    width: 48px;
    height: 48px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 50%;

    color: var(--accent);

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 22px;

    border:
        1px solid
        color-mix(
            in srgb,
            var(--accent) 45%,
            transparent
        );

    background:
        radial-gradient(
            circle,
            color-mix(
                in srgb,
                var(--accent) 14%,
                transparent
            ),
            rgba(5,10,15,.8)
        );
}}

.copy {{
    min-width: 0;

    display: flex;

    flex-direction: column;
}}

.title {{
    color: #eef5fb;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 15px;
    font-weight: 700;

    white-space: nowrap;
}}

.count {{
    margin-top: 4px;

    color: var(--accent);

    font-size: 8px;
    font-weight: 800;

    letter-spacing: .15em;
}}

.description {{
    margin-top: 7px;

    color: #70879a;

    font-size: 9px;

    line-height: 1.35;
}}

.open {{
    margin-top: 7px;

    color: var(--accent);

    font-size: 8px;
    font-weight: 800;

    letter-spacing: .11em;
}}

.drawer-backdrop {{
    position: absolute;

    z-index: 20;

    inset: 0;

    display: none;

    background:
        rgba(2,5,8,.66);

    backdrop-filter:
        blur(4px);
}}

.drawer-backdrop.open {{
    display: block;
}}

.drawer {{
    position: absolute;

    z-index: 30;

    top: 18px;
    right: 18px;
    bottom: 18px;

    width:
        min(
            390px,
            calc(100% - 36px)
        );

    padding: 24px;

    overflow-y: auto;

    border:
        1px solid
        rgba(80,131,172,.28);

    border-radius: 16px;

    background:
        linear-gradient(
            160deg,
            rgba(13,22,31,.99),
            rgba(6,11,16,.99)
        );

    box-shadow:
        -25px 0 70px
        rgba(0,0,0,.45);

    transform:
        translateX(
            calc(100% + 30px)
        );

    transition:
        transform .24s ease;
}}

.drawer.open {{
    transform:
        translateX(0);
}}

.close {{
    position: absolute;

    right: 13px;
    top: 13px;

    width: 30px;
    height: 30px;

    border:
        1px solid
        rgba(130,160,185,.2);

    border-radius: 8px;

    color: #9db0c0;

    background:
        rgba(255,255,255,.025);

    cursor: pointer;
}}

.drawer-kicker {{
    color: #2da8ff;

    font-size: 8px;
    font-weight: 800;

    letter-spacing: .2em;
}}

.drawer-title {{
    margin-top: 7px;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 27px;
}}

.drawer-count {{
    margin-top: 5px;

    color: #8196a9;

    font-size: 9px;

    letter-spacing: .15em;
}}

.drawer-summary {{
    margin-top: 18px;

    color: #a8b7c5;

    font-size: 12px;

    line-height: 1.55;
}}

.drawer-section {{
    margin-top: 22px;
}}

.drawer-heading {{
    color: #eaf3f9;

    font-size: 9px;
    font-weight: 800;

    letter-spacing: .14em;
}}

.row {{
    margin-top: 9px;

    padding: 11px;

    border:
        1px solid
        rgba(100,135,163,.15);

    border-radius: 10px;

    background:
        rgba(255,255,255,.018);
}}

.row-title {{
    color: #eaf3f9;

    font-size: 10px;
    font-weight: 700;
}}

.row-body {{
    margin-top: 4px;

    color: #71879a;

    font-size: 9px;

    line-height: 1.4;
}}

.footer {{
    position: absolute;

    z-index: 8;

    left: 50%;
    bottom: 11px;

    transform:
        translateX(-50%);

    color: #526b80;

    font-size: 7px;

    letter-spacing: .11em;

    white-space: nowrap;
}}

@media (max-width: 1000px) {{

    .asset {{
        width: 235px;
    }}

    .center {{
        transform:
            translate(-50%, -50%)
            scale(.88);
    }}

    .tl,
    .bl {{
        left: 0;
    }}

    .tr,
    .br {{
        right: 0;
    }}
}}

@media (max-width: 820px) {{

    .terminal {{
        height: 700px;

        overflow-y: auto;
    }}

    .map {{
        inset:
            85px
            15px
            30px;

        display: grid;

        grid-template-columns:
            1fr 1fr;

        grid-template-rows:
            repeat(3, 1fr);

        gap: 10px;
    }}

    .connectors,
    .center {{
        display: none;
    }}

    .asset {{
        position: relative;

        inset: auto !important;

        width: auto;

        min-height: 120px;

        transform: none !important;
    }}

    .tl {{
        grid-column: 1;
        grid-row: 1;
    }}

    .tc {{
        grid-column: 2;
        grid-row: 1;
    }}

    .tr {{
        grid-column: 1;
        grid-row: 2;
    }}

    .bl {{
        grid-column: 2;
        grid-row: 2;
    }}

    .bc {{
        grid-column: 1;
        grid-row: 3;
    }}

    .br {{
        grid-column: 2;
        grid-row: 3;
    }}

    .footer {{
        display: none;
    }}
}}

@media (max-width: 540px) {{

    .terminal {{
        height: 830px;
    }}

    .map {{
        grid-template-columns: 1fr;

        grid-template-rows:
            repeat(6, auto);
    }}

    .asset {{
        grid-column: 1 !important;

        grid-row: auto !important;

        min-height: 105px;
    }}

    .title {{
        font-size: 14px;
    }}
}}



/* FINAL_DASHBOARD_CONTAINMENT_V4 */

/* ============================================================
   CLEAN TEXT CONTAINMENT
   IMPORTANT:
   Existing dashboard positioning is NOT changed.
   Existing node widths are NOT changed.
   Only text containment is repaired.
   ============================================================ */

.asset-node {{
    min-width: 0;
    max-width: 100%;
    box-sizing: border-box;
}}


/* ============================================================
   EXISTING COPY AREA
   ============================================================ */

.asset-copy {{
    min-width: 0 !important;
    max-width: 205px !important;

    box-sizing: border-box !important;

    overflow: hidden !important;
}}


/* ============================================================
   ASSET NAME
   ============================================================ */

.asset-name {{

    min-width: 0 !important;
    max-width: 205px !important;

    box-sizing: border-box !important;

    white-space: normal !important;

    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    text-overflow: clip !important;

    height: auto !important;
    max-height: none !important;

    overflow: hidden !important;

    line-height: 1.25 !important;
}}


/* ============================================================
   SECURITY COUNT
   ============================================================ */

.asset-count {{

    min-width: 0 !important;
    max-width: 205px !important;

    box-sizing: border-box !important;

    white-space: normal !important;

    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    text-overflow: clip !important;

    height: auto !important;
    max-height: none !important;

    overflow: hidden !important;
}}


/* ============================================================
   DESCRIPTION
   ============================================================ */

.asset-extension {{

    min-width: 0 !important;
    max-width: 205px !important;

    box-sizing: border-box !important;

    white-space: normal !important;

    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    text-overflow: clip !important;

    height: auto !important;
    max-height: none !important;

    overflow: hidden !important;

    line-height: 1.45 !important;
}}


/* ============================================================
   DETAILS LINK
   ============================================================ */

.detail-link {{

    min-width: 0 !important;
    max-width: 205px !important;

    box-sizing: border-box !important;

    white-space: normal !important;

    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    text-overflow: clip !important;

    height: auto !important;
    max-height: none !important;

    overflow: hidden !important;
}}


/* ============================================================
   DRAWER
   ============================================================ */

.drawer {{

    box-sizing: border-box !important;

    min-width: 0 !important;
    max-width: 100% !important;

    overflow-y: auto !important;
    overflow-x: hidden !important;
}}


/* ============================================================
   DRAWER CONTENT
   ============================================================ */

.drawer * {{

    min-width: 0 !important;
    max-width: 100% !important;

    box-sizing: border-box !important;

    white-space: normal !important;

    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    text-overflow: clip !important;
}}


/* END_FINAL_DASHBOARD_CONTAINMENT_V4 */



/* FINAL_DASHBOARD_CONTAINMENT_V5 */

/* ============================================================
   FINAL DASHBOARD TEXT CONTAINMENT

   Do NOT change:
   - node positions
   - card geometry
   - icon positions
   - connector lines
   - dashboard structure

   Only constrain the text copy area so long titles cannot
   escape the existing card.
   ============================================================ */


/* ============================================================
   ALL ASSET NODES
   ============================================================ */

.asset-node {{
    min-width: 0 !important;
    box-sizing: border-box !important;
}}


/* ============================================================
   ALL COPY CONTAINERS
   ============================================================ */

.asset-copy {{
    min-width: 0 !important;

    box-sizing: border-box !important;

    overflow: hidden !important;
}}


/* ============================================================
   RIGHT-SIDE ASSET CARDS

   Commodities and Indices / Benchmarks are row-reversed.
   Give their copy area an explicit flex basis so the browser
   cannot size it from the intrinsic title width.
   ============================================================ */

.asset-node.co .asset-copy,
.asset-node.ix .asset-copy {{
    width: 190px !important;

    min-width: 0 !important;
    max-width: 190px !important;

    flex: 0 1 190px !important;

    box-sizing: border-box !important;

    overflow: hidden !important;
}}


/* ============================================================
   RIGHT-SIDE TITLES
   ============================================================ */

.asset-node.co .asset-name,
.asset-node.ix .asset-name {{
    width: 100% !important;

    min-width: 0 !important;
    max-width: 100% !important;

    box-sizing: border-box !important;

    white-space: normal !important;

    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    text-overflow: clip !important;

    overflow: hidden !important;

    height: auto !important;
    max-height: none !important;

    line-height: 1.18 !important;

    font-size: 11px !important;
}}


/* ============================================================
   RIGHT-SIDE COUNTS / DESCRIPTIONS / LINKS
   ============================================================ */

.asset-node.co .asset-count,
.asset-node.co .asset-extension,
.asset-node.co .detail-link,

.asset-node.ix .asset-count,
.asset-node.ix .asset-extension,
.asset-node.ix .detail-link {{
    width: 100% !important;

    min-width: 0 !important;
    max-width: 100% !important;

    box-sizing: border-box !important;

    white-space: normal !important;

    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    text-overflow: clip !important;

    overflow: hidden !important;

    height: auto !important;
    max-height: none !important;
}}


/* ============================================================
   SPECIFIC INDICES / BENCHMARKS SAFETY
   ============================================================ */

.asset-node.ix {{
    min-width: 0 !important;
    box-sizing: border-box !important;
}}

.asset-node.ix .asset-copy {{
    text-align: right !important;
    align-items: flex-end !important;
}}


/* ============================================================
   OTHER ASSET NAMES
   ============================================================ */

.asset-name,
.asset-count,
.asset-extension,
.detail-link {{
    min-width: 0 !important;

    box-sizing: border-box !important;

    white-space: normal !important;

    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    text-overflow: clip !important;

    height: auto !important;
    max-height: none !important;

    overflow: hidden !important;
}}


/* ============================================================
   DRAWER
   ============================================================ */

.drawer {{
    min-width: 0 !important;
    max-width: 100% !important;

    box-sizing: border-box !important;

    overflow-x: hidden !important;
    overflow-y: auto !important;
}}

.drawer * {{
    min-width: 0 !important;
    max-width: 100% !important;

    box-sizing: border-box !important;

    white-space: normal !important;

    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    text-overflow: clip !important;
}}


/* END_FINAL_DASHBOARD_CONTAINMENT_V5 */



/* FINAL_INDICES_TITLE_CONTAINMENT */

/*
   FINAL MICRO-FIX:
   Only the INDICES / BENCHMARKS title is adjusted.
   No card position, card size, icon, connector, or layout changes.
*/

.asset-node.ix .asset-name {{
    display: block !important;

    width: 150px !important;
    min-width: 0 !important;
    max-width: 150px !important;

    box-sizing: border-box !important;

    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    overflow: hidden !important;
    text-overflow: clip !important;

    height: auto !important;
    max-height: none !important;

    font-size: 10px !important;
    line-height: 1.15 !important;

    margin-left: auto !important;
    margin-right: 0 !important;
}}

/* END_FINAL_INDICES_TITLE_CONTAINMENT */

</style>
</head>

<body>

<div class="terminal">

    <div class="header">
        <div class="eyebrow">DASHBOARD</div>

        <div class="heading">
            Financial Analysis Terminal
        </div>

        <div class="subtitle">
            Live market overview · multi-asset intelligence · unified analysis
        </div>
    </div>

    <div class="status">
        <span class="status-dot"></span>
        SYSTEM ONLINE
    </div>

    <div class="map">

        <svg
            class="connectors"
            viewBox="0 0 1000 450"
            preserveAspectRatio="none"
            aria-hidden="true"
        >

            <path
                class="connector-glow"
                d="M250 92 C365 110, 410 165, 500 225"
            />

            <path
                class="connector"
                d="M250 92 C365 110, 410 165, 500 225"
            />

            <path
                class="connector-glow"
                d="M500 65 C500 125, 500 170, 500 225"
            />

            <path
                class="connector"
                d="M500 65 C500 125, 500 170, 500 225"
            />

            <path
                class="connector-glow"
                d="M750 92 C635 110, 590 165, 500 225"
            />

            <path
                class="connector"
                d="M750 92 C635 110, 590 165, 500 225"
            />

            <path
                class="connector-glow"
                d="M250 358 C365 340, 410 290, 500 225"
            />

            <path
                class="connector"
                d="M250 358 C365 340, 410 290, 500 225"
            />

            <path
                class="connector-glow"
                d="M500 385 C500 325, 500 280, 500 225"
            />

            <path
                class="connector"
                d="M500 385 C500 325, 500 280, 500 225"
            />

            <path
                class="connector-glow"
                d="M750 358 C635 340, 590 290, 500 225"
            />

            <path
                class="connector"
                d="M750 358 C635 340, 590 290, 500 225"
            />

        </svg>

        <div class="center">

            <div class="center-ring"></div>

            <div class="center-core">

                <div class="core-kicker">
                    GLOBAL MARKET INTELLIGENCE
                </div>

                <div class="core-title">
                    FINANCIAL<br>
                    ANALYSIS<br>
                    TERMINAL
                </div>

                <div class="core-online">
                    SYSTEM ONLINE
                </div>

                <div class="core-total">
                    {total:,} INSTRUMENTS · 6 ASSET CLASSES
                </div>

            </div>

        </div>

        {''.join(nodes)}

    </div>

    <div class="footer">
        YAHOO FINANCE DATA · MASTER UNIVERSE · DATA → ANALYTICS → INTERPRETATION
    </div>

    <div
        class="drawer-backdrop"
        id="backdrop"
    ></div>

    <aside
        class="drawer"
        id="drawer"
        aria-hidden="true"
    >

        <button
            class="close"
            id="closeButton"
            type="button"
        >
            ×
        </button>

        <div class="drawer-kicker">
            ASSET CLASS
        </div>

        <div
            class="drawer-title"
            id="drawerTitle"
        >
            Equities
        </div>

        <div
            class="drawer-count"
            id="drawerCount"
        ></div>

        <div
            class="drawer-summary"
            id="drawerSummary"
        ></div>

        <div class="drawer-section">

            <div class="drawer-heading">
                ANALYTICS AVAILABLE
            </div>

            <div class="row">
                <div class="row-title">
                    Data
                </div>

                <div
                    class="row-body"
                    id="dataRow"
                >
                    Master Yahoo Finance universe
                </div>
            </div>

            <div class="row">
                <div class="row-title">
                    Processing
                </div>

                <div
                    class="row-body"
                    id="processingRow"
                >
                    Validation and normalization
                </div>
            </div>

            <div class="row">
                <div class="row-title">
                    Analytics
                </div>

                <div
                    class="row-body"
                    id="analyticsRow"
                ></div>
            </div>

            <div class="row">
                <div class="row-title">
                    Interpretation
                </div>

                <div
                    class="row-body"
                    id="interpretationRow"
                >
                    Financial analysis and AI-assisted interpretation
                </div>
            </div>

        </div>

    </aside>

</div>

<script>

const DETAILS = __DETAILS__;

const drawer =
    document.getElementById("drawer");

const backdrop =
    document.getElementById("backdrop");

const closeButton =
    document.getElementById("closeButton");

const drawerTitle =
    document.getElementById("drawerTitle");

const drawerCount =
    document.getElementById("drawerCount");

const drawerSummary =
    document.getElementById("drawerSummary");

const dataRow =
    document.getElementById("dataRow");

const processingRow =
    document.getElementById("processingRow");

const analyticsRow =
    document.getElementById("analyticsRow");

const interpretationRow =
    document.getElementById("interpretationRow");


function closeDrawer() {{

    drawer.classList.remove("open");

    backdrop.classList.remove("open");

    drawer.setAttribute(
        "aria-hidden",
        "true"
    );

    document
        .querySelectorAll(".asset")
        .forEach(function(node) {{
            node.classList.remove("active");
        }});
}}


function openDrawer(assetName, node) {{

    const item =
        DETAILS[assetName];

    if (!item) {{
        return;
    }}

    drawerTitle.textContent =
        item.label;

    drawerCount.textContent =
        item.count.toLocaleString()
        + " SECURITIES";

    drawerSummary.textContent =
        item.summary;

    analyticsRow.textContent =
        item.analytics;

    document
        .querySelectorAll(".asset")
        .forEach(function(element) {{
            element.classList.remove("active");
        }});

    if (node) {{
        node.classList.add("active");
    }}

    drawer.classList.add("open");

    backdrop.classList.add("open");

    drawer.setAttribute(
        "aria-hidden",
        "false"
    );
}}


document
    .querySelectorAll(".asset")
    .forEach(function(node) {{

        node.addEventListener(
            "click",
            function(event) {{

                event.preventDefault();

                event.stopPropagation();

                openDrawer(
                    node.getAttribute(
                        "data-asset"
                    ),
                    node
                );
            }}
        );
    }});


backdrop.addEventListener(
    "click",
    closeDrawer
);


closeButton.addEventListener(
    "click",
    closeDrawer
);


document.addEventListener(
    "keydown",
    function(event) {{

        if (event.key === "Escape") {{
            closeDrawer();
        }}
    }}
);

</script>

</body>

</html>
""".replace("__DETAILS__", details_json)


def render_dashboard_system_map(*args, **kwargs):

    counts = _live_counts()

    components.html(
        _build_html(counts),
        height=625,
        scrolling=False,
    )


# Existing app.py compatibility aliases.
render_system_map = render_dashboard_system_map
render_dashboard_map = render_dashboard_system_map
dashboard_system_map = render_dashboard_system_map



