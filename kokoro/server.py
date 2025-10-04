"""
Kokoro TTS Server - Sistema de Síntese de Voz
Sistema LUA - IA Conversacional
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import asyncio
import logging
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime
import redis.asyncio as redis
from contextlib import asynccontextmanager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Diretórios
MODELS_DIR = Path("/app/models")
OUTPUT_DIR = Path("/app/output")
CACHE_DIR = Path("/app/cache")

# Criar diretórios se não existirem
MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Configurações
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Cliente Redis global
redis_client: Optional[redis.Redis] = None

# TTS Engine (será inicializado no startup)
tts_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    global redis_client, tts_engine
    
    # Startup
    logger.info("🎙️ Iniciando Kokoro TTS Server...")
    
    # Conectar ao Redis
    try:
        redis_client = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Redis conectado")
    except Exception as e:
        logger.warning(f"⚠️ Redis não disponível: {e}")
    
    # Inicializar TTS
    try:
        from TTS.api import TTS
        
        # Lista de modelos disponíveis
        available_models = TTS().list_models()
        logger.info(f"📦 Modelos disponíveis: {len(available_models)}")
        
        # Usar modelo multi-idioma
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        
        # Tentar modelo português se disponível
        pt_models = [m for m in available_models if 'portuguese' in m.lower() or 'pt' in m.lower()]
        if pt_models:
            model_name = pt_models[0]
            logger.info(f"🇧🇷 Usando modelo português: {model_name}")
        else:
            logger.info(f"🌍 Usando modelo multilíngue: {model_name}")
        
        # Inicializar TTS
        tts_engine = TTS(model_name=model_name, progress_bar=False, gpu=False)
        logger.info("✅ TTS Engine inicializado")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar TTS: {e}")
        # Criar mock engine para desenvolvimento
        class MockTTS:
            def tts_to_file(self, text, file_path, language=None, speaker=None):
                # Criar arquivo de áudio vazio para testes
                with open(file_path, 'wb') as f:
                    f.write(b'MOCK_AUDIO_DATA')
                return file_path
        
        tts_engine = MockTTS()
        logger.warning("⚠️ Usando Mock TTS Engine")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando Kokoro TTS Server...")
    if redis_client:
        await redis_client.close()

# Criar aplicação
app = FastAPI(
    title="Kokoro TTS Server",
    description="Servidor de síntese de voz para o Sistema LUA",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "pt"
    voice: Optional[str] = None
    speed: Optional[float] = 1.0
    format: Optional[str] = "wav"

class TTSResponse(BaseModel):
    success: bool
    audio_url: Optional[str] = None
    cached: bool = False
    error: Optional[str] = None

# Rotas
@app.get("/api/voice/status")
@app.get("/health")
async def health_check():
    """Verificar status do servidor"""
    return {
        "status": "healthy",
        "service": "Kokoro TTS",
        "timestamp": datetime.now().isoformat(),
        "engine": "TTS" if tts_engine else "Mock"
    }

@app.post("/api/voice/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest, background_tasks: BackgroundTasks):
    """Sintetizar fala a partir de texto"""
    
    if not request.text:
        raise HTTPException(status_code=400, detail="Texto não pode estar vazio")
    
    try:
        # Gerar hash do texto para cache
        text_hash = hashlib.md5(f"{request.text}{request.language}{request.voice}".encode()).hexdigest()
        cache_key = f"tts:{text_hash}"
        output_filename = f"{text_hash}.{request.format}"
        output_path = OUTPUT_DIR / output_filename
        
        # Verificar cache no Redis
        if redis_client:
            cached_file = await redis_client.get(cache_key)
            if cached_file and Path(cached_file).exists():
                logger.info(f"✅ Áudio encontrado no cache: {cached_file}")
                return TTSResponse(
                    success=True,
                    audio_url=f"/audio/{output_filename}",
                    cached=True
                )
        
        # Se não está em cache, gerar novo áudio
        logger.info(f"🎙️ Gerando áudio para: {request.text[:50]}...")
        
        # Mapear idiomas
        language_map = {
            "pt": "pt",
            "pt-BR": "pt",
            "en": "en",
            "es": "es",
            "fr": "fr",
            "de": "de",
            "it": "it",
            "ja": "ja",
            "ko": "ko",
            "zh": "zh-cn"
        }
        
        language = language_map.get(request.language, "pt")
        
        # Gerar áudio
        if tts_engine:
            tts_engine.tts_to_file(
                text=request.text,
                file_path=str(output_path),
                language=language,
                speaker=request.voice
            )
            
            # Salvar no cache Redis
            if redis_client and output_path.exists():
                await redis_client.set(cache_key, str(output_path), ex=3600)  # 1 hora de cache
            
            logger.info(f"✅ Áudio gerado: {output_path}")
            
            # Limpar arquivos antigos em background
            background_tasks.add_task(cleanup_old_files)
            
            return TTSResponse(
                success=True,
                audio_url=f"/audio/{output_filename}",
                cached=False
            )
        else:
            raise Exception("TTS Engine não disponível")
            
    except Exception as e:
        logger.error(f"❌ Erro ao sintetizar fala: {e}")
        return TTSResponse(
            success=False,
            error=str(e)
        )

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Servir arquivo de áudio gerado"""
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=file_path,
        media_type="audio/wav",
        headers={
            "Cache-Control": "public, max-age=3600",
        }
    )

@app.get("/api/voice/languages")
async def list_languages():
    """Listar idiomas disponíveis"""
    return {
        "languages": [
            {"code": "pt", "name": "Português"},
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Español"},
            {"code": "fr", "name": "Français"},
            {"code": "de", "name": "Deutsch"},
            {"code": "it", "name": "Italiano"},
            {"code": "ja", "name": "日本語"},
            {"code": "ko", "name": "한국어"},
            {"code": "zh", "name": "中文"}
        ]
    }

@app.delete("/api/voice/cache")
async def clear_cache():
    """Limpar cache de áudio"""
    try:
        # Limpar arquivos do disco
        for file in OUTPUT_DIR.glob("*.wav"):
            file.unlink()
        for file in OUTPUT_DIR.glob("*.mp3"):
            file.unlink()
        
        # Limpar cache Redis
        if redis_client:
            keys = await redis_client.keys("tts:*")
            if keys:
                await redis_client.delete(*keys)
        
        return {"message": "Cache limpo com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def cleanup_old_files():
    """Limpar arquivos antigos (mais de 1 hora)"""
    try:
        import time
        current_time = time.time()
        
        for file_path in OUTPUT_DIR.glob("*.*"):
            file_age = current_time - file_path.stat().st_mtime
            if file_age > 3600:  # 1 hora
                file_path.unlink()
                logger.info(f"🗑️ Arquivo antigo removido: {file_path}")
    except Exception as e:
        logger.error(f"Erro ao limpar arquivos: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)