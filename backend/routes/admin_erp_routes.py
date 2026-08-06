from flask import Blueprint, request, jsonify
from services import SeatService
from utils import admin_required

admin_erp_bp = Blueprint("admin_erp", __name__)

@admin_erp_bp.route("/api/erp/seat-matrix", methods=["GET"])
def get_seat_matrix():
    matrix = SeatService.get_seat_matrix()
    return jsonify(matrix), 200

@admin_erp_bp.route("/api/erp/merit-list", methods=["GET"])
def get_merit_list():
    department = request.args.get("department", "", type=str).strip()
    merit_list = SeatService.generate_merit_list(department if department else None)
    return jsonify(merit_list), 200

@admin_erp_bp.route("/api/erp/reports", methods=["GET"])
@admin_required
def get_reports():
    reports = SeatService.generate_reports()
    return jsonify(reports), 200
