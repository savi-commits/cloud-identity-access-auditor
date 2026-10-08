"""
routes.py
---------
Flask Blueprint containing all API endpoints for the auditor.

Endpoints:
  GET  /api/health       – health check
  GET  /api/sample-data  – returns mock IAM data
  POST /api/audit        – accepts IAM JSON and returns audit results
"""

from flask import Blueprint, request, jsonify

from backend.audit_engine  import run_audit
from backend.mock_iam_data import get_mock_iam_data

# Blueprint groups all /api/* routes together
api_bp = Blueprint("api", __name__, url_prefix="/api")


# ──────────────────────────────────────────────
# GET /api/health
# ──────────────────────────────────────────────
@api_bp.route("/health", methods=["GET"])
def health_check():
    """Simple endpoint to confirm the server is running."""
    return jsonify({"status": "ok", "service": "Cloud Identity and Access Auditor"}), 200


# ──────────────────────────────────────────────
# GET /api/sample-data
# ──────────────────────────────────────────────
@api_bp.route("/sample-data", methods=["GET"])
def sample_data():
    """
    Returns the built-in mock IAM configuration so the user can load
    it into the frontend without typing anything.
    """
    return jsonify(get_mock_iam_data()), 200


# ──────────────────────────────────────────────
# POST /api/audit
# ──────────────────────────────────────────────
@api_bp.route("/audit", methods=["POST"])
def audit():
    """
    Accepts IAM configuration JSON in the request body and returns
    a full audit report.

    Expected JSON structure:
    {
        "users": [...],
        "roles": [...]
    }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON. Set Content-Type: application/json"}), 400

    iam_data = request.get_json()

    if not isinstance(iam_data, dict):
        return jsonify({"error": "Invalid JSON format. Expected a JSON object."}), 400

    if "users" not in iam_data and "roles" not in iam_data:
        return jsonify({
            "error": "IAM data must contain at least a 'users' or 'roles' key."
        }), 400

    try:
        result = run_audit(iam_data)
    except Exception as exc:
        return jsonify({"error": f"Audit failed: {str(exc)}"}), 500

    return jsonify(result), 200
