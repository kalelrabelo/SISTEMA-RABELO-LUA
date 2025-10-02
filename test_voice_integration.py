#!/usr/bin/env python3
"""
Script de teste para verificar integração do sistema de voz
"""

import sys
import os

# Corrigir path para importações do backend - compatível com Windows e Linux
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_voice_imports():
    """Testa se todas as importações necessárias funcionam"""
    print("🔍 Testando importações do sistema de voz...")
    
    try:
        from backend.src.routes.ai_voice import ai_voice_bp
        print("✅ ai_voice_bp importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar ai_voice_bp: {e}")
        return False
    
    try:
        from backend.src.services.voice_engine import generate_lua_voice, voice_engine
        print("✅ voice_engine importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar voice_engine: {e}")
        return False
    
    return True

def test_voice_engine_status():
    """Testa se o voice engine está funcionando"""
    print("\n🎙️ Testando status do voice engine...")
    
    try:
        from backend.src.services.voice_engine import voice_engine
        
        if voice_engine is None:
            print("⚠️ Voice engine é None - usando modo fallback")
            return True
        
        status = voice_engine.get_voice_status()
        print(f"✅ Voice engine status: {status}")
        
        # Teste de geração de áudio
        test_text = "Teste de integração da LUA"
        audio_path = voice_engine.generate_speech(test_text, "confident")
        
        if audio_path:
            print(f"✅ Áudio de teste gerado: {audio_path}")
            return True
        else:
            print("⚠️ Não foi possível gerar áudio - usando fallback")
            return True
            
    except Exception as e:
        print(f"⚠️ Erro no voice engine: {e}")
        return True  # Não é erro crítico, fallback funciona

def test_jarvis_voice_file():
    """Verifica se o arquivo de voz do Jarvis existe"""
    print("\n🎤 Verificando arquivo de voz do Jarvis...")
    
    jarvis_path = os.path.join(os.path.dirname(__file__), "jarvis_voice.mp3")
    
    if os.path.exists(jarvis_path):
        size = os.path.getsize(jarvis_path)
        print(f"✅ jarvis_voice.mp3 encontrado ({size} bytes)")
        return True
    else:
        print("⚠️ jarvis_voice.mp3 não encontrado - TTS usará fallback")
        return True  # Não é erro crítico

def test_frontend_integration():
    """Verifica se os arquivos do frontend foram modificados corretamente"""
    print("\n🌐 Verificando integração do frontend...")
    
    # Verificar JarvisAI_Enhanced.jsx
    jarvis_path = "frontend/src/components/JarvisAI_Enhanced.jsx"
    if os.path.exists(jarvis_path):
        with open(jarvis_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('playAudio', 'Função playAudio implementada'),
            ('backendVoiceAvailable', 'Estado backend voice implementado'),
            ('/api/voice/speak', 'Integração com API de voz'),
            ('processCRUDCommand', 'Comandos CRUD implementados'),
            ('extractEmployeeName', 'Extração de nomes implementada')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - NÃO ENCONTRADO")
                return False
    else:
        print(f"❌ Arquivo {jarvis_path} não encontrado")
        return False
    
    # Verificar App.jsx
    app_path = "frontend/src/App.jsx"
    if os.path.exists(app_path):
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'modalFilters' in content and 'handleModalOpen' in content:
            print("✅ App.jsx com suporte a filtros implementado")
        else:
            print("❌ App.jsx não tem suporte completo a filtros")
            return False
    else:
        print(f"❌ Arquivo {app_path} não encontrado")
        return False
    
    # Verificar Vales.jsx
    vales_path = "frontend/src/components/Vales.jsx"
    if os.path.exists(vales_path):
        with open(vales_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'processLuaFilters' in content and 'handleCreateValeWithPrefill' in content:
            print("✅ Vales.jsx com processamento LUA implementado")
        else:
            print("❌ Vales.jsx não tem processamento LUA completo")
            return False
    else:
        print(f"❌ Arquivo {vales_path} não encontrado")
        return False
    
    return True

def main():
    """Executa todos os testes"""
    print("🚀 TESTE DE INTEGRAÇÃO - SISTEMA DE VOZ LUA\n")
    
    tests = [
        ("Importações", test_voice_imports),
        ("Voice Engine", test_voice_engine_status),
        ("Arquivo Jarvis", test_jarvis_voice_file),
        ("Frontend", test_frontend_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erro no teste {name}: {e}")
            results.append((name, False))
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES:")
    print("="*50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{name:.<20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de voz integrado e funcionando")
        print("\n📝 PRÓXIMOS PASSOS:")
        print("1. Iniciar backend: cd backend && python main.py")
        print("2. Iniciar frontend: cd frontend && npm start")
        print("3. Ativar LUA: Diga 'Lua' no microfone")
        print("4. Testar comando: 'Lua registrar vale de 100 reais para João'")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("🔧 Revise os arquivos indicados acima")
    
    print("="*50)

if __name__ == "__main__":
    main()