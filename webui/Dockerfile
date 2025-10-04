# Open-WebUI com pandas==2.2.3
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar Open-WebUI com versão específica de pandas
RUN uv pip install --system --no-cache -r requirements.txt

# Criar diretório de dados
RUN mkdir -p /app/backend/data

# Configurações do Open-WebUI
ENV WEBUI_AUTH=false
ENV DATA_DIR=/app/backend/data
ENV ENABLE_SIGNUP=true
ENV DEFAULT_MODELS=llama3.2:latest,mistral:latest
ENV OLLAMA_BASE_URL=http://ollama:11434

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
  CMD curl -f http://localhost:8080/health || exit 1

# Comando para iniciar o Open-WebUI
CMD ["open-webui", "serve", "--host", "0.0.0.0", "--port", "8080"]