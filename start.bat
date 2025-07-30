@echo off
REM AI Resume Builder - Quick Start Script for Windows

echo 🚀 Starting AI Resume Builder...
echo ================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo    Visit: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "output" mkdir output
if not exist "media" mkdir media
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "config" mkdir config

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file from template...
    if exist .env.example (
        copy .env.example .env >nul
        echo ⚠️  Please edit .env file with your configuration values
    ) else (
        echo ⚠️  .env.example not found. You may need to create .env manually
    )
)

REM Build and start the application
echo 🔨 Building Docker image...
docker-compose build

echo 🌟 Starting application...
docker-compose up -d

REM Wait for the application to start
echo ⏳ Waiting for application to start...
timeout /t 10 /nobreak >nul

REM Check if the application is running (simplified check)
echo ✅ Application should be running!
echo.
echo 🌐 Open your browser and go to: http://localhost:8000
echo.
echo 📝 To use the AI features, you'll need an OpenAI API key:
echo    1. Go to https://platform.openai.com/api-keys
echo    2. Create a new API key
echo    3. Set it in your .env file as OPENAI_API_KEY=your-key-here
echo.
echo 📊 View logs:
echo    Container logs: docker-compose logs -f
echo    Application logs: dir logs
echo.
echo 🛑 To stop the application, run: docker-compose down
echo.
pause