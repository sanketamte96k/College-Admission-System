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

