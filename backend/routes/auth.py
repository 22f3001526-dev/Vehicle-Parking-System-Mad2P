"""
Authentication routes
Handles user registration, login, and authentication
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db
from models.user import User
from utils.auth_utils import get_current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        role='user'  # Regular users only, admin is predefined
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Auto-login: create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user (both admin and regular users)"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    # Check credentials
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(include_email=True),
        'access_token': access_token
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Get current user information"""
    user = get_current_user()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict(include_email=True)
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    # JWT tokens are stateless, so logout is handled client-side
    # This endpoint exists for consistency and future token blacklisting
    return jsonify({'message': 'Logout successful'}), 200
