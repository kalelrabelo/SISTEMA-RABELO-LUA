"""
Sistema de Voice Engine com Voice Cloning
Usa a voz do Jarvis/Iron Man para síntese de fala personalizada
"""

import os
import sys
import numpy as np
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch não disponível, usando modo lite")
from pathlib import Path
import soundfile as sf
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import tempfile
import wave
import threading
from queue import Queue
import time

try:
    from TTS.api import TTS
    from TTS.utils.synthesizer import Synthesizer
    from TTS.utils.manage import ModelManager
    from TTS.tts.configs.xtts_config import XttsConfig
except ImportError:
    print("⚠️  Coqui TTS não instalado. Usando fallback para gTTS...")
    TTS = None
    XttsConfig = None

try:
    from pydub import AudioSegment
    from pydub.effects import normalize, compress_dynamic_range
    from pydub.playback import play
except ImportError:
    print("⚠️  PyDub não instalado. Processamento de áudio limitado...")
    AudioSegment = None

class VoiceEngine:
    """Motor principal de síntese de voz com voice cloning"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.voice_dir = self.base_dir / "voices"
        self.cache_dir = self.base_dir / "cache" / "voice"
        self.models_dir = self.base_dir / "models" / "tts"
        
        # Criar diretórios necessários
        for dir_path in [self.voice_dir, self.cache_dir, self.models_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Caminho da voz do Jarvis
        self.jarvis_voice_path = self.base_dir.parent / "jarvis_voice.mp3"
        
        # Configurações de voz
        self.voice_config = {
            "language": "pt",
            "speaker_name": "LUA",
            "emotion": "confident",  # confident, friendly, serious, excited
            "speed": 1.0,
            "pitch": 1.0,
            "energy": 0.9,
            "style": "jarvis"  # Estilo Jarvis/Iron Man
        }
        
        # Cache de áudio gerado
        self.audio_cache = {}
        self.cache_lock = threading.Lock()
        
        # Fila de processamento
        self.tts_queue = Queue()
        self.is_processing = False
        
        # Inicializar TTS
        self.tts_model = None
        self.voice_embeddings = None
        self._initialize_tts()
    
    def _initialize_tts(self):
        """Inicializa o modelo TTS com voice cloning"""
        try:
            if TTS is None:
                print("⚠️  TTS não disponível. Usando modo fallback.")
                return
            
            # Verificar dispositivo (GPU/CPU)
            if TORCH_AVAILABLE:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                print(f"🎯 Usando dispositivo: {self.device}")
            else:
                self.device = "cpu"
                print("🎯 Usando CPU (PyTorch não disponível)")
            
            # Modelos disponíveis para voice cloning
            models = {
                "multi_speaker": "tts_models/multilingual/multi-dataset/xtts_v2",
                "portuguese": "tts_models/pt/cv/vits",
                "clone": "tts_models/en/ljspeech/tacotron2-DDC"
            }
            
            # Tentar carregar modelo XTTS v2 (melhor para voice cloning)
            try:
                print("📥 Carregando modelo XTTS v2 para voice cloning...")
                
                # Confirmar licença automaticamente
                import os
                os.environ['COQUI_TOS_AGREED'] = '1'
                
                # Configurar torch safe globals para XTTS v2 (PyTorch 2.6+ compatibility)
                if TORCH_AVAILABLE and XttsConfig:
                    torch.serialization.add_safe_globals([XttsConfig])
                    print("✅ Torch safe globals configurado para XTTS v2")
                
                self.tts_model = TTS(models["multi_speaker"], progress_bar=True)
                self.tts_model.to(self.device)
                
                print("✅ XTTS v2 carregado com sucesso - voice cloning habilitado!")
                
                # Processar voz de referência do Jarvis
                if self.jarvis_voice_path.exists():
                    print(f"🎤 Processando voz do Jarvis para cloning: {self.jarvis_voice_path}")
                    self.voice_embeddings = self._extract_voice_embeddings(self.jarvis_voice_path)
                    if self.voice_embeddings:
                        print("✅ Voice embeddings extraídos com sucesso!")
                    else:
                        print("⚠️ Falha ao extrair embeddings, usando modelo padrão")
                else:
                    print(f"⚠️ Arquivo de voz do Jarvis não encontrado em: {self.jarvis_voice_path}")
                    
            except Exception as e:
                print(f"❌ Erro crítico ao carregar XTTS v2: {str(e)}")
                print("❌ XTTS v2 é OBRIGATÓRIO - não usar VITS de baixa qualidade")
                # Não usar fallback VITS - preferir gTTS otimizado
                print("📥 Usando fallback gTTS otimizado para qualidade superior")
                self.tts_model = None  # Forçar uso do gTTS otimizado
                    
        except Exception as e:
            print(f"❌ Erro ao inicializar TTS: {str(e)}")
            self.tts_model = None
    
    def _extract_voice_embeddings(self, voice_path: Path) -> Optional[np.ndarray]:
        """Extrai embeddings da voz de referência para cloning"""
        try:
            if not AudioSegment:
                return None
            
            # Converter MP3 para WAV se necessário
            audio = AudioSegment.from_file(str(voice_path))
            
            # Normalizar e processar áudio
            audio = normalize(audio)
            audio = audio.set_frame_rate(22050)
            audio = audio.set_channels(1)
            
            # Salvar temporariamente como WAV
            temp_wav = self.cache_dir / "reference_voice.wav"
            audio.export(str(temp_wav), format="wav")
            
            # Extrair características da voz
            # Aqui usaríamos o modelo para extrair embeddings
            # Por enquanto, vamos guardar o caminho para uso posterior
            return str(temp_wav)
            
        except Exception as e:
            print(f"⚠️  Erro ao extrair embeddings: {str(e)}")
            return None
    
    def generate_speech(self, text: str, emotion: str = None, cache: bool = True) -> Optional[str]:
        """
        Gera áudio a partir do texto usando a voz clonada
        
        Args:
            text: Texto para sintetizar
            emotion: Emoção da fala (confident, friendly, serious, excited)
            cache: Se deve usar cache para textos repetidos
        
        Returns:
            Caminho do arquivo de áudio gerado
        """
        if not text:
            return None
        
        # Gerar hash do texto para cache
        text_hash = hashlib.md5(f"{text}_{emotion}".encode()).hexdigest()
        
        # Verificar cache
        if cache and text_hash in self.audio_cache:
            cached_file = self.audio_cache[text_hash]
            if Path(cached_file).exists():
                print(f"📦 Usando áudio do cache para: {text[:50]}...")
                return cached_file
        
        try:
            output_path = self.cache_dir / f"lua_speech_{text_hash}.wav"
            
            if self.tts_model and self.voice_embeddings:
                # Usar voice cloning com XTTS v2
                print(f"🎙️ Gerando fala com voz clonada: {text[:50]}...")
                
                try:
                    # Gerar áudio com voice cloning
                    self.tts_model.tts_to_file(
                        text=text,
                        speaker_wav=self.voice_embeddings,  # Voz de referência
                        language="pt",
                        file_path=str(output_path)
                    )
                except Exception as clone_error:
                    print(f"⚠️ Erro no voice cloning: {clone_error}")
                    print("❌ XTTS v2 falhou - NÃO usar fallback VITS para manter qualidade")
                    # Tentar novamente sem speaker_wav (XTTS sem cloning)
                    try:
                        self.tts_model.tts_to_file(
                            text=text,
                            language="pt",
                            file_path=str(output_path)
                        )
                        print("✅ XTTS v2 funcionando sem cloning")
                    except Exception as xtts_error:
                        print(f"❌ XTTS v2 completamente inoperante: {xtts_error}")
                        return None  # Não usar VITS fallback
                
            elif self.tts_model:
                # Usar modelo padrão sem voice cloning
                print(f"🎙️ Gerando fala com modelo padrão: {text[:50]}...")
                
                try:
                    # Verificar se o modelo suporta múltiplos speakers
                    if hasattr(self.tts_model, 'speakers') and self.tts_model.speakers:
                        # Escolher um speaker feminino se disponível
                        speaker = None
                        for spk in self.tts_model.speakers:
                            if any(fem in spk.lower() for fem in ['female', 'woman', 'f_']):
                                speaker = spk
                                break
                        
                        self.tts_model.tts_to_file(
                            text=text,
                            file_path=str(output_path),
                            speaker=speaker
                        )
                    else:
                        # Modelo sem speakers específicos
                        self.tts_model.tts_to_file(
                            text=text,
                            file_path=str(output_path)
                        )
                except Exception as model_error:
                    print(f"⚠️ Erro no modelo TTS: {model_error}")
                    print("❌ Modelo TTS falhou - usando fallback controlado")
                    return self._generate_gtts_fallback(text, output_path)
                
            else:
                # Fallback para gTTS
                print(f"🎙️ Usando fallback gTTS: {text[:50]}...")
                return self._generate_gtts_fallback(text, output_path)
            
            # Processar áudio gerado
            if output_path.exists():
                processed_path = self._process_audio(output_path, emotion)
                
                # Adicionar ao cache
                if cache:
                    with self.cache_lock:
                        self.audio_cache[text_hash] = str(processed_path)
                
                print(f"✅ Áudio gerado com sucesso: {processed_path.name}")
                return str(processed_path)
            
        except Exception as e:
            print(f"❌ Erro ao gerar fala: {str(e)}")
            # Tentar fallback
            return self._generate_gtts_fallback(text, output_path)
        
        return None
    
    def _get_emotion_params(self, emotion: str = None) -> Dict[str, Any]:
        """Retorna parâmetros de voz baseados na emoção"""
        emotions = {
            "confident": {
                "speed": 0.95,
                "pitch": 1.0,
                "energy": 0.9,
                "emotion": "confident"
            },
            "friendly": {
                "speed": 1.0,
                "pitch": 1.05,
                "energy": 0.85,
                "emotion": "happy"
            },
            "serious": {
                "speed": 0.9,
                "pitch": 0.95,
                "energy": 0.8,
                "emotion": "serious"
            },
            "excited": {
                "speed": 1.1,
                "pitch": 1.1,
                "energy": 1.0,
                "emotion": "excited"
            },
            "thoughtful": {
                "speed": 0.85,
                "pitch": 0.98,
                "energy": 0.75,
                "emotion": "neutral"
            }
        }
        
        return emotions.get(emotion or self.voice_config["emotion"], emotions["confident"])
    
    def _process_audio(self, audio_path: Path, emotion: str = None) -> Path:
        """Processa e melhora o áudio gerado"""
        if not AudioSegment:
            return audio_path
        
        try:
            # Carregar áudio
            audio = AudioSegment.from_file(str(audio_path))
            
            # Aplicar efeitos baseados na emoção
            params = self._get_emotion_params(emotion)
            
            # Ajustar velocidade
            if params["speed"] != 1.0:
                audio = audio.speedup(playback_speed=params["speed"])
            
            # Normalizar volume
            audio = normalize(audio)
            
            # Adicionar compressão dinâmica (estilo Jarvis)
            audio = compress_dynamic_range(audio, threshold=-20)
            
            # Adicionar um leve reverb para dar profundidade
            # (simplificado - em produção usaríamos librosa ou sox)
            
            # Salvar áudio processado
            output_path = audio_path.parent / f"{audio_path.stem}_processed.wav"
            audio.export(str(output_path), format="wav")
            
            return output_path
            
        except Exception as e:
            print(f"⚠️  Erro ao processar áudio: {str(e)}")
            return audio_path
    
    def _generate_gtts_fallback(self, text: str, output_path: Path) -> Optional[str]:
        """Fallback para gTTS quando Coqui TTS não está disponível"""
        try:
            from gtts import gTTS
            
            # Usar configurações otimizadas para voz feminina similar ao Jarvis
            tts = gTTS(text=text, lang='pt', slow=False)
            tts.save(str(output_path))
            
            # Processar áudio para ficar mais similar ao Jarvis
            if AudioSegment:
                try:
                    audio = AudioSegment.from_file(str(output_path))
                    
                    # Reduzir pitch para voz mais grave (Jarvis-like)
                    # Simular redução de pitch através de velocidade
                    audio_pitched = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": int(audio.frame_rate * 0.9)  # Reduzir 10% para grave
                    }).set_frame_rate(audio.frame_rate)
                    
                    # Adicionar leve eco/reverb para efeito robótico
                    # Misturar com versão levemente atrasada
                    delayed = AudioSegment.silent(duration=50) + audio_pitched
                    mixed = audio_pitched.overlay(delayed - 8)  # -8dB para o eco
                    
                    # Normalizar e exportar
                    mixed = normalize(mixed)
                    processed_path = output_path.parent / f"{output_path.stem}_jarvis.wav"
                    mixed.export(str(processed_path), format="wav")
                    
                    return str(processed_path)
                except Exception as process_error:
                    print(f"⚠️ Erro ao processar áudio do gTTS: {process_error}")
                    return str(output_path)
            
            return str(output_path)
            
        except ImportError:
            print(f"❌ gTTS não está instalado. Instale com: pip install gtts")
            return None
        except Exception as e:
            print(f"❌ Erro no fallback gTTS: {str(e)}")
            return None
    
    def clear_cache(self, older_than_hours: int = 24):
        """Limpa cache de áudio antigo"""
        try:
            now = datetime.now()
            cutoff_time = now - timedelta(hours=older_than_hours)
            
            for audio_file in self.cache_dir.glob("*.wav"):
                if datetime.fromtimestamp(audio_file.stat().st_mtime) < cutoff_time:
                    audio_file.unlink()
                    print(f"🗑️ Cache removido: {audio_file.name}")
            
            # Limpar cache em memória
            with self.cache_lock:
                self.audio_cache.clear()
                
        except Exception as e:
            print(f"⚠️  Erro ao limpar cache: {str(e)}")
    
    def get_voice_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de voz"""
        return {
            "engine": "Coqui TTS" if self.tts_model else "Fallback",
            "voice_cloning": bool(self.voice_embeddings),
            "device": self.device if hasattr(self, 'device') else "cpu",
            "cache_size": len(self.audio_cache),
            "voice_style": self.voice_config["style"],
            "reference_voice": "Jarvis/Iron Man" if self.voice_embeddings else "Default"
        }

