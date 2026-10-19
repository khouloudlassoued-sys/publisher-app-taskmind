from typing import TypedDict


class Failure(TypedDict):
    failedStep: int
    lastCompletedStep: int
    canResume: bool


class ProjectState(TypedDict):
    ticket_id: str
    current_step: int
    last_completed_step: int
    step_status: dict[int, str]
    loop_counts: dict[str, int]
    failure: Failure | None
    history: list[str]
    outcome: str
    failed_step: int | None
    failure_reason: str | None
    decisions: dict[str, str]


def initial_state(ticket_id: str) -> ProjectState:
    return {
        "ticket_id": ticket_id,
        "current_step": 1,
        "last_completed_step": 0,
        "step_status": {},
        "loop_counts": {},
        "failure": None,
        "history": [],
        "outcome": "running",
        "failed_step": None,
        "failure_reason": None,
        "decisions": {},
    }
