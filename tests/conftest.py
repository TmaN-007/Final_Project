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


@pytest.fixture(scope='function')
def db_connection():
    """
    Provide database connection for testing.

    Automatically rolls back changes after each test.

    Usage:
        def test_user_creation(db_connection):
            # Database operations here
            pass
    """
    # Set test database path
    BaseDAL.set_db_path(':memory:')

    # TODO: Initialize test database schema

    yield

    # Cleanup after test
    # (In-memory database automatically cleaned up)


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
