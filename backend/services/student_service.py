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
            query = query.filter(Student.department == department)

        if course:
            query = query.filter(Student.course == course)

        if academic_year:
            query = query.filter(Student.academic_year == academic_year)

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

    # =========================================================
    # CONVERT TO ENROLLED STUDENT WORKFLOW
    # =========================================================
    @staticmethod
    def convert_to_student(student_id, admin_username="admin"):
        student = Student.query.get(student_id)
        if not student:
            return None, "Application record not found"

        if student.is_enrolled or student.status == "Enrolled":
            return None, f"Applicant is already converted to enrolled student ({student.enrollment_number or 'Enrolled'})."

        if student.status not in ["Approved", "Verified", "Documents Verified"]:
            return None, f"Only approved or verified applications can be converted to enrolled students. Current status: '{student.status}'"

        dept_code = "".join([w[0] for w in (student.department or "CE").split() if w]).upper()[:3] or "GEN"
        enrollment_no = f"ZEAL-2026-{dept_code}-{student.id:04d}"

        student.enrollment_number = enrollment_no
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
            return student, f"Applicant converted to enrolled student successfully! Enrollment Number: {enrollment_no}"
        except Exception as e:
            db.session.rollback()
            raise e

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