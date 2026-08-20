from datetime import datetime
from .database import db

class Examination(db.Model):
    __tablename__ = "examinations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(100), nullable=False)
    academic_year = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    semester = db.Column(db.Integer, nullable=False)       # 1 to 8
    subject_code = db.Column(db.String(20), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False, default="End Semester")  # Mid Semester, Internal Assessment, End Semester, Practical, Viva, Unit Test, Supplementary, Other
    exam_date = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD
    start_time = db.Column(db.String(20), default="10:00 AM")
    end_time = db.Column(db.String(20), default="01:00 PM")
    max_marks = db.Column(db.Integer, default=100)
    passing_marks = db.Column(db.Integer, default=40)
    instructions = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="Scheduled")  # Draft, Scheduled, Ongoing, Completed, Results Pending, Published, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to marks
    marks = db.relationship("ExamMark", backref="examination", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "program": self.program,
            "academic_year": self.academic_year,
            "semester": self.semester,
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "exam_type": self.exam_type or "End Semester",
            "exam_date": self.exam_date,
            "start_time": self.start_time or "10:00 AM",
            "end_time": self.end_time or "01:00 PM",
            "max_marks": self.max_marks or 100,
            "passing_marks": self.passing_marks or 40,
            "instructions": self.instructions or "",
            "status": self.status or "Scheduled",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
