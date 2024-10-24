# tests/test_init.py

import pytest
import logging
import os
from unittest import mock

from app.routes import stack_service_bp

# ---------------------------
# Pytest Fixtures
# ---------------------------


@pytest.fixture
def set_development_env(monkeypatch) -> None:
    """Set FLASK_ENV to 'development'."""
    monkeypatch.setenv("FLASK_ENV", "development")


@pytest.fixture
def set_production_env(monkeypatch) -> None:
    """Set FLASK_ENV to 'production'."""
    monkeypatch.setenv("FLASK_ENV", "production")


@pytest.fixture
def mock_init_db(mocker):
    """Mock the init_db function to prevent actual database initialization."""
    return mocker.patch("app.init_db")


@pytest.fixture
def mock_register_blueprint(mocker):
    """Mock Flask's register_blueprint method to prevent actual blueprint registration."""
    return mocker.patch("flask.Flask.register_blueprint")


@pytest.fixture
def mock_get_swaggerui_blueprint(mocker):
    """Mock get_swaggerui_blueprint to return a mock blueprint."""
    return mocker.patch(
        "flask_swagger_ui.get_swaggerui_blueprint",  # Correct patch path
        return_value="swaggerui_blueprint_mock",
    )


@pytest.fixture
def mock_get_swaggerui_blueprint_exception(mocker):
    """Mock get_swaggerui_blueprint to raise an exception."""
    return mocker.patch(
        "flask_swagger_ui.get_swaggerui_blueprint",  # Correct patch path
        side_effect=Exception("Test Exception"),
    )


@pytest.fixture
def mock_flask_swagger_ui_import_error():
    """Simulate ImportError by removing flask_swagger_ui from sys.modules."""
    with mock.patch.dict("sys.modules", {"flask_swagger_ui": None}):
        yield


# ---------------------------
# Test Functions
# ---------------------------


def test_create_app_development(
    set_development_env,
    mock_init_db,
    mock_register_blueprint,
    mock_get_swaggerui_blueprint,
    caplog,
) -> None:
    """Test creating the app in development environment."""
    from app import create_app

    with caplog.at_level(logging.INFO):
        app = create_app()

    assert app is not None, "App instance should not be None."
    assert (
        app.config["ENV"] == "development"
    ), f"Expected ENV to be 'development', got '{app.config['ENV']}'."

    # Ensure that init_db was called with app
    mock_init_db.assert_called_once_with(app)

    # Ensure that register_blueprint was called with stack_service_bp
    mock_register_blueprint.assert_any_call(stack_service_bp)

    # Ensure that get_swaggerui_blueprint was called once
    mock_get_swaggerui_blueprint.assert_called_once()

    # Ensure that register_blueprint was called with the mocked Swagger UI blueprint
    mock_register_blueprint.assert_any_call(
        "swaggerui_blueprint_mock", url_prefix="/api/docs"
    )

    # Ensure logging setup (StreamHandler)
    assert any(
        isinstance(h, logging.StreamHandler) for h in app.logger.handlers
    ), "StreamHandler not found in logger handlers."

    # Ensure the log messages are present
    expected_logs = [
        "Swagger UI has been registered at /api/docs.",
    ]
    for log_msg in expected_logs:
        assert (
            log_msg in caplog.text
        ), f"Expected log message '{log_msg}' not found in caplog."


def test_create_app_production(
    set_production_env, mock_init_db, mock_register_blueprint, caplog
) -> None:
    """Test creating the app in production environment."""
    from app import create_app

    with caplog.at_level(logging.INFO):
        app = create_app()

    # Assert that the app was created successfully
    assert app is not None, "App instance should not be None."
    assert (
        app.config["ENV"] == "production"
    ), f"Expected ENV to be 'production', got '{app.config['ENV']}'."

    # Ensure that init_db was called with the app instance
    mock_init_db.assert_called_once_with(app)

    # Ensure that register_blueprint was called with stack_service_bp
    mock_register_blueprint.assert_any_call(stack_service_bp)

    # Check for FileHandler in logger handlers
    file_handlers = [
        h for h in app.logger.handlers if isinstance(h, logging.FileHandler)
    ]
    assert (
        len(file_handlers) == 1
    ), "Expected exactly one FileHandler in logger handlers."

    # Optionally, verify the filename of the FileHandler
    file_handler = file_handlers[0]
    expected_log_filename = "app.log"
    actual_log_filename = os.path.basename(file_handler.baseFilename)
    assert (
        actual_log_filename == expected_log_filename
    ), f"FileHandler is writing to '{actual_log_filename}', expected '{expected_log_filename}'."

    # Ensure that Swagger UI is not registered in production
    assert (
        "Swagger UI has been registered" not in caplog.text
    ), "Swagger UI should not be registered in production."


def test_register_swagger_ui_import_error(
    set_development_env, mock_init_db, caplog, mock_flask_swagger_ui_import_error
) -> None:
    """Test registering Swagger UI when flask_swagger_ui is not installed."""
    from app import create_app

    with caplog.at_level(logging.ERROR):
        create_app()

    # Check that the ImportError was logged
    expected_log_message = (
        "Flask-Swagger-UI is not installed. Swagger UI not available."
    )
    assert (
        expected_log_message in caplog.text
    ), f"Expected log message '{expected_log_message}' not found in caplog."


def test_register_swagger_ui_exception(
    set_development_env,
    mock_init_db,
    mock_register_blueprint,
    mock_get_swaggerui_blueprint_exception,
    caplog,
) -> None:
    """Test handling of exceptions when registering Swagger UI."""
    from app import create_app

    with caplog.at_level(logging.ERROR):
        create_app()

    # Assert that the exception was caught and logged
    expected_log_message = "Failed to register Swagger UI: Test Exception"
    assert (
        expected_log_message in caplog.text
    ), f"Expected log message '{expected_log_message}' not found in caplog."

    # Ensure that Swagger UI was not registered
    assert (
        "Swagger UI has been registered at /api/docs." not in caplog.text
    ), "Swagger UI should not be registered after exception."
