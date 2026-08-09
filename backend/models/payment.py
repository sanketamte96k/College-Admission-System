from datetime import datetime
from .database import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    fee_type = db.Column(db.String(100), default="Tuition Fee", nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default="UPI / Online", nullable=False)
    payment_mode = db.Column(db.String(50), default="UPI / Online", nullable=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default="SUCCESS", nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(db.String(100), default="admin", nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        method = self.payment_method or self.payment_mode or "UPI / Online"
        date_str = (
            self.payment_date.strftime("%Y-%m-%d %H:%M:%S")
            if self.payment_date
            else (self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "")
        )
        return {
            "id": self.id,
            "student_id": self.student_id,
            "fee_type": self.fee_type or "Tuition Fee",
            "amount": float(self.amount or 0.0),
            "payment_method": method,
            "payment_mode": method,
            "payment_date": date_str,
            "transaction_id": self.transaction_id,
            "status": self.status or "SUCCESS",
            "remarks": self.remarks or "",
            "recorded_by": self.recorded_by or "admin",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

