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


@drugs_bp.route('/<string:drug_id>', methods=['GET'])
@handle_exceptions
def get_drug_detail(drug_id: str):
    """
    Get full drug label information by application number or name

    Path Params:
        drug_id (str): Application number or drug name
    """
    drug_id = drug_id.strip()
    if not drug_id:
        raise BadRequestError("Drug ID is required")

    from app.services.openfda_service import get_drug_detail as fetch_drug_detail
    result = fetch_drug_detail(drug_id)

    if not result.get('success'):
        from app.errors import ExternalAPIError
        raise ExternalAPIError(result.get('error', 'OpenFDA API error'), {"service": "openfda"})

    drug = result.get('drug')
    if not drug:
        from app.errors import NotFoundError
        raise NotFoundError(f"Drug '{drug_id}' not found", {"drug_id": drug_id})

    return api_response(
        data={"drug": drug},
        meta={
            "request_id": g.request_id,
            "source": "openfda",
            "endpoint": "/drug/label"
        }
    )


@drugs_bp.route('/interactions/<string:drug_name>', methods=['GET'])
@handle_exceptions
def drug_drug_interactions(drug_name: str):
    """
    Get drug-drug interaction info from the FDA label

    Path Params:
        drug_name (str): Drug name
    """
    drug_name = validate_query(drug_name, 'drug_name')

    from app.services.openfda_service import get_drug_drug_interactions
    result = get_drug_drug_interactions(drug_name)

    if not result.get('success'):
        from app.errors import ExternalAPIError
        raise ExternalAPIError(result.get('error', 'OpenFDA API error'), {"service": "openfda"})

    return api_response(
        data={
            "drug_queried": drug_name,
            "drug": result.get('drug'),
            "generic_name": result.get('generic_name'),
            "interactions_text": result.get('interactions_text', 'None listed')
        },
        meta={
            "request_id": g.request_id,
            "source": "openfda"
        }
    )


@drugs_bp.route('/side-effects', methods=['GET'])
@handle_exceptions
def side_effects():
    """
    Get side effects / adverse reactions from the FDA label

    Query Params:
        drug (str): Drug name (required)
    """
    drug_name = validate_query(request.args.get('drug', ''), 'drug')

    from app.services.openfda_service import get_side_effects as fetch_side_effects
    result = fetch_side_effects(drug_name)

    if not result.get('success'):
        from app.errors import ExternalAPIError
        raise ExternalAPIError(result.get('error', 'OpenFDA API error'), {"service": "openfda"})

    return api_response(
        data={
            "drug_queried": drug_name,
            "drug": result.get('drug'),
            "generic_name": result.get('generic_name'),
            "adverse_reactions": result.get('adverse_reactions', 'None listed'),
            "warnings": result.get('warnings', 'None listed'),
            "warnings_and_cautions": result.get('warnings_and_cautions', 'None listed')
        },
        meta={
            "request_id": g.request_id,
            "source": "openfda"
        }
    )