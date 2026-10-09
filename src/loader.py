from pathlib import Path
from typing import Dict, List, Optional,Any
import pandas as pd
import re

from src.config import WORKFLOW_FILE , DATA_DIR 
from src.schemas import WorkflowDefinition

REQUIRED_COLUMNS = [
    "Workflow_ID",
    "Workflow_Name",
    "Trigger",
    "Inputs",
    "Steps",
    "Decision_Logic",
    "Tools_Required",
    "Expected_Output",
]






#*********************************************************************************************************************
# 1. Parsing Steps Column
def parse_steps_string(steps_text: str) -> List[str]:
    """Splits raw step sequences delimited by arrows into a clean list of steps."""
    
    if pd.isna(steps_text) or not str(steps_text).strip():
            return []
    # Standardizing both unicode arrow (→) and ascii arrow (->)
    normalized = steps_text.replace("->", "→")
    return [step.strip() for step in normalized.split("→") if step.strip()]

#*************************************************************************************************************************
# 2. Parsing Tool Columns
def parse_tools_string(tools_text: str) -> List[str]:
    """Splits delimited tools into standardized, trimmed tool tokens."""
    if pd.isna(tools_text) or not str(tools_text).strip():
            return []
    # Standardizing the Delimiter
    tools_text = tools_text.replace(";", ",")
    return [ tool.strip() for tool in tools_text.split(",") if tool.strip() ]

# *********************************************************************************************************************
# 3. Dynamic Dataset Extraction
def extract_data_files(inputs_text: Any) -> List[str]:
    """ Resolve Input dataset filenames from the Excel Input column description of Workflow.

    1. Matches explicit filenames (.csv, .xlsx, .json).
    2. Falls back to matching existing file stems in DATA_DIR.
    3. Excludes the master assessment file and handles empty/NaN values cleanly.
    """
    if pd.isna(inputs_text) or not str(inputs_text).strip():
        return []

    text = str(inputs_text).strip()

    # Step 1: Match explicit filenames (e.g., 'catalog.csv', 'vendor_prices.csv')
    matches = re.findall(
        r"[\w\-]+\.(?:csv|xlsx|xls|json)\b",
        text,
        re.IGNORECASE,
    )
    if matches:
        # Exclude the master assessment spreadsheet itself
        filtered = [
            f for f in matches if f.lower() != WORKFLOW_FILE.name.lower()
        ]
        return list(dict.fromkeys(filtered))

    # Step 2: Fallback to matching file stems against actual files in DATA_DIR
    matched_stems: List[str] = []
    text_lower = text.lower()
    if DATA_DIR.exists():
        for file_path in DATA_DIR.iterdir():
            if (
                not file_path.is_file()
                or file_path.name.startswith(".")
                or file_path.name.lower() == WORKFLOW_FILE.name.lower()
            ):
                continue

            stem = file_path.stem.lower()
            if len(stem) >= 3 and (
                stem in text_lower or stem.replace("_", " ") in text_lower
            ):
                matched_stems.append(file_path.name)

    return list(dict.fromkeys(matched_stems))


#***************************************************************************************************************
# Loading Workflow
def load_workflows_from_excel( file_path: Path =WORKFLOW_FILE , sheet_name: str = "Workflows") -> Dict[str, WorkflowDefinition]:
    """Reads the Excel spreadsheet at startup and returns a dictionary of validated WorkflowDefinition objects keyed by Workflow_ID. """
   
    if not file_path.exists():
        raise FileNotFoundError(
            f" workflow definition file not found at: {file_path.resolve()}"
        )

    # Read the Workflows sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Verify all expected columns exist
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Columns is Missing. Required Missing columns: {missing_cols}"
        )

    workflows: Dict[str, WorkflowDefinition] = {}

    for _, row in df.iterrows():
        # Skip empty rows if any
        if pd.isna(row["Workflow_ID"]):
            continue

        wf_id = str(row["Workflow_ID"]).strip()
        raw_steps = str(row["Steps"]).strip()
        raw_tools = str(row["Tools_Required"]).strip()

        # Build and validate using Pydantic schema
        definition = WorkflowDefinition(
            workflow_id=wf_id,
            workflow_name=str(row["Workflow_Name"]).strip(),
            trigger=str(row["Trigger"]).strip(),
            inputs=str(row["Inputs"]).strip(),
            steps=raw_steps,
            parsed_steps=parse_steps_string(raw_steps),
            decision_logic=str(row["Decision_Logic"]).strip(),
            tools_required=raw_tools,
            parsed_tools=parse_tools_string(raw_tools),
            expected_output=str(row["Expected_Output"]).strip(),
        )

        workflows[wf_id] = definition

    return workflows


def load_test_questions(
    file_path: Path = WORKFLOW_FILE , sheet_name: str = "Test_Questions"
) -> List[Dict[str, str]]:
    """Loads evaluation test questions from the Excel sheet for testing."""
   
    if not file_path.exists():
        return []

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    questions = []
    for _, row in df.iterrows():
        if pd.isna(row.get("Workflow_ID")):
            continue
        questions.append(
            {
                "workflow_id": str(row["Workflow_ID"]).strip(),
                "test_request": str(row["Test_Request"]).strip(),
                "what_to_check": str(row.get("What_To_Check", "")).strip(),
            }
        )
    return questions