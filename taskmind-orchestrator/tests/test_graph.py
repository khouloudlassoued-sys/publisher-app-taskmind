import pytest

from graph import STEP_NAMES, build_graph
from langgraph.graph import END, START
from state import initial_state


def run_with_executors(executors):
    execution_order = []

    def wrap(step_number, executor):
        def wrapped(state):
            execution_order.append(step_number)
            return executor(state)

        return wrapped

    wrapped_executors = {
        step_number: wrap(step_number, executors.get(step_number, lambda _state: "ok"))
        for step_number in STEP_NAMES
    }
    result = build_graph(wrapped_executors).invoke(initial_state("SCRUM-5"))
    return result, execution_order


def test_nominal_path_executes_all_steps_in_order():
    result, execution_order = run_with_executors({})

    assert execution_order == list(range(1, 18))
    assert result["failure"] is None
    assert result["last_completed_step"] == 17
    assert result["current_step"] == 17


def test_compiled_graph_edges_match_declared_workflow_exactly():
    graph = build_graph().get_graph()
    expected_destinations = {
        1: (2, None),
        2: (3, None),
        3: (4, None),
        4: (5, None),
        5: (6, None),
        6: (7, None),
        7: (8, None),
        8: (9, None),
        9: (10, None),
        10: (11, None),
        11: (12, 9, None),
        12: (13, 9, None),
        13: (14, None),
        14: (15, 9, None),
        15: (16, None),
        16: (17, 15, None),
        17: (None, 9),
    }
    expected_edges = {(START, STEP_NAMES[1])}
    expected_edges.update(
        (
            STEP_NAMES[step_number],
            STEP_NAMES[destination] if destination is not None else END,
        )
        for step_number, destinations in expected_destinations.items()
        for destination in destinations
    )
    actual_edges = {(edge.source, edge.target) for edge in graph.edges}

    assert actual_edges == expected_edges


@pytest.mark.parametrize("gate_step", [3, 5, 7, 8])
def test_gate_failure_stops_before_following_steps(gate_step):
    result, execution_order = run_with_executors({
        gate_step: lambda _state: "failed",
    })

    assert execution_order == list(range(1, gate_step + 1))
    assert result["failure"] == {
        "failedStep": gate_step,
        "lastCompletedStep": gate_step - 1,
        "canResume": True,
    }
    assert execution_order == [step for step in execution_order if step <= gate_step]
    assert not any(step > gate_step for step in execution_order)


def test_code_review_changes_requested_repeats_implementation_once():
    code_review_runs = 0

    def code_review(_state):
        nonlocal code_review_runs
        code_review_runs += 1
        return "changes_requested" if code_review_runs == 1 else "ok"

    result, execution_order = run_with_executors({12: code_review})

    assert execution_order == list(range(1, 13)) + list(range(9, 18))
    assert result["loop_counts"]["to_9"] == 1
    assert result["failure"] is None
    assert result["last_completed_step"] == 17


def test_documentation_validation_changes_requested_repeats_documentation_only():
    documentation_validation_runs = 0

    def documentation_validation(_state):
        nonlocal documentation_validation_runs
        documentation_validation_runs += 1
        return "changes_requested" if documentation_validation_runs == 1 else "ok"

    result, execution_order = run_with_executors({16: documentation_validation})

    assert execution_order == list(range(1, 17)) + [15, 16, 17]
    assert all(execution_order.count(step) == 1 for step in range(9, 15))
    assert result["loop_counts"]["to_15"] == 1
    assert result["failure"] is None


def test_blocked_code_review_stops():
    result, execution_order = run_with_executors({12: lambda _state: "blocked"})

    assert execution_order == list(range(1, 13))
    assert result["failure"] == {
        "failedStep": 12,
        "lastCompletedStep": 11,
        "canResume": True,
    }


def test_code_review_loop_stops_after_three_returns():
    result, execution_order = run_with_executors({
        12: lambda _state: "changes_requested",
    })

    assert execution_order == list(range(1, 13)) + list(range(9, 13)) * 3
    assert execution_order.count(12) == 4
    assert result["loop_counts"]["to_9"] == 4
    assert result["failure"] == {
        "failedStep": 12,
        "lastCompletedStep": 11,
        "canResume": True,
    }


def test_release_gate_changes_requested_returns_to_implementation():
    release_gate_runs = 0

    def release_gate(_state):
        nonlocal release_gate_runs
        release_gate_runs += 1
        return "changes_requested" if release_gate_runs == 1 else "ok"

    result, execution_order = run_with_executors({17: release_gate})

    assert execution_order == list(range(1, 18)) + list(range(9, 18))
    assert result["loop_counts"]["to_9"] == 1
    assert result["failure"] is None
