from flask import Blueprint, jsonify
import logging

# Get the logger
logger = logging.getLogger(__name__)

stack_service_bp = Blueprint("stack", __name__, url_prefix="/service/stack")


@stack_service_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint to verify that the stack_service is running."""
    return jsonify({"status": "OK"}), 200
