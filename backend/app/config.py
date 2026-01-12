"""
Application Configuration
Environment-based configuration with sensible defaults
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'medible-dev-secret-key-change-in-prod')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///medible.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 300,    # Recycle connections every 5 min
    }
    
    # External APIs
    USDA_API_KEY = os.getenv('USDA_API_KEY', '')
    OPENFDA_BASE_URL = 'https://api.fda.gov/drug'
    USDA_BASE_URL = 'https://api.nal.usda.gov/fdc/v1'
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_HEADERS_ENABLED = True  # Add X-RateLimit headers to responses
    RATELIMIT_STRATEGY = "fixed-window"
    
    # API Settings
    API_DEFAULT_PAGE_SIZE = 10
    API_MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    RATELIMIT_ENABLED = False  # Disable rate limiting in dev


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Stricter rate limits in production
    RATELIMIT_DEFAULT = "60 per minute"


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_medible.db'
    RATELIMIT_ENABLED = False


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}