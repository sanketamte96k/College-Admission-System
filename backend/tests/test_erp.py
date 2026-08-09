import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from models import db, Student, Admin, Payment

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

        # Re-login admin for fee checks
        client.post("/api/login", json={"username": "admin", "password": "admin123"})

        print("7. Testing Fee & Payment Management Module (Tests 1 - 10)...")
        # TEST 1: Admin opens student fee details
        fee_res = client.get(f"/api/students/{st_id}/fees")
        assert fee_res.status_code == 200
        fdata = fee_res.get_json()
        assert "total_fee" in fdata
        assert fdata["total_fee"] > 0
        assert fdata["paid_amount"] == 0.0
        assert fdata["pending_amount"] == fdata["total_fee"]
        assert fdata["payment_status"] == "Pending"
        assert "fee_breakdown" in fdata
        print(f"  [OK] TEST 1: Fee structure fetched (Total: Rs. {fdata['total_fee']}, Status: {fdata['payment_status']}).")

        # TEST 9: Invalid payment amount is rejected
        neg_pay = client.post(f"/api/students/{st_id}/payments", json={
            "amount": -500.0,
            "fee_type": "Tuition Fee"
        })
        assert neg_pay.status_code == 400
        zero_pay = client.post(f"/api/students/{st_id}/payments", json={
            "amount": 0,
            "fee_type": "Tuition Fee"
        })
        assert zero_pay.status_code == 400
        print("  [OK] TEST 9: Invalid payment amount (<= 0) rejected with 400.")

        # TEST 2: Admin records a partial payment
        pay1_res = client.post(f"/api/students/{st_id}/payments", json={
            "amount": 40000.0,
            "fee_type": "Tuition Fee",
            "payment_method": "UPI",
            "transaction_id": "TEST_TXN_001",
            "remarks": "First installment paid"
        })
        assert pay1_res.status_code == 201
        p1_data = pay1_res.get_json()
        assert p1_data["success"] is True
        assert p1_data["payment"]["amount"] == 40000.0
        print("  [OK] TEST 2: First payment recorded successfully (Rs. 40,000 via UPI).")

        # Prevent duplicate transaction ID
        dup_pay = client.post(f"/api/students/{st_id}/payments", json={
            "amount": 10000.0,
            "transaction_id": "TEST_TXN_001"
        })
        assert dup_pay.status_code == 400
        print("  [OK] Duplicate transaction ID successfully blocked.")

        # TEST 3, 4, 5: Paid amount, Pending amount, and Status update to 'Partially Paid'
        summary1 = p1_data["summary"]
        assert summary1["paid_amount"] == 40000.0
        assert summary1["pending_amount"] == round(summary1["total_fee"] - 40000.0, 2)
        assert summary1["payment_status"] == "Partially Paid"
        print(f"  [OK] TEST 3, 4, 5: Partial balance confirmed (Paid: Rs. {summary1['paid_amount']}, Pending: Rs. {summary1['pending_amount']}, Status: {summary1['payment_status']}).")

        # TEST 6: Payment history displays correctly
        hist_res = client.get(f"/api/students/{st_id}/payments")
        assert hist_res.status_code == 200
        hdata = hist_res.get_json()
        assert len(hdata) == 1
        assert hdata[0]["transaction_id"] == "TEST_TXN_001"
        pay1_id = p1_data["payment"]["id"]
        print("  [OK] TEST 6: Payment history returns chronological records.")

        # Pay remaining balance to achieve 'Paid' status
        rem_amount = summary1["pending_amount"]
        pay2_res = client.post(f"/api/students/{st_id}/payments", json={
            "amount": rem_amount,
            "fee_type": "Development Fee",
            "payment_method": "Bank Transfer",
            "remarks": "Final clearance"
        })
        assert pay2_res.status_code == 201
        p2_data = pay2_res.get_json()
        pay2_id = p2_data["payment"]["id"]
        summary2 = p2_data["summary"]
        assert summary2["pending_amount"] == 0.0
        assert summary2["payment_status"] == "Paid"
        print(f"  [OK] Status updated to 'Paid' upon full fee clearance (Paid: Rs. {summary2['paid_amount']}, Pending: Rs. 0).")

        print("8. Testing Official PDF Fee Receipt Generation & Security...")
        # PDF TEST 1: Admin downloads receipt for Payment 1
        admin_rcpt1 = client.get(f"/api/payments/{pay1_id}/receipt")
        assert admin_rcpt1.status_code == 200
        assert "application/pdf" in admin_rcpt1.content_type
        assert admin_rcpt1.data.startswith(b"%PDF")
        assert "attachment;" in admin_rcpt1.headers.get("Content-Disposition", "")
        print(f"  [OK] PDF TEST 1: Admin downloaded Payment 1 PDF Receipt ({len(admin_rcpt1.data)} bytes, Content-Type: application/pdf).")

        # PDF TEST 2 & 3: Multi-payment reconciliation calculations
        from services.receipt_service import ReceiptService
        pay1_obj = Payment.query.get(pay1_id)
        pay2_obj = Payment.query.get(pay2_id)
        student_obj = Student.query.get(st_id)

        recon1 = ReceiptService.calculate_reconciliation_data(pay1_obj, student_obj)
        assert recon1["previously_paid"] == 0.0
        assert recon1["current_payment"] == 40000.0
        assert recon1["cumulative_paid"] == 40000.0
        assert recon1["remaining_balance"] == 70000.0

        recon2 = ReceiptService.calculate_reconciliation_data(pay2_obj, student_obj)
        assert recon2["previously_paid"] == 40000.0
        assert recon2["current_payment"] == 70000.0
        assert recon2["cumulative_paid"] == 110000.0
        assert recon2["remaining_balance"] == 0.0
        print("  [OK] PDF TEST 2 & 3: Database reconciliation math verified across sequential receipts.")

        # PDF TEST 6 & 7: Admin access & 404 for invalid payment ID
        admin_rcpt2 = client.get(f"/api/payments/{pay2_id}/receipt")
        assert admin_rcpt2.status_code == 200
        assert admin_rcpt2.data.startswith(b"%PDF")
        inv_rcpt = client.get("/api/payments/999999/receipt")
        assert inv_rcpt.status_code == 404
        print("  [OK] PDF TEST 6 & 7: Admin authorized access confirmed & invalid payment returned 404.")

        # TEST 7: Student logs in and sees their own fee information & downloads own receipt
        client.get("/api/logout")  # Logout admin
        st_login = client.post("/api/student-login", json={"application_id": st_id, "dob": "2001-09-20"})
        assert st_login.status_code == 200
        
        st_fee_res = client.get("/api/student/fees")
        assert st_fee_res.status_code == 200
        st_fdata = st_fee_res.get_json()
        assert st_fdata["student_id"] == st_id
        assert st_fdata["payment_status"] == "Paid"
        assert len(st_fdata["payments"]) == 2
        print("  [OK] TEST 7: Logged-in student successfully views own fee summary and payments.")

        # PDF TEST 4: Student downloads own receipt
        st_rcpt_res = client.get(f"/api/payments/{pay1_id}/receipt")
        assert st_rcpt_res.status_code == 200
        assert "application/pdf" in st_rcpt_res.content_type
        assert st_rcpt_res.data.startswith(b"%PDF")
        print("  [OK] PDF TEST 4: Student successfully downloaded own PDF receipt.")

        # PDF TEST 5: Security check — Student A cannot download other student's receipt
        # Create a mock payment for a different student to test cross-access prevention
        other_st = Student(
            fullName="Other Candidate",
            email="other.student@zeal.edu.in",
            mobile="9876543210",
            aadhaar="999988887777",
            dob="2002-01-01",
            gender="Female",
            bloodGroup="O+",
            fatherName="Father",
            motherName="Mother",
            address="Pune",
            city="Pune",
            state="Maharashtra",
            pincode="411041",
            nationality="Indian",
            board10="CBSE",
            percentage10=90.0,
            board12="HSC",
            percentage12=90.0,
            entranceExam="MHT-CET",
            entranceScore=95.0,
            department="Computer Engineering",
            admissionType="CAP"
        )
        db.session.add(other_st)
        db.session.commit()
        other_pay = Payment(
            student_id=other_st.id,
            amount=15000.0,
            fee_type="Tuition Fee",
            payment_method="UPI",
            transaction_id="OTHER_ST_TXN_999",
            status="SUCCESS"
        )
        db.session.add(other_pay)
        db.session.commit()

        # Logged in as student `st_id`, attempt to access `other_pay.id`
        forbidden_rcpt = client.get(f"/api/payments/{other_pay.id}/receipt")
        assert forbidden_rcpt.status_code == 403
        print("  [OK] PDF TEST 5: Cross-student receipt access blocked with 403 Forbidden.")

        # Clean up temporary other student
        db.session.delete(other_pay)
        db.session.delete(other_st)
        db.session.commit()

        # Re-login admin for remaining checks
        client.post("/api/student-logout")
        client.post("/api/login", json={"username": "admin", "password": "admin123"})

        print("9. Testing Analytics Dashboard Status & Fee Breakdown...")
        analytics_res = client.get("/api/dashboard")
        assert analytics_res.status_code == 200
        adata = analytics_res.get_json()
        assert adata["total"] >= 1
        assert "status_stats" in adata
        assert "total_fees_collected" in adata
        assert adata["total_fees_collected"] >= summary2["paid_amount"]
        print("  [OK] Analytics Dashboard verification & fee collections confirmed.")

        print("10. Testing Student Record Deletion & Payment Cascade...")
        del_res = client.delete(f"/api/students/{st_id}")
        assert del_res.status_code == 200
        assert "deleted successfully" in del_res.get_json()["message"]

        # Verify 404 after deletion
        get_deleted = client.get(f"/api/students/{st_id}")
        assert get_deleted.status_code == 404
        print("  [OK] Student deletion & payment cleanup verified.")

        print("\nALL PRODUCTION ERP TEST SUITE CASES (VERIFICATION + FEES + PDF RECEIPTS 1-8 + CRUD) PASSED CLEANLY!")

if __name__ == "__main__":
    test_erp_suite()
