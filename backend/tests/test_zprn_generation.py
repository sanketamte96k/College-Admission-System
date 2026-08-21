import unittest
from datetime import datetime
from app import create_app
from models import db, Student, LibraryBook, LibraryTransaction
from services import StudentService, LibraryService

class ZPRNGenerationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Seed initial test student (Pending Admission)
        self.pending_student = Student(
            fullName="Rahul Patil",
            fatherName="Suresh Patil",
            motherName="Sunita Patil",
            dob="2001-05-15",
            gender="Male",
            bloodGroup="O+",
            mobile="9876543210",
            email="rahul.patil@example.com",
            aadhaar="123456789012",
            address="Kothrud, Pune",
            city="Pune",
            state="Maharashtra",
            pincode="411038",
            nationality="Indian",
            board10="SSC",
            percentage10=88.5,
            board12="HSC",
            percentage12=85.0,
            entranceExam="MHT-CET",
            entranceScore=98.2,
            department="Computer Engineering",
            course="B.Tech Computer Engineering",
            academic_year="2026-27",
            admissionType="CAP",
            status="Approved",
            is_enrolled=False
        )

        self.pending_student2 = Student(
            fullName="Anita Deshmukh",
            fatherName="Prakash Deshmukh",
            motherName="Meena Deshmukh",
            dob="2002-08-20",
            gender="Female",
            bloodGroup="A+",
            mobile="9876543211",
            email="anita.deshmukh@example.com",
            aadhaar="987654321098",
            address="Karve Nagar, Pune",
            city="Pune",
            state="Maharashtra",
            pincode="411052",
            nationality="Indian",
            board10="SSC",
            percentage10=90.0,
            board12="HSC",
            percentage12=89.5,
            entranceExam="MHT-CET",
            entranceScore=99.1,
            department="Information Technology",
            course="B.Tech Information Technology",
            academic_year="2026-27",
            admissionType="CAP",
            status="Approved",
            is_enrolled=False
        )

        db.session.add_all([self.pending_student, self.pending_student2])
        db.session.commit()
        LibraryService.initialize_default_books()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_1_admission_completion_generates_zprn(self):
        student, msg = StudentService.convert_to_student(self.pending_student.id)
        self.assertIsNotNone(student)
        self.assertTrue(student.is_enrolled)
        self.assertIsNotNone(student.enrollment_number)
        self.assertTrue(student.enrollment_number.startswith("124BT"))

    def test_2_two_students_receive_different_zprns(self):
        s1, _ = StudentService.convert_to_student(self.pending_student.id)
        s2, _ = StudentService.convert_to_student(self.pending_student2.id)
        self.assertNotEqual(s1.enrollment_number, s2.enrollment_number)
        self.assertTrue(s1.enrollment_number.startswith("124BT"))
        self.assertTrue(s2.enrollment_number.startswith("124IT"))

    def test_3_zprn_is_unique(self):
        s1, _ = StudentService.convert_to_student(self.pending_student.id)
        s2, _ = StudentService.convert_to_student(self.pending_student2.id)
        self.assertNotEqual(s1.enrollment_number, s2.enrollment_number)

    def test_4_zprn_remains_unchanged_after_update(self):
        s1, _ = StudentService.convert_to_student(self.pending_student.id)
        original_zprn = s1.enrollment_number
        StudentService.update_student(s1.id, {"email": "updated.rahul@example.com"}, {}, "/tmp")
        updated_s = Student.query.get(s1.id)
        self.assertEqual(updated_s.enrollment_number, original_zprn)

    def test_5_pending_admission_does_not_have_zprn(self):
        pending = Student(
            fullName="Pending Applicant",
            fatherName="F", motherName="M", dob="2000-01-01", gender="Male",
            bloodGroup="O+", mobile="9000000001", email="pending@test.com", aadhaar="111122223333",
            address="Addr", city="Pune", state="MH", pincode="411001", nationality="Indian",
            board10="SSC", percentage10=70.0, board12="HSC", percentage12=70.0,
            entranceExam="CET", entranceScore=70.0, department="Civil Engineering", admissionType="CAP",
            status="Pending Verification", is_enrolled=False
        )
        db.session.add(pending)
        db.session.commit()
        self.assertIsNone(pending.enrollment_number)

    def test_6_rejected_admission_does_not_have_zprn(self):
        StudentService.reject_application(self.pending_student.id, "Invalid Documents")
        rejected = Student.query.get(self.pending_student.id)
        self.assertIsNone(rejected.enrollment_number)

    def test_7_existing_student_zprn_is_preserved(self):
        self.pending_student.enrollment_number = "124PRESERVED9999"
        db.session.commit()
        s, _ = StudentService.convert_to_student(self.pending_student.id)
        self.assertEqual(s.enrollment_number, "124PRESERVED9999")

    def test_8_library_lookup_using_valid_zprn(self):
        s, _ = StudentService.convert_to_student(self.pending_student.id)
        success, msg, data = LibraryService.verify_student_by_zprn(s.enrollment_number)
        self.assertTrue(success)
        self.assertEqual(data["student_id"], s.id)
        self.assertEqual(data["fullName"], "Rahul Patil")

    def test_9_invalid_zprn_is_rejected(self):
        success, msg, data = LibraryService.verify_student_by_zprn("INVALID-ZPRN-9999")
        self.assertFalse(success)
        self.assertEqual(msg, "Student not found in college records")

    def test_10_inactive_student_cannot_be_issued_book(self):
        pending = Student(
            fullName="Unenrolled Student",
            fatherName="F", motherName="M", dob="2000-01-01", gender="Male",
            bloodGroup="O+", mobile="9000000002", email="unenrolled@test.com", aadhaar="111122223334",
            address="Addr", city="Pune", state="MH", pincode="411001", nationality="Indian",
            board10="SSC", percentage10=70.0, board12="HSC", percentage12=70.0,
            entranceExam="CET", entranceScore=70.0, department="Civil Engineering", admissionType="CAP",
            status="Pending Verification", is_enrolled=False
        )
        db.session.add(pending)
        db.session.commit()
        books = LibraryService.get_books()
        success, msg, _ = LibraryService.issue_book(books[0]["id"], pending.id)
        self.assertFalse(success)

if __name__ == "__main__":
    unittest.main()
