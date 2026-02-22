"""
Interaction History Routes
CRUD operations for user's interaction check history
"""

from flask import Blueprint, request, g
from app.services.auth_service import auth_required
from app.errors import api_response, BadRequestError, NotFoundError
from app.models.medication import InteractionCheck
from app import db

interaction_history_bp = Blueprint('interaction_history', __name__)


@interaction_history_bp.route('', methods=['GET'])
@auth_required
def get_history():
    """
    Get user's interaction check history
    
    Query params:
        limit (int): Max number of results (default: 50)
    
    Returns:
        { data: { history, count }, meta: {...} }
    """
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 100)  # Cap at 100
    
    history = InteractionCheck.get_user_history(g.current_user.id, limit)
    
    return api_response(
        {
            "history": [check.to_dict() for check in history],
            "count": len(history),
        }
    )


@interaction_history_bp.route('', methods=['POST'])
@auth_required
def save_check():
    """
    Save an interaction check to history
    
    Request body:
        {
            "food_name": "Grapefruit",
            "medications": ["Lipitor", "Warfarin"],
            "interactions": [
                {"drugName": "Lipitor", "severity": "high", "effect": "..."}
            ]
        }
    
    Returns:
        { data: { check }, meta: {...} }
    """
    data = request.get_json() or {}
    
    food_name = data.get('food_name', '').strip()
    medications = data.get('medications', [])
    interactions = data.get('interactions', [])
    
    if not food_name:
        raise BadRequestError("Food name is required", {"field": "food_name"})
    
    if not isinstance(medications, list) or len(medications) == 0:
        raise BadRequestError("Medications list is required", {"field": "medications"})
    
    # Save the check
    check = InteractionCheck.log_check(
        user_id=g.current_user.id,
        food_name=food_name,
        medications=medications,
        interactions=interactions
    )
    
    return api_response({"check": check.to_dict()}, status_code=201)


@interaction_history_bp.route('/<int:check_id>', methods=['DELETE'])
@auth_required
def delete_check(check_id):
    """
    Delete a specific interaction check from history
    
    Returns:
        { data: { deleted_id }, meta: {...} }
    """
    check = InteractionCheck.query.filter_by(
        id=check_id,
        user_id=g.current_user.id
    ).first()
    
    if not check:
        raise NotFoundError("Check not found", {"id": check_id})
    
    db.session.delete(check)
    db.session.commit()
    
    return api_response({"deleted_id": check_id})


@interaction_history_bp.route('', methods=['DELETE'])
@auth_required
def clear_history():
    """
    Clear all interaction check history for user
    
    Returns:
        { data: { deleted_count }, meta: {...} }
    """
    deleted = InteractionCheck.query.filter_by(user_id=g.current_user.id).delete()
    db.session.commit()
    
    return api_response({"deleted_count": deleted})


@interaction_history_bp.route('/stats', methods=['GET'])
@auth_required
def get_stats():
    """
    Get user's interaction check statistics

    Returns:
        Total checks, severity distribution, most-flagged foods
    """
    import json
    from sqlalchemy import func

    user_id = g.current_user.id

    total_checks = InteractionCheck.query.filter_by(user_id=user_id).count()

    # Get all checks to analyze
    checks = InteractionCheck.query.filter_by(user_id=user_id).all()

    severity_counts = {"high": 0, "medium": 0, "low": 0, "none": 0}
    food_counts = {}

    for check in checks:
        food_name = check.food_name.lower()
        food_counts[food_name] = food_counts.get(food_name, 0) + 1

        try:
            interactions = json.loads(check.interactions_json) if check.interactions_json else []
        except (json.JSONDecodeError, TypeError):
            interactions = []

        if not interactions:
            severity_counts["none"] += 1
        else:
            severities_found = set()
            for interaction in interactions:
                sev = interaction.get('severity', 'low').lower()
                if sev in severity_counts:
                    severities_found.add(sev)
            # Count the highest severity found
            if 'high' in severities_found:
                severity_counts['high'] += 1
            elif 'medium' in severities_found:
                severity_counts['medium'] += 1
            elif 'low' in severities_found:
                severity_counts['low'] += 1

    # Top 10 most-checked foods
    top_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return api_response({
        "total_checks": total_checks,
        "severity_distribution": severity_counts,
        "top_checked_foods": [{"food": f, "count": c} for f, c in top_foods]
    })
