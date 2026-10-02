import pytest
import os
from ai.lipsync.backends.wav2lip_backend import Wav2LipBackend

def test_wav2lip_backend(tmp_path):
    backend = Wav2LipBackend(device="cpu")
    
    video = os.path.join("tests", "fixtures", "sample.mp4")
    out_video = str(tmp_path / "sync.mp4")
    
    result = backend.sync(video, video, {}, out_video)
    
    assert os.path.exists(result)
    assert result == out_video
