from typing import List, Dict, Tuple, Any
from ai.vision.face_detect import FaceDetector

class FaceTracker:
    """
    Tracks faces across frames using simple IoU (Intersection over Union).
    """
    
    def __init__(self):
        self.detector = FaceDetector()
        self.tracks = {}
        
    def track_video(self, video_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Processes a video and returns tracked faces over time.
        """
        # Mocking MVP logic returning a single continuous track
        return {
            "face_track_0": [
                {"frame": 0, "bbox": (100, 100, 200, 200)},
                {"frame": 1, "bbox": (101, 101, 200, 200)}
            ]
        }
