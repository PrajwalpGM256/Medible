"""
Custom Error Handling
Centralized error classes and handlers for consistent API responses
"""

from flask import jsonify
from functools import wraps
import logging
import traceback
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error with status code and error code"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL_ERROR", details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request", details: dict = None):
        super().__init__(message, 400, "BAD_REQUEST", details)

class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(message, 422, "VALIDATION_ERROR", details)

class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(message, 404, "NOT_FOUND", details)

class ExternalAPIError(AppError):
    def __init__(self, message: str = "External service error", details: dict = None):
        super().__init__(message, 502, "EXTERNAL_API_ERROR", details)

class RateLimitError(AppError):
    def __init__(self, message: str = "Rate limit exceeded", details: dict = None):
        super().__init__(message, 429, "RATE_LIMITED", details)


def generate_request_id():
    """Generate unique request ID for tracing"""
    return str(uuid.uuid4())[:8]


def api_response(data=None, meta=None, status_code=200):
    """
    Standard successful API response format
    { "data": {...}, "meta": { "timestamp", "request_id" } }
    """
    response = {
        "data": data,
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": meta.get("request_id") if meta else generate_request_id(),
            **(meta or {})
        }
    }
    return jsonify(response), status_code


def error_response(error: AppError, request_id: str = None):
    """
    Standard error response format
    { "error": { "code", "message", "details" }, "meta": {...} }
    """
    response = {
        "error": {
            "code": error.error_code,
            "message": error.message,
            "details": error.details
        },
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id or generate_request_id()
        }
    }
    return jsonify(response), error.status_code


def register_error_handlers(app):
    """Register global error handlers on Flask app"""
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        logger.warning(f"AppError: {error.error_code} - {error.message}", extra={
            "error_code": error.error_code,
            "details": error.details
        })
        return error_response(error)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response(NotFoundError("Endpoint not found"))
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return error_response(AppError("Method not allowed", 405, "METHOD_NOT_ALLOWED"))
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"Unhandled exception: {str(error)}\n{traceback.format_exc()}")
        return error_response(AppError("Internal server error", 500, "INTERNAL_ERROR"))


def handle_exceptions(f):
    """Decorator to catch and convert exceptions to AppError responses"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError:
            raise  # Let error handler deal with it
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}\n{traceback.format_exc()}")
            raise AppError(f"An unexpected error occurred", 500, "INTERNAL_ERROR")
    return wrapper