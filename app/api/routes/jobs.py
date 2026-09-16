from fastapi import APIRouter

from app.schemas.job import JobCreate, JobResponse
from app.services.job_repository import InMemoryJobRepository
from app.services.job_service import JobService


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)

job_repository = InMemoryJobRepository()
job_service = JobService(job_repository)


@router.post("/", response_model=JobResponse)
async def create_job(job_data: JobCreate):

    job = job_service.create_job(job_data)

    return JobResponse(
        id=str(job.id),
        type=job.type,
        status=job.status.value,
        priority=job.priority,
    )