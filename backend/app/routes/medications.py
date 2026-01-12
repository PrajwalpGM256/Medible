"""
User Medications Routes
CRUD operations for user's saved medications
"""

from flask import Blueprint, request, g
from datetime import datetime
from app import db
from app.models.medication import UserMedication
from app.services.auth_service import auth_required
from app.services.interaction_service import check_food_against_medications, get_drug_interactions
from app.errors import (
    api_response,
    BadRequestError,
    ValidationError,
    NotFoundError,
    handle_exceptions
)

medications_bp = Blueprint('medications', __name__)


def validate_medication_data(data: dict, require_drug_name: bool = True) -> dict:
    """Validate and sanitize medication data"""
    if not data:
        raise BadRequestError("Request body must be JSON")
    
    validated = {}
    
    # Required field
    if require_drug_name:
        drug_name = data.get('drug_name', '').strip()
        if not drug_name:
            raise ValidationError("drug_name is required", {"field": "drug_name"})
        if len(drug_name) > 255:
            raise ValidationError("drug_name too long", {"field": "drug_name", "max": 255})
        validated['drug_name'] = drug_name
    
    # Optional string fields
    optional_fields = ['brand_name', 'generic_name', 'dosage', 'frequency', 'prescriber', 'pharmacy', 'notes']
    max_lengths = {'brand_name': 255, 'generic_name': 255, 'dosage': 100, 'frequency': 100, 'prescriber': 255, 'pharmacy': 255, 'notes': 1000}
    
    for field in optional_fields:
        if field in data:
            value = data[field]
            if value is not None:
                value = str(value).strip()
                if len(value) > max_lengths.get(field, 255):
                    raise ValidationError(f"{field} too long", {"field": field, "max": max_lengths[field]})
                validated[field] = value if value else None
            else:
                validated[field] = None
    
    # Boolean field
    if 'is_active' in data:
        validated['is_active'] = bool(data['is_active'])
    
    # Date fields
    for date_field in ['start_date', 'end_date']:
        if date_field in data:
            value = data[date_field]
            if value:
                try:
                    validated[date_field] = datetime.fromisoformat(value.replace('Z', '+00:00')).date()
                except (ValueError, AttributeError):
                    raise ValidationError(f"Invalid date format for {date_field}", {"field": date_field, "expected": "YYYY-MM-DD"})
            else:
                validated[date_field] = None
    
    return validated


@medications_bp.route('', methods=['GET'])
@auth_required
@handle_exceptions
def list_medications():
    """
    List all medications for current user
    
    Query Params:
        active_only (bool): Filter to active medications only (default: false)
    
    Returns:
        { data: { medications, count }, meta: {...} }
    """
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    medications = UserMedication.get_user_medications(g.current_user.id, active_only)
    
    return api_response(
        data={
            "medications": [med.to_dict() for med in medications],
            "count": len(medications),
            "active_only": active_only
        },
        meta={"request_id": g.request_id}
    )


@medications_bp.route('', methods=['POST'])
@auth_required
@handle_exceptions
def add_medication():
    """
    Add a new medication to user's list
    
    Request Body:
        {
            "drug_name": "Lipitor",
            "brand_name": "Lipitor",
            "generic_name": "atorvastatin",
            "dosage": "20mg",
            "frequency": "once daily",
            "notes": "Take with food"
        }
    
    Returns:
        { data: { medication }, meta: {...} }
    """
    data = validate_medication_data(request.get_json())
    
    # Check if medication already exists for user
    existing = UserMedication.query.filter_by(
        user_id=g.current_user.id,
        drug_name=data['drug_name']
    ).first()
    
    if existing:
        raise ValidationError(
            "Medication already exists in your list",
            {"field": "drug_name", "existing_id": existing.id}
        )
    
    # Create medication
    medication = UserMedication(
        user_id=g.current_user.id,
        **data
    )
    
    db.session.add(medication)
    db.session.commit()
    
    # Get any known interactions for this drug
    interactions = get_drug_interactions(data['drug_name'])
    
    return api_response(
        data={
            "medication": medication.to_dict(),
            "known_food_interactions": len(interactions),
            "interactions": interactions[:3] if interactions else []  # Show top 3
        },
        meta={"request_id": g.request_id},
        status_code=201
    )


