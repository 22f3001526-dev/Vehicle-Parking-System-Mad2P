"""
Authentication Utilities
Helper functions for JWT token management and role checking

MAD-II Project - Security Functions
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User

def admin_required():
    """
    Decorator to protect routes that only admins can access
    Use this above any route function that should be admin-only
    
    Example usage:
        @admin_required()
        def some_admin_function():
            pass
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # First, verify the JWT token is valid
            verify_jwt_in_request()
            
            # Get the user ID from the token
            current_user_id = get_jwt_identity()
            
            # Find the user in database
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'error': 'User account not found'}), 404
            
            # Check if user has admin role
            if not user.is_admin():
                return jsonify({'error': 'Admin access required for this action'}), 403
            
            # All checks passed, run the actual function
            return fn(*args, **kwargs)
        
        return decorator
    return wrapper

def user_required():
    """
    Decorator to protect routes that require any authenticated user
    Both admin and regular users can access these routes
    
    Example usage:
        @user_required()
        def some_user_function():
            pass
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify token is valid
            verify_jwt_in_request()
            
            # Get user ID from token
            current_user_id = get_jwt_identity()
            
            # Make sure user exists in database
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'error': 'User account not found'}), 404
            
            # User is authenticated, proceed
            return fn(*args, **kwargs)
        
        return decorator
    return wrapper

def get_current_user():
    """
    Helper function to get the currently logged-in user
    Must be called from within a protected route
    
    Returns:
        User object of the currently logged-in user
    """
    current_user_id = get_jwt_identity()
    return User.query.get(current_user_id)
