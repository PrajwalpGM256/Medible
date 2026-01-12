"""
Health Check Routes
For monitoring and load balancer health checks
"""

from flask import Blueprint
from app.errors import api_response

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return api_response(
        data={
            "status": "healthy",
            "service": "medible-api",
            "version": "1.0.0"
        },
        meta={"endpoint": "/health"}
    )


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check - verifies service can handle requests
    """
    checks = {
        "database": check_database(),
        "openfda_api": check_openfda(),
        "usda_api": check_usda()
    }
    
    all_healthy = all(c["status"] == "up" for c in checks.values())
    
    return api_response(
        data={
            "status": "ready" if all_healthy else "degraded",
            "checks": checks
        },
        status_code=200 if all_healthy else 503
    )


def check_database():
    """Check database connectivity"""
    try:
        from app import db
        db.session.execute(db.text('SELECT 1'))
        return {"status": "up"}
    except Exception as e:
        return {"status": "down", "error": str(e)}


def check_openfda():
    """Check OpenFDA API availability"""
    try:
        import requests
        resp = requests.get("https://api.fda.gov/drug/label.json?limit=1", timeout=5)
        return {"status": "up" if resp.status_code == 200 else "down"}
    except Exception:
        return {"status": "down"}


def check_usda():
    """Check USDA API availability"""
    try:
        import requests
        import os
        api_key = os.getenv('USDA_API_KEY', '')
        if not api_key:
            return {"status": "unconfigured"}
        resp = requests.get(
            f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query=test&pageSize=1",
            timeout=5
        )
        return {"status": "up" if resp.status_code == 200 else "down"}
    except Exception:
        return {"status": "down"}