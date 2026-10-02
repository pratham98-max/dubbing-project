import os
import pytest
from ai.tts.xtts_engine import XTTSv2Engine
from ai.tts.piper_engine import PiperEngine

def test_xtts_engine_without_consent(tmp_path):
    engine = XTTSv2Engine(device="cpu")
    out_path = str(tmp_path / "out_xtts.wav")
    
    # Assert voice cloning fails if consent is not explicitly set to True
    with pytest.raises(PermissionError):
        engine.synthesize("Hello world", out_path, speaker_reference_path="dummy.wav", consent_confirmed=False)

def test_xtts_engine_with_consent(tmp_path):
    engine = XTTSv2Engine(device="cpu")
    out_path = str(tmp_path / "out_xtts.wav")
    
    # Assert voice cloning works if consent is True
    engine.synthesize("Hello world", out_path, speaker_reference_path="dummy.wav", consent_confirmed=True)
    assert os.path.exists(out_path)

def test_piper_engine(tmp_path):
    engine = PiperEngine()
    out_path = str(tmp_path / "out_piper.wav")
    
    engine.synthesize("Hello world", out_path)
    assert os.path.exists(out_path)
