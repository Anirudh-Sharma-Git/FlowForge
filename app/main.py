from fastapi import FastAPI
from app.api.routes.jobs import router as jobs_router

app = FastAPI(title="FlowForge")
app.include_router(jobs_router)

@app.get("/")
async def root():
    return {"message": "FlowForge is running"}