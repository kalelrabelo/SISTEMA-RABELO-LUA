# Kokoro - TTS com pandas<2.0
FROM python:3.11-slim

# Instalar dependências do sistema para áudio
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv para gerenciamento rápido
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências com versão específica de pandas
RUN uv pip install --system --no-cache -r requirements.txt

# Criar diretórios necessários
RUN mkdir -p /app/models /app/output /app/cache

# Copiar aplicação
COPY . .

# Baixar modelo Kokoro se não existir
RUN python -c "from TTS.api import TTS; import os; \
    if not os.path.exists('/app/models/kokoro'): \
        print('Downloading Kokoro model...'); \
        tts = TTS(model_name='tts_models/ja/kokoro/tacotron2-DDC', \
                 progress_bar=True, \
                 gpu=False).to('cpu')"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=5 \
  CMD curl -f http://localhost:8000/api/voice/status || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]