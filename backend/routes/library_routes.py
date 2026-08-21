import csv
from io import StringIO
from flask import Blueprint, request, jsonify, send_file, current_app
from services import LibraryService
from utils import admin_required

library_bp = Blueprint("library", __name__)

# ============================================================
# LIBRARY DASHBOARD SUMMARY
# ============================================================
@library_bp.route("/api/library/dashboard", methods=["GET"])
def get_library_dashboard():
    try:
        summary = LibraryService.get_library_dashboard_summary()
        return jsonify(summary), 200
    except Exception as e:
        current_app.logger.exception("Error fetching library dashboard metrics")
        return jsonify({"error": str(e)}), 500


# ============================================================
# BOOKS INVENTORY CRUD
# ============================================================
@library_bp.route("/api/library/books", methods=["GET"])
def get_books():
    category = request.args.get("category", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()
    search = request.args.get("search", "", type=str).strip()

    try:
        books = LibraryService.get_books(category=category, status=status, search=search)
        return jsonify(books), 200
    except Exception as e:
        current_app.logger.exception("Error fetching library books catalog")
        return jsonify({"error": str(e)}), 500


@library_bp.route("/api/library/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    try:
        book = LibraryService.get_book_by_id(book_id)
        if not book:
            return jsonify({"error": "Book record not found."}), 404
        return jsonify(book), 200
    except Exception as e:
        current_app.logger.exception("Error fetching book details")
        return jsonify({"error": str(e)}), 500


@library_bp.route("/api/library/books", methods=["POST"])
@admin_required
def add_book():
    try:
        data = request.get_json() or {}
        success, msg, book_obj = LibraryService.add_book(data)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "book": book_obj}), 201
    except Exception as e:
        current_app.logger.exception("Error adding library book")
        return jsonify({"error": str(e)}), 500


@library_bp.route("/api/library/books/<int:book_id>", methods=["PUT"])
@admin_required
def update_book(book_id):
    try:
        data = request.get_json() or {}
        success, msg, book_obj = LibraryService.update_book(book_id, data)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "book": book_obj}), 200
    except Exception as e:
        current_app.logger.exception("Error updating library book")
        return jsonify({"error": str(e)}), 500


@library_bp.route("/api/library/books/<int:book_id>", methods=["DELETE"])
@admin_required
def delete_book(book_id):
    try:
        success, msg = LibraryService.delete_book(book_id)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg}), 200
    except Exception as e:
        current_app.logger.exception("Error deleting library book")
        return jsonify({"error": str(e)}), 500


# ============================================================
# LIBRARY MEMBERS LEDGER
# ============================================================
@library_bp.route("/api/library/members", methods=["GET"])
def get_members():
    department = request.args.get("department", "", type=str).strip()
    search = request.args.get("search", "", type=str).strip()
    only_eligible = request.args.get("only_eligible", "false").lower() == "true"

    try:
        members = LibraryService.get_members(department=department, search=search, only_eligible=only_eligible)
        return jsonify(members), 200
    except Exception as e:
        current_app.logger.exception("Error fetching library members list")
@library_bp.route("/api/library/verify-student/<path:zprn>", methods=["GET"])
def verify_student_zprn(zprn):
    try:
        success, msg, student_data = LibraryService.verify_student_by_zprn(zprn)
        if not success:
            return jsonify({"error": msg}), 404
        return jsonify({"message": msg, "student": student_data}), 200
    except Exception as e:
        current_app.logger.exception("Error verifying student ZPRN")
        return jsonify({"error": str(e)}), 500


# ============================================================
# ISSUE & RETURN WORKFLOW
# ============================================================
@library_bp.route("/api/library/issue", methods=["POST"])
@admin_required
def issue_book():
    try:
        data = request.get_json() or {}
        book_id = data.get("book_id")
        student_id = data.get("student_id")
        issue_date = data.get("issue_date")
        due_date = data.get("due_date")
        remarks = data.get("remarks", "")

        if not book_id or not student_id:
            return jsonify({"error": "book_id and student_id are required fields."}), 400

        success, msg, tx = LibraryService.issue_book(
            book_id=int(book_id),
            student_id=int(student_id),
            issue_date_str=issue_date,
            due_date_str=due_date,
            remarks=remarks
        )

        if not success:
            return jsonify({"error": msg}), 400

        return jsonify({"message": msg, "transaction": tx}), 201
    except Exception as e:
        current_app.logger.exception("Error issuing library book")
        return jsonify({"error": str(e)}), 500


