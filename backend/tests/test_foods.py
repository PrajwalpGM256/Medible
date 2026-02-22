"""
Tests for Food Endpoints (USDA + Favorites + Unified Search)
"""

import pytest
from unittest.mock import patch


MOCK_USDA_SEARCH = {
    "success": True, "count": 1, "total_hits": 100,
    "foods": [{"fdc_id": 12345, "description": "Banana, raw", "data_type": "Foundation",
               "nutrients": {"calories": 89}}]
}


class TestFoodSearch:
    @patch('app.routes.foods.search_food', return_value=MOCK_USDA_SEARCH)
    def test_search_foods(self, mock_search, client):
        resp = client.get('/api/v1/foods/search?q=banana')
        assert resp.status_code == 200
        assert resp.get_json()['data']['count'] == 1

    def test_search_foods_missing_query(self, client):
        resp = client.get('/api/v1/foods/search')
        assert resp.status_code == 400

    def test_search_foods_query_too_long(self, client):
        resp = client.get(f'/api/v1/foods/search?q={"x" * 201}')
        assert resp.status_code == 422


class TestFavorites:
    def test_add_favorite(self, client, auth_headers):
        resp = client.post('/api/v1/foods/favorites', headers=auth_headers, json={
            'food_name': 'Banana', 'source': 'usda', 'fdc_id': 12345
        })
        assert resp.status_code == 201
        assert resp.get_json()['data']['favorite']['food_name'] == 'Banana'

    def test_get_favorites(self, client, auth_headers):
        # Add a favorite first
        client.post('/api/v1/foods/favorites', headers=auth_headers, json={
            'food_name': 'Banana', 'source': 'usda'
        })
        resp = client.get('/api/v1/foods/favorites', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['count'] >= 1

    def test_delete_favorite(self, client, auth_headers):
        # Add, then delete
        add_resp = client.post('/api/v1/foods/favorites', headers=auth_headers, json={
            'food_name': 'Apple', 'source': 'usda'
        })
        fav_id = add_resp.get_json()['data']['favorite']['id']
        resp = client.delete(f'/api/v1/foods/favorites/{fav_id}', headers=auth_headers)
        assert resp.status_code == 200

    def test_add_favorite_no_auth(self, client):
        resp = client.post('/api/v1/foods/favorites', json={'food_name': 'Banana'})
        assert resp.status_code == 401

    def test_add_favorite_missing_name(self, client, auth_headers):
        resp = client.post('/api/v1/foods/favorites', headers=auth_headers, json={
            'source': 'usda'
        })
        assert resp.status_code == 400


class TestRecentFoods:
    def test_recent_foods(self, client, auth_headers):
        resp = client.get('/api/v1/foods/recent', headers=auth_headers)
        assert resp.status_code == 200
        assert 'recent_foods' in resp.get_json()['data']


class TestUnifiedSearch:
    @patch('app.routes.foods.search_food', return_value=MOCK_USDA_SEARCH)
    @patch('app.services.openfoodfacts_service.search_products',
           return_value={"success": True, "count": 1, "products": [{"product_name": "Banana Chips"}]})
    def test_unified_search(self, mock_off, mock_usda, client):
        resp = client.get('/api/v1/foods/unified-search?q=banana')
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'usda' in data
        assert 'openfoodfacts' in data

    def test_unified_search_missing_query(self, client):
        resp = client.get('/api/v1/foods/unified-search')
        assert resp.status_code == 400
