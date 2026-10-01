import os
import wave
import pytest
from ai.audio.extract import extract_audio

def test_extract_audio_success(tmp_path):
    """
    Test that extract_audio produces a valid 16kHz mono WAV file.
    Uses the checked-in fixture video.
    """
    fixture_video = os.path.join("tests", "fixtures", "sample.mp4")
    
    # Check if fixture exists to fail gracefully
    assert os.path.exists(fixture_video), "Test fixture video not found!"
    
    output_wav = str(tmp_path / "output.wav")
    
    # Run the extraction
    result_path = extract_audio(fixture_video, output_wav)
    
    # Assert output file exists and is the correct path
    assert result_path == output_wav
    assert os.path.exists(output_wav)
    
    # Assert correct format (mono, 16kHz)
    with wave.open(output_wav, 'rb') as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        frames = wav_file.getnframes()
        duration = frames / float(sample_rate)
        
        assert channels == 1, f"Expected mono (1 channel), got {channels}"
        assert sample_rate == 16000, f"Expected 16kHz, got {sample_rate}Hz"
        assert duration > 0, "Audio duration should be greater than 0"

def test_extract_audio_file_not_found():
    """
    Test that extract_audio raises a FileNotFoundError if input does not exist.
    """
    with pytest.raises(FileNotFoundError):
        extract_audio("non_existent_file.mp4", "output.wav")
