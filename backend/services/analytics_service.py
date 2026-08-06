from datetime import datetime, timedelta
from models import Student

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
        other_gender = total - (male_count + female_count)

        dept_counts = {}
        for s in all_students:
            dept = s.department or "Other"
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        total_departments = len(dept_counts) if dept_counts else 6

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

        recent_objs = Student.query.order_by(Student.id.desc()).limit(10).all()
        recent_admissions = [{
            "id": s.id,
            "photo": s.photo or "",
            "fullName": s.fullName,
            "department": s.department,
            "admissionType": s.admissionType,
            "created_at": s.created_at.strftime("%Y-%m-%d") if s.created_at else "",
            "status": s.status or "Pending Verification"
        } for s in recent_objs]

        return {
            "total": total,
            "total_departments": total_departments,
            "today_admissions": today_admissions,
            "month_admissions": month_admissions,
            "male_count": male_count,
            "female_count": female_count,
            "comp": dept_counts.get("Computer Engineering", 0),
            "it": dept_counts.get("Information Technology", 0),
            "aids": dept_counts.get("Artificial Intelligence & Data Science", 0),
            "mech": dept_counts.get("Mechanical Engineering", 0),
            "civil": dept_counts.get("Civil Engineering", 0),
            "dept_stats": dept_counts,
            "gender_stats": {
                "Male": male_count,
                "Female": female_count,
                "Other": max(0, other_gender)
            },
            "admission_type_stats": admission_types,
            "monthly_trends": monthly_trends,
            "highest_dept": highest_dept,
            "lowest_dept": lowest_dept,
            "avg_score": avg_score,
            "avg_perc12": avg_perc12,
            "latest_student": latest_student,
            "recent_admissions": recent_admissions
        }
