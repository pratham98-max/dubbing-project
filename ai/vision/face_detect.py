from typing import List, Dict, Any, Tuple

class FaceDetector:
    """
    Face detection using a mock structure for the MVP (MediaPipe/RetinaFace).
    """
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        
    def detect_faces(self, frame_path: str) -> List[Tuple[int, int, int, int]]:
        """
        Returns bounding boxes (x, y, w, h) for faces found in the frame.
        """
        # Mocking detection
        return [(100, 100, 200, 200)]
