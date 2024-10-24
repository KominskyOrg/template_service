import pytest
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# Tests for /health endpoint
def test_health(client) -> None:
    response = client.get("/service/stack/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "OK"}
