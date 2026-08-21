from flask import Blueprint, jsonify, request, send_file, Response, current_app
from services import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/api/dashboard", methods=["GET"])
def get_dashboard_analytics():
    try:
        metrics = AnalyticsService.get_dashboard_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        current_app.logger.exception("Error fetching dashboard analytics")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/api/analytics/reports", methods=["GET"])
def get_reports_analytics():
    try:
        filters = {
            "academic_year": request.args.get("academic_year", "all"),
            "semester": request.args.get("semester", "all"),
            "department": request.args.get("department", "all"),
            "program": request.args.get("program", "all"),
            "start_date": request.args.get("start_date", ""),
            "end_date": request.args.get("end_date", "")
        }
        data = AnalyticsService.get_reports_analytics(filters)
        return jsonify(data), 200
    except Exception as e:
        current_app.logger.exception("Error fetching reports analytics")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/api/analytics/export/pdf", methods=["GET"])
def export_reports_pdf():
    try:
        report_type = request.args.get("report_type", "general")
        filters = {
            "academic_year": request.args.get("academic_year", "all"),
            "semester": request.args.get("semester", "all"),
            "department": request.args.get("department", "all"),
            "program": request.args.get("program", "all"),
            "start_date": request.args.get("start_date", ""),
            "end_date": request.args.get("end_date", "")
        }
        pdf_buf = AnalyticsService.generate_pdf_report(report_type, filters)
        filename = f"Zeal_ERP_{report_type.title()}_Report.pdf"
        return send_file(
            pdf_buf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        current_app.logger.exception("Error generating PDF report")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/api/analytics/export/csv", methods=["GET"])
def export_reports_csv():
    try:
        report_type = request.args.get("report_type", "general")
        filters = {
            "academic_year": request.args.get("academic_year", "all"),
            "semester": request.args.get("semester", "all"),
            "department": request.args.get("department", "all"),
            "program": request.args.get("program", "all"),
            "start_date": request.args.get("start_date", ""),
            "end_date": request.args.get("end_date", "")
        }
        csv_data = AnalyticsService.generate_csv_report(report_type, filters)
        filename = f"Zeal_ERP_{report_type.title()}_Report.csv"
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except Exception as e:
        current_app.logger.exception("Error generating CSV report")
        return jsonify({"error": str(e)}), 500
