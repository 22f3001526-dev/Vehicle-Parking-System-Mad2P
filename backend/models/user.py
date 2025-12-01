"""
User Model - Represents users of the parking system
This handles both regular users and admin

Author: Student Project MAD-II
"""

from models import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    """
    Database model for storing user information
    Stores login credentials, role, and tracks parking activity
    """
    __tablename__ = 'users'
    
    # Primary key - unique ID for each user
    id = db.Column(db.Integer, primary_key=True)
    
    # User credentials - must be unique
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role: either 'admin' or 'user'
    role = db.Column(db.String(20), nullable=False, default='user')
    
    # Timestamps for tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_booking_date = db.Column(db.DateTime, nullable=True)  # For reminder system
    
    # Relationship: One user can have many reservations
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic', 
                                   cascade='all, delete-orphan')
    
    def set_password(self, plain_password):
        """
        Hashes the password before storing
        We never store plain passwords for security!
        
        Args:
            plain_password: The password user entered
        """
        self.password_hash = generate_password_hash(plain_password)
    
    def check_password(self, plain_password):
        """
        Checks if provided password matches stored hash
        
        Args:
            plain_password: Password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, plain_password)
    
    def is_admin(self):
        """Check if this user has admin privileges"""
        return self.role == 'admin'
    
    def to_dict(self, include_sensitive=False):
        """
        Converts user object to dictionary for JSON responses
        
        Args:
            include_sensitive: Whether to include email and other sensitive data
            
        Returns:
            Dictionary with user data
        """
        user_data = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Only include email if specifically requested
        if include_sensitive:
            user_data['email'] = self.email
            user_data['last_booking_date'] = self.last_booking_date.isoformat() if self.last_booking_date else None
        
        return user_data
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<User {self.username} ({self.role})>'
