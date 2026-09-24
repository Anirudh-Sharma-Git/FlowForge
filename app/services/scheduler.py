from app.models.job import Job


class Scheduler:

    def select_next_job(
        self,
        jobs: list[Job],
    ) -> Job | None:

        queued_jobs = [
            job
            for job in jobs
            if job.status.value == "queued"
        ]

        if not queued_jobs:
            return None

        return max(
            queued_jobs,
            key=lambda job: job.priority,
        )