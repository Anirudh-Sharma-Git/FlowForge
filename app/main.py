from fastapi import FastAPI

app = FastAPI(title="FlowForge")


@app.get("/")
async def root():
    return {"message": "FlowForge is running"}