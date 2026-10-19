from collections.abc import Callable, Mapping
from typing import Any

from routing import loop_key, loop_target
from state import Failure, ProjectState


Executor = Callable[[ProjectState], str]
_VALID_RESULTS = {"ok", "failed", "changes_requested", "blocked"}
_SUCCESS_RESULTS = {"ok", "approved", "approved_with_notes"}
_RESULT_ALIASES = {
    "approved with notes": "approved_with_notes",
    "accepted": "approved",
    "accepted with notes": "approved_with_notes",
    "changes requested": "changes_requested",
}


def _normalize_result(result: str) -> str:
    normalized = result.strip().lower().replace("-", " ")
    normalized = _RESULT_ALIASES.get(normalized, normalized.replace(" ", "_"))
    return normalized if normalized in _VALID_RESULTS | _SUCCESS_RESULTS else "failed"


def _failure(step_number: int, last_completed_step: int) -> Failure:
    return {
        "failedStep": step_number,
        "lastCompletedStep": last_completed_step,
        "canResume": True,
    }


def make_node(step_number: int, executor: Executor | None = None) -> Callable[[ProjectState], dict[str, Any]]:
    run_executor = executor or (lambda _state: "ok")

    def node(state: ProjectState) -> dict[str, Any]:
        result = _normalize_result(run_executor(state))

        last_completed_step = state.get("last_completed_step", 0)
        if result in _SUCCESS_RESULTS:
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
        loop_limit_exceeded = False
        if target is not None:
            counter_key = loop_key(target)
            loop_counts[counter_key] = loop_counts.get(counter_key, 0) + 1
            if loop_counts[counter_key] > 3:
                failure = _failure(step_number, state.get("last_completed_step", 0))
                loop_limit_exceeded = True

        outcome = state.get("outcome", "running")
        failed_step = state.get("failed_step")
        failure_reason = state.get("failure_reason")
        if loop_limit_exceeded:
            outcome = "failed"
            failed_step = step_number
            failure_reason = "loop_limit"
        elif result == "failed" and target is None:
            outcome = "failed"
            failed_step = step_number
            failure_reason = "step_failed"
        elif result == "blocked":
            outcome = "blocked"
            failed_step = step_number
            failure_reason = "blocked"
        elif step_number == 17 and result in _SUCCESS_RESULTS:
            outcome = "success"

        return {
            "current_step": step_number,
            "last_completed_step": last_completed_step,
            "step_status": step_status,
            "loop_counts": loop_counts,
            "failure": failure,
            "history": history,
            "outcome": outcome,
            "failed_step": failed_step,
            "failure_reason": failure_reason,
        }

    return node
