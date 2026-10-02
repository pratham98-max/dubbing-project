from fastapi.testclient import TestClient
from backend.app.main import app
import time

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_check_job():
    # 1. Create Job
    response = client.post("/api/jobs/", json={"video_id": "test_video", "target_language": "eng_Latn"})
    assert response.status_code == 202
    data = response.json()
    job_id = data["job_id"]
    assert data["status"] == "queued"
    
    # 2. Wait for background task to complete
    time.sleep(0.1)
    
    # 3. Check status
    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
