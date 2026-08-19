from datetime import datetime, date
from .database import db

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="Present")  # 'Present' or 'Absent'
    remarks = db.Column(db.Text, nullable=True)
    marked_by = db.Column(db.String(100), default="admin", nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("student_id", "attendance_date", name="uq_student_attendance_date"),
    )

    def to_dict(self):
        date_str = self.attendance_date.strftime("%Y-%m-%d") if isinstance(self.attendance_date, (date, datetime)) else str(self.attendance_date)
        return {
            "id": self.id,
            "student_id": self.student_id,
            "attendance_date": date_str,
            "status": self.status,
            "remarks": self.remarks or "",
            "marked_by": self.marked_by or "admin",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else ""
        }
