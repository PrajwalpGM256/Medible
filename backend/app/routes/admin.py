"""
Admin Routes
Endpoints for platform administration (requires admin role)
"""

from flask import Blueprint, request, g
from app.services.auth_service import auth_required, admin_required
from app.models.user import User
from app.models.medication import UserMedication, SearchHistory, FoodLog, InteractionCheck
from app.models.favorites import InteractionReport
from app import db
from app.errors import (
    api_response,
    BadRequestError,
    NotFoundError,
    ValidationError,
    handle_exceptions
)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
@auth_required
@admin_required
@handle_exceptions
def list_users():
    """
    List all users (paginated)

    Query Params:
        page (int): Page number, default 1
        per_page (int): Results per page, default 20, max 100
        include_deleted (bool): Include soft-deleted users, default false
    """
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(max(request.args.get('per_page', 20, type=int), 1), 100)
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

    query = User.query

    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = []
    for user in pagination.items:
        user_data = user.to_dict()
        user_data['is_admin'] = user.is_admin
        user_data['is_deleted'] = user.is_deleted
        user_data['last_login_at'] = user.last_login_at.isoformat() if user.last_login_at else None
        users.append(user_data)

    return api_response(
        data={
            "users": users,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        },
        meta={"request_id": g.request_id}
    )


@admin_bp.route('/users/<int:user_id>', methods=['PATCH'])
@auth_required
@admin_required
@handle_exceptions
def manage_user(user_id: int):
    """
    Manage a user account (activate/deactivate, toggle admin)

    Request Body:
        {
            "is_active": true/false,
            "is_admin": true/false
        }
    """
    data = request.get_json()
    if not data:
        raise BadRequestError("Request body must be JSON")

    # Find user including deleted ones
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("User not found", {"user_id": user_id})

    if user.id == g.current_user.id:
        raise BadRequestError("Cannot modify your own admin account")

    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
        if data['is_active'] and user.deleted_at:
            # Reactivating a soft-deleted user
            user.deleted_at = None

    if 'is_admin' in data:
        user.is_admin = bool(data['is_admin'])

    db.session.commit()

    user_data = user.to_dict()
    user_data['is_admin'] = user.is_admin

    return api_response(
        data={"user": user_data},
        meta={"request_id": g.request_id}
    )


@admin_bp.route('/users', methods=['POST'])
@auth_required
@admin_required
@handle_exceptions
def create_user():
    """
    Create a new user account (admin only)
    
    Request Body:
        {
            "email": "...",
            "password": "...",
            "first_name": "...",
            "last_name": "...",
            "is_admin": true/false,
            "is_active": true/false
        }
    """
    from app.services.auth_service import validate_email, validate_password
    data = request.get_json()
    if not data:
        raise BadRequestError("Request body must be JSON")

    email = data.get('email', '').strip().lower()
    is_valid, error = validate_email(email)
    if not is_valid:
        raise ValidationError(error, {"field": "email"})

    if User.find_by_email(email):
        raise ValidationError("Email already registered", {"field": "email"})

    password = data.get('password', '')
    is_valid, error = validate_password(password)
    if not is_valid:
        raise ValidationError(error, {"field": "password"})

    user = User(
        email=email,
        password=password,
        first_name=data.get('first_name', '').strip() or None,
        last_name=data.get('last_name', '').strip() or None
    )
    
    user.is_admin = bool(data.get('is_admin', False))
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])

    db.session.add(user)
    db.session.commit()

    user_data = user.to_dict()
    user_data['is_admin'] = user.is_admin
    user_data['is_deleted'] = user.is_deleted
    user_data['last_login_at'] = None

    return api_response(
        data={"user": user_data},
        meta={"request_id": g.request_id},
        status_code=201
    )


@admin_bp.route('/stats', methods=['GET'])
@auth_required
@admin_required
@handle_exceptions
def platform_stats():
    """
    Get platform-wide statistics

    Returns:
        Total users, active users, total medications, total food logs,
        total interaction checks, top drugs, top foods
    """
    from sqlalchemy import func

    total_users = User.query.filter(User.deleted_at.is_(None)).count()
    active_users = User.query.filter(
        User.deleted_at.is_(None),
        User.is_active.is_(True)
    ).count()
    total_medications = UserMedication.query.count()
    total_food_logs = FoodLog.query.count()
    total_checks = InteractionCheck.query.count()
    total_searches = SearchHistory.query.count()
    total_reports = InteractionReport.query.count()

    # Top 10 most-added drugs
    top_drugs = db.session.query(
        UserMedication.drug_name,
        func.count(UserMedication.id).label('count')
    ).group_by(UserMedication.drug_name).order_by(
        func.count(UserMedication.id).desc()
    ).limit(10).all()

    # Top 10 most-searched foods
    top_foods = db.session.query(
        SearchHistory.search_term,
        func.count(SearchHistory.id).label('count')
    ).filter_by(search_type='food').group_by(
        SearchHistory.search_term
    ).order_by(
        func.count(SearchHistory.id).desc()
    ).limit(10).all()

    return api_response(
        data={
            "users": {
                "total": total_users,
                "active": active_users
            },
            "content": {
                "total_medications": total_medications,
                "total_food_logs": total_food_logs,
                "total_interaction_checks": total_checks,
                "total_searches": total_searches,
                "total_interaction_reports": total_reports
            },
            "top_drugs": [{"drug_name": d[0], "count": d[1]} for d in top_drugs],
            "top_foods": [{"food_name": f[0], "count": f[1]} for f in top_foods]
        },
        meta={"request_id": g.request_id}
    )
