from flask import Blueprint, request, jsonify, session
from services import PaymentService

payment_bp = Blueprint("payment", __name__)

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
