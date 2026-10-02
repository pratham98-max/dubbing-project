import pytest
from ai.translation.indictrans2_engine import IndicTrans2Engine
from ai.translation.nllb_engine import NLLBEngine

def test_indictrans2_engine():
    engine = IndicTrans2Engine(device="cpu")
    # Using the fixture text from the canonical schema
    source = "आप कहाँ जा रहे हैं?"
    result = engine.translate(source, "hin_Deva", "eng_Latn")
    assert result == "Where are you going?"
    assert len(result) > 0

def test_nllb_engine():
    engine = NLLBEngine(device="cpu")
    source = "आप कहाँ जा रहे हैं?"
    result = engine.translate(source, "hin_Deva", "eng_Latn")
    assert result == "Where are you going?"
    assert len(result) > 0
