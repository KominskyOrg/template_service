# tests/test_config.py

import pytest
from unittest.mock import patch
import importlib


@pytest.mark.parametrize(
    "env_vars,expected_uri,expected_debug,expected_env",
    [
        (
            # DevConfig with LOCAL_DATABASE_URL set
            {
                "FLASK_ENV": "development",
                "LOCAL_DATABASE_URL": "mysql://dev_user:dev_pass@localhost:3306/dev_db",
            },
            "mysql://dev_user:dev_pass@localhost:3306/dev_db",
            True,
            "development",
        ),
        (
            # DevConfig without LOCAL_DATABASE_URL set (should use default)
            {
                "FLASK_ENV": "development",
                # No LOCAL_DATABASE_URL provided
            },
            "mysql://stack_user:stack_password@db:3306/stack_db",
            True,
            "development",
        ),
        (
            # StagingConfig with all required environment variables set
            {
                "FLASK_ENV": "staging",
                "db_username": "staging_user",
                "db_password": "staging_pass",
                "db_name": "staging_db",
                "db_host": "staging_host",
                "db_port": "3307",
            },
            "mysql+pymysql://staging_user:staging_pass@staging_host:3307/staging_db",
            True,
            "staging",
        ),
        (
            # ProdConfig with all required environment variables set
            {
                "FLASK_ENV": "production",
                "db_username": "prod_user",
                "db_password": "prod_pass",
                "db_name": "prod_db",
                "db_host": "prod_host",
                "db_port": "3308",
            },
            "mysql+pymysql://prod_user:prod_pass@prod_host:3308/prod_db",
            False,
            "production",
        ),
    ],
)
def test_configuration(env_vars, expected_uri, expected_debug, expected_env) -> None:
    """Test configuration classes based on environment variables."""
    with patch.dict("os.environ", env_vars, clear=True):
        import app.config

        importlib.reload(app.config)
        from app.config import Config, DevConfig, StagingConfig, ProdConfig

        # Determine which config class to test based on FLASK_ENV
        flask_env = env_vars.get("FLASK_ENV", "development")
        if flask_env == "development":
            config = DevConfig
        elif flask_env == "staging":
            config = StagingConfig
        elif flask_env == "production":
            config = ProdConfig
        else:
            pytest.fail(f"Unknown FLASK_ENV: {flask_env}")

        # Assertions
        assert config.SQLALCHEMY_DATABASE_URI == expected_uri
        assert config.DEBUG == expected_debug
        assert config.ENV == expected_env
        assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False


def test_get_config_development() -> None:
    """Test that get_config() returns DevConfig when FLASK_ENV is development."""
    env_vars = {
        "FLASK_ENV": "development",
        "LOCAL_DATABASE_URL": "mysql://dev_user:dev_pass@localhost:3306/dev_db",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        import app.config

        importlib.reload(app.config)
        from app.config import get_config, DevConfig

        config_class = get_config()
        assert config_class == DevConfig


def test_get_config_staging() -> None:
    """Test that get_config() returns StagingConfig when FLASK_ENV is staging."""
    env_vars = {
        "FLASK_ENV": "staging",
        "db_username": "staging_user",
        "db_password": "staging_pass",
        "db_name": "staging_db",
        "db_host": "staging_host",
        "db_port": "3307",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        import app.config

        importlib.reload(app.config)
        from app.config import get_config, StagingConfig

        config_class = get_config()
        assert config_class == StagingConfig


def test_get_config_production() -> None:
    """Test that get_config() returns ProdConfig when FLASK_ENV is production."""
    env_vars = {
        "FLASK_ENV": "production",
        "db_username": "prod_user",
        "db_password": "prod_pass",
        "db_name": "prod_db",
        "db_host": "prod_host",
        "db_port": "3308",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        import app.config

        importlib.reload(app.config)
        from app.config import get_config, ProdConfig

        config_class = get_config()
        assert config_class == ProdConfig


def test_get_config_unknown_env() -> None:
    """Test that get_config() raises ValueError for an unknown FLASK_ENV."""
    env_vars = {
        "FLASK_ENV": "unknown_env",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        import app.config

        importlib.reload(app.config)
        from app.config import get_config

        with pytest.raises(ValueError) as excinfo:
            get_config()
        assert "Unknown environment: unknown_env" in str(excinfo.value)
