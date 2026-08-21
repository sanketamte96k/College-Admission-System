from datetime import datetime, date, timedelta
from io import BytesIO
from flask import current_app
from models import db, LibraryBook, LibraryTransaction, Student, Department
from utils import sanitize_input

DEFAULT_BOOKS = [
    {
        "isbn": "978-0262033848",
        "title": "Introduction to Algorithms (CLRS)",
        "author": "Thomas H. Cormen, Charles E. Leiserson",
        "category": "Computer Engineering",
        "publisher": "MIT Press",
        "edition": "3rd Edition",
        "pub_year": 2009,
        "quantity": 10,
        "location": "Shelf CS-01",
        "description": "Comprehensive textbook covering graph algorithms, dynamic programming, sorting, and complexity."
    },
    {
        "isbn": "978-0078022159",
        "title": "Database System Concepts",
        "author": "Abraham Silberschatz, Henry F. Korth",
        "category": "Computer Engineering",
        "publisher": "McGraw-Hill",
        "edition": "7th Edition",
        "pub_year": 2019,
        "quantity": 8,
        "location": "Shelf CS-02",
        "description": "Core reference for relational database design, SQL optimization, transaction management, and indexing."
    },
    {
        "isbn": "978-1119456339",
        "title": "Operating System Concepts",
        "author": "Abraham Silberschatz, Peter B. Galvin",
        "category": "Computer Engineering",
        "publisher": "Wiley",
        "edition": "10th Edition",
        "pub_year": 2018,
        "quantity": 12,
        "location": "Shelf CS-03",
        "description": "Process scheduling, virtual memory management, Linux kernel architecture, and file systems."
    },
    {
        "isbn": "978-0133594140",
        "title": "Computer Networking: A Top-Down Approach",
        "author": "James Kurose, Keith Ross",
        "category": "Information Technology",
        "publisher": "Pearson",
        "edition": "7th Edition",
        "pub_year": 2017,
        "quantity": 9,
        "location": "Shelf IT-01",
        "description": "TCP/IP architecture, socket programming, wireless communication, and network security protocols."
    },
    {
        "isbn": "978-0134610993",
        "title": "Artificial Intelligence: A Modern Approach",
        "author": "Stuart Russell, Peter Norvig",
        "category": "Artificial Intelligence & Data Science",
        "publisher": "Pearson",
        "edition": "4th Edition",
        "pub_year": 2020,
        "quantity": 7,
        "location": "Shelf AI-01",
        "description": "Standard university textbook on machine learning, search heuristics, constraint satisfaction, and neural networks."
    },
    {
        "isbn": "978-0132350884",
        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
        "author": "Robert C. Martin",
        "category": "Information Technology",
        "publisher": "Prentice Hall",
        "edition": "1st Edition",
        "pub_year": 2008,
        "quantity": 6,
        "location": "Shelf IT-02",
        "description": "Best practices for refactoring, software architecture, unit testing, and readable code structure."
    },
    {
        "isbn": "978-0387310732",
        "title": "Pattern Recognition and Machine Learning",
        "author": "Christopher M. Bishop",
        "category": "Artificial Intelligence & Data Science",
        "publisher": "Springer",
        "edition": "1st Edition",
        "pub_year": 2006,
        "quantity": 5,
        "location": "Shelf AI-02",
        "description": "Bayesian inference, mixture models, support vector machines, and deep neural network foundations."
    },
    {
        "isbn": "978-0073398068",
        "title": "Thermodynamics: An Engineering Approach",
        "author": "Yunus A. Cengel, Michael A. Boles",
        "category": "Mechanical Engineering",
        "publisher": "McGraw-Hill",
        "edition": "8th Edition",
        "pub_year": 2014,
        "quantity": 8,
        "location": "Shelf ME-01",
        "description": "First and second laws of thermodynamics, power cycles, refrigeration, and combustion analysis."
    },
    {
        "isbn": "978-0073398242",
        "title": "Design of Concrete Structures",
        "author": "Arthur H. Nilson, David Darwin",
        "category": "Civil Engineering",
        "publisher": "McGraw-Hill",
        "edition": "15th Edition",
        "pub_year": 2016,
        "quantity": 6,
        "location": "Shelf CE-01",
        "description": "Reinforced concrete beam design, column analysis, prestressed concrete, and seismic detailing."
    },
    {
        "isbn": "978-0199321384",
        "title": "Principles of Electromagnetics",
        "author": "Matthew N.O. Sadiku",
        "category": "Electronics & Telecommunication",
        "publisher": "Oxford University Press",
        "edition": "6th Edition",
        "pub_year": 2015,
        "quantity": 7,
        "location": "Shelf ET-01",
        "description": "Maxwell's equations, wave propagation, transmission lines, waveguide theory, and antennas."
    }
]

