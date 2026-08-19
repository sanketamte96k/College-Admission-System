from datetime import datetime, date
from flask import current_app
from models import db, Student, Attendance

class AttendanceService:
    @staticmethod
    def parse_date(date_str):
        if not date_str:
            return date.today()
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, datetime):
            return date_str.date()
        try:
            return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def get_students_for_attendance(department=None, date_str=None):
        target_date = AttendanceService.parse_date(date_str)
        if target_date is None:
            return None, "Invalid date format. Expected YYYY-MM-DD."

        query = Student.query
        if department and department.strip() and department.lower() != "all":
            query = query.filter(Student.department == department.strip())

        students = query.order_by(Student.fullName.asc()).all()
        student_ids = [s.id for s in students]

        existing_records = Attendance.query.filter(
            Attendance.student_id.in_(student_ids),
            Attendance.attendance_date == target_date
        ).all() if student_ids else []

        attendance_map = {rec.student_id: rec for rec in existing_records}

        student_sheet = []
        for s in students:
            rec = attendance_map.get(s.id)
            student_sheet.append({
                "student_id": s.id,
                "fullName": s.fullName,
                "department": s.department or "-",
                "admissionType": s.admissionType or "-",
                "status": rec.status if rec else "Present",
                "remarks": rec.remarks if rec else "",
                "is_marked": rec is not None,
                "attendance_id": rec.id if rec else None
            })

        summary = {
            "attendance_date": target_date.strftime("%Y-%m-%d"),
            "department": department if department else "All Departments",
            "total_students": len(students),
            "marked_count": len(existing_records),
            "present_count": sum(1 for r in existing_records if r.status == "Present"),
            "absent_count": sum(1 for r in existing_records if r.status == "Absent"),
            "students": student_sheet
        }

        return summary, None

    @staticmethod
    def record_bulk_attendance(attendance_date_str, records, admin_username="admin"):
        target_date = AttendanceService.parse_date(attendance_date_str)
        if target_date is None:
            return False, "Invalid attendance date format. Expected YYYY-MM-DD.", None

        if not records or not isinstance(records, list):
            return False, "Attendance records list is required.", None

        saved_count = 0
        updated_count = 0

        try:
            for item in records:
                if not isinstance(item, dict):
                    raise ValueError("Each attendance record must be an object with student_id and status.")

                st_id = item.get("student_id")
                raw_status = str(item.get("status", "Present")).strip().capitalize()
                remarks = str(item.get("remarks", "")).strip()

                if not st_id:
                    raise ValueError("Missing student_id in attendance record.")

                if raw_status not in ["Present", "Absent"]:
                    raise ValueError(f"Invalid status '{raw_status}'. Must be 'Present' or 'Absent'.")

                student = Student.query.get(st_id)
                if not student:
                    raise ValueError(f"Student #{st_id} not found in database.")

                # Check for existing record to enforce duplicate prevention and upsert
                existing = Attendance.query.filter_by(
                    student_id=st_id,
                    attendance_date=target_date
                ).first()

                if existing:
                    existing.status = raw_status
                    existing.remarks = remarks
                    existing.marked_by = admin_username
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    new_rec = Attendance(
                        student_id=st_id,
                        attendance_date=target_date,
                        status=raw_status,
                        remarks=remarks,
                        marked_by=admin_username
                    )
                    db.session.add(new_rec)
                    saved_count += 1

            db.session.commit()

            return True, f"Attendance successfully saved ({saved_count} created, {updated_count} updated).", {
                "attendance_date": target_date.strftime("%Y-%m-%d"),
                "total_processed": len(records),
                "created": saved_count,
                "updated": updated_count
            }

        except Exception as e:
            db.session.rollback()
            return False, str(e), None

    @staticmethod
    def get_student_attendance_summary(student_id):
        student = Student.query.get(student_id)
        if not student:
            return None

        all_records = Attendance.query.filter_by(
            student_id=student_id
        ).order_by(Attendance.attendance_date.desc()).all()

        present_days = sum(1 for r in all_records if r.status == "Present")
        absent_days = sum(1 for r in all_records if r.status == "Absent")
        total_days = present_days + absent_days

        if total_days > 0:
            attendance_percentage = round((present_days / total_days) * 100.0, 2)
        else:
            attendance_percentage = 100.0

        min_threshold = 75.0
        try:
            if current_app:
                min_threshold = float(current_app.config.get("ATTENDANCE_MIN_PERCENTAGE", 75.0))
        except Exception:
            min_threshold = 75.0

        is_low = (attendance_percentage < min_threshold) and (total_days > 0)
        status_label = "Low Attendance" if is_low else "Good Attendance"
        warning_msg = (
            f"Your attendance ({attendance_percentage}%) is below the mandatory {int(min_threshold)}% threshold."
            if is_low
            else ""
        )

        return {
            "student_id": student.id,
            "fullName": student.fullName,
            "department": student.department or "-",
            "admissionType": student.admissionType or "-",
            "present_days": present_days,
            "absent_days": absent_days,
            "total_days": total_days,
            "attendance_percentage": attendance_percentage,
            "min_threshold": min_threshold,
            "is_low_attendance": is_low,
            "status_label": status_label,
            "warning_message": warning_msg,
            "records": [r.to_dict() for r in all_records]
        }

    @staticmethod
    def get_attendance_report(department=None, date_str=None):
        target_date = AttendanceService.parse_date(date_str)
        if target_date is None:
            return None, "Invalid date format. Expected YYYY-MM-DD."

        query = Student.query
        if department and department.strip() and department.lower() != "all":
            query = query.filter(Student.department == department.strip())

        students = query.all()
        total_students = len(students)
        student_ids = [s.id for s in students]

        day_records = Attendance.query.filter(
            Attendance.student_id.in_(student_ids),
            Attendance.attendance_date == target_date
        ).all() if student_ids else []

        present_count = sum(1 for r in day_records if r.status == "Present")
        absent_count = sum(1 for r in day_records if r.status == "Absent")
        total_marked = len(day_records)
        day_percentage = round((present_count / total_marked) * 100.0, 2) if total_marked > 0 else 0.0

        # Calculate overall low attendance students (< 75%)
        low_attendance_students = []
        min_threshold = 75.0
        try:
            if current_app:
                min_threshold = float(current_app.config.get("ATTENDANCE_MIN_PERCENTAGE", 75.0))
        except Exception:
            min_threshold = 75.0

        for s in students:
            st_records = Attendance.query.filter_by(student_id=s.id).all()
            if st_records:
                p_cnt = sum(1 for r in st_records if r.status == "Present")
                t_cnt = len(st_records)
                pct = round((p_cnt / t_cnt) * 100.0, 2)
                if pct < min_threshold:
                    low_attendance_students.append({
                        "student_id": s.id,
                        "fullName": s.fullName,
                        "department": s.department,
                        "present_days": p_cnt,
                        "total_days": t_cnt,
                        "attendance_percentage": pct
                    })

        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "department": department if department else "All Departments",
            "total_students": total_students,
            "marked_students": total_marked,
            "present_count": present_count,
            "absent_count": absent_count,
            "attendance_percentage": day_percentage,
            "min_threshold": min_threshold,
            "low_attendance_students": low_attendance_students
        }, None
