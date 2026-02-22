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


@foods_bp.route('/favorites', methods=['GET'])
@handle_exceptions
def get_favorites():
    """Get user's favorite foods"""
    from app.services.auth_service import auth_required, get_current_user
    get_current_user()
    from app.models.favorites import FavoriteFood

    favorites = FavoriteFood.get_user_favorites(g.current_user.id)

    return api_response(
        data={
            "favorites": [f.to_dict() for f in favorites],
            "count": len(favorites)
        },
        meta={"request_id": g.request_id}
    )


@foods_bp.route('/favorites', methods=['POST'])
@handle_exceptions
def add_favorite():
    """Add a food to favorites"""
    from app.services.auth_service import get_current_user
    get_current_user()
    from app.models.favorites import FavoriteFood
    from app import db
    import json

    data = request.get_json()
    if not data:
        raise BadRequestError("Request body must be JSON")

    food_name = data.get('food_name', '').strip()
    if not food_name:
        raise BadRequestError("food_name is required")

    source = data.get('source', 'usda')
    if source not in ('usda', 'openfoodfacts'):
        raise ValidationError("source must be 'usda' or 'openfoodfacts'")

    # Check if already favorited
    existing = FavoriteFood.query.filter_by(
        user_id=g.current_user.id, food_name=food_name, source=source
    ).first()
    if existing:
        return api_response(
            data={"favorite": existing.to_dict(), "message": "Already in favorites"},
            meta={"request_id": g.request_id}
        )

    nutrition = data.get('nutrition')
    fav = FavoriteFood(
        user_id=g.current_user.id,
        food_name=food_name,
        fdc_id=data.get('fdc_id'),
        off_id=data.get('off_id'),
        source=source,
        nutrition_snapshot=json.dumps(nutrition) if nutrition else None
    )
    db.session.add(fav)
    db.session.commit()

    return api_response(
        data={"favorite": fav.to_dict()},
        meta={"request_id": g.request_id},
        status_code=201
    )


@foods_bp.route('/favorites/<int:fav_id>', methods=['DELETE'])
@handle_exceptions
def remove_favorite(fav_id: int):
    """Remove a food from favorites"""
    from app.services.auth_service import get_current_user
    get_current_user()
    from app.models.favorites import FavoriteFood
    from app import db

    fav = FavoriteFood.query.filter_by(id=fav_id, user_id=g.current_user.id).first()
    if not fav:
        raise NotFoundError("Favorite not found", {"id": fav_id})

    db.session.delete(fav)
    db.session.commit()

    return api_response(
        data={"deleted_id": fav_id},
        meta={"request_id": g.request_id}
    )


@foods_bp.route('/recent', methods=['GET'])
@handle_exceptions
def get_recent_foods():
    """Get recently searched/logged foods for the user"""
    from app.services.auth_service import get_current_user
    get_current_user()
    from app.models.medication import SearchHistory

    limit = min(max(request.args.get('limit', 10, type=int), 1), 50)

    recent = SearchHistory.query.filter_by(
        user_id=g.current_user.id, search_type='food'
    ).order_by(SearchHistory.searched_at.desc()).limit(limit).all()

    return api_response(
        data={
            "recent_foods": [r.to_dict() for r in recent],
            "count": len(recent)
        },
        meta={"request_id": g.request_id}
    )


@foods_bp.route('/unified-search', methods=['GET'])
@handle_exceptions
def unified_search():
    """
    Search across both USDA and Open Food Facts simultaneously

    Query Params:
        q (str): Search query (required)
        limit (int): Max results per source, default 5
        source (str): 'all' (default), 'usda', or 'off'
    """
    query = validate_query(request.args.get('q', ''))
    limit = validate_limit(request.args.get('limit', 5, type=int), max_limit=20)
    source = request.args.get('source', 'all').lower()

    results = {"usda": [], "openfoodfacts": []}

    if source in ('all', 'usda'):
        usda_result = search_food(query, limit)
        if usda_result.get('success'):
            results["usda"] = usda_result.get('foods', [])

    if source in ('all', 'off'):
        from app.services.openfoodfacts_service import search_products
        off_result = search_products(query, limit)
        if off_result.get('success'):
            results["openfoodfacts"] = off_result.get('products', [])

    total_count = len(results["usda"]) + len(results["openfoodfacts"])

    return api_response(
        data={
            "query": query,
            "source": source,
            "total_count": total_count,
            "usda": {
                "count": len(results["usda"]),
                "foods": results["usda"]
            },
            "openfoodfacts": {
                "count": len(results["openfoodfacts"]),
                "products": results["openfoodfacts"]
            }
        },
        meta={
            "request_id": g.request_id,
            "sources_queried": ["usda", "openfoodfacts"] if source == 'all' else [source]
        }
    )