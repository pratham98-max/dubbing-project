# Frontend Development Notes

## Blockers and Workarounds

During the implementation of the Master Frontend Build Prompt, several constraints were discovered regarding the current MVP backend API (`backend/app/routers/jobs.py` and the synchronous Colab worker).

1. **WebSocket Streaming (`GET/WS /api/jobs/{id}/stream`)**: 
   The backend does not support WebSockets, nor does the Colab pipeline broadcast its stage-by-stage granular progress (Audio Extraction -> ASR -> Translation, etc). The frontend UI has gracefully downgraded to long-polling the overarching job status (`pending` -> `running` -> `completed`) and displays an honest "API Note" in the UI rather than faking progress steps.

2. **Live Transcripts (`GET /api/jobs/{id}/transcript`)**: 
   The Colab worker does not serialize or persist the WhisperX segments to the backend database. Therefore, the "Live Transcript Review" panel requested in the prompt has been hidden, and users bypass Phase F4 (Transcript Regeneration).

3. **Face Detection Robustness**:
   Users should be advised that uploading videos where a face is not consistently present in every frame will crash the remote GPU pipeline due to S3FD detector constraints in Wav2Lip. The frontend simply maps this to a generic `failed` job status.

## Next Steps
To unlock the full interactive UI (Phase F4 & F5), the Colab pipeline must be refactored to asynchronously push webhooks back to the FastAPI backend, storing segment-level metadata.
