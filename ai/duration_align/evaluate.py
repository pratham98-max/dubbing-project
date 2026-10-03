import os
import torch
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from ai.duration_align.duration_predictor_model import DurationPredictor
from ai.duration_align.train import KNOWN_LANGUAGES, get_language_one_hot

def heuristic_estimate(text):
    # Old baseline: 0.3 seconds per syllable approx. We used char_count / 15 earlier.
    # We will use char_count * 0.08 or length of text * 0.08
    return len(text) * 0.07

def compare_to_heuristic(model=None, csv_path="data/duration_test_set.csv"):
    df = pd.read_csv(csv_path)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if model is None:
        model = DurationPredictor(num_languages=len(KNOWN_LANGUAGES), embed_dim=384)
        model.load_state_dict(torch.load("models/duration_predictor.pt", map_location=device))
        
    model.to(device)
    model.eval()
    
    encoder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    
    texts = df['text'].tolist()
    embeddings = encoder.encode(texts, convert_to_tensor=True, show_progress_bar=False).to(device)
    
    char_counts = torch.tensor(df['char_count'].values, dtype=torch.float32).unsqueeze(1).to(device)
    word_counts = torch.tensor(df['word_count'].values, dtype=torch.float32).unsqueeze(1).to(device)
    lang_one_hots = torch.tensor([get_language_one_hot(l) for l in df['language']], dtype=torch.float32).to(device)
    
    true_durations = df['duration_seconds'].values
    
    with torch.no_grad():
        preds = model(embeddings, char_counts, word_counts, lang_one_hots).cpu().numpy().flatten()
        
    heuristic_preds = np.array([heuristic_estimate(t) for t in texts])
    
    model_mae = np.mean(np.abs(preds - true_durations))
    heuristic_mae = np.mean(np.abs(heuristic_preds - true_durations))
    
    results = {
        "model_mae": round(model_mae, 4),
        "heuristic_mae": round(heuristic_mae, 4),
        "improvement": round(heuristic_mae - model_mae, 4)
    }
    
    # Save writeup
    os.makedirs("docs/results", exist_ok=True)
    with open("docs/results/duration_model_eval.md", "w") as f:
        f.write("# Duration Predictor Evaluation\n\n")
        f.write(f"**Test Set Size:** {len(df)} samples\n\n")
        f.write("| Metric | Mean Absolute Error (Seconds) |\n")
        f.write("|--------|-----------------------------|\n")
        f.write(f"| Syllable/Char Heuristic Baseline | {results['heuristic_mae']:.4f}s |\n")
        f.write(f"| Trained NN Predictor | **{results['model_mae']:.4f}s** |\n")
        f.write(f"| **Improvement** | **{results['improvement']:.4f}s** |\n")
        
    return results

if __name__ == "__main__":
    res = compare_to_heuristic()
    print(res)
