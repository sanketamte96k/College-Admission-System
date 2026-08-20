from datetime import datetime
from .database import db

class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    hod_name = db.Column(db.String(100), default="To Be Appointed")
    hod_email = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    total_seats = db.Column(db.Integer, default=60)
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "hod_name": self.hod_name or "To Be Appointed",
            "hod_email": self.hod_email or "",
            "description": self.description or "",
            "total_seats": self.total_seats or 60,
            "status": self.status or "Active",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
