import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from models import db, Student, Admin

def test_erp_suite():
    print("=== STARTING PRODUCTION ERP TEST SUITE ===")
    app = create_app("test")
    
    with app.app_context():
        db.create_all()
        client = app.test_client()

        print("1. Testing Health Check & 404 Error Handler...")
        res_404 = client.get("/api/non-existent-route")
        assert res_404.status_code == 404
        assert "Resource Not Found" in res_404.get_json()["error"]
        print("  [OK] 404 Error handler verified.")

        print("2. Testing Default Admin Credentials...")
        admin = Admin.query.filter_by(username="admin").first()
        assert admin is not None
        assert admin.check_password("admin123")
        print("  [OK] Admin password hashing & verification confirmed.")

        print("3. Testing Admin Login Route...")
        admin_login = client.post("/api/login", json={"username": "admin", "password": "admin123"})
        assert admin_login.status_code == 200
        print("  [OK] Admin login successful.")

        print("4. Testing Student Admission Creation & Status...")
        student_data = {
            "fullName": "ERP Candidate",
            "fatherName": "Father",
            "motherName": "Mother",
            "dob": "2001-09-20",
            "gender": "Male",
            "bloodGroup": "B+",
            "mobile": "9876543210",
            "email": "erp.candidate@zeal.edu.in",
            "aadhaar": "987654321012",
            "address": "123 ERP Street",
            "city": "Pune",
            "state": "Maharashtra",
            "pincode": "411038",
            "nationality": "Indian",
            "board10": "CBSE",
            "percentage10": "91.0",
            "board12": "HSC",
            "percentage12": "87.5",
            "entranceExam": "MHT-CET",
            "entranceScore": "96.0",
            "department": "Computer Engineering",
            "admissionType": "CAP"
        }

        create_res = client.post("/api/students", json=student_data)
        assert create_res.status_code == 201
        created_st = create_res.get_json()["student"]
        st_id = created_st["id"]
        assert created_st["status"] == "Pending Verification"
        print(f"  [OK] Student created with ID #{st_id} and status 'Pending Verification'.")

        print("5. Testing Student Login & Profile View...")
        st_login = client.post("/api/student-login", json={"application_id": st_id, "dob": "2001-09-20"})
        assert st_login.status_code == 200

        st_profile = client.get("/api/student/profile")
        assert st_profile.status_code == 200
        assert st_profile.get_json()["fullName"] == "ERP Candidate"
        print("  [OK] Student login & profile view confirmed.")

        print("6. Testing Analytics Dashboard Metrics...")
        analytics_res = client.get("/api/dashboard")
        assert analytics_res.status_code == 200
        adata = analytics_res.get_json()
        assert adata["total"] >= 1
        assert "dept_stats" in adata
        print("  [OK] Analytics Dashboard metrics verified.")

        print("7. Testing Student Logout...")
        logout_res = client.post("/api/student-logout")
        assert logout_res.status_code == 200
        print("  [OK] Student logout verified.")

        print("8. Testing Student Record Deletion...")
        del_res = client.delete(f"/api/students/{st_id}")
        assert del_res.status_code == 200
        assert "deleted successfully" in del_res.get_json()["message"]

        # Verify 404 after deletion
        get_deleted = client.get(f"/api/students/{st_id}")
        assert get_deleted.status_code == 404
        print("  [OK] Student deletion & cleanup verified.")

        print("\nALL PRODUCTION ERP TEST SUITE CASES PASSED CLEANLY!")

if __name__ == "__main__":
    test_erp_suite()
