from flask import Blueprint, request, jsonify, session, current_app
from services import StudentService
from email_service import send_student_confirmation_email, send_admin_notification_email
from utils import admin_required, student_required

student_bp = Blueprint("students", __name__)

@student_bp.route("/api/students", methods=["GET"])
def get_students():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 50, type=int)
    search_query = request.args.get("search", "", type=str).strip()
    department = request.args.get("dept", "", type=str).strip()
    admission_type = request.args.get("admission_type", "", type=str).strip()
    gender = request.args.get("gender", "", type=str).strip()

    result = StudentService.get_all_students(
        page=page,
        limit=limit,
        search_query=search_query,
        department=department,
        admission_type=admission_type,
        gender=gender
    )
    # If limit is 50/large and no pagination parameter requested, return raw array for backward compatibility
    if "page" not in request.args:
        return jsonify(result["students"]), 200
    return jsonify(result), 200

@student_bp.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = StudentService.get_student_by_id(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student.to_dict()), 200

@student_bp.route("/api/students", methods=["POST"])
def create_student():
    data = request.get_json() or request.form or {}
    files = request.files

    try:
        new_student = StudentService.create_student(
            data=data,
            files=files,
            upload_folder=current_app.config["UPLOAD_FOLDER"]
        )
        student_dict = new_student.to_dict()

        # Trigger email notifications
        mail_ext = current_app.extensions.get("mail")
        email_sent = False
        email_msg = ""
        if mail_ext:
            email_sent, email_msg = send_student_confirmation_email(mail_ext, student_dict)
            send_admin_notification_email(mail_ext, student_dict)

        if email_sent:
            return jsonify({
                "message": "Admission Submitted Successfully and Confirmation Email Sent!",
                "student": student_dict,
                "email_status": "sent"
            }), 201
        else:
            return jsonify({
                "message": "Admission Submitted Successfully. Email notification could not be delivered.",
                "student": student_dict,
                "email_status": "failed",
                "email_note": email_msg
            }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@student_bp.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json() or request.form or {}
    files = request.files

    student = StudentService.update_student(
        student_id=student_id,
        data=data,
        files=files,
        upload_folder=current_app.config["UPLOAD_FOLDER"]
    )
    if not student:
        return jsonify({"error": "Student record not found"}), 404

    return jsonify({
        "message": "Student updated successfully",
        "student": student.to_dict()
    }), 200

@student_bp.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    success = StudentService.delete_student(student_id, current_app.config["UPLOAD_FOLDER"])
    if not success:
        return jsonify({"error": "Unable to delete student"}), 400
    return jsonify({"message": "Student deleted successfully"}), 200

@student_bp.route("/api/student/profile", methods=["GET"])
@student_required
def get_student_profile():
    student_id = session.get("student_id")
    student = StudentService.get_student_by_id(student_id)
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    return jsonify(student.to_dict()), 200

@student_bp.route("/api/student/profile", methods=["PUT"])
@student_required
def update_student_profile():
    student_id = session.get("student_id")
    data = request.get_json() or request.form or {}

    # Restrict allowed keys to contact info ONLY
    contact_data = {
        k: v for k, v in data.items()
        if k in ["mobile", "altMobile", "email", "address", "city", "state", "pincode"]
    }

    student = StudentService.update_student(
        student_id=student_id,
        data=contact_data,
        files={},
        upload_folder=current_app.config["UPLOAD_FOLDER"]
    )
    return jsonify({
        "message": "Contact details updated successfully",
        "student": student.to_dict()
    }), 200
