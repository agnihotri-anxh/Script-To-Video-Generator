from flask import Blueprint, render_template

# Create blueprint for web routes
web_bp = Blueprint('web', __name__)

@web_bp.route('/', methods=['GET'])
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@web_bp.route('/about', methods=['GET'])
def about():
    """About page"""
    return render_template('about.html')

@web_bp.route('/docs', methods=['GET'])
def docs():
    """Documentation page"""
    return render_template('docs.html') 