"""
Food-Drug Interaction Routes
Endpoints for checking interactions between foods and medications
"""

from flask import Blueprint, request, g
from app.services.interaction_service import (
    check_interaction,
    check_food_against_medications,
    get_drug_interactions,
    get_food_interactions,
    get_interaction_stats
)
from app.errors import (
    api_response,
    BadRequestError,
    ValidationError,
    NotFoundError,
    handle_exceptions
)

interactions_bp = Blueprint('interactions', __name__)


def validate_param(value: str, field_name: str, max_length: int = 100) -> str:
    """Validate a required string parameter"""
    if not value or not value.strip():
        raise BadRequestError(
            f"Missing required parameter: {field_name}",
            {"field": field_name}
        )
    value = value.strip()
    if len(value) > max_length:
        raise ValidationError(
            f"Parameter too long: {field_name}",
            {"field": field_name, "max_length": max_length}
        )
    return value


@interactions_bp.route('/check', methods=['GET'])
@handle_exceptions
def check_single_interaction():
    """
    Check for interaction between a single food and drug
    
    Query Params:
        food (str): Food name (required)
        drug (str): Drug name (required)
    
    Returns:
        { data: { food, drug, has_interaction, interactions }, meta: {...} }
    """
    food = validate_param(request.args.get('food', ''), 'food')
    drug = validate_param(request.args.get('drug', ''), 'drug')
    
    results = check_interaction(food, drug)
    
    interactions = []
    for r in results:
        interactions.append({
            "id": r.interaction_id,
            "severity": r.severity,
            "food_matched": r.food_name,
            "drug_matched": r.drug_name,
            "drug_class": r.drug_class,
            "effect": r.effect,
            "recommendation": r.recommendation,
            "evidence_level": r.evidence_level
        })
    
    # Determine overall severity (highest found)
    severity_order = ['high', 'medium', 'low']
    overall_severity = None
    for sev in severity_order:
        if any(i['severity'] == sev for i in interactions):
            overall_severity = sev
            break
    
    return api_response(
        data={
            "food_queried": food,
            "drug_queried": drug,
            "has_interaction": len(interactions) > 0,
            "interaction_count": len(interactions),
            "overall_severity": overall_severity,
            "interactions": interactions
        },
        meta={
            "request_id": g.request_id,
            "source": "medible_interaction_db"
        }
    )


@interactions_bp.route('/check-multiple', methods=['POST'])
@handle_exceptions
def check_multiple_interactions():
    """
    Check a food against multiple medications
    
    Request Body (JSON):
        {
            "food": "grapefruit",
            "medications": ["lipitor", "lisinopril", "metformin"]
        }
    
    Returns:
        { data: { food_checked, medications_checked, warnings }, meta: {...} }
    """
    data = request.get_json()
    
    if not data:
        raise BadRequestError("Request body must be JSON", {"expected": "application/json"})
    
    food = validate_param(data.get('food', ''), 'food')
    medications = data.get('medications', [])
    
    if not isinstance(medications, list):
        raise ValidationError(
            "medications must be an array",
            {"field": "medications", "received": type(medications).__name__}
        )
    
    if len(medications) == 0:
        raise ValidationError(
            "medications array cannot be empty",
            {"field": "medications"}
        )
    
    if len(medications) > 20:
        raise ValidationError(
            "Too many medications (max 20)",
            {"field": "medications", "max": 20, "received": len(medications)}
        )
    
    # Validate each medication
    validated_meds = []
    for i, med in enumerate(medications):
        if not isinstance(med, str) or not med.strip():
            raise ValidationError(
                f"Invalid medication at index {i}",
                {"field": f"medications[{i}]", "value": med}
            )
        validated_meds.append(med.strip())
    
    result = check_food_against_medications(food, validated_meds)
    
    return api_response(
        data=result,
        meta={
            "request_id": g.request_id,
            "source": "medible_interaction_db"
        },
        status_code=200
    )


@interactions_bp.route('/drug/<drug_name>', methods=['GET'])
@handle_exceptions
def get_interactions_for_drug(drug_name: str):
    """
    Get all known food interactions for a specific drug
    
    Path Params:
        drug_name (str): Drug name or brand name
    
    Returns:
        { data: { drug, interaction_count, foods_to_avoid }, meta: {...} }
    """
    drug = validate_param(drug_name, 'drug_name')
    
    interactions = get_drug_interactions(drug)
    
    return api_response(
        data={
            "drug_queried": drug,
            "interaction_count": len(interactions),
            "foods_to_avoid": interactions
        },
        meta={
            "request_id": g.request_id,
            "source": "medible_interaction_db"
        }
    )


