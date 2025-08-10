#  AI Video Generator

Transform your script into a professional video with AI-powered voiceover and stock footage.

## ✨ Features

- **🎤 AI Voiceover Generation** - Convert text to speech using Google TTS
- **🎥 Local Video Integration** - Use videos from your local videos directory
- **🧠 NLP Analysis** - Extract keywords from scripts using spaCy
- **🎬 Video Composition** - Combine clips and audio with MoviePy
- **🌐 Web Interface** - Beautiful, responsive web UI
- **📱 Video Preview** - Watch generated videos directly in the browser
- **🐳 Docker Support** - Easy deployment with Docker and Docker Compose

## 🚀 Quick Start with Docker

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### 1. Clone and Setup
   ```bash
git clone <your-repo-url>
   cd ai-video-generator
   ```

### 2. Configure API Keys
Edit the `.env` file with your API keys:
```env
PEXELS_API_KEY=your-pexels-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
HOST=0.0.0.0
PORT=5000
DEBUG=False
```

### 3. Run with Docker
**Windows:**
   ```bash
docker-setup.bat
```

**Linux/Mac:**
```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

**Manual Docker commands:**
   ```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

### 4. Access the Application
Open your browser and go to: **http://localhost:5000**

## 🛠️ Manual Installation

### Prerequisites
- Python 3.10+
- FFmpeg installed
- Local videos in the `videos` directory

### 1. Install Dependencies
   ```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment
Create a `.env` file:
```env
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
HOST=0.0.0.0
PORT=5000
DEBUG=True
```

**Note:** Pexels API key is no longer required as the application now uses local videos from the `videos` directory.

### 3. Run the Application
```bash
python app.py
```

## 📖 How to Use

### 1. Write Your Script
Enter a descriptive script in the text area. For example:
```
A young musician sits in a studio playing guitar. The city lights shine through the window. People walk on busy streets below. Birds fly over green hills in the distance.
```

### 2. Generate Video
Click "🎬 Generate Video" and wait for processing.

### 3. Watch and Download
- **Watch** the generated video directly in the browser
- **Download** the video file
- **Replay** the video with the replay button
- **View** script analysis and extracted keywords

## 🏗️ Architecture

```
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── core/
│   └── video_generator.py # Main video generation logic
├── services/
│   ├── stock_video_service.py  # Pexels API integration
│   └── video_processor.py      # Video editing with MoviePy
├── utils/
│   ├── nlp_analyzer.py   # Text analysis with spaCy
│   └── tts_generator.py  # Text-to-speech with gTTS
├── routes/
│   ├── api_routes.py     # REST API endpoints
│   └── web_routes.py     # Web interface routes
└── templates/
    └── index.html        # Web interface
```

## 🔧 API Endpoints

- `GET /api/health` - Health check
- `POST /api/generate-video` - Generate video from script
- `GET /api/download/<project_id>` - Download generated video
- `POST /api/analyze-script` - Analyze script without generating video
- `POST /api/generate-voiceover` - Generate voiceover only

## 🎯 Example Scripts

### Simple Test Script
```
A young musician sits in a studio playing guitar. The city lights shine through the window. People walk on busy streets below. Birds fly over green hills in the distance. A storm approaches the mountains. The sun sets behind the skyline. Music brings people together in the night.
```

### 2-Minute Music Video Script
```
[Verse 1 - 0:00-0:30]
A young musician sits alone in a dimly lit studio, fingers gently strumming an acoustic guitar. The soft glow of streetlights filters through dusty windows, casting long shadows across wooden floors.

[Chorus - 0:30-0:45]
Suddenly, the scene transforms into a vibrant cityscape at dawn. Golden sunlight breaks through skyscrapers, painting the urban landscape in warm, hopeful colors.

[Verse 2 - 0:45-1:15]
We transition to a peaceful countryside where rolling hills meet endless horizons. A lone figure walks along a winding road, carrying a backpack and guitar case.

[Bridge - 1:15-1:30]
The mood shifts to a dramatic mountain landscape where storm clouds gather over jagged peaks. Lightning illuminates the rugged terrain.

[Final Chorus - 1:30-2:00]
We return to the city, but now it's evening and the urban landscape is transformed by millions of twinkling lights.
```

## 🔑 API Keys Required

### ElevenLabs API (Optional)
1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for an account
3. Get your API key
4. Add to `.env` file: `ELEVENLABS_API_KEY=your-key-here`

## 📁 Local Videos Setup

The application now uses videos from your local `videos` directory instead of Pexels API. To set up:

1. **Add Videos**: Place your video files (MP4, AVI, MOV, MKV) in the `videos` directory
2. **Video Format**: Supported formats: MP4, AVI, MOV, MKV
3. **Video Quality**: Videos will be automatically resized to 1280x720 resolution
4. **Random Selection**: The application randomly selects videos from your collection for each script

**Note**: The more videos you have in the directory, the more variety your generated videos will have.

## 🐳 Docker Commands

```bash
# Build image
docker-compose build

# Start application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# Check status
docker-compose ps
```

## 🚨 Troubleshooting

### Common Issues

1. **TTS API Error (502 Bad Gateway)**
   - The system will automatically create a silent audio fallback
   - Try shorter scripts or wait and retry

2. **Video Download Issues**
   - Check that the video file exists in the outputs directory
   - Ensure proper file permissions

3. **Docker Issues**
   - Make sure Docker Desktop is running
   - Check available disk space
   - Verify port 5000 is not in use

4. **FFmpeg Errors**
   - Ensure FFmpeg is installed in Docker container
   - Check video file formats are supported

### Logs and Debugging

```bash
# View application logs
docker-compose logs -f

# Check container status
docker-compose ps

# Access container shell
docker-compose exec video-generator bash

# Check health endpoint
curl http://localhost:5000/api/health
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the logs
- Create an issue on GitHub

---

**🎬 Happy Video Generating!** ✨ 