class LibraryService:

    @staticmethod
    def initialize_default_books():
        """Ensure standard engineering textbooks are seeded into library_books table"""
        for item in DEFAULT_BOOKS:
            existing = LibraryBook.query.filter_by(isbn=item["isbn"]).first()
            if not existing:
                book = LibraryBook(
                    isbn=item["isbn"],
                    title=item["title"],
                    author=item["author"],
                    category=item["category"],
                    publisher=item["publisher"],
                    edition=item["edition"],
                    pub_year=item["pub_year"],
                    quantity=item["quantity"],
                    available_qty=item["quantity"],
                    location=item["location"],
                    status="Available",
                    description=item["description"]
                )
                db.session.add(book)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    @staticmethod
    def sync_overdue_transactions():
        """Automatically mark transactions past due date as Overdue and compute backend fines"""
        today = date.today()
        active_txs = LibraryTransaction.query.filter(
            LibraryTransaction.status.in_(["Issued", "Overdue"])
        ).all()

        updated = False
        for tx in active_txs:
            if tx.due_date < today:
                tx.status = "Overdue"
                days = (today - tx.due_date).days
                tx.overdue_days = max(0, days)
                tx.fine_amount = round(tx.overdue_days * 10.0, 2)  # ₹10 per day overdue fine
                if tx.fine_status == "None" and tx.fine_amount > 0:
                    tx.fine_status = "Pending"
                updated = True

        if updated:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

    @staticmethod
    def get_library_dashboard_summary():
        LibraryService.initialize_default_books()
        LibraryService.sync_overdue_transactions()

        books = LibraryBook.query.all()
        total_books = sum(b.quantity for b in books)
        available_books = sum(b.available_qty for b in books)
        total_titles = len(books)

        issued_txs = LibraryTransaction.query.filter_by(status="Issued").all()
        overdue_txs = LibraryTransaction.query.filter_by(status="Overdue").all()

        issued_books_count = len(issued_txs)
        overdue_books_count = len(overdue_txs)

        total_members = Student.query.filter(
            db.or_(Student.is_enrolled == True, Student.status == "Approved")
        ).count()
        if total_members == 0:
            total_members = Student.query.count()

        pending_fines = LibraryTransaction.query.filter_by(fine_status="Pending").all()
        outstanding_fines = sum(tx.fine_amount for tx in pending_fines)

        categories = db.session.query(
            LibraryBook.category, db.func.count(LibraryBook.id), db.func.sum(LibraryBook.quantity)
        ).group_by(LibraryBook.category).all()

        category_breakdown = [
            {"category": c[0], "title_count": c[1], "book_count": c[2] or 0} for c in categories
        ]

        return {
            "total_titles": total_titles,
            "total_books": total_books,
            "available_books": available_books,
            "issued_books": issued_books_count,
            "overdue_books": overdue_books_count,
            "total_members": total_members,
            "outstanding_fines": round(outstanding_fines, 2),
            "category_breakdown": category_breakdown
        }

    @staticmethod
    def get_books(category="", status="", search=""):
        LibraryService.initialize_default_books()
        query = LibraryBook.query

        if category and category.strip() and category.lower() != "all":
            query = query.filter(LibraryBook.category == category.strip())

        if status and status.strip() and status.lower() != "all":
            query = query.filter(LibraryBook.status == status.strip())

        if search and search.strip():
            sq = f"%{search.strip()}%"
            query = query.filter(
                db.or_(
                    LibraryBook.title.ilike(sq),
                    LibraryBook.author.ilike(sq),
                    LibraryBook.isbn.ilike(sq),
                    LibraryBook.publisher.ilike(sq),
                    LibraryBook.category.ilike(sq)
                )
            )

        books = query.order_by(LibraryBook.id.asc()).all()
        return [b.to_dict() for b in books]

    @staticmethod
    def get_book_by_id(book_id):
        book = LibraryBook.query.get(book_id)
        return book.to_dict() if book else None

    @staticmethod
    def add_book(data):
        isbn = sanitize_input(data.get("isbn", "")).strip()
        title = sanitize_input(data.get("title", "")).strip()
        author = sanitize_input(data.get("author", "")).strip()
        category = sanitize_input(data.get("category", "General")).strip()
        publisher = sanitize_input(data.get("publisher", "")).strip()
        edition = sanitize_input(data.get("edition", "1st Edition")).strip()
        location = sanitize_input(data.get("location", "Shelf A-1")).strip()
        description = sanitize_input(data.get("description", "")).strip()

        if not isbn or not title or not author:
            return False, "ISBN, Title, and Author are required fields.", None

        try:
            quantity = int(data.get("quantity", 1))
            if quantity < 0:
                return False, "Quantity cannot be negative.", None
        except (ValueError, TypeError):
            return False, "Quantity must be a valid non-negative integer.", None

        try:
            pub_year = int(data.get("pub_year", 2024))
        except (ValueError, TypeError):
            pub_year = 2024

        existing = LibraryBook.query.filter_by(isbn=isbn).first()
        if existing:
            return False, f"Book with ISBN '{isbn}' already exists in library catalog.", None

        status = "Available" if quantity > 0 else "Unavailable"

        new_book = LibraryBook(
            isbn=isbn,
            title=title,
            author=author,
            category=category,
            publisher=publisher,
            edition=edition,
            pub_year=pub_year,
            quantity=quantity,
            available_qty=quantity,
            location=location,
            status=status,
            description=description
        )

        db.session.add(new_book)
        db.session.commit()
        return True, f"Book '{title}' added successfully to catalog.", new_book.to_dict()

    @staticmethod
    def update_book(book_id, data):
        book = LibraryBook.query.get(book_id)
        if not book:
            return False, "Book record not found.", None

        if "isbn" in data and data["isbn"]:
            new_isbn = sanitize_input(data["isbn"]).strip()
            if new_isbn != book.isbn:
                dup = LibraryBook.query.filter_by(isbn=new_isbn).first()
                if dup:
                    return False, f"ISBN '{new_isbn}' is already assigned to another book.", None
                book.isbn = new_isbn

        if "title" in data and data["title"]: book.title = sanitize_input(data["title"]).strip()
        if "author" in data and data["author"]: book.author = sanitize_input(data["author"]).strip()
        if "category" in data and data["category"]: book.category = sanitize_input(data["category"]).strip()
        if "publisher" in data: book.publisher = sanitize_input(data["publisher"]).strip()
        if "edition" in data: book.edition = sanitize_input(data["edition"]).strip()
        if "location" in data: book.location = sanitize_input(data["location"]).strip()
        if "description" in data: book.description = sanitize_input(data["description"]).strip()

        if "quantity" in data:
            try:
                new_qty = int(data["quantity"])
                if new_qty < 0:
                    return False, "Quantity cannot be negative.", None

                issued_qty = book.quantity - book.available_qty
                if new_qty < issued_qty:
                    return False, f"Cannot reduce total quantity below currently issued count ({issued_qty}).", None

                book.available_qty = new_qty - issued_qty
                book.quantity = new_qty
            except (ValueError, TypeError):
                pass

        if book.available_qty <= 0:
            book.status = "Unavailable"
        elif book.available_qty < book.quantity:
            book.status = "Partially Available"
        else:
            book.status = "Available"

        db.session.commit()
        return True, f"Book '{book.title}' updated successfully.", book.to_dict()

    @staticmethod
    def delete_book(book_id):
        book = LibraryBook.query.get(book_id)
        if not book:
            return False, "Book record not found."

        active_issues = LibraryTransaction.query.filter(
            LibraryTransaction.book_id == book_id,
            LibraryTransaction.status.in_(["Issued", "Overdue"])
        ).count()

        if active_issues > 0:
            return False, f"Cannot delete book '{book.title}' because {active_issues} copy/copies are currently issued to students."

        db.session.delete(book)
        db.session.commit()
        return True, f"Book '{book.title}' deleted successfully from catalog."

    @staticmethod
    def get_members(department="", search="", only_eligible=False):
        LibraryService.sync_overdue_transactions()
        query = Student.query

        if only_eligible:
            query = query.filter(
                db.or_(Student.is_enrolled == True, Student.status.in_(["Approved", "Enrolled"]))
            )

        if department and department.strip() and department.lower() != "all":
            query = query.filter(Student.department == department.strip())

        if search and search.strip():
            sq = f"%{search.strip()}%"
            query = query.filter(
                db.or_(
                    Student.fullName.ilike(sq),
                    Student.email.ilike(sq),
                    Student.enrollment_number.ilike(sq),
                    Student.department.ilike(sq)
                )
            )

        students = query.order_by(Student.id.asc()).all()

        members = []
        for s in students:
            txs = LibraryTransaction.query.filter_by(student_id=s.id).all()
            active_issued = sum(1 for t in txs if t.status in ["Issued", "Overdue"])
            overdue_count = sum(1 for t in txs if t.status == "Overdue")
            pending_fine = sum(t.fine_amount for t in txs if t.fine_status == "Pending")

            members.append({
                "student_id": s.id,
                "fullName": s.fullName,
                "roll_number": s.enrollment_number or f"STU-{s.id:04d}",
                "department": s.department or "-",
                "course": s.course or f"B.Tech in {s.department or 'Engineering'}",
                "academic_year": s.academic_year or "2026-27",
                "issued_books_count": active_issued,
                "overdue_count": overdue_count,
                "outstanding_fine": round(pending_fine, 2),
                "is_enrolled": bool(s.is_enrolled),
                "status": "Active Member" if (s.is_enrolled or s.status == "Approved") else "Pending"
            })

    @staticmethod
    def verify_student_by_zprn(zprn_input):
        if not zprn_input or not str(zprn_input).strip():
            return False, "Student not found in college records", None

        zprn_clean = str(zprn_input).strip()

        # 1. Direct match on enrollment_number
        student = Student.query.filter(
            db.func.lower(Student.enrollment_number) == zprn_clean.lower()
        ).first()

        # 2. Try integer primary key match if digits only
        if not student and zprn_clean.isdigit():
            student = Student.query.get(int(zprn_clean))

        # 3. Fallback search by formatted student codes (ADM-2026-000X, STU-000X, ZPRN-000X)
        if not student:
            all_students = Student.query.all()
            for s in all_students:
                app_code = f"ADM-2026-{s.id:04d}"
                roll_code = s.enrollment_number or f"STU-{s.id:04d}"
                zprn_code = f"ZPRN-2026-{s.id:04d}"
                if zprn_clean.upper() in [app_code.upper(), roll_code.upper(), zprn_code.upper(), str(s.id)]:
                    student = s
                    break

        if not student:
            return False, "Student not found in college records", None

        # 4. Enforce official college enrollment check
        if not student.is_enrolled and student.status not in ["Approved", "Enrolled"]:
            return False, "Student not found in college records", None

        # Compute current active borrowed books count
        active_issued = LibraryTransaction.query.filter(
            LibraryTransaction.student_id == student.id,
            LibraryTransaction.status.in_(["Issued", "Overdue"])
        ).count()

        year_num = int(student.academic_year) if (student.academic_year and str(student.academic_year).isdigit()) else 1
        sem_num = (year_num * 2) - 1

        return True, "Student verified in college records.", {
            "student_id": student.id,
            "zprn": student.enrollment_number or f"ZPRN-2026-{student.id:04d}",
            "fullName": student.fullName,
            "department": student.department or "Engineering",
            "course": student.course or f"B.Tech in {student.department or 'Engineering'}",
            "academic_year": f"Year {year_num}",
            "semester": f"Semester {sem_num}",
            "active_issued_books": active_issued,
            "status": "Officially Enrolled"
        }

    @staticmethod
    def issue_book(book_id, student_id, issue_date_str=None, due_date_str=None, remarks="", admin_username="admin"):
        LibraryService.sync_overdue_transactions()

        book = LibraryBook.query.get(book_id)
        if not book:
            return False, "Selected book record not found.", None

        if book.available_qty <= 0:
            return False, f"Book '{book.title}' has zero available copies in stock.", None

        student = Student.query.get(student_id)
        if not student:
            return False, "Access Denied: Student is not registered in the college database. Book issue permission denied.", None

        # Strict college student enrollment check
        if not student.is_enrolled and student.status not in ["Approved", "Enrolled"]:
            return False, f"Permission Denied: Student '{student.fullName}' is not an active/enrolled student of this college (Status: {student.status or 'Pending'}). Library book issue is strictly restricted to valid college students.", None

        # Prevent duplicate active issue of the exact same book to the same student
        dup_issue = LibraryTransaction.query.filter(
            LibraryTransaction.book_id == book_id,
            LibraryTransaction.student_id == student_id,
            LibraryTransaction.status.in_(["Issued", "Overdue"])
        ).first()

        if dup_issue:
            return False, f"Student '{student.fullName}' already has an active copy of '{book.title}' issued on {dup_issue.issue_date}.", None

        # Date resolution
        today = date.today()
        if issue_date_str:
            try:
                iss_date = datetime.strptime(issue_date_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                iss_date = today
        else:
            iss_date = today

        if due_date_str:
            try:
                d_date = datetime.strptime(due_date_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                d_date = iss_date + timedelta(days=14)
        else:
            d_date = iss_date + timedelta(days=14)  # Default 14-day borrowing period

        if d_date < iss_date:
            return False, "Due date cannot be before issue date.", None

        # Decrement inventory and record transaction
        book.available_qty -= 1
        if book.available_qty <= 0:
            book.status = "Unavailable"
        else:
            book.status = "Partially Available"

        tx = LibraryTransaction(
            book_id=book.id,
            student_id=student.id,
            issue_date=iss_date,
            due_date=d_date,
            status="Issued",
            overdue_days=0,
            fine_amount=0.0,
            fine_status="None",
            remarks=sanitize_input(remarks),
            issued_by=admin_username
        )

        db.session.add(tx)
        db.session.commit()
        return True, f"Book '{book.title}' successfully issued to {student.fullName}.", tx.to_dict()

    @staticmethod
    def return_book(transaction_id, return_date_str=None, fine_action="Pending", remarks=""):
        tx = LibraryTransaction.query.get(transaction_id)
        if not tx:
            return False, "Library transaction record not found.", None

        if tx.status == "Returned":
            return False, "This book transaction has already been marked as returned.", None

        today = date.today()
        if return_date_str:
            try:
                ret_date = datetime.strptime(return_date_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                ret_date = today
        else:
            ret_date = today

        # Calculate backend overdue days and fine amount (₹10/day)
        overdue_days = max(0, (ret_date - tx.due_date).days)
        fine_amount = round(overdue_days * 10.0, 2)

        tx.return_date = ret_date
        tx.overdue_days = overdue_days
        tx.fine_amount = fine_amount
        tx.status = "Returned"

        if fine_amount > 0:
            f_action = (fine_action or "Pending").strip().capitalize()
            if f_action in ["Paid", "Waived", "Pending"]:
                tx.fine_status = f_action
            else:
                tx.fine_status = "Pending"
        else:
            tx.fine_status = "None"

        if remarks:
            tx.remarks = (tx.remarks or "") + " | Return Note: " + sanitize_input(remarks)

        # Restore book inventory
        book = tx.book
        if book:
            book.available_qty = min(book.quantity, book.available_qty + 1)
            if book.available_qty == book.quantity:
                book.status = "Available"
            else:
                book.status = "Partially Available"

        db.session.commit()
        return True, f"Book '{book.title if book else ''}' successfully returned by {tx.student.fullName if tx.student else ''}.", tx.to_dict()

    @staticmethod
    def get_transactions(status="", student_id=None, book_id=None, search=""):
        LibraryService.sync_overdue_transactions()
        query = LibraryTransaction.query

        if status and status.strip() and status.lower() != "all":
            query = query.filter(LibraryTransaction.status == status.strip())

        if student_id:
            query = query.filter(LibraryTransaction.student_id == student_id)

        if book_id:
            query = query.filter(LibraryTransaction.book_id == book_id)

        if search and search.strip():
            sq = f"%{search.strip()}%"
            query = query.join(LibraryBook).join(Student).filter(
                db.or_(
                    LibraryBook.title.ilike(sq),
                    LibraryBook.isbn.ilike(sq),
                    Student.fullName.ilike(sq),
                    Student.enrollment_number.ilike(sq)
                )
            )

        txs = query.order_by(LibraryTransaction.id.desc()).all()
        return [t.to_dict() for t in txs]

    @staticmethod
    def get_overdue_list():
        LibraryService.sync_overdue_transactions()
        overdue_txs = LibraryTransaction.query.filter(
            LibraryTransaction.status.in_(["Issued", "Overdue"]),
            LibraryTransaction.due_date < date.today()
        ).order_by(LibraryTransaction.due_date.asc()).all()

        return [t.to_dict() for t in overdue_txs]

    @staticmethod
    def update_fine_status(transaction_id, fine_status):
        tx = LibraryTransaction.query.get(transaction_id)
        if not tx:
            return False, "Transaction not found."

        status_clean = (fine_status or "").strip().capitalize()
        if status_clean not in ["Paid", "Waived", "Pending", "None"]:
            return False, "Invalid fine status. Expected Paid, Waived, or Pending."

        tx.fine_status = status_clean
        db.session.commit()
        return True, f"Fine status for transaction #{tx.id} updated to '{status_clean}'."

    @staticmethod
    def generate_pdf_library_report(report_type="inventory"):
        """Generate certified ReportLab PDF library reports reusing existing PDF infrastructure"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        except ImportError:
            return None, "ReportLab library not available."

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'LibTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0F172A'),
            alignment=1,
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'LibSub',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#2563EB'),
            alignment=1,
            spaceAfter=15
        )

        cell_style = ParagraphStyle('LibCell', fontName='Helvetica', fontSize=9, leading=11, textColor=colors.HexColor('#1E293B'))
        header_cell_style = ParagraphStyle('LibHeaderCell', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white)

        elements.append(Paragraph("ZEAL COLLEGE OF ENGINEERING & RESEARCH", title_style))

        if report_type == "overdue":
            elements.append(Paragraph("OFFICIAL LIBRARY OVERDUE BOOKS REPORT", subtitle_style))
            data = LibraryService.get_overdue_list()
            table_data = [[
                Paragraph("TX ID", header_cell_style),
                Paragraph("Student Name", header_cell_style),
                Paragraph("Book Title", header_cell_style),
                Paragraph("Issue Date", header_cell_style),
                Paragraph("Due Date", header_cell_style),
                Paragraph("Overdue Days", header_cell_style),
                Paragraph("Fine (₹)", header_cell_style)
            ]]
            for row in data:
                table_data.append([
                    Paragraph(f"#{row['id']}", cell_style),
                    Paragraph(row['student_name'], cell_style),
                    Paragraph(row['book_title'], cell_style),
                    Paragraph(row['issue_date'], cell_style),
                    Paragraph(row['due_date'], cell_style),
                    Paragraph(f"{row['overdue_days']} Days", cell_style),
                    Paragraph(f"₹{row['fine_amount']}", cell_style)
                ])
            col_widths = [45, 110, 150, 70, 70, 70, 55]
        else:
            elements.append(Paragraph("OFFICIAL LIBRARY BOOK INVENTORY REPORT", subtitle_style))
            data = LibraryService.get_books()
            table_data = [[
                Paragraph("ISBN", header_cell_style),
                Paragraph("Title", header_cell_style),
                Paragraph("Author", header_cell_style),
                Paragraph("Category", header_cell_style),
                Paragraph("Qty", header_cell_style),
                Paragraph("Available", header_cell_style),
                Paragraph("Status", header_cell_style)
            ]]
            for row in data:
                table_data.append([
                    Paragraph(row['isbn'], cell_style),
                    Paragraph(row['title'], cell_style),
                    Paragraph(row['author'], cell_style),
                    Paragraph(row['category'], cell_style),
                    Paragraph(str(row['quantity']), cell_style),
                    Paragraph(str(row['available_qty']), cell_style),
                    Paragraph(row['status'], cell_style)
                ])
            col_widths = [85, 140, 110, 110, 35, 45, 65]

        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(t)
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Records: {len(data)}", cell_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer, None
