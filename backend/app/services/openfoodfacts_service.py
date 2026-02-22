"""
Open Food Facts API Service
Handles search, barcode lookup, and product details for packaged/branded foods
Docs: https://wiki.openfoodfacts.org/API
"""

import requests
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://world.openfoodfacts.org"
USER_AGENT = "Medible/1.0 (https://medible.app)"


def _make_request(url: str, params: dict = None, timeout: int = 10) -> dict:
    """Make a request to Open Food Facts API with standard error handling"""
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)

        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 404:
            return {"success": True, "data": None, "message": "Product not found"}
        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Open Food Facts API error: {e}")
        return {"success": False, "error": str(e)}


def search_products(query: str, limit: int = 10, page: int = 1) -> dict:
    """
    Search packaged foods by name
    Returns: list of products with nutrition info
    """
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
        "page": page,
        "fields": "code,product_name,brands,image_front_small_url,nutriscore_grade,"
                  "nutriments,categories_tags,ingredients_text,allergens_tags,"
                  "nova_group,quantity"
    }

    result = _make_request(url, params)

    if not result.get("success"):
        return result

    data = result.get("data", {})
    products_raw = data.get("products", [])

    products = []
    for item in products_raw:
        product = _parse_product(item)
        if product.get("product_name"):
            products.append(product)

    return {
        "success": True,
        "count": len(products),
        "total_hits": data.get("count", 0),
        "page": data.get("page", 1),
        "products": products
    }


def get_product_by_barcode(barcode: str) -> dict:
    """
    Look up a product by UPC/EAN barcode
    Returns: product details with full nutrition and ingredients
    """
    url = f"{BASE_URL}/api/v2/product/{barcode}"
    params = {
        "fields": "code,product_name,brands,image_front_url,image_front_small_url,"
                  "nutriscore_grade,nutriments,categories_tags,ingredients_text,"
                  "ingredients_text_en,ingredients,allergens_tags,traces_tags,"
                  "nova_group,quantity,serving_size,additives_tags"
    }

    result = _make_request(url, params)

    if not result.get("success"):
        return result

    data = result.get("data", {})
    product_data = data.get("product")

    if not product_data:
        return {"success": True, "product": None, "message": "Product not found"}

    return {
        "success": True,
        "product": _parse_product_detail(product_data)
    }


def get_product_detail(off_id: str) -> dict:
    """
    Get detailed product info by Open Food Facts product code
    Returns: full nutrition, ingredients, allergens, additives
    """
    return get_product_by_barcode(off_id)


def parse_ingredients(product_data: dict) -> list:
    """
    Extract and normalize ingredient list from a product
    Returns: list of ingredient names (lowercase, trimmed)
    """
    ingredients_text = product_data.get("ingredients_text_en") or product_data.get("ingredients_text", "")

    if not ingredients_text:
        # Try structured ingredients
        structured = product_data.get("ingredients", [])
        if structured:
            return [
                ing.get("text", "").lower().strip()
                for ing in structured
                if ing.get("text")
            ]
        return []

    # Parse comma-separated ingredient list
    # Remove parenthetical info and clean up
    import re
    cleaned = re.sub(r'\([^)]*\)', '', ingredients_text)
    cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)

    ingredients = []
    for item in cleaned.split(','):
        item = item.strip().lower()
        # Remove percentage info
        item = re.sub(r'\d+\.?\d*\s*%', '', item).strip()
        if item and len(item) > 1:
            ingredients.append(item)

    return ingredients


def _parse_product(item: dict) -> dict:
    """Parse a product from search results into a clean format"""
    nutriments = item.get("nutriments", {})

    return {
        "off_id": item.get("code", ""),
        "product_name": item.get("product_name", ""),
        "brands": item.get("brands", ""),
        "image_url": item.get("image_front_small_url", ""),
        "nutriscore_grade": item.get("nutriscore_grade"),
        "nova_group": item.get("nova_group"),
        "quantity": item.get("quantity", ""),
        "nutrition": {
            "calories": nutriments.get("energy-kcal_100g"),
            "fat_g": nutriments.get("fat_100g"),
            "saturated_fat_g": nutriments.get("saturated-fat_100g"),
            "carbs_g": nutriments.get("carbohydrates_100g"),
            "sugars_g": nutriments.get("sugars_100g"),
            "fiber_g": nutriments.get("fiber_100g"),
            "protein_g": nutriments.get("proteins_100g"),
            "sodium_mg": nutriments.get("sodium_100g", 0) * 1000 if nutriments.get("sodium_100g") else None,
            "salt_g": nutriments.get("salt_100g"),
        }
    }


def _parse_product_detail(item: dict) -> dict:
    """Parse a product with full detail including ingredients and allergens"""
    base = _parse_product(item)

    # Add detailed fields
    base["image_url_full"] = item.get("image_front_url", "")
    base["serving_size"] = item.get("serving_size", "")
    base["ingredients_text"] = item.get("ingredients_text_en") or item.get("ingredients_text", "")
    base["ingredients_list"] = parse_ingredients(item)
    base["allergens"] = [
        tag.replace("en:", "").replace("-", " ").title()
        for tag in item.get("allergens_tags", [])
    ]
    base["traces"] = [
        tag.replace("en:", "").replace("-", " ").title()
        for tag in item.get("traces_tags", [])
    ]
    base["additives"] = [
        tag.replace("en:", "").upper()
        for tag in item.get("additives_tags", [])
    ]
    base["categories"] = [
        tag.replace("en:", "").replace("-", " ").title()
        for tag in item.get("categories_tags", [])[:5]
    ]

    return base
