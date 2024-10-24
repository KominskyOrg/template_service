# tests/test_database.py

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

from app.database import init_db, get_db, db


@pytest.fixture
def mock_app(mocker):
    """
    Fixture to create a mock Flask app.
    """
    return mocker.MagicMock()


def test_init_db_calls_init_app(mock_app, mocker):
    """
    Test that init_db initializes the database with the Flask app
    and logs the appropriate debug message.
    """
    # Arrange
    mock_init_app = mocker.patch.object(db, 'init_app')
    mock_logger_debug = mocker.patch('app.database.logger.debug')

    # Act
    init_db(mock_app)

    # Assert
    mock_init_app.assert_called_once_with(mock_app)
    mock_logger_debug.assert_called_once_with("Database has been initialized.")


def test_get_db_success(mocker):
    """
    Test that get_db yields the database session correctly
    and closes the session after use without errors.
    """
    # Arrange
    mock_session = mocker.MagicMock()
    # Patch 'db.session' as a property, not as a callable
    mocker.patch.object(db, 'session', new=mock_session)
    mock_logger_debug = mocker.patch('app.database.logger.debug')
    mock_logger_error = mocker.patch('app.database.logger.error')

    # Act
    with get_db() as session:
        # Simulate some database operations
        session.query.return_value.all.return_value = []

    # Assert
    mock_logger_debug.assert_any_call("Getting database session")
    mock_logger_debug.assert_any_call("Database session closed")
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_not_called()
    mock_logger_error.assert_not_called()


def test_get_db_exception(mocker):
    """
    Test that get_db handles exceptions by rolling back the session,
    logging the error, and re-raising the exception.
    """
    # Arrange
    mock_session = mocker.MagicMock()
    # Patch 'db.session' as a property, not as a callable
    mocker.patch.object(db, 'session', new=mock_session)
    mock_logger_debug = mocker.patch('app.database.logger.debug')
    mock_logger_error = mocker.patch('app.database.logger.error')

    # Act & Assert
    with pytest.raises(SQLAlchemyError, match="Test exception"):
        with get_db() as session:
            # Simulate a database operation that raises an exception
            session.some_operation.side_effect = SQLAlchemyError("Test exception")
            session.some_operation()

    # Assert
    mock_logger_debug.assert_any_call("Getting database session")
    mock_logger_debug.assert_any_call("Database session closed")
    mock_logger_error.assert_called_once_with("Database session rollback due to error: Test exception")
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
