"""
Rotas da API para o sistema de voz da LUA
"""

from flask import Blueprint, request, jsonify, send_file
from pathlib import Path
import base64
import os
from datetime import datetime

# Importar serviços
from src.services.voice_engine import voice_engine, generate_lua_voice
from src.services.lua_consciousness import lua_consciousness, get_lua_response

ai_voice_bp = Blueprint('ai_voice', __name__)

@ai_voice_bp.route('/speak', methods=['POST'])
def text_to_speech():
    """
    Converte texto em fala usando a voz clonada da LUA
    Retorna áudio em formato base64 ou URL do arquivo
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        emotion = data.get('emotion', 'confident')
        format_type = data.get('format', 'base64')  # base64 ou file
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Texto não fornecido'
            }), 400
        
        # Gerar áudio
        audio_path = generate_lua_voice(text, emotion)
        
        if not audio_path:
            return jsonify({
                'success': False,
                'error': 'Falha ao gerar áudio'
            }), 500
        
        if format_type == 'base64':
            # Retornar áudio como base64
            with open(audio_path, 'rb') as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
            
            return jsonify({
                'success': True,
                'audio': audio_data,
                'format': 'wav',
                'emotion': emotion
            })
        else:
            # Retornar caminho do arquivo
            return jsonify({
                'success': True,
                'audio_url': f'/api/voice/audio/{Path(audio_path).name}',
                'format': 'wav',
                'emotion': emotion
            })
            
    except Exception as e:
        print(f"Erro no TTS: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_voice_bp.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve arquivo de áudio gerado"""
    try:
        base_path = Path(__file__).parent.parent.parent
        audio_path = base_path / "cache" / "voice" / filename
        
        if not audio_path.exists():
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(
            str(audio_path),
            mimetype='audio/wav',
            as_attachment=False
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_voice_bp.route('/consciousness', methods=['GET'])
def get_consciousness():
    """Retorna o estado de consciência atual da LUA"""
    try:
        status = lua_consciousness.get_consciousness_status()
        return jsonify({
            'success': True,
            'consciousness': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_voice_bp.route('/voice-status', methods=['GET'])
def voice_status():
    """Retorna status do sistema de voz"""
    try:
        status = voice_engine.get_voice_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_voice_bp.route('/clear-cache', methods=['POST'])
def clear_voice_cache():
    """Limpa cache de voz antigo"""
    try:
        hours = request.get_json().get('hours', 24)
        voice_engine.clear_cache(hours)
        return jsonify({
            'success': True,
            'message': f'Cache de voz limpo (mais antigo que {hours} horas)'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500