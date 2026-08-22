import unittest
import json
from datetime import date
from app import create_app
from models import db, Student, TransportVehicle, TransportRoute, TransportStop, TransportDriver, TransportAssignment
from services.student_service import StudentService
from services.transport_service import TransportService

class TestTransportModule(unittest.TestCase):

    def setUp(self):
        import os
        os.environ["TESTING"] = "True"
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed sample enrolled student
        self.student = Student(
            fullName="Rohan Deshmukh",
            fatherName="Suresh Deshmukh",
            motherName="Sunita Deshmukh",
            dob="2002-05-10",
            gender="Male",
            bloodGroup="O+",
            mobile="9876543210",
            email="rohan.transport@zeal.edu.in",
            aadhaar="123456789012",
            address="Swargate Pune",
            city="Pune",
            state="Maharashtra",
            pincode="411037",
            nationality="Indian",
            board10="SSC",
            percentage10=85.0,
            board12="HSC",
            percentage12=82.0,
            entranceExam="MHT-CET",
            entranceScore=95.0,
            department="Computer Science",
            course="B.Tech Computer Science",
            academic_year="1",
            admissionType="CAP",
            status="Approved",
            is_enrolled=True,
            enrollment_number="124CS260001"
        )
        db.session.add(self.student)

        # Seed sample non-enrolled applicant
        self.applicant = Student(
            fullName="Unenrolled Applicant",
            fatherName="Ramesh Applicant",
            motherName="Lata Applicant",
            dob="2003-01-01",
            gender="Female",
            bloodGroup="B+",
            mobile="9876543211",
            email="applicant.test@zeal.edu.in",
            aadhaar="123456789013",
            address="Kothrud Pune",
            city="Pune",
            state="Maharashtra",
            pincode="411038",
            nationality="Indian",
            board10="SSC",
            percentage10=75.0,
            board12="HSC",
            percentage12=72.0,
            entranceExam="MHT-CET",
            entranceScore=80.0,
            department="Mechanical",
            course="B.Tech Mechanical",
            academic_year="1",
            admissionType="CAP",
            status="Pending",
            is_enrolled=False
        )
        db.session.add(self.applicant)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_initialize_default_transport(self):
        """Verify default routes, vehicles, stops, and drivers seed correctly."""
        summary = TransportService.get_dashboard_summary()
        self.assertGreaterEqual(summary["total_vehicles"], 4)
        self.assertGreaterEqual(summary["total_routes"], 4)
        self.assertGreaterEqual(summary["total_drivers"], 4)

    def test_02_verify_enrolled_student_by_zprn(self):
        """Verify official student ZPRN resolution for transport pass eligibility."""
        success, msg, data = TransportService.verify_student_by_zprn("124CS260001")
        self.assertTrue(success)
        self.assertEqual(data["fullName"], "Rohan Deshmukh")
        self.assertEqual(data["department"], "Computer Science")

    def test_03_reject_unenrolled_student_for_transport(self):
        """Verify non-enrolled student cannot register for college transport."""
        success, msg, data = TransportService.verify_student_by_zprn(str(self.applicant.id))
        self.assertFalse(success)
        self.assertIn("not an enrolled student", msg)

    def test_04_issue_transport_pass_and_capacity(self):
        """Verify transport pass issuance and vehicle capacity limit enforcement."""
        TransportService.initialize_default_transport()

        r = TransportRoute.query.filter_by(route_code="R-01").first()
        st = TransportStop.query.filter_by(route_id=r.id).first()
        v = TransportVehicle.query.filter_by(assigned_route_id=r.id).first()

        # Set small capacity to test safeguard
        v.capacity = 1
        db.session.commit()

        # Issue pass 1 - Should succeed
        success1, msg1, pass1 = TransportService.assign_student_transport(
            zprn_or_student_id="124CS260001",
            route_id=r.id,
            stop_id=st.id,
            vehicle_id=v.id
        )
        self.assertTrue(success1, msg=f"Assignment failed: {msg1}")
        self.assertEqual(pass1["zprn"], "124CS260001")

        # Create second enrolled student
        s2 = Student(
            fullName="Priya Verma",
            fatherName="Vijay Verma",
            motherName="Rekha Verma",
            dob="2002-08-20",
            gender="Female",
            bloodGroup="A+",
            mobile="9876543212",
            email="priya.v@zeal.edu.in",
            aadhaar="123456789014",
            address="Hadapsar Pune",
            city="Pune",
            state="Maharashtra",
            pincode="411028",
            nationality="Indian",
            board10="SSC",
            percentage10=90.0,
            board12="HSC",
            percentage12=88.0,
            entranceExam="MHT-CET",
            entranceScore=96.0,
            department="Computer Science",
            course="B.Tech Computer Science",
            academic_year="1",
            admissionType="CAP",
            status="Approved",
            is_enrolled=True,
            enrollment_number="124CS260002"
        )
        db.session.add(s2)
        db.session.commit()

        # Issue pass 2 to full vehicle - Should fail with capacity warning!
        success2, msg2, pass2 = TransportService.assign_student_transport(
            zprn_or_student_id="124CS260002",
            route_id=r.id,
            stop_id=st.id,
            vehicle_id=v.id
        )
        self.assertFalse(success2)
        self.assertIn("Vehicle capacity is full", msg2)

    def test_05_transport_api_endpoints(self):
        """Test transport REST endpoints."""
        res_dash = self.client.get('/api/transport/dashboard')
        self.assertEqual(res_dash.status_code, 200)

        res_veh = self.client.get('/api/transport/vehicles')
        self.assertEqual(res_veh.status_code, 200)

        res_routes = self.client.get('/api/transport/routes')
        self.assertEqual(res_routes.status_code, 200)

        res_verify = self.client.get('/api/transport/verify-student/124CS260001')
        self.assertEqual(res_verify.status_code, 200)
        self.assertEqual(res_verify.json["student"]["fullName"], "Rohan Deshmukh")

if __name__ == "__main__":
    unittest.main()
