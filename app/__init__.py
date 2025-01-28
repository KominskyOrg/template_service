from kom_python_core.python_core.logging import LoggingConfig
import logging
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from app.routes import stack_service_bp
from app.config import get_config
from app.database import init_db, db
import os


env = os.getenv("FLASK_ENV", "development")
log_level = os.getenv("LOG_LEVEL", "INFO")
logger_config = LoggingConfig(log_level=log_level, environment=env)
logger_config.configure()

logger = logging.get_logger(__name__)

def create_app():
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Configure Logging
    logger.configure()
    logger.set_log_level(log_level)
    logger.debug("Creating the Flask application.")

    # Load configuration
    config = get_config()
    app.config.from_object(config)
    logger.debug("Configuration loaded.")

    # Initialize the database
    init_db(app)
    logger.debug("Database has been initialized.")

    # Initialize Flask-Migrate
    Migrate(app, db)
    logger.debug("Flask-Migrate has been initialized.")

    # Import models after initializing db and migrate
    from app import models  # Ensure models are imported here

    # Register blueprints
    app.register_blueprint(stack_service_bp)
    logger.debug("Stack service blueprint registered.")

    # Conditionally register Swagger UI in development environment
    if app.config.get("ENV") == "development":
        register_swagger_ui(app)

    logger.info("Flask application creation complete.")
    return app


def register_swagger_ui(app) -> None:
    """Registers Swagger UI for API documentation in development environment."""
    try:
        from flask_swagger_ui import get_swaggerui_blueprint

        SWAGGER_URL = "/api/docs"
        API_URL = "/static/swagger.yaml"

        swaggerui_blueprint = get_swaggerui_blueprint(
            SWAGGER_URL, API_URL, config={"app_name": "Stack Service"}
        )
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
        logger.info("Swagger UI has been registered at %s.", SWAGGER_URL)
    except ImportError:
        logger.error("Flask-Swagger-UI is not installed. Swagger UI not available.")
    except Exception as e:
        logger.error("Failed to register Swagger UI: %s", e)
