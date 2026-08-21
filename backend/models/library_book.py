from datetime import datetime
from .database import db

class LibraryBook(db.Model):
    __tablename__ = "library_books"

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(30), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False, default="General")
    publisher = db.Column(db.String(150), nullable=True)
    edition = db.Column(db.String(50), nullable=True, default="1st Edition")
    pub_year = db.Column(db.Integer, nullable=True, default=2024)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    available_qty = db.Column(db.Integer, nullable=False, default=1)
    location = db.Column(db.String(50), nullable=True, default="Rack A-1")
    status = db.Column(db.String(30), nullable=False, default="Available")
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "publisher": self.publisher or "-",
            "edition": self.edition or "1st Edition",
            "pub_year": self.pub_year or 2024,
            "quantity": self.quantity,
            "available_qty": self.available_qty,
            "location": self.location or "Rack A-1",
            "status": self.status,
            "description": self.description or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else ""
        }
