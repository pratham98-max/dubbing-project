from pydantic import BaseModel
from typing import List, Optional

class Word(BaseModel):
    word: str
    start: float
    end: float

class TranscriptSegment(BaseModel):
    id: str
    start: float
    end: float
    speaker: Optional[str] = None
    face_id: Optional[str] = None
    source_text: str
    asr_confidence: float
    translated_text: Optional[str] = None
    duration_adjusted_text: Optional[str] = None
    target_duration_estimate_sec: Optional[float] = None
    voice_id: Optional[str] = None
    generated_audio_path: Optional[str] = None
    words: List[Word] = []

class CanonicalTranscript(BaseModel):
    job_id: str
    source_language: str
    target_language: str
    segments: List[TranscriptSegment]
