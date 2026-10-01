# GitHub Setup Guide

To meet the requirements of **Phase 0 — Environment & Repo Scaffolding**, follow these instructions to set up the GitHub repository and Issues.

## 1. Setup GitHub Project Board
Create a GitHub Projects (beta) board called **"Dubbing Pipeline Build"**.
Add the following columns:
- `Backlog`
- `In Progress`
- `In Review`
- `Done`

## 2. Create Issues
Create the following issues in your GitHub repository and link them to the project board. 

*You can use the GitHub CLI to create these rapidly:*

```bash
gh issue create --title "Phase 0 — Environment & Repo Scaffolding" --body "Build: project skeleton, .env.example, dependency manifests split by phase. Acceptance: pytest runs with exit code 0; repo pushed to GitHub with Issues #1–#13 created for all phases." --label "phase"

gh issue create --title "Phase 1 — Audio/Video Extraction" --body "Build: ai/audio/extract.py wrapping FFmpeg. Acceptance: unit test asserts correct sample rate/channel count/duration on a checked-in fixture clip." --label "phase"

gh issue create --title "Phase 2 — ASR" --body "Build: ai/asr/whisperx_engine.py. Acceptance threshold: Word Error Rate (WER) <= 25% on the test set for clear, single-speaker audio." --label "phase"

gh issue create --title "Phase 3 — Translation" --body "Build: ai/translation/indictrans2_engine.py and nllb_engine.py. Acceptance threshold: BLEU score >= 25 against reference translations on the same test set." --label "phase"

gh issue create --title "Phase 4 — Duration-Aware Translation" --body "Build: ai/duration_align/duration_translator.py. Acceptance threshold: final audio duration is within +/-15% of the source segment duration for at least 80% of segments, and no segment requires more than +/-20% time-stretch." --label "phase"

gh issue create --title "Phase 5 — TTS" --body "Build: ai/tts/xtts_engine.py and piper_engine.py. Acceptance threshold: human-rated intelligibility — at least 2 independent listeners rate 10 generated clips as understandable (target >= 90%)." --label "phase"

gh issue create --title "Phase 6 — Audio Replacement & Mixing (V1 MVP)" --body "Build: ai/audio/mixer.py, mux into final MP4 via FFmpeg. Acceptance threshold: output video duration within +/-5% of source video duration; A/V playback has no audible dropout/overlap." --label "phase"

gh issue create --title "Phase 7 — Speaker Diarization & Voice Consent Gate" --body "Build: ai/diarization/pyannote_engine.py. Acceptance threshold: Diarization Error Rate (DER) <= 30% on a multi-speaker test clip AND zero voice-cloning calls succeed without the consent flag set." --label "phase"

gh issue create --title "Phase 8 — Face Detection & Tracking" --body "Build: ai/vision/face_detect.py, face_track.py. Acceptance threshold: tracked face bounding boxes remain on the correct face for >= 90% of frames." --label "phase"

gh issue create --title "Phase 9 — Speaker-Face Association" --body "Build: ai/vision/speaker_face_match.py. Acceptance threshold: correct speaker-to-face assignment on >= 80% of diarized turns in a 2-speaker test clip." --label "phase"

gh issue create --title "Phase 10 — Lip Synchronization" --body "Build: ai/lipsync/backends/wav2lip_backend.py. Acceptance threshold: LSE-D at or below the range Wav2Lip itself reports on its original benchmark." --label "phase"

gh issue create --title "Phase 11 — Full Pipeline Integration + API + Job Queue" --body "Build: FastAPI, Redis+RQ, PostgreSQL, WebSockets. Acceptance threshold: a job submitted via POST /api/jobs reaches status: completed for 100% of test clips without manual intervention." --label "phase"

gh issue create --title "Phase 12 — Frontend + Deployment" --body "Build: React/Next.js UI, Docker Compose. Acceptance threshold: a non-technical reviewer can complete a full dub unaided via docker compose up." --label "phase"
```
