# Enterprise AI Agent Workflow Automation Engine

A Python project that uses **LangGraph, LangChain, and an LLM** to run
business workflows defined in an Excel file.

The user describes a task in normal language. The system identifies the
matching workflow, reads its rules from Excel, calls the required tools,
and returns a result. If the request does not match a supported
workflow, the system uses a fallback response.

## How It Works

1.  **User request:** The user asks for an operation, such as checking
    low-stock products.
2.  **Workflow selection:** The LLM matches the request to a workflow ID
    in the Excel file and extracts relevant details.
3.  **Workflow configuration:** The application loads the selected
    workflow's steps, rules, tools, and expected output.
4.  **Tool execution:** Python tools read files and perform the required
    checks or calculations.
5.  **Final response:** The system presents the tool results in a clear
    format.
6.  **Fallback:** If no workflow matches, the system responds without
    running tools.

## Main Design Choices

### Workflow details come from Excel

The Excel workbook stores workflow names, triggers, inputs, steps,
decision rules, required tools, and expected results. This makes it
easier to update workflow instructions without changing the main Python
code.

### LLM reasoning and Python execution have different jobs

The LLM understands the user's request and helps prepare the response.
Python tools perform file reading, calculations, and data checks so that
these operations follow defined rules.

### Data is processed in Python

CSV, Excel, and JSON files are processed with Python libraries such as
Pandas. This avoids sending large datasets to the LLM when normal Python
code can handle them.

### Pydantic checks data formats

Pydantic models validate workflow information and standardize important
inputs and outputs. This helps catch invalid data earlier.

### Unsupported requests use a fallback

If the system cannot match a request to a known workflow, it returns a
fallback response instead of running unrelated tools.

## Project Structure

``` text
├── data/
│   ├── Assessment_Workflows.xlsx   # Workflow definitions
│   ├── inventory.csv              # Inventory data
│   ├── catalog.csv                # Product catalog
│   └── vendor_prices.csv           # Vendor prices
├── src/
│   ├── config.py                  # Environment settings and LLM setup
│   ├── schemas.py                 # Pydantic models
│   ├── router.py                  # Selects a workflow from the request
│   ├── workflow_registry.py       # Loads workflows from Excel
│   ├── agent_graph.py             # LangGraph workflow
│   └── tools/
│       ├── ingestion_tools.py     # Reads CSV, Excel, and JSON files
│       ├── analysis_tools.py      # Checks and compares data
│       └── integration_tools.py   # Simulates notifications and exports
├── app.py                         # Streamlit web interface
├── main.py                        # Terminal interface
├── run_eval.py                    # Runs evaluation tests
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment settings
└── README.md
```

## Setup

### 1. Clone the repository

``` bash
git clone <repository-url>
cd <repository-folder>
```

Replace `<repository-url>` and `<repository-folder>` with the actual
repository details.

### 2. Create a virtual environment

**Windows PowerShell:**

``` powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

**macOS/Linux:**

``` bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Add your API key

Create a `.env` file in the project root and add your Groq API key:

``` env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=your_supported_model_name
```

Use a valid model supported by your configured LLM provider. Do not
upload your real API key to GitHub.

## Run the Application

### Streamlit web interface

``` bash
streamlit run app.py
```

The dashboard provides a web interface for submitting workflow requests
and viewing results.

### Terminal interface

``` bash
python main.py
```

Use the terminal interface to submit requests. If supported by the
implementation, commands may include `help`, `workflows`, `clear`, and
`exit`.

### Run evaluation tests

``` bash
python run_eval.py
```

This runs the project's evaluation cases and saves a report to
`eval_results.json`, if configured by the script.

## Available Tools

Tools are grouped by their purpose.

  -------------------------------------------------------------------------
  Group                   Tool                      Purpose
  ----------------------- ------------------------- -----------------------
  File reading            `read_csv`                Reads CSV data

  File reading            `read_excel`              Reads Excel data

  File reading            `read_json`               Reads JSON data

  Analysis                `check_threshold`         Finds values above or
                                                    below a limit

  Analysis                `compare_prices`          Compares product and
                                                    vendor prices

  Analysis                `validate_catalog_data`   Checks catalog data for
                                                    problems

  Analysis                `detect_log_anomalies`    Finds error-related log
                                                    entries

  Integration             `generate_restock_list`   Prepares a restock list

  Integration             `send_notification`       Simulates sending a
                                                    notification

  Integration             `export_report`           Simulates preparing a
                                                    report export
  -------------------------------------------------------------------------

Some integrations are simulations. They should not be described as
sending real notifications or completing real external actions unless an
actual integration has been connected.

## Evaluation

The evaluation script is intended to check:

-   **Workflow selection:** Does the system choose the correct workflow?
-   **Tool execution:** Does it use the tools needed for the task?
-   **Fallback behavior:** Does it handle unsupported requests safely?
-   **Output format:** Does the response follow the expected format?

## Example Result

A request such as "Find products that need restocking" may select the
inventory workflow, check stock levels against the configured threshold,
and prepare a restock list.

The exact results depend on the contents of the data files and the
configured workflow rules.

## Technologies Used

-   Python
-   LangChain
-   LangGraph
-   LLM tool calling
-   Pandas
-   Pydantic
-   Excel workflow configuration
-   Streamlit
