from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.jobs import router as jobs_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="FlowForge",
    lifespan=lifespan,
)

app.include_router(jobs_router)


@app.get("/")
async def root():
    return {"message": "FlowForge is running"}