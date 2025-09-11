import io
import tempfile
import logging
from typing import Optional
from faster_whisper import WhisperModel
import soundfile as sf
import numpy as np


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioService:
    def __init__(self, model_size: str = "small"):
        """
        Initialize the audio service with Faster-Whisper.
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            logger.info(f"Loading Faster-Whisper model: {self.model_size}")
           
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def transcribe_audio(self, audio_data: bytes, sample_rate: int = 16000) -> Optional[str]:
        """
        Transcribe audio data to text using Faster-Whisper.
        
        Args:
            audio_data: Raw audio data as bytes
            sample_rate: Sample rate of the audio (default: 16000)
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            if self.model is None:
                logger.error("Model not loaded")
                return None
            
            
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
           
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            
            segments, info = self.model.transcribe(
                audio_float,
                beam_size=5,
                language="en",  
                condition_on_previous_text=False
            )
            
            
            transcribed_text = ""
            for segment in segments:
                transcribed_text += segment.text
            
            
            transcribed_text = transcribed_text.strip()
            
            if transcribed_text:
                logger.info(f"Transcription successful: {transcribed_text}")
                return transcribed_text
            else:
                logger.warning("No speech detected in audio")
                return None
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe audio from a file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            if self.model is None:
                logger.error("Model not loaded")
                return None
            
           
            segments, info = self.model.transcribe(
                file_path,
                beam_size=5,
                language="en",
                condition_on_previous_text=False
            )
            
           
            transcribed_text = ""
            for segment in segments:
                transcribed_text += segment.text
            
           
            transcribed_text = transcribed_text.strip()
            
            if transcribed_text:
                logger.info(f"Transcription successful: {transcribed_text}")
                return transcribed_text
            else:
                logger.warning("No speech detected in audio file")
                return None
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None


audio_service = AudioService(model_size="small")  

def get_audio_service() -> AudioService:
    """Get the global audio service instance."""
    return audio_service
