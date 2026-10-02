from abc import ABC, abstractmethod
from typing import List

class TranslationEngine(ABC):
    """
    Abstract base class for all translation engines.
    """
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translates a single string of text.
        """
        pass
    
    @abstractmethod
    def translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """
        Translates a batch of strings.
        """
        pass
