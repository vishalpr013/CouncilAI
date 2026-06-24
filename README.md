# CouncilAI - Agentic Investment Research Committee

CouncilAI is a multi-agent equity analysis platform built with **FastAPI** (Python) and **React JS** (Vite + Tailwind CSS). It orchestrates a consensus-driven committee of specialized agents using **LangGraph** to perform real-time financial ingestion, deterministic Discounted Cash Flow (DCF) modeling, qualitative risk audits, and synthesis reporting.

---

## 1. Project Architecture & Flow

```
                      User Question (e.g. "Should I buy Apple?")
                                         │
                                         ▼
                               [FastAPI WebSocket Gateway]
                                         │
                                         ▼
                            [LangGraph Agent Committee]
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
         [1. Researcher Agent]                          [2. Valuation Analyst]
         * Extracts Ticker (using Gemini)               * Runs Programmatic DCF Model
         * Ingests Financial Statements (yfinance)      * Validates Valuation Multiples
         * Gathers News & Web Search (DuckDuckGo)        * Summarizes Intrinsic Value Targets
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                              [3. Moat & Risk Critic]
                              * Pokes holes in the bull case
                              * Audits balance sheet debt & interest sensitivity
                              * Performs competitive advantage (Moat) check
                                         │
                                         ▼
                            [4. Committee Chair / Reporter]
                            * Reconciles Researcher, Analyst & Critic outputs
                            * Synthesizes findings into unified consensus report
                                         │
                                         ▼
                         [Interactive React JS Dashboard]
                         * Real-time WebSocket Node Execution Tracker
                         * ApexCharts Financial Visualization
                         * Live Draggable DCF Assumption Recalculation
```

---

## 2. Repository Structure

The project has been organized into a clean monorepo layout:

```
CouncilAI/
├── backend/
│   ├── app/
│   │   ├── agents/            # Individual agent node logics
│   │   │   ├── researcher.py  # Ingests market news & financial statements
│   │   │   ├── analyst.py     # Computes valuation using DCF tool
│   │   │   ├── critic.py      # Challenges margins, moats, and debt levels
│   │   │   └── reporter.py    # Merges thesis, consensus, and final report
│   │   ├── graph/
│   │   │   ├── builder.py     # Compiles the LangGraph workflow graph
│   │   │   └── state.py       # Defines multi-agent shared state schema
│   │   ├── llm/
│   │   │   └── gemini.py      # LLM configuration (Gemini 2.5 Flash)
│   │   └── tools/
│   │       ├── financials.py  # Programmatic yfinance data extractor & DCF model
│   │       └── search.py      # DuckDuckGo search integration for latest news
│   ├── server.py              # FastAPI endpoint router & WebSocket broadcaster
│   └── requirements.txt       # Python environment dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # React Dashboard UI (Tailwind CSS)
│   │   ├── index.css          # Tailwind imports & custom typographic overrides
│   │   └── main.jsx           # Vite application entry point
│   ├── tailwind.config.js     # Warm minimalist color & font configurations
│   └── postcss.config.js      # PostCSS configuration for Tailwind v4
│
└── devmind_plan.md            # Startup design plan for DevMind (AI Pair Programmer)
```

---

## 3. Engineering Details & Development Flow

This application is built to address typical LLM reasoning flaws (e.g. calculation hallucinations and outdated training sets) by introducing **hybrid agentic engineering**:

### Step 1: Programmatic Tool Grounding
* **No LLM Math:** LLMs are notorious for hallucinating financial calculations. We implemented a deterministic calculation engine (`backend/app/tools/financials.py`) to run a Discounted Cash Flow model. The Valuation Agent reads the output variables of this script rather than estimating values itself.
* **Real-time Ingestion:** The `Researcher` agent extracts the ticker symbol using a dedicated extraction prompt and uses `yfinance` to grab actual, active SEC balance sheets, income statements, and cash flows.

### Step 2: Adversarial Debate Orchestration (LangGraph)
* Using **LangGraph**, the execution state flows through a compiled DAG. The `Critic` node is intentionally designed with an adversarial prompt to challenge the `Analyst`'s valuation model. This ensures a balanced, non-hallucinated report containing realistic risks.

### Step 3: Real-Time UI Streaming
* During analysis, the backend communicates with the React frontend via a **WebSocket pipeline** (`ws://127.0.0.1:8000/ws`).
* As each LangGraph node completes, it pushes partial state updates to the UI, enabling a visual progress graph that lets the user track the active agent.

### Step 4: Interactive Recalculation (Human-in-the-Loop)
* On the frontend dashboard, the user is presented with draggable range sliders for Revenue Growth Rate, WACC (Discount Rate), Terminal Multiples, and Margin of Safety.
* Modifying these sliders immediately shoots a request to the FastAPI `/api/dcf-recalculate` endpoint, re-running the python DCF calculation instantly to modify the intrinsic value target without having to re-run the entire LLM agent committee.

---

## 4. Setup & Running Instructions

### Backend Setup
1. Navigate to `/backend`.
2. Activate your virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your environment variables in `backend/.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
4. Start the FastAPI server:
   ```bash
   python server.py
   ```
   *The API will be available at http://127.0.0.1:8000.*

### Frontend Setup
1. Navigate to `/frontend`.
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the local development server:
   ```bash
   npm run dev
   ```
   *The frontend dashboard will run at http://localhost:5173.*
