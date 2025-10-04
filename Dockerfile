# Dockerfile for Lua TTS System with Kokoro-82M
# Compatible with Windows and Linux

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Audio libraries
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    # Speech synthesis
    espeak-ng \
    # Build tools
    build-essential \
    # Network tools
    curl \
    wget \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LANG=pt_BR.UTF-8 \
    LC_ALL=pt_BR.UTF-8 \
    TZ=America/Sao_Paulo

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    # Install Kokoro separately to ensure latest version
    pip install "kokoro>=0.9.4" && \
    # Clean pip cache
    pip cache purge

# Copy application code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Create necessary directories
RUN mkdir -p /app/backend/logs \
    /app/backend/temp \
    /app/backend/models \
    /app/backend/voices

# Create .env file with defaults
RUN echo "API_HOST=0.0.0.0" > /app/backend/.env && \
    echo "API_PORT=8000" >> /app/backend/.env && \
    echo "USE_GPU=false" >> /app/backend/.env && \
    echo "LOG_LEVEL=INFO" >> /app/backend/.env

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]