"""
Tests for Interactions & Interaction History Endpoints
Covers: check, check-multiple, drug/food lookups, stats,
        batch-check, report, history CRUD, history stats
"""

import pytest
from unittest.mock import patch


class TestCheckInteraction:
    def test_check_interaction(self, client):
        resp = client.get('/api/v1/interactions/check?food=grapefruit&drug=lipitor')
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'has_interaction' in data
        assert 'food_queried' in data

    def test_check_interaction_missing_food(self, client):
        resp = client.get('/api/v1/interactions/check?drug=lipitor')
        assert resp.status_code == 400

    def test_check_interaction_missing_drug(self, client):
        resp = client.get('/api/v1/interactions/check?food=grapefruit')
        assert resp.status_code == 400

    def test_check_interaction_with_synonym(self, client):
        # "grape juice" should map to "grapefruit" and trigger the interaction with "lipitor"
        resp = client.get('/api/v1/interactions/check?food=grape%20juice&drug=lipitor')
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert data['has_interaction'] is True
        # Check that it matched grapefruit
        assert any(i['food_matched'] == 'Grapefruit' for i in data['interactions'])

    @patch('app.services.openfda_service.get_drug_detail')
    def test_check_interaction_openfda_allergy(self, mock_fda, client):
        # Mock OpenFDA response indicating peanut is an inactive ingredient
        mock_fda.return_value = {
            "success": True,
            "drug": {
                "brand_name": "TestDrug",
                "inactive_ingredient": ["peanut oil", "water"]
            }
        }
        resp = client.get('/api/v1/interactions/check?food=peanut&drug=TestDrug')
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert data['has_interaction'] is True
        # Check that the FDA allergy interaction was created
        interactions = data['interactions']
        assert any("FDA-ALG" in i['id'] for i in interactions)
        assert any(i['severity'] == 'high' for i in interactions)

    @patch('app.services.openfda_service.get_drug_detail')
    def test_check_interaction_openfda_text_warning(self, mock_fda, client):
        # Mock OpenFDA response with warning text matching food
        mock_fda.return_value = {
            "success": True,
            "drug": {
                "brand_name": "TestDrug",
                "warnings": ["Do not take with st johns wort."]
            }
        }
        resp = client.get('/api/v1/interactions/check?food=st%20johns%20wort&drug=TestDrug')
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert data['has_interaction'] is True
        interactions = data['interactions']
        assert any("FDA-TXT" in i['id'] for i in interactions)
        assert any(i['severity'] == 'medium' for i in interactions)


class TestCheckMultiple:
    def test_check_multiple(self, client):
        resp = client.post('/api/v1/interactions/check-multiple', json={
            'food': 'grapefruit',
            'medications': ['lipitor', 'metformin']
        })
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'food_checked' in data

    def test_check_multiple_empty_meds(self, client):
        resp = client.post('/api/v1/interactions/check-multiple', json={
            'food': 'grapefruit', 'medications': []
        })
        assert resp.status_code == 422

    def test_check_multiple_too_many(self, client):
        resp = client.post('/api/v1/interactions/check-multiple', json={
            'food': 'grapefruit', 'medications': ['drug'] * 21
        })
        assert resp.status_code == 422


class TestDrugFoodLookups:
    def test_interactions_for_drug(self, client):
        resp = client.get('/api/v1/interactions/drug/lipitor')
        assert resp.status_code == 200
        assert 'foods_to_avoid' in resp.get_json()['data']

    def test_interactions_for_food(self, client):
        resp = client.get('/api/v1/interactions/food/grapefruit')
        assert resp.status_code == 200
        assert 'drugs_affected' in resp.get_json()['data']


class TestInteractionStats:
    def test_stats(self, client):
        resp = client.get('/api/v1/interactions/stats')
        assert resp.status_code == 200
        assert 'total_interactions' in resp.get_json()['data']


class TestBatchCheck:
    def test_batch_check(self, client, auth_headers, sample_food_log, sample_medication):
        resp = client.post('/api/v1/interactions/batch-check', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'foods_checked' in data
        assert 'medications_checked' in data


class TestReportInteraction:
    def test_report(self, client, auth_headers):
        resp = client.post('/api/v1/interactions/report', headers=auth_headers, json={
            'food_name': 'Pomelo',
            'drug_name': 'Lipitor',
            'description': 'Similar to grapefruit',
            'severity_suggestion': 'high'
        })
        assert resp.status_code == 201
        assert resp.get_json()['data']['report']['food_name'] == 'Pomelo'

    def test_report_missing_food(self, client, auth_headers):
        resp = client.post('/api/v1/interactions/report', headers=auth_headers, json={
            'drug_name': 'Lipitor'
        })
        assert resp.status_code == 400

    def test_report_invalid_severity(self, client, auth_headers):
        resp = client.post('/api/v1/interactions/report', headers=auth_headers, json={
            'food_name': 'Test', 'drug_name': 'Test', 'severity_suggestion': 'extreme'
        })
        assert resp.status_code == 422


class TestInteractionHistory:
    def test_get_history(self, client, auth_headers):
        resp = client.get('/api/v1/interaction-history', headers=auth_headers)
        assert resp.status_code == 200
        assert 'history' in resp.get_json()['data']

    def test_save_check(self, client, auth_headers):
        resp = client.post('/api/v1/interaction-history', headers=auth_headers, json={
            'food_name': 'Grapefruit',
            'medications': ['Lipitor'],
            'interactions': [{'drugName': 'Lipitor', 'severity': 'high'}]
        })
        assert resp.status_code == 201

    def test_delete_check(self, client, auth_headers):
        # Save then delete
        save = client.post('/api/v1/interaction-history', headers=auth_headers, json={
            'food_name': 'Test', 'medications': ['Test'],
            'interactions': []
        })
        cid = save.get_json()['data']['check']['id']
        resp = client.delete(f'/api/v1/interaction-history/{cid}', headers=auth_headers)
        assert resp.status_code == 200

    def test_clear_history(self, client, auth_headers):
        resp = client.delete('/api/v1/interaction-history', headers=auth_headers)
        assert resp.status_code == 200

    def test_history_stats(self, client, auth_headers):
        resp = client.get('/api/v1/interaction-history/stats', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'total_checks' in data
        assert 'severity_distribution' in data

    def test_history_no_auth(self, client):
        resp = client.get('/api/v1/interaction-history')
        assert resp.status_code == 401
