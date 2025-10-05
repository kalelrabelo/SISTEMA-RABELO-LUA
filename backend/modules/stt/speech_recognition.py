"""
Speech-to-Text module for Lua TTS System
"""
import os
import tempfile
import wave
import json
from typing import Optional, Dict, Any
from pathlib import Path
import logging

import numpy as np
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """Speech-to-Text engine with multiple providers support"""
    
    def __init__(self):
        """Initialize speech recognizer"""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Language settings
        self.language = "pt-BR"
        
        # Available STT providers
        self.providers = {
            "google": self._recognize_google,
            "google_cloud": self._recognize_google_cloud,
            "azure": self._recognize_azure,
            "wit": self._recognize_wit,
            "whisper": self._recognize_whisper
        }
        
        self.default_provider = "google"  # Free Google Web Speech API
        
    async def transcribe_audio(
        self,
        audio_data: bytes,
        provider: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio data in bytes
            provider: STT provider to use
            language: Language code
            
        Returns:
            Dictionary with transcript and metadata
        """
        provider = provider or self.default_provider
        language = language or self.language
        
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        try:
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                temp_path = tmp.name
            
            # Load audio with speech_recognition
            with sr.AudioFile(temp_path) as source:
                audio = self.recognizer.record(source)
            
            # Transcribe using selected provider
            result = await self.providers[provider](audio, language)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    async def _recognize_google(self, audio: sr.AudioData, language: str) -> Dict[str, Any]:
        """Use Google Web Speech API (free, no API key required)"""
        try:
            transcript = self.recognizer.recognize_google(
                audio,
                language=language,
                show_all=True
            )
            
            if isinstance(transcript, dict) and 'alternative' in transcript:
                # Get best transcript
                best = transcript['alternative'][0]
                return {
                    "success": True,
                    "transcript": best.get('transcript', ''),
                    "confidence": best.get('confidence', 0.0),
                    "alternatives": transcript['alternative'],
                    "provider": "google",
                    "language": language
                }
            elif isinstance(transcript, str):
                return {
                    "success": True,
                    "transcript": transcript,
                    "confidence": 1.0,
                    "alternatives": [],
                    "provider": "google",
                    "language": language
                }
            else:
                return {
                    "success": False,
                    "error": "No transcript available",
                    "provider": "google"
                }
                
        except sr.UnknownValueError:
            return {
                "success": False,
                "error": "Could not understand audio",
                "provider": "google"
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "error": f"Google API error: {e}",
                "provider": "google"
            }
    
    async def _recognize_google_cloud(self, audio: sr.AudioData, language: str) -> Dict[str, Any]:
        """Use Google Cloud Speech-to-Text (requires API key)"""
        # Implementation requires Google Cloud credentials
        return {
            "success": False,
            "error": "Google Cloud STT not configured",
            "provider": "google_cloud"
        }
    
    async def _recognize_azure(self, audio: sr.AudioData, language: str) -> Dict[str, Any]:
        """Use Azure Speech Services (requires API key)"""
        # Implementation requires Azure credentials
        return {
            "success": False,
            "error": "Azure STT not configured",
            "provider": "azure"
        }
    
    async def _recognize_wit(self, audio: sr.AudioData, language: str) -> Dict[str, Any]:
        """Use Wit.ai (requires API key)"""
        # Implementation requires Wit.ai API key
        return {
            "success": False,
            "error": "Wit.ai not configured",
            "provider": "wit"
        }
    
    async def _recognize_whisper(self, audio: sr.AudioData, language: str) -> Dict[str, Any]:
        """Use OpenAI Whisper (local or API)"""
        try:
            # Try to use local Whisper model
            import whisper
            
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio.get_wav_data())
                temp_path = tmp.name
            
            # Load Whisper model (base model for balance between speed and accuracy)
            model = whisper.load_model("base")
            
            # Transcribe
            result = model.transcribe(
                temp_path,
                language=language[:2],  # Whisper uses 2-letter codes
                fp16=False
            )
            
            # Clean up
            os.unlink(temp_path)
            
            return {
                "success": True,
                "transcript": result["text"],
                "confidence": 1.0,
                "segments": result.get("segments", []),
                "provider": "whisper",
                "language": result.get("language", language)
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "Whisper not installed. Install with: pip install openai-whisper",
                "provider": "whisper"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Whisper error: {e}",
                "provider": "whisper"
            }
    
    async def transcribe_streaming(
        self,
        audio_stream: bytes,
        provider: Optional[str] = None
    ) -> str:
        """
        Transcribe audio stream in real-time
        
        Args:
            audio_stream: Audio stream bytes
            provider: STT provider
            
        Returns:
            Partial transcript
        """
        # For real-time transcription, we need smaller chunks
        # This is a simplified version - real implementation would need WebRTC
        result = await self.transcribe_audio(audio_stream, provider)
        return result.get("transcript", "") if result.get("success") else ""
    
    def process_audio_for_vad(self, audio_data: bytes) -> bytes:
        """
        Process audio with Voice Activity Detection
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Processed audio with silence removed
        """
        try:
            # Convert bytes to AudioSegment
            audio = AudioSegment.from_wav(audio_data)
            
            # Split on silence
            chunks = split_on_silence(
                audio,
                min_silence_len=500,  # 500ms of silence
                silence_thresh=-40,    # Silence threshold in dB
                keep_silence=250       # Keep 250ms of silence at boundaries
            )
            
            if not chunks:
                return audio_data
            
            # Combine chunks
            processed = AudioSegment.empty()
            for chunk in chunks:
                processed += chunk
            
            # Export to bytes
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                processed.export(tmp.name, format="wav")
                tmp.seek(0)
                result = tmp.read()
                os.unlink(tmp.name)
            
            return result
            
        except Exception as e:
            logger.error(f"VAD processing failed: {e}")
            return audio_data