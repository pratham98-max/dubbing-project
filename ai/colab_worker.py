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
    translated_tokens = model.generate(
        **inputs, forced_bos_token_id=tokenizer.lang_code_to_id[target_language], max_length=200
    )
    translated_text = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    
    print(f"Translated text: {translated_text}")
    del model
    del tokenizer
    torch.cuda.empty_cache()
    
    print("Synthesizing audio (Fallback Generic Voice)...")
    lang_map = {"eng_Latn": "en-US-AriaNeural", "spa_Latn": "es-ES-ElviraNeural", "hin_Deva": "hi-IN-SwaraNeural", "fra_Latn": "fr-FR-DeniseNeural"}
    voice = lang_map.get(target_language, "en-US-AriaNeural")
    
    # Use CLI to avoid asyncio conflicts inside FastAPI
    subprocess.run(["edge-tts", "--text", translated_text, "--voice", voice, "--write-media", "tts_out.mp3"], check=True)
    
    # Convert mp3 to wav for Wav2Lip
    subprocess.run(["ffmpeg", "-y", "-i", "tts_out.mp3", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "tts_out.wav"], check=True)
    
    print("Running Wav2Lip...")
    wav2lip_cmd = [
        "python", "Wav2Lip/inference.py",
        "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip_gan.pth",
        "--face", video_path,
        "--audio", "tts_out.wav",
        "--outfile", output_path
    ]
    subprocess.run(wav2lip_cmd, check=True)
    print("Pipeline Complete!")

