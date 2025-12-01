"""
Main application file for the Parking Management System
This file sets up the Flask server and connects all the components

Author: MAD-II Student Project
"""

from flask import Flask, jsonify
from flask_cors import CORS  # Allows frontend to talk to backend
from flask_jwt_extended import JWTManager  # Handles user authentication
from config import Config
from models import db

def create_app(config_class=Config):
    """
    Creates and configures the Flask application
    This is called the 'application factory' pattern
    
    Returns:
        Flask app instance ready to run
    """
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Setup database connection
    db.init_app(app)
    
    # Enable CORS so Vue frontend can make requests
    CORS(app)
    
    # Setup JWT for token-based authentication
    jwt_manager = JWTManager(app)
    
    # Import and register all route blueprints
    # (Importing here to avoid circular imports)
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    # Error handlers for common HTTP errors
    @app.errorhandler(404)
    def page_not_found(error):
        """Handle 404 errors (page not found)"""
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors (server problems)"""
        return jsonify({'error': 'Internal server error occurred'}), 500
    
    # Simple health check endpoint to test if API is running
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Returns OK if server is running properly"""
        return jsonify({
            'status': 'healthy',
            'message': 'Parking Management API is running successfully'
        }), 200
    
    return app

# Run the application
if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("🚗 Vehicle Parking Management System Starting...")
    print("=" * 60)
    print("Server running at: http://localhost:5000")
    print("API endpoints available at: http://localhost:5000/api/")
    print("Health check: http://localhost:5000/api/health")
    print("=" * 60)
    
    # Start the development server
    app.run(debug=True, host='0.0.0.0', port=5000)
