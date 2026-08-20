from flask import Blueprint, request, jsonify, current_app
from services import CourseService
from utils import admin_required

course_bp = Blueprint("courses", __name__)

# ============================================================
# GET CURRICULUM & COURSES LIST
# ============================================================
@course_bp.route("/api/courses", methods=["GET"])
def get_curriculum():
    department = request.args.get("department", "", type=str).strip()
    program = request.args.get("program", "", type=str).strip()
    academic_year = request.args.get("academic_year", "", type=str).strip()
    semester = request.args.get("semester", "", type=str).strip()
    search = request.args.get("search", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()

    try:
        data = CourseService.get_curriculum(
            department=department,
            program=program,
            academic_year=academic_year,
            semester=semester,
            search=search,
            status=status
        )
        return jsonify(data), 200
    except Exception as e:
        current_app.logger.exception("Error fetching curriculum data")
        return jsonify({"error": str(e)}), 500


@course_bp.route("/api/courses/list", methods=["GET"])
def get_courses_list():
    department = request.args.get("department", "", type=str).strip()
    search = request.args.get("search", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()

    try:
        courses = CourseService.get_all_courses(department=department, search=search, status=status)
        return jsonify(courses), 200
    except Exception as e:
        current_app.logger.exception("Error fetching course programs list")
        return jsonify({"error": str(e)}), 500


@course_bp.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    try:
        course = CourseService.get_course_by_id(course_id)
        if not course:
            return jsonify({"error": "Course program not found"}), 404
        return jsonify(course), 200
    except Exception as e:
        current_app.logger.exception("Error fetching course details")
        return jsonify({"error": str(e)}), 500


@course_bp.route("/api/courses", methods=["POST"])
@admin_required
def create_course():
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        new_course = CourseService.create_course(data)
        return jsonify({
            "message": f"Program '{new_course.name}' created successfully!",
            "course": new_course.to_dict()
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error creating course program")
        return jsonify({"error": str(e)}), 500


@course_bp.route("/api/courses/<int:course_id>", methods=["PUT"])
@admin_required
def update_course(course_id):
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        updated = CourseService.update_course(course_id, data)
        if not updated:
            return jsonify({"error": "Course program not found"}), 404
        return jsonify({
            "message": f"Program '{updated.name}' updated successfully!",
            "course": updated.to_dict()
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error updating course program")
        return jsonify({"error": str(e)}), 500


@course_bp.route("/api/courses/<int:course_id>", methods=["DELETE"])
@admin_required
def delete_course(course_id):
    try:
        success, message = CourseService.delete_course(course_id)
        if not success:
            return jsonify({"error": message}), 400
        return jsonify({"message": message}), 200
    except Exception as e:
        current_app.logger.exception("Error deleting course program")
        return jsonify({"error": str(e)}), 500


# ============================================================
# SUBJECT ENDPOINTS
# ============================================================

@course_bp.route("/api/subjects/<int:subject_id>", methods=["GET"])
def get_subject(subject_id):
    try:
        sub = CourseService.get_subject_by_id(subject_id)
        if not sub:
            return jsonify({"error": "Subject not found"}), 404
        return jsonify(sub), 200
    except Exception as e:
        current_app.logger.exception("Error fetching subject details")
        return jsonify({"error": str(e)}), 500


@course_bp.route("/api/subjects", methods=["POST"])
@admin_required
def create_subject():
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        new_sub = CourseService.create_subject(data)
        return jsonify({
            "message": f"Subject '{new_sub.name}' ({new_sub.code}) added successfully!",
            "subject": new_sub.to_dict()
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error adding subject")
        return jsonify({"error": str(e)}), 500


@course_bp.route("/api/subjects/<int:subject_id>", methods=["PUT"])
@admin_required
def update_subject(subject_id):
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        updated = CourseService.update_subject(subject_id, data)
        if not updated:
            return jsonify({"error": "Subject not found"}), 404
        return jsonify({
            "message": f"Subject '{updated.name}' updated successfully!",
            "subject": updated.to_dict()
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error updating subject")
        return jsonify({"error": str(e)}), 500


@course_bp.route("/api/subjects/<int:subject_id>", methods=["DELETE"])
@admin_required
def delete_subject(subject_id):
    try:
        success, message = CourseService.delete_subject(subject_id)
        if not success:
            return jsonify({"error": message}), 400
        return jsonify({"message": message}), 200
    except Exception as e:
        current_app.logger.exception("Error deleting subject")
        return jsonify({"error": str(e)}), 500
