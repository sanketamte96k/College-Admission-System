from flask import Blueprint, jsonify
from services import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/api/dashboard", methods=["GET"])
def get_dashboard_analytics():
    metrics = AnalyticsService.get_dashboard_metrics()
    return jsonify(metrics), 200
