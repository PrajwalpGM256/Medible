"""
Drug Routes - OpenFDA API Integration
Handles drug search, adverse events, and recall information
"""

from flask import Blueprint, request, g
from app.services.openfda_service import search_drug, get_adverse_events, get_drug_recalls
from app.errors import api_response, BadRequestError, ValidationError, handle_exceptions

drugs_bp = Blueprint('drugs', __name__)


def validate_limit(limit: int, max_limit: int = 20) -> int:
    """Validate and cap limit parameter"""
    if limit < 1:
        raise ValidationError("Limit must be at least 1", {"field": "limit", "min": 1})
    return min(limit, max_limit)


def validate_query(query: str, field_name: str = "q") -> str:
    """Validate search query parameter"""
    if not query or not query.strip():
        raise BadRequestError(f"Missing required parameter: {field_name}", {"field": field_name})
    if len(query) > 200:
        raise ValidationError("Query too long", {"field": field_name, "max_length": 200})
    return query.strip()


@drugs_bp.route('/search', methods=['GET'])
@handle_exceptions
def search_drugs():
    """
    Search drugs by brand or generic name
    
    Query Params:
        q (str): Search query (required)
        limit (int): Max results, default 5, max 20
    
    Returns:
        { data: { query, count, drugs }, meta: {...} }
    """
    query = validate_query(request.args.get('q', ''))
    limit = validate_limit(request.args.get('limit', 5, type=int))
    
    result = search_drug(query, limit)
    
    if not result.get('success'):
        from app.errors import ExternalAPIError
        raise ExternalAPIError(result.get('error', 'OpenFDA API error'), {"service": "openfda"})
    
    return api_response(
        data={
            "query": query,
            "count": result.get('count', 0),
            "drugs": result.get('drugs', [])
        },
        meta={
            "request_id": g.request_id,
            "source": "openfda",
            "endpoint": "/drug/label"
        }
    )


@drugs_bp.route('/adverse-events', methods=['GET'])
@handle_exceptions
def adverse_events():
    """
    Get adverse event reports for a drug
    
    Query Params:
        drug (str): Drug name (required)
        limit (int): Max results, default 5, max 20
    """
    drug_name = validate_query(request.args.get('drug', ''), 'drug')
    limit = validate_limit(request.args.get('limit', 5, type=int))
    
    result = get_adverse_events(drug_name, limit)
    
    if not result.get('success'):
        from app.errors import ExternalAPIError
        raise ExternalAPIError(result.get('error', 'OpenFDA API error'), {"service": "openfda"})
    
    return api_response(
        data={
            "drug": drug_name,
            "count": result.get('count', 0),
            "events": result.get('events', [])
        },
        meta={
            "request_id": g.request_id,
            "source": "openfda",
            "endpoint": "/drug/event"
        }
    )


@drugs_bp.route('/recalls', methods=['GET'])
@handle_exceptions
def recalls():
    """
    Check for drug recalls
    
    Query Params:
        drug (str): Drug name (required)
        limit (int): Max results, default 5, max 20
    """
    drug_name = validate_query(request.args.get('drug', ''), 'drug')
    limit = validate_limit(request.args.get('limit', 5, type=int))
    
    result = get_drug_recalls(drug_name, limit)
    
    if not result.get('success'):
        from app.errors import ExternalAPIError
        raise ExternalAPIError(result.get('error', 'OpenFDA API error'), {"service": "openfda"})
    
    return api_response(
        data={
            "drug": drug_name,
            "count": result.get('count', 0),
            "recalls": result.get('recalls', [])
        },
        meta={
            "request_id": g.request_id,
            "source": "openfda",
            "endpoint": "/drug/enforcement"
        }
    )