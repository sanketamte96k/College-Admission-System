import time
import uuid
from datetime import datetime
from models import db, Student, Payment
from utils import sanitize_input

class PaymentService:
    FEE_CATEGORIES = [
        "Tuition Fee",
        "Development Fee",
        "Examination Fee",
        "Library Fee",
        "Laboratory Fee",
        "Other Fee"
    ]

    PAYMENT_METHODS = [
        "Cash",
        "Bank Transfer",
        "UPI",
        "Online Payment",
        "Demand Draft"
    ]

    # Department Base Fee Structure (Annual)
    DEPARTMENT_BASE_FEES = {
        "Computer Engineering": {
            "Tuition Fee": 75000.0,
            "Development Fee": 15000.0,
            "Examination Fee": 5000.0,
            "Library Fee": 5000.0,
            "Laboratory Fee": 7000.0,
            "Other Fee": 3000.0
        },
        "Information Technology": {
            "Tuition Fee": 72000.0,
            "Development Fee": 14000.0,
            "Examination Fee": 5000.0,
            "Library Fee": 5000.0,
            "Laboratory Fee": 6000.0,
            "Other Fee": 3000.0
        },
        "Artificial Intelligence & Data Science": {
            "Tuition Fee": 74000.0,
            "Development Fee": 15000.0,
            "Examination Fee": 5000.0,
            "Library Fee": 5000.0,
            "Laboratory Fee": 6000.0,
            "Other Fee": 3000.0
        },
        "Mechanical Engineering": {
            "Tuition Fee": 65000.0,
            "Development Fee": 13000.0,
            "Examination Fee": 5000.0,
            "Library Fee": 4000.0,
            "Laboratory Fee": 5000.0,
            "Other Fee": 3000.0
        },
        "Civil Engineering": {
            "Tuition Fee": 62000.0,
            "Development Fee": 12000.0,
            "Examination Fee": 5000.0,
            "Library Fee": 4000.0,
            "Laboratory Fee": 4000.0,
            "Other Fee": 3000.0
        }
    }

    DEFAULT_BASE_FEE = {
        "Tuition Fee": 65000.0,
        "Development Fee": 13000.0,
        "Examination Fee": 5000.0,
        "Library Fee": 4000.0,
        "Laboratory Fee": 5000.0,
        "Other Fee": 3000.0
    }

    @staticmethod
    def get_fee_breakdown_for_student(student):
        """Calculate dynamic fee breakdown based on department and admission quota"""
        dept = (student.department or "").strip()
        base = dict(PaymentService.DEPARTMENT_BASE_FEES.get(dept, PaymentService.DEFAULT_BASE_FEE))

        # Quota adjustments
        quota = (student.admissionType or "CAP").strip().upper()
        if quota == "MANAGEMENT":
            base["Development Fee"] += 25000.0
        elif quota == "NRI":
            base["Development Fee"] += 50000.0

        total = sum(base.values())
        return base, total

    @staticmethod
    def get_student_fee_summary(student_id):
        """
        Get complete fee details for a student including:
        - Total Fee
        - Fee Breakdown by Category
        - Paid Amount
        - Pending Amount
        - Payment Status (Paid, Partially Paid, Pending)
        - Payment History
        """
        student = Student.query.get(student_id)
        if not student:
            return None

        breakdown, total_fee = PaymentService.get_fee_breakdown_for_student(student)
        payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.id.desc()).all()

        paid_amount = sum(float(p.amount) for p in payments if p.status in ["SUCCESS", "Paid"])
        pending_amount = max(0.0, round(total_fee - paid_amount, 2))
        paid_amount = round(paid_amount, 2)

        # Determine Payment Status
        if paid_amount == 0.0:
            payment_status = "Pending"
        elif paid_amount >= total_fee:
            payment_status = "Paid"
        else:
            payment_status = "Partially Paid"

        return {
            "student_id": student.id,
            "student_name": student.fullName,
            "department": student.department,
            "admission_type": student.admissionType,
            "total_fee": round(total_fee, 2),
            "paid_amount": paid_amount,
            "pending_amount": pending_amount,
            "payment_status": payment_status,
            "fee_breakdown": breakdown,
            "payments": [p.to_dict() for p in payments],
            "payment_count": len(payments)
        }

    @staticmethod
    def record_payment(
        student_id,
        amount,
        fee_type="Tuition Fee",
        payment_method="UPI",
        transaction_id=None,
        remarks="",
        admin_username="admin",
        payment_date=None
    ):
        """
        Record a fee payment transaction with strict validation and balance updates.
        """
        student = Student.query.get(student_id)
        if not student:
            return None, "Student record not found"

        # Validate amount
        try:
            val_amount = float(amount)
            if val_amount <= 0:
                return None, "Payment amount must be greater than zero."
        except (ValueError, TypeError):
            return None, "Invalid payment amount format."

        # Validate fee type
        clean_fee_type = (fee_type or "Tuition Fee").strip()
        if clean_fee_type not in PaymentService.FEE_CATEGORIES:
            clean_fee_type = "Tuition Fee"

        # Validate payment method
        clean_method = (payment_method or "UPI").strip()

        # Handle transaction / reference ID
        if transaction_id and str(transaction_id).strip():
            clean_txn_id = str(transaction_id).strip()
            existing = Payment.query.filter_by(transaction_id=clean_txn_id).first()
            if existing:
                return None, f"Transaction ID '{clean_txn_id}' has already been recorded."
        else:
            ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            short_id = uuid.uuid4().hex[:6].upper()
            clean_txn_id = f"ZEAL-PAY-{ts}-{short_id}"

        # Payment Date
        if isinstance(payment_date, str) and payment_date.strip():
            try:
                p_date = datetime.strptime(payment_date.strip(), "%Y-%m-%d")
            except Exception:
                p_date = datetime.utcnow()
        elif isinstance(payment_date, datetime):
            p_date = payment_date
        else:
            p_date = datetime.utcnow()

        clean_remarks = sanitize_input(remarks or "")

        payment = Payment(
            student_id=student_id,
            fee_type=clean_fee_type,
            amount=val_amount,
            payment_method=clean_method,
            payment_mode=clean_method,
            payment_date=p_date,
            transaction_id=clean_txn_id,
            status="SUCCESS",
            remarks=clean_remarks,
            recorded_by=admin_username or "admin"
        )

        try:
            db.session.add(payment)
            db.session.commit()
            updated_summary = PaymentService.get_student_fee_summary(student_id)
            return {
                "payment": payment.to_dict(),
                "summary": updated_summary
            }, "Fee payment recorded successfully."
        except Exception as e:
            db.session.rollback()
            return None, f"Database error recording payment: {str(e)}"

    @staticmethod
    def get_payment_history(student_id):
        """Fetch chronological list of payments for a student"""
        payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.id.desc()).all()
        return [p.to_dict() for p in payments]

    @staticmethod
    def get_fee_dashboard_summary():
        """Aggregated fee collection metrics for ERP fee dashboard"""
        all_students = Student.query.all()
        all_payments = Payment.query.filter(Payment.status.in_(["SUCCESS", "Paid"])).all()

        total_expected = 0.0
        student_summaries = []

        for st in all_students:
            _, total_fee = PaymentService.get_fee_breakdown_for_student(st)
            total_expected += total_fee
            st_payments = [p for p in all_payments if p.student_id == st.id]
            paid = sum(float(p.amount) for p in st_payments)
            pending = max(0.0, round(total_fee - paid, 2))
            student_summaries.append({
                "student": st,
                "total_fee": total_fee,
                "paid": paid,
                "pending": pending
            })

        total_collected = round(sum(float(p.amount) for p in all_payments), 2)
        total_pending = round(max(0.0, total_expected - total_collected), 2)

        # Monthly & Today collections
        now = datetime.utcnow()
        this_month_collection = sum(
            float(p.amount) for p in all_payments
            if p.payment_date and p.payment_date.year == now.year and p.payment_date.month == now.month
        )
        today_collection = sum(
            float(p.amount) for p in all_payments
            if p.payment_date and p.payment_date.date() == now.date()
        )

        fully_paid_count = sum(1 for s in student_summaries if s["pending"] <= 0)
        pending_students_count = sum(1 for s in student_summaries if s["pending"] > 0)
        partially_paid_count = sum(1 for s in student_summaries if 0 < s["paid"] < s["total_fee"])
        overdue_count = sum(1 for s in student_summaries if s["pending"] > 0 and s["paid"] == 0)

        return {
            "total_expected": round(total_expected, 2),
            "total_collected": total_collected,
            "total_pending": total_pending,
            "this_month_collection": round(this_month_collection, 2),
            "today_collection": round(today_collection, 2),
            "fully_paid_count": fully_paid_count,
            "pending_students_count": pending_students_count,
            "partially_paid_count": partially_paid_count,
            "overdue_count": overdue_count,
            "total_students": len(all_students)
        }

    @staticmethod
    def get_all_student_fees(department="", program="", academic_year="", semester="", fee_status="", search=""):
        """Get filtered fee ledger list for all students"""
        query = Student.query

        if department:
            query = query.filter(Student.department == department)
        if search:
            sq = search.strip()
            query = query.filter(
                db.or_(
                    Student.fullName.ilike(f"%{sq}%"),
                    Student.email.ilike(f"%{sq}%"),
                    Student.mobile.ilike(f"%{sq}%"),
                    Student.enrollment_number.ilike(f"%{sq}%")
                )
            )

        students = query.order_by(Student.id.asc()).all()

        results = []
        for st in students:
            summary = PaymentService.get_student_fee_summary(st.id)
            if not summary:
                continue

            status = summary["payment_status"]
            if fee_status:
                if fee_status == "Paid" and status != "Paid": continue
                if fee_status == "Partially Paid" and status != "Partially Paid": continue
                if fee_status == "Pending" and status != "Pending": continue
                if fee_status == "Overdue" and (status != "Pending" or summary["paid_amount"] > 0): continue

            results.append({
                "student_id": st.id,
                "student_name": st.fullName,
                "enrollment_number": st.enrollment_number or f"STU-{st.id:04d}",
                "department": st.department,
                "course": st.course or "B.Tech Computer Engineering",
                "academic_year": st.academic_year or "2026-27",
                "admission_type": st.admissionType or "CAP",
                "total_fee": summary["total_fee"],
                "paid_amount": summary["paid_amount"],
                "pending_amount": summary["pending_amount"],
                "status": status,
                "due_date": "2026-10-31",
                "fee_breakdown": summary["fee_breakdown"],
                "payment_count": summary["payment_count"]
            })

        return results

    @staticmethod
    def get_all_payment_history(department="", fee_type="", payment_method="", search=""):
        """Get master payment history across all students"""
        query = Payment.query.order_by(Payment.id.desc())

        if fee_type:
            query = query.filter(Payment.fee_type == fee_type)
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)

        payments = query.all()
        results = []
        for p in payments:
            p_dict = p.to_dict()
            st = Student.query.get(p.student_id)
            p_dict["student_name"] = st.fullName if st else "Unknown Student"
            p_dict["department"] = st.department if st else ""
            p_dict["enrollment_number"] = (st.enrollment_number or f"STU-{st.id:04d}") if st else ""
            results.append(p_dict)

        return results

    @staticmethod
    def process_payment(student_id, amount=95000.0, payment_mode="UPI / Online"):
        """Legacy simulator method for backward compatibility"""
        res, msg = PaymentService.record_payment(
            student_id=student_id,
            amount=amount,
            fee_type="Tuition Fee",
            payment_method=payment_mode,
            remarks="Online portal payment"
        )
        if res:
            return res["payment"], msg
        return None, msg


