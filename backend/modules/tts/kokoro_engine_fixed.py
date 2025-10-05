"""
Kokoro TTS Engine for Portuguese (PT-BR)
Fixed version with proper dependencies
"""
import os
import tempfile
from typing import Optional, AsyncGenerator, Dict, List
from pathlib import Path
import logging

import numpy as np
import torch
import soundfile as sf

# Import TTS instead of kokoro
from TTS.api import TTS

logger = logging.getLogger(__name__)


class KokoroEngine:
    """Modern TTS Engine with PT-BR support using Coqui TTS"""
    
    # Portuguese voices mapping
    PTBR_VOICES = {
        "pt-BR-f1": "female_1",  # Female voice 1
        "pt-BR-f2": "female_2",  # Female voice 2
        "pt-BR-f3": "female_3",  # Female voice 3
        "pt-BR-m1": "male_1",    # Male voice 1
        "pt-BR-m2": "male_2",    # Male voice 2
        "luna": "female_luna",   # Luna's default voice
    }
    
    def __init__(self):
        """Initialize TTS engine"""
        self.device = self._get_device()
        self.model: Optional[TTS] = None
        self.is_initialized = False
        self.sample_rate = 22050
        
    def _get_device(self) -> str:
        """Determine the best available device"""
        if torch.cuda.is_available():
            logger.info("Using CUDA device")
            return "cuda"
        logger.info("Using CPU device")
        return "cpu"
        
    async def initialize(self) -> bool:
        """Initialize the TTS model"""
        try:
            logger.info("Initializing TTS Engine...")
            
            # Use a multilingual model that supports Portuguese
            # Using XTTS v2 which supports multiple languages including Portuguese
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            
            # Alternative: Use a specific Portuguese model if available
            # model_name = "tts_models/pt/cv/vits"
            
            # Initialize TTS
            self.model = TTS(model_name=model_name, progress_bar=False, gpu=(self.device == "cuda"))
            
            # Get sample rate from model
            if hasattr(self.model.synthesizer, 'output_sample_rate'):
                self.sample_rate = self.model.synthesizer.output_sample_rate
            elif hasattr(self.model, 'synthesizer') and hasattr(self.model.synthesizer, 'sample_rate'):
                self.sample_rate = self.model.synthesizer.sample_rate
            else:
                self.sample_rate = 22050  # Default
            
            # Warm up the model
            await self._warmup()
            
            self.is_initialized = True
            logger.info("✅ TTS Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            # Fallback to a simpler model
            try:
                logger.info("Trying fallback model...")
                self.model = TTS("tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
                self.is_initialized = True
                logger.info("✅ TTS Engine initialized with fallback model")
                return True
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                return False
            
    async def _warmup(self):
        """Warm up the model with a test generation"""
        try:
            logger.info("Warming up TTS model...")
            test_text = "Olá, eu sou a Lua."
            
            # Generate small test audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                if hasattr(self.model, 'tts_to_file'):
                    self.model.tts_to_file(
                        text=test_text,
                        file_path=tmp.name,
                        language="pt" if "multilingual" in str(self.model.model_name) else None
                    )
                logger.info("✅ Model warmup successful")
        except Exception as e:
            logger.warning(f"Warmup failed (non-critical): {e}")
            
    async def generate_speech(
        self,
        text: str,
        voice: str = "luna",
        speed: float = 1.0,
        lang_code: str = "pt"
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate speech from text
        
        Args:
            text: Text to synthesize
            voice: Voice identifier (currently ignored as we use single model)
            speed: Speech speed (0.5 to 2.0)
            lang_code: Language code ('pt' for Portuguese)
            
        Yields:
            Audio chunks in bytes
        """
        if not self.is_initialized:
            raise RuntimeError("Engine not initialized")
            
        try:
            logger.info(f"Generating speech: '{text[:50]}...' with voice '{voice}'")
            
            # Generate audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                temp_path = tmp.name
                
            try:
                # Generate audio file
                if hasattr(self.model, 'tts_to_file'):
                    # For multilingual models
                    if "multilingual" in str(self.model.model_name):
                        self.model.tts_to_file(
                            text=text,
                            file_path=temp_path,
                            language=lang_code,
                            speed=speed
                        )
                    else:
                        # For single language models
                        self.model.tts_to_file(
                            text=text,
                            file_path=temp_path
                        )
                    
                    # Read the generated audio
                    with open(temp_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    yield audio_bytes
                else:
                    # Alternative method using numpy array
                    wav = self.model.tts(text=text, language=lang_code if "multilingual" in str(self.model.model_name) else None)
                    
                    if isinstance(wav, torch.Tensor):
                        wav = wav.cpu().numpy()
                    elif not isinstance(wav, np.ndarray):
                        wav = np.array(wav)
                    
                    # Save to file
                    sf.write(temp_path, wav, self.sample_rate)
                    
                    with open(temp_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    yield audio_bytes
                    
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            raise
            
    async def mix_voices(
        self,
        text: str,
        voices: List[str],
        weights: Optional[List[float]] = None,
        speed: float = 1.0
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate speech with mixed voices (simplified version)
        Currently just uses the first voice
        """
        if not self.is_initialized:
            raise RuntimeError("Engine not initialized")
            
        if not voices:
            raise ValueError("At least one voice required")
        
        # For now, just use the first voice
        voice = voices[0] if voices else "luna"
        
        async for chunk in self.generate_speech(text, voice, speed):
            yield chunk
            
    def get_available_voices(self) -> Dict[str, str]:
        """Get list of available voices"""
        return {
            voice_id: f"Portuguese {desc}"
            for voice_id, desc in [
                ("pt-BR-f1", "Female 1"),
                ("pt-BR-f2", "Female 2"),
                ("pt-BR-f3", "Female 3"),
                ("pt-BR-m1", "Male 1"),
                ("pt-BR-m2", "Male 2"),
                ("luna", "Luna (Assistant)"),
            ]
        }
        
    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.model:
                del self.model
                self.model = None
                
            # Clear GPU cache if available
            if self.device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                
            self.is_initialized = False
            logger.info("TTS engine cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")