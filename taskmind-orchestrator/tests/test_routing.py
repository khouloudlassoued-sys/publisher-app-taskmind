import pytest

from routing import loop_key, loop_target, route_step


@pytest.mark.parametrize("step_number", [3, 5, 7, 8])
@pytest.mark.parametrize("result", ["failed", "blocked"])
def test_gates_stop_on_failure_or_block(step_number, result):
    state = {"step_status": {step_number: result}, "loop_counts": {}}

    assert route_step(step_number, state) is None


@pytest.mark.parametrize(
    ("step_number", "result", "expected_target"),
    [
        (11, "failed", 9),
        (11, "changes_requested", 9),
        (12, "changes_requested", 9),
        (14, "changes_requested", 9),
        (16, "changes_requested", 15),
        (17, "changes_requested", 9),
    ],
)
def test_review_and_validation_routes(step_number, result, expected_target):
    state = {"step_status": {step_number: result}, "loop_counts": {}}

    assert loop_target(step_number, result) == expected_target
    assert route_step(step_number, state) == expected_target


def test_loop_guard_stops_after_three_returns():
    state = {
        "step_status": {12: "changes_requested"},
        "loop_counts": {loop_key(9): 4},
    }

    assert route_step(12, state) is None


def test_normal_success_routes_to_next_step():
    state = {"step_status": {4: "ok"}, "loop_counts": {}}

    assert route_step(4, state) == 5


def test_release_gate_success_ends_graph():
    state = {"step_status": {17: "ok"}, "loop_counts": {}}

    assert route_step(17, state) is None
