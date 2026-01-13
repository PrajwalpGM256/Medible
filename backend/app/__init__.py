"""
Medible - Flask Application Factory
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import time

from app.config import config
from app.errors import register_error_handlers, generate_request_id

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def setup_logging(app):
    """Configure structured JSON logging"""
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            import json
            log_data = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
            }
            if hasattr(record, 'request_id'):
                log_data["request_id"] = record.request_id
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_data)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    
    # File handler (rotating)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = RotatingFileHandler('logs/medible.log', maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(JSONFormatter())
    
    # Set log level
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    logging.getLogger().setLevel(log_level)


def create_app(config_name=None):
    """Application factory pattern"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Request lifecycle hooks
    @app.before_request
    def before_request():
        g.request_id = generate_request_id()
        g.start_time = time.time()
        g.current_user = None  # Will be set by auth_required decorator
    
    @app.after_request
    def after_request(response):
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        duration = time.time() - getattr(g, 'start_time', time.time())
        app.logger.info(f"Request completed in {duration:.3f}s")
        return response
    
    # Import models to register with SQLAlchemy
    with app.app_context():
        from app import models  # noqa: F401
    
    # Register blueprints
    from app.routes.drugs import drugs_bp
    from app.routes.foods import foods_bp
    from app.routes.interactions import interactions_bp
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.medications import medications_bp
    from app.routes.food_diary import food_diary_bp
    from app.routes.interaction_history import interaction_history_bp
    
    # API v1 routes
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(drugs_bp, url_prefix='/api/v1/drugs')
    app.register_blueprint(foods_bp, url_prefix='/api/v1/foods')
    app.register_blueprint(interactions_bp, url_prefix='/api/v1/interactions')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(medications_bp, url_prefix='/api/v1/medications')
    app.register_blueprint(food_diary_bp, url_prefix='/api/v1/food-diary')
    app.register_blueprint(interaction_history_bp, url_prefix='/api/v1/interaction-history')
    
    # Root endpoint
    @app.route('/')
    def home():
        return {
            'app': 'Medible',
            'tagline': 'Med + Edible = Know your food. Know your meds. Stay safe.',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/v1/health',
                'auth': {
                    'register': 'POST /api/v1/auth/register',
                    'login': 'POST /api/v1/auth/login',
                    'profile': 'GET /api/v1/auth/me'
                },
                'medications': {
                    'list': 'GET /api/v1/medications',
                    'add': 'POST /api/v1/medications',
                    'check_food': 'POST /api/v1/medications/check-food'
                },
                'food_diary': {
                    'today': 'GET /api/v1/food-diary/today',
                    'add': 'POST /api/v1/food-diary',
                    'summary': 'GET /api/v1/food-diary/summary?days=7'
                },
                'drugs': '/api/v1/drugs/search?q=aspirin',
                'foods': '/api/v1/foods/search?q=banana',
                'interactions': '/api/v1/interactions/check?food=grapefruit&drug=lipitor'
            }
        }
    
    app.logger.info(f"Medible app initialized in {config_name} mode")
    
    return app