"""
Food Routes - USDA FoodData Central API Integration
Handles food search and nutrition information
"""

from flask import Blueprint, request, g
from app.services.usda_service import search_food, get_food_details
from app.errors import api_response, BadRequestError, ValidationError, NotFoundError, ExternalAPIError, handle_exceptions

foods_bp = Blueprint('foods', __name__)


def validate_limit(limit: int, max_limit: int = 50) -> int:
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


@foods_bp.route('/search', methods=['GET'])
@handle_exceptions
def search_foods():
    """
    Search foods by name
    
    Query Params:
        q (str): Search query (required)
        limit (int): Max results, default 10, max 50
    
    Returns:
        { data: { query, count, total_hits, foods }, meta: {...} }
    """
    query = validate_query(request.args.get('q', ''))
    limit = validate_limit(request.args.get('limit', 10, type=int))
    
    result = search_food(query, limit)
    
    if not result.get('success'):
        raise ExternalAPIError(result.get('error', 'USDA API error'), {"service": "usda"})
    
    return api_response(
        data={
            "query": query,
            "count": result.get('count', 0),
            "total_hits": result.get('total_hits', 0),
            "foods": result.get('foods', [])
        },
        meta={
            "request_id": g.request_id,
            "source": "usda_fooddata_central",
            "endpoint": "/foods/search"
        }
    )


@foods_bp.route('/<int:fdc_id>', methods=['GET'])
@handle_exceptions
def get_food(fdc_id: int):
    """
    Get detailed nutrition info for a specific food
    
    Path Params:
        fdc_id (int): USDA FoodData Central ID
    
    Returns:
        { data: { fdc_id, food }, meta: {...} }
    """
    if fdc_id < 1:
        raise ValidationError("Invalid FDC ID", {"field": "fdc_id", "value": fdc_id})
    
    result = get_food_details(fdc_id)
    
    if not result.get('success'):
        error_msg = result.get('error', '')
        if 'not found' in error_msg.lower():
            raise NotFoundError(f"Food with FDC ID {fdc_id} not found", {"fdc_id": fdc_id})
        raise ExternalAPIError(error_msg, {"service": "usda"})
    
    return api_response(
        data={
            "fdc_id": fdc_id,
            "food": result.get('food')
        },
        meta={
            "request_id": g.request_id,
            "source": "usda_fooddata_central",
            "endpoint": f"/food/{fdc_id}"
        }
    )