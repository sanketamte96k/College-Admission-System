from datetime import datetime, timedelta
from models import Student, Payment, Attendance

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
        from .payment_service import PaymentService
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
