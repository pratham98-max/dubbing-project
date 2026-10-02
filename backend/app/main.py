from fastapi import FastAPI
from backend.app.routers import jobs
import os

app = FastAPI(title="AI Dubbing API", version="1.0.0")

app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
