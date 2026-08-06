from flask import Blueprint, request, jsonify
from services import AIService, StudentService

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/api/ai/chatbot", methods=["POST"])
def ai_chatbot():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    reply = AIService.chatbot_reply(message)
    return jsonify({"reply": reply}), 200

@ai_bp.route("/api/ai/check-eligibility", methods=["POST"])
def check_eligibility():
    data = request.get_json() or {}
    try:
        perc_10 = float(data.get("percentage10", 0))
        perc_12 = float(data.get("percentage12", 0))
        entrance_score = float(data.get("entranceScore", 0))
        department = str(data.get("department", "Computer Engineering"))

        res = AIService.check_eligibility(perc_10, perc_12, entrance_score, department)
        return jsonify(res), 200
    except ValueError:
        return jsonify({"error": "Invalid numerical scores provided"}), 400

@ai_bp.route("/api/ai/predict-admission", methods=["POST"])
def predict_admission():
    data = request.get_json() or {}
    try:
        perc_12 = float(data.get("percentage12", 0))
        entrance_score = float(data.get("entranceScore", 0))
        department = str(data.get("department", "Computer Engineering"))

        res = AIService.predict_admission_chances(perc_12, entrance_score, department)
        return jsonify(res), 200
    except ValueError:
        return jsonify({"error": "Invalid numerical scores provided"}), 400

@ai_bp.route("/api/ai/verify-documents/<int:student_id>", methods=["GET"])
def verify_documents(student_id):
    student = StudentService.get_student_by_id(student_id)
    if not student:
        return jsonify({"error": "Student record not found"}), 404

    res = AIService.verify_documents(student.to_dict())
    return jsonify(res), 200
