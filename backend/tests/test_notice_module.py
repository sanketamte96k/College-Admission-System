import unittest
import json
from datetime import datetime, timedelta
from app import create_app
from models import db, Notice, Admin
from services import NoticeService

class NoticeModuleTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()

        # Get or create admin user for auth test
        admin = Admin.query.filter_by(username="admin").first()
        if not admin:
            admin = Admin(username="admin", email="admin@zeal.edu.in")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
        self.admin_id = admin.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login_admin(self):
        with self.client.session_transaction() as sess:
            sess["admin_id"] = self.admin_id
            sess["admin_username"] = "admin"

    def test_seed_notices(self):
        NoticeService.seed_default_notices()
        notices = Notice.query.all()
        self.assertGreater(len(notices), 0)

    def test_create_notice_and_rbac(self):
        payload = {
            "title": "Test Circular",
            "content": "Important update regarding semester exams.",
            "category": "Examination",
            "priority": "Urgent",
            "status": "Draft",
            "audience": "Students"
        }

        # 1. Unauthorized attempt (no session) -> 401
        res = self.client.post("/api/notices", json=payload)
        self.assertEqual(res.status_code, 401)

        # 2. Authorized attempt (login admin) -> 201
        self._login_admin()
        res = self.client.post("/api/notices", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn("notice", data)
        self.assertEqual(data["notice"]["title"], "Test Circular")

    def test_notice_lifecycle_publish_archive_pin_delete(self):
        self._login_admin()
        notice = NoticeService.create_notice({
            "title": "Lifecycle Test Notice",
            "content": "Testing status changes.",
            "category": "General",
            "status": "Draft"
        })
        n_id = notice.id

        # 1. Publish Notice
        res = self.client.post(f"/api/notices/{n_id}/publish")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["notice"]["status"], "Published")

        # 2. Pin Notice
        res = self.client.post(f"/api/notices/{n_id}/pin")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["notice"]["is_pinned"])

        # 3. Archive Notice
        res = self.client.post(f"/api/notices/{n_id}/archive")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["notice"]["status"], "Archived")

        # 4. Delete Notice
        res = self.client.delete(f"/api/notices/{n_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(Notice.query.get(n_id))

    def test_notice_filtering_and_search(self):
        self._login_admin()
        NoticeService.create_notice({
            "title": "Placement Drive by TCS",
            "content": "TCS registration details.",
            "category": "Placement",
            "priority": "Important",
            "status": "Published"
        })
        NoticeService.create_notice({
            "title": "Library Books Overdue",
            "content": "Return books by Friday.",
            "category": "Library",
            "priority": "Normal",
            "status": "Published"
        })

        # Search filter
        res = self.client.get("/api/notices?search=TCS")
        data = res.get_json()
        self.assertEqual(len(data["notices"]), 1)
        self.assertEqual(data["notices"][0]["category"], "Placement")

        # Category filter
        res = self.client.get("/api/notices?category=Library")
        data = res.get_json()
        self.assertEqual(len(data["notices"]), 1)
        self.assertEqual(data["notices"][0]["title"], "Library Books Overdue")

    def test_notice_effective_expiry_and_scheduled_status(self):
        now = datetime.utcnow()
        past_date = now - timedelta(days=2)
        future_date = now + timedelta(days=5)

        # 1. Expired Notice
        expired_notice = NoticeService.create_notice({
            "title": "Past Sports Meet",
            "content": "Event finished.",
            "status": "Published",
            "expiry_date": past_date.strftime("%Y-%m-%d %H:%M:%S")
        })
        self.assertEqual(expired_notice.effective_status, "Expired")

        # 2. Scheduled Notice
        scheduled_notice = NoticeService.create_notice({
            "title": "Future Exam Announcement",
            "content": "Starting next month.",
            "status": "Published",
            "publish_date": future_date.strftime("%Y-%m-%d %H:%M:%S")
        })
        self.assertEqual(scheduled_notice.effective_status, "Scheduled")

    def test_notice_kpi_stats(self):
        self._login_admin()
        NoticeService.create_notice({
            "title": "Notice 1",
            "content": "Content 1",
            "status": "Published",
            "priority": "Urgent",
            "is_pinned": True
        })
        NoticeService.create_notice({
            "title": "Notice 2",
            "content": "Content 2",
            "status": "Draft"
        })

        res = self.client.get("/api/notices/stats")
        self.assertEqual(res.status_code, 200)
        stats = res.get_json()
        self.assertGreaterEqual(stats["total_notices"], 2)
        self.assertGreaterEqual(stats["published"], 1)
        self.assertGreaterEqual(stats["drafts"], 1)
        self.assertGreaterEqual(stats["urgent"], 1)
        self.assertGreaterEqual(stats["pinned"], 1)

if __name__ == "__main__":
    unittest.main()
