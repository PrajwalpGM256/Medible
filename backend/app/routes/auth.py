"""
Authentication Routes
Handles user registration, login, logout, and profile
"""

from flask import Blueprint, request, g
from app import db
from app.models.user import User
from app.services.auth_service import (
    generate_token,
    generate_refresh_token,
    decode_token,
    auth_required,
    validate_password,
    validate_email,
    AuthenticationError
)
from app.errors import (
    api_response,
    BadRequestError,
    ValidationError,
    handle_exceptions
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@handle_exceptions
def register():
    """
    Register a new user
    """
    data = request.get_json()
    
    if not data:
        raise BadRequestError("Request body must be JSON")
    
    # Validate email
    email = data.get('email', '').strip().lower()
    is_valid, error = validate_email(email)
    if not is_valid:
        raise ValidationError(error, {"field": "email"})
    
    # Check if email already exists
    if User.find_by_email(email):
        raise ValidationError("Email already registered", {"field": "email"})
    
    # Validate password
    password = data.get('password', '')
    is_valid, error = validate_password(password)
    if not is_valid:
        raise ValidationError(error, {"field": "password"})
    
    # Create user
    user = User(
        email=email,
        password=password,
        first_name=data.get('first_name', '').strip() or None,
        last_name=data.get('last_name', '').strip() or None
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Generate tokens
    access_token = generate_token(user)
    refresh_token = generate_refresh_token(user)
    
    return api_response(
        data={
            "user": user.to_dict(),
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": 86400
            }
        },
        meta={"request_id": g.request_id},
        status_code=201
    )


@auth_bp.route('/login', methods=['POST'])
@handle_exceptions
def login():
    """
    Authenticate user and return tokens
    """
    data = request.get_json()
    
    if not data:
        raise BadRequestError("Request body must be JSON")
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        raise BadRequestError("Email and password are required")
    
    # Find user
    user = User.find_by_email(email)
    
    if not user or not user.check_password(password):
        raise AuthenticationError("Invalid email or password")
    
    if not user.is_active:
        raise AuthenticationError("Account is deactivated")
    
    # Update last login
    user.update_last_login()
    
    # Generate tokens
    access_token = generate_token(user)
    refresh_token = generate_refresh_token(user)
    
    return api_response(
        data={
            "user": user.to_dict(),
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": 86400
            }
        },
        meta={"request_id": g.request_id}
    )


@auth_bp.route('/refresh', methods=['POST'])
@handle_exceptions
def refresh():
    """
    Refresh access token using refresh token
    """
    data = request.get_json()
    
    if not data:
        raise BadRequestError("Request body must be JSON")
    
    refresh_token = data.get('refresh_token', '')
    
    if not refresh_token:
        raise BadRequestError("Refresh token is required")
    
    # Decode and validate refresh token
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise AuthenticationError("Invalid refresh token")
    
    if payload.get('type') != 'refresh':
        raise AuthenticationError("Invalid token type")
    
    # Find user
    user = User.find_by_id(payload.get('user_id'))
    
    if not user or not user.is_active:
        raise AuthenticationError("User not found or deactivated")
    
    # Generate new access token
    access_token = generate_token(user)
    
    return api_response(
        data={
            "tokens": {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 86400
            }
        },
        meta={"request_id": g.request_id}
    )


@auth_bp.route('/me', methods=['GET'])
@auth_required
@handle_exceptions
def get_profile():
    """
    Get current user's profile
    """
    return api_response(
        data={"user": g.current_user.to_dict()},
        meta={"request_id": g.request_id}
    )


@auth_bp.route('/me', methods=['PATCH'])
@auth_required
@handle_exceptions
def update_profile():
    """
    Update current user's profile
    """
    data = request.get_json()
    
    if not data:
        raise BadRequestError("Request body must be JSON")
    
    user = g.current_user
    
    if 'first_name' in data:
        user.first_name = data['first_name'].strip() or None
    
    if 'last_name' in data:
        user.last_name = data['last_name'].strip() or None
    
    db.session.commit()
    
    return api_response(
        data={"user": user.to_dict()},
        meta={"request_id": g.request_id}
    )


@auth_bp.route('/me/password', methods=['PUT'])
@auth_required
@handle_exceptions
def change_password():
    """
    Change current user's password
    """
    data = request.get_json()
    
    if not data:
        raise BadRequestError("Request body must be JSON")
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        raise BadRequestError("Current password and new password are required")
    
    user = g.current_user
    
    if not user.check_password(current_password):
        raise AuthenticationError("Current password is incorrect")
    
    is_valid, error = validate_password(new_password)
    if not is_valid:
        raise ValidationError(error, {"field": "new_password"})
    
    user.set_password(new_password)
    db.session.commit()
    
    return api_response(
        data={"message": "Password updated successfully"},
        meta={"request_id": g.request_id}
    )