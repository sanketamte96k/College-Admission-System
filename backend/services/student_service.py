import os
from datetime import datetime

from models import db, Student
from utils import sanitize_input


class StudentService:

    ALLOWED_STATUSES = [
        "Pending Verification",
        "Under Review",
        "Verified",
        "Rejected"
    ]

    # =========================================================
    # GET ALL STUDENTS
    # =========================================================

    @staticmethod
    def get_all_students(
        page=1,
        limit=50,
        search_query="",
        department="",
        admission_type="",
        gender="",
        status=""
    ):
        query = Student.query

        if search_query:
            query = query.filter(
                Student.fullName.ilike(
                    f"%{search_query}%"
                )
            )

        if department:
            query = query.filter(
                Student.department == department
            )

        if admission_type:
            query = query.filter(
                Student.admissionType == admission_type
            )

        if gender:
            query = query.filter(
                Student.gender == gender
            )

        if status:
            query = query.filter(
                Student.status == status
            )

        query = query.order_by(
            Student.id.desc()
        )

        total = query.count()

        pagination = query.paginate(
            page=page,
            per_page=limit,
            error_out=False
        )

        students = [
            student.to_dict()
            for student in pagination.items
        ]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pagination.pages,
            "students": students
        }

    # =========================================================
    # GET STUDENT BY ID
    # =========================================================

    @staticmethod
    def get_student_by_id(student_id):
        return Student.query.get(student_id)

    # =========================================================
    # CREATE STUDENT
    # =========================================================

    @staticmethod
    def create_student(
        data,
        files,
        upload_folder
    ):

        full_name = sanitize_input(
            data.get("fullName", "")
        )

        father_name = sanitize_input(
            data.get("fatherName", "")
        )

        mother_name = sanitize_input(
            data.get("motherName", "")
        )

        dob = sanitize_input(
            data.get("dob", "")
        )

        gender = sanitize_input(
            data.get("gender", "")
        )

        blood_group = sanitize_input(
            data.get("bloodGroup", "")
        )

        mobile = sanitize_input(
            data.get("mobile", "")
        )

        alt_mobile = sanitize_input(
            data.get("altMobile", "")
        )

        email = sanitize_input(
            data.get("email", "")
        ).lower()

        aadhaar = sanitize_input(
            data.get("aadhaar", "")
        )

        address = sanitize_input(
            data.get("address", "")
        )

        city = sanitize_input(
            data.get("city", "")
        )

        state = sanitize_input(
            data.get("state", "")
        )

        pincode = sanitize_input(
            data.get("pincode", "")
        )

        nationality = sanitize_input(
            data.get("nationality", "")
        )

        board10 = sanitize_input(
            data.get("board10", "")
        )

        board12 = sanitize_input(
            data.get("board12", "")
        )

        entrance_exam = sanitize_input(
            data.get("entranceExam", "")
        )

        department = sanitize_input(
            data.get("department", "")
        )

        admission_type = sanitize_input(
            data.get("admissionType", "")
        )

        status = sanitize_input(
            data.get(
                "status",
                "Pending Verification"
            )
        )

        # =====================================================
        # REQUIRED FIELD VALIDATION
        # =====================================================

        required_fields = {
            "Full Name": full_name,
            "Father Name": father_name,
            "Mother Name": mother_name,
            "Date of Birth": dob,
            "Gender": gender,
            "Blood Group": blood_group,
            "Mobile": mobile,
            "Email": email,
            "Aadhaar": aadhaar,
            "Address": address,
            "City": city,
            "State": state,
            "Pincode": pincode,
            "Nationality": nationality,
            "10th Board": board10,
            "12th Board": board12,
            "Entrance Exam": entrance_exam,
            "Department": department,
            "Admission Type": admission_type
        }

        missing_fields = [
            field
            for field, value in required_fields.items()
            if not value
        ]

        if missing_fields:
            raise ValueError(
                "Missing required fields: "
                + ", ".join(missing_fields)
            )

        # =====================================================
        # DUPLICATE CHECK
        # =====================================================

        existing_student = Student.query.filter_by(
            aadhaar=aadhaar
        ).first()

        if existing_student:
            raise ValueError(
                "An admission already exists with "
                "this Aadhaar number. "
                f"Application ID: {existing_student.id}"
            )

        existing_student = Student.query.filter_by(
            email=email
        ).first()

        if existing_student:
            raise ValueError(
                "An admission already exists with "
                "this email address. "
                f"Application ID: {existing_student.id}"
            )

        existing_student = Student.query.filter_by(
            mobile=mobile
        ).first()

        if existing_student:
            raise ValueError(
                "An admission already exists with "
                "this mobile number. "
                f"Application ID: {existing_student.id}"
            )

        # =====================================================
        # NUMERIC VALUES
        # =====================================================

        try:
            percentage10 = float(
                data.get("percentage10", 0)
            )

            percentage12 = float(
                data.get("percentage12", 0)
            )

            entrance_score = float(
                data.get("entranceScore", 0)
            )

        except (TypeError, ValueError):
            raise ValueError(
                "Percentage and entrance score "
                "must be valid numbers."
            )

        # =====================================================
        # CREATE STUDENT
        # =====================================================

        new_student = Student(
            fullName=full_name,
            fatherName=father_name,
            motherName=mother_name,
            dob=dob,
            gender=gender,
            bloodGroup=blood_group,

            mobile=mobile,
            altMobile=alt_mobile,
            email=email,
            aadhaar=aadhaar,

            address=address,
            city=city,
            state=state,
            pincode=pincode,
            nationality=nationality,

            board10=board10,
            percentage10=percentage10,

            board12=board12,
            percentage12=percentage12,

            entranceExam=entrance_exam,
            entranceScore=entrance_score,

            department=department,
            admissionType=admission_type,

            status=status
        )

        # =====================================================
        # SAVE STUDENT
        # =====================================================

        try:
            db.session.add(new_student)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        # =====================================================
        # DOCUMENT UPLOADS
        # =====================================================

        doc_fields = {
            "photo": "photo",
            "marksheet10": "10th",
            "marksheet12": "12th",
            "leavingCertificate": "lc"
        }

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        file_updated = False

        for field_name, doc_name in doc_fields.items():

            if field_name not in files:
                continue

            file = files[field_name]

            if not file:
                continue

            if file.filename == "":
                continue

            ext = os.path.splitext(
                file.filename
            )[1].lower()

            saved_filename = (
                f"{new_student.id}_{doc_name}{ext}"
            )

            file_path = os.path.join(
                upload_folder,
                saved_filename
            )

            file.save(file_path)

            setattr(
                new_student,
                field_name,
                saved_filename
            )

            file_updated = True

        if file_updated:

            try:
                db.session.commit()

            except Exception:
                db.session.rollback()
                raise

        return new_student

    # =========================================================
    # UPDATE STUDENT
    # =========================================================

    @staticmethod
    def update_student(
        student_id,
        data,
        files,
        upload_folder
    ):

        student = Student.query.get(
            student_id
        )

        if not student:
            return None

        # -----------------------------------------------------
        # Duplicate email
        # -----------------------------------------------------

        if data.get("email"):

            email = sanitize_input(
                data["email"]
            ).lower()

            existing = Student.query.filter(
                Student.email == email,
                Student.id != student_id
            ).first()

            if existing:
                raise ValueError(
                    "Another student already uses "
                    "this email. "
                    f"Application ID: {existing.id}"
                )

        # -----------------------------------------------------
        # Duplicate mobile
        # -----------------------------------------------------

        if data.get("mobile"):

            mobile = sanitize_input(
                data["mobile"]
            )

            existing = Student.query.filter(
                Student.mobile == mobile,
                Student.id != student_id
            ).first()

            if existing:
                raise ValueError(
                    "Another student already uses "
                    "this mobile number. "
                    f"Application ID: {existing.id}"
                )

        # -----------------------------------------------------
        # Duplicate Aadhaar
        # -----------------------------------------------------

        if data.get("aadhaar"):

            aadhaar = sanitize_input(
                data["aadhaar"]
            )

            existing = Student.query.filter(
                Student.aadhaar == aadhaar,
                Student.id != student_id
            ).first()

            if existing:
                raise ValueError(
                    "Another student already uses "
                    "this Aadhaar number. "
                    f"Application ID: {existing.id}"
                )

        # =====================================================
        # TEXT FIELDS
        # =====================================================

        text_fields = [
            "fullName",
            "fatherName",
            "motherName",
            "dob",
            "gender",
            "bloodGroup",
            "mobile",
            "altMobile",
            "email",
            "aadhaar",
            "address",
            "city",
            "state",
            "pincode",
            "nationality",
            "board10",
            "board12",
            "entranceExam",
            "department",
            "admissionType",
            "status"
        ]

        for key in text_fields:

            if key not in data:
                continue

            if data[key] is None:
                continue

            value = sanitize_input(
                data[key]
            )

            if key == "email":
                value = value.lower()

            setattr(
                student,
                key,
                value
            )

        # =====================================================
        # NUMERIC FIELDS
        # =====================================================

        try:

            if "percentage10" in data:
                student.percentage10 = float(
                    data["percentage10"]
                )

            if "percentage12" in data:
                student.percentage12 = float(
                    data["percentage12"]
                )

            if "entranceScore" in data:
                student.entranceScore = float(
                    data["entranceScore"]
                )

        except (TypeError, ValueError):

            raise ValueError(
                "Percentage and entrance score "
                "must be valid numbers."
            )

        # =====================================================
        # DOCUMENT UPDATES
        # =====================================================

        doc_fields = {
            "photo": "photo",
            "marksheet10": "10th",
            "marksheet12": "12th",
            "leavingCertificate": "lc"
        }

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        for field_name, doc_name in doc_fields.items():

            if field_name not in files:
                continue

            file = files[field_name]

            if not file:
                continue

            if file.filename == "":
                continue

            ext = os.path.splitext(
                file.filename
            )[1].lower()

            saved_filename = (
                f"{student.id}_{doc_name}{ext}"
            )

            file_path = os.path.join(
                upload_folder,
                saved_filename
            )

            file.save(file_path)

            setattr(
                student,
                field_name,
                saved_filename
            )

        # =====================================================
        # SAVE
        # =====================================================

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return student

    # =========================================================
    # DELETE STUDENT
    # =========================================================

    @staticmethod
    def delete_student(
        student_id,
        upload_folder
    ):

        student = Student.query.get(
            student_id
        )

        if not student:
            return False

        uploaded_files = [
            student.photo,
            student.marksheet10,
            student.marksheet12,
            student.leavingCertificate
        ]

        for filename in uploaded_files:

            if not filename:
                continue

            file_path = os.path.join(
                upload_folder,
                filename
            )

            if os.path.exists(file_path):

                try:
                    os.remove(file_path)
                except OSError:
                    pass

        try:

            db.session.delete(student)
            db.session.commit()

        except Exception:

            db.session.rollback()
            raise

        return True

    # =========================================================
    # UPDATE ADMISSION VERIFICATION DECISION
    # =========================================================

    @staticmethod
    def update_verification(
        student_id,
        status,
        remarks="",
        admin_username="admin"
    ):
        student = Student.query.get(student_id)
        if not student:
            return None

        # Validate status
        if status not in StudentService.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Allowed statuses: {', '.join(StudentService.ALLOWED_STATUSES)}"
            )

        # Sanitize remarks
        clean_remarks = sanitize_input(remarks or "")

        # Rejection requires a meaningful remark/reason
        if status == "Rejected" and not clean_remarks:
            raise ValueError(
                "Verification remarks are required when rejecting an admission application."
            )

        student.status = status
        student.verification_remarks = clean_remarks

        if status in ["Verified", "Rejected", "Under Review"]:
            student.verified_at = datetime.utcnow()
            student.verified_by = admin_username or "admin"
        elif status == "Pending Verification":
            # Retain history or reset if reopened
            student.verified_at = None
            student.verified_by = None

        try:
            db.session.commit()
            return student
        except Exception:
            db.session.rollback()
            raise