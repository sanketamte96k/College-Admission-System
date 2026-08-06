from functools import wraps
from flask import session, jsonify

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_id"):
            return jsonify({"error": "Unauthorized Admin Access", "redirect": "/login.html"}), 401
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("student_id"):
            return jsonify({"error": "Unauthorized Student Access", "redirect": "/student-login.html"}), 401
        return f(*args, **kwargs)
    return decorated_function
