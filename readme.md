# Enterprise AI Agent Workflow Automation Engine

An autonomous, metadata-driven operations agent built with **LangGraph**, **LangChain**, and **Python**. The system bridges business logic maintained in enterprise spreadsheets (`Assessment_Workflows.xlsx`) with automated reasoning, parameter extraction, and deterministic execution pipelines.

---

## 📑 Table of Contents

1. [Architectural Decisions & Scalability Rationale](#architectural-decisions--scalability-rationale)
   - [1. In-Memory Preloaded Metadata Registry](#1-in-memory-preloaded-metadata-registry)
   - [2. Decoupled Semantic vs. Deterministic Separation](#2-decoupled-semantic-vs-deterministic-separation)
   - [3. Token-Efficient In-Memory Data Passing](#3-token-efficient-in-memory-data-passing)
   - [4. Strict Schema Contracts via Pydantic](#4-strict-schema-contracts-via-pydantic)
   - [5. Resilient Fallback Architecture](#5-resilient-fallback-architecture)
   - [6. Stateless, Horizontally Scalable Tooling](#6-stateless-horizontally-scalable-tooling)
2. [Workflow Execution Lifecycle](#workflow-execution-lifecycle)
3. [Repository Structure](#repository-structure)
4. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
5. [Running the Application](#running-the-application)
   - [Streamlit Operations Dashboard](#1-interactive-streamlit-ui)
   - [Interactive Terminal Console](#2-cli-interactive-mode)
   - [Automated Evaluation Suite](#3-automated-evaluation-suite)
6. [Tool Suite & Simulated Integrations](#tool-suite--simulated-integrations)
7. [Evaluation Contract & Metrics](#evaluation-contract--metrics)

---

## 🏛️ Architectural Decisions & Scalability Rationale

This project was engineered to solve the primary challenges of deploying LLMs in mission-critical enterprise environments: **cost unpredictability, execution hallucinations, tight coupling, and data serialization bottlenecks.**

```
                      User Operational Query
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │            Semantic Routing Layer            │
         │  • Maps natural text to Workflow ID (WF001)  │
         │  • Extracts query parameters into JSON       │
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │     Preloaded Excel Metadata Registry        │
         │  • Fast RAM lookup (O(1))                    │
         │  • Injects Steps, Rules & Output Format      │
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │           LangGraph State Machine            │
         │  • Valid Workflow  ──► Agent Execution Loop  │
         │  • Out-of-Scope    ──► Safe Fallback Edge    │
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │     Strict Output Contract Validation        │
         │  • Validated ExecutionResponse Model         │
         └──────────────────────────────────────────────┘
```

### 1. In-Memory Preloaded Metadata Registry
- **The Design:** On application boot, `src/workflow_registry.py` reads and parses `Assessment_Workflows.xlsx` into memory, transforming each row into a validated `WorkflowDefinition` model stored in a fast dictionary cache.
- **Why It Matters for Scalability:** 
  - **Zero Per-Request Disk I/O:** Reading spreadsheets from disk on every query introduces disk I/O contention and high latency under concurrent load. Caching the registry in RAM provides instantaneous $\mathcal{O}(1)$ lookups.
  - **Zero-Code Business Extensibility:** Non-technical operators can add new workflows, change decision thresholds, or update output schemas simply by editing the Excel file. The application reloads these rules without requiring Python code changes or redeployments.

### 2. Decoupled Semantic vs. Deterministic Separation
- **The Design:** The LLM is deployed strictly at the system boundaries:
  1. *At the Input:* Semantic intent classification and parameter extraction from natural text.
  2. *At the Output:* Report synthesis matching business requirements.
- **Why It Matters for Scalability:** Purely autonomous agents frequently hallucinate tool names, scramble step sequences, or terminate execution prematurely. By anchoring the agent's system prompt directly to the verified sequence declared in Excel, we retain natural language flexibility while enforcing strict deterministic compliance.

### 3. Token-Efficient In-Memory Data Passing
- **The Design:** File parsing and analytical calculations are carried out in Python memory using Pandas and standard data structures. Raw tables (e.g., 50+ inventory rows) are processed directly by local functions rather than repeatedly passed back and forth as large JSON blocks across LLM token contexts.
- **Why It Matters for Scalability:** 
  - **Cost Minimization:** Passing entire dataframes into prompt context windows consumes thousands of tokens per request and rapidly exhausts model rate limits.
  - **Latency Reduction:** Local in-memory filtering executes in single-digit milliseconds, eliminating multiple slow LLM API round-trips.

### 4. Strict Schema Contracts via Pydantic
- **The Design:** Every communication boundary is governed by Pydantic models:
  - `WorkflowDefinition`: Validates spreadsheet rows, parsing steps and inputs into clean lists.
  - `RoutingDecision`: Enforces structured LLM router outputs (`workflow_id`, `confidence`, `reasoning`, `parameters`).
  - `ExecutionResponse`: Standardizes the final payload returned to the UI, CLI, and evaluation runner.
- **Why It Matters for Scalability:** Eliminates runtime `KeyError` exceptions and untyped dictionary bugs, guaranteeing seamless downstream integration with external microservices, APIs, and automated test runners.

### 5. Resilient Fallback Architecture
- **The Design:** Unrecognized or out-of-scope queries (e.g., general trivia, unrelated prompts) are classified as `UNKNOWN` and diverted through a dedicated `fallback` conditional edge in the LangGraph state graph.
- **Why It Matters for Scalability:** Protects internal data and downstream systems by preventing unauthorized tool calls for ambiguous queries, terminating cleanly without wasting inference tokens.

### 6. Stateless, Horizontally Scalable Tooling
- **The Design:** All tools under `src/tools/` are stateless pure functions. They take inputs (file paths, thresholds, metrics), execute deterministic logic, and return standard dictionaries/lists.
- **Why It Matters for Scalability:** The system can be containerized into microservices or distributed across worker processes (e.g., Celery, FastStream, or AWS Lambda) without race conditions or shared state conflicts.

---

## 🔄 Workflow Execution Lifecycle

1. **Initialization:** `initialize_workflow_registry()` parses the master Excel specification, mapping triggers, inputs, steps, required tools, decision logic, and expected formats into typed models.
2. **Routing Node (`route_node`):** The user query is semantically classified against registered triggers. If matched, the workflow's business rules and step sequence are injected into the dynamic system prompt.
3. **Branching Condition (`route_edge`):**
   - **Matched:** The graph routes to the execution agent.
   - **Unmatched / `UNKNOWN`:** The graph branches to `fallback_node`, returning a rejection reason with zero tool invocations.
4. **Execution Loop:** The agent references the injected workflow steps, invoking the necessary ingestion, analysis, and integration tools.
5. **Synthesis & Packaging:** The agent synthesizes tool outputs to match the Excel `Expected_Output` specification, packaging the result into an `ExecutionResponse`.

---

## 📂 Repository Structure

```text
├── data/
│   ├── Assessment_Workflows.xlsx   # Master business workflow specification
│   ├── inventory.csv               # Inventory operational dataset
│   ├── catalog.csv                 # Product catalog benchmark dataset
│   └── vendor_prices.csv           # Vendor price quotes dataset
├── src/
│   ├── __init__.py
│   ├── config.py                   # Environment configuration & LLM provider init
│   ├── schemas.py                  # Pydantic schemas (ExecutionResponse, WorkflowDefinition)
│   ├── router.py                   # Semantic intent classification engine
│   ├── workflow_registry.py        # Excel parser and in-memory workflow cache
│   ├── agent_graph.py              # LangGraph StateGraph, ToolNode, and execution runner
│   └── tools/
│       ├── __init__.py
│       ├── ingestion_tools.py      # CSV, Excel, and JSON file ingestion
│       ├── analysis_tools.py       # Threshold checks, price variance, and catalog audits
│       └── integration_tools.py    # PO generation, notifications, exports (simulated)
├── app.py                          # Streamlit operations dashboard (Web UI)
├── main.py                         # Interactive terminal console (CLI)
├── run_eval.py                     # Automated evaluation suite & JSON reporter
├── eval_results.json               # Exported benchmark evaluation report
├── requirements.txt                # Package dependencies
├── .env.example                    # Sample environment variables
└── README.md                       # Comprehensive system documentation
```

---

## 🛠️ Prerequisites & Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AIAgentAutomation
```

### 2. Create and Activate a Virtual Environment
```bash
# macOS/Linux:
python3 -m venv myenv
source myenv/bin/activate

# Windows:
python -m venv myenv
myenv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
# LLM Provider Configuration (Groq or OpenAI)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Alternative Provider:
# OPENAI_API_KEY=sk-your-openai-key-here
# OPENAI_MODEL=gpt-4o
```

---

## 🖥️ Running the Application

### 1. Interactive Streamlit UI
Run the web dashboard for real-time workflow tracking, parameter inspection, and report rendering:
```bash
streamlit run app.py
```
- **Live Registry View:** Inspect active workflows, triggers, and expected schemas in the sidebar.
- **One-Click Test Queries:** Run preloaded sample queries directly from the UI.
- **Visual Telemetry:** Color-coded badges indicate successful executions, simulated actions, and fallback rejections.

### 2. CLI Interactive Mode
Run the terminal interface for headless operation:
```bash
python main.py
```
- Supports full terminal REPL with built-in commands (`help`, `workflows`, `clear`, `exit`).
- Clean ANSI formatting with error shielding against runtime timeouts and interrupts (`Ctrl+C`, `Ctrl+D`).

### 3. Automated Evaluation Suite
Run benchmark testing across all Excel workflows and fallback edge cases:
```bash
python run_eval.py
```
This script executes every workflow trigger from Excel, tests out-of-scope fallback resilience, displays a console scorecard, and exports a detailed report to **`eval_results.json`**.

---

## 🔧 Tool Suite & Simulated Integrations

Tools are categorized by operational function and feature comprehensive type annotations, docstrings, and error handling:

| Domain | Tool Name | Description | Error Handling |
| :--- | :--- | :--- | :--- |
| **Ingestion** | `read_csv` | Parses CSV files into structured record lists. | Path verification via `find_file`, `NaN` sanitization. |
| **Ingestion** | `read_excel` | Reads target sheets from `.xlsx`/`.xls` workbooks. | Sheet index resolution, empty sheet safety. |
| **Ingestion** | `read_json` | Reads and validates structured JSON records. | Format validation, missing file handling. |
| **Ingestion** | `filter_records` | Evaluates numeric and string comparison operators. | Graceful type coercion, missing field skipping. |
| **Analysis** | `check_threshold` | Audits numeric fields against operational cutoffs. | Numeric coercion, missing column safety. |
| **Analysis** | `compare_prices` | Computes price discrepancies and variance percentages. | Key matching (`sku`/`product_id`), zero division guard. |
| **Analysis** | `validate_catalog_data` | Audits catalogs for nulls, negative prices, and duplicate SKUs. | Safe aggregation across missing columns. |
| **Analysis** | `detect_log_anomalies` | Scans log records for `ERROR`, `TIMEOUT`, and `CRITICAL` entries. | File existence fallback, pattern matching. |
| **Integration** | `generate_restock_list` | Simulates purchase order creation for depleted stock. | Structured audit payload generation. |
| **Integration** | `send_notification` | Simulates dispatching alerts (Email/Webhook). | Non-blocking preview generation. |
| **Integration** | `export_report` | Simulates exporting structured operational findings to disk. | File extension and payload validation. |

---

## 📊 Evaluation Contract & Metrics

All operations adhere to the standardized Pydantic `ExecutionResponse` contract:

```json
{
  "selected_workflow": "WF001 - Inventory Restock Check",
  "reasoning": "Query requested restocking items with stock levels below threshold 10.",
  "steps_executed": [
    "1. Execute read_csv [SUCCESS]",
    "2. Execute check_threshold [SUCCESS]",
    "3. Execute generate_restock_list [SUCCESS]"
  ],
  "result": "### Executive Inventory Summary\n- Analyzed Items: 15 SKUs\n- Flagged for Restock: 3 SKUs (SKU-1001, SKU-1003, SKU-1007)\n- Action Taken: Restock Purchase Order Draft PO-RESTOCK-2026 created successfully."
}
```

### Core Verification Criteria Checked by `run_eval.py`:
1. **Routing Precision:** Resolves natural queries to the exact Excel `workflow_id`.
2. **Deterministic Sequence:** Executes the required tool pipeline without skipping steps.
3. **Fallback Integrity:** Confirms out-of-scope queries exit gracefully through the fallback edge without invoking external tools.
4. **Format Compliance:** Synthesizes final reports strictly according to the `Expected_Output` specification in the spreadsheet.