import requests
from config import Config

class StockVideoService:
    """Service for searching and downloading stock videos"""
    
    def __init__(self):
        self.pexels_api_key = Config.PEXELS_API_KEY
        self.max_results = Config.PEXELS_MAX_RESULTS
    
    def search_stock_videos(self, keywords, max_results=None):
        """Search for stock videos using Pexels API"""
        if not max_results:
            max_results = self.max_results
            
        if not self.pexels_api_key or self.pexels_api_key == 'your-pexels-api-key-here':
            # Return mock data if no API key
            return self._get_mock_videos(keywords)
        
        try:
            # Combine keywords into a search query
            query = ' '.join(keywords[:3])  # Use first 3 keywords
            
            headers = {
                'Authorization': self.pexels_api_key
            }
            
            params = {
                'query': query,
                'per_page': max_results,
                'orientation': 'landscape'
            }
            
            response = requests.get(
                'https://api.pexels.com/videos/search',
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for video in data.get('videos', []):
                    # Get the best quality video file
                    video_files = video.get('video_files', [])
                    if video_files:
                        # Prefer HD quality
                        hd_files = [f for f in video_files if f.get('width', 0) >= Config.VIDEO_WIDTH]
                        if hd_files:
                            best_file = min(hd_files, key=lambda x: x.get('width', 0))
                        else:
                            best_file = max(video_files, key=lambda x: x.get('width', 0))
                        
                        videos.append({
                            'url': best_file['link'],
                            'width': best_file.get('width'),
                            'height': best_file.get('height'),
                            'duration': video.get('duration'),
                            'preview': video.get('image'),
                            'source': 'pexels'
                        })
                
                return videos[:max_results]
            else:
                print(f"Pexels API error: {response.status_code}")
                return self._get_mock_videos(keywords)
                
        except Exception as e:
            print(f"Error searching videos: {e}")
            return self._get_mock_videos(keywords)
    
    def _get_mock_videos(self, keywords):
        """Return mock video data for testing"""
        # These are placeholder URLs - in production you'd use real stock video URLs
        mock_videos = [
            {
                'url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                'width': Config.VIDEO_WIDTH,
                'height': Config.VIDEO_HEIGHT,
                'duration': 10,
                'preview': 'https://via.placeholder.com/320x180',
                'source': 'mock'
            }
        ]
        return mock_videos
    
    def download_video(self, video_url, output_path):
        """Download video from URL"""
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            # Convert path to string if it's a Path object
            output_path_str = str(output_path)
            
            with open(output_path_str, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False
    
    def get_video_info(self, video_url):
        """Get information about a video without downloading"""
        try:
            response = requests.head(video_url)
            if response.status_code == 200:
                return {
                    'content_length': response.headers.get('content-length'),
                    'content_type': response.headers.get('content-type'),
                    'available': True
                }
            return {'available': False}
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {'available': False} 