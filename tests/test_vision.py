import pytest
from ai.vision.face_detect import FaceDetector
from ai.vision.face_track import FaceTracker

def test_face_detector():
    detector = FaceDetector()
    boxes = detector.detect_faces("dummy.jpg")
    assert len(boxes) == 1
    assert len(boxes[0]) == 4

def test_face_tracker():
    tracker = FaceTracker()
    tracks = tracker.track_video("dummy.mp4")
    assert "face_track_0" in tracks
    assert len(tracks["face_track_0"]) > 0
