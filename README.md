# 🌙 Sistema Lua TTS - Joalheria com Assistente IA

Sistema completo de gerenciamento de joalheria com assistente de IA integrada (Lua), incluindo conversação por voz bidirecional e interface visual com esfera de energia.

## 🚀 Características Principais

### ✅ Funcionalidades Implementadas

1. **Sistema de Gerenciamento de Joalheria**
   - Cadastro de produtos, clientes e funcionários
   - Controle de estoque e materiais
   - Gestão financeira e notas fiscais
   - Sistema de pedidos e ordens de serviço

2. **Assistente IA Lua**
   - Conversação natural em português (PT-BR)
   - Text-to-Speech (TTS) com múltiplas vozes
   - Speech-to-Text (STT) para comandos de voz
   - Personalidade customizada e contexto de conversa

3. **Interface Visual Imersiva**
   - Modo conversa com esfera de energia animada
   - Vídeo em loop de partículas azuis
   - Esfera que pulsa sincronizada com a voz da Lua
   - Transição suave com fade para preto

4. **Conversação Bidirecional**
   - Captura de voz do usuário via microfone
   - Transcrição automática para texto
   - Resposta da Lua com voz sintetizada
   - WebSocket para comunicação em tempo real

## 📋 Pré-requisitos

- Docker e Docker Compose
- Node.js 18+ (para desenvolvimento local)
- Python 3.11+ (para desenvolvimento local)
- Navegador com suporte a Web Speech API (Chrome, Edge)
- Microfone para comandos de voz

## 🎬 Configuração do Vídeo da Esfera

### ⚠️ IMPORTANTE: Adicionar o Vídeo Manualmente

O arquivo de vídeo da esfera de energia não está incluído no repositório devido ao seu tamanho (>400MB).

1. **Baixe ou localize o arquivo:**
   - Nome original: `abstract-blue-looped-energy-sphere-of-particles-an-2025-08-29-12-33-41-utc.mp4`

2. **Coloque o arquivo na pasta correta:**
   ```bash
   frontend/public/videos/
   ```

3. **Renomeie o arquivo para:**
   ```bash
   abstract-blue-looped-energy-sphere.mp4
   ```

4. **Estrutura esperada:**
   ```
   frontend/public/videos/
   ├── abstract-blue-looped-energy-sphere.mp4  # <-- Adicione este arquivo
   └── README.md
   ```

## 🐳 Instalação com Docker (Recomendado)

### 1. Clone o repositório
```bash
git clone https://github.com/kalelrabelo/SISTEMA-RABELO-LUA.git
cd SISTEMA-RABELO-LUA
```

### 2. Adicione o vídeo da esfera (veja seção acima)

### 3. Configure as variáveis de ambiente
```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

### 4. Build e execute com Docker Compose
```bash
# Usar o docker-compose corrigido
docker-compose -f docker-compose.fixed.yml up --build
```

### 5. Acesse o sistema
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Documentação API: http://localhost:5000/docs

## 💻 Instalação Local (Desenvolvimento)

### Backend (FastAPI)

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar servidor
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Frontend (React)

```bash
cd frontend

# Instalar dependências
npm install

