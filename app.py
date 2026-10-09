"""app.py - Complete Streamlit Interface for AI Agent Workflow System."""

import time
import streamlit as st

from src.workflow_registry import (
    initialize_workflow_registry,
    get_all_workflows,
)
from src.agent_graph import run_agent
from src.schemas import ExecutionResponse


# ----------------------------------------------------------------------
# Page Configuration & Styling
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Enterprise Agent Operations",
    page_icon="⚡",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title { font-size: 2rem; font-weight: 700; margin-bottom: 0.2rem; }
    .subtitle { color: #6c757d; font-size: 1rem; margin-bottom: 1.5rem; }
    .step-box { padding: 8px 14px; margin: 5px 0; border-radius: 6px; font-family: monospace; font-size: 0.88rem; }
    .step-success { background-color: #e6f4ea; border-left: 4px solid #34a853; color: #137333; }
    .step-rejected { background-color: #fce8e6; border-left: 4px solid #ea4335; color: #c5221f; }
    .step-simulated { background-color: #e8f0fe; border-left: 4px solid #1a73e8; color: #174ea6; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# State & Registry Initialization
# ----------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_registry():
    """Initializes Excel metadata into memory once during application startup."""
    initialize_workflow_registry()
    return get_all_workflows()


try:
    workflows_data = load_registry()
    workflow_list = (
        list(workflows_data.values())
        if isinstance(workflows_data, dict)
        else list(workflows_data)
    )
except Exception as err:
    st.error(f"Failed to load Excel Workflow Registry: {err}")
    st.stop()

if "query_text" not in st.session_state:
    st.session_state["query_text"] = ""


def set_example_query(prompt: str):
    st.session_state["query_text"] = prompt


# ----------------------------------------------------------------------
# Sidebar: System Telemetry & Workflows
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ System Control")
    st.success(f"Excel Registry Loaded: **{len(workflow_list)} Workflows**")

    st.subheader("Active Workflows")
    for wf in workflow_list:
        with st.expander(f"📌 {wf.workflow_id}: {wf.workflow_name}"):
            st.caption(f"**Trigger:** {wf.trigger}")
            st.caption(f"**Required Tools:** `{wf.tools_required}`")
            data_files_display = (
                ", ".join(wf.data_files) if wf.data_files else "None"
            )
            st.caption(f"**Data Files:** `{data_files_display}`")

    st.divider()
    st.subheader("Example Queries")
    example_prompts = [
        "Check today's inventory and find products needing restock below threshold 10.",
        "Compare vendor price quotes with catalog benchmark prices and flag discrepancies.",
        "Audit product catalog for missing attributes and duplicate IDs.",
        "What is the capital of France?",
    ]

    for idx, ex in enumerate(example_prompts):
        st.button(
            f"💡 {ex[:45]}...",
            key=f"ex_{idx}",
            on_click=set_example_query,
            args=(ex,),
            use_container_width=True,
        )


# ----------------------------------------------------------------------
# Main Application Area
# ----------------------------------------------------------------------
st.markdown(
    '<div class="main-title">⚡ Enterprise AI Agent Workflow Engine</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">LangGraph Tool Calling governed by Excel Workflow Metadata</div>',
    unsafe_allow_html=True,
)

# Text Input Bound to Session State
query = st.text_area(
    "Enter Operational Query:",
    key="query_text",
    placeholder="e.g. Check stock levels in inventory and prepare restock list for items below 10...",
    height=90,
)

col1, col2 = st.columns([1, 5])
with col1:
    execute_button = st.button(
        "🚀 Run Workflow", type="primary", use_container_width=True
    )

# ----------------------------------------------------------------------
# Execution Handling
# ----------------------------------------------------------------------
if execute_button:
    if not query.strip():
        st.warning("Please enter a query before running.")
    else:
        with st.spinner("Classifying intent, scoping tools, and executing graph..."):
            start_time = time.time()
            try:
                response = run_agent(query.strip())
                elapsed = time.time() - start_time

                # Extract attributes whether response is ExecutionResponse or dict
                if isinstance(response, ExecutionResponse):
                    selected_workflow = response.selected_workflow
                    reasoning = response.reasoning
                    steps_executed = response.steps_executed
                    result_payload = response.result
                else:
                    selected_workflow = response.get(
                        "selected_workflow", "Unknown"
                    )
                    reasoning = response.get("reasoning", "N/A")
                    steps_executed = response.get("steps_executed", [])
                    result_payload = response.get(
                        "result", response.get("final_output", "")
                    )

                st.divider()

                # Status Banner
                is_fallback = (
                    "UNKNOWN" in selected_workflow
                    or "None" in selected_workflow
                )

                stat_col1, stat_col2 = st.columns([3, 1])
                with stat_col1:
                    if is_fallback:
                        st.error(f"**Status:** Fallback Triggered ({selected_workflow})")
                    else:
                        st.success(f"**Matched Workflow:** {selected_workflow}")
                with stat_col2:
                    st.metric(label="Execution Time", value=f"{elapsed:.2f}s")

                # Semantic Router Reasoning
                with st.expander("🧠 Semantic Router Reasoning", expanded=True):
                    st.info(reasoning)

                # Step Pipeline Telemetry
                st.subheader("🛠️ Executed Pipeline Steps")
                if steps_executed:
                    for step in steps_executed:
                        if "[SUCCESS]" in step:
                            st.markdown(
                                f'<div class="step-box step-success">✔ {step}</div>',
                                unsafe_allow_html=True,
                            )
                        elif "[REJECTED]" in step:
                            st.markdown(
                                f'<div class="step-box step-rejected">✖ {step}</div>',
                                unsafe_allow_html=True,
                            )
                        elif "[SIMULATED]" in step:
                            st.markdown(
                                f'<div class="step-box step-simulated">ℹ {step}</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f'<div class="step-box">{step}</div>',
                                unsafe_allow_html=True,
                            )
                else:
                    st.write("No external tool steps executed.")

                # Final Business Output
                st.subheader("📋 Final Synthesized Output")
                st.markdown(result_payload)

            except Exception as err:
                st.error(f"An unexpected error occurred during execution: {err}")