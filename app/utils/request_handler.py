# app/utils/request_handler.py

import logging
from flask import jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from app.utils.exceptions import (
    ValidationError as CustomValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
)

logger = logging.getLogger(__name__)


def handle_request(service_function, *args, **kwargs):
    logger.info(f"Handling request for {service_function.__name__}")
    logger.debug(f"Arguments: args={args}, kwargs={kwargs}")
    try:
        response, status_code = service_function(*args, **kwargs)
        logger.debug(
            f"Service function response: {response}, Status code: {status_code}"
        )
        return jsonify(response), status_code
    except MarshmallowValidationError as ve:
        logger.warning(
            f"Validation error in {service_function.__name__}: {ve.messages}"
        )
        return jsonify({"error": ve.messages}), 400
    except CustomValidationError as ve:
        logger.warning(f"Validation error in {service_function.__name__}: {ve.message}")
        return jsonify({"error": ve.message}), 400
    except AuthenticationError as ae:
        logger.warning(
            f"Authentication error in {service_function.__name__}: {ae.message}"
        )
        return jsonify({"error": ae.message}), 401
    except AuthorizationError as aze:
        logger.warning(
            f"Authorization error in {service_function.__name__}: {aze.message}"
        )
        return jsonify({"error": aze.message}), 403
    except DatabaseError as de:
        logger.error(f"Database error in {service_function.__name__}: {de}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.exception(f"Unexpected error in {service_function.__name__}: {e}")
        return jsonify({"error": "Internal server error"}), 500
