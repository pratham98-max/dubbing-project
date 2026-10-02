import pytest
from ai.common.schemas import TranscriptSegment
from ai.translation.nllb_engine import NLLBEngine
from ai.duration_align.duration_translator import DurationAwareTranslator

def test_duration_translator_fit():
    engine = NLLBEngine(device="cpu")
    translator = DurationAwareTranslator(engine, target_speech_rate_syllables_per_sec=4.0)
    
    # Create a dummy segment with a slot of 1.5 seconds.
    segment = TranscriptSegment(
        id="seg1",
        start=0.0,
        end=1.5,
        source_text="आप कहाँ जा रहे हैं?",
        asr_confidence=0.99
    )
    
    # "Where are you going?" has ~5 syllables. 5 / 4.0 = 1.25s.
    # 1.25s is within 15% of 1.5s (0.83 ratio). No rewrite needed.
    processed = translator.process_segment(segment, "eng_Latn")
    
    assert processed.translated_text == "Where are you going?"
    assert processed.duration_adjusted_text == "Where are you going?"
    assert processed.target_duration_estimate_sec == 1.0
    
def test_duration_translator_too_long():
    engine = NLLBEngine(device="cpu")
    translator = DurationAwareTranslator(engine, target_speech_rate_syllables_per_sec=4.0)
    
    # Slot of 0.5s is way too short for a 5 syllable sentence (1.25s est)
    # Ratio = 1.25 / 0.5 = 2.5 (too long!). Our simple mock rewrite in MVP
    # tries to drop fillers but won't find any, but tests that the logic runs.
    segment = TranscriptSegment(
        id="seg2",
        start=0.0,
        end=0.5,
        source_text="आप कहाँ जा रहे हैं?",
        asr_confidence=0.99
    )
    processed = translator.process_segment(segment, "eng_Latn")
    
    # For now, it strips fillers (none present), so it remains the same
    # The actual acceptance threshold for time stretch is verified downstream.
    assert processed.duration_adjusted_text == "Where are you going?"
    assert processed.target_duration_estimate_sec > segment.end - segment.start
