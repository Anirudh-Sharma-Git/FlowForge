from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.job import JobCreate, JobResponse
from app.services.job_repository import PostgresJobRepository
from app.services.job_service import JobService


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    session: AsyncSession = Depends(get_db_session),
):
    repository = PostgresJobRepository(session)
    service = JobService(repository)

    job = await service.create_job(job_data)

    return JobResponse(
        id=str(job.id),
        type=job.type,
        status=job.status.value,
        priority=job.priority,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    repository = PostgresJobRepository(session)
    service = JobService(repository)

    job = await service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return JobResponse(
        id=str(job.id),
        type=job.type,
        status=job.status.value,
        priority=job.priority,
    )