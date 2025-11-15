"""
Campus Resource Hub - Pytest Configuration
==========================================
This file contains pytest fixtures used across all tests.

Fixtures provide:
- Test database setup/teardown
- Test client for HTTP requests
- Mock data for testing
- Authentication helpers
"""

import pytest
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import create_app
from src.data_access.base_dal import BaseDAL
from config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """
    Create Flask application instance for testing.

    Scope: session (created once per test session)
    """
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def client(app):
    """
    Create test client for making HTTP requests.

    Scope: function (new client per test)

    Usage:
        def test_homepage(client):
            response = client.get('/')
            assert response.status_code == 200
    """
    return app.test_client()


@pytest.fixture(scope='function', autouse=True)
def db_connection():
    """
    Provide database connection for testing.

    Automatically cleans database before each test.
    Uses autouse=True so it runs for every test automatically.

    Usage:
        def test_user_creation():
            # Database operations here - fresh database guaranteed
            pass
    """
    # Clean all test data from database before each test
    import sqlite3
    db_path = BaseDAL.get_db_path()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Delete all test data (keep schema)
        cursor.execute("DELETE FROM bookings")
        cursor.execute("DELETE FROM messages")
        cursor.execute("DELETE FROM reviews")
        cursor.execute("DELETE FROM resources")
        cursor.execute("DELETE FROM users")

        conn.commit()
        conn.close()
    except Exception as e:
        # Database might not exist yet or tables might not be created
        pass

    yield

    # Cleanup after test (optional - next test will clean anyway)


@pytest.fixture
def sample_user():
    """
    Provide sample user data for testing.

    Usage:
        def test_registration(client, sample_user):
            response = client.post('/auth/register', data=sample_user)
    """
    return {
        'name': 'Test User',
        'email': 'test@iu.edu',
        'password': 'TestPass123!',
        'role': 'student'
    }


@pytest.fixture
def authenticated_client(client, sample_user):
    """
    Provide authenticated test client.

    Usage:
        def test_dashboard(authenticated_client):
            response = authenticated_client.get('/dashboard')
            assert response.status_code == 200
    """
    # TODO: Implement authentication
    # 1. Create test user
    # 2. Login
    # 3. Return authenticated client

    return client


# TODO: Add more fixtures:
# - sample_resource
# - sample_booking
# - admin_client
# - staff_client
