# tests/test_request_handler.py

import pytest
from unittest.mock import Mock
from flask import Flask
from app.utils.request_handler import handle_request
from app.utils.exceptions import (
    ValidationError as CustomValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
)
from marshmallow import ValidationError as MarshmallowValidationError
import logging

# -------------------- Pytest Fixtures -------------------- #


@pytest.fixture
def app():
    """Fixture to create a Flask app for testing."""
    app = Flask(__name__)
    return app


# -------------------- handle_request Tests -------------------- #


def test_handle_request_success(client, mocker, caplog) -> None:
    """Test handle_request with a successful service function.
    Ensures that the correct response and status code are returned.
    """
    # Arrange
    service_function = Mock()
    service_function.__name__ = "mock_service"
    expected_response = {"data": "success"}
    expected_status_code = 200
    service_function.return_value = (expected_response, expected_status_code)

    # Set logging level to capture INFO and DEBUG logs
    caplog.set_level(logging.DEBUG, logger="app.utils.request_handler")

    # Act
    response, status_code = handle_request(service_function, "arg1", key="value")

    # Assert
    assert status_code == expected_status_code
    assert response.json == expected_response

    service_function.assert_called_once_with("arg1", key="value")

    # Verify logs
    assert "Handling request for mock_service" in caplog.text
    assert "Arguments: args=('arg1',), kwargs={'key': 'value'}" in caplog.text
    assert (
        "Service function response: {'data': 'success'}, Status code: 200"
        in caplog.text
    )


def test_handle_request_validation_error(client, mocker, caplog) -> None:
    """Test handle_request when a Marshmallow ValidationError is raised.
    Ensures that a 400 Bad Request is returned.
    """
    # Arrange
    service_function = Mock()
    service_function.__name__ = "mock_service"
    error_message = "Invalid input data"
    service_function.side_effect = MarshmallowValidationError(error_message)

    # Set logging level to capture WARNING logs
    caplog.set_level(logging.WARNING, logger="app.utils.request_handler")

    # Act
    response, status_code = handle_request(service_function, "arg1", key="value")

    # Assert
    assert status_code == 400
    assert response.json == {"error": error_message}

    service_function.assert_called_once_with("arg1", key="value")

    # Verify logs
    assert f"Validation error in mock_service: {error_message}" in caplog.text


def test_handle_request_custom_validation_error(client, mocker, caplog) -> None:
    """Test handle_request when a custom ValidationError is raised.
    Ensures that a 400 Bad Request is returned.
    """
    # Arrange
    service_function = Mock()
    service_function.__name__ = "mock_service"
    error_message = "Custom validation error"
    service_function.side_effect = CustomValidationError(error_message)

    # Set logging level to capture WARNING logs
    caplog.set_level(logging.WARNING, logger="app.utils.request_handler")

    # Act
    response, status_code = handle_request(service_function, "arg1", key="value")

    # Assert
    assert status_code == 400
    assert response.json == {"error": error_message}

    service_function.assert_called_once_with("arg1", key="value")

    # Verify logs
    assert f"Validation error in mock_service: {error_message}" in caplog.text


def test_handle_request_authentication_error(client, mocker, caplog) -> None:
    """Test handle_request when an AuthenticationError is raised.
    Ensures that a 401 Unauthorized is returned.
    """
    # Arrange
    service_function = Mock()
    service_function.__name__ = "mock_service"
    error_message = "Authentication failed"
    service_function.side_effect = AuthenticationError(error_message)

    # Set logging level to capture WARNING logs
    caplog.set_level(logging.WARNING, logger="app.utils.request_handler")

    # Act
    response, status_code = handle_request(service_function, "arg1", key="value")

    # Assert
    assert status_code == 401
    assert response.json == {"error": error_message}

    service_function.assert_called_once_with("arg1", key="value")

    # Verify logs
    assert f"Authentication error in mock_service: {error_message}" in caplog.text


def test_handle_request_authorization_error(client, mocker, caplog) -> None:
    """Test handle_request when an AuthorizationError is raised.
    Ensures that a 403 Forbidden is returned.
    """
    # Arrange
    service_function = Mock()
    service_function.__name__ = "mock_service"
    error_message = "Authorization failed"
    service_function.side_effect = AuthorizationError(error_message)

    # Set logging level to capture WARNING logs
    caplog.set_level(logging.WARNING, logger="app.utils.request_handler")

    # Act
    response, status_code = handle_request(service_function, "arg1", key="value")

    # Assert
    assert status_code == 403
    assert response.json == {"error": error_message}

    service_function.assert_called_once_with("arg1", key="value")

    # Verify logs
    assert f"Authorization error in mock_service: {error_message}" in caplog.text


def test_handle_request_database_error(client, mocker, caplog) -> None:
    """Test handle_request when a DatabaseError is raised.
    Ensures that a 500 Internal Server Error is returned.
    """
    # Arrange
    service_function = Mock()
    service_function.__name__ = "mock_service"
    error_message = "Database connection failed"
    service_function.side_effect = DatabaseError(error_message)

    # Set logging level to capture ERROR logs
    caplog.set_level(logging.ERROR, logger="app.utils.request_handler")

    # Act
    response, status_code = handle_request(service_function, "arg1", key="value")

    # Assert
    assert status_code == 500
    assert response.json == {"error": "Database error occurred"}

    service_function.assert_called_once_with("arg1", key="value")

    # Verify logs
    assert f"Database error in mock_service: {error_message}" in caplog.text


def test_handle_request_unexpected_error(client, mocker, caplog) -> None:
    """Test handle_request when a generic Exception is raised.
    Ensures that a 500 Internal Server Error is returned.
    """
    # Arrange
    service_function = Mock()
    service_function.__name__ = "mock_service"
    error_message = "Unexpected failure"
    service_function.side_effect = Exception(error_message)

    # Set logging level to capture EXCEPTION logs
    caplog.set_level(logging.ERROR, logger="app.utils.request_handler")

    # Act
    response, status_code = handle_request(service_function, "arg1", key="value")

    # Assert
    assert status_code == 500
    assert response.json == {"error": "Internal server error"}

    service_function.assert_called_once_with("arg1", key="value")

    # Verify logs
    assert f"Unexpected error in mock_service: {error_message}" in caplog.text
    # Additionally, check that the exception was logged with traceback
    assert "Traceback (most recent call last)" in caplog.text
