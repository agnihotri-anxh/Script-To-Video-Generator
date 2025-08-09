import uuid
from pathlib import Path
from utils.nlp_analyzer import NLPAnalyzer
from utils.tts_generator import TTSGenerator
from services.local_video_service import LocalVideoService
from services.video_processor import VideoProcessor
from config import Config

class VideoGenerator:
    """Main video generator class that orchestrates all services"""
    
    def __init__(self):
        self.nlp_analyzer = NLPAnalyzer()
        self.tts_generator = TTSGenerator()
        self.local_video_service = LocalVideoService()
        self.video_processor = VideoProcessor()
    
    def generate_video(self, script, project_id=None):
        """Generate a complete video from script"""
        try:
            # Generate project ID if not provided
            if not project_id:
                project_id = str(uuid.uuid4())
            
            # Create project directory (robust)
            project_dir = Config.OUTPUTS_DIR / project_id
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Analyze script
            print("Analyzing script...")
            script_analysis = self.nlp_analyzer.analyze_script(script)
            
            # Step 2: Generate voiceover
            print("Generating voiceover...")
            voiceover_path = project_dir / "voiceover.mp3"
            voiceover_result = self.tts_generator.generate_voiceover(script, voiceover_path)
            
            if not voiceover_result:
                raise Exception("Failed to generate voiceover")
            
            # Step 3: Create video
            print("Creating video...")
            output_path = project_dir / "final_video.mp4"
            video_result = self.video_processor.create_video(
                script_analysis, 
                voiceover_path, 
                output_path,
                self.local_video_service
            )
            
            if not video_result:
                raise Exception("Failed to create video")
            
            # Return success response
            return {
                'success': True,
                'project_id': project_id,
                'video_path': str(output_path),
                'voiceover_path': str(voiceover_path),
                'analysis': script_analysis,
                'project_dir': str(project_dir)
            }
            
        except Exception as e:
            print(f"Error in video generation: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_id': project_id
            }

    def analyze_script_only(self, script):
        """Analyze script without generating video"""
        try:
            analysis = self.nlp_analyzer.analyze_script(script)
            return {
                'success': True,
                'analysis': analysis
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_voiceover_only(self, script, output_path):
        """Generate voiceover without video"""
        try:
            result = self.tts_generator.generate_voiceover(script, output_path)
            return {
                'success': result,
                'output_path': str(output_path) if result else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def search_videos_only(self, keywords):
        """Search for local videos without downloading"""
        try:
            videos = self.local_video_service.search_stock_videos(keywords)
            return {
                'success': True,
                'videos': videos
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_project_info(self, project_id):
        """Get information about a project"""
        try:
            project_dir = Config.OUTPUTS_DIR / project_id
            video_path = Config.OUTPUTS_DIR / project_id / "final_video.mp4"
            voiceover_path = project_dir / "voiceover.mp3"
            
            info = {
                'project_id': project_id,
                'project_dir': str(project_dir),
                'video_exists': video_path.exists(),
                'voiceover_exists': voiceover_path.exists()
            }
            
            if video_path.exists():
                info['video_size'] = video_path.stat().st_size
                info['video_path'] = str(video_path)
            
            if voiceover_path.exists():
                info['voiceover_size'] = voiceover_path.stat().st_size
                info['voiceover_path'] = str(voiceover_path)
            
            return info
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_multi_scene_video(self, scenes, scene_keywords, project_id):
        """Generate and merge videos for each scene, then combine into one final video with voiceover."""
        try:
            project_dir = Config.OUTPUTS_DIR / project_id
            project_dir.mkdir(parents=True, exist_ok=True)
            video_clips = []

            # For each scene, find a matching video and create a clip
            for i, keywords in enumerate(scene_keywords):
                found_videos = self.local_video_service.search_stock_videos(keywords)
                if not found_videos:
                    raise Exception(f"No videos found for scene {i+1}: {keywords}")
                # Pick the first found video for simplicity
                video_info = found_videos[0]
                video_clips.append(video_info['path'])

            # Step: Generate voiceover for the whole script
            script = " and ".join(scenes)
            voiceover_path = project_dir / "voiceover.mp3"
            voiceover_result = self.tts_generator.generate_voiceover(script, voiceover_path)
            if not voiceover_result:
                raise Exception("Failed to generate voiceover")

            # Merge all clips into one video with voiceover
            output_path = project_dir / "final_video.mp4"
            merge_success = self.video_processor.merge_clips_with_voiceover(video_clips, voiceover_path, output_path)

            if not merge_success:
                raise Exception("Failed to merge video clips")

            return {
                'success': True,
                'project_id': project_id,
                'video_path': str(output_path),
                'voiceover_path': str(voiceover_path),
                'project_dir': str(project_dir)
            }
        except Exception as e:
            print(f"Error in multi-scene video generation: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_id': project_id
            }