from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4


@dataclass
class Lease:
    job_id: UUID
    attempt_id: UUID
    worker_id: str

    id: UUID = field(default_factory=uuid4)

    acquired_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    expires_at: datetime | None = None

    last_heartbeat_at: datetime | None = None

    duration_seconds: int = 30

    def acquire(self) -> None:
        now = datetime.now(timezone.utc)

        self.acquired_at = now
        self.last_heartbeat_at = now
        self.expires_at = now + timedelta(
            seconds=self.duration_seconds
        )

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return True

        return datetime.now(timezone.utc) >= self.expires_at

    def renew(self) -> None:
        if self.is_expired():
            raise RuntimeError("Cannot renew an expired lease")

        now = datetime.now(timezone.utc)

        self.last_heartbeat_at = now
        self.expires_at = now + timedelta(
            seconds=self.duration_seconds
        )