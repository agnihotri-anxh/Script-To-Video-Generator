from flask import Blueprint, request, jsonify, send_file
from core.video_generator import VideoGenerator
from config import Config
import os

# Create blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize video generator
video_generator = VideoGenerator()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'Server is running!',
        'version': '1.0.0',
        'services': {
            'nlp_analyzer': True,
            'tts_generator': True,
            'stock_video_service': True,
            'video_processor': True
        }
    })
@api_bp.route('/generate-video', methods=['POST'])
def generate_video():
    """Generate a video by merging scenes based on the script."""
    try:
        data = request.get_json()
        script = data.get('script', '').strip()

        if not script:
            return jsonify({'error': 'Script is required'}), 400

        # Split script into scenes (using ' and ' as separator)
        scenes = [s.strip() for s in script.split(' and ') if s.strip()]
        print("Scenes detected:", scenes)

        # Extract keywords for each scene
        scene_keywords = []
        for scene in scenes:
            analysis = video_generator.nlp_analyzer.analyze_script(scene)
            # Flatten keywords for this scene
            keywords = []
            for item in analysis:
                keywords.extend(item.get('keywords', []))
            scene_keywords.append(list(set(keywords)))
            print(f"Keywords for scene '{scene}':", keywords)

        import uuid
        project_id = str(uuid.uuid4())
        project_dir = Config.OUTPUTS_DIR / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        # Pass scenes and their keywords to the generator
        result = video_generator.generate_multi_scene_video(
            scenes=scenes,
            scene_keywords=scene_keywords,
            project_id=project_id
        )

        if result['success']:
            return jsonify({
                'success': True,
                'project_id': project_id,
                'video_url': f'/download/{project_id}'
            })
        else:
            return jsonify({'error': result['error']}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@api_bp.route('/generate-voiceover', methods=['POST'])
def generate_voiceover():
    """Generate voiceover without video"""
    try:
        data = request.get_json()
        script = data.get('script', '').strip()

        if not script:
            return jsonify({'error': 'Script is required'}), 400

        # Create temporary file for voiceover
        import uuid
        project_id = str(uuid.uuid4())
        project_dir = Config.OUTPUTS_DIR / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        voiceover_path = project_dir / "voiceover.mp3"

        result = video_generator.generate_voiceover_only(script, voiceover_path)

        if result['success']:
            return jsonify({
                'success': True,
                'voiceover_url': f'/download-voiceover/{project_id}',
                'project_id': project_id
            })
        else:
            return jsonify({'error': result['error']}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/search-videos', methods=['POST'])
def search_videos():
    """Search for stock videos"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        
        if not keywords:
            return jsonify({'error': 'Keywords are required'}), 400
        
        result = video_generator.search_videos_only(keywords)
        
        if result['success']:
            return jsonify({
                'success': True,
                'videos': result['videos']
            })
        else:
            return jsonify({'error': result['error']}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/download/<project_id>', methods=['GET'])
def download_video(project_id):
    """Download generated video"""
    try:
        video_path = Config.OUTPUTS_DIR / project_id / "final_video.mp4"
        if not video_path.exists():
            return jsonify({'error': 'Video not found'}), 404

        return send_file(
            video_path,
            as_attachment=False,  # Set to False for in-browser playback
            mimetype='video/mp4'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/download-voiceover/<project_id>', methods=['GET'])
def download_voiceover(project_id):
    """Download generated voiceover"""
    try:
        voiceover_path = Config.OUTPUTS_DIR / project_id / "voiceover.mp3"
        
        if not voiceover_path.exists():
            return jsonify({'error': 'Voiceover not found'}), 404
        
        return send_file(
            voiceover_path,
            as_attachment=True,
            download_name=f"voiceover_{project_id}.mp3"
        )
        
    except Exception as e:
        print(f"Error downloading voiceover: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects/<project_id>/status', methods=['GET'])
def get_project_status(project_id):
    """Get project status and information"""
    try:
        info = video_generator.get_project_info(project_id)
        
        if info.get('success') is False:
            return jsonify({'error': info['error']}), 500
        
        if info['video_exists']:
            return jsonify({
                'status': 'completed',
                'video_url': f'/download/{project_id}',
                'voiceover_url': f'/download-voiceover/{project_id}',
                'info': info
            })
        else:
            return jsonify({'status': 'processing'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects/<project_id>/info', methods=['GET'])
def get_project_info(project_id):
    """Get detailed project information"""
    try:
        info = video_generator.get_project_info(project_id)
        
        if info.get('success') is False:
            return jsonify({'error': info['error']}), 500
        
        return jsonify(info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500