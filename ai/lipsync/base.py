from abc import ABC, abstractmethod
from typing import Dict, List, Any

class LipSyncBackend(ABC):
    """
    Abstract interface for swappable lip-sync models.
    """
    
    @abstractmethod
    def sync(self, video_path: str, audio_path: str, face_tracks: Dict[str, List[Dict[str, Any]]], output_path: str) -> str:
        """
        Synchronizes lips in the video to match the audio.
        """
        pass
