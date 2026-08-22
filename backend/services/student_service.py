import os
from datetime import datetime

from models import db, Student, SeatMatrix
from utils import sanitize_input


class StudentService:

    ALLOWED_STATUSES = [
        "Pending Verification",
        "Under Review",
        "Documents Verified",
        "Verified",
        "Approved",
        "Rejected",
        "Enrolled"
    ]

    # =========================================================
    # GET ALL STUDENTS / ADMISSIONS
    # =========================================================

    @staticmethod
    def get_all_students(
        page=1,
        limit=50,
        search_query="",
        department="",
        course="",
        academic_year="",
        admission_type="",
        gender="",
        status="",
        from_date="",
        to_date=""
    ):
        query = Student.query

        if search_query:
            sq = search_query.strip()
            # Support formatted Application ID search e.g. ADM-2026-0001 or raw ID digits
            id_match = None
            if sq.upper().startswith("ADM-"):
                try:
                    parts = sq.split("-")
                    id_match = int(parts[-1])
                except ValueError:
                    pass
            elif sq.isdigit():
                id_match = int(sq)

            if id_match:
                query = query.filter(
                    db.or_(
                        Student.id == id_match,
                        Student.fullName.ilike(f"%{sq}%"),
                        Student.email.ilike(f"%{sq}%"),
                        Student.mobile.ilike(f"%{sq}%")
                    )
                )
            else:
                query = query.filter(
                    db.or_(
                        Student.fullName.ilike(f"%{sq}%"),
                        Student.email.ilike(f"%{sq}%"),
                        Student.mobile.ilike(f"%{sq}%")
                    )
                )

        if department:
            query = query.filter(db.or_(Student.department == department, Student.department.ilike(f"%{department}%")))

        if course:
            query = query.filter(db.or_(Student.course == course, Student.course.ilike(f"%{course}%")))

        if academic_year:
            if academic_year == "2026-27":
                query = query.filter(db.or_(Student.academic_year == "2026-27", Student.academic_year.in_(["1", "2", "3", "4"]), Student.academic_year == None))
            else:
                query = query.filter(db.or_(Student.academic_year == academic_year, Student.academic_year.ilike(f"%{academic_year}%")))

        if admission_type:
            query = query.filter(Student.admissionType == admission_type)

        if gender:
            query = query.filter(Student.gender == gender)

        if status:
            if status == "Approved":
                query = query.filter(Student.status.in_(["Approved", "Verified"]))
            elif status == "Pending Review":
                query = query.filter(Student.status.in_(["Pending Verification", "Under Review"]))
            else:
                query = query.filter(Student.status == status)

        if from_date:
            try:
                dt_from = datetime.strptime(from_date, "%Y-%m-%d")
                query = query.filter(Student.created_at >= dt_from)
            except ValueError:
                pass

        if to_date:
            try:
                dt_to = datetime.strptime(to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                query = query.filter(Student.created_at <= dt_to)
            except ValueError:
                pass

        query = query.order_by(Student.id.desc())

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
            course=sanitize_input(data.get("course", "")) or f"B.Tech in {department}",
            academic_year=sanitize_input(data.get("academic_year", "")) or "2026-27",
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

        # Flexible status normalization
        raw_status = (status or "").strip()
        lower_status = raw_status.lower()
        if "verif" in lower_status or "approv" in lower_status:
            normalized_status = "Verified"
        elif "reject" in lower_status:
            normalized_status = "Rejected"
        elif "review" in lower_status:
            normalized_status = "Under Review"
        elif "pend" in lower_status:
            normalized_status = "Pending Verification"
        else:
            normalized_status = raw_status

        # Validate status against allowed list
        if normalized_status not in StudentService.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Allowed statuses: {', '.join(StudentService.ALLOWED_STATUSES)}"
            )

        # Sanitize remarks
        clean_remarks = sanitize_input(remarks or "")

        # Rejection requires a meaningful remark/reason
        if normalized_status == "Rejected" and not clean_remarks:
            raise ValueError(
                "Verification remarks are required when rejecting an admission application."
            )

        student.status = normalized_status
        student.verification_remarks = clean_remarks

        if normalized_status in ["Verified", "Rejected", "Under Review"]:
            student.verified_at = datetime.utcnow()
            student.verified_by = admin_username or "admin"
        elif normalized_status == "Pending Verification":
            student.verified_at = None
            student.verified_by = None

        try:
            db.session.commit()
            return student
        except Exception:
            db.session.rollback()
            raise

    # =========================================================
    # VERIFY INDIVIDUAL DOCUMENT
    # =========================================================
    @staticmethod
    def verify_document(student_id, doc_type, status, reason="", admin_username="admin"):
        student = Student.query.get(student_id)
        if not student:
            return None, "Student application not found"

        clean_doc = (doc_type or "").lower().strip()
        clean_status = "Verified" if "verif" in status.lower() else ("Rejected" if "reject" in status.lower() else "Pending")
        clean_reason = sanitize_input(reason or "")

        if clean_status == "Rejected" and not clean_reason:
            return None, "Rejection reason is required when rejecting a document."

        if clean_doc in ["photo"]:
            student.doc_status_photo = clean_status
        elif clean_doc in ["10th", "marksheet10"]:
            student.doc_status_10th = clean_status
        elif clean_doc in ["12th", "marksheet12"]:
            student.doc_status_12th = clean_status
        elif clean_doc in ["lc", "leavingcertificate"]:
            student.doc_status_lc = clean_status
        else:
            return None, f"Unknown document type '{doc_type}'"

        if clean_reason:
            student.verification_remarks = f"Document ({clean_doc.upper()}) {clean_status}: {clean_reason}"

        doc_statuses = [student.doc_status_photo, student.doc_status_10th, student.doc_status_12th, student.doc_status_lc]
        if "Rejected" in doc_statuses:
            student.status = "Under Review"
        elif all(s == "Verified" for s in doc_statuses):
            student.status = "Documents Verified"

        student.verified_at = datetime.utcnow()
        student.verified_by = admin_username or "admin"

        try:
            db.session.commit()
            return student, "Document verification status updated successfully"
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # APPROVE APPLICATION WORKFLOW
    # =========================================================
    @staticmethod
    def approve_application(student_id, admin_username="admin"):
        student = Student.query.get(student_id)
        if not student:
            return None, "Application not found"

        if student.status == "Enrolled":
            return student, "Application is already enrolled"

        student.status = "Approved"
        student.verified_at = datetime.utcnow()
        student.verified_by = admin_username or "admin"

        try:
            db.session.commit()
            return student, "Application approved successfully"
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # REJECT APPLICATION WORKFLOW
    # =========================================================
    @staticmethod
    def reject_application(student_id, reason, admin_username="admin"):
        student = Student.query.get(student_id)
        if not student:
            return None, "Application not found"

        clean_reason = sanitize_input(reason or "").strip()
        if not clean_reason:
            return None, "Rejection reason is required"

        student.status = "Rejected"
        student.rejection_reason = clean_reason
        student.verification_remarks = f"Application Rejected: {clean_reason}"
        student.verified_at = datetime.utcnow()
        student.verified_by = admin_username or "admin"

        try:
            db.session.commit()
            return student, "Application rejected successfully"
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def generate_official_zprn(student):
        """
        Generate official permanent ZPRN (Zeal Permanent Registration Number).
        Format: COLLEGE_CODE + PROGRAM_CODE + ADMISSION_YEAR_2DIGIT + SEQUENCE
        Example: 124BT260001, 124IT260042, 124AD260420
        """
        if not student:
            return None

        college_code = "124"
        try:
            from flask import current_app
            if current_app:
                college_code = str(current_app.config.get("COLLEGE_CODE", "124")).strip()
        except Exception:
            college_code = "124"

        dept_str = (student.department or "").strip().lower()
        if "comp" in dept_str or "cs" in dept_str:
            program_code = "BT"
        elif "info" in dept_str or "it" in dept_str:
            program_code = "IT"
        elif "ai" in dept_str or "data" in dept_str:
            program_code = "AD"
        elif "elec" in dept_str or "e&tc" in dept_str or "telecom" in dept_str:
            program_code = "ET"
        elif "mech" in dept_str:
            program_code = "ME"
        elif "civil" in dept_str:
            program_code = "CE"
        elif "electr" in dept_str:
            program_code = "EE"
        else:
            program_code = "BT"

        year_str = "26"
        if student.created_at:
            year_str = student.created_at.strftime("%y")
        elif student.academic_year:
            parts = str(student.academic_year).split("-")
            if len(parts) > 0 and len(parts[0]) == 4:
                year_str = parts[0][-2:]

        seq_str = f"{student.id:04d}" if student.id else "0001"
        zprn = f"{college_code}{program_code}{year_str}{seq_str}"
        return zprn

    # =========================================================
    # CONVERT TO ENROLLED STUDENT WORKFLOW
    # =========================================================
    @staticmethod
    def convert_to_student(student_id, admin_username="admin"):
        student = Student.query.get(student_id)
        if not student:
            return None, "Application record not found"

        if student.is_enrolled or student.status == "Enrolled":
            return None, f"Applicant is already converted to enrolled student (ZPRN: {student.enrollment_number or 'Enrolled'})."

        if student.status not in ["Approved", "Verified", "Documents Verified"]:
            return None, f"Only approved or verified applications can be converted to enrolled students. Current status: '{student.status}'"

        # Generate official permanent ZPRN if not already set
        if not student.enrollment_number:
            zprn_code = StudentService.generate_official_zprn(student)
            dup = Student.query.filter(Student.enrollment_number == zprn_code, Student.id != student.id).first()
            if dup:
                zprn_code = f"{zprn_code}-{student.id}"
            student.enrollment_number = zprn_code

        enrollment_no = student.enrollment_number
        student.is_enrolled = True
        student.enrolled_at = datetime.utcnow()
        student.status = "Enrolled"

        try:
            seat_record = SeatMatrix.query.filter_by(department=student.department).first()
            if seat_record:
                seat_record.filled_seats = (seat_record.filled_seats or 0) + 1
        except Exception:
            pass

        try:
            db.session.commit()
            return student, f"Applicant converted to enrolled student successfully! Official ZPRN: {enrollment_no}"
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # SEED DEFAULT INDIAN / MAHARASHTRIAN STUDENTS
    # =========================================================
    @staticmethod
    def seed_default_students():
        """
        Seed sample Indian/Maharashtrian students following the official admission workflow:
        Admission Application -> Approval -> Official ZPRN Generation -> Official Enrolled Record.
        """
        try:
            if Student.query.count() == 0:
                samples = [
                    {
                        "fullName": "Aarav Sharma",
                        "fatherName": "Rajesh Sharma",
                        "motherName": "Sunita Sharma",
                        "dob": "2004-05-15",
                        "gender": "Male",
                        "bloodGroup": "B+",
                        "mobile": "9822001101",
                        "email": "aarav.sharma@zeal.edu.in",
                        "aadhaar": "123456789001",
                        "address": "Kothrud, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411038",
                        "nationality": "Indian",
                        "board10": "CBSE",
                        "percentage10": 92.5,
                        "board12": "CBSE",
                        "percentage12": 90.0,
                        "entranceExam": "MHT-CET",
                        "entranceScore": 98.5,
                        "department": "Computer Engineering",
                        "course": "B.Tech Computer Engineering",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    },
                    {
                        "fullName": "Sneha Deshmukh",
                        "fatherName": "Prakash Deshmukh",
                        "motherName": "Anjali Deshmukh",
                        "dob": "2005-08-20",
                        "gender": "Female",
                        "bloodGroup": "O+",
                        "mobile": "9822001102",
                        "email": "sneha.deshmukh@zeal.edu.in",
                        "aadhaar": "123456789002",
                        "address": "Karve Nagar, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411052",
                        "nationality": "Indian",
                        "board10": "SSC",
                        "percentage10": 89.0,
                        "board12": "HSC",
                        "percentage12": 87.5,
                        "entranceExam": "MHT-CET",
                        "entranceScore": 95.2,
                        "department": "Information Technology",
                        "course": "B.Tech Information Technology",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    },
                    {
                        "fullName": "Rohan Kulkarni",
                        "fatherName": "Milind Kulkarni",
                        "motherName": "Madhuri Kulkarni",
                        "dob": "2006-03-12",
                        "gender": "Male",
                        "bloodGroup": "A+",
                        "mobile": "9822001103",
                        "email": "rohan.kulkarni@zeal.edu.in",
                        "aadhaar": "123456789003",
                        "address": "Deccan, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411004",
                        "nationality": "Indian",
                        "board10": "SSC",
                        "percentage10": 94.0,
                        "board12": "HSC",
                        "percentage12": 91.8,
                        "entranceExam": "JEE Main",
                        "entranceScore": 97.4,
                        "department": "Computer Engineering",
                        "course": "B.Tech Computer Engineering",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    },
                    {
                        "fullName": "Priya Joshi",
                        "fatherName": "Sanjay Joshi",
                        "motherName": "Sujata Joshi",
                        "dob": "2004-11-05",
                        "gender": "Female",
                        "bloodGroup": "AB+",
                        "mobile": "9822001104",
                        "email": "priya.joshi@zeal.edu.in",
                        "aadhaar": "123456789004",
                        "address": "Swargate, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411042",
                        "nationality": "Indian",
                        "board10": "CBSE",
                        "percentage10": 91.0,
                        "board12": "CBSE",
                        "percentage12": 89.4,
                        "entranceExam": "MHT-CET",
                        "entranceScore": 96.8,
                        "department": "Artificial Intelligence & Data Science",
                        "course": "B.Tech Artificial Intelligence & Data Science",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    },
                    {
                        "fullName": "Aditya Patil",
                        "fatherName": "Suresh Patil",
                        "motherName": "Shobha Patil",
                        "dob": "2003-01-25",
                        "gender": "Male",
                        "bloodGroup": "B+",
                        "mobile": "9822001105",
                        "email": "aditya.patil@zeal.edu.in",
                        "aadhaar": "123456789005",
                        "address": "Hadapsar, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411028",
                        "nationality": "Indian",
                        "board10": "SSC",
                        "percentage10": 86.5,
                        "board12": "HSC",
                        "percentage12": 84.0,
                        "entranceExam": "MHT-CET",
                        "entranceScore": 93.0,
                        "department": "Computer Engineering",
                        "course": "B.Tech Computer Engineering",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    },
                    {
                        "fullName": "Ananya Patil",
                        "fatherName": "Vikram Patil",
                        "motherName": "Vandana Patil",
                        "dob": "2005-09-18",
                        "gender": "Female",
                        "bloodGroup": "O+",
                        "mobile": "9822001106",
                        "email": "ananya.patil@zeal.edu.in",
                        "aadhaar": "123456789006",
                        "address": "Baner, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411045",
                        "nationality": "Indian",
                        "board10": "CBSE",
                        "percentage10": 93.2,
                        "board12": "CBSE",
                        "percentage12": 90.6,
                        "entranceExam": "MHT-CET",
                        "entranceScore": 96.1,
                        "department": "Information Technology",
                        "course": "B.Tech Information Technology",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    },
                    {
                        "fullName": "Rahul Jadhav",
                        "fatherName": "Dnyaneshwar Jadhav",
                        "motherName": "Usha Jadhav",
                        "dob": "2004-06-30",
                        "gender": "Male",
                        "bloodGroup": "A+",
                        "mobile": "9822001107",
                        "email": "rahul.jadhav@zeal.edu.in",
                        "aadhaar": "123456789007",
                        "address": "Warje, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411058",
                        "nationality": "Indian",
                        "board10": "SSC",
                        "percentage10": 85.0,
                        "board12": "HSC",
                        "percentage12": 83.2,
                        "entranceExam": "MHT-CET",
                        "entranceScore": 91.5,
                        "department": "Electronics & Telecommunication",
                        "course": "B.Tech Electronics & Telecommunication",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    },
                    {
                        "fullName": "Neha Shinde",
                        "fatherName": "Eknath Shinde",
                        "motherName": "Sarita Shinde",
                        "dob": "2005-04-14",
                        "gender": "Female",
                        "bloodGroup": "B-",
                        "mobile": "9822001108",
                        "email": "neha.shinde@zeal.edu.in",
                        "aadhaar": "123456789008",
                        "address": "Katraj, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411046",
                        "nationality": "Indian",
                        "board10": "SSC",
                        "percentage10": 88.0,
                        "board12": "HSC",
                        "percentage12": 86.0,
                        "entranceExam": "MHT-CET",
                        "entranceScore": 92.8,
                        "department": "Mechanical Engineering",
                        "course": "B.Tech Mechanical Engineering",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    },
                    {
                        "fullName": "Omkar Pawar",
                        "fatherName": "Ashok Pawar",
                        "motherName": "Asha Pawar",
                        "dob": "2006-07-22",
                        "gender": "Male",
                        "bloodGroup": "O+",
                        "mobile": "9822001109",
                        "email": "omkar.pawar@zeal.edu.in",
                        "aadhaar": "123456789009",
                        "address": "Dhankawadi, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411043",
                        "nationality": "Indian",
                        "board10": "SSC",
                        "percentage10": 87.5,
                        "board12": "HSC",
                        "percentage12": 85.0,
                        "entranceExam": "MHT-CET",
                        "entranceScore": 90.2,
                        "department": "Electrical Engineering",
                        "course": "B.Tech Electrical Engineering",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    },
                    {
                        "fullName": "Pooja More",
                        "fatherName": "Ganesh More",
                        "motherName": "Geeta More",
                        "dob": "2004-10-10",
                        "gender": "Female",
                        "bloodGroup": "A-",
                        "mobile": "9822001110",
                        "email": "pooja.more@zeal.edu.in",
                        "aadhaar": "123456789010",
                        "address": "Narhe, Pune",
                        "city": "Pune",
                        "state": "Maharashtra",
                        "pincode": "411041",
                        "nationality": "Indian",
                        "board10": "SSC",
                        "percentage10": 89.2,
                        "board12": "HSC",
                        "percentage12": 87.0,
                        "entranceExam": "MHT-CET",
                        "entranceScore": 94.1,
                        "department": "Civil Engineering",
                        "course": "B.Tech Civil Engineering",
                        "academic_year": "2026-27",
                        "admissionType": "CAP"
                    }
                ]

                created_students = []
                for item in samples:
                    s = Student(**item)
                    s.status = "Approved"
                    db.session.add(s)
                    db.session.commit()
                    StudentService.convert_to_student(s.id, admin_username="admin")
                    created_students.append(s)

                # Seed Fee Payments (Paid, Partially Paid, Pending)
                try:
                    from services.payment_service import PaymentService
                    # 1. Aarav Sharma - Fully Paid
                    PaymentService.record_payment(created_students[0].id, 75000.0, "Tuition Fee", "UPI / Online", "TXN-2026-AR01", "Annual Tuition Fee Paid")
                    PaymentService.record_payment(created_students[0].id, 35000.0, "Development Fee", "Bank Transfer", "TXN-2026-AR02", "Development & Exam Fee Paid")

                    # 2. Sneha Deshmukh - Fully Paid
                    PaymentService.record_payment(created_students[1].id, 72000.0, "Tuition Fee", "UPI / Online", "TXN-2026-SN01", "Tuition Fee Paid")
                    PaymentService.record_payment(created_students[1].id, 34000.0, "Development Fee", "Cash", "TXN-2026-SN02", "Development Fee Paid")

                    # 3. Rohan Kulkarni - Fully Paid
                    PaymentService.record_payment(created_students[2].id, 75000.0, "Tuition Fee", "Bank Transfer", "TXN-2026-RK01", "Annual Tuition Fee Paid")
                    PaymentService.record_payment(created_students[2].id, 35000.0, "Development Fee", "Demand Draft", "TXN-2026-RK02", "Development Fee Paid")

                    # 4. Priya Joshi - Partially Paid
                    PaymentService.record_payment(created_students[3].id, 60000.0, "Tuition Fee", "UPI / Online", "TXN-2026-PJ01", "Installment 1 Tuition Fee Paid")

                    # 5. Aditya Patil - Partially Paid
                    PaymentService.record_payment(created_students[4].id, 50000.0, "Tuition Fee", "UPI / Online", "TXN-2026-AP01", "Installment 1 Tuition Fee Paid")

                    # 6. Rahul Jadhav - Partially Paid
                    PaymentService.record_payment(created_students[6].id, 45000.0, "Tuition Fee", "Cash", "TXN-2026-RJ01", "Partial Fee Paid")
                except Exception as pe:
                    pass

                # Seed Transport Fleet & Passes
                try:
                    from services.transport_service import TransportService
                    TransportService.initialize_default_transport()
                    routes = TransportService.get_routes()
                    if routes and len(routes) >= 4:
                        r1, r2, r3, r4 = routes[0], routes[1], routes[2], routes[3]
                        if r1.get("stops") and len(r1["stops"]) > 0:
                            TransportService.assign_student_transport(created_students[0].enrollment_number, r1["id"], r1["stops"][0]["id"])
                        if r2.get("stops") and len(r2["stops"]) > 0:
                            TransportService.assign_student_transport(created_students[1].enrollment_number, r2["id"], r2["stops"][0]["id"])
                        if r3.get("stops") and len(r3["stops"]) > 0:
                            TransportService.assign_student_transport(created_students[2].enrollment_number, r3["id"], r3["stops"][0]["id"])
                        if r4.get("stops") and len(r4["stops"]) > 0:
                            TransportService.assign_student_transport(created_students[3].enrollment_number, r4["id"], r4["stops"][0]["id"])
                except Exception as te:
                    pass
        except Exception as e:
            db.session.rollback()

    # =========================================================
    # ADMISSIONS REAL ANALYTICS
    # =========================================================
    @staticmethod
    def get_admissions_analytics():
        total_applications = Student.query.count()
        pending_review = Student.query.filter(Student.status.in_(["Pending Verification", "Under Review"])).count()
        approved = Student.query.filter(Student.status.in_(["Approved", "Verified", "Documents Verified"])).count()
        rejected = Student.query.filter(Student.status == "Rejected").count()
        under_review = Student.query.filter(Student.status == "Under Review").count()
        enrolled = Student.query.filter(db.or_(Student.status == "Enrolled", Student.is_enrolled == True)).count()

        admission_rate = round((approved / total_applications * 100), 1) if total_applications > 0 else 0.0

        dept_counts = {}
        all_students = Student.query.all()
        for s in all_students:
            dept = s.department or "Unassigned"
            if dept not in dept_counts:
                dept_counts[dept] = {"total": 0, "approved": 0, "pending": 0, "enrolled": 0}
            dept_counts[dept]["total"] += 1
            if s.status in ["Approved", "Verified", "Documents Verified"]:
                dept_counts[dept]["approved"] += 1
            elif s.status in ["Pending Verification", "Under Review"]:
                dept_counts[dept]["pending"] += 1
            if s.status == "Enrolled" or s.is_enrolled:
                dept_counts[dept]["enrolled"] += 1

        doc_pending_count = Student.query.filter(
            db.or_(
                Student.doc_status_photo == "Pending",
                Student.doc_status_10th == "Pending",
                Student.doc_status_12th == "Pending",
                Student.doc_status_lc == "Pending"
            )
        ).count()

        approved_unconverted_count = Student.query.filter(
            Student.status.in_(["Approved", "Verified", "Documents Verified"]),
            db.or_(Student.is_enrolled == False, Student.is_enrolled == None)
        ).count()

        return {
            "total_applications": total_applications,
            "pending_review": pending_review,
            "approved": approved,
            "rejected": rejected,
            "under_review": under_review,
            "enrolled": enrolled,
            "admission_rate": admission_rate,
            "pipeline": {
                "new": Student.query.filter(Student.status == "Pending Verification").count(),
                "under_review": under_review,
                "documents_verification": Student.query.filter(Student.status == "Documents Verified").count(),
                "approved": approved,
                "rejected": rejected,
                "enrolled": enrolled
            },
            "by_department": dept_counts,
            "attention_required": {
                "pending_documents": doc_pending_count,
                "awaiting_review": pending_review,
                "approved_awaiting_enrollment": approved_unconverted_count
            }
        }

    # =========================================================
    # STUDENTS MODULE KPI STATS
    # =========================================================
    @staticmethod
    def get_students_kpi_stats():
        total_students = Student.query.count()
        active_students = Student.query.filter(
            db.or_(
                Student.status == "Enrolled",
                Student.status.in_(["Approved", "Verified", "Documents Verified"]),
                Student.is_enrolled == True
            )
        ).count()
        male_students = Student.query.filter(Student.gender.ilike("male")).count()
        female_students = Student.query.filter(Student.gender.ilike("female")).count()
        new_students = Student.query.filter(
            db.or_(
                Student.academic_year == "2026-27",
                Student.created_at >= datetime(2026, 1, 1)
            )
        ).count()

        return {
            "total_students": total_students,
            "active_students": active_students,
            "male_students": male_students,
            "female_students": female_students,
            "new_students": new_students
        }