from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class InvalidAttemptTransition(Exception):
    """Raised when an execution attempt makes an invalid state transition."""


class AttemptStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class AttemptStateMachine:

    _TRANSITIONS = {
        AttemptStatus.PENDING: {
            AttemptStatus.RUNNING,
        },
        AttemptStatus.RUNNING: {
            AttemptStatus.SUCCEEDED,
            AttemptStatus.FAILED,
        },
        AttemptStatus.SUCCEEDED: set(),
        AttemptStatus.FAILED: set(),
    }

    @classmethod
    def can_transition(
        cls,
        current: AttemptStatus,
        target: AttemptStatus,
    ) -> bool:
        return target in cls._TRANSITIONS[current]

    @classmethod
    def transition(
        cls,
        current: AttemptStatus,
        target: AttemptStatus,
    ) -> AttemptStatus:

        if not cls.can_transition(current, target):
            raise InvalidAttemptTransition(
                f"Invalid attempt transition: "
                f"{current.value} -> {target.value}"
            )

        return target


@dataclass
class ExecutionAttempt:
    job_id: UUID
    attempt_number: int

    id: UUID = field(default_factory=uuid4)
    status: AttemptStatus = AttemptStatus.PENDING

    worker_id: str | None = None

    started_at: datetime | None = None
    finished_at: datetime | None = None

    error: str | None = None
    result: dict | None = None

    def start(self, worker_id: str) -> None:
        self.status = AttemptStateMachine.transition(
            self.status,
            AttemptStatus.RUNNING,
        )

        self.worker_id = worker_id
        self.started_at = datetime.now(timezone.utc)

    def succeed(self, result: dict | None = None) -> None:
        self.status = AttemptStateMachine.transition(
            self.status,
            AttemptStatus.SUCCEEDED,
        )

        self.finished_at = datetime.now(timezone.utc)
        self.result = result

    def fail(self, error: str) -> None:
        self.status = AttemptStateMachine.transition(
            self.status,
            AttemptStatus.FAILED,
        )

        self.finished_at = datetime.now(timezone.utc)
        self.error = error