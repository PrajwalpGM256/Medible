"""
Tests for Food Diary Endpoints
Covers: get logs, today, add, delete, update, summary, weekly, streaks, export
"""

import pytest
from datetime import date


class TestGetFoodLogs:
    def test_get_today_logs(self, client, auth_headers, sample_food_log):
        resp = client.get('/api/v1/food-diary/today', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['date'] == date.today().isoformat()

    def test_get_logs_by_date(self, client, auth_headers, sample_food_log):
        today = date.today().isoformat()
        resp = client.get(f'/api/v1/food-diary?date={today}', headers=auth_headers)
        assert resp.status_code == 200

    def test_get_logs_range(self, client, auth_headers):
        resp = client.get('/api/v1/food-diary?days=7', headers=auth_headers)
        assert resp.status_code == 200

    def test_get_logs_no_auth(self, client):
        resp = client.get('/api/v1/food-diary/today')
        assert resp.status_code == 401


class TestAddFoodLog:
    def test_add_food_log(self, client, auth_headers):
        resp = client.post('/api/v1/food-diary', headers=auth_headers, json={
            'food_name': 'Oatmeal', 'calories': 150, 'meal_type': 'breakfast'
        })
        assert resp.status_code == 201
        assert resp.get_json()['data']['food_log']['food_name'] == 'Oatmeal'

    def test_add_food_log_missing_name(self, client, auth_headers):
        resp = client.post('/api/v1/food-diary', headers=auth_headers, json={
            'calories': 150
        })
        assert resp.status_code == 400


class TestUpdateDeleteFoodLog:
    def test_update_food_log(self, client, auth_headers, sample_food_log):
        resp = client.patch(f'/api/v1/food-diary/{sample_food_log.id}',
                            headers=auth_headers, json={'calories': 200})
        assert resp.status_code == 200

    def test_delete_food_log(self, client, auth_headers, sample_food_log):
        resp = client.delete(f'/api/v1/food-diary/{sample_food_log.id}',
                             headers=auth_headers)
        assert resp.status_code == 200


class TestSummary:
    def test_summary(self, client, auth_headers):
        resp = client.get('/api/v1/food-diary/summary?days=7', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'daily_summaries' in data
        assert 'averages' in data


class TestWeekly:
    def test_weekly(self, client, auth_headers):
        resp = client.get('/api/v1/food-diary/weekly', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'daily' in data
        assert len(data['daily']) == 7


class TestStreaks:
    def test_streaks(self, client, auth_headers):
        resp = client.get('/api/v1/food-diary/streaks', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'current_streak' in data
        assert 'total_days_logged' in data

    def test_streaks_with_log(self, client, auth_headers, sample_food_log):
        resp = client.get('/api/v1/food-diary/streaks', headers=auth_headers)
        data = resp.get_json()['data']
        assert data['current_streak'] >= 1
        assert data['today_logged'] is True


class TestExport:
    def test_export(self, client, auth_headers):
        resp = client.get('/api/v1/food-diary/export', headers=auth_headers)
        assert resp.status_code == 200
        assert 'export' in resp.get_json()['data']

    def test_export_custom_days(self, client, auth_headers):
        resp = client.get('/api/v1/food-diary/export?days=14', headers=auth_headers)
        assert resp.status_code == 200
