from flask import Blueprint, request, jsonify, session, current_app
from services import PaymentService
from utils import admin_required, student_required

payment_bp = Blueprint("payment", __name__)


# ============================================================
# ADMIN OR AUTHORIZED STUDENT: GET STUDENT FEE SUMMARY
# ============================================================
@payment_bp.route("/api/students/<int:student_id>/fees", methods=["GET"])
def get_student_fees(student_id):
    is_admin = bool(session.get("admin_id"))
    current_student_id = session.get("student_id")

    # Security check: Admin can access any student, student can only access themselves
    if not is_admin:
        if not current_student_id:
            return jsonify({"error": "Authentication required", "redirect": "/login.html"}), 401
        if int(current_student_id) != int(student_id):
            return jsonify({"error": "Forbidden: You cannot access another student's fee details"}), 403

    summary = PaymentService.get_student_fee_summary(student_id)
    if not summary:
        return jsonify({"error": f"Student #{student_id} not found"}), 404

    return jsonify(summary), 200


# ============================================================
# ADMIN OR AUTHORIZED STUDENT: GET STUDENT PAYMENT HISTORY
# ============================================================
@payment_bp.route("/api/students/<int:student_id>/payments", methods=["GET"])
def get_student_payments(student_id):
    is_admin = bool(session.get("admin_id"))
    current_student_id = session.get("student_id")

    if not is_admin:
        if not current_student_id:
            return jsonify({"error": "Authentication required", "redirect": "/login.html"}), 401
        if int(current_student_id) != int(student_id):
            return jsonify({"error": "Forbidden: You cannot access another student's payments"}), 403

    payments = PaymentService.get_payment_history(student_id)
    return jsonify(payments), 200


# ============================================================
# ADMIN ONLY: RECORD A FEE PAYMENT
# ============================================================
@payment_bp.route("/api/students/<int:student_id>/payments", methods=["POST"])
@admin_required
def record_student_payment(student_id):
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    amount = data.get("amount")
    fee_type = data.get("fee_type") or data.get("feeType") or "Tuition Fee"
    payment_method = data.get("payment_method") or data.get("paymentMethod") or data.get("payment_mode") or "UPI"
    transaction_id = data.get("transaction_id") or data.get("transactionId") or data.get("reference_id") or None
    remarks = data.get("remarks") or data.get("notes") or ""
    payment_date = data.get("payment_date") or data.get("paymentDate") or None
    admin_username = session.get("admin_username") or "admin"

    if amount is None or str(amount).strip() == "":
        return jsonify({"error": "Payment amount is required."}), 400

    result, message = PaymentService.record_payment(
        student_id=student_id,
        amount=amount,
        fee_type=fee_type,
        payment_method=payment_method,
        transaction_id=transaction_id,
        remarks=remarks,
        admin_username=admin_username,
        payment_date=payment_date
    )

    if not result:
        return jsonify({"error": message}), 400

    return jsonify({
        "success": True,
        "message": message,
        "payment": result["payment"],
        "summary": result["summary"]
    }), 201


# ============================================================
# LOGGED-IN STUDENT PORTAL ENDPOINTS
# ============================================================
@payment_bp.route("/api/student/fees", methods=["GET"])
@student_required
def get_logged_in_student_fees():
    student_id = session.get("student_id")
    summary = PaymentService.get_student_fee_summary(student_id)
    if not summary:
        return jsonify({"error": "Student record not found"}), 404
    return jsonify(summary), 200


@payment_bp.route("/api/student/payments", methods=["GET"])
@student_required
def get_logged_in_student_payments():
    student_id = session.get("student_id")
    payments = PaymentService.get_payment_history(student_id)
    return jsonify(payments), 200


# ============================================================
# LEGACY COMPATIBILITY ROUTES
# ============================================================
@payment_bp.route("/api/payment/process", methods=["POST"])
def process_payment():
    data = request.get_json() or {}
    student_id = data.get("student_id") or session.get("student_id")
    amount = float(data.get("amount", 95000.0))
    payment_mode = data.get("payment_mode", "UPI / Online")

    if not student_id:
        return jsonify({"error": "Student ID is required"}), 400

    txn, message = PaymentService.process_payment(student_id, amount, payment_mode)
    if not txn:
        return jsonify({"error": message}), 400

    return jsonify({
        "message": message,
        "transaction": txn
    }), 201


@payment_bp.route("/api/payment/history/<int:student_id>", methods=["GET"])
def payment_history(student_id):
    history = PaymentService.get_payment_history(student_id)
    return jsonify(history), 200

