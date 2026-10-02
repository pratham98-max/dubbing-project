import pytest
import os
from ai.diarization.pyannote_engine import PyannoteDiarizationEngine

def test_pyannote_engine():
    engine = PyannoteDiarizationEngine(device="cpu")
    fixture = os.path.join("tests", "fixtures", "sample.mp4")
    
    turns = engine.diarize(fixture)
    assert len(turns) > 0
    assert "speaker" in turns[0]
    assert turns[0]["start"] >= 0.0
