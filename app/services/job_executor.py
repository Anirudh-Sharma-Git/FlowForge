from app.models.job import Job


class JobExecutor:

    async def execute(self, job: Job) -> dict:
        if job.type == "echo":
            return {
                "message": job.payload.get("message"),
            }

        raise ValueError(f"Unknown job type: {job.type}")