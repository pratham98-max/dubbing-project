import os
import whisperx
from typing import Dict, Any

def transcribe_audio(audio_path: str, batch_size: int = 16, compute_type: str = "float16", device: str = "cuda") -> Dict[str, Any]:
    """
    Transcribes audio using WhisperX and returns word-level timestamps.
    
    Args:
        audio_path (str): Path to the input audio file (preferably 16kHz mono WAV).
        batch_size (int): Batch size for transcription. Reduce if OOM.
        compute_type (str): float16 or int8 for quantization.
        device (str): cuda or cpu.
        
    Returns:
        dict: A dictionary containing the detected language, transcript segments, and word timestamps.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    if device == "cpu":
        compute_type = "int8"
        
    # 1. Transcribe with WhisperX
    model = whisperx.load_model("large-v2", device, compute_type=compute_type)
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=batch_size)
    
    # 2. Align whisper output for accurate word-level timestamps
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    
    return {
        "language": result.get("language", "unknown"),
        "segments": result["segments"]
    }
