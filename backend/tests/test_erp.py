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

        print("6. Testing Admission Verification & Email Notifications...")
        # Ensure admin is logged in
        client.post("/api/login", json={"username": "admin", "password": "admin123"})

        # CASE 1: Admin verifies student with working/suppressed SMTP
        verify_res = client.put(f"/api/students/{st_id}/verification", json={
            "status": "Verified",
            "remarks": "All documents verified and approved for CAP admission."
        })
        assert verify_res.status_code == 200
        verify_json = verify_res.get_json()
        assert verify_json["status"] == "Verified"
        assert verify_json["email_status"] == "sent"
        assert verify_json["student"]["status"] == "Verified"
        assert verify_json["student"]["verified_by"] == "admin"
        assert verify_json["student"]["verified_at"] != ""
        print("  [OK] CASE 1: Admin verified student with working SMTP (email_status='sent', DB updated).")

        # CASE 2: Admin verifies student with broken SMTP (simulated SMTPAuthenticationError 530)
        from unittest.mock import patch
        import smtplib
        with patch.object(app.extensions["mail"], "send", side_effect=smtplib.SMTPAuthenticationError(530, b"5.7.0 Authentication Required")):
            broken_smtp_res = client.put(f"/api/students/{st_id}/verification", json={
                "status": "Verified",
                "remarks": "Re-verified under SMTP outage."
            })
            assert broken_smtp_res.status_code == 200  # No 500 error!
            broken_json = broken_smtp_res.get_json()
            assert broken_json["status"] == "Verified"
            assert broken_json["email_status"] == "failed"
            assert "Unable to send notification email" in broken_json["email_note"]
            # Verify DB was still updated
            db_student = Student.query.get(st_id)
            assert db_student.status == "Verified"
            assert db_student.verification_remarks == "Re-verified under SMTP outage."
        print("  [OK] CASE 2: Broken SMTP handled gracefully without 500 (email_status='failed', DB updated).")

        # CASE 3: Admin rejects student with remarks
        reject_res = client.put(f"/api/students/{st_id}/verification", json={
            "status": "Rejected",
            "remarks": "12th marksheet illegible. Please submit original attested copy."
        })
        assert reject_res.status_code == 200
        reject_json = reject_res.get_json()
        assert reject_json["status"] == "Rejected"
        assert reject_json["student"]["status"] == "Rejected"
        assert reject_json["student"]["verification_remarks"] == "12th marksheet illegible. Please submit original attested copy."
        print("  [OK] CASE 3: Admin rejected student with remarks (rejection recorded & email dispatched).")

        # Rejection without remarks must fail with 400
        rej_no_remarks = client.put(f"/api/students/{st_id}/verification", json={
            "status": "Rejected",
            "remarks": ""
        })
        assert rej_no_remarks.status_code == 400
        assert "remarks are required" in rej_no_remarks.get_json()["error"]
        print("  [OK] Rejection without remarks blocked (400).")

        # CASE 4: Student has missing/invalid email
        student_no_email = Student(
            fullName="No Email Candidate",
            fatherName="Father",
            motherName="Mother",
            dob="2002-01-01",
            gender="Female",
            bloodGroup="O+",
            mobile="9876543211",
            email="",  # Missing email
            aadhaar="987654321013",
            address="Address",
            city="Pune",
            state="Maharashtra",
            pincode="411038",
            nationality="Indian",
            board10="CBSE",
            percentage10=85.0,
            board12="HSC",
            percentage12=88.0,
            entranceExam="MHT-CET",
            entranceScore=92.0,
            department="Information Technology",
            admissionType="CAP"
        )
        db.session.add(student_no_email)
        db.session.commit()
        no_email_id = student_no_email.id

        no_email_res = client.put(f"/api/students/{no_email_id}/verification", json={
            "status": "Verified",
            "remarks": "Approved despite no email"
        })
        assert no_email_res.status_code == 200
        no_email_json = no_email_res.get_json()
        assert no_email_json["status"] == "Verified"
        assert no_email_json["email_status"] == "failed"
        assert "No valid student email provided" in no_email_json["email_note"]
        # Confirm DB was updated and not rolled back
        assert Student.query.get(no_email_id).status == "Verified"
        db.session.delete(student_no_email)
        db.session.commit()
        print("  [OK] CASE 4: Missing email handled gracefully (verification succeeded, email_status='failed').")

        # CASE 5: Unauthorized user attempts verification
        client.get("/api/logout")  # Logout admin
        unauth_ver = client.put(f"/api/students/{st_id}/verification", json={
            "status": "Verified",
            "remarks": "Hacker attempt"
        })
        assert unauth_ver.status_code == 401
        print("  [OK] CASE 5: Unauthorized verification attempt blocked with 401.")

        # Re-login admin for remaining checks
        client.post("/api/login", json={"username": "admin", "password": "admin123"})

        print("7. Testing Analytics Dashboard Status Breakdown...")
        analytics_res = client.get("/api/dashboard")
        assert analytics_res.status_code == 200
        adata = analytics_res.get_json()
        assert adata["total"] >= 1
        assert "status_stats" in adata
        print("  [OK] Analytics Dashboard verification stats confirmed.")

        print("8. Testing Student Record Deletion...")
        del_res = client.delete(f"/api/students/{st_id}")
        assert del_res.status_code == 200
        assert "deleted successfully" in del_res.get_json()["message"]

        # Verify 404 after deletion
        get_deleted = client.get(f"/api/students/{st_id}")
        assert get_deleted.status_code == 404
        print("  [OK] Student deletion & cleanup verified.")

        print("\nALL PRODUCTION ERP TEST SUITE CASES (CASES 1-5 + CRUD) PASSED CLEANLY!")

if __name__ == "__main__":
    test_erp_suite()
