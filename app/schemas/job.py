from pydantic import BaseModel, Field

class JobCreate(BaseModel):
    type: str
    payload: dict
    priority: int = Field(default=0, ge=0)

class JobResponse(BaseModel):
    id: str
    type: str
    status: str
    priority: int

