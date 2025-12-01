"""
Configuration file for the Vehicle Parking App
Author: MAD-II Project
Date: December 2024

This file contains all the configuration settings needed for:
- Database connection (SQLite)
- JWT authentication tokens
- Redis caching
- Celery task queue
"""

import os
from datetime import timedelta

class Config:
    """
    Main configuration class
    All settings are loaded from environment variables with fallback defaults
    """
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-secret-key-for-parking-app-2024'
    
    # Database settings - using SQLite for simplicity
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'parking_database.db')
    
    # Disable modification tracking to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT token settings for authentication
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-parking-secret-2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Token valid for 24 hours
    
    # Redis settings for caching (makes the app faster)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_EXPIRY = 900  # 15 minutes = 900 seconds
    
    # Celery settings for background tasks
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
    # Default parking price (can be customized per lot)
    DEFAULT_PRICE_PER_HOUR = 50  # Rs. 50 per hour
