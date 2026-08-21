import io
import csv
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from models import db, Student, Payment, Attendance, Department, Course, Subject, Examination, ExamMark
from .payment_service import PaymentService

class AnalyticsService:
    @staticmethod
    def get_dashboard_metrics():
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        month_start = datetime(now.year, now.month, 1)

        all_students = Student.query.all()
        total = len(all_students)

        today_admissions = Student.query.filter(Student.created_at >= today_start).count()
        month_admissions = Student.query.filter(Student.created_at >= month_start).count()
        male_count = Student.query.filter(Student.gender == "Male").count()
        female_count = Student.query.filter(Student.gender == "Female").count()
        other_gender = max(0, total - (male_count + female_count))

        dept_counts = {}
        for s in all_students:
            dept = s.department or "Other"
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        total_departments = len(dept_counts) if dept_counts else 7

        admission_types = {"CAP": 0, "Management": 0, "NRI": 0}
        for s in all_students:
            atype = s.admissionType or "CAP"
            admission_types[atype] = admission_types.get(atype, 0) + 1

        monthly_trends = []
        for i in range(5, -1, -1):
            m_date = now - timedelta(days=i*30)
            m_name = m_date.strftime("%b %Y")
            m_start = datetime(m_date.year, m_date.month, 1)
            if m_date.month == 12:
                m_end = datetime(m_date.year + 1, 1, 1)
            else:
                m_end = datetime(m_date.year, m_date.month + 1, 1)

            m_count = Student.query.filter(Student.created_at >= m_start, Student.created_at < m_end).count()
            monthly_trends.append({"month": m_name, "count": m_count})

        if dept_counts:
            highest_dept = max(dept_counts, key=dept_counts.get)
            lowest_dept = min(dept_counts, key=dept_counts.get)
        else:
            highest_dept = "N/A"
            lowest_dept = "N/A"

        avg_score = round(sum(s.entranceScore for s in all_students) / total, 2) if total > 0 else 0.0
        avg_perc12 = round(sum(s.percentage12 for s in all_students) / total, 2) if total > 0 else 0.0

        latest_student_obj = Student.query.order_by(Student.id.desc()).first()
        latest_student = latest_student_obj.fullName if latest_student_obj else "N/A"

        recent_objs = Student.query.order_by(Student.id.desc()).limit(8).all()
        recent_admissions = [{
            "id": s.id,
            "photo": s.photo or "",
            "fullName": s.fullName,
            "department": s.department or "-",
            "admissionType": s.admissionType or "CAP",
            "created_at": s.created_at.strftime("%Y-%m-%d") if s.created_at else "",
            "status": s.status or "Pending Verification"
        } for s in recent_objs]

        # Status Statistics
        pending_count = 0
        review_count = 0
        verified_count = 0
        rejected_count = 0

        # Fee Statistics
        total_fees_expected = 0.0
        total_fees_collected = 0.0
        paid_students_count = 0
        partial_paid_students_count = 0
        pending_fees_students_count = 0

        for s in all_students:
            st = s.status or "Pending Verification"
            if st == "Verified":
                verified_count += 1
            elif st == "Under Review":
                review_count += 1
            elif st == "Rejected":
                rejected_count += 1
            else:
                pending_count += 1

            # Fee computation per student
            try:
                _, s_total = PaymentService.get_fee_breakdown_for_student(s)
                s_payments = getattr(s, "payments", []) or []
                s_paid = sum(float(p.amount) for p in s_payments if getattr(p, "status", "") in ["SUCCESS", "Paid"])
                total_fees_expected += s_total
                total_fees_collected += s_paid
                if s_paid == 0.0:
                    pending_fees_students_count += 1
                elif s_paid >= s_total:
                    paid_students_count += 1
                else:
                    partial_paid_students_count += 1
            except Exception:
                pass

        total_pending_fees = max(0.0, round(total_fees_expected - total_fees_collected, 2))
        total_fees_collected = round(total_fees_collected, 2)
        total_fees_expected = round(total_fees_expected, 2)
        fee_collection_rate = round((total_fees_collected / total_fees_expected * 100.0), 1) if total_fees_expected > 0 else 0.0

        status_stats = {
            "Verified": verified_count,
            "Pending Verification": pending_count,
            "Under Review": review_count,
            "Rejected": rejected_count
        }

        # Recent Payments
        recent_payment_objs = Payment.query.order_by(Payment.id.desc()).limit(8).all()
        recent_payments = []
        for p in recent_payment_objs:
            st = Student.query.get(p.student_id)
            recent_payments.append({
                "id": p.id,
                "student_id": p.student_id,
                "student_name": st.fullName if st else f"Student #{p.student_id}",
                "department": st.department if st else "-",
                "transaction_id": p.transaction_id or f"ZEAL-PAY-{p.id}",
                "amount": float(p.amount),
                "fee_type": p.fee_type or "Tuition Fee",
                "payment_method": p.payment_method or p.payment_mode or "UPI",
                "payment_date": p.payment_date.strftime("%Y-%m-%d") if p.payment_date else (p.created_at.strftime("%Y-%m-%d") if p.created_at else ""),
                "status": p.status or "SUCCESS"
            })

        # Today's Attendance Overview
        today_date = now.date()
        today_records = Attendance.query.filter_by(attendance_date=today_date).all()
        today_present = sum(1 for r in today_records if r.status == "Present")
        today_absent = sum(1 for r in today_records if r.status == "Absent")
        today_total_marked = len(today_records)
        if today_total_marked > 0:
            today_attendance_rate = round((today_present / today_total_marked) * 100.0, 1)
        else:
            all_att_records = Attendance.query.all()
            if all_att_records:
                overall_pres = sum(1 for r in all_att_records if r.status == "Present")
                today_attendance_rate = round((overall_pres / len(all_att_records)) * 100.0, 1)
            else:
                today_attendance_rate = 100.0 if total > 0 else 0.0

        attendance_summary = {
            "total_students": total,
            "marked_today": today_total_marked,
            "present_today": today_present,
            "absent_today": today_absent,
            "attendance_rate": today_attendance_rate
        }

        # Department Performance Overview
        standard_depts = [
            "Computer Engineering",
            "Information Technology",
            "Artificial Intelligence & Data Science",
            "Electronics & Telecommunication",
            "Mechanical Engineering",
            "Civil Engineering",
            "Electrical Engineering"
        ]
        dept_overview = []
        for d in standard_depts:
            d_students = [s for s in all_students if (s.department or "").strip() == d]
            d_count = len(d_students)
            d_student_ids = [s.id for s in d_students]
            d_att_recs = Attendance.query.filter(Attendance.student_id.in_(d_student_ids)).all() if d_student_ids else []
            if d_att_recs:
                d_pres = sum(1 for r in d_att_recs if r.status == "Present")
                d_att_rate = round((d_pres / len(d_att_recs)) * 100.0, 1)
            else:
                d_att_rate = 100.0 if d_count > 0 else 0.0

            dept_overview.append({
                "name": d,
                "students_count": d_count,
                "attendance_rate": d_att_rate,
                "admissions_count": d_count
            })

        # Attention Required Alerts
        alerts = []
        if pending_count > 0:
            alerts.append({
                "type": "warning",
                "category": "Admissions",
                "title": "Pending Verification",
                "description": f"{pending_count} student admission application{'s' if pending_count > 1 else ''} require verification and document check.",
                "count": pending_count,
                "action_text": "Review Applications",
                "action_target": "pane-admissions"
            })

        # Low attendance check (< 75%)
        low_att_count = 0
        for s in all_students:
            st_att = Attendance.query.filter_by(student_id=s.id).all()
            if st_att:
                p_cnt = sum(1 for r in st_att if r.status == "Present")
                if round((p_cnt / len(st_att)) * 100.0, 1) < 75.0:
                    low_att_count += 1

        if low_att_count > 0:
            alerts.append({
                "type": "danger",
                "category": "Attendance",
                "title": "Low Attendance Alert",
                "description": f"{low_att_count} enrolled student{'s' if low_att_count > 1 else ''} currently below mandatory 75% attendance.",
                "count": low_att_count,
                "action_text": "Inspect Attendance",
                "action_target": "pane-attendance"
            })

        if pending_fees_students_count > 0:
            alerts.append({
                "type": "info",
                "category": "Payments",
                "title": "Outstanding Fee Dues",
                "description": f"{pending_fees_students_count} student{'s' if pending_fees_students_count > 1 else ''} have pending tuition fee balances totaling ₹ {total_pending_fees:,.2f}.",
                "count": pending_fees_students_count,
                "action_text": "View Payments",
                "action_target": "pane-fees"
            })

        # Recent Activity Stream
        activity = []
        for s in recent_objs[:4]:
            activity.append({
                "type": "admission",
                "title": "New Student Admission",
                "description": f"{s.fullName} registered for {s.department or 'Engineering'}.",
                "timestamp": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "Recently",
                "icon": "📝",
                "color": "#2563EB"
            })
        for p in recent_payment_objs[:3]:
            st = Student.query.get(p.student_id)
            st_name = st.fullName if st else f"Student #{p.student_id}"
            p_date_str = p.payment_date.strftime("%Y-%m-%d") if p.payment_date else (p.created_at.strftime("%Y-%m-%d") if p.created_at else "Recently")
            activity.append({
                "type": "payment",
                "title": "Fee Payment Recorded",
                "description": f"₹ {float(p.amount):,.0f} paid via {p.payment_method or 'UPI'} for {st_name}.",
                "timestamp": p_date_str,
                "icon": "💳",
                "color": "#059669"
            })

        return {
            "total": total,
            "total_departments": total_departments,
            "today_admissions": today_admissions,
            "month_admissions": month_admissions,
            "male_count": male_count,
            "female_count": female_count,
            "pending_count": pending_count,
            "review_count": review_count,
            "verified_count": verified_count,
            "rejected_count": rejected_count,
            "status_stats": status_stats,
            "total_fees_collected": total_fees_collected,
            "total_pending_fees": total_pending_fees,
            "total_fees_expected": total_fees_expected,
            "fee_collection_rate": fee_collection_rate,
            "paid_students_count": paid_students_count,
            "partial_paid_students_count": partial_paid_students_count,
            "pending_fees_students_count": pending_fees_students_count,
            "comp": dept_counts.get("Computer Engineering", 0),
            "it": dept_counts.get("Information Technology", 0),
            "aids": dept_counts.get("Artificial Intelligence & Data Science", 0),
            "mech": dept_counts.get("Mechanical Engineering", 0),
            "civil": dept_counts.get("Civil Engineering", 0),
            "dept_stats": dept_counts,
            "gender_stats": {
                "Male": male_count,
                "Female": female_count,
                "Other": other_gender
            },
            "admission_type_stats": admission_types,
            "monthly_trends": monthly_trends,
            "highest_dept": highest_dept,
            "lowest_dept": lowest_dept,
            "avg_score": avg_score,
            "avg_perc12": avg_perc12,
            "latest_student": latest_student,
            "recent_admissions": recent_admissions,
            "recent_payments": recent_payments,
            "attendance_summary": attendance_summary,
            "department_overview": dept_overview,
            "alerts": alerts,
            "activity": activity
        }

    @staticmethod
    def get_reports_analytics(filters=None):
        if filters is None:
            filters = {}

        acad_year_val = str(filters.get("academic_year", "all")).strip()
        semester_val = str(filters.get("semester", "all")).strip()
        department_val = str(filters.get("department", "all")).strip()
        program_val = str(filters.get("program", "all")).strip()

        start_date_val = filters.get("start_date")
        end_date_val = filters.get("end_date")

        # Base Student Query
        st_query = Student.query

        if department_val and department_val.lower() != "all":
            st_query = st_query.filter(Student.department == department_val)

        if program_val and program_val.lower() != "all":
            st_query = st_query.filter(Student.course.ilike(f"%{program_val}%"))

        if acad_year_val and acad_year_val.lower() != "all":
            if acad_year_val in ["1", "2", "3", "4"]:
                year_map = {"1": "1st Year", "2": "2nd Year", "3": "3rd Year", "4": "4th Year"}
                st_query = st_query.filter(
                    (Student.academic_year == acad_year_val) |
                    (Student.academic_year.ilike(f"%{year_map[acad_year_val]}%"))
                )
            else:
                st_query = st_query.filter(Student.academic_year == acad_year_val)

        if start_date_val:
            try:
                s_dt = datetime.strptime(start_date_val, "%Y-%m-%d")
                st_query = st_query.filter(Student.created_at >= s_dt)
            except ValueError:
                pass

        if end_date_val:
            try:
                e_dt = datetime.strptime(end_date_val, "%Y-%m-%d") + timedelta(days=1)
                st_query = st_query.filter(Student.created_at < e_dt)
            except ValueError:
                pass

        filtered_students = st_query.all()
        student_ids = [s.id for s in filtered_students]

        # Section 1 — Institution Overview
        all_departments = Department.query.all()
        all_courses = Course.query.all()
        all_subjects = Subject.query.all()

        total_students_count = len(filtered_students)
        active_students_count = sum(1 for s in filtered_students if s.is_enrolled or (s.status and s.status == "Verified"))
        inactive_students_count = total_students_count - active_students_count

        now = datetime.utcnow()
        new_admissions_count = sum(1 for s in filtered_students if s.created_at and s.created_at >= (now - timedelta(days=30)))

        overview = {
            "total_students": total_students_count,
            "active_students": active_students_count,
            "inactive_students": inactive_students_count,
            "total_departments": len(all_departments) if all_departments else 7,
            "total_programs": len(all_courses) if all_courses else 7,
            "total_courses_subjects": len(all_subjects) if all_subjects else 15,
            "new_admissions": new_admissions_count
        }

        # Section 2 — Student Analytics
        male_count = sum(1 for s in filtered_students if (s.gender or "").capitalize() == "Male")
        female_count = sum(1 for s in filtered_students if (s.gender or "").capitalize() == "Female")
        other_gender_count = max(0, total_students_count - (male_count + female_count))

        # Students by Department
        dept_dist = {}
        for s in filtered_students:
            d = s.department or "Unassigned"
            dept_dist[d] = dept_dist.get(d, 0) + 1

        students_by_department = [{"department": k, "count": v} for k, v in dept_dist.items()]

        # Students by Academic Year
        year_dist = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}
        for s in filtered_students:
            y_raw = str(s.academic_year or "")
            if "1" in y_raw or "1st" in y_raw: year_dist["1st Year"] += 1
            elif "2" in y_raw or "2nd" in y_raw: year_dist["2nd Year"] += 1
            elif "3" in y_raw or "3rd" in y_raw: year_dist["3rd Year"] += 1
            elif "4" in y_raw or "4th" in y_raw: year_dist["4th Year"] += 1
            else: year_dist["1st Year"] += 1

        students_by_academic_year = [{"year": k, "count": v} for k, v in year_dist.items()]

        # Students by Semester
        sem_dist = {f"Semester {i}": 0 for i in range(1, 9)}
        for s in filtered_students:
            y_raw = str(s.academic_year or "")
            if "2" in y_raw or "2nd" in y_raw:
                sem_dist["Semester 3"] += 1
            elif "3" in y_raw or "3rd" in y_raw:
                sem_dist["Semester 5"] += 1
            elif "4" in y_raw or "4th" in y_raw:
                sem_dist["Semester 7"] += 1
            else:
                sem_dist["Semester 1"] += 1

        students_by_semester = [{"semester": k, "count": v} for k, v in sem_dist.items()]

        student_analytics = {
            "total_students": total_students_count,
            "male_count": male_count,
            "female_count": female_count,
            "other_count": other_gender_count,
            "active_students": active_students_count,
            "inactive_students": inactive_students_count,
            "students_by_department": students_by_department,
            "students_by_academic_year": students_by_academic_year,
            "students_by_semester": students_by_semester
        }

        # Section 3 — Department Analytics
        dept_analytics = []
        for d in all_departments:
            if department_val and department_val.lower() != "all" and d.name != department_val:
                continue

            d_st = [s for s in filtered_students if (s.department or "").strip() == d.name]
            d_st_count = len(d_st)
            d_st_ids = [s.id for s in d_st]

            d_courses_count = sum(1 for c in all_courses if (c.department or "").strip() == d.name)
            capacity = d.total_seats or 60
            occupancy = round((d_st_count / capacity * 100.0), 1) if capacity > 0 else 0.0

            # Attendance for dept
            d_att_recs = Attendance.query.filter(Attendance.student_id.in_(d_st_ids)).all() if d_st_ids else []
            if d_att_recs:
                pres_c = sum(1 for r in d_att_recs if r.status == "Present")
                att_rate = round((pres_c / len(d_att_recs) * 100.0), 1)
            else:
                att_rate = 100.0 if d_st_count > 0 else 0.0

            # Exam performance for dept
            d_marks = ExamMark.query.filter(ExamMark.student_id.in_(d_st_ids)).all() if d_st_ids else []
            valid_marks = [m.percentage for m in d_marks if m.percentage is not None]
            avg_perf = round(sum(valid_marks) / len(valid_marks), 1) if valid_marks else 0.0

            dept_analytics.append({
                "id": d.id,
                "department": d.name,
                "code": d.code,
                "hod_name": d.hod_name or "To Be Appointed",
                "students": d_st_count,
                "courses": d_courses_count,
                "capacity": capacity,
                "occupancy": occupancy,
                "attendance": att_rate,
                "avg_performance": avg_perf,
                "status": d.status or "Active"
            })

        # Section 4 — Year & Semester Analytics
        year_semester_matrix = []
        sem_details = [
            {"year_num": 1, "year_label": "1st Year", "semesters": [1, 2]},
            {"year_num": 2, "year_label": "2nd Year", "semesters": [3, 4]},
            {"year_num": 3, "year_label": "3rd Year", "semesters": [5, 6]},
            {"year_num": 4, "year_label": "4th Year", "semesters": [7, 8]}
        ]

        for y_info in sem_details:
            y_num = y_info["year_num"]
            if acad_year_val and acad_year_val.lower() != "all" and acad_year_val in ["1", "2", "3", "4"] and str(y_num) != acad_year_val:
                continue

            for sem_num in y_info["semesters"]:
                if semester_val and semester_val.lower() != "all" and str(sem_num) != semester_val:
                    continue

                # Filter students for this year
                sem_st = [s for s in filtered_students if (
                    ("1" in str(s.academic_year or "") if y_num == 1 else
                     "2" in str(s.academic_year or "") if y_num == 2 else
                     "3" in str(s.academic_year or "") if y_num == 3 else
                     "4" in str(s.academic_year or "") if y_num == 4 else True)
                )]
                sem_st_ids = [s.id for s in sem_st]

                # Attendance
                sem_att = Attendance.query.filter(Attendance.student_id.in_(sem_st_ids)).all() if sem_st_ids else []
                if sem_att:
                    att_pct = round((sum(1 for r in sem_att if r.status == "Present") / len(sem_att) * 100.0), 1)
                else:
                    att_pct = 100.0 if sem_st else 0.0

                # Examination metrics for this year and semester
                exams_query = Examination.query.filter_by(academic_year=y_num, semester=sem_num)
                if department_val and department_val.lower() != "all":
                    exams_query = exams_query.filter_by(department=department_val)
                sem_exams = exams_query.all()
                sem_exam_ids = [e.id for e in sem_exams]

                if sem_exam_ids:
                    sem_marks = ExamMark.query.filter(ExamMark.exam_id.in_(sem_exam_ids)).all()
                    valid_pcts = [m.percentage for m in sem_marks if m.percentage is not None]
                    avg_m = round(sum(valid_pcts) / len(valid_pcts), 1) if valid_pcts else None
                    passed_cnt = sum(1 for m in sem_marks if m.result_status == "Pass")
                    pass_p = round((passed_cnt / len(sem_marks) * 100.0), 1) if sem_marks else None
                else:
                    avg_m = None
                    pass_p = None

                # Fee metrics
                sem_expected = 0.0
                sem_collected = 0.0
                for s in sem_st:
                    try:
                        _, s_tot = PaymentService.get_fee_breakdown_for_student(s)
                        s_pays = getattr(s, "payments", []) or []
                        s_pd = sum(float(p.amount) for p in s_pays if getattr(p, "status", "") in ["SUCCESS", "Paid"])
                        sem_expected += s_tot
                        sem_collected += s_pd
                    except Exception:
                        pass

                sem_collected = round(sem_collected, 2)
                sem_expected = round(sem_expected, 2)
                sem_pending = max(0.0, round(sem_expected - sem_collected, 2))
                fee_rate = round((sem_collected / sem_expected * 100.0), 1) if sem_expected > 0 else 0.0

                year_semester_matrix.append({
                    "academic_year": y_info["year_label"],
                    "year_num": y_num,
                    "semester": sem_num,
                    "semester_label": f"Semester {sem_num}",
                    "students": len(sem_st),
                    "attendance": att_pct,
                    "average_marks": avg_m,
                    "pass_percentage": pass_p,
                    "fee_collected": sem_collected,
                    "fee_expected": sem_expected,
                    "fee_collection_rate": fee_rate,
                    "pending_fees": sem_pending
                })

        # Section 5 — Attendance Analytics
        if student_ids:
            all_att_records = Attendance.query.filter(Attendance.student_id.in_(student_ids)).all()
        else:
            all_att_records = []

        total_att_marked = len(all_att_records)
        present_att_count = sum(1 for r in all_att_records if r.status == "Present")
        overall_avg_att = round((present_att_count / total_att_marked * 100.0), 1) if total_att_marked > 0 else (100.0 if total_students_count > 0 else 0.0)

        # Per student attendance rates
        above_75_count = 0
        below_75_count = 0
        critical_below_60_count = 0

        for s in filtered_students:
            st_recs = [r for r in all_att_records if r.student_id == s.id]
            if st_recs:
                st_rate = (sum(1 for r in st_recs if r.status == "Present") / len(st_recs)) * 100.0
            else:
                st_rate = 100.0

            if st_rate >= 75.0:
                above_75_count += 1
            else:
                below_75_count += 1
                if st_rate < 60.0:
                    critical_below_60_count += 1

        # Subject-wise attendance
        subject_att_list = []
        for subj in all_subjects:
            if department_val and department_val.lower() != "all" and subj.department != department_val:
                continue
            if semester_val and semester_val.lower() != "all" and str(subj.semester) != semester_val:
                continue

            d_st = [s for s in filtered_students if s.department == subj.department]
            d_st_ids = [s.id for s in d_st]
            d_att = [r for r in all_att_records if r.student_id in d_st_ids]
            if d_att:
                s_rate = round((sum(1 for r in d_att if r.status == "Present") / len(d_att) * 100.0), 1)
            else:
                s_rate = 85.0 if d_st else 100.0

            subject_att_list.append({
                "code": subj.code,
                "name": subj.name,
                "department": subj.department,
                "semester": subj.semester,
                "attendance": s_rate
            })

        attendance_analytics = {
            "overall_avg": overall_avg_att,
            "above_75_count": above_75_count,
            "below_75_count": below_75_count,
            "critical_below_60_count": critical_below_60_count,
            "subject_attendance": subject_att_list[:10]
        }

        # Section 6 — Examination Analytics
        exam_query = Examination.query
        if department_val and department_val.lower() != "all":
            exam_query = exam_query.filter(Examination.department == department_val)
        if program_val and program_val.lower() != "all":
            exam_query = exam_query.filter(Examination.program.ilike(f"%{program_val}%"))
        if acad_year_val and acad_year_val in ["1", "2", "3", "4"]:
            exam_query = exam_query.filter(Examination.academic_year == int(acad_year_val))
        if semester_val and semester_val.lower() != "all" and semester_val.isdigit():
            exam_query = exam_query.filter(Examination.semester == int(semester_val))

        filtered_exams = exam_query.all()
        exam_ids = [e.id for e in filtered_exams]

        total_exams = len(filtered_exams)
        completed_exams = sum(1 for e in filtered_exams if e.status == "Completed")
        upcoming_exams = sum(1 for e in filtered_exams if e.status in ["Scheduled", "Draft"])
        published_results = sum(1 for e in filtered_exams if e.status == "Published")
        pending_eval = sum(1 for e in filtered_exams if e.status in ["Ongoing", "Results Pending"])

        if exam_ids:
            marks_query = ExamMark.query.filter(ExamMark.exam_id.in_(exam_ids))
            if student_ids:
                marks_query = marks_query.filter(ExamMark.student_id.in_(student_ids))
            filtered_marks = marks_query.all()
        else:
            filtered_marks = []

        valid_percentages = [m.percentage for m in filtered_marks if m.percentage is not None]

        if valid_percentages:
            avg_marks = round(sum(valid_percentages) / len(valid_percentages), 1)
            highest_marks = round(max(valid_percentages), 1)
            lowest_marks = round(min(valid_percentages), 1)
            pass_cnt = sum(1 for m in filtered_marks if m.result_status == "Pass")
            fail_cnt = sum(1 for m in filtered_marks if m.result_status == "Fail")
            total_eval = len(filtered_marks)
            pass_rate = round((pass_cnt / total_eval * 100.0), 1) if total_eval > 0 else 0.0
            fail_rate = round((fail_cnt / total_eval * 100.0), 1) if total_eval > 0 else 0.0
        else:
            avg_marks = 0.0
            highest_marks = 0.0
            lowest_marks = 0.0
            pass_rate = 0.0
            fail_rate = 0.0

        examination_analytics = {
            "total_exams": total_exams,
            "completed_exams": completed_exams,
            "upcoming_exams": upcoming_exams,
            "published_results": published_results,
            "pending_evaluation": pending_eval,
            "avg_marks": avg_marks,
            "highest_marks": highest_marks,
            "lowest_marks": lowest_marks,
            "pass_percentage": pass_rate,
            "fail_percentage": fail_rate,
            "has_records": len(filtered_marks) > 0
        }

        # Section 7 — Fee Analytics
        fee_expected = 0.0
        fee_collected = 0.0
        paid_students = 0
        partial_students = 0
        pending_students = 0

        for s in filtered_students:
            try:
                _, s_tot = PaymentService.get_fee_breakdown_for_student(s)
                s_pays = getattr(s, "payments", []) or []
                s_pd = sum(float(p.amount) for p in s_pays if getattr(p, "status", "") in ["SUCCESS", "Paid"])
                fee_expected += s_tot
                fee_collected += s_pd

                if s_pd == 0.0:
                    pending_students += 1
                elif s_pd >= s_tot:
                    paid_students += 1
                else:
                    partial_students += 1
            except Exception:
                pass

        fee_collected = round(fee_collected, 2)
        fee_expected = round(fee_expected, 2)
        fee_outstanding = max(0.0, round(fee_expected - fee_collected, 2))
        fee_rate = round((fee_collected / fee_expected * 100.0), 1) if fee_expected > 0 else 0.0

        fee_analytics = {
            "total_expected": fee_expected,
            "total_collected": fee_collected,
            "total_outstanding": fee_outstanding,
            "collection_rate": fee_rate,
            "paid_students": paid_students,
            "partial_students": partial_students,
            "pending_students": pending_students
        }

        # Section 8 — Performance Analytics
        has_performance_data = len(valid_percentages) > 0

        if has_performance_data:
            dept_perf = []
            for d in dept_analytics:
                if d["students"] > 0:
                    dept_perf.append({
                        "department": d["department"],
                        "avg_performance": d["avg_performance"],
                        "attendance": d["attendance"]
                    })

            performance_analytics = {
                "has_data": True,
                "avg_performance": avg_marks,
                "pass_rate": pass_rate,
                "fail_rate": fail_rate,
                "dept_comparison": dept_perf
            }
        else:
            performance_analytics = {
                "has_data": False,
                "message": "Performance data is not available for the selected filters."
            }

        return {
            "filters": {
                "academic_year": acad_year_val,
                "semester": semester_val,
                "department": department_val,
                "program": program_val,
                "start_date": start_date_val or "",
                "end_date": end_date_val or ""
            },
            "overview": overview,
            "student_analytics": student_analytics,
            "department_analytics": dept_analytics,
            "year_semester_matrix": year_semester_matrix,
            "attendance_analytics": attendance_analytics,
            "examination_analytics": examination_analytics,
            "fee_analytics": fee_analytics,
            "performance_analytics": performance_analytics
        }

    @staticmethod
    def generate_pdf_report(report_type, filters=None):
        analytics = AnalyticsService.get_reports_analytics(filters)
        pdf_buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        styles = getSampleStyleSheet()
        normal = styles["Normal"]

        title_style = ParagraphStyle(
            "HeaderTitle",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            alignment=1,
            textColor=colors.HexColor("#1e3a8a")
        )

        sub_style = ParagraphStyle(
            "HeaderSub",
            parent=normal,
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            alignment=1,
            textColor=colors.HexColor("#475569")
        )

        banner_style = ParagraphStyle(
            "BannerText",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            alignment=1,
            textColor=colors.white
        )

        th_style = ParagraphStyle(
            "THStyle",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10,
            textColor=colors.HexColor("#1e3a8a")
        )

        td_style = ParagraphStyle(
            "TDStyle",
            parent=normal,
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1e293b")
        )

        td_bold = ParagraphStyle(
            "TDBold",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0f172a")
        )

        elements = []

        # 1. Branding Header
        elements.append(Paragraph("ZEAL COLLEGE OF ENGINEERING AND RESEARCH", title_style))
        elements.append(Paragraph("Approved by AICTE, Affiliated to Savitribai Phule Pune University (SPPU)", sub_style))
        elements.append(Paragraph("Survey No. 39, Narhe, Pune - 411041, Maharashtra, India", sub_style))
        elements.append(Spacer(1, 4 * mm))

        # Report Title
        report_titles = {
            "student": "INSTITUTIONAL STUDENT ENROLLMENT REPORT",
            "department": "DEPARTMENT PERFORMANCE & CAPACITY AUDIT REPORT",
            "attendance": "ACADEMIC ATTENDANCE AUDIT REPORT",
            "examination": "EXAMINATION & EVALUATION SUMMARY REPORT",
            "result": "STUDENT ACADEMIC PERFORMANCE REPORT",
            "fee": "FEE COLLECTION & REVENUE AUDIT REPORT",
            "pending_fee": "OUTSTANDING FEE DUES AUDIT REPORT"
        }
        r_title = report_titles.get(report_type, "OFFICIAL INSTITUTIONAL ANALYTICS REPORT")

        banner = Table([[Paragraph(r_title, banner_style)]], colWidths=[180 * mm])
        banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1e3a8a")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(banner)
        elements.append(Spacer(1, 4 * mm))

        # 2. Filter Summary Box
        f_info = analytics["filters"]
        gen_date = datetime.utcnow().strftime("%d-%b-%Y %I:%M %p")
        filter_data = [
            [
                Paragraph("<b>Generated Date:</b>", td_style), Paragraph(gen_date, td_style),
                Paragraph("<b>Academic Year:</b>", td_style), Paragraph(f_info['academic_year'].title(), td_style)
            ],
            [
                Paragraph("<b>Department:</b>", td_style), Paragraph(f_info['department'].title(), td_style),
                Paragraph("<b>Semester:</b>", td_style), Paragraph(f_info['semester'].title(), td_style)
            ]
        ]
        filter_table = Table(filter_data, colWidths=[38 * mm, 52 * mm, 38 * mm, 52 * mm])
        filter_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(filter_table)
        elements.append(Spacer(1, 4 * mm))

        # 3. Dynamic Section Content & Tables
        if report_type == "student":
            st_stats = analytics["student_analytics"]
            summary_grid = [
                [Paragraph("Total Students", th_style), Paragraph("Male", th_style), Paragraph("Female", th_style), Paragraph("Active", th_style)],
                [Paragraph(str(st_stats["total_students"]), td_bold), Paragraph(str(st_stats["male_count"]), td_style), Paragraph(str(st_stats["female_count"]), td_style), Paragraph(str(st_stats["active_students"]), td_style)]
            ]
            t = Table(summary_grid, colWidths=[45 * mm, 45 * mm, 45 * mm, 45 * mm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 4 * mm))

            dept_rows = [[Paragraph("Department", th_style), Paragraph("Enrolled Students", th_style)]]
            for row in st_stats["students_by_department"]:
                dept_rows.append([Paragraph(row["department"], td_style), Paragraph(str(row["count"]), td_bold)])
            dt = Table(dept_rows, colWidths=[120 * mm, 60 * mm])
            dt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(dt)

        elif report_type == "department":
            dept_rows = [[Paragraph("Department", th_style), Paragraph("Students", th_style), Paragraph("Courses", th_style), Paragraph("Capacity", th_style), Paragraph("Occupancy %", th_style), Paragraph("Attendance %", th_style)]]
            for d in analytics["department_analytics"]:
                dept_rows.append([
                    Paragraph(d["department"], td_style),
                    Paragraph(str(d["students"]), td_style),
                    Paragraph(str(d["courses"]), td_style),
                    Paragraph(str(d["capacity"]), td_style),
                    Paragraph(f"{d['occupancy']}%", td_style),
                    Paragraph(f"{d['attendance']}%", td_bold)
                ])
            dt = Table(dept_rows, colWidths=[55 * mm, 25 * mm, 25 * mm, 25 * mm, 25 * mm, 25 * mm])
            dt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(dt)

        elif report_type in ["fee", "pending_fee"]:
            fees = analytics["fee_analytics"]
            f_rows = [
                [Paragraph("Metric", th_style), Paragraph("Amount (INR)", th_style)],
                [Paragraph("Total Expected Fees", td_style), Paragraph(f"Rs. {fees['total_expected']:,.2f}", td_style)],
                [Paragraph("Total Fees Collected", td_style), Paragraph(f"Rs. {fees['total_collected']:,.2f}", td_bold)],
                [Paragraph("Total Outstanding Dues", td_style), Paragraph(f"Rs. {fees['total_outstanding']:,.2f}", td_bold)],
                [Paragraph("Collection Rate", td_style), Paragraph(f"{fees['collection_rate']}%", td_bold)]
            ]
            ft = Table(f_rows, colWidths=[110 * mm, 70 * mm])
            ft.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(ft)

        else:
            m_rows = [[Paragraph("Academic Year", th_style), Paragraph("Semester", th_style), Paragraph("Students", th_style), Paragraph("Attendance %", th_style), Paragraph("Pass %", th_style), Paragraph("Fee Collection %", th_style)]]
            for row in analytics["year_semester_matrix"]:
                m_rows.append([
                    Paragraph(row["academic_year"], td_style),
                    Paragraph(row["semester_label"], td_style),
                    Paragraph(str(row["students"]), td_style),
                    Paragraph(f"{row['attendance']}%", td_style),
                    Paragraph(f"{row['pass_percentage']}%" if row['pass_percentage'] is not None else "N/A", td_style),
                    Paragraph(f"{row['fee_collection_rate']}%", td_bold)
                ])
            mt = Table(m_rows, colWidths=[35 * mm, 35 * mm, 25 * mm, 30 * mm, 25 * mm, 30 * mm])
            mt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(mt)

        elements.append(Spacer(1, 8 * mm))

        sig_data = [
            [
                Paragraph("<b>Generated By:</b><br/>Institutional ERP System", td_style),
                Paragraph("<b>Verification Seal:</b><br/><font color=\"#64748b\">[Digitally Verified Report]</font>", td_style),
                Paragraph("<b>Principal / Controller of Examinations:</b><br/><br/>_______________________", td_style)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[60 * mm, 60 * mm, 60 * mm])
        sig_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ]))
        elements.append(KeepTogether([
            sig_table,
            Spacer(1, 4 * mm),
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=2),
            Paragraph("<font size=\"7\" color=\"#64748b\">Zeal College of Engineering and Research — Official Confidential Report</font>", sub_style)
        ]))

        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer

    @staticmethod
    def generate_csv_report(report_type, filters=None):
        analytics = AnalyticsService.get_reports_analytics(filters)
        output = io.StringIO()
        writer = csv.writer(output)

        if report_type == "student":
            writer.writerow(["Department", "Student Count"])
            for row in analytics["student_analytics"]["students_by_department"]:
                writer.writerow([row["department"], row["count"]])
        elif report_type == "department":
            writer.writerow(["Department", "Code", "HOD", "Students", "Courses", "Capacity", "Occupancy %", "Attendance %", "Avg Performance %"])
            for d in analytics["department_analytics"]:
                writer.writerow([d["department"], d["code"], d["hod_name"], d["students"], d["courses"], d["capacity"], d["occupancy"], d["attendance"], d["avg_performance"]])
        elif report_type in ["fee", "pending_fee"]:
            writer.writerow(["Metric", "Value"])
            fees = analytics["fee_analytics"]
            writer.writerow(["Total Expected Fees", fees["total_expected"]])
            writer.writerow(["Total Collected", fees["total_collected"]])
            writer.writerow(["Total Outstanding", fees["total_outstanding"]])
            writer.writerow(["Collection Rate %", fees["collection_rate"]])
        else:
            writer.writerow(["Academic Year", "Semester", "Students", "Attendance %", "Pass %", "Fee Collection %", "Pending Fees"])
            for row in analytics["year_semester_matrix"]:
                writer.writerow([row["academic_year"], row["semester_label"], row["students"], row["attendance"], row["pass_percentage"] or "N/A", row["fee_collection_rate"], row["pending_fees"]])

        return output.getvalue()
