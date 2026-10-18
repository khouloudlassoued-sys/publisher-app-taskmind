from collections.abc import Mapping
from typing import Any


_LOOP_TARGETS = {
    (11, "failed"): 9,
    (11, "changes_requested"): 9,
    (12, "changes_requested"): 9,
    (14, "changes_requested"): 9,
    (16, "changes_requested"): 15,
    (17, "changes_requested"): 9,
}


def loop_target(step_number: int, result: str) -> int | None:
    return _LOOP_TARGETS.get((step_number, result))


def loop_key(target_step: int) -> str:
    return f"to_{target_step}"


def route_step(step_number: int, state: Mapping[str, Any]) -> int | None:
    result = state.get("step_status", {}).get(step_number)
    target = loop_target(step_number, result)

    if target is not None:
        if state.get("loop_counts", {}).get(loop_key(target), 0) > 3:
            return None
        return target

    if result in {"failed", "blocked"}:
        return None
    if result in {"ok", "changes_requested"} and step_number < 17:
        return step_number + 1
    return None
