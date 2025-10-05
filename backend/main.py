"""
Lua TTS System - Main FastAPI Application
Sistema de IA Conversacional com Kokoro-82M
"""
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import base64
from datetime import datetime

from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core import settings, logger
from backend.modules.lua import LuaAssistant
# Use the fixed version of TTS engine
from backend.modules.tts.kokoro_engine_fixed import KokoroEngine
from backend.modules.stt.speech_recognition import SpeechRecognizer

# Global instances
lua_assistant: Optional[LuaAssistant] = None
tts_engine: Optional[KokoroEngine] = None
stt_engine: Optional[SpeechRecognizer] = None


# Pydantic models
class TTSRequest(BaseModel):
    """Text-to-Speech request model"""
    text: str = Field(..., description="Text to synthesize")
    voice: Optional[str] = Field("luna", description="Voice to use")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed")
    
class VoiceMixRequest(BaseModel):
    """Voice mixing request model"""
    text: str = Field(..., description="Text to synthesize")
    voices: List[str] = Field(..., description="List of voices to mix")
    weights: Optional[List[float]] = Field(None, description="Voice weights")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed")
    
class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message")
    user_id: Optional[str] = Field(None, description="User identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    voice_response: Optional[bool] = Field(False, description="Return voice response")
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global lua_assistant, tts_engine, stt_engine
    
    # Startup
    logger.info("=" * 50)
    logger.info("🚀 Starting Lua TTS System...")
    logger.info("=" * 50)
    
    try:
        # Initialize TTS Engine
        logger.info("Initializing TTS Engine...")
        tts_engine = KokoroEngine()
        await tts_engine.initialize()
        
        # Initialize STT Engine
        logger.info("Initializing STT Engine...")
        stt_engine = SpeechRecognizer()
        
        # Initialize Lua Assistant
        logger.info("Initializing Lua Assistant...")
        lua_assistant = LuaAssistant()
        await lua_assistant.initialize()
        
        logger.info("=" * 50)
        logger.info("✅ System ready!")
        logger.info(f"🌐 API: http://{settings.host}:{settings.port}")
        logger.info(f"📚 Docs: http://{settings.host}:{settings.port}/docs")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
        
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Lua TTS System...")
    
    try:
        if lua_assistant:
            await lua_assistant.cleanup()
        if tts_engine:
            await tts_engine.cleanup()
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
        

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )


