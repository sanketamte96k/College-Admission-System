from .auth_routes import auth_bp
from .student_routes import student_bp
from .analytics_routes import analytics_bp
from .ai_routes import ai_bp
from .admin_erp_routes import admin_erp_bp
from .payment_routes import payment_bp
from .ticket_routes import ticket_bp
from .attendance_routes import attendance_bp
from .department_routes import department_bp

__all__ = [
    "auth_bp",
    "student_bp",
    "analytics_bp",
    "ai_bp",
    "admin_erp_bp",
    "payment_bp",
    "ticket_bp",
    "attendance_bp",
    "department_bp"
]