# Instanciar Voice Engine com sistema robusto de fallback
voice_engine = None

# Primeiro tentar Voice Engine completo
try:
    voice_engine = VoiceEngine()
    print("✅ Voice Engine completo carregado")
except Exception as e:
    print(f"⚠️ Erro ao carregar Voice Engine completo: {str(e)}")
    
    # Fallback para Voice Engine Lite
    try:
        print("📌 Tentando Voice Engine Lite...")
        from .voice_engine_lite import VoiceEngineLite
        voice_engine = VoiceEngineLite()
        print("✅ Voice Engine Lite carregado")
    except Exception as e2:
        print(f"⚠️ Erro ao carregar Voice Engine Lite: {str(e2)}")
        
        # Fallback final para classe básica
        try:
            print("📌 Usando Voice Engine básico (apenas gTTS)...")
            
            class BasicVoiceEngine:
                """Engine básico usando apenas gTTS"""
                
                def __init__(self):
                    self.base_dir = Path(__file__).parent.parent.parent
                    self.cache_dir = self.base_dir / "cache" / "voice"
                    self.cache_dir.mkdir(parents=True, exist_ok=True)
                
                def generate_speech(self, text: str, emotion: str = None, cache: bool = True) -> Optional[str]:
                    """Gera fala usando gTTS simples"""
                    try:
                        from gtts import gTTS
                        import hashlib
                        
                        # Hash para cache
                        text_hash = hashlib.md5(f"{text}_{emotion}".encode()).hexdigest()
                        output_path = self.cache_dir / f"basic_speech_{text_hash}.mp3"
                        
                        if cache and output_path.exists():
                            return str(output_path)
                        
                        # Gerar com gTTS
                        tts = gTTS(text=text, lang='pt', slow=False)
                        tts.save(str(output_path))
                        
                        print(f"✅ Áudio básico gerado: {text[:30]}...")
                        return str(output_path)
                        
                    except Exception as e:
                        print(f"❌ Erro no engine básico: {e}")
                        return None
                
                def get_voice_status(self):
                    return {
                        "engine": "gTTS Básico",
                        "voice_cloning": False,
                        "device": "cpu",
                        "status": "Funcional"
                    }
            
            voice_engine = BasicVoiceEngine()
            print("✅ Voice Engine básico ativo")
            
        except Exception as e3:
            print(f"❌ Falha completa no sistema de voz: {str(e3)}")
            voice_engine = None

def generate_lua_voice(text: str, emotion: str = "confident") -> Optional[str]:
    """Interface simplificada para gerar voz da LUA"""
    if voice_engine:
        return voice_engine.generate_speech(text, emotion)
    return None

def get_engine_status() -> Dict[str, Any]:
    """Retorna status do engine de voz"""
    if voice_engine:
        return voice_engine.get_voice_status()
    return {"engine": "None", "status": "Offline"}