# app/database.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import logging
from contextlib import contextmanager

# Initialize Flask-SQLAlchemy
db = SQLAlchemy()

# Get the logger
logger = logging.getLogger(__name__)


def init_db(app) -> None:
    """Initializes the database with the Flask app."""
    db.init_app(app)
    logger.debug("Database has been initialized.")


@contextmanager
def get_db():
    """Provides a database session for a request.
    Closes the session when done.
    """
    logger.debug("Getting database session")
    db_session = db.session
    try:
        yield db_session
    except SQLAlchemyError as e:
        logger.error(f"Database session rollback due to error: {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()
        logger.debug("Database session closed")
