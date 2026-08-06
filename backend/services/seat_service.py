from datetime import datetime
from models import db, Student, SeatMatrix, Payment

DEFAULT_SEAT_MATRIX = [
    ("Computer Engineering", 120, 80.0),
    ("Information Technology", 60, 75.0),
    ("Artificial Intelligence & Data Science", 60, 75.0),
    ("Electronics & Telecommunication", 60, 60.0),
    ("Mechanical Engineering", 60, 50.0),
    ("Civil Engineering", 60, 50.0)
]

class SeatService:
    @staticmethod
    def initialize_seat_matrix():
        """Ensure seat matrix database table is populated with default branches"""
        for dept, seats, cutoff in DEFAULT_SEAT_MATRIX:
            matrix = SeatMatrix.query.filter_by(department=dept).first()
            if not matrix:
                matrix = SeatMatrix(department=dept, total_seats=seats, filled_seats=0, cutoff_score=cutoff)
                db.session.add(matrix)
        db.session.commit()

    @staticmethod
    def get_seat_matrix():
        SeatService.initialize_seat_matrix()
        matrices = SeatMatrix.query.all()
        result = []
        for m in matrices:
            filled = Student.query.filter_by(department=m.department).count()
            m.filled_seats = filled
            result.append(m.to_dict())
        db.session.commit()
        return result

    @staticmethod
    def generate_merit_list(department=None):
        """Generate merit ranking list based on Entrance Score & 12th Percentage"""
        query = Student.query
        if department:
            query = query.filter(Student.department == department)

        # Rank by entranceScore descending, then percentage12 descending
        students = query.order_by(Student.entranceScore.desc(), Student.percentage12.desc()).all()

        merit_list = []
        for rank, s in enumerate(students, 1):
            merit_list.append({
                "merit_rank": rank,
                "id": s.id,
                "fullName": s.fullName,
                "department": s.department,
                "entranceScore": s.entranceScore,
                "percentage12": s.percentage12,
                "admissionType": s.admissionType,
                "status": s.status or "Pending Verification",
                "cap_round_eligible": "CAP Round 1" if rank <= 60 else ("CAP Round 2" if rank <= 120 else "Waiting List")
            })

        return merit_list

    @staticmethod
    def generate_reports():
        """Generate comprehensive administrative ERP reports"""
        all_students = Student.query.all()
        total_students = len(all_students)

        now = datetime.utcnow()
        today_count = Student.query.filter(Student.created_at >= datetime(now.year, now.month, now.day)).count()

        all_payments = Payment.query.all()
        total_revenue = sum(p.amount for p in all_payments if p.status == "SUCCESS")

        dept_reports = {}
        for s in all_students:
            d = s.department or "Other"
            dept_reports[d] = dept_reports.get(d, 0) + 1

        return {
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "daily_report": {
                "date": now.strftime("%Y-%m-%d"),
                "new_admissions_today": today_count
            },
            "monthly_report": {
                "month": now.strftime("%B %Y"),
                "total_admissions": total_students
            },
            "department_report": dept_reports,
            "revenue_report": {
                "total_transactions": len(all_payments),
                "total_revenue_collected": total_revenue,
                "currency": "INR"
            }
        }
