from datetime import datetime
from .database import db

class SeatMatrix(db.Model):
    __tablename__ = "seat_matrix"

    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), unique=True, nullable=False)
    total_seats = db.Column(db.Integer, default=60)
    filled_seats = db.Column(db.Integer, default=0)
    cutoff_score = db.Column(db.Float, default=70.0)

    def to_dict(self):
        return {
            "id": self.id,
            "department": self.department,
            "total_seats": self.total_seats,
            "filled_seats": self.filled_seats,
            "vacant_seats": max(0, self.total_seats - self.filled_seats),
            "cutoff_score": self.cutoff_score
        }
