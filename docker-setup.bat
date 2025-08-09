@echo off
echo 🎬 AI Video Generator - Docker Setup
echo =====================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
        echo HOST=0.0.0.0
        echo PORT=5000
        echo DEBUG=False
    ) > .env
    echo ⚠️  Please update the .env file with your ElevenLabs API key if needed.
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist outputs mkdir outputs
if not exist uploads mkdir uploads
if not exist temp mkdir temp
if not exist videos mkdir videos

REM Build and run the application
echo 🔨 Building Docker image...
docker-compose build

echo 🚀 Starting the application...
docker-compose up -d

echo ⏳ Waiting for the application to start...
timeout /t 10 /nobreak >nul

REM Check if the application is running
curl -f http://localhost:5000/api/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Application failed to start. Check logs with: docker-compose logs
    pause
    exit /b 1
) else (
    echo ✅ Application is running successfully!
    echo 🌐 Open your browser and go to: http://localhost:5000
    echo.
    echo 📋 Useful commands:
    echo   - View logs: docker-compose logs -f
    echo   - Stop application: docker-compose down
    echo   - Restart application: docker-compose restart
    echo   - Rebuild and restart: docker-compose up --build -d
)

pause 