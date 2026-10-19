import pytest

from graph import STEP_DESTINATIONS, STEP_NAMES, build_graph
from langgraph.graph import END, START
from state import initial_state


def run_with_executors(executors, decisions=None):
    execution_order = []

    def wrap(step_number, executor):
        def wrapped(state):
            execution_order.append(step_number)
            return executor(state)

        return wrapped

    defaults = {
        18: lambda state: state.get("decisions", {}).get("architecture_review", "approved"),
        19: lambda state: state.get("decisions", {}).get("security_review", "approved"),
        20: lambda state: state.get("decisions", {}).get("integration_review", "Approved"),
    }
    wrapped_executors = {
        step_number: wrap(
            step_number,
            executors.get(step_number, defaults.get(step_number, lambda _state: "ok")),
        )
        for step_number in STEP_NAMES
    }
    state = initial_state("SCRUM-5")
    if decisions is not None:
        state["decisions"] = decisions
    result = build_graph(wrapped_executors).invoke(state)
    return result, execution_order


def test_nominal_path_executes_all_steps_and_succeeds():
    result, execution_order = run_with_executors({})

    assert execution_order == [step for step in STEP_NAMES if step != 21]
    assert result["failure"] is None
    assert result["outcome"] == "success"
    assert result["failed_step"] is None
    assert result["last_completed_step"] == 17
    assert result["current_step"] == 17


def test_compiled_graph_has_exactly_the_declared_50_edges():
    graph = build_graph().get_graph()
    expected_edges = {(START, STEP_NAMES[1])}
    expected_edges.update(
        (
            STEP_NAMES[step_number],
            STEP_NAMES[destination] if destination is not None else END,
        )
        for step_number, destinations in STEP_DESTINATIONS.items()
        for destination in destinations
    )
    actual_edges = {(edge.source, edge.target) for edge in graph.edges}

    assert len(expected_edges) == 50
    assert actual_edges == expected_edges


@pytest.mark.parametrize("gate_step", [3, 5, 7, 8])
def test_gate_failure_stops_with_failed_outcome(gate_step):
    result, execution_order = run_with_executors({
        gate_step: lambda _state: "failed",
    })

    assert execution_order == [step for step in STEP_NAMES if step <= gate_step]
    assert result["outcome"] == "failed"
    assert result["failed_step"] == gate_step
    assert result["failure"] == {
        "failedStep": gate_step,
        "lastCompletedStep": gate_step - 1,
        "canResume": True,
    }


def test_architecture_changes_requested_returns_to_plan():
    architecture_runs = 0

    def architecture_review(_state):
        nonlocal architecture_runs
        architecture_runs += 1
        return "changes_requested" if architecture_runs == 1 else "approved"

    result, execution_order = run_with_executors({18: architecture_review})

    assert execution_order[:10] == [1, 2, 3, 4, 5, 6, 7, 8, 18, 4]
    assert execution_order[10:15] == [5, 6, 7, 8, 18]
    assert result["loop_counts"]["to_plan"] == 1
    assert result["outcome"] == "success"


def test_security_blocked_sets_blocked_outcome():
    result, execution_order = run_with_executors({19: lambda _state: "blocked"})

    assert execution_order == [1, 2, 3, 4, 5, 6, 7, 8, 18, 19]
    assert result["outcome"] == "blocked"
    assert result["failed_step"] == 19
    assert result["failure_reason"] == "blocked"


def test_integration_changes_requested_routes_through_converge_to_implementation():
    integration_runs = 0

    def integration_review(_state):
        nonlocal integration_runs
        integration_runs += 1
        return "Changes Requested" if integration_runs == 1 else "Approved with notes"

    result, execution_order = run_with_executors({20: integration_review})
    first_integration = execution_order.index(20)

    assert execution_order[first_integration:first_integration + 4] == [20, 21, 9, 20]
    assert result["loop_counts"]["to_converge"] == 1
    assert result["outcome"] == "success"


def test_code_review_changes_requested_routes_through_converge():
    code_review_runs = 0

    def code_review(_state):
        nonlocal code_review_runs
        code_review_runs += 1
        return "changes_requested" if code_review_runs == 1 else "ok"

    result, execution_order = run_with_executors({12: code_review})
    first_review = execution_order.index(12)

    assert execution_order[first_review:first_review + 5] == [12, 21, 9, 20, 10]
    assert result["loop_counts"]["to_converge"] == 1
    assert result["outcome"] == "success"


def test_documentation_validation_changes_requested_repeats_documentation_only():
    validation_runs = 0

    def documentation_validation(_state):
        nonlocal validation_runs
        validation_runs += 1
        return "changes_requested" if validation_runs == 1 else "ok"

    result, execution_order = run_with_executors({16: documentation_validation})

    assert execution_order[-3:] == [15, 16, 17]
    assert execution_order[execution_order.index(16) + 1:][:2] == [15, 16]
    assert all(execution_order.count(step) == 1 for step in range(9, 15))
    assert result["loop_counts"]["to_15"] == 1
    assert result["outcome"] == "success"


def test_blocked_code_review_sets_blocked_outcome():
    result, execution_order = run_with_executors({12: lambda _state: "blocked"})

    assert execution_order[-1] == 12
    assert result["outcome"] == "blocked"
    assert result["failed_step"] == 12


def test_converge_loop_limit_stops_with_loop_limit_failure():
    result, execution_order = run_with_executors({
        12: lambda _state: "changes_requested",
    })

    assert execution_order.count(12) == 4
    assert result["loop_counts"]["to_converge"] == 4
    assert result["outcome"] == "failed"
    assert result["failed_step"] == 12
    assert result["failure_reason"] == "loop_limit"


def test_release_gate_changes_requested_returns_through_converge():
    release_gate_runs = 0

    def release_gate(_state):
        nonlocal release_gate_runs
        release_gate_runs += 1
        return "changes_requested" if release_gate_runs == 1 else "ok"

    result, execution_order = run_with_executors({17: release_gate})
    first_return = execution_order.index(21)

    assert execution_order[first_return:first_return + 5] == [21, 9, 20, 10, 11]
    assert result["loop_counts"]["to_converge"] == 1
    assert result["outcome"] == "success"
