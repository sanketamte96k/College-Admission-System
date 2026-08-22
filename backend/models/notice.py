from datetime import datetime
from .database import db

class Notice(db.Model):
    __tablename__ = "notices"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="General")
    priority = db.Column(db.String(20), nullable=False, default="Normal")
    status = db.Column(db.String(20), nullable=False, default="Draft")
    
    audience = db.Column(db.String(50), nullable=False, default="Everyone")
    department = db.Column(db.String(100), nullable=True)
    course = db.Column(db.String(100), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True)
    semester = db.Column(db.String(20), nullable=True)
    
    publish_date = db.Column(db.DateTime, nullable=True)
    expiry_date = db.Column(db.DateTime, nullable=True)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    
    created_by = db.Column(db.String(100), default="Admin", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def effective_status(self):
        now = datetime.utcnow()
        if self.status == "Archived":
            return "Archived"
        if self.status == "Draft":
            return "Draft"
        if self.expiry_date and self.expiry_date <= now:
            return "Expired"
        if self.publish_date and self.publish_date > now:
            return "Scheduled"
        if self.status == "Published":
            return "Published"
        return self.status

    def to_dict(self):
        eff_status = self.effective_status
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category or "General",
            "priority": self.priority or "Normal",
            "status": eff_status,
            "stored_status": self.status,
            "audience": self.audience or "Everyone",
            "department": self.department or "",
            "course": self.course or "",
            "academic_year": self.academic_year or "",
            "semester": self.semester or "",
            "publish_date": self.publish_date.strftime("%Y-%m-%d %H:%M:%S") if self.publish_date else "",
            "publish_date_iso": self.publish_date.strftime("%Y-%m-%dT%H:%M") if self.publish_date else "",
            "expiry_date": self.expiry_date.strftime("%Y-%m-%d %H:%M:%S") if self.expiry_date else "",
            "expiry_date_iso": self.expiry_date.strftime("%Y-%m-%dT%H:%M") if self.expiry_date else "",
            "is_pinned": bool(self.is_pinned),
            "created_by": self.created_by or "Admin",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else ""
        }
