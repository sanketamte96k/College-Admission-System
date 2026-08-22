from flask import Blueprint, request, jsonify, current_app, session
from services import NoticeService
from utils import admin_required

notice_bp = Blueprint("notices", __name__)

# ============================================================
# GET ALL NOTICES (ADMIN / MANAGEMENT LISTING WITH FILTERS)
# ============================================================
@notice_bp.route("/api/notices", methods=["GET"])
def get_notices():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    search = request.args.get("search", "", type=str).strip()
    category = request.args.get("category", "", type=str).strip()
    priority = request.args.get("priority", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()
    audience = request.args.get("audience", "", type=str).strip()
    department = request.args.get("department", "", type=str).strip() or request.args.get("dept", "", type=str).strip()
    academic_year = request.args.get("academic_year", "", type=str).strip()

    is_pinned_param = request.args.get("is_pinned", None)
    is_pinned = None
    if is_pinned_param is not None and is_pinned_param != "":
        is_pinned = is_pinned_param.lower() in ("true", "1", "yes")

    try:
        result = NoticeService.get_all_notices(
            page=page,
            limit=limit,
            search=search,
            category=category,
            priority=priority,
            status=status,
            audience=audience,
            department=department,
            academic_year=academic_year,
            is_pinned=is_pinned
        )
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.exception("Error fetching notices")
        return jsonify({"error": str(e)}), 500

# ============================================================
# GET ACTIVE PUBLIC / STUDENT NOTICES
# ============================================================
@notice_bp.route("/api/notices/active", methods=["GET"])
def get_active_notices():
    audience = request.args.get("audience", None, type=str)
    department = request.args.get("department", None, type=str)
    course = request.args.get("course", None, type=str)
    academic_year = request.args.get("academic_year", None, type=str)
    limit = request.args.get("limit", 10, type=int)

    try:
        notices = NoticeService.get_active_notices(
            audience=audience,
            department=department,
            course=course,
            academic_year=academic_year,
            limit=limit
        )
        return jsonify(notices), 200
    except Exception as e:
        current_app.logger.exception("Error fetching active notices")
        return jsonify({"error": str(e)}), 500

# ============================================================
# GET NOTICE KPI STATS
# ============================================================
@notice_bp.route("/api/notices/stats", methods=["GET"])
def get_notice_stats():
    try:
        stats = NoticeService.get_notice_kpi_stats()
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.exception("Error fetching notice stats")
        return jsonify({"error": str(e)}), 500

# ============================================================
# GET SINGLE NOTICE BY ID
# ============================================================
@notice_bp.route("/api/notices/<int:notice_id>", methods=["GET"])
def get_notice(notice_id):
    try:
        notice = NoticeService.get_notice_by_id(notice_id)
        if not notice:
            return jsonify({"error": f"Notice with ID {notice_id} not found."}), 404
        return jsonify(notice.to_dict()), 200
    except Exception as e:
        current_app.logger.exception("Error fetching notice detail")
        return jsonify({"error": str(e)}), 500

# ============================================================
# CREATE NOTICE (ADMIN ONLY)
# ============================================================
@notice_bp.route("/api/notices", methods=["POST"])
@admin_required
def create_notice():
    data = request.get_json() or {}
    created_by = session.get("admin_username") or "Admin"
    try:
        notice = NoticeService.create_notice(data, created_by=created_by)
        return jsonify({
            "message": "Notice created successfully.",
            "notice": notice.to_dict()
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error creating notice")
        return jsonify({"error": str(e)}), 500

# ============================================================
# UPDATE NOTICE (ADMIN ONLY)
# ============================================================
@notice_bp.route("/api/notices/<int:notice_id>", methods=["PUT"])
@admin_required
def update_notice(notice_id):
    data = request.get_json() or {}
    try:
        notice = NoticeService.update_notice(notice_id, data)
        return jsonify({
            "message": "Notice updated successfully.",
            "notice": notice.to_dict()
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error updating notice")
        return jsonify({"error": str(e)}), 500

# ============================================================
# DELETE NOTICE (ADMIN ONLY)
# ============================================================
@notice_bp.route("/api/notices/<int:notice_id>", methods=["DELETE"])
@admin_required
def delete_notice(notice_id):
    try:
        NoticeService.delete_notice(notice_id)
        return jsonify({"message": "Notice deleted successfully."}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        current_app.logger.exception("Error deleting notice")
        return jsonify({"error": str(e)}), 500

# ============================================================
# PUBLISH NOTICE (ADMIN ONLY)
# ============================================================
@notice_bp.route("/api/notices/<int:notice_id>/publish", methods=["POST"])
@admin_required
def publish_notice(notice_id):
    try:
        notice = NoticeService.publish_notice(notice_id)
        return jsonify({
            "message": "Notice published successfully.",
            "notice": notice.to_dict()
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        current_app.logger.exception("Error publishing notice")
        return jsonify({"error": str(e)}), 500

# ============================================================
# ARCHIVE NOTICE (ADMIN ONLY)
# ============================================================
@notice_bp.route("/api/notices/<int:notice_id>/archive", methods=["POST"])
@admin_required
def archive_notice(notice_id):
    try:
        notice = NoticeService.archive_notice(notice_id)
        return jsonify({
            "message": "Notice archived successfully.",
            "notice": notice.to_dict()
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        current_app.logger.exception("Error archiving notice")
        return jsonify({"error": str(e)}), 500

# ============================================================
# TOGGLE PIN NOTICE (ADMIN ONLY)
# ============================================================
@notice_bp.route("/api/notices/<int:notice_id>/pin", methods=["POST"])
@admin_required
def toggle_pin_notice(notice_id):
    try:
        notice = NoticeService.toggle_pin_notice(notice_id)
        status_txt = "pinned" if notice.is_pinned else "unpinned"
        return jsonify({
            "message": f"Notice {status_txt} successfully.",
            "notice": notice.to_dict()
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        current_app.logger.exception("Error toggling notice pin")
        return jsonify({"error": str(e)}), 500
