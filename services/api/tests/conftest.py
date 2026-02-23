"""
Shared test fixtures for the API service.

I'm using an in-memory approach where each test run gets a fresh database
state via transaction rollback, keeping tests fast and isolated.
"""

import pytest

from app.create_app import create_app
from app.config import TestingConfig
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Create application for the entire test session."""
    test_app = create_app(config_override=TestingConfig)
    yield test_app


@pytest.fixture(scope="function")
def db(app):
    """Provide a clean database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    """Flask test client with a clean database."""
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client
