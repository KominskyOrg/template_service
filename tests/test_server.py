# tests/test_server.py

import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
import importlib
import sys


def test_server_creates_app(mocker):
    """
    Test that the server module correctly initializes the Flask app
    by calling create_app and assigning it to the app variable.
    """
    # Remove 'app.server' from sys.modules if already loaded to ensure a fresh import
    if 'app.server' in sys.modules:
        del sys.modules['app.server']

    # Patch 'app.create_app' before importing 'app.server'
    with patch('app.create_app') as mock_create_app:
        # Create a mock Flask app instance to be returned by create_app
        mock_app = MagicMock(spec=Flask)
        mock_create_app.return_value = mock_app

        # Import the server module after patching
        server_module = importlib.import_module('app.server')

        # Assert that create_app was called exactly once
        mock_create_app.assert_called_once()

        # Assert that the 'app' variable in server_module is the mock_app
        assert server_module.app == mock_app
