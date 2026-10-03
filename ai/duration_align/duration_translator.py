import re
import os
import math
import torch
from ai.common.schemas import TranscriptSegment
from ai.translation.base import TranslationEngine

class DurationAwareTranslator:
    """
    Implements the MVP algorithm for duration-aware translation.
    1. Translate normally.
    2. Estimate synthesized duration using the trained Neural Network (or heuristic fallback).
    3. Check if estimated_duration is within +/-15% of slot_duration.
    4. If too long, rewrite to be shorter.
    """
    def __init__(self, translation_engine: TranslationEngine, target_speech_rate_syllables_per_sec: float = 4.0):
        self.translation_engine = translation_engine
        self.target_speech_rate = target_speech_rate_syllables_per_sec
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.encoder = None
        
        # Load NN Predictor if available
        model_path = "models/duration_predictor.pt"
        if os.path.exists(model_path):
            try:
                from ai.duration_align.duration_predictor_model import DurationPredictor
                from ai.duration_align.train import KNOWN_LANGUAGES
                from sentence_transformers import SentenceTransformer
                
                self.model = DurationPredictor(num_languages=len(KNOWN_LANGUAGES), embed_dim=384)
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.model.to(self.device)
                self.model.eval()
                
                self.encoder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
                self.known_languages = KNOWN_LANGUAGES
                print("Successfully loaded Custom NN Duration Predictor!")
            except Exception as e:
                print(f"Failed to load NN Duration Predictor: {e}. Falling back to heuristic.")
                self.model = None

    def _get_language_one_hot(self, lang):
        idx = self.known_languages.index(lang) if lang in self.known_languages else 0
        vec = [0.0] * len(self.known_languages)
        vec[idx] = 1.0
        return vec

    def _count_syllables(self, text: str) -> int:
        """Cheap heuristic fallback for syllable counting in English."""
        text = text.lower()
        text = re.sub(r'[^a-z]', '', text)
        if not text: return 0
        count = len(re.findall(r'[aeiouy]+', text))
        if text.endswith('e') and count > 1 and not text.endswith('le'):
            count -= 1
        return max(1, count)

    def estimate_duration(self, text: str, target_lang: str) -> float:
        if self.model and self.encoder:
            # Use Trained NN
            with torch.no_grad():
                emb = self.encoder.encode([text], convert_to_tensor=True, show_progress_bar=False).to(self.device)
                char_c = torch.tensor([[len(text)]], dtype=torch.float32).to(self.device)
                word_c = torch.tensor([[len(text.split())]], dtype=torch.float32).to(self.device)
                lang_oh = torch.tensor([self._get_language_one_hot(target_lang)], dtype=torch.float32).to(self.device)
                pred = self.model(emb, char_c, word_c, lang_oh)
                return max(0.1, pred.item())
        else:
            # Fallback to Heuristic
            syllables = self._count_syllables(text)
            return syllables / self.target_speech_rate

    def process_segment(self, segment: TranscriptSegment, target_lang: str) -> TranscriptSegment:
        slot_duration = segment.end - segment.start
        if slot_duration <= 0:
            slot_duration = 1.0 # fallback

        # 1. Translate normally
        source_lang = "eng_Latn" # Simplified for MVP
        translated = self.translation_engine.translate(segment.source_text, source_lang, target_lang)
        segment.translated_text = translated

        # 2. Estimate duration
        est_duration = self.estimate_duration(translated, target_lang)
        segment.target_duration_estimate_sec = est_duration

        # 3. Check fit (+/- 15%)
        ratio = est_duration / slot_duration
        
        # 4. Rewrite logic (MVP heuristic: remove filler words if too long)
        final_text = translated
        pre_rewrite_est = est_duration
        if ratio > 1.15:
            # simple mock rewrite: drop known filler words
            for filler in [" actually", " literally", " basically", " just", " you know"]:
                final_text = final_text.replace(filler, "")
            
            est_duration = self.estimate_duration(final_text, target_lang)
            segment.target_duration_estimate_sec = est_duration
            
        segment.duration_adjusted_text = final_text.strip()
        
        # Log exact duration checks per requirement
        estimator_type = "NN" if self.model else "Heuristic"
        print(f"Duration Log [{estimator_type}] -> segment_id: {getattr(segment, 'id', 'unknown')}, source duration: {slot_duration:.2f}s, "
              f"translated estimate: {pre_rewrite_est:.2f}s, post-rewrite estimate: {est_duration:.2f}s")
              
        return segment
