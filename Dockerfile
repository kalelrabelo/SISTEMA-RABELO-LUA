# ==============================================================
# 🧠 Lua TTS System - Kokoro-82M (PT-BR)
# Author: Kalel
# Compatible with Windows, Linux and Docker Desktop
# ==============================================================

FROM python:3.11-slim

# 1️⃣ Working directory
WORKDIR /app

# 2️⃣ Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    espeak-ng \
    build-essential \
    curl \
    wget \
    locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3️⃣ Configure environment and locale
RUN sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG=pt_BR.UTF-8 \
    LC_ALL=pt_BR.UTF-8 \
    TZ=America/Sao_Paulo \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=0 \
    PIP_INDEX_URL=https://pypi.org/simple \
    PYTHONPATH=/app

# 4️⃣ Copy dependency list
COPY requirements.txt .

# 5️⃣ Optional: allocate dummy swap (no swapon to avoid Docker error)
RUN fallocate -l 2G /swapfile && chmod 600 /swapfile || true

# 6️⃣ Install dependencies (optimized for CPU)
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt --index-url https://pypi.org/simple && \
    pip install --no-cache-dir torch==2.5.0+cpu --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir "kokoro>=0.9.3" && \
    pip install --no-cache-dir "misaki==0.9.3" && \
    pip install --no-cache-dir "espeakng==1.0.2" && \
    (pip cache purge || true)

# 7️⃣ Remove temporary swap
RUN rm -f /swapfile || true

# 8️⃣ Copy backend and frontend
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# 9️⃣ Create folders and default environment configuration
RUN mkdir -p /app/backend/{logs,temp,models,voices} && \
    echo "API_HOST=0.0.0.0" > /app/backend/.env && \
    echo "API_PORT=8000" >> /app/backend/.env && \
    echo "USE_GPU=false" >> /app/backend/.env && \
    echo "LOG_LEVEL=INFO" >> /app/backend/.env && \
    echo "KOKORO_MODEL=hexgrad/Kokoro-82M" >> /app/backend/.env && \
    echo "KOKORO_LANGUAGE=pt" >> /app/backend/.env && \
    echo "KOKORO_VOICE=af_heart" >> /app/backend/.env

# 🔊 10️⃣ Expose API port
EXPOSE 8000

# 11️⃣ Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 🚀 12️⃣ Start FastAPI server
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
