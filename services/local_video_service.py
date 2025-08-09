import os
import random
from pathlib import Path
from config import Config

class LocalVideoService:
    """Service for managing and selecting local videos from the videos directory"""
    
    def __init__(self):
        self.videos_dir = Config.VIDEOS_DIR
        self.available_videos = self._scan_videos()
    
    def _scan_videos(self):
        """Scan the videos directory for available video files"""
        videos = []
        if self.videos_dir.exists():
            for file_path in self.videos_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                    videos.append({
                        'path': str(file_path),
                        'filename': file_path.name,
                        'size': file_path.stat().st_size,
                        'source': 'local'
                    })
        return videos
    
    def search_stock_videos(self, keywords, max_results=None):
        """Search for videos based on keywords using filename matching"""
        if not max_results:
            max_results = Config.LOCAL_MAX_RESULTS
        
        if not self.available_videos:
            return []
        
        # Create keyword mapping for better matching
        keyword_mapping = {
            # Car-related keywords
            'car': ['car', 'automobile', 'vehicle', 'driving', 'lamborghini', 'forza', 'centenario'],
            'vehicle': ['car', 'automobile', 'vehicle', 'driving', 'lamborghini', 'forza', 'centenario'],
            'driving': ['car', 'automobile', 'vehicle', 'driving', 'lamborghini', 'forza', 'centenario'],
            'lights': ['lights', 'city', 'manhattan', 'urban', 'night', 'street'],
            'city': ['city', 'manhattan', 'urban', 'lights', 'street', 'plaza'],
            'night': ['night', 'lights', 'city', 'manhattan', 'urban'],
            
            # Animal-related keywords
            'cat': ['cat', 'kitten', 'kitty', 'feline', 'pet', 'cute'],
            'kitten': ['cat', 'kitten', 'kitty', 'feline', 'pet', 'cute'],
            'pet': ['cat', 'kitten', 'puppy', 'dog', 'pet', 'animal', 'cute'],
            'animal': ['cat', 'kitten', 'puppy', 'dog', 'pet', 'animal', 'cute'],
            'puppy': ['puppy', 'dog', 'pet', 'animal', 'cute', 'funny'],
            'dog': ['puppy', 'dog', 'pet', 'animal', 'cute', 'funny'],
            
            # Nature-related keywords
            'nature': ['nature', 'mountain', 'sunrise', 'sunset', 'landscape', 'beautiful'],
            'mountain': ['mountain', 'nature', 'landscape', 'ai'],
            'sunrise': ['sunrise', 'sunset', 'beautiful', 'nature'],
            'sunset': ['sunrise', 'sunset', 'beautiful', 'nature'],
            'beautiful': ['beautiful', 'sunrise', 'sunset', 'nature'],
            
            # Weather-related keywords
            'snow': ['snow', 'winter', 'cold', 'chicago'],
            'winter': ['snow', 'winter', 'cold', 'chicago'],
            
            # Generic keywords
            'playing': ['playing', 'funny', 'cute', 'kitten', 'puppy', 'falling'],
            'cute': ['cute', 'kitten', 'puppy', 'funny'],
            'funny': ['funny', 'cute', 'puppy', 'kitten'],
        }
        
        # Score each video based on keyword matches
        scored_videos = []
        for video in self.available_videos:
            filename_lower = video['filename'].lower()
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Handle multi-word keywords (like "a cat", "a car")
                keyword_words = keyword_lower.split()
                
                # Direct filename match
                if keyword_lower in filename_lower:
                    score += 10
                    matched_keywords.append(keyword)
                
                # Check individual words in multi-word keywords
                for word in keyword_words:
                    if word in filename_lower:
                        score += 8
                        if keyword not in matched_keywords:
                            matched_keywords.append(keyword)
                
                # Special handling for "cat" keyword to prioritize kitten videos
                if 'cat' in keyword_words and 'kitten' in filename_lower:
                    score += 15  # Higher score for direct cat->kitten match
                    if keyword not in matched_keywords:
                        matched_keywords.append(keyword)
                
                # Check keyword mapping
                if keyword_lower in keyword_mapping:
                    for related_word in keyword_mapping[keyword_lower]:
                        if related_word in filename_lower:
                            score += 5
                            if keyword not in matched_keywords:
                                matched_keywords.append(keyword)
                            break
                
                # Also check individual words in keyword mapping
                for word in keyword_words:
                    if word in keyword_mapping:
                        for related_word in keyword_mapping[word]:
                            if related_word in filename_lower:
                                score += 5
                                if keyword not in matched_keywords:
                                    matched_keywords.append(keyword)
                                break
                
                # Partial word match
                for word in filename_lower.split():
                    if keyword_lower in word or word in keyword_lower:
                        score += 2
                        if keyword not in matched_keywords:
                            matched_keywords.append(keyword)
                        break
            
            if score > 0:
                scored_videos.append({
                    'video': video,
                    'score': score,
                    'matched_keywords': matched_keywords
                })
        
        # Sort by score (highest first) and take top results
        scored_videos.sort(key=lambda x: x['score'], reverse=True)
        
        # If no keyword matches found, fall back to random selection
        if not scored_videos:
            print(f"No keyword matches found for: {keywords}, using random selection")
            selected_videos = random.sample(
                self.available_videos, 
                min(max_results, len(self.available_videos))
            )
        else:
            # Take top scored videos
            selected_videos = [item['video'] for item in scored_videos[:max_results]]
            print(f"Keyword matches found: {[item['matched_keywords'] for item in scored_videos[:max_results]]}")
        
        # Format videos to match the expected structure
        formatted_videos = []
        for video in selected_videos:
            formatted_videos.append({
                'url': f'file://{video["path"]}',  # Local file URL
                'path': video['path'],  # Actual file path
                'filename': video['filename'],
                'width': Config.VIDEO_WIDTH,  # Default values
                'height': Config.VIDEO_HEIGHT,
                'duration': 10,  # Default duration
                'preview': None,  # No preview for local videos
                'source': 'local'
            })
        
        return formatted_videos
    
    def get_random_video(self):
        """Get a single random video"""
        if not self.available_videos:
            return None
        
        video = random.choice(self.available_videos)
        return {
            'url': f'file://{video["path"]}',
            'path': video['path'],
            'filename': video['filename'],
            'width': Config.VIDEO_WIDTH,
            'height': Config.VIDEO_HEIGHT,
            'duration': 10,
            'preview': None,
            'source': 'local'
        }
    
    def get_video_by_index(self, index):
        """Get a specific video by index"""
        if 0 <= index < len(self.available_videos):
            video = self.available_videos[index]
            return {
                'url': f'file://{video["path"]}',
                'path': video['path'],
                'filename': video['filename'],
                'width': Config.VIDEO_WIDTH,
                'height': Config.VIDEO_HEIGHT,
                'duration': 10,
                'preview': None,
                'source': 'local'
            }
        return None
    
    def get_video_count(self):
        """Get the total number of available videos"""
        return len(self.available_videos)
    
    def list_videos(self):
        """List all available videos"""
        return self.available_videos.copy()
    
    def download_video(self, video_info, output_path):
        """Copy local video to output path (simulates download)"""
        try:
            import shutil
            source_path = video_info.get('path') or video_info.get('url', '').replace('file://', '')
            
            if not source_path or not os.path.exists(source_path):
                return False
            
            # Convert path to string if it's a Path object
            output_path_str = str(output_path)
            
            # Copy the file
            shutil.copy2(source_path, output_path_str)
            return True
            
        except Exception as e:
            print(f"Error copying video: {e}")
            return False
    
    def get_video_info(self, video_info):
        """Get information about a local video"""
        try:
            source_path = video_info.get('path') or video_info.get('url', '').replace('file://', '')
            
            if not source_path or not os.path.exists(source_path):
                return {'available': False}
            
            stat = os.stat(source_path)
            return {
                'content_length': stat.st_size,
                'content_type': 'video/mp4',  # Assume MP4 for local files
                'available': True,
                'path': source_path
            }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {'available': False}
