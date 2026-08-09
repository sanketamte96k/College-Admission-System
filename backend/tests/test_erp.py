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

        print("6. Testing Admission Verification Workflow (Admin Only)...")
        # Ensure admin is logged in
        client.post("/api/login", json={"username": "admin", "password": "admin123"})

        # Transition to "Under Review"
        review_res = client.put(f"/api/students/{st_id}/verification", json={
            "status": "Under Review",
            "remarks": "Documents being verified by admission officer."
        })
        assert review_res.status_code == 200
        review_data = review_res.get_json()["student"]
        assert review_data["status"] == "Under Review"
        assert review_data["verification_remarks"] == "Documents being verified by admission officer."
        assert review_data["verified_by"] == "admin"
        assert review_data["verified_at"] != ""
        print("  [OK] Transition to 'Under Review' verified.")

        # Rejection without remarks must fail with 400
        rej_no_remarks = client.put(f"/api/students/{st_id}/verification", json={
            "status": "Rejected",
            "remarks": ""
        })
        assert rej_no_remarks.status_code == 400
        assert "remarks are required" in rej_no_remarks.get_json()["error"]
        print("  [OK] Rejection without remarks blocked as expected (400).")

        # Invalid status must fail with 400
        invalid_stat = client.put(f"/api/students/{st_id}/verification", json={
            "status": "InvalidStatus123"
        })
        assert invalid_stat.status_code == 400
        print("  [OK] Invalid status rejected as expected (400).")

        # Transition to "Verified"
        verify_res = client.put(f"/api/students/{st_id}/verification", json={
            "status": "Verified",
            "remarks": "All documents verified and approved for CAP admission."
        })
        assert verify_res.status_code == 200
        verify_data = verify_res.get_json()["student"]
        assert verify_data["status"] == "Verified"
        assert verify_data["verified_by"] == "admin"
        print("  [OK] Transition to 'Verified' approved.")

        # Test Status Filter in GET /api/students
        filter_verified = client.get("/api/students?status=Verified")
        assert filter_verified.status_code == 200
        v_list = filter_verified.get_json()
        assert any(s["id"] == st_id for s in v_list)
        print("  [OK] Status filter in GET /api/students verified.")

        print("7. Testing Analytics Dashboard Status Breakdown...")
        analytics_res = client.get("/api/dashboard")
        assert analytics_res.status_code == 200
        adata = analytics_res.get_json()
        assert adata["total"] >= 1
        assert "status_stats" in adata
        assert adata["verified_count"] >= 1
        print("  [OK] Analytics Dashboard verification stats confirmed.")

        print("8. Testing Unauthorized Access Protection...")
        # Logout admin
        client.get("/api/logout")
        unauth_ver = client.put(f"/api/students/{st_id}/verification", json={
            "status": "Rejected",
            "remarks": "Hacker attempt"
        })
        assert unauth_ver.status_code == 401
        print("  [OK] Unauthorized verification attempt blocked with 401.")

        # Re-login admin for cleanup
        client.post("/api/login", json={"username": "admin", "password": "admin123"})

        print("9. Testing Student Record Deletion...")
        del_res = client.delete(f"/api/students/{st_id}")
        assert del_res.status_code == 200
        assert "deleted successfully" in del_res.get_json()["message"]

        # Verify 404 after deletion
        get_deleted = client.get(f"/api/students/{st_id}")
        assert get_deleted.status_code == 404
        print("  [OK] Student deletion & cleanup verified.")

        print("\nALL PRODUCTION ERP TEST SUITE CASES (INCLUDING ADMISSION VERIFICATION WORKFLOW) PASSED CLEANLY!")

if __name__ == "__main__":
    test_erp_suite()