# Routes
@app.get("/")
async def root():
    """Root endpoint with system info"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "voices": "/api/voice/voices",
            "speak": "/api/voice/speak",
            "chat": "/api/chat",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "tts_engine": tts_engine is not None and tts_engine.is_initialized,
            "lua_assistant": lua_assistant is not None and lua_assistant.is_initialized
        }
    }


@app.get("/api/voice/voices")
async def get_voices():
    """Get available voices"""
    if not tts_engine:
        raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
    voices = tts_engine.get_available_voices()
    return {
        "success": True,
        "voices": voices,
        "default": settings.default_voice,
        "count": len(voices)
    }


@app.post("/api/voice/speak")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    if not tts_engine:
        raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
    try:
        logger.info(f"TTS request: '{request.text[:50]}...' with voice '{request.voice}'")
        
        async def audio_generator():
            async for chunk in tts_engine.generate_speech(
                text=request.text,
                voice=request.voice,
                speed=request.speed
            ):
                yield chunk
                
        return StreamingResponse(
            audio_generator(),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=speech.wav",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/mix")
async def mix_voices(request: VoiceMixRequest):
    """Generate speech with mixed voices"""
    if not tts_engine:
        raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
    try:
        logger.info(f"Voice mix request: {len(request.voices)} voices")
        
        async def audio_generator():
            async for chunk in tts_engine.mix_voices(
                text=request.text,
                voices=request.voices,
                weights=request.weights,
                speed=request.speed
            ):
                yield chunk
                
        return StreamingResponse(
            audio_generator(),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=mixed_speech.wav",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"Voice mixing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat_with_lua(request: ChatRequest):
    """Chat with Lua Assistant"""
    if not lua_assistant:
        raise HTTPException(status_code=503, detail="Lua Assistant not initialized")
        
    try:
        logger.info(f"Chat request from {request.user_id or 'anonymous'}")
        
        # Process message
        response = await lua_assistant.process_message(
            message=request.message,
            user_id=request.user_id,
            context=request.context
        )
        
        # Add voice response if requested
        if request.voice_response and response["success"]:
            audio_data = b""
            async for chunk in lua_assistant.speak(response["response"]):
                audio_data += chunk
                
            # Encode audio as base64
            response["audio"] = base64.b64encode(audio_data).decode("utf-8")
            response["audio_format"] = "wav"
            
        return response
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/voice")
async def chat_with_voice_response(request: ChatRequest):
    """Chat with Lua and get voice response"""
    if not lua_assistant:
        raise HTTPException(status_code=503, detail="Lua Assistant not initialized")
        
    try:
        logger.info(f"Voice chat request from {request.user_id or 'anonymous'}")
        
        async def audio_generator():
            async for chunk in lua_assistant.speak_response(
                message=request.message,
                user_id=request.user_id
            ):
                yield chunk
                
        return StreamingResponse(
            audio_generator(),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=lua_response.wav",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"Voice chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history")
async def get_chat_history():
    """Get chat history"""
    if not lua_assistant:
        raise HTTPException(status_code=503, detail="Lua Assistant not initialized")
        
    return {
        "success": True,
        "history": lua_assistant.get_conversation_history(),
        "session_id": lua_assistant.session_id
    }


@app.delete("/api/chat/history")
async def clear_chat_history():
    """Clear chat history"""
    if not lua_assistant:
        raise HTTPException(status_code=503, detail="Lua Assistant not initialized")
        
    lua_assistant.clear_conversation()
    return {"success": True, "message": "Chat history cleared"}


# ============= STT Endpoints =============

@app.post("/api/stt/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    provider: Optional[str] = Query(None, description="STT provider"),
    language: Optional[str] = Query("pt-BR", description="Language code")
):
    """Transcribe audio file to text"""
    if not stt_engine:
        raise HTTPException(status_code=503, detail="STT engine not initialized")
    
    try:
        # Read audio file
        audio_data = await file.read()
        
        # Transcribe
        result = await stt_engine.transcribe_audio(
            audio_data=audio_data,
            provider=provider,
            language=language
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/conversation")
async def websocket_conversation(websocket):
    """WebSocket endpoint for real-time conversation"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "audio":
                # Handle audio data for STT
                audio_data = base64.b64decode(data["audio"])
                
                # Transcribe audio
                result = await stt_engine.transcribe_audio(audio_data)
                
                if result.get("success"):
                    transcript = result["transcript"]
                    
                    # Send transcript to client
                    await websocket.send_json({
                        "type": "transcript",
                        "text": transcript
                    })
                    
                    # Get Lua response
                    response = await lua_assistant.process_message(
                        message=transcript,
                        user_id=data.get("user_id", "websocket-user")
                    )
                    
                    # Send text response
                    await websocket.send_json({
                        "type": "response",
                        "text": response["response"]
                    })
                    
                    # Generate and send audio response
                    audio_chunks = []
                    async for chunk in tts_engine.generate_speech(
                        text=response["response"],
                        voice="luna"
                    ):
                        audio_chunks.append(chunk)
                    
                    # Combine chunks and send
                    audio_data = b"".join(audio_chunks)
                    await websocket.send_json({
                        "type": "audio",
                        "data": base64.b64encode(audio_data).decode("utf-8")
                    })
                    
            elif data.get("type") == "text":
                # Handle text message
                message = data["message"]
                
                # Get Lua response
                response = await lua_assistant.process_message(
                    message=message,
                    user_id=data.get("user_id", "websocket-user")
                )
                
                # Send response
                await websocket.send_json({
                    "type": "response",
                    "text": response["response"]
                })
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )