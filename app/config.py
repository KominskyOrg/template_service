import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    logger.debug("Config base class initialized.")


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "LOCAL_DATABASE_URL", "mysql://stack_user:stack_password@db:3306/stack_db"
    )
    DEBUG = True
    ENV = "development"
    logger.debug("DevConfig initialized with DEBUG=True and ENV=development.")


class StagingConfig(Config):
    DEBUG = True
    ENV = "staging"

    DB_USERNAME = os.getenv("db_username")
    DB_PASSWORD = os.getenv("db_password")
    DB_NAME = os.getenv("db_name")
    DB_HOST = os.getenv("db_host")
    DB_PORT = os.getenv("db_port")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    logger.debug("StagingConfig initialized with DEBUG=True and ENV=staging.")


class ProdConfig(Config):
    DEBUG = False
    ENV = "production"

    DB_USERNAME = os.getenv("db_username")
    DB_PASSWORD = os.getenv("db_password")
    DB_NAME = os.getenv("db_name")
    DB_HOST = os.getenv("db_host")
    DB_PORT = os.getenv("db_port")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    logger.debug("ProdConfig initialized with DEBUG=False and ENV=production.")


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    logger.debug(f"FLASK_ENV: {env}")

    if env == "development":
        config = DevConfig
        logger.info("Loading DevConfig.")
    elif env == "staging":
        config = StagingConfig
        logger.info("Loading StagingConfig.")
    elif env == "production":
        config = ProdConfig
        logger.info("Loading ProdConfig.")
    else:
        logger.error(f"Unknown environment: {env}")
        raise ValueError(f"Unknown environment: {env}")

    # Set log level based on environment
    if env == "production":
        logger.setLevel(logging.INFO)
        logger.info("Log level set to INFO for production.")
    else:
        logger.setLevel(logging.DEBUG)
        logger.debug(f"Log level set to DEBUG for {env} environment.")

    return config
