from pathlib import Path
from typing import Dict, List, Optional

from src.config import WORKFLOW_FILE
from src.loader import load_workflows_from_excel
from src.schemas import WorkflowDefinition

# Module-level dictionary cache (In-memory singleton)
_WORKFLOWS: Dict[str, WorkflowDefinition] = {}


def initialize_workflow_registry(file_path: Optional[Path] = None) -> None:
    """Loads and caches all workflows in memory during application startup."""
    global _WORKFLOWS
    target_path = file_path or WORKFLOW_FILE
    _WORKFLOWS = load_workflows_from_excel(file_path=target_path)


def get_workflow(workflow_id: str) -> Optional[WorkflowDefinition]:
    """Retrieves a workflow definition by its unique identifier (e.g., 'WF001').
    Returns None if the workflow ID is empty or not found.
    """
    if not workflow_id:
        return None
    return _WORKFLOWS.get(workflow_id.strip().upper())


def get_all_workflows() -> List[WorkflowDefinition]:
    """Returns all currently registered workflow definitions as a list."""
    return list(_WORKFLOWS.values())


def get_workflow_ids() -> List[str]:
    """Returns a list of all registered workflow IDs (e.g., ['WF001', 'WF002', ...])."""
    return list(_WORKFLOWS.keys())


def count_workflows() -> int:
    """Returns the total number of registered workflows."""
    return len(_WORKFLOWS)


def is_initialized() -> bool:
    """Checks whether the workflow cache has been populated."""
    return len(_WORKFLOWS) > 0


def get_routing_manifest() -> str:
    """Generates a compact trigger manifest formatted for the router prompt.
    Exposes only the Workflow ID, Name, and Trigger phrase to prevent
    token bloat and avoid tool confusion.
    """
    manifest_lines = []
    for wf in _WORKFLOWS.values():
        manifest_lines.append(
            f"- [{wf.workflow_id}] {wf.workflow_name}: Triggered by '{wf.trigger}'"
        )
    return "\n".join(manifest_lines)