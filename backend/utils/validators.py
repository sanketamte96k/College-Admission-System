import re
import html
from flask import request, jsonify

login_attempts = {}

def sanitize_input(text):
    if not text:
        return ""
    text_str = str(text)
    sanitized = html.escape(text_str)
    return sanitized.strip()

def validate_email(email):
    if not email:
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email.strip()))

def validate_mobile(mobile):
    if not mobile:
        return False
    pattern = r"^\+?\d{10,15}$"
    return bool(re.match(pattern, mobile.strip()))

def rate_limit(max_attempts=10, window_seconds=60):
    """Simple IP-based brute force rate limiting decorator"""
    def decorator(f):
        from functools import wraps
        from datetime import datetime

        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr or "127.0.0.1"
            now = datetime.utcnow().timestamp()

            attempts = login_attempts.get(ip, [])
            attempts = [t for t in attempts if now - t < window_seconds]
            login_attempts[ip] = attempts

            if len(attempts) >= max_attempts:
                return jsonify({
                    "error": "Too many requests. Brute force protection activated. Please try again later."
                }), 429

            login_attempts[ip].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator
