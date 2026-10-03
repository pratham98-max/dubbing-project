import os
import sys
import subprocess
import torch
import shutil

def run_full_pipeline(video_path, target_language, output_path):
    print("Extracting audio...")
    subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "audio.wav"], check=True)
    
    print("Transcribing with WhisperX...")
    import whisperx
    device = "cuda" if torch.cuda.is_available() else "cpu"
    whisper_model = whisperx.load_model("base", device, compute_type="float32")
    audio = whisperx.load_audio("audio.wav")
    result = whisper_model.transcribe(audio)
    text = " ".join([seg["text"] for seg in result["segments"]]).strip()
    print(f"Detected text: {text}")
    del whisper_model
    torch.cuda.empty_cache()
    
    print("Translating with NLLB...")
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    
    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M", use_safetensors=True).to(device)
    
    inputs = tokenizer(text, return_tensors="pt").to(device)
    forced_id = tokenizer.convert_tokens_to_ids(target_language)
    translated_tokens = model.generate(
        **inputs, forced_bos_token_id=forced_id, max_length=200
    )
    translated_text = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    
    print(f"Translated text: {translated_text}")
    del model
    del tokenizer
    torch.cuda.empty_cache()
    
    print("Synthesizing audio (Voice Cloning via XTTS)...")
    
    # 1. Extract a 6-second clean reference of the user's voice from the original audio
    subprocess.run(["ffmpeg", "-y", "-i", "audio.wav", "-ss", "0", "-t", "6", "-ac", "1", "-ar", "16000", "voice_ref.wav"], check=True)
    
    # 2. Map language code to XTTS format
    lang_short = {"eng_Latn": "en", "spa_Latn": "es", "hin_Deva": "hi", "fra_Latn": "fr"}.get(target_language, "en")
    
    # 3. Load Coqui XTTS Model
    import os
    os.environ["COQUI_TOS_AGREED"] = "1"
    from TTS.api import TTS
    print(f"Loading XTTS Model on {device}...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    
    # 4. Generate cloned speech
    print(f"Cloning voice and generating speech in '{lang_short}'...")
    tts.tts_to_file(text=translated_text, speaker_wav="voice_ref.wav", language=lang_short, file_path="tts_out.wav")
    
    del tts
    torch.cuda.empty_cache()
    
    print("Running Wav2Lip...")
    wav2lip_cmd = [
        sys.executable, "Wav2Lip/inference.py",
        "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip_gan.pth",
        "--face", video_path,
        "--audio", "tts_out.wav",
        "--outfile", output_path
    ]
    subprocess.run(wav2lip_cmd, check=True)
    print("Pipeline Complete!")

