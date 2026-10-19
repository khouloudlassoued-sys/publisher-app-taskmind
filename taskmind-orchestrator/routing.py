from collections.abc import Mapping
from typing import Any


_LOOP_TARGETS = {
    (11, "failed"): 21,
    (11, "changes_requested"): 21,
    (12, "changes_requested"): 21,
    (14, "changes_requested"): 21,
    (16, "changes_requested"): 15,
    (17, "changes_requested"): 21,
    (18, "changes_requested"): 4,
    (19, "changes_requested"): 18,
    (20, "changes_requested"): 21,
}

_LOOP_KEYS = {
    4: "to_plan",
    15: "to_15",
    18: "to_architecture_review",
    21: "to_converge",
}


def loop_target(step_number: int, result: str) -> int | None:
    return _LOOP_TARGETS.get((step_number, result))


def loop_key(target_step: int) -> str:
    return _LOOP_KEYS.get(target_step, f"to_{target_step}")


def route_step(step_number: int, state: Mapping[str, Any]) -> int | None:
    result = state.get("step_status", {}).get(step_number)
    target = loop_target(step_number, result)

    if target is not None:
        if state.get("loop_counts", {}).get(loop_key(target), 0) >= 4:
            return None
        return target

    if result in {"failed", "blocked"}:
        return None
    if step_number == 8 and result in {"ok", "approved"}:
        return 18
    if step_number == 18:
        if result in {"ok", "approved"}:
            return 19
        if result == "changes_requested":
            return 4
    if step_number == 19 and result in {"ok", "approved"}:
        return 9
    if step_number == 9 and result in {"ok", "approved"}:
        return 20
    if step_number == 20:
        if result in {"ok", "approved", "approved_with_notes"}:
            return 10
        if result == "changes_requested":
            return 21
    if step_number == 21 and result in {"ok", "approved"}:
        return 9
    if result in {"ok", "approved"} and step_number < 17:
        return step_number + 1
    if result == "changes_requested" and step_number == 16:
        return 15
    return None