@interactions_bp.route('/food/<food_name>', methods=['GET'])
@handle_exceptions
def get_interactions_for_food(food_name: str):
    """
    Get all known drug interactions for a specific food
    
    Path Params:
        food_name (str): Food name
    
    Returns:
        { data: { food, interaction_count, drugs_affected }, meta: {...} }
    """
    food = validate_param(food_name, 'food_name')
    
    interactions = get_food_interactions(food)
    
    return api_response(
        data={
            "food_queried": food,
            "interaction_count": len(interactions),
            "drugs_affected": interactions
        },
        meta={
            "request_id": g.request_id,
            "source": "medible_interaction_db"
        }
    )


@interactions_bp.route('/stats', methods=['GET'])
@handle_exceptions
def interaction_stats():
    """
    Get statistics about the interaction database
    
    Returns:
        { data: { total_interactions, severity_breakdown, ... }, meta: {...} }
    """
    stats = get_interaction_stats()
    
    return api_response(
        data=stats,
        meta={
            "request_id": g.request_id,
            "source": "medible_interaction_db"
        }
    )


@interactions_bp.route('/health', methods=['GET'])
def health():
    """Health check for interactions service"""
    stats = get_interaction_stats()
    
    return api_response(
        data={
            "status": "healthy" if stats.get("total_interactions", 0) > 0 else "degraded",
            "interactions_loaded": stats.get("total_interactions", 0)
        }
    )


@interactions_bp.route('/batch-check', methods=['POST'])
@handle_exceptions
def batch_check():
    """
    Check all of today's food diary entries against all active medications

    Requires auth. Checks every food logged today against every active med.
    """
    from app.services.auth_service import get_current_user
    from app.models.medication import UserMedication, FoodLog
    from datetime import date
    from sqlalchemy import func

    get_current_user()
    from flask import g
    user_id = g.current_user.id
    today = date.today()

    # Get today's food names
    today_foods = FoodLog.query.filter_by(user_id=user_id).filter(
        func.date(FoodLog.logged_date) == today
    ).all()

    food_names = list(set(f.food_name.lower() for f in today_foods))

    # Get active medication names
    med_names = UserMedication.get_user_medication_names(user_id, active_only=True)

    if not food_names or not med_names:
        return api_response(
            data={
                "foods_checked": len(food_names),
                "medications_checked": len(med_names),
                "total_warnings": 0,
                "results": []
            },
            meta={"request_id": g.request_id}
        )

    results = []
    total_warnings = 0
    for food in food_names:
        result = check_food_against_medications(food, med_names)
        warnings = result.get('warnings', [])
        if warnings:
            total_warnings += len(warnings)
            results.append({
                "food": food,
                "warning_count": len(warnings),
                "warnings": warnings
            })

    return api_response(
        data={
            "foods_checked": len(food_names),
            "medications_checked": len(med_names),
            "total_warnings": total_warnings,
            "results": results
        },
        meta={
            "request_id": g.request_id,
            "source": "medible_interaction_db"
        }
    )


@interactions_bp.route('/report', methods=['POST'])
@handle_exceptions
def report_interaction():
    """
    Report a missing food-drug interaction for review

    Request Body:
        {
            "food_name": "Pomelo",
            "drug_name": "Lipitor",
            "description": "Pomelo has similar compounds to grapefruit",
            "severity_suggestion": "high"
        }
    """
    from app.services.auth_service import get_current_user
    from app.models.favorites import InteractionReport
    from app import db

    get_current_user()

    data = request.get_json()
    if not data:
        raise BadRequestError("Request body must be JSON")

    food_name = validate_param(data.get('food_name', ''), 'food_name')
    drug_name = validate_param(data.get('drug_name', ''), 'drug_name')

    severity = data.get('severity_suggestion', '').lower()
    if severity and severity not in ('low', 'medium', 'high'):
        raise ValidationError(
            "severity_suggestion must be low, medium, or high",
            {"field": "severity_suggestion"}
        )

    report = InteractionReport(
        user_id=g.current_user.id,
        food_name=food_name,
        drug_name=drug_name,
        description=data.get('description', '').strip() or None,
        severity_suggestion=severity or None
    )

    db.session.add(report)
    db.session.commit()

    return api_response(
        data={"report": report.to_dict()},
        meta={"request_id": g.request_id},
        status_code=201
    )