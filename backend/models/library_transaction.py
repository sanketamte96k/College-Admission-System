from datetime import datetime, date
from .database import db

class LibraryTransaction(db.Model):
    __tablename__ = "library_transactions"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("library_books.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Issued")  # Issued, Returned, Overdue, Lost
    overdue_days = db.Column(db.Integer, nullable=False, default=0)
    fine_amount = db.Column(db.Float, nullable=False, default=0.0)
    fine_status = db.Column(db.String(30), nullable=False, default="None")  # None, Pending, Paid, Waived
    remarks = db.Column(db.Text, nullable=True)
    issued_by = db.Column(db.String(100), nullable=True, default="admin")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    book = db.relationship("LibraryBook", backref="transactions", lazy=True)
    student = db.relationship("Student", backref="library_transactions", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "book_title": self.book.title if self.book else "Unknown Book",
            "book_isbn": self.book.isbn if self.book else "-",
            "book_author": self.book.author if self.book else "-",
            "student_id": self.student_id,
            "student_name": self.student.fullName if self.student else "Unknown Student",
            "student_roll": self.student.enrollment_number if (self.student and self.student.enrollment_number) else (f"STU-{self.student_id:04d}" if self.student else "-"),
            "department": self.student.department if self.student else "-",
            "issue_date": self.issue_date.strftime("%Y-%m-%d") if self.issue_date else "",
            "due_date": self.due_date.strftime("%Y-%m-%d") if self.due_date else "",
            "return_date": self.return_date.strftime("%Y-%m-%d") if self.return_date else "-",
            "status": self.status,
            "overdue_days": self.overdue_days,
            "fine_amount": round(self.fine_amount, 2),
            "fine_status": self.fine_status,
            "remarks": self.remarks or "",
            "issued_by": self.issued_by or "admin",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }
