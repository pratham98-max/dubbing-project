from fastapi import APIRouter, BackgroundTasks, HTTPException, File, Form, UploadFile
from pydantic import BaseModel
import uuid
import os
import shutil
import time

router = APIRouter()

class JobResponse(BaseModel):
    job_id: str
    status: str

MOCK_DB = {}

def process_pipeline(job_id: str, input_path: str, target_language: str):
    """
    Background worker that runs the full modular pipeline.
    If PIPELINE_MODE=full, sends video to Colab GPU URL.
    """
    import requests
    output_path = os.path.join("media", f"{job_id}_output.mp4")
    
    colab_url = os.getenv("COLAB_INFERENCE_URL")
    pipeline_mode = os.getenv("PIPELINE_MODE", "mock")
    
    if pipeline_mode == "full" and colab_url:
        print(f"Sending job {job_id} to Colab GPU at {colab_url}")
        try:
            with open(input_path, "rb") as f:
                response = requests.post(
                    colab_url,
                    files={"video_file": f},
                    data={"target_language": target_language},
                    headers={"ngrok-skip-browser-warning": "1"}
                )
            if response.status_code == 200:
                with open(output_path, "wb") as f_out:
                    f_out.write(response.content)
            else:
                MOCK_DB[job_id] = f"error: Colab returned {response.status_code}"
                return
        except Exception as e:
            MOCK_DB[job_id] = f"error: {str(e)}"
            return
    else:
        # Mock mode
        time.sleep(3)
        shutil.copy(input_path, output_path)
    
    MOCK_DB[job_id] = "completed"

@router.post("/", response_model=JobResponse, status_code=202)
async def create_job(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...),
    target_language: str = Form(...)
):
    job_id = str(uuid.uuid4())
    MOCK_DB[job_id] = "processing"
    
    os.makedirs("media", exist_ok=True)
    input_path = os.path.join("media", f"{job_id}_input.mp4")
    
    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)
    
    # Enqueue background processing
    background_tasks.add_task(process_pipeline, job_id, input_path, target_language)
    
    return JobResponse(job_id=job_id, status="processing")

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in MOCK_DB:
        raise HTTPException(status_code=404, detail="Job not found")
        
    response = {"job_id": job_id, "status": MOCK_DB[job_id]}
    
    if MOCK_DB[job_id] == "completed":
        response["download_url"] = f"http://localhost:8000/media/{job_id}_output.mp4"
        
    return response
