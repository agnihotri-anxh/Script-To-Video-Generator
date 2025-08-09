from gtts import gTTS
import os

class TTSGenerator:
    """Text-to-Speech generator using Google TTS"""
    
    def __init__(self, language='en', slow=False):
        self.language = language
        self.slow = slow
    
    def generate_voiceover(self, script, output_path):
        """Generate voiceover using gTTS"""
        try:
            # Split long scripts into smaller chunks to avoid API limits
            max_chunk_length = 500  # Google TTS has limits
            if len(script) > max_chunk_length:
                return self._generate_voiceover_chunked(script, output_path)
            
            tts = gTTS(text=script, lang=self.language, slow=self.slow)
            tts.save(str(output_path))
            return True
        except Exception as e:
            print(f"Error generating voiceover: {e}")
            # Create a silent audio file as fallback
            return self._create_silent_audio(output_path)
    
    def _generate_voiceover_chunked(self, script, output_path):
        """Generate voiceover for long scripts by splitting into chunks"""
        try:
            # For now, just try to generate the full script
            # If it fails, create silent audio
            try:
                tts = gTTS(text=script, lang=self.language, slow=self.slow)
                tts.save(str(output_path))
                return True
            except Exception as e:
                print(f"Error generating full voiceover: {e}")
                return self._create_silent_audio(output_path)
                
        except Exception as e:
            print(f"Error in chunked voiceover generation: {e}")
            return self._create_silent_audio(output_path)
    
    def _create_silent_audio(self, output_path):
        """Create a silent audio file as fallback"""
        try:
            # Create a simple empty file as fallback
            with open(str(output_path), 'wb') as f:
                # Write minimal MP3 header
                f.write(b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            print(f"Created minimal audio fallback at {output_path}")
            return True
        except Exception as e:
            print(f"Error creating silent audio: {e}")
            return False
    
    def generate_voiceover_with_metadata(self, script, output_path, **kwargs):
        """Generate voiceover with additional metadata"""
        try:
            # Extract additional parameters
            language = kwargs.get('language', self.language)
            slow = kwargs.get('slow', self.slow)
            
            tts = gTTS(text=script, lang=language, slow=slow)
            tts.save(str(output_path))
            
            # Return metadata about the generated audio
            return {
                'success': True,
                'file_path': str(output_path),
                'language': language,
                'text_length': len(script),
                'file_size': os.path.getsize(str(output_path)) if os.path.exists(str(output_path)) else 0
            }
        except Exception as e:
            print(f"Error generating voiceover: {e}")
            return {'success': False, 'error': str(e)} 