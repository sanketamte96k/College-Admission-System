import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db, Course, Subject, Student, Admin

class CoursesModuleTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["TESTING"] = "True"
        self.app = create_app("test")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create admin user & session
        with self.client.session_transaction() as sess:
            sess["admin_id"] = 1
            sess["username"] = "admin"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_curriculum_and_auto_seed(self):
        res = self.client.get("/api/courses")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("summary", data)
        self.assertIn("curriculum", data)
        self.assertGreaterEqual(data["summary"]["total_programs"], 7)
        self.assertGreaterEqual(data["summary"]["total_subjects"], 20)
        self.assertEqual(len(data["curriculum"]), 4)  # 4 Academic Years

    def test_create_and_update_course_program(self):
        # Create Program
        payload = {
            "name": "B.Tech Robotics Engineering",
            "code": "BTECH-ROBOT",
            "department": "Mechanical Engineering",
            "degree_type": "B.Tech",
            "duration_years": 4,
            "total_credits": 165,
            "description": "Specialized degree in autonomous systems and mechatronics."
        }
        res = self.client.post("/api/courses", json=payload)
        self.assertEqual(res.status_code, 201)
        c_data = res.get_json()
        self.assertIn("course", c_data)
        course_id = c_data["course"]["id"]

        # Update Program
        update_payload = {"total_credits": 170, "description": "Updated robotics program."}
        res_up = self.client.put(f"/api/courses/{course_id}", json=update_payload)
        self.assertEqual(res_up.status_code, 200)
        up_data = res_up.get_json()
        self.assertEqual(up_data["course"]["total_credits"], 170)

    def test_create_edit_and_delete_subject(self):
        # Create Subject in Year 3, Sem 5
        sub_payload = {
            "code": "ROB501",
            "name": "Kinematics & Dynamics of Robots",
            "department": "Mechanical Engineering",
            "program": "B.Tech Mechanical Engineering",
            "academic_year": 3,
            "semester": 5,
            "credits": 4,
            "subject_type": "Core",
            "description": "Forward and inverse kinematics for robotic manipulators."
        }
        res = self.client.post("/api/subjects", json=sub_payload)
        self.assertEqual(res.status_code, 201)
        s_data = res.get_json()
        sub_id = s_data["subject"]["id"]

        # Edit Subject
        edit_payload = {"credits": 5, "subject_type": "Lab"}
        res_edit = self.client.put(f"/api/subjects/{sub_id}", json=edit_payload)
        self.assertEqual(res_edit.status_code, 200)
        self.assertEqual(res_edit.get_json()["subject"]["credits"], 5)

        # Delete Subject
        res_del = self.client.delete(f"/api/subjects/{sub_id}")
        self.assertEqual(res_del.status_code, 200)

    def test_safe_course_deletion_protection(self):
        # Try deleting seeded course program with subjects
        res = self.client.get("/api/courses")
        course = Course.query.filter_by(code="BTECH-COMP").first()
        self.assertIsNotNone(course)

        # Attempt deletion — should be blocked because subjects belong to BTECH-COMP
        res_del = self.client.delete(f"/api/courses/{course.id}")
        self.assertEqual(res_del.status_code, 400)
        self.assertIn("Cannot delete program", res_del.get_json()["error"])

if __name__ == "__main__":
    unittest.main()
