import unittest
from datetime import date, timedelta
from app import create_app
from models import db, Student, LibraryBook, LibraryTransaction
from services import LibraryService

class LibraryModuleTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Seed test student
        self.student = Student(
            fullName="Library Test Student",
            fatherName="Father",
            motherName="Mother",
            dob="2000-01-01",
            gender="Male",
            bloodGroup="O+",
            mobile="9876543210",
            email="libstudent@example.com",
            aadhaar="123456789012",
            address="Pune Campus",
            city="Pune",
            state="Maharashtra",
            pincode="411041",
            nationality="Indian",
            board10="SSC",
            percentage10=85.0,
            board12="HSC",
            percentage12=82.0,
            entranceExam="MHT-CET",
            entranceScore=95.5,
            department="Computer Engineering",
            course="B.Tech Computer Engineering",
            academic_year="2",
            admissionType="CAP",
            is_enrolled=True,
            enrollment_number="STU-LIB-001"
        )
        db.session.add(self.student)
        db.session.commit()

        # Initialize books
        LibraryService.initialize_default_books()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_library_dashboard_summary(self):
        summary = LibraryService.get_library_dashboard_summary()
        self.assertIn("total_books", summary)
        self.assertGreater(summary["total_books"], 0)
        self.assertGreater(summary["total_titles"], 0)

    def test_add_and_get_book(self):
        success, msg, book = LibraryService.add_book({
            "isbn": "978-0000000001",
            "title": "Unit Test Engineering Math",
            "author": "Test Author",
            "category": "Mathematics",
            "quantity": 5,
            "location": "Shelf M-1"
        })
        self.assertTrue(success)
        self.assertEqual(book["available_qty"], 5)

        # Test duplicate ISBN prevention
        dup_success, dup_msg, _ = LibraryService.add_book({
            "isbn": "978-0000000001",
            "title": "Duplicate Book",
            "author": "Test Author"
        })
        self.assertFalse(dup_success)

    def test_issue_and_return_book(self):
        books = LibraryService.get_books()
        self.assertGreater(len(books), 0)
        test_book = books[0]

        # Issue book
        success, msg, tx = LibraryService.issue_book(
            book_id=test_book["id"],
            student_id=self.student.id,
            issue_date_str="2026-08-01",
            due_date_str="2026-08-15"
        )
        self.assertTrue(success)
        self.assertEqual(tx["status"], "Issued")

        # Verify duplicate active issue prevention
        dup_iss, _, _ = LibraryService.issue_book(
            book_id=test_book["id"],
            student_id=self.student.id
        )
        self.assertFalse(dup_iss)

        # Return book (with overdue fine calculation)
        ret_success, ret_msg, ret_tx = LibraryService.return_book(
            transaction_id=tx["id"],
            return_date_str="2026-08-20",  # 5 days past due date (15th to 20th)
            fine_action="Paid"
        )
        self.assertTrue(ret_success)
        self.assertEqual(ret_tx["status"], "Returned")
        self.assertEqual(ret_tx["overdue_days"], 5)
        self.assertEqual(ret_tx["fine_amount"], 50.0)  # ₹10/day * 5 days

    def test_non_college_student_issue_prevention(self):
        # Create un-enrolled / pending applicant (not a verified college student)
        pending_applicant = Student(
            fullName="External Applicant",
            fatherName="Father",
            motherName="Mother",
            dob="2002-05-05",
            gender="Female",
            bloodGroup="A+",
            mobile="9876543211",
            email="external@example.com",
            aadhaar="987654321098",
            address="External",
            city="Pune",
            state="Maharashtra",
            pincode="411041",
            nationality="Indian",
            board10="SSC",
            percentage10=70.0,
            board12="HSC",
            percentage12=72.0,
            entranceExam="MHT-CET",
            entranceScore=75.0,
            department="Computer Engineering",
            admissionType="CAP",
            is_enrolled=False,
            status="Pending Verification"
        )
        db.session.add(pending_applicant)
        db.session.commit()

        books = LibraryService.get_books()
        self.assertGreater(len(books), 0)
        test_book = books[0]

        # Verify that issue_book fails for non-enrolled student
        success, msg, tx = LibraryService.issue_book(
            book_id=test_book["id"],
            student_id=pending_applicant.id
        )
        self.assertFalse(success)
        self.assertIn("Permission Denied", msg)

        # Verify non-existent student ID issue fails
        fake_succ, fake_msg, _ = LibraryService.issue_book(
            book_id=test_book["id"],
            student_id=999999
        )
        self.assertFalse(fake_succ)
        self.assertIn("Access Denied", fake_msg)

    def test_zprn_verification_workflow(self):
        # 1. Test valid ZPRN verification for enrolled college student
        success, msg, student_data = LibraryService.verify_student_by_zprn(self.student.enrollment_number)
        self.assertTrue(success)
        self.assertEqual(student_data["student_id"], self.student.id)
        self.assertEqual(student_data["fullName"], "Library Test Student")
        self.assertEqual(student_data["department"], "Computer Engineering")

        # 2. Test invalid ZPRN verification (should return "Student not found in college records")
        invalid_succ, invalid_msg, _ = LibraryService.verify_student_by_zprn("INVALID-ZPRN-9999")
        self.assertFalse(invalid_succ)
        self.assertEqual(invalid_msg, "Student not found in college records")

    def test_library_reports(self):
        buffer, err = LibraryService.generate_pdf_library_report("inventory")
        self.assertIsNone(err)
        self.assertIsNotNone(buffer)
        self.assertGreater(len(buffer.getvalue()), 100)

if __name__ == "__main__":
    unittest.main()
