from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowDefinition(BaseModel):
    """Schema representing a workflow specification parsed from the Excel file."""
    workflow_id: str = Field(description="Unique Workflow ID  e.g., WF001")
    workflow_name: str = Field(description="Name of Business Workflow")
    trigger: str = Field(description="Trigger phrase or User request that should trigger the workflow")
    inputs: str = Field(description="Input data requirement for Workflow")
    steps: str = Field(description="Raw delimited step sequence from Excel")
    parsed_steps: List[str] = Field(
        default_factory=list,
        description="Cleaned, sequential list of steps"
    )
    data_files: List[str] = Field(
        default_factory=list,
        description="Dataset filenames required by this workflow (e.g., ['inventory.csv'] or ['catalog.csv', 'vendor_prices.csv']) supports 0, 1, or multiple files",
    )
    decision_logic: str = Field(description="Conditional rules and thresholds of Workflow")
    tools_required: str = Field(description="Raw required tools string")
    parsed_tools: List[str] = Field(
        default_factory=list,
        description="Standardized list of required tool names"
    )
    expected_output: str = Field(description="Expected Final output")


class RoutingDecision(BaseModel):
    """Schema for structured LLM intent classification and parameter extraction."""
    workflow_id: str = Field(
        description="Matched workflow ID, e.g., 'WF001'. Returns 'UNKNOWN' if no match."
    )
    reasoning: str = Field(
        description="Semantic justification explaining why this workflow was selected."
    )
    extracted_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted important parameters from query (e.g., order_id, thresholds, dates)."
    )


class StepRecord(BaseModel):
    """Log entry for an individual step executed by the engine."""
    step_number: int
    step_description: str
    status: str = Field(default="completed", description="completed, skipped, or failed")
    details: Optional[str] = None


class ExecutionResponse(BaseModel):
    """Deliverable schema matching the evaluation's required output structure."""
    selected_workflow: str = Field(
        description="Selected Workflow identifier and name, e.g., 'WF001 - Inventory Restock Check'"
    )
    reasoning: str = Field(
        description="Semantic explanation of workflow selection"
    )
    steps_executed: List[str] = Field(
        description="Human-readable list of sequential steps that ran"
    )
    result: Any = Field(
        description="Final business payload, report data, or clarification prompt"
    )