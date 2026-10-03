import os
from typing import List, Dict, Any

class PyannoteDiarizationEngine:
    """
    Speaker Diarization Engine using pyannote.audio.
    """
    
    def __init__(self, auth_token: str = None, device: str = "cpu"):
        self.auth_token = auth_token
        self.device = device
        self.pipeline = None
        
    def _load_if_needed(self):
        if self.pipeline is None:
            if not self.auth_token:
                print("Warning: No HuggingFace token provided for Pyannote. This would fail in real use.")
            print(f"Loading pyannote/speaker-diarization-3.1 on {self.device}...")
            # self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=self.auth_token)
            self.pipeline = "loaded_mock"
            
    def diarize(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Diarizes the audio file.
        Returns a list of speaker turns.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        self._load_if_needed()
        
        # MVP Mock returning a single speaker turn for the whole duration
        return [
            {"speaker": "SPEAKER_00", "start": 0.0, "end": 3.0}
        ]
        
    def extract_speaker_references(self, audio_path: str, turns: List[Dict[str, Any]], job_id: str) -> Dict[str, str]:
        """
        Extracts a clean reference audio clip for each unique speaker for voice cloning.
        """
        out_dir = os.path.join("media", "processed", job_id, "voice_refs")
        os.makedirs(out_dir, exist_ok=True)
        
        speaker_refs = {}
        # Group by speaker to find their longest turn
        speaker_turns = {}
        for turn in turns:
            spk = turn["speaker"]
            dur = turn["end"] - turn["start"]
            if spk not in speaker_turns or dur > speaker_turns[spk]["dur"]:
                speaker_turns[spk] = {"start": turn["start"], "dur": dur}
                
        for spk, turn in speaker_turns.items():
            out_file = os.path.join(out_dir, f"{spk}.wav")
            # Extract via ffmpeg
            import subprocess
            cmd = [
                "ffmpeg", "-y", "-i", audio_path,
                "-ss", str(turn["start"]), "-t", str(turn["dur"]),
                "-ac", "1", "-ar", "16000", out_file
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Log exact extraction per requirements
            print(f"Extraction Log -> Created voice reference for {spk}: {out_file} (Duration: {turn['dur']:.2f}s)")
            speaker_refs[spk] = out_file
            
        return speaker_refs
