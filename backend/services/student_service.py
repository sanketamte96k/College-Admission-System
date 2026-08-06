import os
from models import db, Student
from utils import sanitize_input

class StudentService:
    @staticmethod
    def get_all_students(page=1, limit=50, search_query="", department="", admission_type="", gender=""):
        query = Student.query

        if search_query:
            query = query.filter(Student.fullName.like(f"%{search_query}%"))
        if department:
            query = query.filter(Student.department == department)
        if admission_type:
            query = query.filter(Student.admissionType == admission_type)
        if gender:
            query = query.filter(Student.gender == gender)

        query = query.order_by(Student.id.desc())

        total = query.count()
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        students = [s.to_dict() for s in pagination.items]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pagination.pages,
            "students": students
        }

    @staticmethod
    def get_student_by_id(student_id):
        return Student.query.get(student_id)

    @staticmethod
    def create_student(data, files, upload_folder):
        new_student = Student(
            fullName=sanitize_input(data.get("fullName")),
            fatherName=sanitize_input(data.get("fatherName")),
            motherName=sanitize_input(data.get("motherName")),
            dob=sanitize_input(data.get("dob")),
            gender=sanitize_input(data.get("gender")),
            bloodGroup=sanitize_input(data.get("bloodGroup")),
            mobile=sanitize_input(data.get("mobile")),
            altMobile=sanitize_input(data.get("altMobile", "")),
            email=sanitize_input(data.get("email")),
            aadhaar=sanitize_input(data.get("aadhaar")),
            address=sanitize_input(data.get("address")),
            city=sanitize_input(data.get("city")),
            state=sanitize_input(data.get("state")),
            pincode=sanitize_input(data.get("pincode")),
            nationality=sanitize_input(data.get("nationality")),
            board10=sanitize_input(data.get("board10")),
            percentage10=float(data.get("percentage10", 0)),
            board12=sanitize_input(data.get("board12")),
            percentage12=float(data.get("percentage12", 0)),
            entranceExam=sanitize_input(data.get("entranceExam")),
            entranceScore=float(data.get("entranceScore", 0)),
            department=sanitize_input(data.get("department")),
            admissionType=sanitize_input(data.get("admissionType")),
            status=sanitize_input(data.get("status", "Pending Verification"))
        )

        db.session.add(new_student)
        db.session.commit()

        # Document files handling
        doc_fields = {
            "photo": "photo",
            "marksheet10": "10th",
            "marksheet12": "12th",
            "leavingCertificate": "lc"
        }

        file_updated = False
        for field_name, doc_name in doc_fields.items():
            if field_name in files:
                file = files[field_name]
                if file and file.filename != "":
                    ext = os.path.splitext(file.filename)[1].lower()
                    saved_filename = f"{new_student.id}_{doc_name}{ext}"
                    file_path = os.path.join(upload_folder, saved_filename)
                    file.save(file_path)
                    setattr(new_student, field_name, saved_filename)
                    file_updated = True

        if file_updated:
            db.session.commit()

        return new_student

    @staticmethod
    def update_student(student_id, data, files, upload_folder):
        student = Student.query.get(student_id)
        if not student:
            return None

        # Update basic fields if provided
        for key in ["fullName", "fatherName", "motherName", "dob", "gender", "bloodGroup",
                    "mobile", "altMobile", "email", "aadhaar", "address", "city", "state",
                    "pincode", "nationality", "board10", "board12", "entranceExam",
                    "department", "admissionType", "status"]:
            if key in data and data[key] is not None:
                setattr(student, key, sanitize_input(data[key]))

        if "percentage10" in data: student.percentage10 = float(data["percentage10"])
        if "percentage12" in data: student.percentage12 = float(data["percentage12"])
        if "entranceScore" in data: student.entranceScore = float(data["entranceScore"])

        # Update uploaded documents
        doc_fields = {
            "photo": "photo",
            "marksheet10": "10th",
            "marksheet12": "12th",
            "leavingCertificate": "lc"
        }

        for field_name, doc_name in doc_fields.items():
            if field_name in files:
                file = files[field_name]
                if file and file.filename != "":
                    ext = os.path.splitext(file.filename)[1].lower()
                    saved_filename = f"{student.id}_{doc_name}{ext}"
                    file_path = os.path.join(upload_folder, saved_filename)
                    file.save(file_path)
                    setattr(student, field_name, saved_filename)

        db.session.commit()
        return student

    @staticmethod
    def delete_student(student_id, upload_folder):
        student = Student.query.get(student_id)
        if not student:
            return False

        # Cleanup physical uploaded files
        for fn in [student.photo, student.marksheet10, student.marksheet12, student.leavingCertificate]:
            if fn:
                file_path = os.path.join(upload_folder, fn)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass

        db.session.delete(student)
        db.session.commit()
        return True
