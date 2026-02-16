"""
Application Configuration
Environment-based configuration with sensible defaults
"""

import os
import secrets
from dotenv import load_dotenv

load_dotenv()

# Generate a new secret on each server start (for dev)
# This invalidates all existing tokens when server restarts
_DEV_JWT_SECRET = secrets.token_hex(32)
print(f"🔐 Generated new JWT secret (first 8 chars): {_DEV_JWT_SECRET[:8]}...")


def get_database_url():
    """Get database URL, fixing Railway's postgres:// to postgresql://"""
    url = os.getenv('DATABASE_URL', 'sqlite:///medible.db')
    # Railway uses postgres:// but SQLAlchemy needs postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'medible-dev-secret-key-change-in-prod')
    
    # Database
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 300,    # Recycle connections every 5 min
    }
    
    # External APIs
    USDA_API_KEY = os.getenv('USDA_API_KEY', '')
    OPENFDA_BASE_URL = 'https://api.fda.gov/drug'
    USDA_BASE_URL = 'https://api.nal.usda.gov/fdc/v1'
    
    # CORS - Frontend URLs allowed to access the API
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    
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
    CORS_ORIGINS = ['*']  # Allow all origins in dev
    
    # ALWAYS use dynamic secret in dev - tokens invalidate on server restart
    # This ensures users are logged out when server restarts (security feature)
    SECRET_KEY = _DEV_JWT_SECRET


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