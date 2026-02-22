"""
Tests for Medication Endpoints
Covers: CRUD, food-check, interactions-summary, reminders, bulk import, export
"""

import pytest


class TestListMedications:
    def test_list_medications(self, client, auth_headers, sample_medication):
        resp = client.get('/api/v1/medications', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['count'] >= 1

    def test_list_active_only(self, client, auth_headers, sample_medication):
        resp = client.get('/api/v1/medications?active_only=true', headers=auth_headers)
        assert resp.status_code == 200

    def test_list_no_auth(self, client):
        resp = client.get('/api/v1/medications')
        assert resp.status_code == 401


class TestAddMedication:
    def test_add_medication(self, client, auth_headers):
        resp = client.post('/api/v1/medications', headers=auth_headers, json={
            'drug_name': 'Metformin', 'dosage': '500mg', 'frequency': 'twice daily'
        })
        assert resp.status_code == 201
        assert resp.get_json()['data']['medication']['drug_name'] == 'Metformin'

    def test_add_duplicate(self, client, auth_headers, sample_medication):
        resp = client.post('/api/v1/medications', headers=auth_headers, json={
            'drug_name': 'Lipitor'
        })
        assert resp.status_code == 422

    def test_add_missing_name(self, client, auth_headers):
        resp = client.post('/api/v1/medications', headers=auth_headers, json={
            'dosage': '20mg'
        })
        assert resp.status_code == 422


class TestUpdateMedication:
    def test_update_medication(self, client, auth_headers, sample_medication):
        resp = client.patch(f'/api/v1/medications/{sample_medication.id}',
                            headers=auth_headers, json={'dosage': '40mg'})
        assert resp.status_code == 200
        assert resp.get_json()['data']['medication']['dosage'] == '40mg'

    def test_update_nonexistent(self, client, auth_headers):
        resp = client.patch('/api/v1/medications/9999', headers=auth_headers,
                            json={'dosage': '40mg'})
        assert resp.status_code == 404


class TestDeleteMedication:
    def test_delete_medication(self, client, auth_headers, sample_medication):
        resp = client.delete(f'/api/v1/medications/{sample_medication.id}',
                             headers=auth_headers)
        assert resp.status_code == 204

    def test_delete_nonexistent(self, client, auth_headers):
        resp = client.delete('/api/v1/medications/9999', headers=auth_headers)
        assert resp.status_code == 404


class TestReminders:
    def test_get_reminders(self, client, auth_headers):
        resp = client.get('/api/v1/medications/reminders', headers=auth_headers)
        assert resp.status_code == 200
        assert 'reminders' in resp.get_json()['data']

    def test_create_reminder(self, client, auth_headers, sample_medication):
        resp = client.post('/api/v1/medications/reminders', headers=auth_headers, json={
            'medication_id': sample_medication.id,
            'reminder_time': '08:00',
            'days_of_week': ['mon', 'wed', 'fri']
        })
        assert resp.status_code == 201

    def test_create_reminder_bad_time(self, client, auth_headers, sample_medication):
        resp = client.post('/api/v1/medications/reminders', headers=auth_headers, json={
            'medication_id': sample_medication.id,
            'reminder_time': 'not-a-time'
        })
        assert resp.status_code == 422

    def test_delete_reminder(self, client, auth_headers, sample_medication):
        # Create then delete
        create = client.post('/api/v1/medications/reminders', headers=auth_headers, json={
            'medication_id': sample_medication.id,
            'reminder_time': '09:00'
        })
        rid = create.get_json()['data']['reminder']['id']
        resp = client.delete(f'/api/v1/medications/reminders/{rid}', headers=auth_headers)
        assert resp.status_code == 200


class TestBulkImport:
    def test_bulk_import(self, client, auth_headers):
        resp = client.post('/api/v1/medications/import', headers=auth_headers, json={
            'medications': [
                {'drug_name': 'Aspirin', 'dosage': '81mg'},
                {'drug_name': 'Ibuprofen', 'dosage': '200mg'}
            ]
        })
        assert resp.status_code == 201
        data = resp.get_json()['data']
        assert data['imported_count'] == 2

    def test_bulk_import_skip_duplicates(self, client, auth_headers, sample_medication):
        resp = client.post('/api/v1/medications/import', headers=auth_headers, json={
            'medications': [
                {'drug_name': 'Lipitor'},
                {'drug_name': 'Aspirin'}
            ]
        })
        data = resp.get_json()['data']
        assert data['imported_count'] == 1
        assert data['skipped_count'] == 1

    def test_bulk_import_empty(self, client, auth_headers):
        resp = client.post('/api/v1/medications/import', headers=auth_headers, json={
            'medications': []
        })
        assert resp.status_code == 422


class TestExportMedications:
    def test_export(self, client, auth_headers, sample_medication):
        resp = client.get('/api/v1/medications/export', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['export']['total'] >= 1
