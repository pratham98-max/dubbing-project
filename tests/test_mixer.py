import os
import pytest
from ai.audio.mixer import mix_audio_and_video

def test_mix_audio_and_video(tmp_path):
    """
    Tests audio and video mixing by using the fixture sample video 
    as both the video source and the audio source (extracted earlier).
    """
    video_path = os.path.join("tests", "fixtures", "sample.mp4")
    assert os.path.exists(video_path), "Fixture video missing"
    
    # Normally we would pass the generated TTS audio. 
    # For MVP test, we'll pass the video itself as the audio source 
    # (FFmpeg handles pulling the audio stream automatically).
    output_path = str(tmp_path / "final_dubbed.mp4")
    
    result = mix_audio_and_video(video_path, video_path, output_path)
    
    assert os.path.exists(result)
    assert result == output_path
