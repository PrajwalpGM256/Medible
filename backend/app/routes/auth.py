"""
Authentication Routes
Handles user registration, login, logout, and profile
"""

from flask import Blueprint, request, g, jsonify
from app import db
from app.models.user import User
from app.services.auth_service import (
    generate_token,
    generate_refresh_token,
    decode_token,
    auth_required,
    validate_password,
    validate_email,
    generate_password_reset_token,
    verify_password_reset_token,
    clear_password_reset_token,
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
    
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if new_email != user.email:
            is_valid, error = validate_email(new_email)
            if not is_valid:
                raise ValidationError(error, {"field": "email"})
            if User.find_by_email(new_email):
                raise ValidationError("Email already registered", {"field": "email"})
            user.email = new_email
    
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


@auth_bp.route('/logout', methods=['POST'])
@auth_required
@handle_exceptions
def logout():
    """
    Logout user by blacklisting the current token
    """
    from app.services.auth_service import get_token_from_header
    from app.models.token_blacklist import TokenBlacklist
    from datetime import datetime, timezone

    token = get_token_from_header()
    payload = decode_token(token)

    jti = payload.get('jti', token[:32])  # Use first 32 chars as JTI if none
    exp = payload.get('exp')
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc)

    TokenBlacklist.blacklist_token(
        jti=jti,
        user_id=g.current_user.id,
        expires_at=expires_at
    )

    return api_response(
        data={"message": "Successfully logged out"},
        meta={"request_id": g.request_id}
    )


@auth_bp.route('/me', methods=['DELETE'])
@auth_required
@handle_exceptions
def delete_account():
    """
    Soft-delete the current user's account
    """
    data = request.get_json() or {}
    password = data.get('password', '')

    if not password:
        raise BadRequestError("Password is required to delete account")

    user = g.current_user
    if not user.check_password(password):
        raise AuthenticationError("Incorrect password")

    user.soft_delete()

    return api_response(
        data={"message": "Account has been deactivated"},
        meta={"request_id": g.request_id}
    )


@auth_bp.route('/forgot-password', methods=['POST'])
@handle_exceptions
def forgot_password():
    """
    Request a password reset token.
    Always returns success to avoid leaking whether an email exists.
    """
    data = request.get_json()
    if not data:
        raise BadRequestError("Request body must be JSON")

    email = data.get('email', '').strip().lower()
    if not email:
        raise BadRequestError("Email is required")

    user = User.find_by_email(email)
    if user:
        token = generate_password_reset_token(user)
        # In production, send this via email.
        # For dev, we return it in the response.
        import os
        if os.getenv('FLASK_ENV') == 'development':
            return api_response(
                data={
                    "message": "Password reset token generated",
                    "reset_token": token  # Only in dev!
                },
                meta={"request_id": g.request_id}
            )

    return api_response(
        data={"message": "If the email exists, a reset link has been sent"},
        meta={"request_id": g.request_id}
    )


@auth_bp.route('/reset-password', methods=['POST'])
@handle_exceptions
def reset_password():
    """
    Reset password using a reset token

    Request Body:
        { "token": "...", "new_password": "..." }
    """
    data = request.get_json()
    if not data:
        raise BadRequestError("Request body must be JSON")

    token = data.get('token', '').strip()
    new_password = data.get('new_password', '')

    if not token:
        raise BadRequestError("Reset token is required")
    if not new_password:
        raise BadRequestError("New password is required")

    is_valid, error = validate_password(new_password)
    if not is_valid:
        raise ValidationError(error, {"field": "new_password"})

    user = verify_password_reset_token(token)
    user.set_password(new_password)
    clear_password_reset_token(user)

    return api_response(
        data={"message": "Password has been reset successfully"},
        meta={"request_id": g.request_id}
    )


@auth_bp.route('/me/export', methods=['GET'])
@auth_required
@handle_exceptions
def export_user_data():
    """
    Export all user data (GDPR data portability)
    Returns a JSON dump of all user-related data
    """
    from app.models.medication import UserMedication, FoodLog, InteractionCheck, SearchHistory
    from app.models.favorites import FavoriteFood, MedicationReminder

    user = g.current_user
    user_id = user.id

    medications = UserMedication.query.filter_by(user_id=user_id).all()
    food_logs = FoodLog.query.filter_by(user_id=user_id).order_by(FoodLog.logged_date.desc()).all()
    interaction_checks = InteractionCheck.query.filter_by(user_id=user_id).all()
    search_history = SearchHistory.query.filter_by(user_id=user_id).all()
    favorites = FavoriteFood.query.filter_by(user_id=user_id).all()
    reminders = MedicationReminder.query.filter_by(user_id=user_id).all()

    export = {
        "user": user.to_dict(),
        "medications": [m.to_dict() for m in medications],
        "food_logs": [f.to_dict() for f in food_logs],
        "interaction_checks": [c.to_dict() for c in interaction_checks],
        "search_history": [s.to_dict() for s in search_history],
        "favorite_foods": [f.to_dict() for f in favorites],
        "medication_reminders": [r.to_dict() for r in reminders],
        "exported_at": __import__('datetime').datetime.now(
            __import__('datetime').timezone.utc
        ).isoformat()
    }

    return api_response(
        data={"export": export},
        meta={"request_id": g.request_id}
    )