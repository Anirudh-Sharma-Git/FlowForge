import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.jobs import router as jobs_router
from app.core.kafka import start_kafka, stop_kafka
from app.db.init_db import init_db
from app.services.outbox_publisher import OutboxPublisher


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()
    await start_kafka()

    outbox_publisher = OutboxPublisher()

    publisher_task = asyncio.create_task(
        outbox_publisher.run()
    )

    app.state.outbox_publisher = outbox_publisher
    app.state.outbox_publisher_task = publisher_task

    try:
        yield

    finally:

        publisher_task.cancel()

        try:
            await publisher_task
        except asyncio.CancelledError:
            pass

        await stop_kafka()


app = FastAPI(
    title="FlowForge",
    lifespan=lifespan,
)

app.include_router(jobs_router)


@app.get("/")
async def root():
    return {
        "message": "FlowForge is running"
    }