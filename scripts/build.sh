#!/bin/bash

echo "🚀 Building Lua TTS System..."

# Build Docker image
echo "📦 Building Docker image..."
docker build -t lua-webapp .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
else
    echo "❌ Docker build failed!"
    exit 1
fi

# Optional: Build frontend separately
if [ -d "frontend" ]; then
    echo "🎨 Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    echo "✅ Frontend build complete!"
fi

echo "🎉 Build process completed!"