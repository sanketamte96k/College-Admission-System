from datetime import datetime
from .database import db

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g. "B.Tech Computer Engineering"
    code = db.Column(db.String(20), unique=True, nullable=False)  # e.g. "BTECH-COMP"
    department = db.Column(db.String(100), nullable=False)  # e.g. "Computer Engineering"
    degree_type = db.Column(db.String(50), default="Undergraduate")  # e.g. "B.Tech"
    duration_years = db.Column(db.Integer, default=4)
    total_semesters = db.Column(db.Integer, default=8)
    total_credits = db.Column(db.Integer, default=160)
    status = db.Column(db.String(20), default="Active")
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "department": self.department,
            "degree_type": self.degree_type or "Undergraduate",
            "duration_years": self.duration_years or 4,
            "total_semesters": self.total_semesters or 8,
            "total_credits": self.total_credits or 160,
            "status": self.status or "Active",
            "description": self.description or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
