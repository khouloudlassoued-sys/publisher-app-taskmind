from collections.abc import Callable, Mapping
from typing import Any

from routing import loop_key, loop_target
from state import Failure, ProjectState


Executor = Callable[[ProjectState], str]
_VALID_RESULTS = {"ok", "failed", "changes_requested", "blocked"}


def _failure(step_number: int, last_completed_step: int) -> Failure:
    return {
        "failedStep": step_number,
        "lastCompletedStep": last_completed_step,
        "canResume": True,
    }


def make_node(step_number: int, executor: Executor | None = None) -> Callable[[ProjectState], dict[str, Any]]:
    run_executor = executor or (lambda _state: "ok")

    def node(state: ProjectState) -> dict[str, Any]:
        result = run_executor(state)
        if result not in _VALID_RESULTS:
            result = "failed"

        last_completed_step = state.get("last_completed_step", 0)
        if result == "ok":
            last_completed_step = step_number

        step_status = dict(state.get("step_status", {}))
        step_status[step_number] = result
        history = list(state.get("history", []))
        history.append(f"step_{step_number}: {result}")

        failure = None
        if result in {"failed", "blocked"}:
            failure = _failure(step_number, last_completed_step if result == "ok" else state.get("last_completed_step", 0))

        loop_counts = dict(state.get("loop_counts", {}))
        target = loop_target(step_number, result)
        if target is not None:
            counter_key = loop_key(target)
            loop_counts[counter_key] = loop_counts.get(counter_key, 0) + 1
            if loop_counts[counter_key] > 3:
                failure = _failure(step_number, state.get("last_completed_step", 0))

        return {
            "current_step": step_number,
            "last_completed_step": last_completed_step,
            "step_status": step_status,
            "loop_counts": loop_counts,
            "failure": failure,
            "history": history,
        }

    return node
