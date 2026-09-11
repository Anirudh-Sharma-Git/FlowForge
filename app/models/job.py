from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InvalidJobTransition(Exception):
    """Raised when a job attempts an invalid state transition."""


class JobStateMachine:
    _TRANSITIONS = {
        JobStatus.PENDING: {
            JobStatus.QUEUED,
            JobStatus.CANCELLED,
        },
        JobStatus.QUEUED: {
            JobStatus.RUNNING,
            JobStatus.CANCELLED,
        },
        JobStatus.RUNNING: {
            JobStatus.SUCCEEDED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        },
        JobStatus.FAILED: {
            JobStatus.QUEUED,
        },
        JobStatus.SUCCEEDED: set(),
        JobStatus.CANCELLED: set(),
    }

    @classmethod
    def can_transition(
        cls,
        current: JobStatus,
        target: JobStatus,
    ) -> bool:
        return target in cls._TRANSITIONS[current]

    @classmethod
    def transition(
        cls,
        current: JobStatus,
        target: JobStatus,
    ) -> JobStatus:
        if not cls.can_transition(current, target):
            raise InvalidJobTransition(
                f"Invalid job transition: "
                f"{current.value} -> {target.value}"
            )

        return target


@dataclass
class Job:
    type: str
    payload: dict

    id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING
    priority: int = 0
    max_attempts: int = 3

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    version: int = 1    # Every state change will increment this version

    def transition_to(self, target: JobStatus) -> None:
        self.status = JobStateMachine.transition(
            self.status,
            target,
        )

        self.updated_at = datetime.now(timezone.utc)
        self.version += 1