from datetime import datetime
from flask import Blueprint, jsonify, request, session
from services import SettingService
from utils import admin_required

setting_bp = Blueprint("setting", __name__, url_prefix="/api/settings")

@setting_bp.route("", methods=["GET"])
def get_settings():
    """Retrieve all application and system configuration settings."""
    try:
        data = SettingService.get_all_settings()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve settings: {str(e)}"}), 500


@setting_bp.route("/<group>", methods=["PUT"])
@admin_required
def update_group_settings(group):
    """Update settings by category group (Admin only)."""
    try:
        payload = request.get_json() or {}
        updated = SettingService.update_settings_group(group, payload)
        return jsonify({
            "message": f"Settings for '{group}' saved successfully.",
            "settings": updated
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to save settings: {str(e)}"}), 500


@setting_bp.route("/academic-years", methods=["GET"])
def get_academic_years():
    """Retrieve list of all registered campus academic years."""
    try:
        years = SettingService.get_academic_years()
        return jsonify(years), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch academic years: {str(e)}"}), 500


@setting_bp.route("/academic-years", methods=["POST"])
@admin_required
def create_academic_year():
    """Create a new campus academic year (Admin only)."""
    try:
        data = request.get_json() or {}
        year_name = data.get("year_name")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        new_year = SettingService.create_academic_year(year_name, start_date, end_date)
        return jsonify({
            "message": f"Academic year '{year_name}' created successfully.",
            "academic_year": new_year
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create academic year: {str(e)}"}), 500


@setting_bp.route("/academic-years/<int:year_id>/set-active", methods=["POST"])
@admin_required
def set_active_academic_year(year_id):
    """Set active campus academic year (Admin only)."""
    try:
        updated = SettingService.set_active_academic_year(year_id)
        return jsonify({
            "message": f"Academic year '{updated['year_name']}' is now set as the ACTIVE campus academic year.",
            "academic_year": updated
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to activate academic year: {str(e)}"}), 500


@setting_bp.route("/academic-years/<int:year_id>/close", methods=["POST"])
@admin_required
def close_academic_year(year_id):
    """Close an academic year (Admin only)."""
    try:
        updated = SettingService.close_academic_year(year_id)
        return jsonify({
            "message": f"Academic year '{updated['year_name']}' closed successfully.",
            "academic_year": updated
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to close academic year: {str(e)}"}), 500


@setting_bp.route("/profile", methods=["GET"])
def get_user_profile():
    """Retrieve logged in user profile."""
    try:
        admin_id = session.get("admin_id")
        if not admin_id:
            return jsonify({"error": "Unauthorized session."}), 401
        
        from models import Admin
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({"error": "Admin user not found."}), 444
            
        profile_data = admin.to_dict()
        profile_data["role"] = "Super Administrator"
        profile_data["last_login"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        return jsonify(profile_data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch profile: {str(e)}"}), 500


@setting_bp.route("/profile", methods=["PUT"])
def update_user_profile():
    """Update current user profile."""
    try:
        admin_id = session.get("admin_id")
        if not admin_id:
            return jsonify({"error": "Unauthorized session."}), 401

        data = request.get_json() or {}
        updated_profile = SettingService.update_user_profile(admin_id, data)
        return jsonify({
            "message": "User profile updated successfully.",
            "profile": updated_profile
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update profile: {str(e)}"}), 500


@setting_bp.route("/change-password", methods=["POST"])
def change_password():
    """Change current user password."""
    try:
        admin_id = session.get("admin_id")
        if not admin_id:
            return jsonify({"error": "Unauthorized session."}), 401

        data = request.get_json() or {}
        curr_pass = data.get("current_password")
        new_pass = data.get("new_password")
        confirm_pass = data.get("confirm_password")

        res = SettingService.change_user_password(admin_id, curr_pass, new_pass, confirm_pass)
        return jsonify(res), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to change password: {str(e)}"}), 500


@setting_bp.route("/maintenance", methods=["GET"])
@admin_required
def get_maintenance_status():
    """Retrieve system status and database health info (Admin only)."""
    try:
        status = SettingService.get_maintenance_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch maintenance status: {str(e)}"}), 500
