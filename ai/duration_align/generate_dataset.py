import os
import csv
import time
import subprocess
import wave
import contextlib
import random

def get_audio_duration(file_path):
    try:
        with contextlib.closing(wave.open(file_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / float(rate)
    except Exception as e:
        return 0.0

def generate_dataset(output_csv="data/duration_dataset.csv", num_samples=3000):
    print(f"Generating duration dataset: {num_samples} samples...")
    
    # Simple corpus generation: normally you'd use a real dataset like FLORES-200, 
    # but for project reproducibility without huge downloads, we generate 
    # synthetically varying lengths of text in multiple languages.
    
    languages = [
        ("eng_Latn", "en-US-AriaNeural", ["The quick brown fox jumps over the lazy dog.", "AI dubbing is the future.", "Hello world, this is a test of the speech synthesis duration model."]),
        ("spa_Latn", "es-ES-ElviraNeural", ["El zorro marrón rápido salta sobre el perro perezoso.", "El doblaje con IA es el futuro.", "Hola mundo, esta es una prueba."]),
        ("hin_Deva", "hi-IN-SwaraNeural", ["तेज़ भूरी लोमड़ी आलसी कुत्ते के ऊपर से कूद जाती है।", "एआई डबिंग भविष्य है।", "नमस्ते दुनिया, यह एक परीक्षण है।"]),
        ("fra_Latn", "fr-FR-DeniseNeural", ["Le renard brun rapide saute par-dessus le chien paresseux.", "Le doublage par IA est l'avenir.", "Bonjour le monde."])
    ]

    os.makedirs("data", exist_ok=True)
    
    results = []
    
    # We will generate varying lengths by repeating/truncating words
    for i in range(num_samples):
        lang_code, voice, seeds = random.choice(languages)
        seed_text = random.choice(seeds)
        
        # Randomly scale the sentence length (1 to 15 words roughly)
        words = seed_text.split()
        target_len = random.randint(2, 20)
        
        # Build a synthetic sentence of target length
        text_parts = []
        while len(text_parts) < target_len:
            text_parts.extend(words)
        
        text = " ".join(text_parts[:target_len])
        char_count = len(text)
        word_count = len(text.split())
        
        audio_file = "temp_dataset_audio.wav"
        
        # Generate with Edge-TTS (simulating our pipeline's exact engine)
        try:
            cmd = ["edge-tts", "--text", text, "--voice", voice, "--write-media", audio_file]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            duration = get_audio_duration(audio_file)
            
            if duration > 0.1:
                results.append({
                    "text": text,
                    "language": lang_code,
                    "char_count": char_count,
                    "word_count": word_count,
                    "duration_seconds": round(duration, 3)
                })
                
                if len(results) % 100 == 0:
                    print(f"Generated {len(results)} / {num_samples} samples...")
        except Exception as e:
            pass
            
    # Save CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["text", "language", "char_count", "word_count", "duration_seconds"])
        writer.writeheader()
        writer.writerows(results)
        
    # Print stats
    durations = [r["duration_seconds"] for r in results]
    if durations:
        print("\nDataset Generation Complete!")
        print(f"Total valid samples: {len(results)}")
        print(f"Min Duration: {min(durations):.2f}s")
        print(f"Max Duration: {max(durations):.2f}s")
        print(f"Mean Duration: {sum(durations)/len(durations):.2f}s")
    
if __name__ == "__main__":
    # For CI/Colab testing, we default to a smaller dataset to save time, 
    # but it can be scaled up to 3000 as requested.
    generate_dataset(num_samples=3000)
