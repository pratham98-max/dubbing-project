import os
import subprocess
import torch
import shutil

def run_full_pipeline(video_path, target_language, output_path):
    print("Extracting audio...")
    subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "audio.wav"], check=True)
    
    print("Transcribing with WhisperX...")
    import whisperx
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Use float32 to avoid float16 errors on some Colab setups
    whisper_model = whisperx.load_model("base", device, compute_type="float32")
    audio = whisperx.load_audio("audio.wav")
    result = whisper_model.transcribe(audio)
    text = " ".join([seg["text"] for seg in result["segments"]]).strip()
    print(f"Detected text: {text}")
    
    # Free up VRAM
    del whisper_model
    torch.cuda.empty_cache()
    
    print("Translating with NLLB...")
    from transformers import pipeline
    # target_language comes in as eng_Latn, spa_Latn, hin_Deva, fra_Latn
    translator = pipeline("translation", model="facebook/nllb-200-distilled-600M", device=0 if device=="cuda" else -1)
    translated_text = translator(text, src_lang="eng_Latn", tgt_lang=target_language)[0]['translation_text']
    print(f"Translated text: {translated_text}")
    
    del translator
    torch.cuda.empty_cache()
    
    print("Synthesizing audio with XTTS-v2...")
    from TTS.api import TTS
    # Mapping nllb lang to xtts lang
    lang_map = {"eng_Latn": "en", "spa_Latn": "es", "hin_Deva": "hi", "fra_Latn": "fr"}
    tts_lang = lang_map.get(target_language, "en")
    
    # We use Piper as fallback if XTTS requires terms agreement, but we will try XTTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    tts.tts_to_file(text=translated_text, speaker_wav="audio.wav", language=tts_lang, file_path="tts_out.wav")
    
    del tts
    torch.cuda.empty_cache()
    
    print("Running Wav2Lip...")
    # Wav2Lip takes the original video (face) and the new audio (tts_out.wav)
    wav2lip_cmd = [
        "python", "Wav2Lip/inference.py",
        "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip_gan.pth",
        "--face", video_path,
        "--audio", "tts_out.wav",
        "--outfile", output_path
    ]
    subprocess.run(wav2lip_cmd, check=True)
    
    print("Pipeline Complete!")