# Executar servidor de desenvolvimento
npm run dev
```

## 🎤 Como Usar o Modo Conversa da Lua

### Ativação por Voz
1. Diga: **"Lua, iniciar modo conversa"**
2. Ou clique no botão **"Iniciar Modo Conversa 🌙"**
3. Ou use o atalho **Alt + L**

### Durante a Conversa
- A tela escurece suavemente
- A esfera de energia azul aparece no centro
- O microfone é ativado automaticamente
- Fale naturalmente - a Lua responderá
- A esfera pulsa quando a Lua fala
- Para sair, clique em "Encerrar Conversa"

## 🗂️ Estrutura do Projeto

```
SISTEMA-RABELO-LUA/
├── backend/                    # API FastAPI
│   ├── main.py                # Aplicação principal
│   ├── modules/               
│   │   ├── tts/               # Engine TTS corrigido
│   │   │   ├── kokoro_engine_fixed.py
│   │   │   └── kokoro_engine.py (original)
│   │   ├── stt/               # Speech-to-Text
│   │   │   └── speech_recognition.py
│   │   └── lua/               # Assistente IA
│   │       ├── assistant.py
│   │       └── personality.py
│   ├── src/                   # Modelos de dados
│   │   └── models/            # Entidades da joalheria
│   ├── requirements.txt       # Dependências Python
│   ├── requirements_tts.txt   # Dependências TTS
│   ├── requirements_stt.txt   # Dependências STT
│   ├── Dockerfile            
│   └── Dockerfile.fixed       # Dockerfile corrigido
│
├── frontend/                   # React App
│   ├── src/
│   │   ├── App.jsx            # Componente principal
│   │   └── components/
│   │       ├── LuaConversation.jsx    # Modo conversa
│   │       ├── LuaConversation.css    # Estilos
│   │       ├── ChatInterface.jsx
│   │       └── VoiceControls.jsx
│   ├── public/
│   │   └── videos/            # ADICIONE O VÍDEO AQUI
│   │       └── abstract-blue-looped-energy-sphere.mp4
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml          # Configuração original
├── docker-compose.fixed.yml    # Configuração corrigida
└── README.md                   # Este arquivo
```

## 🔧 Correções Implementadas

### 1. Erro do Kokoro TTS Engine
- **Problema**: `'EspeakG2P' object has no attribute 'lexicon'`
- **Solução**: Migração para Coqui TTS com modelos multilíngues
- **Arquivo**: `backend/modules/tts/kokoro_engine_fixed.py`

### 2. Dependências Fixadas
- Versões específicas no `requirements_tts.txt`
- TTS==0.22.0, torch==2.1.2, etc.
- Dockerfile atualizado com todas as dependências de sistema

### 3. Interface Visual da Lua
- Componente React completo: `LuaConversation.jsx`
- Animações CSS suaves e responsivas
- Integração com Web Audio API para efeito de pulsação

### 4. Modo Conversa Bidirecional
- WebSocket endpoint: `/ws/conversation`
- STT endpoint: `/api/stt/transcribe`
- Integração com Web Speech API no frontend

## 🐛 Solução de Problemas

### Erro: "Vídeo não encontrado"
- Certifique-se de adicionar o arquivo MP4 em `frontend/public/videos/`
- Renomeie para `abstract-blue-looped-energy-sphere.mp4`

### Erro: "Microfone não autorizado"
- Permita acesso ao microfone quando solicitado
- Use HTTPS em produção para Web Speech API

### Erro: "TTS não inicializa"
- Verifique se o Docker tem memória suficiente (mínimo 4GB)
- Use `docker-compose.fixed.yml` ao invés do original

### Erro: "Port already in use"
```bash
# Linux/Mac
sudo lsof -i :3000
sudo lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 📚 API Endpoints

### Chat
- `POST /api/chat` - Enviar mensagem para Lua
- `GET /api/chat/history` - Histórico de conversas

### TTS (Text-to-Speech)
- `POST /api/tts/generate` - Gerar áudio da fala
- `POST /api/voice/mix` - Misturar vozes
- `GET /api/voice/voices` - Listar vozes disponíveis

### STT (Speech-to-Text)
- `POST /api/stt/transcribe` - Transcrever áudio
- `WS /ws/conversation` - WebSocket para conversa

### Sistema
- `GET /health` - Status do sistema
- `GET /docs` - Documentação Swagger

## 🚀 Deploy em Produção

### Usando Docker
1. Configure variáveis de ambiente de produção
2. Use `docker-compose.fixed.yml` com ajustes
3. Configure HTTPS com nginx/traefik
4. Use volumes para persistência de dados

### Considerações de Segurança
- Configure CORS adequadamente
- Use HTTPS para Web Speech API
- Implemente autenticação JWT
- Configure rate limiting
- Use secrets para API keys

## 📝 Próximos Passos Recomendados

1. **Melhorias na Interface**
   - Adicionar mais animações à esfera
   - Implementar temas personalizáveis
   - Adicionar visualização de ondas sonoras

2. **Funcionalidades IA**
   - Integração com GPT-4 para respostas mais inteligentes
   - Análise de sentimento na voz
   - Múltiplos idiomas

3. **Sistema de Joalheria**
   - Dashboard com gráficos
   - Relatórios automáticos
   - Integração com sistemas de pagamento

4. **Performance**
   - Cache de respostas frequentes
   - Otimização de modelos TTS
   - CDN para assets estáticos

## 📄 Licença

Proprietary - Sistema desenvolvido para Joalheria Rabelo

## 👤 Autor

**Kalel Rabelo**
- GitHub: [@kalelrabelo](https://github.com/kalelrabelo)

## 🙏 Agradecimentos

- Equipe Coqui TTS pelo engine de síntese
- Comunidade FastAPI e React
- OpenAI pela tecnologia de IA

---

**Nota**: Para suporte técnico ou dúvidas, abra uma issue no GitHub ou entre em contato com o desenvolvedor.