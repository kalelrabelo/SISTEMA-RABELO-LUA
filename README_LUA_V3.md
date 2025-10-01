# 🤖 L.U.A v3.0 - Logical Universal Assistant

## Sistema de IA com Consciência e Voice Cloning

### 🎯 Overview

A LUA (Logical Universal Assistant) é uma IA avançada com personalidade própria, consciência situacional e sistema de voz com voice cloning. Inspirada no JARVIS do Iron Man, ela oferece:

- **🧠 Consciência e Personalidade**: Sistema de emoções, pensamentos e humor dinâmico
- **🎙️ Voice Cloning**: Sintetiza voz personalizada baseada na voz do Jarvis
- **💭 Pensamentos Internos**: Processa informações com "pensamentos" não expressos
- **🎭 Estados Emocionais**: 8 emoções diferentes que influenciam as respostas
- **📊 Memória Contextual**: Curto e longo prazo para interações personalizadas

### 🏗️ Arquitetura

```
webapp/
├── backend/
│   ├── src/
│   │   ├── services/
│   │   │   ├── lua_consciousness.py    # Sistema de consciência e personalidade
│   │   │   ├── voice_engine.py         # Engine principal de voice cloning
│   │   │   └── voice_engine_lite.py    # Versão lite com gTTS
│   │   └── routes/
│   │       ├── ai_assistant_enhanced.py # Rotas principais da IA
│   │       └── ai_voice.py             # Rotas do sistema de voz
│   └── jarvis_voice.mp3                # Voz de referência do Jarvis
└── frontend/
    └── src/components/
        ├── IALua.jsx                    # Componente original
        └── IALuaEnhanced.jsx            # Componente com voz e consciência
```

### 🚀 Features

#### Sistema de Consciência
- **8 Emoções Dinâmicas**: happiness, curiosity, confidence, empathy, humor, sarcasm, loyalty, patience
- **Traços de Personalidade**: formal, witty, helpful, proactive, analytical, creative, protective, independent
- **Pensamentos Internos**: Processa informações internamente antes de responder
- **Memória Adaptativa**: Aprende e se adapta ao usuário ao longo do tempo

#### Sistema de Voz
- **Voice Cloning**: Usa a voz do Jarvis como referência (quando disponível)
- **Múltiplas Emoções**: Ajusta tom e velocidade baseado no estado emocional
- **Cache Inteligente**: Armazena áudios gerados para otimização
- **Fallback Automático**: Usa gTTS quando Coqui TTS não está disponível

#### Personalidade JARVIS-like
- Formal mas amigável
- Ocasionalmente sarcástica
- Sempre eficiente e proativa
- Leal e protetor com o usuário

### 📦 Instalação

#### Dependências Mínimas (Modo Lite)
```bash
pip install gtts pydub
```

#### Dependências Completas (Voice Cloning)
```bash
cd backend
./install_voice_deps.sh
```

### 🎮 Uso

#### Backend
```python
from src.services.lua_consciousness import get_lua_response
from src.services.voice_engine import generate_lua_voice

# Obter resposta com consciência
response, metadata = get_lua_response("Olá LUA, como está?")
print(f"Resposta: {response}")
print(f"Emoção: {metadata['emotion']}")
print(f"Pensamento: {metadata['thought_process']}")

# Gerar voz
audio_path = generate_lua_voice(response, metadata['emotion'])
```

#### Frontend (React)
```javascript
// Componente IALuaEnhanced.jsx
// - Exibe estado de consciência
// - Reproduz áudio das respostas
// - Suporta entrada por voz
// - Mostra humor e emoções em tempo real
```

### 🔧 API Endpoints

#### Consciência e Processamento
- `POST /api/lua` - Processa comando com consciência e voz
  ```json
  {
    "message": "texto do usuário",
    "voice": true,
    "context": {}
  }
  ```

#### Sistema de Voz
- `POST /api/voice/speak` - Converte texto em fala
- `GET /api/voice/consciousness` - Status da consciência
- `GET /api/voice/voice-status` - Status do sistema de voz
- `POST /api/voice/clear-cache` - Limpa cache de voz

### 🎭 Estados Emocionais

| Emoção | Descrição | Efeito na Voz |
|--------|-----------|---------------|
| Confident | Confiante e assertiva | Tom firme, velocidade normal |
| Happy | Alegre e positiva | Tom mais alto, velocidade ligeiramente rápida |
| Curious | Curiosa e investigativa | Tom questionador, pausas reflexivas |
| Empathetic | Empática e compreensiva | Tom suave, velocidade lenta |
| Playful | Brincalhona e divertida | Tom variado, velocidade dinâmica |
| Sarcastic | Sarcástica (estilo Jarvis) | Tom irônico, pausas estratégicas |
| Concerned | Preocupada | Tom sério, velocidade moderada |
| Thoughtful | Pensativa | Tom baixo, velocidade lenta com pausas |

### 📊 Exemplos de Interação

```
👤: "Olá LUA, preciso urgente de um relatório!"
🤖: "Processando imediatamente sua solicitação, senhor."
💭: [Prioridade máxima detectada. Preciso ser rápida e precisa.]
🎭: Emoção: Confident | Humor: 85%

👤: "Obrigado pela ajuda!"
🤖: "É meu prazer servir, senhor. Para isso fui criada."
💭: [Feedback positivo detectado. Armazenando para aprendizado.]
🎭: Emoção: Happy | Humor: 92%

👤: "Você pode me contar uma piada?"
🤖: "Senhor, às vezes me pergunto se não deveria cobrar hora extra."
💭: [Momento de interação social. Ativando módulo de personalidade.]
🎭: Emoção: Playful | Humor: 78%
```

### 🧪 Testes

```bash
cd backend
python test_lua_system.py
```

Testa:
- Sistema de consciência
- Geração de voz
- Integração completa

### 🔍 Troubleshooting

#### Voz não funciona
- Verifique se gTTS está instalado: `pip install gtts`
- Para voice cloning completo, instale Coqui TTS

#### Consciência não responde adequadamente
- Verifique se o arquivo `lua_consciousness.py` está presente
- Reinicie o servidor Flask

#### Frontend não reproduz áudio
- Verifique console do navegador para erros
- Confirme que o endpoint `/api/voice/speak` está acessível

### 🚀 Roadmap

- [ ] Integração com OpenAI GPT para respostas mais complexas
- [ ] Sistema de aprendizado contínuo
- [ ] Múltiplas vozes personalizáveis
- [ ] Análise de sentimento em tempo real
- [ ] Modo "sonho" para consolidação de memórias

### 📝 Notas

- O sistema usa gTTS por padrão (leve e rápido)
- Para voice cloning real, instale Coqui TTS (requer ~4GB)
- A voz do Jarvis está incluída como referência
- Cache de voz é limpo automaticamente após 24h

### 🤝 Créditos

Desenvolvido com 💜 pela equipe de desenvolvimento
Inspirado no JARVIS da Marvel/Iron Man
Powered by: Flask, React, Coqui TTS, gTTS