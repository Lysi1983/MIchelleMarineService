from flask import Flask, render_template, url_for, jsonify, make_response, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_minify import Minify
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__, template_folder='templates', static_folder='static')

# Enable HTML minification
Minify(app=app, html=True, js=False, cssless=False)


# Configure Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@app.route('/')
@app.route('/michelle/marine/home')
@limiter.limit("50 per minute")
def index():
    return render_template('index.html')

@app.route('/michelle/marine/services')
@limiter.limit("20 per minute")
def services():
    return render_template('services.html')

@app.route('/michelle/marine/gallery')
@limiter.limit("50 per minute")
def gallery():
    return render_template('gallery.html')

@app.route('/michelle/marine/contact')
@limiter.limit("50 per minute")
def contact():
    return render_template('contact.html')

@app.route('/get_images/<folder_name>')
def get_images(folder_name):
    # Construct path relative to the application's static folder
    # Use app.root_path to get the application's root directory
    base_static_path = os.path.join(app.root_path, app.static_folder or 'static')
    image_folder_path = os.path.join(base_static_path, 'images', folder_name)
    image_folder_url_base = f'images/{folder_name}'  # Base for URL generation

    try:
        # Security check: Ensure the resolved path is still within the intended 'static/images' directory
        if not os.path.abspath(image_folder_path).startswith(os.path.abspath(os.path.join(base_static_path, 'images'))):
            app.logger.warning(f"Attempt to access invalid path: {folder_name}")
            return jsonify({"error": "Invalid folder path"}), 400  # Bad Request

        if os.path.isdir(image_folder_path):
            images = [f for f in os.listdir(image_folder_path) if os.path.isfile(os.path.join(image_folder_path, f))]
            # Generate URLs correctly using url_for
            image_urls = [url_for('static', filename=os.path.join(image_folder_url_base, img).replace('\\', '/')) for img in images]
            return jsonify(image_urls)
        else:
            app.logger.info(f"Image folder not found: {folder_name}")
            return jsonify({"error": "Folder not found"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching images for {folder_name}: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                           error_code='404', 
                           error_name='Страницата не е намерена', 
                           error_description='Страницата, която търсите, не съществува или е преместена.'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html',
                           error_code='500',
                           error_name='Грешка в сървъра',
                           error_description='Възникна проблем с нашия сървър. Моля, опитайте отново по-късно.'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html',
                           error_code='403',
                           error_name='Достъпът е забранен',
                           error_description='Нямате разрешение за достъп до тази страница.'), 403

@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html',
                           error_code='400',
                           error_name='Невалидна заявка',
                           error_description='Сървърът не може да обработи вашата заявка.'), 400

@app.errorhandler(429)
def too_many_requests(e):
    return render_template('error.html',
                           error_code='429',
                           error_name='Твърде много заявки',
                           error_description='Вие изпратихте твърде много заявки за кратък период от време.'), 429

# Add caching headers for static files
@app.after_request
def add_cache_headers(response):
    """Add caching headers for performance optimization"""
    # Cache static assets for 1 year
    if request.path.startswith('/static/'):
        # Images, fonts, and other static assets
        if any(request.path.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot']):
            response.cache_control.max_age = 31536000  # 1 year
            response.cache_control.public = True
        # CSS and JS files
        elif any(request.path.endswith(ext) for ext in ['.css', '.js']):
            response.cache_control.max_age = 2592000  # 30 days
            response.cache_control.public = True

    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    return response

if __name__ == '__main__':
    # Add basic logging configuration
    app.run(debug=True)
