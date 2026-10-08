"""
app.py
------
Entry point for the Cloud Identity and Access Auditor Flask application.

Run with:
    python app.py

The Flask dev server will start on http://127.0.0.1:5000
"""

from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.routes import api_bp

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────

BASE_DIR     = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

# ──────────────────────────────────────────────
# Create Flask app
# ──────────────────────────────────────────────

# Pass FRONTEND_DIR as a plain str so Flask's type is unambiguous
app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path="",
)

# Allow cross-origin requests (useful if frontend is served separately)
CORS(app)

# Register all /api/* routes from the Blueprint
app.register_blueprint(api_bp)


# ──────────────────────────────────────────────
# Serve the frontend
# ──────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main dashboard page."""
    return send_from_directory(str(FRONTEND_DIR), "index.html")


# ──────────────────────────────────────────────
# Run the server
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Cloud Identity and Access Auditor")
    print("  Starting on: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True, host="127.0.0.1", port=5000)
