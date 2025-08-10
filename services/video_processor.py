from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, ColorClip, TextClip
from moviepy.editor import CompositeVideoClip
from config import Config
import os
import PIL

# Fix for PIL ANTIALIAS deprecation
try:
    from PIL import Image
    # Check if ANTIALIAS exists, if not use LANCZOS
    if hasattr(Image, 'ANTIALIAS'):
        RESAMPLING_MODE = Image.ANTIALIAS
    else:
        RESAMPLING_MODE = Image.LANCZOS
except ImportError:
    RESAMPLING_MODE = None

class VideoProcessor:
    """Service for video processing and composition"""
    
    def __init__(self):
        self.video_width = Config.VIDEO_WIDTH
        self.video_height = Config.VIDEO_HEIGHT
        self.video_fps = Config.VIDEO_FPS
        self.video_codec = Config.VIDEO_CODEC
        self.audio_codec = Config.AUDIO_CODEC
        self.max_clip_duration = Config.MAX_CLIP_DURATION
    
    def create_video(self, script_analysis, voiceover_path, output_path, video_service):
        """Create final video by combining clips and voiceover"""
        try:
            video_clips = []
            temp_files = []
            
            # Process each sentence
            for i, analysis in enumerate(script_analysis):
                # Search for videos based on keywords
                videos = video_service.search_stock_videos(analysis['keywords'])
                
                if videos:
                    # Use the first video
                    video_info = videos[0]
                    temp_video_path = Config.TEMP_DIR / f"clip_{i}.mp4"
                    
                    if video_service.download_video(video_info, str(temp_video_path)):
                        temp_files.append(temp_video_path)
                        
                        # Load video clip
                        clip = VideoFileClip(str(temp_video_path))
                        
                        # Resize to standard format with error handling
                        try:
                            clip = clip.resize(width=self.video_width, height=self.video_height)
                        except Exception as resize_error:
                            print(f"Resize error, using original size: {resize_error}")
                            # Use original size if resize fails
                        
                        # Handle short clips better
                        original_duration = clip.duration
                        print(f"Video duration: {original_duration:.2f}s")
                        
                        if original_duration < 3.0:
                            # For very short clips, use a better approach
                            print(f"Short clip detected ({original_duration:.2f}s), using smooth extension")
                            target_duration = min(self.max_clip_duration, 4.0)  # Cap at 4 seconds
                            
                            if original_duration < 1.0:
                                # For extremely short clips, slow down more
                                speed_factor = original_duration / target_duration
                                clip = clip.speedx(speed_factor)
                            else:
                                # For moderately short clips, use a gentler approach
                                # Create a loop that fades in/out smoothly
                                loop_count = int(target_duration / original_duration) + 1
                                clips_list = [clip] * loop_count
                                extended_clip = concatenate_videoclips(clips_list)
                                clip = extended_clip.subclip(0, target_duration)
                        else:
                            # For longer clips, limit duration normally
                            max_duration = min(self.max_clip_duration, clip.duration)
                            clip = clip.subclip(0, max_duration)
                        
                        video_clips.append(clip)
                    else:
                        # If download fails, create a placeholder clip
                        placeholder_clip = self._create_placeholder_clip(analysis['sentence'])
                        video_clips.append(placeholder_clip)
                else:
                    # Create placeholder clip if no videos found
                    placeholder_clip = self._create_placeholder_clip(analysis['sentence'])
                    video_clips.append(placeholder_clip)
            
            if not video_clips:
                raise Exception("No video clips available")
            
            # Add transitions between clips
            video_clips_with_transitions = self.add_transitions(video_clips, transition_duration=0.3)
            
            # Concatenate all video clips
            final_video = concatenate_videoclips(video_clips_with_transitions)
            
            # Load voiceover (with fallback to silent audio)
            try:
                if os.path.exists(str(voiceover_path)):
                    voiceover = AudioFileClip(str(voiceover_path))
                    # Set voiceover as audio for the video
                    final_video = final_video.set_audio(voiceover)
                else:
                    print(f"Voiceover file not found: {voiceover_path}")
                    # Create silent audio as fallback
                    from moviepy.audio.AudioClip import AudioClip
                    silent_audio = AudioClip(lambda t: 0, duration=final_video.duration)
                    final_video = final_video.set_audio(silent_audio)
            except Exception as e:
                print(f"Error loading voiceover: {e}")
                # Create silent audio as fallback
                from moviepy.audio.AudioClip import AudioClip
                silent_audio = AudioClip(lambda t: 0, duration=final_video.duration)
                final_video = final_video.set_audio(silent_audio)
            
            # Write final video
            final_video.write_videofile(
                str(output_path),
                fps=self.video_fps,
                codec=self.video_codec,
                audio_codec=self.audio_codec
            )
            
            # Clean up
            final_video.close()
            try:
                voiceover.close()
            except:
                pass  # Voiceover might not exist if we used silent audio
            for clip in video_clips:
                try:
                    clip.close()
                except:
                    pass
            
            # Remove temporary files
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error creating video: {e}")
            return False
    
    def _create_placeholder_clip(self, text):
        """Create a placeholder video clip with text"""
        # Create a black background
        clip = ColorClip(size=(self.video_width, self.video_height), color=(0, 0, 0), duration=3)
        
        # Add text with enhanced compatibility fix for newer Pillow versions
        try:
            # Try with method='caption' first
            text_clip = TextClip(
                text,
                fontsize=40,
                color='white',
                size=(1200, None),
                method='caption'
            ).set_position('center').set_duration(3)
        except Exception as e:
            try:
                # Fallback without method parameter
                text_clip = TextClip(
                    text,
                    fontsize=30,
                    color='white',
                    size=(self.video_width-100, None)
                ).set_position('center').set_duration(3)
            except Exception as e2:
                try:
                    # Third fallback - try with minimal parameters
                    text_clip = TextClip(
                        text,
                        fontsize=24,
                        color='white'
                    ).set_position('center').set_duration(3)
                except Exception as e3:
                    # Final fallback - create simple color clip without text
                    print(f"TextClip creation failed completely: {e3}")
                    # Return just the background clip without text
                    return clip
        
        # Combine background and text
        try:
            final_clip = clip.set_make_frame(lambda t: text_clip.get_frame(t))
            return final_clip
        except Exception as e:
            print(f"Error combining text with background: {e}")
            return clip
    
    def add_transitions(self, clips, transition_duration=0.5):
        """Add fade transitions between video clips"""
        if len(clips) <= 1:
            return clips
        
        # Add crossfade transitions between clips
        from moviepy.video.compositing.transitions import crossfadein
        
        final_clips = []
        for i, clip in enumerate(clips):
            if i == 0:
                # First clip - add fade in
                clip = clip.fadein(transition_duration)
            elif i == len(clips) - 1:
                # Last clip - add fade out
                clip = clip.fadeout(transition_duration)
            else:
                # Middle clips - add both fade in and out
                clip = clip.fadein(transition_duration).fadeout(transition_duration)
            
            final_clips.append(clip)
        
        return final_clips
    
    def resize_video(self, video_path, output_path, width=None, height=None):
        """Resize a video to specified dimensions"""
        try:
            clip = VideoFileClip(str(video_path))
            
            if width and height:
                clip = clip.resize(width=width, height=height)
            elif width:
                clip = clip.resize(width=width)
            elif height:
                clip = clip.resize(height=height)
            
            clip.write_videofile(str(output_path), codec=self.video_codec)
            clip.close()
            return True
        except Exception as e:
            print(f"Error resizing video: {e}")
            return False
    
    def merge_clips(self, video_clips, output_path):
        """Merge a list of video file paths into one video."""
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        try:
            clips = [VideoFileClip(clip) for clip in video_clips]
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
            return True
        except Exception as e:
            print(f"Error merging clips: {e}")
            return False
    
    def merge_clips_with_voiceover(self, video_clips, voiceover_path, output_path):
        """Merge video clips and add voiceover as audio track."""
        from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
        try:
            clips = [VideoFileClip(clip) for clip in video_clips]
            final_clip = concatenate_videoclips(clips, method="compose")
            audio = AudioFileClip(str(voiceover_path))
            final_clip = final_clip.set_audio(audio)
            final_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
            return True
        except Exception as e:
            print(f"Error merging clips with voiceover: {e}")
            return False
    

    def add_caption_to_video(input_video_path, output_video_path, caption_text, position=("center", "bottom"), font_size=40, font_color="white"):
        """
        Add a caption overlay to a video.
        """
        # Load video
        video = VideoFileClip(str(input_video_path))

        # Create text clip for the caption
        txt_clip = (TextClip(caption_text, fontsize=font_size, color=font_color, font="Arial-Bold")
                    .set_duration(video.duration)
                    .set_position(position)
                    .margin(bottom=30, opacity=0))

        # Combine video + caption
        final_clip = CompositeVideoClip([video, txt_clip])

        # Export video
        final_clip.write_videofile(str(output_video_path), codec="libx264", audio_codec="aac")
    

    
    