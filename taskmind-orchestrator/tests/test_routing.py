import pytest

from routing import loop_key, loop_target, route_step


@pytest.mark.parametrize("step_number", [3, 5, 7, 8, 18, 19, 20, 21])
@pytest.mark.parametrize("result", ["failed", "blocked"])
def test_terminal_results_end_when_no_rework_route_exists(step_number, result):
    state = {"step_status": {step_number: result}, "loop_counts": {}}

    assert route_step(step_number, state) is None


@pytest.mark.parametrize(
    ("step_number", "result", "expected_target"),
    [
        (11, "failed", 21),
        (11, "changes_requested", 21),
        (12, "changes_requested", 21),
        (14, "changes_requested", 21),
        (16, "changes_requested", 15),
        (17, "changes_requested", 21),
        (18, "changes_requested", 4),
        (19, "changes_requested", 18),
        (20, "changes_requested", 21),
    ],
)
def test_rework_routes_and_loop_targets(step_number, result, expected_target):
    state = {"step_status": {step_number: result}, "loop_counts": {}}

    assert loop_target(step_number, result) == expected_target
    assert route_step(step_number, state) == expected_target


@pytest.mark.parametrize(
    ("step_number", "result", "expected_target"),
    [
        (8, "ok", 18),
        (18, "approved", 19),
        (19, "approved", 9),
        (9, "ok", 20),
        (20, "approved_with_notes", 10),
        (21, "ok", 9),
    ],
)
def test_approved_steps_follow_new_workflow(step_number, result, expected_target):
    state = {"step_status": {step_number: result}, "loop_counts": {}}

    assert route_step(step_number, state) == expected_target


@pytest.mark.parametrize(
    ("target", "key"),
    [
        (4, "to_plan"),
        (15, "to_15"),
        (18, "to_architecture_review"),
        (21, "to_converge"),
    ],
)
def test_each_feedback_loop_has_its_own_counter(target, key):
    assert loop_key(target) == key


def test_loop_guard_allows_three_returns_and_stops_on_fourth():
    state = {
        "step_status": {12: "changes_requested"},
        "loop_counts": {loop_key(21): 3},
    }
    assert route_step(12, state) == 21

    state["loop_counts"][loop_key(21)] = 4
    assert route_step(12, state) is None


def test_release_gate_success_ends_graph():
    state = {"step_status": {17: "ok"}, "loop_counts": {}}

    assert route_step(17, state) is None
