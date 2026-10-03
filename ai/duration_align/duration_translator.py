import re
import math
from ai.common.schemas import TranscriptSegment
from ai.translation.base import TranslationEngine

class DurationAwareTranslator:
    """
    Implements the MVP algorithm for duration-aware translation.
    1. Translate normally.
    2. Estimate synthesized duration (syllables / target_speech_rate).
    3. Check if estimated_duration is within +/-15% of slot_duration.
    4. If too long, rewrite to be shorter (mocked via heuristic).
    """
    def __init__(self, translation_engine: TranslationEngine, target_speech_rate_syllables_per_sec: float = 4.0):
        self.translation_engine = translation_engine
        self.target_speech_rate = target_speech_rate_syllables_per_sec

    def _count_syllables(self, text: str) -> int:
        """
        Cheap heuristic for syllable counting in English.
        """
        text = text.lower()
        text = re.sub(r'[^a-z]', '', text)
        if not text:
            return 0
        count = len(re.findall(r'[aeiouy]+', text))
        if text.endswith('e') and count > 1 and not text.endswith('le'):
            count -= 1
        return max(1, count)

    def process_segment(self, segment: TranscriptSegment, target_lang: str) -> TranscriptSegment:
        slot_duration = segment.end - segment.start
        if slot_duration <= 0:
            slot_duration = 1.0 # fallback

        # 1. Translate normally
        source_lang = "eng_Latn" # Simplified for MVP
        translated = self.translation_engine.translate(segment.source_text, source_lang, target_lang)
        segment.translated_text = translated

        # 2. Estimate duration
        syllables = self._count_syllables(translated)
        est_duration = syllables / self.target_speech_rate
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
            
            new_syllables = self._count_syllables(final_text)
            est_duration = new_syllables / self.target_speech_rate
            segment.target_duration_estimate_sec = est_duration
            
        segment.duration_adjusted_text = final_text.strip()
        
        # Log exact duration checks per requirement
        print(f"Duration Log -> segment_id: {getattr(segment, 'id', 'unknown')}, source duration: {slot_duration:.2f}s, "
              f"translated estimate: {pre_rewrite_est:.2f}s, post-rewrite estimate: {est_duration:.2f}s")
              
        return segment
