import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the video generator application"""
    
    # API Keys
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', 'your-pexels-api-key-here')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', 'your-elevenlabs-api-key-here')
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # File Paths
    BASE_DIR = Path(__file__).parent
    UPLOADS_DIR = BASE_DIR / 'uploads'
    OUTPUTS_DIR = BASE_DIR / 'outputs'
    TEMP_DIR = BASE_DIR / 'temp'
    VIDEOS_DIR = BASE_DIR / 'videos'
    
    # Video Settings
    VIDEO_WIDTH = 1280
    VIDEO_HEIGHT = 720
    VIDEO_FPS = 24
    VIDEO_CODEC = 'libx264'
    AUDIO_CODEC = 'aac'
    
    # API Settings
    PEXELS_MAX_RESULTS = 3
    LOCAL_MAX_RESULTS = 3  # Number of local videos to use
    MAX_CLIP_DURATION = 5  # seconds
    
    # NLP Settings
    SPACY_MODEL = "en_core_web_sm"
    MAX_KEYWORDS_PER_SENTENCE = 5
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.UPLOADS_DIR, cls.OUTPUTS_DIR, cls.TEMP_DIR, cls.VIDEOS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)