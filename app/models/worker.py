from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class InvalidWorkerTransition(Exception):
    """Raised when a worker attempts an invalid state transition."""


class WorkerStatus(str, Enum):
    STARTING = "starting"
    ACTIVE = "active"
    DRAINING = "draining"
    OFFLINE = "offline"


class WorkerStateMachine:

    _TRANSITIONS = {
        WorkerStatus.STARTING: {
            WorkerStatus.ACTIVE,
            WorkerStatus.OFFLINE,
        },
        WorkerStatus.ACTIVE: {
            WorkerStatus.DRAINING,
            WorkerStatus.OFFLINE,
        },
        WorkerStatus.DRAINING: {
            WorkerStatus.OFFLINE,
        },
        WorkerStatus.OFFLINE: set(),
    }

    @classmethod
    def can_transition(
        cls,
        current: WorkerStatus,
        target: WorkerStatus,
    ) -> bool:
        return target in cls._TRANSITIONS[current]

    @classmethod
    def transition(
        cls,
        current: WorkerStatus,
        target: WorkerStatus,
    ) -> WorkerStatus:

        if not cls.can_transition(current, target):
            raise InvalidWorkerTransition(
                f"Invalid worker transition: "
                f"{current.value} -> {target.value}"
            )

        return target


@dataclass
class Worker:
    hostname: str
    capacity: int

    id: UUID = field(default_factory=uuid4)

    status: WorkerStatus = WorkerStatus.STARTING

    registered_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    last_heartbeat_at: datetime | None = None

    def activate(self) -> None:
        self.status = WorkerStateMachine.transition(
            self.status,
            WorkerStatus.ACTIVE,
        )

        self.last_heartbeat_at = datetime.now(timezone.utc)

    def begin_draining(self) -> None:
        self.status = WorkerStateMachine.transition(
            self.status,
            WorkerStatus.DRAINING,
        )

    def mark_offline(self) -> None:
        self.status = WorkerStateMachine.transition(
            self.status,
            WorkerStatus.OFFLINE,
        )

    def heartbeat(self) -> None:
        if self.status not in {
            WorkerStatus.ACTIVE,
            WorkerStatus.DRAINING,
        }:
            raise RuntimeError(
                "Only active or draining workers can send heartbeats"
            )

        self.last_heartbeat_at = datetime.now(timezone.utc)