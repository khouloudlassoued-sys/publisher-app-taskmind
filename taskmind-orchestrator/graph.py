from collections.abc import Callable
from typing import Any

from langgraph.graph import END, START, StateGraph

from nodes import Executor, make_node
from routing import route_step
from state import ProjectState


STEP_NAMES = {
    1: "extraction",
    2: "specify",
    3: "clarify",
    4: "plan",
    5: "analyze_plan",
    6: "tasks",
    7: "persistence_check",
    8: "analyze_cross",
    9: "implementation",
    10: "unit_tests_gen",
    11: "unit_tests_validation",
    12: "code_review",
    13: "e2e_test",
    14: "e2e_review",
    15: "documentation",
    16: "documentation_validation",
    17: "release_gate",
}

STEP_DESTINATIONS = {
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


def build_graph(executors: dict[int, Executor] | None = None) -> Any:
    configured_executors = executors or {}
    builder = StateGraph(ProjectState)

    for step_number, step_name in STEP_NAMES.items():
        builder.add_node(
            step_name,
            make_node(step_number, configured_executors.get(step_number)),
        )

    builder.add_edge(START, STEP_NAMES[1])

    for step_number, step_name in STEP_NAMES.items():
        def route(state: ProjectState, current_step: int = step_number) -> int | None:
            return route_step(current_step, state)

        path_map = {
            destination: STEP_NAMES[destination] if destination is not None else END
            for destination in STEP_DESTINATIONS[step_number]
        }
        builder.add_conditional_edges(step_name, route, path_map=path_map)

    return builder.compile()
