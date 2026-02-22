"""
Test configuration and fixtures
Shared fixtures for all test modules
"""

import pytest
import json
from app import create_app, db as _db
from app.models.user import User
from app.models.medication import UserMedication, FoodLog, InteractionCheck, SearchHistory
from app.models.token_blacklist import TokenBlacklist
from app.models.favorites import FavoriteFood, MedicationReminder, InteractionReport


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # In-memory DB
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key-for-pytest'

    with app.app_context():
        _db.create_all()

    yield app

    with app.app_context():
        _db.drop_all()


@pytest.fixture(autouse=True)
def db_session(app):
    """Create a fresh database for each test"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture
def test_user(db_session):
    """Create a standard test user"""
    user = User(
        email='test@example.com',
        password='TestPass1',
        first_name='Test',
        last_name='User'
    )
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin test user"""
    user = User(
        email='admin@example.com',
        password='AdminPass1',
        first_name='Admin',
        last_name='User'
    )
    _db.session.add(user)
    _db.session.flush()
    user.is_admin = True
    _db.session.commit()
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers with a valid token for test_user"""
    resp = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'TestPass1'
    })
    data = resp.get_json()
    token = data['data']['tokens']['access_token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


@pytest.fixture
def admin_headers(client, admin_user):
    """Get auth headers with a valid token for admin_user"""
    resp = client.post('/api/v1/auth/login', json={
        'email': 'admin@example.com',
        'password': 'AdminPass1'
    })
    data = resp.get_json()
    token = data['data']['tokens']['access_token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


@pytest.fixture
def sample_medication(test_user, db_session):
    """Create a sample medication for the test user"""
    med = UserMedication(
        user_id=test_user.id,
        drug_name='Lipitor',
        brand_name='Lipitor',
        generic_name='atorvastatin',
        dosage='20mg',
        frequency='once daily',
        is_active=True
    )
    _db.session.add(med)
    _db.session.commit()
    return med


@pytest.fixture
def sample_food_log(test_user, db_session):
    """Create a sample food log entry"""
    from datetime import date
    log = FoodLog(
        user_id=test_user.id,
        food_name='Banana',
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.4,
        meal_type='snack',
        logged_date=date.today()
    )
    _db.session.add(log)
    _db.session.commit()
    return log
