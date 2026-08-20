from flask import Blueprint, request, jsonify, current_app
from services import ExaminationService
from utils import admin_required

examination_bp = Blueprint("examinations", __name__)

@examination_bp.route("/api/examinations", methods=["GET"])
def get_examinations():
    department = request.args.get("department", "", type=str).strip()
    program = request.args.get("program", "", type=str).strip()
    academic_year = request.args.get("academic_year", "", type=str).strip()
    semester = request.args.get("semester", "", type=str).strip()
    exam_type = request.args.get("exam_type", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()
    search = request.args.get("search", "", type=str).strip()

    try:
        data = ExaminationService.get_all_examinations(
            department=department,
            program=program,
            academic_year=academic_year,
            semester=semester,
            exam_type=exam_type,
            status=status,
            search=search
        )
        return jsonify(data), 200
    except Exception as e:
        current_app.logger.exception("Error fetching examinations list")
        return jsonify({"error": str(e)}), 500


@examination_bp.route("/api/examinations/schedule", methods=["GET"])
def get_exam_schedule():
    department = request.args.get("department", "", type=str).strip()
    program = request.args.get("program", "", type=str).strip()
    academic_year = request.args.get("academic_year", "", type=str).strip()
    semester = request.args.get("semester", "", type=str).strip()

    try:
        schedule = ExaminationService.get_exam_schedule(
            department=department,
            program=program,
            academic_year=academic_year,
            semester=semester
        )
        return jsonify(schedule), 200
    except Exception as e:
        current_app.logger.exception("Error fetching exam schedule")
        return jsonify({"error": str(e)}), 500


@examination_bp.route("/api/examinations/<int:exam_id>", methods=["GET"])
def get_examination(exam_id):
    try:
        exam = ExaminationService.get_examination_by_id(exam_id)
        if not exam:
            return jsonify({"error": "Examination record not found"}), 404
        return jsonify(exam), 200
    except Exception as e:
        current_app.logger.exception("Error fetching examination details")
        return jsonify({"error": str(e)}), 500


@examination_bp.route("/api/examinations", methods=["POST"])
@admin_required
def create_examination():
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        new_exam = ExaminationService.create_examination(data)
        return jsonify({
            "message": f"Examination '{new_exam.name}' created successfully!",
            "examination": new_exam.to_dict()
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error creating examination")
        return jsonify({"error": str(e)}), 500


@examination_bp.route("/api/examinations/<int:exam_id>", methods=["PUT"])
@admin_required
def update_examination(exam_id):
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        updated = ExaminationService.update_examination(exam_id, data)
        if not updated:
            return jsonify({"error": "Examination record not found"}), 404
        return jsonify({
            "message": f"Examination '{updated.name}' updated successfully!",
            "examination": updated.to_dict()
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error updating examination")
        return jsonify({"error": str(e)}), 500


@examination_bp.route("/api/examinations/<int:exam_id>", methods=["DELETE"])
@admin_required
def delete_examination(exam_id):
    try:
        success, message = ExaminationService.delete_examination(exam_id)
        if not success:
            return jsonify({"error": message}), 400
        return jsonify({"message": message}), 200
    except Exception as e:
        current_app.logger.exception("Error deleting examination")
        return jsonify({"error": str(e)}), 500


# ============================================================
# MARKS / EVALUATION ENDPOINTS
# ============================================================

@examination_bp.route("/api/examinations/<int:exam_id>/marks", methods=["GET"])
def get_examination_marks(exam_id):
    try:
        data = ExaminationService.get_examination_marks(exam_id)
        if not data:
            return jsonify({"error": "Examination not found"}), 404
        return jsonify(data), 200
    except Exception as e:
        current_app.logger.exception("Error fetching exam marks")
        return jsonify({"error": str(e)}), 500


@examination_bp.route("/api/examinations/<int:exam_id>/marks", methods=["POST", "PUT"])
@admin_required
def save_examination_marks(exam_id):
    data = request.get_json(silent=True) or {}
    marks_list = data.get("marks", [])

    if not isinstance(marks_list, list):
        return jsonify({"error": "Payload must contain a 'marks' list."}), 400

    try:
        success, message = ExaminationService.save_examination_marks(exam_id, marks_list)
        if not success:
            return jsonify({"error": message}), 400
        return jsonify({"message": message}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error saving examination marks")
        return jsonify({"error": str(e)}), 500


@examination_bp.route("/api/examinations/<int:exam_id>/publish", methods=["POST"])
@admin_required
def publish_results(exam_id):
    try:
        success, message = ExaminationService.publish_results(exam_id)
        if not success:
            return jsonify({"error": message}), 400
        return jsonify({"message": message}), 200
    except Exception as e:
        current_app.logger.exception("Error publishing examination results")
        return jsonify({"error": str(e)}), 500


@examination_bp.route("/api/examinations/<int:exam_id>/unpublish", methods=["POST"])
@admin_required
def unpublish_results(exam_id):
    try:
        success, message = ExaminationService.unpublish_results(exam_id)
        if not success:
            return jsonify({"error": message}), 400
        return jsonify({"message": message}), 200
    except Exception as e:
        current_app.logger.exception("Error unpublishing examination results")
        return jsonify({"error": str(e)}), 500
