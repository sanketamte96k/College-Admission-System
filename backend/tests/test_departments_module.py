import unittest
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from models import db, Department, Student

class TestDepartmentsModule(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "True"
        self.app = create_app("test")
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_departments_crud_and_safety(self):
        # 1. Test GET /api/departments (auto-initializes 7 standard departments)
        res = self.client.get("/api/departments")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("summary", data)
        self.assertIn("departments", data)
        self.assertGreaterEqual(len(data["departments"]), 7)

        # Log in as admin
        login_res = self.client.post("/api/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(login_res.status_code, 200)

        new_dept_payload = {
            "name": "Robotics Engineering",
            "code": "ROBO",
            "hod_name": "Dr. K. S. Verma",
            "hod_email": "hod.robo@zeal.edu.in",
            "total_seats": 60,
            "status": "Active",
            "description": "Robotics automation and AI mechanics."
        }

        res = self.client.post("/api/departments", json=new_dept_payload)
        self.assertEqual(res.status_code, 201)
        res_json = json.loads(res.data)
        dept_id = res_json["department"]["id"]
        self.assertEqual(res_json["department"]["name"], "Robotics Engineering")

        # 3. Test PUT /api/departments/<id> (Update department)
        update_payload = {
            "hod_name": "Dr. K. S. Verma (Updated)",
            "total_seats": 120
        }
        res = self.client.put(f"/api/departments/{dept_id}", json=update_payload)
        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.data)
        self.assertEqual(res_json["department"]["hod_name"], "Dr. K. S. Verma (Updated)")
        self.assertEqual(res_json["department"]["total_seats"], 120)

        # 4. Test Safe Deletion Block (Attach a student to Computer Engineering and attempt deletion)
        with self.app.app_context():
            comp_dept = Department.query.filter_by(name="Computer Engineering").first()
            self.assertIsNotNone(comp_dept)

            test_student = Student(
                fullName="Test Candidate",
                fatherName="Father",
                motherName="Mother",
                dob="2005-01-01",
                gender="Male",
                bloodGroup="O+",
                mobile="9876543210",
                email="test.dept@example.com",
                aadhaar="123456789012",
                address="Street 1",
                city="Pune",
                state="Maharashtra",
                pincode="411041",
                nationality="Indian",
                board10="CBSE",
                percentage10=85.0,
                board12="HSC",
                percentage12=88.0,
                entranceExam="MHT-CET",
                entranceScore=92.5,
                department="Computer Engineering",
                admissionType="CAP"
            )
            db.session.add(test_student)
            db.session.commit()
            comp_id = comp_dept.id

        # Attempt to delete Computer Engineering (Should be BLOCKED because student exists)
        res = self.client.delete(f"/api/departments/{comp_id}")
        self.assertEqual(res.status_code, 400)
        res_json = json.loads(res.data)
        self.assertIn("Cannot delete department", res_json["error"])

        # 5. Test Successful Deletion for empty department (Robotics Engineering)
        res = self.client.delete(f"/api/departments/{dept_id}")
        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.data)
        self.assertIn("deleted successfully", res_json["message"])

if __name__ == "__main__":
    unittest.main()
