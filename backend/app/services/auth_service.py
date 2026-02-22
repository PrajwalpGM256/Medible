"""
Authentication Service
Handles JWT token generation, validation, and user authentication
"""

import jwt
import secrets
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, g, current_app
from app.models.user import User
from app.errors import AppError


class AuthenticationError(AppError):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(message, 401, "AUTHENTICATION_ERROR", details)


class AuthorizationError(AppError):
    """Authorization failed (authenticated but not permitted)"""
    def __init__(self, message: str = "Access denied", details: dict = None):
        super().__init__(message, 403, "AUTHORIZATION_ERROR", details)


def generate_token(user: User, expires_in: int = 86400) -> str:
    """
    Generate JWT token for user
    Default expiry: 24 hours (86400 seconds)
    """
    payload = {
        "user_id": user.id,
        "email": user.email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def generate_refresh_token(user: User, expires_in: int = 604800) -> str:
    """
    Generate refresh token for user
    Default expiry: 7 days (604800 seconds)
    """
    payload = {
        "user_id": user.id,
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def decode_token(token: str) -> dict:
    """Decode and validate JWT token, checking blacklist"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )

        # Check if token is blacklisted
        from app.models.token_blacklist import TokenBlacklist
        jti = payload.get('jti')
        if jti and TokenBlacklist.is_blacklisted(jti):
            raise AuthenticationError("Token has been revoked", {"reason": "blacklisted"})

        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired", {"reason": "expired"})
    except jwt.InvalidTokenError as e:
        raise AuthenticationError("Invalid token", {"reason": str(e)})


def get_token_from_header() -> str:
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header:
        raise AuthenticationError("Missing Authorization header", {"header": "Authorization"})
    
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise AuthenticationError(
            "Invalid Authorization header format. Use: Bearer <token>",
            {"expected": "Bearer <token>"}
        )
    
    return parts[1]


def get_current_user() -> User:
    """Get current authenticated user from request context"""
    if hasattr(g, 'current_user') and g.current_user:
        return g.current_user
    
    token = get_token_from_header()
    payload = decode_token(token)
    
    user = User.find_by_id(payload.get('user_id'))
    
    if not user:
        raise AuthenticationError("User not found", {"user_id": payload.get('user_id')})
    
    if not user.is_active:
        raise AuthorizationError("User account is deactivated")
    
    g.current_user = user
    return user


def auth_required(f):
    """
    Decorator to require authentication for a route
    Sets g.current_user for use in route handler
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        get_current_user()  # This will raise if not authenticated
        return f(*args, **kwargs)
    return decorated


def auth_optional(f):
    """
    Decorator for routes where auth is optional
    Sets g.current_user if authenticated, None otherwise
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            get_current_user()
        except AuthenticationError:
            g.current_user = None
        return f(*args, **kwargs)
    return decorated


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format
    Returns (is_valid, error_message)
    """
    import re
    
    if not email or not email.strip():
        return False, "Email is required"
    
    email = email.strip().lower()
    
    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email too long"
    
    return True, ""


def generate_password_reset_token(user: User) -> str:
    """
    Generate a password reset token for the user
    Token expires in 1 hour
    """
    from app import db
    token = secrets.token_urlsafe(32)
    user.password_reset_token = token
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    db.session.commit()
    return token


def verify_password_reset_token(token: str) -> User:
    """
    Verify a password reset token and return the associated user
    Raises AuthenticationError if token is invalid or expired
    """
    user = User.query.filter_by(password_reset_token=token).filter(
        User.deleted_at.is_(None)
    ).first()

    if not user:
        raise AuthenticationError("Invalid reset token")

    if user.password_reset_expires < datetime.now(timezone.utc):
        raise AuthenticationError("Reset token has expired")

    return user


def clear_password_reset_token(user: User):
    """Clear the password reset token after successful reset"""
    from app import db
    user.password_reset_token = None
    user.password_reset_expires = None
    db.session.commit()


def admin_required(f):
    """
    Decorator to require admin access for a route
    Must be used after @auth_required
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user.is_admin:
            raise AuthorizationError("Admin access required")
        return f(*args, **kwargs)
    return decorated