"""
Tests for Dashboard, Search History, and Admin Endpoints
"""

import pytest


# ─── Dashboard ────────────────────────────────────────────

class TestDashboardSummary:
    def test_summary(self, client, auth_headers):
        resp = client.get('/api/v1/dashboard/summary', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'medications' in data
        assert 'nutrition_today' in data
        assert 'food_diary_streak' in data

    def test_summary_no_auth(self, client):
        resp = client.get('/api/v1/dashboard/summary')
        assert resp.status_code == 401


class TestDashboardAlerts:
    def test_alerts(self, client, auth_headers):
        resp = client.get('/api/v1/dashboard/alerts', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'alert_count' in data
        assert 'alerts' in data

    def test_alerts_no_auth(self, client):
        resp = client.get('/api/v1/dashboard/alerts')
        assert resp.status_code == 401


# ─── Search History ───────────────────────────────────────

class TestSearchHistory:
    def test_get_search_history(self, client, auth_headers):
        resp = client.get('/api/v1/search-history', headers=auth_headers)
        assert resp.status_code == 200
        assert 'history' in resp.get_json()['data']

    def test_clear_search_history(self, client, auth_headers):
        resp = client.delete('/api/v1/search-history', headers=auth_headers)
        assert resp.status_code == 200
        assert 'deleted_count' in resp.get_json()['data']

    def test_search_history_no_auth(self, client):
        resp = client.get('/api/v1/search-history')
        assert resp.status_code == 401


# ─── Admin ────────────────────────────────────────────────

class TestAdminUsers:
    def test_list_users_admin(self, client, admin_headers):
        resp = client.get('/api/v1/admin/users', headers=admin_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'users' in data
        assert 'pagination' in data

    def test_list_users_non_admin(self, client, auth_headers):
        resp = client.get('/api/v1/admin/users', headers=auth_headers)
        assert resp.status_code == 403

    def test_list_users_no_auth(self, client):
        resp = client.get('/api/v1/admin/users')
        assert resp.status_code == 401


class TestAdminManageUser:
    def test_manage_user(self, client, admin_headers, test_user):
        resp = client.patch(f'/api/v1/admin/users/{test_user.id}',
                            headers=admin_headers, json={'is_active': False})
        assert resp.status_code == 200

    def test_manage_self_blocked(self, client, admin_headers, admin_user):
        resp = client.patch(f'/api/v1/admin/users/{admin_user.id}',
                            headers=admin_headers, json={'is_admin': False})
        assert resp.status_code == 400

    def test_manage_nonexistent(self, client, admin_headers):
        resp = client.patch('/api/v1/admin/users/9999',
                            headers=admin_headers, json={'is_active': True})
        assert resp.status_code == 404


class TestAdminStats:
    def test_stats(self, client, admin_headers):
        resp = client.get('/api/v1/admin/stats', headers=admin_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert 'users' in data
        assert 'content' in data

    def test_stats_non_admin(self, client, auth_headers):
        resp = client.get('/api/v1/admin/stats', headers=auth_headers)
        assert resp.status_code == 403
