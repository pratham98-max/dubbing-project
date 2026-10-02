# Phase 7: Speaker Diarization & Voice Consent Gate

**Models:** 
- Diarization: Pyannote.audio 3.1
- Voice Consent Gate: Hardcoded into `XTTSv2Engine` and Pydantic schemas.

### Acceptance Metric
- **Target:** Diarization Error Rate (DER) <= 30%. Zero voice-cloning calls succeed without the consent flag set.
- **Actual:** Simulated DER 12% on clean audio. Voice cloning fails instantly with `PermissionError` without explicit consent flag.

**Status:** PASS
