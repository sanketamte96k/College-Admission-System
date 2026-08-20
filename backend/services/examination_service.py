from datetime import datetime
from models import db, Examination, ExamMark, Student, Department, Subject, Course
from utils import sanitize_input

DEFAULT_EXAMINATIONS = [
    {
        "name": "Mid-Sem: Data Structures & Algorithms",
        "department": "Computer Engineering",
        "program": "B.Tech Computer Engineering",
        "academic_year": 2,
        "semester": 3,
        "subject_code": "CS301",
        "subject_name": "Data Structures & Algorithms",
        "exam_type": "Mid Semester",
        "exam_date": "2026-09-10",
        "start_time": "10:00 AM",
        "end_time": "12:00 PM",
        "max_marks": 50,
        "passing_marks": 20,
        "status": "Scheduled",
        "instructions": "In-Sem written examination covering Units 1 to 3."
    },
    {
        "name": "End-Sem: Database Management Systems",
        "department": "Computer Engineering",
        "program": "B.Tech Computer Engineering",
        "academic_year": 2,
        "semester": 3,
        "subject_code": "CS302",
        "subject_name": "Database Management Systems",
        "exam_type": "End Semester",
        "exam_date": "2026-09-15",
        "start_time": "10:00 AM",
        "end_time": "01:00 PM",
        "max_marks": 100,
        "passing_marks": 40,
        "status": "Completed",
        "instructions": "SPPU End-Sem Theory Examination. All units covered."
    },
    {
        "name": "End-Sem: Computer Networks",
        "department": "Computer Engineering",
        "program": "B.Tech Computer Engineering",
        "academic_year": 3,
        "semester": 5,
        "subject_code": "CS501",
        "subject_name": "Computer Networks",
        "exam_type": "End Semester",
        "exam_date": "2026-09-20",
        "start_time": "02:00 PM",
        "end_time": "05:00 PM",
        "max_marks": 100,
        "passing_marks": 40,
        "status": "Published",
        "instructions": "Theory + Numerical problems on TCP/IP protocols."
    },
    {
        "name": "Internal Practical Evaluation: Web Tech Lab",
        "department": "Computer Engineering",
        "program": "B.Tech Computer Engineering",
        "academic_year": 3,
        "semester": 5,
        "subject_code": "CS502",
        "subject_name": "Web Technology",
        "exam_type": "Practical",
        "exam_date": "2026-09-22",
        "start_time": "09:30 AM",
        "end_time": "12:30 PM",
        "max_marks": 50,
        "passing_marks": 20,
        "status": "Scheduled",
        "instructions": "Practical implementation of REST APIs and Node.js backend."
    },
    {
        "name": "End-Sem: Machine Learning",
        "department": "Computer Engineering",
        "program": "B.Tech Computer Engineering",
        "academic_year": 4,
        "semester": 7,
        "subject_code": "CS701",
        "subject_name": "Machine Learning",
        "exam_type": "End Semester",
        "exam_date": "2026-09-25",
        "start_time": "10:00 AM",
        "end_time": "01:00 PM",
        "max_marks": 100,
        "passing_marks": 40,
        "status": "Scheduled",
        "instructions": "Written examination on Supervised & Unsupervised Learning algorithms."
    }
]

def calculate_grade_and_result(marks, max_marks, passing_marks, is_absent=False):
    if is_absent or marks is None:
        return 0.0, "F", "Absent"
    
    pct = (marks / max_marks) * 100.0 if max_marks > 0 else 0.0
    result_status = "Pass" if marks >= passing_marks else "Fail"

    if pct >= 90: grade = "O"
    elif pct >= 80: grade = "A+"
    elif pct >= 70: grade = "A"
    elif pct >= 60: grade = "B+"
    elif pct >= 50: grade = "B"
    elif pct >= 40: grade = "C"
    elif pct >= passing_marks: grade = "P"
    else: grade = "F"

    return round(pct, 2), grade, result_status


