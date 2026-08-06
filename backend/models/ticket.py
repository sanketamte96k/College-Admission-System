from datetime import datetime
from .database import db

class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), default="General Inquiry")
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Open")  # Open, In Progress, Resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "subject": self.subject,
            "category": self.category,
            "message": self.message,
            "response": self.response or "",
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }
