#!/bin/bash

# AI Resume Builder - Quick Start Script

echo "🚀 Starting AI Resume Builder..."
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p output media data logs config

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env file with your configuration values"
    else
        echo "⚠️  .env.example not found. You may need to create .env manually"
    fi
fi

# Build and start the application
echo "🔨 Building Docker image..."
if command -v docker-compose &> /dev/null; then
    docker-compose build
    echo "🌟 Starting application..."
    docker-compose up -d
else
    docker compose build
    echo "🌟 Starting application..."
    docker compose up -d
fi

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ Application is running successfully!"
    echo ""
    echo "🌐 Open your browser and go to: http://localhost:8000"
    echo ""
    echo "📝 To use the AI features, you'll need an OpenAI API key:"
    echo "   1. Go to https://platform.openai.com/api-keys"
    echo "   2. Create a new API key"
    echo "   3. Set it in your .env file as OPENAI_API_KEY=your-key-here"
    echo ""
    echo "📊 View logs:"
    echo "   Container logs: docker-compose logs -f"
    echo "   Application logs: ls -la logs/"
    echo ""
    echo "🛑 To stop the application, run: docker-compose down"
else
    echo "❌ Application failed to start. Check the logs:"
    if command -v docker-compose &> /dev/null; then
        docker-compose logs
    else
        docker compose logs
    fi
fi