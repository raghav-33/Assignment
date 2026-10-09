
import time
from typing import Any, Dict, List
from src.agent_graph import run_agent
from src.schemas import ExecutionResponse
from src.workflow_registry import (
    get_all_workflows,
    initialize_workflow_registry,
)


def run_evaluation() -> None:
    """Executes test cases against all registered workflows and outputs a performance scorecard."""
    print("\n============================================================")
    print("        ENTERPRISE AGENT WORKFLOW EVALUATION SUITE          ")
    print("============================================================\n")

    # 1. Initialize registry and load workflow specifications
    initialize_workflow_registry()
    workflows_data = get_all_workflows()
    workflows = (
        list(workflows_data.values())
        if isinstance(workflows_data, dict)
        else list(workflows_data)
    )

    print(f"Loaded {len(workflows)} active workflows from Excel registry.\n")

    # 2. Build test cases (All registered workflows + 1 fallback query)
    test_cases: List[Dict[str, Any]] = []

    for wf in workflows:
        test_cases.append(
            {
                "case_id": wf.workflow_id,
                "name": wf.workflow_name,
                "query": wf.trigger,
                "expected_id": wf.workflow_id,
                "type": "WORKFLOW",
            }
        )

    # Negative test case to verify conditional fallback routing
    test_cases.append(
        {
            "case_id": "FALLBACK_TEST",
            "name": "Out-of-Scope Query",
            "query": "What is the capital of France and what is the weather there?",
            "expected_id": "UNKNOWN",
            "type": "NEGATIVE",
        }
    )

    # 3. Execute evaluation loop
    results: List[Dict[str, Any]] = []
    total_latency = 0.0

    for idx, case in enumerate(test_cases, 1):
        print(f"[{idx}/{len(test_cases)}] Testing {case['case_id']}...")
        start_time = time.time()

        try:
            response: ExecutionResponse = run_agent(case["query"])
            duration = time.time() - start_time
            total_latency += duration

            selected_wf = response.selected_workflow
            steps_run = response.steps_executed
            output_text = str(response.result).strip()

            # Verify routing accuracy
            if case["type"] == "WORKFLOW":
                routed_correctly = case["expected_id"] in selected_wf
                tools_executed = len(steps_run) > 0 and not any(
                    "REJECTED" in s for s in steps_run
                )
            else:
                # Fallback expects UNKNOWN or None in workflow selection
                routed_correctly = (
                    "UNKNOWN" in selected_wf or "None" in selected_wf
                )
                tools_executed = any("REJECTED" in s for s in steps_run)

            has_output = len(output_text) > 20
            passed = routed_correctly and has_output

            results.append(
                {
                    "case_id": case["case_id"],
                    "expected": case["expected_id"],
                    "matched": (
                        selected_wf.split(" - ")[0]
                        if " - " in selected_wf
                        else selected_wf
                    ),
                    "routing": "PASS" if routed_correctly else "FAIL",
                    "tools_ran": len(steps_run),
                    "latency": f"{duration:.2f}s",
                    "status": "PASS" if passed else "FAIL",
                }
            )

        except Exception as err:
            duration = time.time() - start_time
            total_latency += duration
            results.append(
                {
                    "case_id": case["case_id"],
                    "expected": case["expected_id"],
                    "matched": "ERROR",
                    "routing": "FAIL",
                    "tools_ran": 0,
                    "latency": f"{duration:.2f}s",
                    "status": "FAIL",
                }
            )
            print(f"    ERROR running {case['case_id']}: {err}")

    # 4. Print Scorecard Table
    header = f"{'Case ID':<15} | {'Expected':<10} | {'Matched':<15} | {'Routing':<8} | {'Tools Ran':<10} | {'Latency':<8} | {'Status':<6}"
    divider = "-" * len(header)

    print("\n" + divider)
    print("                    EVALUATION RESULTS TABLE                ")
    print(divider)
    print(header)
    print(divider)

    passed_count = 0
    for r in results:
        if r["status"] == "PASS":
            passed_count += 1
        print(
            f"{r['case_id']:<15} | {r['expected']:<10} | {r['matched']:<15} | {r['routing']:<8} | {r['tools_ran']:<10} | {r['latency']:<8} | {r['status']:<6}"
        )

    print(divider)

    # 5. Print Summary Metrics
    total_cases = len(test_cases)
    accuracy_pct = (passed_count / total_cases) * 100
    avg_latency = total_latency / total_cases if total_cases > 0 else 0.0

    print(f"\nTotal Test Cases  : {total_cases}")
    print(f"Passed            : {passed_count}")
    print(f"Failed            : {total_cases - passed_count}")
    print(f"Success Rate      : {accuracy_pct:.1f}%")
    print(f"Average Latency   : {avg_latency:.2f}s per query")
    print("============================================================\n")


if __name__ == "__main__":
    run_evaluation()