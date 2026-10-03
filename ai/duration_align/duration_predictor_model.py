import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer

class DurationPredictor(nn.Module):
    def __init__(self, num_languages=10, embed_dim=384):
        super(DurationPredictor, self).__init__()
        
        # We assume the sentence embedding (embed_dim) is pre-computed and passed in.
        # Features = embed_dim + 2 (char_count, word_count) + num_languages (one_hot)
        input_dim = embed_dim + 2 + num_languages
        
        self.regressor = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
    def forward(self, embeddings, char_counts, word_counts, lang_one_hots):
        # char_counts and word_counts should be shape (batch, 1)
        # lang_one_hots should be shape (batch, num_languages)
        x = torch.cat([embeddings, char_counts, word_counts, lang_one_hots], dim=1)
        return self.regressor(x)
