from abc import ABC, abstractmethod

class TTSEngine(ABC):
    """
    Abstract base class for all Text-to-Speech engines.
    """
    
    @abstractmethod
    def synthesize(self, text: str, output_path: str, speaker_reference_path: str = None) -> str:
        """
        Synthesizes text into speech and saves it to output_path.
        
        Args:
            text (str): The text to synthesize.
            output_path (str): The path to save the generated audio file (WAV).
            speaker_reference_path (str): Optional path to a reference audio file for voice cloning.
            
        Returns:
            str: Path to the generated audio file.
        """
        pass
