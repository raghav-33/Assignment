import logging
from langchain_core.prompts import ChatPromptTemplate
from src.config import routing_llm
from src.schemas import RoutingDecision
from src.workflow_registry import get_routing_manifest ,initialize_workflow_registry
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# System prompt 
ROUTER_SYSTEM_PROMPT = """You are an expert AI Workflow Classifier and Slot Extractor.
Your job is to match incoming user requests to the correct operational workflow.

### Available Workflows:
{manifest}

### Instructions:
1. Compare the user's intent with the trigger conditions in the manifest above.
2. If the request matches a workflow, return its exact Workflow_ID (e.g., 'WF001').
3. If the request does not match any registered workflow or is completely off-topic, return 'UNKNOWN'.
4. Provide a clear, factual justification in the 'reasoning' field explaining why this workflow was selected.
5. Extract any operational parameters mentioned in the query into 'extracted_parameters':
   - Thresholds, bounds, or numeric limits (e.g., "threshold": 10)
   - Specific product IDs, SKUs, order IDs, or categories
   - Desired limits/row counts (e.g., "limit": 5)
   - Any explicit filenames if mentioned by the user (e.g., "file_path": "custom.csv")
"""

def route_query( user_query: str) -> RoutingDecision:
    """Classifies a user query into a registered workflow and extracts parameters.
       Returns a validated RoutingDecision schema. """
       
    #  Handling empty or whitespace-only inputs / user Queries
    if not user_query or not str(user_query).strip():
        return RoutingDecision(
            workflow_id="UNKNOWN",
            reasoning="No input provided. Query was empty or whitespace.",
            extracted_parameters={},
        )

    #  Dynamically retrieve\Loading the current manifest from memory
    manifest = get_routing_manifest()
    if not manifest:
        return RoutingDecision(
            workflow_id="UNKNOWN",
            reasoning="Workflow registry is uninitialized or empty.",
            extracted_parameters={},
        )

    #  Construct prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ROUTER_SYSTEM_PROMPT),
            ("human", "{query}"),
        ]
    )

    #  Invoke LLM with structured output enforcement
    try:
        structured_llm = routing_llm().with_structured_output(RoutingDecision)
        chain = prompt | structured_llm
        decision = chain.invoke({
                "manifest": manifest,
                "query": user_query
            })
        

        # formatting Workflow ID 
        decision.workflow_id = decision.workflow_id.strip().upper()
        return decision

    except Exception as exc:
        logger.error(
            f"Structured routing failed: {str(exc)}. Executing defensive fallback.",
            exc_info=True,
        )
        return RoutingDecision(
            workflow_id="UNKNOWN",
            reasoning=f"Router encountered an execution error: {str(exc)}",
            extracted_parameters={},
        )
        