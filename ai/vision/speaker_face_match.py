from typing import Dict, List, Any

class SpeakerFaceMatcher:
    """
    Associates diarized speakers with tracked faces using active speaker detection heuristics.
    """
    
    def match(self, diarization_turns: List[Dict[str, Any]], face_tracks: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """
        Maps speaker_id to face_track_id based on overlap.
        
        Args:
            diarization_turns: Output from PyannoteDiarizationEngine.
            face_tracks: Output from FaceTracker.
            
        Returns:
            Dict mapping speaker_id -> face_track_id.
        """
        # MVP Logic: Assign the first face track to the first speaker found
        mapping = {}
        track_ids = list(face_tracks.keys())
        
        if not track_ids:
            return mapping
            
        for idx, turn in enumerate(diarization_turns):
            speaker_id = turn.get("speaker")
            if speaker_id and speaker_id not in mapping:
                # Map speaker to the track index (wrap around if more speakers than faces)
                mapping[speaker_id] = track_ids[len(mapping) % len(track_ids)]
                
        return mapping
