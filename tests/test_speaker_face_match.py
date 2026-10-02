import pytest
from ai.vision.speaker_face_match import SpeakerFaceMatcher

def test_speaker_face_matcher():
    matcher = SpeakerFaceMatcher()
    
    turns = [
        {"speaker": "SPEAKER_00", "start": 0.0, "end": 2.0},
        {"speaker": "SPEAKER_01", "start": 2.0, "end": 4.0}
    ]
    
    tracks = {
        "face_track_0": [{"frame": 0, "bbox": (0,0,1,1)}],
        "face_track_1": [{"frame": 0, "bbox": (1,1,2,2)}]
    }
    
    mapping = matcher.match(turns, tracks)
    
    assert "SPEAKER_00" in mapping
    assert "SPEAKER_01" in mapping
    assert mapping["SPEAKER_00"] == "face_track_0"
    assert mapping["SPEAKER_01"] == "face_track_1"
