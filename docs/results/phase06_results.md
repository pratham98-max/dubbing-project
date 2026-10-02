# Phase 6: Audio Replacement & Mixing (Version 1 MVP)

**Tool:** FFmpeg (subprocess wrapper)
**Process:** A/V muxing replacing original audio track with dubbed audio track, truncated to `-shortest` to prevent drift.

### Acceptance Metric
- **Target:** Output video duration within +/-5% of source video duration; no audible dropout.
- **Actual:** 100% match (verified via FFmpeg metadata output duration), playback verified.

**Status:** PASS
**Milestone:** VERSION 1 MVP ACHIEVED
