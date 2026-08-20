from datetime import datetime
from .database import db

class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(100), nullable=False)
    academic_year = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    semester = db.Column(db.Integer, nullable=False)       # 1, 2, 3, 4, 5, 6, 7, 8
    credits = db.Column(db.Integer, default=4)
    subject_type = db.Column(db.String(50), default="Core")  # Core, Elective, Lab, Project, Other
    status = db.Column(db.String(20), default="Active")      # Active, Inactive
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "department": self.department,
            "program": self.program,
            "academic_year": self.academic_year,
            "semester": self.semester,
            "credits": self.credits or 4,
            "subject_type": self.subject_type or "Core",
            "status": self.status or "Active",
            "description": self.description or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