@library_bp.route("/api/library/return/<int:transaction_id>", methods=["POST"])
@admin_required
def return_book(transaction_id):
    try:
        data = request.get_json() or {}
        return_date = data.get("return_date")
        fine_action = data.get("fine_status", "Pending")
        remarks = data.get("remarks", "")

        success, msg, tx = LibraryService.return_book(
            transaction_id=transaction_id,
            return_date_str=return_date,
            fine_action=fine_action,
            remarks=remarks
        )

        if not success:
            return jsonify({"error": msg}), 400

        return jsonify({"message": msg, "transaction": tx}), 200
    except Exception as e:
        current_app.logger.exception("Error returning library book")
        return jsonify({"error": str(e)}), 500


# ============================================================
# TRANSACTIONS & OVERDUE
# ============================================================
@library_bp.route("/api/library/transactions", methods=["GET"])
def get_transactions():
    status = request.args.get("status", "", type=str).strip()
    student_id = request.args.get("student_id", None, type=int)
    book_id = request.args.get("book_id", None, type=int)
    search = request.args.get("search", "", type=str).strip()

    try:
        txs = LibraryService.get_transactions(status=status, student_id=student_id, book_id=book_id, search=search)
        return jsonify(txs), 200
    except Exception as e:
        current_app.logger.exception("Error fetching library transactions log")
        return jsonify({"error": str(e)}), 500


@library_bp.route("/api/library/overdue", methods=["GET"])
def get_overdue():
    try:
        overdue_list = LibraryService.get_overdue_list()
        return jsonify(overdue_list), 200
    except Exception as e:
        current_app.logger.exception("Error fetching overdue books list")
        return jsonify({"error": str(e)}), 500


@library_bp.route("/api/library/fines/<int:transaction_id>", methods=["POST"])
@admin_required
def update_fine(transaction_id):
    try:
        data = request.get_json() or {}
        fine_status = data.get("fine_status", "Paid")
        success, msg = LibraryService.update_fine_status(transaction_id, fine_status)

        if not success:
            return jsonify({"error": msg}), 400

        return jsonify({"message": msg}), 200
    except Exception as e:
        current_app.logger.exception("Error updating library fine status")
        return jsonify({"error": str(e)}), 500


# ============================================================
# EXPORT REPORTS (PDF & CSV)
# ============================================================
@library_bp.route("/api/library/export/pdf", methods=["GET"])
def export_pdf_report():
    report_type = request.args.get("type", "inventory", type=str).strip()

    try:
        pdf_buffer, err = LibraryService.generate_pdf_library_report(report_type)
        if err:
            return jsonify({"error": err}), 400

        filename = f"Zeal_ERP_Library_{report_type.capitalize()}_Report.pdf"
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        current_app.logger.exception("Error exporting PDF library report")
        return jsonify({"error": str(e)}), 500


@library_bp.route("/api/library/export/csv", methods=["GET"])
def export_csv_report():
    report_type = request.args.get("type", "inventory", type=str).strip()

    try:
        output = StringIO()
        writer = csv.writer(output)

        if report_type == "overdue":
            data = LibraryService.get_overdue_list()
            writer.writerow(["Transaction ID", "Student ID", "Student Name", "Roll Number", "Book Title", "ISBN", "Issue Date", "Due Date", "Overdue Days", "Fine Amount (INR)", "Fine Status"])
            for row in data:
                writer.writerow([
                    row["id"], row["student_id"], row["student_name"], row["student_roll"],
                    row["book_title"], row["book_isbn"], row["issue_date"], row["due_date"],
                    row["overdue_days"], row["fine_amount"], row["fine_status"]
                ])
        elif report_type == "transactions":
            data = LibraryService.get_transactions()
            writer.writerow(["Transaction ID", "Student Name", "Book Title", "Issue Date", "Due Date", "Return Date", "Status", "Overdue Days", "Fine (INR)", "Fine Status"])
            for row in data:
                writer.writerow([
                    row["id"], row["student_name"], row["book_title"], row["issue_date"],
                    row["due_date"], row["return_date"], row["status"], row["overdue_days"],
                    row["fine_amount"], row["fine_status"]
                ])
        else:
            data = LibraryService.get_books()
            writer.writerow(["Book ID", "ISBN", "Title", "Author", "Category", "Publisher", "Edition", "Pub Year", "Total Qty", "Available Qty", "Location", "Status"])
            for row in data:
                writer.writerow([
                    row["id"], row["isbn"], row["title"], row["author"], row["category"],
                    row["publisher"], row["edition"], row["pub_year"], row["quantity"],
                    row["available_qty"], row["location"], row["status"]
                ])

        response_bytes = output.getvalue().encode("utf-8")
        filename = f"Zeal_ERP_Library_{report_type.capitalize()}_Export.csv"

        return send_file(
            BytesIO(response_bytes),
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        current_app.logger.exception("Error exporting CSV library report")
        return jsonify({"error": str(e)}), 500
