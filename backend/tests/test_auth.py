"""
Tests for Auth Endpoints
Covers: register, login, refresh, profile, update, password change,
        logout, delete account, forgot/reset password, export
"""

import pytest


class TestRegister:
    def test_register_success(self, client):
        resp = client.post('/api/v1/auth/register', json={
            'email': 'new@example.com',
            'password': 'NewPass1!'
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['data']['user']['email'] == 'new@example.com'
        assert 'access_token' in data['data']['tokens']

    def test_register_duplicate_email(self, client, test_user):
        resp = client.post('/api/v1/auth/register', json={
            'email': 'test@example.com',
            'password': 'NewPass1!'
        })
        assert resp.status_code == 422

    def test_register_weak_password(self, client):
        resp = client.post('/api/v1/auth/register', json={
            'email': 'new2@example.com',
            'password': 'short'
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        resp = client.post('/api/v1/auth/register', json={
            'email': 'notanemail',
            'password': 'ValidPass1'
        })
        assert resp.status_code == 422

    def test_register_missing_body(self, client):
        resp = client.post('/api/v1/auth/register',
                           json={})
        assert resp.status_code in (400, 422)


class TestLogin:
    def test_login_success(self, client, test_user):
        resp = client.post('/api/v1/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass1'
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'access_token' in data['data']['tokens']
        assert data['data']['user']['email'] == 'test@example.com'

    def test_login_wrong_password(self, client, test_user):
        resp = client.post('/api/v1/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPass1'
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post('/api/v1/auth/login', json={
            'email': 'nobody@example.com',
            'password': 'TestPass1'
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post('/api/v1/auth/login', json={'email': 'test@example.com'})
        assert resp.status_code == 400


class TestProfile:
    def test_get_profile(self, client, auth_headers):
        resp = client.get('/api/v1/auth/me', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['user']['email'] == 'test@example.com'

    def test_get_profile_no_auth(self, client):
        resp = client.get('/api/v1/auth/me')
        assert resp.status_code == 401

    def test_update_profile_name(self, client, auth_headers):
        resp = client.patch('/api/v1/auth/me', headers=auth_headers, json={
            'first_name': 'Updated',
            'last_name': 'Name'
        })
        assert resp.status_code == 200
        assert resp.get_json()['data']['user']['first_name'] == 'Updated'

    def test_update_profile_email(self, client, auth_headers):
        resp = client.patch('/api/v1/auth/me', headers=auth_headers, json={
            'email': 'updated@example.com'
        })
        assert resp.status_code == 200
        assert resp.get_json()['data']['user']['email'] == 'updated@example.com'


class TestPasswordChange:
    def test_change_password_success(self, client, auth_headers):
        resp = client.put('/api/v1/auth/me/password', headers=auth_headers, json={
            'current_password': 'TestPass1',
            'new_password': 'NewPass1!'
        })
        assert resp.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        resp = client.put('/api/v1/auth/me/password', headers=auth_headers, json={
            'current_password': 'WrongPass1',
            'new_password': 'NewPass1!'
        })
        assert resp.status_code == 401


class TestLogout:
    def test_logout_success(self, client, auth_headers):
        resp = client.post('/api/v1/auth/logout', headers=auth_headers)
        assert resp.status_code == 200
        assert 'logged out' in resp.get_json()['data']['message'].lower()


class TestDeleteAccount:
    def test_delete_account_success(self, client, auth_headers):
        resp = client.delete('/api/v1/auth/me', headers=auth_headers, json={
            'password': 'TestPass1'
        })
        assert resp.status_code == 200

    def test_delete_account_wrong_password(self, client, auth_headers):
        resp = client.delete('/api/v1/auth/me', headers=auth_headers, json={
            'password': 'WrongPassword1'
        })
        assert resp.status_code == 401


class TestPasswordReset:
    def test_forgot_password(self, client, test_user):
        resp = client.post('/api/v1/auth/forgot-password', json={
            'email': 'test@example.com'
        })
        assert resp.status_code == 200

    def test_forgot_password_nonexistent(self, client):
        """Should still return 200 to not leak email existence"""
        resp = client.post('/api/v1/auth/forgot-password', json={
            'email': 'nobody@example.com'
        })
        assert resp.status_code == 200

    def test_reset_password_invalid_token(self, client):
        resp = client.post('/api/v1/auth/reset-password', json={
            'token': 'invalid-token',
            'new_password': 'NewPass1!'
        })
        assert resp.status_code == 401


class TestExportUserData:
    def test_export_data(self, client, auth_headers):
        resp = client.get('/api/v1/auth/me/export', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']['export']
        assert 'user' in data
        assert 'medications' in data
        assert 'food_logs' in data

    def test_export_data_no_auth(self, client):
        resp = client.get('/api/v1/auth/me/export')
        assert resp.status_code == 401
