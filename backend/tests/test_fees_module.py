import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db, Student, Payment

class FeesModuleTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["TESTING"] = "True"
        self.app = create_app("test")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Admin test session
        with self.client.session_transaction() as sess:
            sess["admin_id"] = 1
            sess["username"] = "admin"

        # Create sample test student
        self.test_student = Student(
            fullName="Amit Sharma",
            fatherName="Rajesh Sharma",
            motherName="Anita Sharma",
            dob="2003-08-20",
            gender="Male",
            bloodGroup="B+",
            mobile="9876543211",
            email="amit.sharma@example.com",
            aadhaar="123456789013",
            address="Pune",
            city="Pune",
            state="Maharashtra",
            pincode="411041",
            nationality="Indian",
            board10="SSC",
            percentage10=90.0,
            board12="HSC",
            percentage12=88.5,
            entranceExam="MHT-CET",
            entranceScore=96.0,
            department="Computer Engineering",
            course="B.Tech Computer Engineering",
            academic_year="2026-27",
            admissionType="CAP Round 1",
            enrollment_number="EN2026-COMP-101",
            status="Enrolled"
        )
        db.session.add(self.test_student)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_fee_dashboard_and_roster(self):
        # Fetch dashboard summary
        res = self.client.get("/api/fees/dashboard")
        self.assertEqual(res.status_code, 200)
        dash = res.get_json()
        self.assertIn("total_expected", dash)
        self.assertIn("total_collected", dash)
        self.assertIn("total_pending", dash)

        # Fetch student fee roster
        res_r = self.client.get("/api/fees/students")
        self.assertEqual(res_r.status_code, 200)
        roster = res_r.get_json()
        self.assertGreater(len(roster), 0)

    def test_record_payment_and_pdf_receipt(self):
        st_id = self.test_student.id

        # 1. Record valid payment
        pay_payload = {
            "amount": 40000.0,
            "fee_type": "Tuition Fee",
            "payment_method": "UPI",
            "transaction_id": "TEST-UPI-99887766",
            "remarks": "Part payment of tuition fee"
        }
        res_p = self.client.post(f"/api/students/{st_id}/payments", json=pay_payload)
        self.assertEqual(res_p.status_code, 201)
        p_data = res_p.get_json()
        pay_id = p_data["payment"]["id"]

        # 2. Verify balance update
        res_summary = self.client.get(f"/api/students/{st_id}/fees")
        self.assertEqual(res_summary.status_code, 200)
        s_data = res_summary.get_json()
        self.assertEqual(s_data["paid_amount"], 40000.0)
        self.assertEqual(s_data["payment_status"], "Partially Paid")

        # 3. Test PDF receipt generation stream
        res_pdf = self.client.get(f"/api/payments/{pay_id}/receipt")
        self.assertEqual(res_pdf.status_code, 200)
        self.assertEqual(res_pdf.mimetype, "application/pdf")
        self.assertGreater(len(res_pdf.data), 1000)

    def test_payment_validation_rules(self):
        st_id = self.test_student.id

        # Invalid zero amount rejected
        res_zero = self.client.post(f"/api/students/{st_id}/payments", json={"amount": 0})
        self.assertEqual(res_zero.status_code, 400)

        # Invalid negative amount rejected
        res_neg = self.client.post(f"/api/students/{st_id}/payments", json={"amount": -500})
        self.assertEqual(res_neg.status_code, 400)

if __name__ == "__main__":
    unittest.main()
