"""
Tests for Drug Endpoints
Covers: search, adverse events, recalls, detail, drug-drug interactions, side effects
"""

import pytest
from unittest.mock import patch


MOCK_SEARCH_RESULT = {
    "success": True, "count": 1,
    "drugs": [{"brand_name": "Aspirin", "generic_name": "aspirin", "manufacturer": "Bayer",
               "purpose": "Pain relief", "warnings": "None", "dosage": "See label",
               "active_ingredient": "aspirin"}]
}

MOCK_DETAIL = {
    "success": True,
    "drug": {"brand_name": "Aspirin", "generic_name": "aspirin", "manufacturer": "Bayer",
             "warnings": "None", "drug_interactions": "None listed",
             "adverse_reactions": "Stomach bleeding"}
}


class TestDrugSearch:
    @patch('app.routes.drugs.search_drug', return_value=MOCK_SEARCH_RESULT)
    def test_search_drugs(self, mock_search, client):
        resp = client.get('/api/v1/drugs/search?q=aspirin')
        assert resp.status_code == 200
        assert resp.get_json()['data']['count'] == 1

    def test_search_drugs_missing_query(self, client):
        resp = client.get('/api/v1/drugs/search')
        assert resp.status_code == 400


class TestDrugDetail:
    @patch('app.services.openfda_service.get_drug_detail', return_value=MOCK_DETAIL)
    def test_get_drug_detail(self, mock_detail, client):
        resp = client.get('/api/v1/drugs/aspirin')
        assert resp.status_code == 200

    @patch('app.services.openfda_service.get_drug_detail',
           return_value={"success": True, "drug": None, "message": "Drug not found"})
    def test_get_drug_detail_not_found(self, mock_detail, client):
        resp = client.get('/api/v1/drugs/nonexistent_drug_xyz')
        assert resp.status_code == 404


class TestDrugInteractions:
    @patch('app.services.openfda_service.get_drug_drug_interactions',
           return_value={"success": True, "drug": "Aspirin", "generic_name": "aspirin",
                         "interactions_text": "May interact with blood thinners"})
    def test_drug_drug_interactions(self, mock_inter, client):
        resp = client.get('/api/v1/drugs/interactions/aspirin')
        assert resp.status_code == 200
        assert 'interactions_text' in resp.get_json()['data']


class TestSideEffects:
    @patch('app.services.openfda_service.get_side_effects',
           return_value={"success": True, "drug": "Aspirin", "generic_name": "aspirin",
                         "adverse_reactions": "Stomach bleeding", "warnings": "None",
                         "warnings_and_cautions": "None"})
    def test_side_effects(self, mock_se, client):
        resp = client.get('/api/v1/drugs/side-effects?drug=aspirin')
        assert resp.status_code == 200
        assert 'adverse_reactions' in resp.get_json()['data']

    def test_side_effects_missing_drug(self, client):
        resp = client.get('/api/v1/drugs/side-effects')
        assert resp.status_code == 400
