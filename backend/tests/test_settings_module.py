import unittest
import json
import os
import sys

# Ensure backend path is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from models import db, Admin, SystemSetting, AcademicYear
from services import SettingService

class TestSettingsModule(unittest.TestCase):

    def setUp(self):
        os.environ["TESTING"] = "True"
        self.app = create_app("test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        db.create_all()

        # Query or create test admin user
        self.admin = Admin.query.filter_by(username="admin").first()
        if not self.admin:
            self.admin = Admin(
                username="admin",
                email="admin@zeal.edu.in"
            )
            self.admin.set_password("admin123")
            db.session.add(self.admin)
            db.session.commit()

        # Seed default settings
        SettingService.seed_default_settings()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_admin(self):
        with self.client.session_transaction() as sess:
            sess["admin_id"] = self.admin.id

    def test_get_settings(self):
        res = self.client.get("/api/settings")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("grouped", data)
        self.assertIn("flat", data)
        self.assertEqual(data["flat"].get("app_name"), "Zeal College ERP")

    def test_update_general_settings(self):
        self.login_admin()
        payload = {
            "app_name": "Zeal ERP System 2026",
            "institution_name": "Zeal Institute of Technology",
            "institution_email": "contact@zeal.edu.in",
            "institution_phone": "+91 20 6720 6000"
        }
        res = self.client.put("/api/settings/general", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)

        # Verify persistence
        updated = SystemSetting.query.filter_by(key="app_name").first()
        self.assertEqual(updated.value, "Zeal ERP System 2026")

    def test_validation_invalid_email(self):
        self.login_admin()
        payload = {
            "institution_email": "invalid-email-format"
        }
        res = self.client.put("/api/settings/general", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_academic_years(self):
        self.login_admin()
        res = self.client.get("/api/settings/academic-years")
        self.assertEqual(res.status_code, 200)
        years = json.loads(res.data)
        self.assertGreaterEqual(len(years), 3)

        # Create new academic year
        payload = {
            "year_name": "2028-29",
            "start_date": "2028-06-01",
            "end_date": "2029-05-31"
        }
        create_res = self.client.post("/api/settings/academic-years", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(create_res.status_code, 201)

        # Verify only 1 active year
        new_year = AcademicYear.query.filter_by(year_name="2028-29").first()
        activate_res = self.client.post(f"/api/settings/academic-years/{new_year.id}/set-active")
        self.assertEqual(activate_res.status_code, 200)

        active_years = AcademicYear.query.filter_by(is_active=True).all()
        self.assertEqual(len(active_years), 1)
        self.assertEqual(active_years[0].year_name, "2028-29")

    def test_change_password(self):
        self.login_admin()
        # Invalid current password
        bad_res = self.client.post("/api/settings/change-password", data=json.dumps({
            "current_password": "wrongpassword",
            "new_password": "newsecretpass",
            "confirm_password": "newsecretpass"
        }), content_type="application/json")
        self.assertEqual(bad_res.status_code, 400)

        # Valid change
        good_res = self.client.post("/api/settings/change-password", data=json.dumps({
            "current_password": "admin123",
            "new_password": "newsecretpass",
            "confirm_password": "newsecretpass"
        }), content_type="application/json")
        self.assertEqual(good_res.status_code, 200)

        # Verify admin can authenticate with new password
        admin_ref = Admin.query.get(self.admin.id)
        self.assertTrue(admin_ref.check_password("newsecretpass"))

if __name__ == "__main__":
    unittest.main()
