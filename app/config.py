import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

    def __init__(self):
        logger.debug("Base Config class initialized.")


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "LOCAL_DATABASE_URL", "mysql://stack_user:stack_password@db:3306/stack_db"
    )
    DEBUG = True
    ENV = "development"

    def __init__(self):
        super().__init__()
        logger.debug("DevConfig initialized with DEBUG=True and ENV=development.")


class StagingConfig(Config):
    DEBUG = True
    ENV = "staging"

    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    def __init__(self):
        super().__init__()
        logger.debug("StagingConfig initialized with DEBUG=True and ENV=staging.")


class ProdConfig(Config):
    DEBUG = False
    ENV = "production"

    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    def __init__(self):
        super().__init__()
        logger.debug("ProdConfig initialized with DEBUG=False and ENV=production.")


def get_config():
    env = os.getenv("FLASK_ENV", "development")

    if env == "development":
        return DevConfig()
    elif env == "staging":
        return StagingConfig()
    elif env == "production":
        return ProdConfig()
    else:
        raise ValueError(f"Unknown FLASK_ENV: {env}")
