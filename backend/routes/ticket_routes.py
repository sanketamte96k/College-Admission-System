from flask import Blueprint, request, jsonify, session
from models import db, Ticket
from utils import sanitize_input

ticket_bp = Blueprint("ticket", __name__)

@ticket_bp.route("/api/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json() or {}
    student_id = data.get("student_id") or session.get("student_id")
    subject = sanitize_input(data.get("subject"))
    category = sanitize_input(data.get("category", "General Inquiry"))
    message = sanitize_input(data.get("message"))

    if not student_id or not subject or not message:
        return jsonify({"error": "Student ID, Subject, and Message are required"}), 400

    ticket = Ticket(
        student_id=student_id,
        subject=subject,
        category=category,
        message=message,
        status="Open"
    )

    db.session.add(ticket)
    db.session.commit()

    return jsonify({
        "message": "Support ticket created successfully",
        "ticket": ticket.to_dict()
    }), 201

@ticket_bp.route("/api/tickets", methods=["GET"])
def get_tickets():
    student_id = request.args.get("student_id", type=int) or session.get("student_id")
    if student_id:
        tickets = Ticket.query.filter_by(student_id=student_id).order_by(Ticket.id.desc()).all()
    else:
        tickets = Ticket.query.order_by(Ticket.id.desc()).all()
    return jsonify([t.to_dict() for t in tickets]), 200

@ticket_bp.route("/api/tickets/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    data = request.get_json() or {}
    ticket = Ticket.query.get_or_404(ticket_id)

    if "response" in data: ticket.response = sanitize_input(data["response"])
    if "status" in data: ticket.status = sanitize_input(data["status"])

    db.session.commit()
    return jsonify({
        "message": "Ticket updated successfully",
        "ticket": ticket.to_dict()
    }), 200
