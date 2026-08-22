from flask import Blueprint, request, jsonify, current_app, send_file
from functools import wraps
from services.transport_service import TransportService

transport_bp = Blueprint("transport", __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# DASHBOARD SUMMARY
# ============================================================
@transport_bp.route("/api/transport/dashboard", methods=["GET"])
def get_transport_dashboard():
    try:
        summary = TransportService.get_dashboard_summary()
        return jsonify(summary), 200
    except Exception as e:
        current_app.logger.exception("Error fetching transport dashboard")
        return jsonify({"error": str(e)}), 500

# ============================================================
# VEHICLE ENDPOINTS
# ============================================================
@transport_bp.route("/api/transport/vehicles", methods=["GET"])
def get_vehicles():
    status = request.args.get("status", "", type=str).strip()
    search = request.args.get("search", "", type=str).strip()
    try:
        vehicles = TransportService.get_vehicles(status=status, search=search)
        return jsonify(vehicles), 200
    except Exception as e:
        current_app.logger.exception("Error fetching vehicles")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/vehicles", methods=["POST"])
@admin_required
def add_vehicle():
    data = request.get_json() or {}
    try:
        success, msg, veh = TransportService.add_vehicle(data)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "vehicle": veh}), 201
    except Exception as e:
        current_app.logger.exception("Error adding vehicle")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/vehicles/<int:vehicle_id>", methods=["PUT"])
@admin_required
def update_vehicle(vehicle_id):
    data = request.get_json() or {}
    try:
        success, msg, veh = TransportService.update_vehicle(vehicle_id, data)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "vehicle": veh}), 200
    except Exception as e:
        current_app.logger.exception("Error updating vehicle")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/vehicles/<int:vehicle_id>", methods=["DELETE"])
@admin_required
def delete_vehicle(vehicle_id):
    try:
        success, msg = TransportService.delete_vehicle(vehicle_id)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg}), 200
    except Exception as e:
        current_app.logger.exception("Error deleting vehicle")
        return jsonify({"error": str(e)}), 500

# ============================================================
# ROUTE & STOP ENDPOINTS
# ============================================================
@transport_bp.route("/api/transport/routes", methods=["GET"])
def get_routes():
    status = request.args.get("status", "", type=str).strip()
    search = request.args.get("search", "", type=str).strip()
    try:
        routes = TransportService.get_routes(status=status, search=search)
        return jsonify(routes), 200
    except Exception as e:
        current_app.logger.exception("Error fetching routes")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/routes", methods=["POST"])
@admin_required
def add_route():
    data = request.get_json() or {}
    try:
        success, msg, r = TransportService.add_route(data)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "route": r}), 201
    except Exception as e:
        current_app.logger.exception("Error adding route")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/routes/<int:route_id>", methods=["PUT"])
@admin_required
def update_route(route_id):
    data = request.get_json() or {}
    try:
        success, msg, r = TransportService.update_route(route_id, data)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "route": r}), 200
    except Exception as e:
        current_app.logger.exception("Error updating route")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/routes/<int:route_id>", methods=["DELETE"])
@admin_required
def delete_route(route_id):
    try:
        success, msg = TransportService.delete_route(route_id)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg}), 200
    except Exception as e:
        current_app.logger.exception("Error deleting route")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/stops", methods=["POST"])
@admin_required
def add_stop():
    data = request.get_json() or {}
    try:
        success, msg, stop = TransportService.add_stop(data)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "stop": stop}), 201
    except Exception as e:
        current_app.logger.exception("Error adding stop")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/stops/<int:stop_id>", methods=["DELETE"])
@admin_required
def delete_stop(stop_id):
    try:
        success, msg = TransportService.delete_stop(stop_id)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg}), 200
    except Exception as e:
        current_app.logger.exception("Error deleting stop")
        return jsonify({"error": str(e)}), 500

# ============================================================
# DRIVER ENDPOINTS
# ============================================================
@transport_bp.route("/api/transport/drivers", methods=["GET"])
def get_drivers():
    status = request.args.get("status", "", type=str).strip()
    search = request.args.get("search", "", type=str).strip()
    try:
        drivers = TransportService.get_drivers(status=status, search=search)
        return jsonify(drivers), 200
    except Exception as e:
        current_app.logger.exception("Error fetching drivers")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/drivers", methods=["POST"])
@admin_required
def add_driver():
    data = request.get_json() or {}
    try:
        success, msg, d = TransportService.add_driver(data)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "driver": d}), 201
    except Exception as e:
        current_app.logger.exception("Error adding driver")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/drivers/<int:driver_id>", methods=["DELETE"])
@admin_required
def delete_driver(driver_id):
    try:
        success, msg = TransportService.delete_driver(driver_id)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg}), 200
    except Exception as e:
        current_app.logger.exception("Error deleting driver")
        return jsonify({"error": str(e)}), 500

# ============================================================
# STUDENT VERIFICATION & TRANSPORT PASS ASSIGNMENT
# ============================================================
@transport_bp.route("/api/transport/verify-student/<path:zprn>", methods=["GET"])
def verify_student_zprn(zprn):
    try:
        success, msg, s_data = TransportService.verify_student_by_zprn(zprn)
        if not success:
            return jsonify({"error": msg}), 404
        return jsonify({"message": msg, "student": s_data}), 200
    except Exception as e:
        current_app.logger.exception("Error verifying student for transport")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/assignments", methods=["GET"])
def get_assignments():
    route_id = request.args.get("route_id", None, type=int)
    search = request.args.get("search", "", type=str).strip()
    try:
        assignments = TransportService.get_assignments(route_id=route_id, search=search)
        return jsonify(assignments), 200
    except Exception as e:
        current_app.logger.exception("Error fetching assignments")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/assignments", methods=["POST"])
@admin_required
def assign_transport():
    data = request.get_json() or {}
    zprn = data.get("zprn") or data.get("student_id")
    route_id = data.get("route_id")
    stop_id = data.get("stop_id")
    vehicle_id = data.get("vehicle_id")
    fee_amount = data.get("fee_amount", 15000.0)

    if not zprn or not route_id or not stop_id:
        return jsonify({"error": "ZPRN/Student ID, Route ID, and Stop ID are required fields."}), 400

    try:
        success, msg, assignment = TransportService.assign_student_transport(
            zprn_or_student_id=zprn,
            route_id=route_id,
            stop_id=stop_id,
            vehicle_id=vehicle_id,
            fee_amount=fee_amount
        )
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "assignment": assignment}), 201
    except Exception as e:
        current_app.logger.exception("Error issuing transport assignment")
        return jsonify({"error": str(e)}), 500

@transport_bp.route("/api/transport/assignments/<int:assignment_id>/cancel", methods=["POST"])
@admin_required
def cancel_assignment(assignment_id):
    try:
        success, msg = TransportService.cancel_assignment(assignment_id)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg}), 200
    except Exception as e:
        current_app.logger.exception("Error cancelling transport assignment")
        return jsonify({"error": str(e)}), 500

# ============================================================
# EXPORTS
# ============================================================
@transport_bp.route("/api/transport/export/pdf", methods=["GET"])
def export_transport_pdf():
    report_type = request.args.get("type", "vehicle", type=str).strip().lower()
    try:
        pdf_buffer, err = TransportService.generate_pdf_transport_report(report_type)
        if err:
            return jsonify({"error": err}), 400
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"zeal_transport_{report_type}_report.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        current_app.logger.exception("Error generating transport PDF report")
        return jsonify({"error": str(e)}), 500
