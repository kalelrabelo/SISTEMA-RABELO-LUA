"""
Rotas da API para o sistema de voz da LUA
"""

from flask import Blueprint, request, jsonify
import base64
import os
from pathlib import Path

# Importar serviços
from src.services.voice_engine import generate_lua_voice, voice_engine

ai_voice_bp = Blueprint('ai_voice', __name__)

@ai_voice_bp.route('/status', methods=['GET'])
def voice_status():
    """Retorna status do sistema de voz"""
    try:
        if voice_engine:
            status = voice_engine.get_voice_status()
            return jsonify({
                'success': True,
                'status': status,
                'engine_loaded': True
            })
        else:
            return jsonify({
                'success': False,
                'status': {'engine': 'None', 'status': 'Offline'},
                'engine_loaded': False
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'engine_loaded': False
        }), 500

def convert_to_mp3_44k_stereo(audio_path):
    """
    Converte áudio para MP3 44.1kHz estéreo usando pydub + ffmpeg
    Garante formato consistente para o frontend
    """
    try:
        if not AudioSegment:
            print("⚠️ pydub não disponível - retornando arquivo original")
            return audio_path
        
        audio_path = Path(audio_path)
        
        # Verificar se já é MP3 com especificações corretas
        try:
            audio = AudioSegment.from_file(str(audio_path))
            
            # Converter para 44.1kHz estéreo
            audio = audio.set_frame_rate(44100)  # 44.1kHz
            audio = audio.set_channels(2)        # Estéreo
            
            # Normalizar volume para evitar distorções
            audio = normalize(audio)
            
            # Criar arquivo temporário MP3
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Exportar como MP3 com qualidade alta
            audio.export(
                tmp_path, 
                format="mp3",
                bitrate="128k",
                parameters=[
                    "-ar", "44100",  # Sample rate
                    "-ac", "2",      # Canais (estéreo)
                    "-q:a", "2"      # Qualidade alta
                ]
            )
            
            print(f"✅ Áudio convertido para MP3 44.1kHz estéreo: {tmp_path}")
            return tmp_path
            
        except Exception as conversion_error:
            print(f"⚠️ Erro na conversão com pydub: {conversion_error}")
            
            # Fallback: tentar conversão direta com ffmpeg se disponível
            try:
                import subprocess
                
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                
                # Usar ffmpeg diretamente
                cmd = [
                    'ffmpeg', '-i', str(audio_path),
                    '-ar', '44100',      # 44.1kHz
                    '-ac', '2',          # Estéreo
                    '-b:a', '128k',      # Bitrate
                    '-y',                # Overwrite
                    tmp_path
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"✅ Áudio convertido via ffmpeg: {tmp_path}")
                return tmp_path
                
            except (subprocess.CalledProcessError, FileNotFoundError) as ffmpeg_error:
                print(f"⚠️ ffmpeg não disponível: {ffmpeg_error}")
                return audio_path  # Retornar original como último recurso
    
    except Exception as e:
        print(f"❌ Erro na conversão de áudio: {e}")
        return audio_path  # Retornar original em caso de erro

@ai_voice_bp.route('/speak', methods=['POST'])
def text_to_speech():
    """
    Converte texto em fala usando a voz clonada da LUA
    Retorna áudio em formato base64
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        emotion = data.get('emotion', 'confident')
        format_type = data.get('format', 'base64')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Texto não fornecido'
            }), 400
        
        # Gerar áudio usando a voz da LUA
        audio_path = generate_lua_voice(text, emotion)
        
        if not audio_path or not Path(audio_path).exists():
            return jsonify({
                'success': False,
                'error': 'Falha ao gerar áudio'
            }), 500
        
        # Retornar áudio como base64
        try:
            with open(audio_path, 'rb') as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
            
            return jsonify({
                'success': True,
                'audio_base64': audio_data,
                'format': 'wav',
                'emotion': emotion
            })
            
        except Exception as file_error:
            return jsonify({
                'success': False,
                'error': f'Erro ao ler arquivo de áudio: {str(file_error)}'
            }), 500
            
    except Exception as e:
        print(f"Erro no TTS: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_voice_bp.route('/clear-cache', methods=['POST'])
def clear_voice_cache():
    """Limpa cache de voz antigo"""
    try:
        if voice_engine and hasattr(voice_engine, 'clear_cache'):
            hours = request.get_json().get('hours', 24) if request.get_json() else 24
            voice_engine.clear_cache(hours)
            return jsonify({
                'success': True,
                'message': f'Cache de voz limpo (mais antigo que {hours} horas)'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Engine de voz não disponível'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500