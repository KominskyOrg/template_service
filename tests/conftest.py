# tests/conftest.py

import pytest
from app import create_app


@pytest.fixture
def app():
    """Creates and configures a new app instance for each test."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            # You can add more test-specific configurations here if needed
        }
    )

    yield app

    # Teardown can be done here if necessary
