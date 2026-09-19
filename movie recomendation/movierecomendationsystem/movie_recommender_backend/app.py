from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from recommend import MovieRecommender

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize recommender
recommender = None

def init_recommender():
    """Initialize the movie recommender system"""
    global recommender
    try:
        artifacts_path = os.getenv('ARTIFACTS_PATH', 'ml_model/artifacts/')
        logger.info(f"Initializing recommender with artifacts path: {artifacts_path}")
        recommender = MovieRecommender(artifacts_path=artifacts_path)
        logger.info("✅ Movie recommender initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize recommender: {e}", exc_info=True)
        return False

# Initialize on startup
init_recommender()

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Movie Recommender API',
        'version': '1.0',
        'status': 'running',
        'recommender_loaded': recommender is not None,
        'endpoints': {
            'POST /api/search': 'Search for movies and get recommendations',
            'GET /api/health': 'Health check endpoint',
            'GET /': 'API information'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'recommender_loaded': recommender is not None,
        'tmdb_api_configured': bool(os.getenv('TMDB_API_KEY')),
        'omdb_api_configured': bool(os.getenv('OMDB_API_KEY'))
    }), 200

@app.route('/api/search', methods=['POST', 'OPTIONS'])
def search_movie():
    """
    Search for a movie and get recommendations
    
    Request body:
    {
        "movie_name": "Inception",
        "n_recommendations": 10,  // optional, default 10
        "preference_genres": []   // optional
    }
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    # Check if recommender is initialized
    if not recommender:
        logger.error("Recommender not initialized")
        return jsonify({
            'error': 'Movie recommender system is not initialized',
            'status': 'error'
        }), 500
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400
        
        # Validate required fields
        if 'movie_name' not in data:
            return jsonify({
                'error': 'movie_name is required',
                'status': 'error'
            }), 400
        
        movie_name = data['movie_name'].strip()
        
        if not movie_name:
            return jsonify({
                'error': 'movie_name cannot be empty',
                'status': 'error'
            }), 400
        
        # Get optional parameters
        n_recommendations = int(data.get('n_recommendations', 10))
        preference_genres = data.get('preference_genres', None)
        
        # Validate n_recommendations
        if n_recommendations < 1 or n_recommendations > 50:
            n_recommendations = 10
        
        logger.info(f"📽️  Searching for: '{movie_name}' with {n_recommendations} recommendations")
        
        # Get recommendations
        result = recommender.get_recommendations(
            movie_name=movie_name,
            n_recommendations=n_recommendations,
            preference_genres=preference_genres
        )
        
        # Log result summary
        status = result.get('status', 'unknown')
        searched_movie = result.get('searched_movie')
        recommendations_count = len(result.get('recommendations', []))
        
        logger.info(f"✅ Search completed - Status: {status}, Recommendations: {recommendations_count}")
        
        if searched_movie:
            poster = searched_movie.get('poster_path', 'None')
            logger.info(f"📸 Main movie poster: {poster[:100] if poster else 'None'}")
        
        # Log sample recommendation posters
        for i, rec in enumerate(result.get('recommendations', [])[:3]):
            poster = rec.get('poster_path', 'None')
            logger.info(f"📸 Rec {i+1} ({rec.get('title')}): {poster[:100] if poster else 'None'}")
        
        # Return appropriate status code
        if status == 'not_found':
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'error': f'Invalid input: {str(e)}',
            'status': 'error'
        }), 400
        
    except Exception as e:
        logger.error(f"Error in search_movie: {e}", exc_info=True)
        return jsonify({
            'error': 'An internal error occurred',
            'status': 'error',
            'details': str(e) if app.debug else None
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    # Check for API keys
    if not os.getenv('TMDB_API_KEY'):
        logger.warning("⚠️  TMDB_API_KEY not set in environment variables")
    if not os.getenv('OMDB_API_KEY'):
        logger.warning("⚠️  OMDB_API_KEY not set in environment variables")
    
    # Run the app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting Flask server on http://127.0.0.1:{port}")
    logger.info(f"🐛 Debug mode: {debug}")
    
    app.run(
        host='127.0.0.1',
        port=port,
        debug=debug,
        threaded=True
    )