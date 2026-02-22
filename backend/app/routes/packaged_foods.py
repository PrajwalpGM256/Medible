"""
Packaged Foods Routes - Open Food Facts API Integration
Handles search, barcode lookup, and nutrition info for packaged/branded foods
"""

from flask import Blueprint, request, g
from app.services.openfoodfacts_service import (
    search_products,
    get_product_by_barcode,
    get_product_detail,
    parse_ingredients
)
from app.services.auth_service import auth_required
from app.services.interaction_service import check_food_against_medications
from app.errors import (
    api_response,
    BadRequestError,
    ValidationError,
    NotFoundError,
    ExternalAPIError,
    handle_exceptions
)

packaged_foods_bp = Blueprint('packaged_foods', __name__)


@packaged_foods_bp.route('/search', methods=['GET'])
@handle_exceptions
def search_packaged_foods():
    """
    Search packaged/branded foods by name via Open Food Facts

    Query Params:
        q (str): Search query (required)
        limit (int): Max results, default 10, max 50
        page (int): Page number, default 1
    """
    query = request.args.get('q', '').strip()
    if not query:
        raise BadRequestError("Missing required parameter: q", {"field": "q"})
    if len(query) > 200:
        raise ValidationError("Query too long", {"field": "q", "max_length": 200})

    limit = min(max(request.args.get('limit', 10, type=int), 1), 50)
    page = max(request.args.get('page', 1, type=int), 1)

    result = search_products(query, limit, page)

    if not result.get('success'):
        raise ExternalAPIError(
            result.get('error', 'Open Food Facts API error'),
            {"service": "openfoodfacts"}
        )

    return api_response(
        data={
            "query": query,
            "count": result.get('count', 0),
            "total_hits": result.get('total_hits', 0),
            "page": result.get('page', 1),
            "products": result.get('products', [])
        },
        meta={
            "request_id": g.request_id,
            "source": "openfoodfacts",
            "endpoint": "/cgi/search.pl"
        }
    )


@packaged_foods_bp.route('/barcode/<string:barcode>', methods=['GET'])
@handle_exceptions
def lookup_barcode(barcode: str):
    """
    Look up a product by UPC/EAN barcode

    Path Params:
        barcode (str): UPC or EAN barcode
    """
    barcode = barcode.strip()
    if not barcode or not barcode.isdigit():
        raise ValidationError("Invalid barcode format", {"field": "barcode", "value": barcode})

    result = get_product_by_barcode(barcode)

    if not result.get('success'):
        raise ExternalAPIError(
            result.get('error', 'Open Food Facts API error'),
            {"service": "openfoodfacts"}
        )

    product = result.get('product')
    if not product:
        raise NotFoundError(f"Product with barcode {barcode} not found", {"barcode": barcode})

    return api_response(
        data={
            "barcode": barcode,
            "product": product
        },
        meta={
            "request_id": g.request_id,
            "source": "openfoodfacts"
        }
    )


@packaged_foods_bp.route('/<string:off_id>', methods=['GET'])
@handle_exceptions
def get_packaged_food(off_id: str):
    """
    Get detailed product info by Open Food Facts product code

    Path Params:
        off_id (str): Open Food Facts product code
    """
    off_id = off_id.strip()
    if not off_id:
        raise ValidationError("Invalid product ID", {"field": "off_id"})

    result = get_product_detail(off_id)

    if not result.get('success'):
        raise ExternalAPIError(
            result.get('error', 'Open Food Facts API error'),
            {"service": "openfoodfacts"}
        )

    product = result.get('product')
    if not product:
        raise NotFoundError(f"Product {off_id} not found", {"off_id": off_id})

    return api_response(
        data={
            "off_id": off_id,
            "product": product
        },
        meta={
            "request_id": g.request_id,
            "source": "openfoodfacts"
        }
    )


@packaged_foods_bp.route('/<string:off_id>/ingredients', methods=['GET'])
@handle_exceptions
def get_product_ingredients(off_id: str):
    """
    Get parsed ingredient list for a product

    Path Params:
        off_id (str): Open Food Facts product code
    """
    off_id = off_id.strip()
    if not off_id:
        raise ValidationError("Invalid product ID", {"field": "off_id"})

    result = get_product_detail(off_id)

    if not result.get('success'):
        raise ExternalAPIError(
            result.get('error', 'Open Food Facts API error'),
            {"service": "openfoodfacts"}
        )

    product = result.get('product')
    if not product:
        raise NotFoundError(f"Product {off_id} not found", {"off_id": off_id})

    return api_response(
        data={
            "off_id": off_id,
            "product_name": product.get("product_name", ""),
            "ingredients_text": product.get("ingredients_text", ""),
            "ingredients_list": product.get("ingredients_list", []),
            "allergens": product.get("allergens", []),
            "additives": product.get("additives", [])
        },
        meta={
            "request_id": g.request_id,
            "source": "openfoodfacts"
        }
    )


@packaged_foods_bp.route('/check-ingredients', methods=['POST'])
@auth_required
@handle_exceptions
def check_ingredients_interactions():
    """
    Check a product's ingredients against user's medications for interactions

    Request Body:
        {
            "off_id": "5449000000996",  // or provide ingredients_list directly
            "ingredients_list": ["grapefruit juice", "sugar", "water"]
        }
    """
    data = request.get_json()
    if not data:
        raise BadRequestError("Request body must be JSON")

    ingredients_list = data.get('ingredients_list', [])
    off_id = data.get('off_id', '').strip()

    # If off_id provided, fetch ingredients from Open Food Facts
    if off_id and not ingredients_list:
        result = get_product_detail(off_id)
        if result.get('success') and result.get('product'):
            ingredients_list = result['product'].get('ingredients_list', [])

    if not ingredients_list:
        raise BadRequestError("No ingredients provided or found", {"field": "ingredients_list"})

    # Get user's active medication names
    from app.models.medication import UserMedication
    med_names = UserMedication.get_user_medication_names(g.current_user.id, active_only=True)

    if not med_names:
        return api_response(
            data={
                "message": "No active medications to check against",
                "ingredients_checked": len(ingredients_list),
                "medications_checked": 0,
                "warnings": []
            },
            meta={"request_id": g.request_id}
        )

    # Check each ingredient against medications
    all_warnings = []
    for ingredient in ingredients_list:
        result = check_food_against_medications(ingredient, med_names)
        warnings_by_severity = result.get('warnings', {})
        for severity, warnings_list in warnings_by_severity.items():
            for warning in warnings_list:
                warning_entry = {**warning, 'triggering_ingredient': ingredient, 'severity': severity}
                all_warnings.append(warning_entry)

    return api_response(
        data={
            "off_id": off_id or None,
            "ingredients_checked": len(ingredients_list),
            "medications_checked": len(med_names),
            "has_warnings": len(all_warnings) > 0,
            "warning_count": len(all_warnings),
            "warnings": all_warnings
        },
        meta={
            "request_id": g.request_id,
            "source": "medible_interaction_db"
        }
    )
