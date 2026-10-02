from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid

router = APIRouter()

class JobRequest(BaseModel):
    video_id: str
    target_language: str

class JobResponse(BaseModel):
    job_id: str
    status: str

# In-memory mock for MVP (Replaced by Postgres + Redis in actual deployment)
MOCK_DB = {}

def process_pipeline(job_id: str):
    """
    Background worker function that mocks orchestrating the AI pipeline.
    """
    MOCK_DB[job_id] = "completed"

@router.post("/", response_model=JobResponse, status_code=202)
async def create_job(request: JobRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    MOCK_DB[job_id] = "queued"
    
    # Enqueue background processing
    background_tasks.add_task(process_pipeline, job_id)
    
    return JobResponse(job_id=job_id, status="queued")

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in MOCK_DB:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": MOCK_DB[job_id]}
