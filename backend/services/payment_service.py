import time
from models import db, Student, Payment

class PaymentService:
    @staticmethod
    def process_payment(student_id, amount=95000.0, payment_mode="UPI / Online"):
        """Simulate online fee payment processing and record transaction"""
        student = Student.query.get(student_id)
        if not student:
            return None, "Student record not found"

        transaction_id = f"TXN_{int(time.time())}_{student_id}"

        payment = Payment(
            student_id=student_id,
            transaction_id=transaction_id,
            amount=amount,
            payment_mode=payment_mode,
            status="SUCCESS"
        )

        db.session.add(payment)
        student.status = "Approved"
        db.session.commit()

        return payment.to_dict(), "Payment processed successfully"

    @staticmethod
    def get_payment_history(student_id):
        payments = Payment.query.filter_by(student_id=student_id).all()
        return [p.to_dict() for p in payments]