@medications_bp.route('/<int:medication_id>', methods=['GET'])
@auth_required
@handle_exceptions
def get_medication(medication_id: int):
    """
    Get a specific medication
    
    Returns:
        { data: { medication, interactions }, meta: {...} }
    """
    medication = UserMedication.query.filter_by(
        id=medication_id,
        user_id=g.current_user.id
    ).first()
    
    if not medication:
        raise NotFoundError("Medication not found", {"medication_id": medication_id})
    
    # Get interactions for this drug
    interactions = get_drug_interactions(medication.drug_name)
    
    return api_response(
        data={
            "medication": medication.to_dict(),
            "food_interactions": interactions
        },
        meta={"request_id": g.request_id}
    )


@medications_bp.route('/<int:medication_id>', methods=['PATCH'])
@auth_required
@handle_exceptions
def update_medication(medication_id: int):
    """
    Update a medication
    
    Request Body:
        {
            "dosage": "40mg",
            "frequency": "twice daily",
            "is_active": true
        }
    
    Returns:
        { data: { medication }, meta: {...} }
    """
    medication = UserMedication.query.filter_by(
        id=medication_id,
        user_id=g.current_user.id
    ).first()
    
    if not medication:
        raise NotFoundError("Medication not found", {"medication_id": medication_id})
    
    data = validate_medication_data(request.get_json(), require_drug_name=False)
    
    # Update fields
    for key, value in data.items():
        setattr(medication, key, value)
    
    db.session.commit()
    
    return api_response(
        data={"medication": medication.to_dict()},
        meta={"request_id": g.request_id}
    )


@medications_bp.route('/<int:medication_id>', methods=['DELETE'])
@auth_required
@handle_exceptions
def delete_medication(medication_id: int):
    """
    Delete a medication
    
    Returns:
        204 No Content
    """
    medication = UserMedication.query.filter_by(
        id=medication_id,
        user_id=g.current_user.id
    ).first()
    
    if not medication:
        raise NotFoundError("Medication not found", {"medication_id": medication_id})
    
    db.session.delete(medication)
    db.session.commit()
    
    return '', 204


@medications_bp.route('/check-food', methods=['POST'])
@auth_required
@handle_exceptions
def check_food_interactions():
    """
    Check a food against all of user's active medications
    
    Request Body:
        {
            "food": "grapefruit"
        }
    
    Returns:
        { data: { food, medications_checked, warnings }, meta: {...} }
    """
    data = request.get_json()
    
    if not data:
        raise BadRequestError("Request body must be JSON")
    
    food = data.get('food', '').strip()
    if not food:
        raise ValidationError("food is required", {"field": "food"})
    
    # Get user's active medications
    medication_names = UserMedication.get_user_medication_names(g.current_user.id, active_only=True)
    
    if not medication_names:
        return api_response(
            data={
                "food_checked": food,
                "medications_checked": [],
                "total_warnings": 0,
                "message": "No active medications in your list",
                "warnings": {"high": [], "medium": [], "low": []}
            },
            meta={"request_id": g.request_id}
        )
    
    # Check interactions
    result = check_food_against_medications(food, medication_names)
    
    return api_response(
        data=result,
        meta={"request_id": g.request_id}
    )


@medications_bp.route('/interactions-summary', methods=['GET'])
@auth_required
@handle_exceptions
def get_all_interactions():
    """
    Get all known food interactions for user's medications
    
    Returns:
        { data: { medications_with_interactions }, meta: {...} }
    """
    medications = UserMedication.get_user_medications(g.current_user.id, active_only=True)
    
    result = []
    total_interactions = 0
    
    for med in medications:
        interactions = get_drug_interactions(med.drug_name)
        if interactions:
            total_interactions += len(interactions)
            result.append({
                "medication": med.to_dict(),
                "food_interactions": interactions
            })
    
    return api_response(
        data={
            "medications_with_interactions": result,
            "total_medications": len(medications),
            "medications_with_warnings": len(result),
            "total_food_interactions": total_interactions
        },
        meta={"request_id": g.request_id}
    )