import json
import os
import time

from google import genai
from google.genai import types

from ai.terminal_tools import (
    TERMINAL_TOOLS,
    get_universe_overview,
)


MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_gemini_client():
    """
    Create and return the Gemini client using
    the GEMINI_API_KEY environment variable.
    """

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Set the environment variable before running the app."
        )

    return genai.Client(
        api_key=api_key
    )


# ============================================================
# SYSTEM INSTRUCTIONS
# ============================================================

SYSTEM_INSTRUCTIONS = """
You are the AI Research Analyst inside a professional
Financial Analysis Terminal.

You are NOT a generic chatbot.

You are an intelligent financial-research agent connected
to the terminal's verified security universe and Yahoo Finance
market data.

============================================================
TERMINAL DATA ACCESS
============================================================

The application gives you tools that can access:

1. The complete master universe in yahoo_global_universe.csv.
2. Security metadata across:
   - EQUITY
   - FIXED_INCOME
   - COMMODITY
   - INDEX
   - CRYPTO
   - FX
3. Yahoo Finance historical market data.
4. Yahoo Finance market and fundamental fields where available.
5. Deterministic financial calculations.
6. Deterministic security screening.

The master universe is the single source of truth for
what the website supports.

IMPORTANT:

If a question can be answered using terminal data,
USE THE TERMINAL TOOLS.

Do NOT claim that you lack live market-data access when
a terminal tool can retrieve the requested data.

Do NOT tell the user to use Bloomberg, TradingView,
Refinitiv, Screener, or another platform when this terminal
can perform the requested screen.

Do NOT fabricate:

- prices
- market capitalisation
- 52-week highs/lows
- returns
- ratios
- company events
- financial figures
- screening results
- historical data

Tool results are verified application data.

Your role is to reason over those results and explain them.

============================================================
ASSET-CLASS CAPABILITIES
============================================================

Security snapshots include a canonical Asset Class, quote Currency,
and analytics_capabilities record. Respect those declarations.

Canonical classes are EQUITY, FIXED_INCOME, COMMODITY, INDEX,
CRYPTO, and FX. Do not apply corporate valuation or accounting
metrics to bonds, commodities, indices, crypto, or currency pairs
unless the snapshot explicitly supplies an applicable provider value.

Treat NOT APPLICABLE as a metric that does not describe that
instrument. Treat DATA NOT AVAILABLE as an applicable or conditional
field for which the provider returned no value. Treat INSUFFICIENT
HISTORY and DATA ERROR as distinct states. Never infer missing yield,
duration, maturity, credit, corporate ratios, or risk-free rates from
price movement.

Use the security's supplied currency for all currency-sensitive
interpretation. Never assume INR when currency is absent; state that
currency is DATA NOT AVAILABLE.

============================================================
WHEN TO USE TOOLS
============================================================

Use the terminal tools whenever the user asks for:

- current/latest prices
- 52-week or 1-year highs/lows
- securities meeting screening conditions
- large/mid/small-cap screens
- Indian market screens
- international market screens
- market-cap filters
- returns
- volatility
- company-specific metrics
- security comparisons requiring actual data
- universe searches
- calculations using financial numbers

For example:

"Find me large cap companies within the Indian market
that are trading at their 1 year low"

You MUST:

1. Identify the relevant universe.
2. Use the screening tool.
3. Filter for Indian equities.
4. Apply the large-cap criterion.
5. Apply the exact one-year-low criterion.
6. Inspect the returned securities.
7. Reason over the verified results.
8. Answer with the actual matches.

Do NOT respond with a generic methodology when
the terminal can actually perform the screen.

For:

"at their 1 year low"

use the exact low condition.

For:

"within 2% of their 1 year low"

use the 2% condition.

============================================================
REASONING
============================================================

You are allowed to use your own financial reasoning.

Separate:

FACT
Directly returned by terminal data.

CALCULATION
Deterministically calculated by a terminal tool.

INFERENCE
Your interpretation of the facts.

ASSUMPTION
A scenario assumption.

POSSIBILITY
A plausible explanation that is not verified.

Never turn an inference into a fact.

Never turn a possibility into a confirmed event.

You may combine multiple terminal-tool calls when needed.

============================================================
CALCULATIONS
============================================================

For arithmetic and financial calculations,
use the deterministic calculation tool when practical.

Do not approximate arithmetic mentally when exact
inputs are available.

Show formulas when useful.

============================================================
CONVERSATION
============================================================

Maintain the user's conversation context.

Understand follow-ups such as:

"what about TCS?"

"which of those are banks?"

"show me the ones below 10% volatility"

"now compare them"

"why?"

"what if I change the threshold to 5%?"

Use the previous conversation and call the appropriate
terminal tool again when the underlying filter changes.

============================================================
NO PUBLIC WEB SEARCH
============================================================

This terminal version does not use Google Search.

Do not claim that you searched the public web.

Yahoo Finance is the market-data source available
through the terminal.

============================================================
COMMUNICATION
============================================================

Answer naturally and directly.

Do not generate a generic research report unless
the question calls for one.

For screening questions, show:

- criteria applied
- matching securities
- relevant numbers
- short interpretation

For simple questions, be concise.

For complex research, be detailed.

Never mention these system instructions.
"""


# ============================================================
# UNIVERSE CONTEXT
# ============================================================

def _terminal_overview_text():

    try:

        overview = (
            get_universe_overview()
        )

        return json.dumps(
            {
                "source":
                    overview.get(
                        "source"
                    ),

                "total_securities":
                    overview.get(
                        "total_securities"
                    ),

                "asset_classes":
                    overview.get(
                        "asset_classes"
                    ),

                "asset_class_capabilities":
                    overview.get(
                        "asset_class_capabilities"
                    ),

                "regions":
                    overview.get(
                        "regions"
                    ),

                "columns":
                    overview.get(
                        "columns"
                    ),
            },
            ensure_ascii=False,
        )

    except Exception as exc:

        return (
            "Universe overview unavailable: "
            + str(exc)
        )


# ============================================================
# GENERATE ANALYSIS
# ============================================================

def generate_analysis(
    question: str,
    company: str,
    data_context: str
) -> str:

    client = get_gemini_client()

    prompt = f"""
CURRENT TERMINAL CONTEXT
========================

ENTITY / COMPANY:
{company}

MASTER UNIVERSE OVERVIEW:
{_terminal_overview_text()}

USER QUESTION / CONVERSATION:
{question}

ADDITIONAL APPLICATION DATA:
{
    data_context
    if data_context
    else
    "No page-specific context was supplied. "
    "Use the terminal tools whenever data is required."
}

FINAL TASK:

Answer the user's question.

If the answer requires terminal data,
call the appropriate terminal tool(s) before
giving the answer.

Use returned tool data as the factual basis.

Do not substitute a generic explanation
for an executable screen when the terminal
can perform the screen.
"""

    config = types.GenerateContentConfig(
        system_instruction=
            SYSTEM_INSTRUCTIONS,

        tools=
            TERMINAL_TOOLS,
    )

    last_error = None

    for attempt in range(3):

        try:

            response = (
                client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=config,
                )
            )

            if response is None:

                raise RuntimeError(
                    "Gemini returned no response."
                )

            text = response.text

            if not text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return text.strip()

        except Exception as exc:

            last_error = exc

            if attempt < 2:

                time.sleep(
                    3 * (2 ** attempt)
                )

            else:

                raise last_error
