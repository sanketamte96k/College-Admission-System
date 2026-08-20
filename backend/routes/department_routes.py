from flask import Blueprint, request, jsonify, current_app
from services import DepartmentService
from utils import admin_required

department_bp = Blueprint("departments", __name__)

# ============================================================
# GET ALL DEPARTMENTS WITH SUMMARY STATS
# ============================================================
@department_bp.route("/api/departments", methods=["GET"])
def get_departments():
    search = request.args.get("search", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()

    try:
        data = DepartmentService.get_all_departments(search=search, status=status)
        return jsonify(data), 200
    except Exception as e:
        current_app.logger.exception("Error fetching departments")
        return jsonify({"error": str(e)}), 500


# ============================================================
# GET SINGLE DEPARTMENT DETAILS
# ============================================================
@department_bp.route("/api/departments/<int:dept_id>", methods=["GET"])
def get_department(dept_id):
    try:
        dept = DepartmentService.get_department_by_id(dept_id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404
        return jsonify(dept), 200
    except Exception as e:
        current_app.logger.exception("Error fetching department details")
        return jsonify({"error": str(e)}), 500


# ============================================================
# CREATE NEW DEPARTMENT
# ============================================================
@department_bp.route("/api/departments", methods=["POST"])
@admin_required
def create_department():
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        new_dept = DepartmentService.create_department(data)
        return jsonify({
            "message": f"Department '{new_dept.name}' created successfully!",
            "department": new_dept.to_dict()
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error creating department")
        return jsonify({"error": str(e)}), 500


# ============================================================
# UPDATE DEPARTMENT
# ============================================================
@department_bp.route("/api/departments/<int:dept_id>", methods=["PUT"])
@admin_required
def update_department(dept_id):
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        updated_dept = DepartmentService.update_department(dept_id, data)
        if not updated_dept:
            return jsonify({"error": "Department record not found"}), 404

        return jsonify({
            "message": f"Department '{updated_dept.name}' updated successfully!",
            "department": updated_dept.to_dict()
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error updating department")
        return jsonify({"error": str(e)}), 500


# ============================================================
# DELETE DEPARTMENT (SAFE DELETION CHECK)
# ============================================================
@department_bp.route("/api/departments/<int:dept_id>", methods=["DELETE"])
@admin_required
def delete_department(dept_id):
    try:
        success, message = DepartmentService.delete_department(dept_id)
        if not success:
            return jsonify({"error": message}), 400

        return jsonify({"message": message}), 200
    except Exception as e:
        current_app.logger.exception("Error deleting department")
        return jsonify({"error": str(e)}), 500
