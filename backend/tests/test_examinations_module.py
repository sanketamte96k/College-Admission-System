import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db, Examination, ExamMark, Student

class ExaminationsModuleTestCase(unittest.TestCase):

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
            fullName="Rahul Verma",
            fatherName="Sanjay Verma",
            motherName="Sunita Verma",
            dob="2003-05-14",
            gender="Male",
            bloodGroup="O+",
            mobile="9876543210",
            email="rahul.verma@example.com",
            aadhaar="123456789012",
            address="Pune",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            nationality="Indian",
            board10="SSC",
            percentage10=88.5,
            board12="HSC",
            percentage12=86.0,
            entranceExam="MHT-CET",
            entranceScore=94.5,
            department="Computer Engineering",
            course="B.Tech Computer Engineering",
            academic_year="2026-27",
            admissionType="CAP Round 1",
            enrollment_number="EN2026-COMP-099",
            status="Enrolled"
        )
        db.session.add(self.test_student)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_examinations_and_auto_seed(self):
        res = self.client.get("/api/examinations")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("summary", data)
        self.assertIn("examinations", data)
        self.assertGreaterEqual(data["summary"]["total_exams"], 5)

    def test_create_and_edit_examination(self):
        payload = {
            "name": "Mid-Sem: Artificial Intelligence",
            "department": "Computer Engineering",
            "program": "B.Tech Computer Engineering",
            "academic_year": 4,
            "semester": 7,
            "subject_code": "CS702",
            "subject_name": "Artificial Intelligence",
            "exam_type": "Mid Semester",
            "exam_date": "2026-10-05",
            "max_marks": 50,
            "passing_marks": 20,
            "status": "Scheduled"
        }
        res = self.client.post("/api/examinations", json=payload)
        self.assertEqual(res.status_code, 201)
        exam_id = res.get_json()["examination"]["id"]

        # Edit
        res_up = self.client.put(f"/api/examinations/{exam_id}", json={"max_marks": 60})
        self.assertEqual(res_up.status_code, 200)
        self.assertEqual(res_up.get_json()["examination"]["max_marks"], 60)

    def test_marks_evaluation_and_result_publication(self):
        # Fetch auto-seeded exam
        res = self.client.get("/api/examinations")
        exam_id = res.get_json()["examinations"][0]["id"]

        # Fetch marks roster
        res_m = self.client.get(f"/api/examinations/{exam_id}/marks")
        self.assertEqual(res_m.status_code, 200)
        marks_roster = res_m.get_json()["marks"]
        self.assertGreater(len(marks_roster), 0)

        # Enter marks for student
        save_payload = {
            "marks": [
                {
                    "student_id": self.test_student.id,
                    "marks_obtained": 42.5,
                    "is_absent": False,
                    "remarks": "Excellent performance"
                }
            ]
        }
        res_save = self.client.post(f"/api/examinations/{exam_id}/marks", json=save_payload)
        self.assertEqual(res_save.status_code, 200)

        # Publish results
        res_pub = self.client.post(f"/api/examinations/{exam_id}/publish")
        self.assertEqual(res_pub.status_code, 200)

        # Delete protection test for published exam
        res_del = self.client.delete(f"/api/examinations/{exam_id}")
        self.assertEqual(res_del.status_code, 400)
        self.assertIn("Cannot delete examination", res_del.get_json()["error"])

if __name__ == "__main__":
    unittest.main()
