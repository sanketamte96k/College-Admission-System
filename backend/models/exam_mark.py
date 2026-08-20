from datetime import datetime
from .database import db

class ExamMark(db.Model):
    __tablename__ = "exam_marks"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("examinations.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    roll_no = db.Column(db.String(50), nullable=True)
    marks_obtained = db.Column(db.Float, nullable=True)
    is_absent = db.Column(db.Boolean, default=False)
    percentage = db.Column(db.Float, nullable=True)
    grade = db.Column(db.String(10), nullable=True)
    result_status = db.Column(db.String(20), default="Pending")  # Pass, Fail, Absent, Pending
    status = db.Column(db.String(20), default="Draft")           # Draft, Evaluated, Published
    remarks = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to student
    student = db.relationship("Student", backref="exam_marks", lazy=True)

    def to_dict(self):
        student_dict = self.student.to_dict() if self.student else {}
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "student_id": self.student_id,
            "roll_no": self.roll_no or student_dict.get("enrollmentNo") or f"STU-{self.student_id:04d}",
            "student_name": student_dict.get("fullName", "Unknown Student"),
            "application_no": student_dict.get("applicationNo", ""),
            "department": student_dict.get("department", ""),
            "course": student_dict.get("course", ""),
            "academic_year": student_dict.get("academic_year", 1),
            "marks_obtained": self.marks_obtained,
            "is_absent": self.is_absent,
            "percentage": round(self.percentage, 2) if self.percentage is not None else None,
            "grade": self.grade or "-",
            "result_status": self.result_status or ("Absent" if self.is_absent else "Pending"),
            "status": self.status or "Draft",
            "remarks": self.remarks or "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }
