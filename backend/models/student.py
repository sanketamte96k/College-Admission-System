from datetime import datetime
from .database import db

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(100), nullable=False)
    fatherName = db.Column(db.String(100), nullable=False)
    motherName = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    bloodGroup = db.Column(db.String(10), nullable=False)

    mobile = db.Column(db.String(20), nullable=False)
    altMobile = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    aadhaar = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    nationality = db.Column(db.String(50), nullable=False)

    board10 = db.Column(db.String(100), nullable=False)
    percentage10 = db.Column(db.Float, nullable=False)
    board12 = db.Column(db.String(100), nullable=False)
    percentage12 = db.Column(db.Float, nullable=False)
    entranceExam = db.Column(db.String(50), nullable=False)
    entranceScore = db.Column(db.Float, nullable=False)

    department = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=True, default="B.Tech Computer Science")
    academic_year = db.Column(db.String(20), nullable=True, default="2026-27")
    admissionType = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    photo = db.Column(db.String(255), nullable=True)
    marksheet10 = db.Column(db.String(255), nullable=True)
    marksheet12 = db.Column(db.String(255), nullable=True)
    leavingCertificate = db.Column(db.String(255), nullable=True)

    doc_status_photo = db.Column(db.String(20), default="Pending", nullable=True)
    doc_status_10th = db.Column(db.String(20), default="Pending", nullable=True)
    doc_status_12th = db.Column(db.String(20), default="Pending", nullable=True)
    doc_status_lc = db.Column(db.String(20), default="Pending", nullable=True)

    status = db.Column(db.String(50), default="Pending Verification", nullable=True)
    verification_remarks = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by = db.Column(db.String(100), nullable=True)

    enrollment_number = db.Column(db.String(50), nullable=True)
    is_enrolled = db.Column(db.Boolean, default=False, nullable=True)
    enrolled_at = db.Column(db.DateTime, nullable=True)

    payments = db.relationship("Payment", backref="student", cascade="all, delete-orphan", lazy=True)
    attendance_records = db.relationship("Attendance", backref="student", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        app_id_code = f"ADM-2026-{self.id:04d}" if self.id else "ADM-2026-0000"
        return {
            "id": self.id,
            "application_id": app_id_code,
            "applicationId": app_id_code,
            "fullName": self.fullName,
            "fatherName": self.fatherName,
            "motherName": self.motherName,
            "dob": self.dob,
            "gender": self.gender,
            "bloodGroup": self.bloodGroup,
            "mobile": self.mobile,
            "altMobile": self.altMobile,
            "email": self.email,
            "aadhaar": self.aadhaar,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode,
            "nationality": self.nationality,
            "board10": self.board10,
            "percentage10": self.percentage10,
            "board12": self.board12,
            "percentage12": self.percentage12,
            "entranceExam": self.entranceExam,
            "entranceScore": self.entranceScore,
            "department": self.department,
            "course": self.course or (f"B.Tech in {self.department}" if self.department else "B.Tech Engineering"),
            "academic_year": self.academic_year or "2026-27",
            "admissionType": self.admissionType,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "photo": self.photo or "",
            "marksheet10": self.marksheet10 or "",
            "marksheet12": self.marksheet12 or "",
            "leavingCertificate": self.leavingCertificate or "",
            "doc_status_photo": self.doc_status_photo or ("Verified" if self.photo else "Pending"),
            "doc_status_10th": self.doc_status_10th or ("Verified" if self.marksheet10 else "Pending"),
            "doc_status_12th": self.doc_status_12th or ("Verified" if self.marksheet12 else "Pending"),
            "doc_status_lc": self.doc_status_lc or ("Verified" if self.leavingCertificate else "Pending"),
            "status": self.status or "Pending Verification",
            "verification_remarks": self.verification_remarks or "",
            "rejection_reason": self.rejection_reason or self.verification_remarks or "",
            "verified_at": self.verified_at.strftime("%Y-%m-%d %H:%M:%S") if self.verified_at else "",
            "verified_by": self.verified_by or "",
            "enrollment_number": self.enrollment_number or "",
            "is_enrolled": bool(self.is_enrolled),
            "enrolled_at": self.enrolled_at.strftime("%Y-%m-%d %H:%M:%S") if self.enrolled_at else ""
        }
