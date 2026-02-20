from flask import Blueprint, jsonify

from app.extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return jsonify({
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
    }), 200 if db_status == "healthy" else 503
