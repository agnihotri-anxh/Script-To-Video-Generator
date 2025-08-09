#!/bin/bash

# AI Video Generator Docker Setup Script

echo "🎬 AI Video Generator - Docker Setup"
echo "====================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
HOST=0.0.0.0
PORT=5000
DEBUG=False
EOF
    echo "⚠️  Please update the .env file with your ElevenLabs API key if needed."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p outputs uploads temp videos

# Build and run the application
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting the application..."
docker-compose up -d

echo "⏳ Waiting for the application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:5000/api/health &> /dev/null; then
    echo "✅ Application is running successfully!"
    echo "🌐 Open your browser and go to: http://localhost:5000"
    echo ""
    echo "📋 Useful commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop application: docker-compose down"
    echo "  - Restart application: docker-compose restart"
    echo "  - Rebuild and restart: docker-compose up --build -d"
else
    echo "❌ Application failed to start. Check logs with: docker-compose logs"
    exit 1
fi 