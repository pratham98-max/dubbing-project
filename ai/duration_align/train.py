import os
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
from torch.utils.data import DataLoader, TensorDataset

from ai.duration_align.duration_predictor_model import DurationPredictor

# Define known target languages to build a consistent one-hot vector
KNOWN_LANGUAGES = ["eng_Latn", "spa_Latn", "hin_Deva", "fra_Latn", "mar_Deva", "tam_Taml", "tel_Telu", "jpn_Jpan", "deu_Latn", "arb_Arab"]

def get_language_one_hot(lang):
    idx = KNOWN_LANGUAGES.index(lang) if lang in KNOWN_LANGUAGES else 0
    vec = [0.0] * len(KNOWN_LANGUAGES)
    vec[idx] = 1.0
    return vec

def prepare_data(csv_path):
    print("Loading dataset...")
    df = pd.read_csv(csv_path)
    
    # Stratified split 80/10/10 based on length bins
    df['length_bin'] = pd.qcut(df['char_count'], q=5, labels=False, duplicates='drop')
    
    train_df, temp_df = train_test_split(df, test_size=0.2, stratify=df['length_bin'], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['length_bin'], random_state=42)
    
    # Save test set for evaluate.py
    test_df.to_csv("data/duration_test_set.csv", index=False)
    
    print("Loading Sentence Transformer...")
    encoder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    
    def df_to_tensors(dataframe):
        texts = dataframe['text'].tolist()
        embeddings = encoder.encode(texts, convert_to_tensor=True, show_progress_bar=False).cpu()
        
        char_counts = torch.tensor(dataframe['char_count'].values, dtype=torch.float32).unsqueeze(1)
        word_counts = torch.tensor(dataframe['word_count'].values, dtype=torch.float32).unsqueeze(1)
        
        lang_one_hots = torch.tensor([get_language_one_hot(l) for l in dataframe['language']], dtype=torch.float32)
        
        durations = torch.tensor(dataframe['duration_seconds'].values, dtype=torch.float32).unsqueeze(1)
        
        return TensorDataset(embeddings, char_counts, word_counts, lang_one_hots, durations)
    
    print("Encoding sets...")
    train_ds = df_to_tensors(train_df)
    val_ds = df_to_tensors(val_df)
    
    return train_ds, val_ds

def train_model(csv_path="data/duration_dataset.csv", epochs=30, batch_size=32):
    train_ds, val_ds = prepare_data(csv_path)
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on {device}...")
    
    model = DurationPredictor(num_languages=len(KNOWN_LANGUAGES), embed_dim=384).to(device)
    criterion = nn.HuberLoss() # Robust to outliers
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    train_losses, val_losses = [], []
    
    for epoch in range(epochs):
        model.train()
        batch_losses = []
        for emb, ch, wd, lng, dur in train_loader:
            emb, ch, wd, lng, dur = emb.to(device), ch.to(device), wd.to(device), lng.to(device), dur.to(device)
            
            optimizer.zero_grad()
            preds = model(emb, ch, wd, lng)
            loss = criterion(preds, dur)
            loss.backward()
            optimizer.step()
            
            batch_losses.append(loss.item())
            
        train_loss = np.mean(batch_losses)
        train_losses.append(train_loss)
        
        model.eval()
        with torch.no_grad():
            val_batch_losses = []
            for emb, ch, wd, lng, dur in val_loader:
                emb, ch, wd, lng, dur = emb.to(device), ch.to(device), wd.to(device), lng.to(device), dur.to(device)
                preds = model(emb, ch, wd, lng)
                val_loss = criterion(preds, dur)
                val_batch_losses.append(val_loss.item())
            
            val_loss = np.mean(val_batch_losses)
            val_losses.append(val_loss)
            
        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        
    # Save plot
    os.makedirs("docs/results", exist_ok=True)
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Huber Loss")
    plt.title("Duration Predictor Training Curve")
    plt.legend()
    plt.savefig("docs/results/duration_model_training_curve.png")
    plt.close()
    
    return model, {"train_loss": train_losses, "val_loss": val_losses}

if __name__ == "__main__":
    model, history = train_model()
    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/duration_predictor.pt")
    print("Model saved to models/duration_predictor.pt")