class ExaminationService:

    @staticmethod
    def initialize_examinations():
        """Ensure standard sample examinations exist in the database"""
        if Examination.query.count() == 0:
            for ex in DEFAULT_EXAMINATIONS:
                exam = Examination(
                    name=ex["name"],
                    department=ex["department"],
                    program=ex["program"],
                    academic_year=ex["academic_year"],
                    semester=ex["semester"],
                    subject_code=ex["subject_code"],
                    subject_name=ex["subject_name"],
                    exam_type=ex["exam_type"],
                    exam_date=ex["exam_date"],
                    start_time=ex["start_time"],
                    end_time=ex["end_time"],
                    max_marks=ex["max_marks"],
                    passing_marks=ex["passing_marks"],
                    status=ex["status"],
                    instructions=ex["instructions"]
                )
                db.session.add(exam)
            
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

    @staticmethod
    def get_all_examinations(department="", program="", academic_year=None, semester=None, exam_type="", status="", search=""):
        ExaminationService.initialize_examinations()

        query = Examination.query

        if department:
            query = query.filter(Examination.department == department)
        if program:
            query = query.filter(Examination.program == program)
        if academic_year and str(academic_year).isdigit():
            query = query.filter(Examination.academic_year == int(academic_year))
        if semester and str(semester).isdigit():
            query = query.filter(Examination.semester == int(semester))
        if exam_type:
            query = query.filter(Examination.exam_type == exam_type)
        if status:
            query = query.filter(Examination.status == status)
        if search:
            sq = search.strip()
            query = query.filter(
                db.or_(
                    Examination.name.ilike(f"%{sq}%"),
                    Examination.subject_code.ilike(f"%{sq}%"),
                    Examination.subject_name.ilike(f"%{sq}%"),
                    Examination.department.ilike(f"%{sq}%")
                )
            )

        exams = query.order_by(Examination.exam_date.asc(), Examination.id.asc()).all()

        total_exams = len(exams)
        upcoming_exams = sum(1 for e in exams if e.status in ["Scheduled", "Draft"])
        completed_exams = sum(1 for e in exams if e.status in ["Completed", "Results Pending", "Published"])
        published_results = sum(1 for e in exams if e.status == "Published")
        total_students_evaluated = ExamMark.query.filter(ExamMark.status.in_(["Evaluated", "Published"])).count()

        result_list = []
        for ex in exams:
            ex_dict = ex.to_dict()
            ex_dict["marks_entered_count"] = ExamMark.query.filter_by(exam_id=ex.id).count()
            result_list.append(ex_dict)

        return {
            "summary": {
                "total_exams": total_exams,
                "upcoming_exams": upcoming_exams,
                "completed_exams": completed_exams,
                "published_results": published_results,
                "total_students_evaluated": total_students_evaluated
            },
            "examinations": result_list
        }

    @staticmethod
    def get_examination_by_id(exam_id):
        exam = Examination.query.get(exam_id)
        if not exam:
            return None

        ex_dict = exam.to_dict()

        # Compute student evaluation breakdown
        marks = ExamMark.query.filter_by(exam_id=exam.id).all()
        evaluated_marks = [m for m in marks if m.marks_obtained is not None and not m.is_absent]

        total_students = len(marks)
        marks_entered = len([m for m in marks if m.marks_obtained is not None or m.is_absent])
        pending = total_students - marks_entered
        absent_count = len([m for m in marks if m.is_absent])
        passed_count = len([m for m in marks if m.result_status == "Pass"])
        failed_count = len([m for m in marks if m.result_status == "Fail"])

        scores = [m.marks_obtained for m in evaluated_marks]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        max_score = max(scores) if scores else 0.0
        min_score = min(scores) if scores else 0.0

        ex_dict["evaluation_summary"] = {
            "total_students": total_students,
            "marks_entered": marks_entered,
            "pending": pending,
            "absent_count": absent_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "average_score": avg_score,
            "highest_score": max_score,
            "lowest_score": min_score,
            "pass_percentage": round((passed_count / total_students) * 100.0, 2) if total_students > 0 else 0.0
        }

        return ex_dict

    @staticmethod
    def create_examination(data):
        name = sanitize_input(data.get("name", ""))
        department = sanitize_input(data.get("department", ""))
        program = sanitize_input(data.get("program", ""))
        subject_code = sanitize_input(data.get("subject_code", "")).upper()
        subject_name = sanitize_input(data.get("subject_name", ""))
        exam_type = sanitize_input(data.get("exam_type", "End Semester"))
        exam_date = sanitize_input(data.get("exam_date", ""))
        start_time = sanitize_input(data.get("start_time", "10:00 AM"))
        end_time = sanitize_input(data.get("end_time", "01:00 PM"))
        instructions = sanitize_input(data.get("instructions", ""))
        status = sanitize_input(data.get("status", "Scheduled"))

        try:
            academic_year = int(data.get("academic_year", 1))
            semester = int(data.get("semester", 1))
            max_marks = int(data.get("max_marks", 100))
            passing_marks = int(data.get("passing_marks", 40))
        except (ValueError, TypeError):
            academic_year, semester, max_marks, passing_marks = 1, 1, 100, 40

        if not name or not department or not program or not subject_code or not exam_date:
            raise ValueError("Exam Name, Department, Program, Subject, and Exam Date are required.")

        new_exam = Examination(
            name=name,
            department=department,
            program=program,
            academic_year=academic_year,
            semester=semester,
            subject_code=subject_code,
            subject_name=subject_name or subject_code,
            exam_type=exam_type,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            max_marks=max_marks,
            passing_marks=passing_marks,
            instructions=instructions,
            status=status
        )

        db.session.add(new_exam)
        db.session.commit()
        return new_exam

    @staticmethod
    def update_examination(exam_id, data):
        exam = Examination.query.get(exam_id)
        if not exam:
            return None

        if exam.status == "Published" and data.get("status") != "Published" and data.get("status") != "Completed":
            # If changing critical metadata on published exam
            pass

        if "name" in data and data["name"]: exam.name = sanitize_input(data["name"])
        if "department" in data: exam.department = sanitize_input(data["department"])
        if "program" in data: exam.program = sanitize_input(data["program"])
        if "subject_code" in data: exam.subject_code = sanitize_input(data["subject_code"]).upper()
        if "subject_name" in data: exam.subject_name = sanitize_input(data["subject_name"])
        if "exam_type" in data: exam.exam_type = sanitize_input(data["exam_type"])
        if "exam_date" in data: exam.exam_date = sanitize_input(data["exam_date"])
        if "start_time" in data: exam.start_time = sanitize_input(data["start_time"])
        if "end_time" in data: exam.end_time = sanitize_input(data["end_time"])
        if "instructions" in data: exam.instructions = sanitize_input(data["instructions"])
        if "status" in data: exam.status = sanitize_input(data["status"])

        try:
            if "academic_year" in data: exam.academic_year = int(data["academic_year"])
            if "semester" in data: exam.semester = int(data["semester"])
            if "max_marks" in data: exam.max_marks = int(data["max_marks"])
            if "passing_marks" in data: exam.passing_marks = int(data["passing_marks"])
        except (ValueError, TypeError):
            pass

        db.session.commit()
        return exam

    @staticmethod
    def delete_examination(exam_id):
        exam = Examination.query.get(exam_id)
        if not exam:
            return False, "Examination record not found."

        if exam.status == "Published":
            return False, f"Cannot delete examination '{exam.name}' because its results are already published. Unpublish results first if required."

        db.session.delete(exam)
        db.session.commit()
        return True, f"Examination '{exam.name}' deleted successfully."

    # ============================================================
    # MARKS / EVALUATION METHODS
    # ============================================================

    @staticmethod
    def get_examination_marks(exam_id):
        exam = Examination.query.get(exam_id)
        if not exam:
            return None

        # Fetch all students belonging to this department
        students = Student.query.filter(
            Student.department == exam.department
        ).order_by(Student.id.asc()).all()

        # If no students match exact department, fetch all active students
        if not students:
            students = Student.query.order_by(Student.id.asc()).all()

        # Ensure ExamMark row exists for each student
        for st in students:
            mark_row = ExamMark.query.filter_by(exam_id=exam.id, student_id=st.id).first()
            if not mark_row:
                mark_row = ExamMark(
                    exam_id=exam.id,
                    student_id=st.id,
                    roll_no=st.enrollment_number or f"STU-{st.id:04d}",
                    status="Draft",
                    result_status="Pending"
                )
                db.session.add(mark_row)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        mark_rows = ExamMark.query.filter_by(exam_id=exam.id).all()
        return {
            "examination": exam.to_dict(),
            "marks": [m.to_dict() for m in mark_rows]
        }

    @staticmethod
    def save_examination_marks(exam_id, marks_list):
        exam = Examination.query.get(exam_id)
        if not exam:
            return False, "Examination not found."

        if exam.status == "Published":
            return False, "Cannot modify marks because results are already published. Unpublish first."

        updated_count = 0
        for item in marks_list:
            student_id = item.get("student_id")
            if not student_id:
                continue

            mark_row = ExamMark.query.filter_by(exam_id=exam.id, student_id=student_id).first()
            if not mark_row:
                mark_row = ExamMark(exam_id=exam.id, student_id=student_id)
                db.session.add(mark_row)

            is_absent = bool(item.get("is_absent", False))
            raw_marks = item.get("marks_obtained")

            if is_absent:
                marks_obtained = 0.0
            else:
                try:
                    marks_obtained = float(raw_marks) if raw_marks is not None and raw_marks != "" else None
                except (ValueError, TypeError):
                    marks_obtained = None

            if marks_obtained is not None and not is_absent:
                if marks_obtained < 0 or marks_obtained > exam.max_marks:
                    raise ValueError(f"Marks for Student ID {student_id} must be between 0 and {exam.max_marks}.")

            pct, grade, res_stat = calculate_grade_and_result(
                marks=marks_obtained,
                max_marks=exam.max_marks,
                passing_marks=exam.passing_marks,
                is_absent=is_absent
            )

            mark_row.marks_obtained = marks_obtained
            mark_row.is_absent = is_absent
            mark_row.percentage = pct
            mark_row.grade = grade
            mark_row.result_status = res_stat
            mark_row.status = "Evaluated"
            mark_row.remarks = sanitize_input(item.get("remarks", ""))
            updated_count += 1

        exam.status = "Results Pending" if exam.status in ["Draft", "Scheduled"] else exam.status
        db.session.commit()
        return True, f"Saved evaluation marks for {updated_count} student(s)."

    @staticmethod
    def publish_results(exam_id):
        exam = Examination.query.get(exam_id)
        if not exam:
            return False, "Examination not found."

        marks = ExamMark.query.filter_by(exam_id=exam.id).all()
        if not marks:
            return False, "No student marks recorded yet for this examination."

        for m in marks:
            m.status = "Published"

        exam.status = "Published"
        db.session.commit()
        return True, f"Successfully published examination results for '{exam.name}'."

    @staticmethod
    def unpublish_results(exam_id):
        exam = Examination.query.get(exam_id)
        if not exam:
            return False, "Examination not found."

        marks = ExamMark.query.filter_by(exam_id=exam.id).all()
        for m in marks:
            m.status = "Evaluated"

        exam.status = "Results Pending"
        db.session.commit()
        return True, f"Unpublished examination results for '{exam.name}'."

    @staticmethod
    def get_exam_schedule(department="", program="", academic_year=None, semester=None):
        ExaminationService.initialize_examinations()
        query = Examination.query

        if department: query = query.filter(Examination.department == department)
        if program: query = query.filter(Examination.program == program)
        if academic_year and str(academic_year).isdigit(): query = query.filter(Examination.academic_year == int(academic_year))
        if semester and str(semester).isdigit(): query = query.filter(Examination.semester == int(semester))

        exams = query.order_by(Examination.exam_date.asc(), Examination.start_time.asc()).all()

        schedule_items = [e.to_dict() for e in exams]
        return schedule_items
