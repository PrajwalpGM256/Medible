"""
Tests for Packaged Foods Endpoints (Open Food Facts)
"""

import pytest
from unittest.mock import patch


MOCK_OFF_SEARCH = {
    "success": True, "count": 1, "total_hits": 50, "page": 1,
    "products": [{"off_id": "123", "product_name": "Coca-Cola", "brands": "Coca-Cola"}]
}

MOCK_OFF_PRODUCT = {
    "success": True,
    "product": {
        "off_id": "5449000000996", "product_name": "Coca-Cola",
        "brands": "Coca-Cola", "ingredients_text": "Water, sugar, caramel color",
        "ingredients_list": ["water", "sugar", "caramel color"],
        "allergens": [], "additives": ["E150D"], "nutrition": {"calories": 42}
    }
}


class TestPackagedFoodSearch:
    @patch('app.routes.packaged_foods.search_products', return_value=MOCK_OFF_SEARCH)
    def test_search(self, mock_search, client):
        resp = client.get('/api/v1/foods/packaged/search?q=coca+cola')
        assert resp.status_code == 200
        assert resp.get_json()['data']['count'] == 1

    def test_search_missing_query(self, client):
        resp = client.get('/api/v1/foods/packaged/search')
        assert resp.status_code == 400


class TestBarcodeLookup:
    @patch('app.routes.packaged_foods.get_product_by_barcode', return_value=MOCK_OFF_PRODUCT)
    def test_barcode_lookup(self, mock_barcode, client):
        resp = client.get('/api/v1/foods/packaged/barcode/5449000000996')
        assert resp.status_code == 200
        assert resp.get_json()['data']['product']['product_name'] == 'Coca-Cola'

    def test_barcode_invalid(self, client):
        resp = client.get('/api/v1/foods/packaged/barcode/abc')
        assert resp.status_code == 422


class TestProductDetail:
    @patch('app.routes.packaged_foods.get_product_detail', return_value=MOCK_OFF_PRODUCT)
    def test_product_detail(self, mock_detail, client):
        resp = client.get('/api/v1/foods/packaged/5449000000996')
        assert resp.status_code == 200

    @patch('app.routes.packaged_foods.get_product_detail',
           return_value={"success": True, "product": None, "message": "Not found"})
    def test_product_not_found(self, mock_detail, client):
        resp = client.get('/api/v1/foods/packaged/0000000000000')
        assert resp.status_code == 404


class TestIngredients:
    @patch('app.routes.packaged_foods.get_product_detail', return_value=MOCK_OFF_PRODUCT)
    def test_get_ingredients(self, mock_detail, client):
        resp = client.get('/api/v1/foods/packaged/5449000000996/ingredients')
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'ingredients_list' in data


class TestCheckIngredients:
    @patch('app.routes.packaged_foods.get_product_detail', return_value=MOCK_OFF_PRODUCT)
    def test_check_ingredients(self, mock_detail, client, auth_headers, sample_medication):
        resp = client.post('/api/v1/foods/packaged/check-ingredients',
                           headers=auth_headers,
                           json={'off_id': '5449000000996'})
        assert resp.status_code == 200
        assert 'ingredients_checked' in resp.get_json()['data']

    def test_check_ingredients_no_auth(self, client):
        resp = client.post('/api/v1/foods/packaged/check-ingredients',
                           json={'off_id': '123'})
        assert resp.status_code == 401
