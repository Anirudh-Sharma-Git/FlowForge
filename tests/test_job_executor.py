import pytest

from app.models.job import Job
from app.services.job_executor import JobExecutor


@pytest.mark.asyncio
async def test_echo_job():
    job = Job(
        type="echo",
        payload={
            "message": "Hello FlowForge",
        },
    )

    executor = JobExecutor()

    result = await executor.execute(job)

    assert result == {
        "message": "Hello FlowForge",
    }


@pytest.mark.asyncio
async def test_unknown_job_type():
    job = Job(
        type="unknown",
        payload={},
    )

    executor = JobExecutor()

    with pytest.raises(ValueError):
        await executor.execute(job)