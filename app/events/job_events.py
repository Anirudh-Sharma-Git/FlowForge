from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import UUID


@dataclass
class JobEvent:
    event_type: str
    job_id: UUID
    job_type: str
    status: str
    timestamp: datetime
    payload: dict | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        data = asdict(self)

        data["job_id"] = str(data["job_id"])
        data["timestamp"] = data["timestamp"].isoformat()

        return data


def create_job_event(
    event_type: str,
    job_id: UUID,
    job_type: str,
    status: str,
    payload: dict | None = None,
    error: str | None = None,
) -> JobEvent:

    return JobEvent(
        event_type=event_type,
        job_id=job_id,
        job_type=job_type,
        status=status,
        timestamp=datetime.now(timezone.utc),
        payload=payload,
        error=error,
    )