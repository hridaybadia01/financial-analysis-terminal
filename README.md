# GenAI-Powered Financial Analysis Terminal

## What this project is

This is a student project that builds a Bloomberg/OpenBB-inspired
financial analysis application. The goal is to let a user pick a
company, pull in market and financial statement data, upload annual
reports, and ask natural-language questions about a company's
performance — with every AI-generated answer backed by real,
traceable data (sources, page numbers, and the exact Python
calculation used).

The underlying system (data handling, financial calculations,
document retrieval, source tracking) is a custom implementation built
from scratch for this project, not a copy of any commercial product.

## What we are eventually building

Over the course of the project, the application will be able to:

1. Search for / select a company
2. Pull relevant financial and market data from permitted sources
3. Accept uploaded annual reports / financial documents
4. Retrieve relevant evidence from those documents
5. Calculate financial metrics using deterministic Python functions
   (never guessed by an AI model)
6. Answer natural-language financial questions
7. Use an LLM only to *interpret* verified data and evidence — never
   to invent numbers
8. Display charts and analysis in a Streamlit interface
9. Show exactly where every fact came from (source traceability)
10. Show the exact Python calculation behind every metric

This is being built in phases, one at a time, so that the project is
always in a working state.

## What Step 1 (Phase 1 — Project Foundation) accomplishes

Step 1 only sets up the skeleton of the project. At this stage there
is:

- No AI / LLM integration
- No external API calls
- No database
- No PDF processing
- No financial calculations yet

All Step 1 does is confirm that:

- The folder structure exists
- Streamlit is installed and runs correctly
- A basic page loads in the browser

Everything else will be added in later phases.

### Project structure

```
financial_analysis_terminal/
│
├── app.py                 # Streamlit entry point (run this file)
├── requirements.txt       # Python packages needed so far
├── README.md               # This file
├── .gitignore              # Files Git should not track
│
├── data/                   # Will hold sample / cached data later
├── financial_engine/       # Will hold the Python calculation functions
├── retrieval/               # Will hold document/data retrieval logic
├── ai/                     # Will hold LLM-related code
├── traceability/            # Will hold source & calculation tracking
├── tests/                   # Will hold unit tests
└── docs/                    # Will hold project documentation/notes
```

The subfolders (`financial_engine/`, `retrieval/`, `ai/`,
`traceability/`) are currently empty except for an `__init__.py` file,
which just tells Python "this folder is a package." They will be
filled in during later phases.

## How to set this up on your machine

### 1. Create a virtual environment

A virtual environment keeps this project's Python packages separate
from everything else on your computer.

**Windows:**
```
python -m venv .venv
.venv\Scripts\activate
```

**Mac / Linux:**
```
python3 -m venv .venv
source .venv/bin/activate
```

You'll know it worked because your terminal prompt will show
`(.venv)` at the start of the line.

### 2. Install the requirements

With the virtual environment activated:

```
pip install -r requirements.txt
```

This installs Streamlit, which is the only package needed so far.

### 3. Run the Streamlit application

```
streamlit run app.py
```

This should automatically open a browser tab (usually at
`http://localhost:8501`). If it doesn't open automatically, copy that
URL into your browser manually.

### 4. What you should see

A page titled **"Financial Analysis Terminal"** with the text:

> Project foundation successfully initialized.

If you see that, Step 1 is working correctly.

## Next steps

Do not build further features until Step 1 is confirmed working.
Phase 2 (the financial calculation engine) will be started only after
explicit approval.
