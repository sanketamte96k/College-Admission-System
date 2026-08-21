import os
import sys
import unittest
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from models import db, Student, Admin, SeatMatrix

class TestAdmissionsModule(unittest.TestCase):

    def setUp(self):
        os.environ["FLASK_ENV"] = "test"
        os.environ["TESTING"] = "True"
        self.app = create_app("test")
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Ensure seat matrix entry
            if not SeatMatrix.query.filter_by(department="Computer Engineering").first():
                seat = SeatMatrix(department="Computer Engineering", total_seats=60, filled_seats=0)
                db.session.add(seat)
                db.session.commit()

        # Admin login
        res = self.client.post("/api/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_admissions_end_to_end_flow(self):
        with self.app.app_context():
            # 1. Create a candidate admission
            candidate_data = {
                "fullName": "Sanket Amte",
                "fatherName": "Rajesh Amte",
                "motherName": "Sunita Amte",
                "dob": "2002-05-15",
                "gender": "Male",
                "bloodGroup": "O+",
                "mobile": "9876543210",
                "altMobile": "9876543211",
                "email": "sanket@zeal.edu.in",
                "aadhaar": "123456789012",
                "address": "Zeal Campus, Narhe",
                "city": "Pune",
                "state": "Maharashtra",
                "pincode": "411041",
                "nationality": "Indian",
                "board10": "State Board",
                "percentage10": "89.5",
                "board12": "HSC",
                "percentage12": "87.2",
                "entranceExam": "MHT-CET",
                "entranceScore": "95.5",
                "department": "Computer Engineering",
                "course": "B.Tech Computer Science",
                "admissionType": "CAP",
                "academic_year": "2026-27"
            }

            res = self.client.post("/api/students", data=candidate_data)
            self.assertEqual(res.status_code, 201)

            st = Student.query.filter_by(email="sanket@zeal.edu.in").first()
            self.assertIsNotNone(st)
            st_id = st.id
            self.assertEqual(st.status, "Pending Verification")
            self.assertEqual(st.to_dict()["application_id"], f"ADM-2026-{st_id:04d}")

            # 2. Test Admissions Analytics
            res = self.client.get("/api/admissions/analytics")
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data["total_applications"], 1)
            self.assertEqual(data["pending_review"], 1)

            # 3. Test Verify Document
            res = self.client.post(f"/api/admissions/{st_id}/verify-document", json={
                "doc_type": "10th",
                "status": "Verified"
            })
            self.assertEqual(res.status_code, 200)
            st = Student.query.get(st_id)
            self.assertEqual(st.doc_status_10th, "Verified")

            # 4. Test Approve Application
            res = self.client.post(f"/api/admissions/{st_id}/approve")
            self.assertEqual(res.status_code, 200)
            st = Student.query.get(st_id)
            self.assertEqual(st.status, "Approved")

            # 5. Test Convert to Student
            res = self.client.post(f"/api/admissions/{st_id}/convert-to-student")
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertTrue(data["success"])
            self.assertTrue(data["enrollment_number"].startswith("124BT"))

            st = Student.query.get(st_id)
            self.assertEqual(st.status, "Enrolled")
            self.assertTrue(st.is_enrolled)

            # Seat Matrix filled seat check
            seat = SeatMatrix.query.filter_by(department="Computer Engineering").first()
            self.assertEqual(seat.filled_seats, 1)

            # 6. Test Prevent Duplicate Conversion
            res = self.client.post(f"/api/admissions/{st_id}/convert-to-student")
            self.assertEqual(res.status_code, 400)

            # 7. Test Export CSV
            res = self.client.get("/api/admissions/export")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Application ID", res.data)
            self.assertIn(b"Sanket Amte", res.data)

            # 8. Test Rejection Flow on new applicant
            candidate_data2 = dict(candidate_data)
            candidate_data2["email"] = "reject@zeal.edu.in"
            candidate_data2["mobile"] = "9876543299"
            candidate_data2["aadhaar"] = "123456789999"
            self.client.post("/api/students", data=candidate_data2)
            st2 = Student.query.filter_by(email="reject@zeal.edu.in").first()

            # Rejection without reason fails
            res = self.client.post(f"/api/admissions/{st2.id}/reject", json={"reason": ""})
            self.assertEqual(res.status_code, 400)

            # Rejection with reason succeeds
            res = self.client.post(f"/api/admissions/{st2.id}/reject", json={"reason": "12th Marksheet illegible"})
            self.assertEqual(res.status_code, 200)
            st2 = Student.query.get(st2.id)
            self.assertEqual(st2.status, "Rejected")
            self.assertEqual(st2.rejection_reason, "12th Marksheet illegible")

if __name__ == "__main__":
    unittest.main()
