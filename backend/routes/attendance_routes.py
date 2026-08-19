from flask import Blueprint, request, jsonify, session
from services import AttendanceService
from utils import admin_required, student_required

attendance_bp = Blueprint("attendance", __name__)


# ============================================================
# ADMIN ONLY: GET ATTENDANCE SHEET FOR DATE & DEPARTMENT
# ============================================================
@attendance_bp.route("/api/attendance", methods=["GET"])
@admin_required
def get_attendance():
    department = request.args.get("department")
    date_str = request.args.get("date")

    data, error = AttendanceService.get_students_for_attendance(
        department=department,
        date_str=date_str
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify(data), 200


# ============================================================
# ADMIN ONLY: SAVE / UPDATE BULK ATTENDANCE
# ============================================================
@attendance_bp.route("/api/attendance", methods=["POST"])
@admin_required
def save_attendance():
    data = request.get_json(silent=True) or {}
    attendance_date = data.get("attendance_date") or data.get("date")
    records = data.get("records")

    if not attendance_date:
        return jsonify({"error": "Attendance date (YYYY-MM-DD) is required."}), 400

    if not records or not isinstance(records, list):
        return jsonify({"error": "Attendance records list is required."}), 400

    admin_username = session.get("admin_username") or "admin"

    success, message, result = AttendanceService.record_bulk_attendance(
        attendance_date_str=attendance_date,
        records=records,
        admin_username=admin_username
    )

    if not success:
        return jsonify({"error": message}), 400

    return jsonify({
        "success": True,
        "message": message,
        "data": result
    }), 201


# ============================================================
# ADMIN ONLY: ATTENDANCE ANALYTICS REPORT
# ============================================================
@attendance_bp.route("/api/attendance/report", methods=["GET"])
@admin_required
def get_attendance_report():
    department = request.args.get("department")
    date_str = request.args.get("date")

    report, error = AttendanceService.get_attendance_report(
        department=department,
        date_str=date_str
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify(report), 200


# ============================================================
# ADMIN OR AUTHORIZED STUDENT: GET SPECIFIC STUDENT ATTENDANCE
# ============================================================
@attendance_bp.route("/api/students/<int:student_id>/attendance", methods=["GET"])
def get_student_attendance(student_id):
    is_admin = bool(session.get("admin_id"))
    current_student_id = session.get("student_id")

    if not is_admin:
        if not current_student_id:
            return jsonify({"error": "Authentication required", "redirect": "/login.html"}), 401
        if int(current_student_id) != int(student_id):
            return jsonify({"error": "Forbidden: You cannot access another student's attendance records."}), 403

    summary = AttendanceService.get_student_attendance_summary(student_id)
    if not summary:
        return jsonify({"error": f"Student #{student_id} not found."}), 404

    return jsonify(summary), 200


# ============================================================
# LOGGED-IN STUDENT PORTAL: GET OWN ATTENDANCE
# ============================================================
@attendance_bp.route("/api/student/attendance", methods=["GET"])
@student_required
def get_logged_in_student_attendance():
    student_id = session.get("student_id")
    summary = AttendanceService.get_student_attendance_summary(student_id)
    if not summary:
        return jsonify({"error": "Student record not found."}), 404

    return jsonify(summary), 200
