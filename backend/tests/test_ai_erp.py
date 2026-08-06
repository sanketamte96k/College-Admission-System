import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from models import db, Student, Admin, Payment, Ticket, SeatMatrix

def test_enterprise_ai_erp_suite():
    print("=== STARTING ENTERPRISE AI ERP TEST SUITE ===")
    app = create_app("test")

    with app.app_context():
        db.create_all()
        client = app.test_client()

        print("1. Testing AI Assistant Chatbot...")
        bot_res = client.post("/api/ai/chatbot", json={"message": "What is the tuition fee for Computer Engineering?"})
        assert bot_res.status_code == 200
        assert "tuition fee" in bot_res.get_json()["reply"].lower()
        print("  [OK] AI Chatbot query returned smart response.")

        print("2. Testing AI Eligibility Checker...")
        elig_res = client.post("/api/ai/check-eligibility", json={
            "percentage10": 85.0,
            "percentage12": 72.0,
            "entranceScore": 88.0,
            "department": "Computer Engineering"
        })
        assert elig_res.status_code == 200
        assert elig_res.get_json()["eligible"] is True
        print("  [OK] AI Eligibility Checker evaluated candidate correctly.")

        print("3. Testing AI Admission Predictor...")
        pred_res = client.post("/api/ai/predict-admission", json={
            "percentage12": 80.0,
            "entranceScore": 92.0,
            "department": "Computer Engineering"
        })
        assert pred_res.status_code == 200
        pdata = pred_res.get_json()
        assert pdata["chance_level"] == "High"
        assert pdata["probability_percentage"] >= 80.0
        print("  [OK] AI Admission Predictor computed High chance probability.")

        print("4. Testing Seat Matrix & Branch Capacity...")
        seat_res = client.get("/api/erp/seat-matrix")
        assert seat_res.status_code == 200
        matrix = seat_res.get_json()
        assert len(matrix) >= 5
        print("  [OK] Seat Matrix returned branch capacities.")

        print("5. Testing Merit List Generator...")
        merit_res = client.get("/api/erp/merit-list")
        assert merit_res.status_code == 200
        print("  [OK] Merit List & CAP Round Allocator generated ranks.")

        print("6. Testing Student Creation & AI Document Verification...")
        st = Student(
            fullName="AI ERP Student",
            fatherName="Father",
            motherName="Mother",
            dob="2002-01-01",
            gender="Female",
            bloodGroup="O+",
            mobile="9876543210",
            email="ai.student@zeal.edu.in",
            aadhaar="123412341234",
            address="Street 1",
            city="Pune",
            state="MH",
            pincode="411038",
            nationality="Indian",
            board10="CBSE",
            percentage10=92.0,
            board12="HSC",
            percentage12=90.0,
            entranceExam="MHT-CET",
            entranceScore=95.0,
            department="Computer Engineering",
            admissionType="CAP",
            photo="1_photo.jpg",
            marksheet10="1_10th.pdf",
            marksheet12="1_12th.pdf",
            leavingCertificate="1_lc.pdf"
        )
        db.session.add(st)
        db.session.commit()
        st_id = st.id

        doc_res = client.get(f"/api/ai/verify-documents/{st_id}")
        assert doc_res.status_code == 200
        assert doc_res.get_json()["is_complete"] is True
        print(f"  [OK] AI Document Verification verified all 4 mandatory files for student #{st_id}.")

        print("7. Testing Online Fee Payment Gateway Simulator...")
        pay_res = client.post("/api/payment/process", json={
            "student_id": st_id,
            "amount": 95000.0,
            "payment_mode": "UPI"
        })
        assert pay_res.status_code == 201
        pay_data = pay_res.get_json()
        assert pay_data["transaction"]["status"] == "SUCCESS"
        print("  [OK] Fee payment processed and transaction recorded.")

        print("8. Testing Support Ticket Desk...")
        tkt_res = client.post("/api/tickets", json={
            "student_id": st_id,
            "subject": "Document Verification Query",
            "message": "When will my 12th marksheet be verified?"
        })
        assert tkt_res.status_code == 201
        assert tkt_res.get_json()["ticket"]["status"] == "Open"
        print("  [OK] Support Ticket created successfully.")

        print("\nALL ENTERPRISE AI ERP TEST SUITE CASES PASSED CLEANLY!")

if __name__ == "__main__":
    test_enterprise_ai_erp_suite()
