from datetime import datetime
from models import db, Course, Subject, Student, Department
from utils import sanitize_input

DEFAULT_COURSES = [
    {
        "name": "B.Tech Computer Engineering",
        "code": "BTECH-COMP",
        "department": "Computer Engineering",
        "degree_type": "B.Tech",
        "duration_years": 4,
        "total_semesters": 8,
        "total_credits": 160,
        "status": "Active",
        "description": "4-Year Undergraduate Degree Program in Computer Systems, Algorithms, and Software Engineering."
    },
    {
        "name": "B.Tech Information Technology",
        "code": "BTECH-IT",
        "department": "Information Technology",
        "degree_type": "B.Tech",
        "duration_years": 4,
        "total_semesters": 8,
        "total_credits": 160,
        "status": "Active",
        "description": "4-Year Undergraduate Degree Program in Cloud Computing, Cybersecurity, and Web Infrastructure."
    },
    {
        "name": "B.Tech AI & Data Science",
        "code": "BTECH-AIDS",
        "department": "Artificial Intelligence & Data Science",
        "degree_type": "B.Tech",
        "duration_years": 4,
        "total_semesters": 8,
        "total_credits": 160,
        "status": "Active",
        "description": "4-Year Degree Program in Machine Learning, Deep Neural Networks, and Predictive Analytics."
    },
    {
        "name": "B.Tech Electronics & Telecommunication",
        "code": "BTECH-ENTC",
        "department": "Electronics & Telecommunication",
        "degree_type": "B.Tech",
        "duration_years": 4,
        "total_semesters": 8,
        "total_credits": 160,
        "status": "Active",
        "description": "4-Year Degree Program in Embedded Systems, IoT Architectures, and Signal Processing."
    },
    {
        "name": "B.Tech Mechanical Engineering",
        "code": "BTECH-MECH",
        "department": "Mechanical Engineering",
        "degree_type": "B.Tech",
        "duration_years": 4,
        "total_semesters": 8,
        "total_credits": 160,
        "status": "Active",
        "description": "4-Year Degree Program in Thermodynamics, Robotics Automation, and CAD/CAM Design."
    },
    {
        "name": "B.Tech Civil Engineering",
        "code": "BTECH-CIVIL",
        "department": "Civil Engineering",
        "degree_type": "B.Tech",
        "duration_years": 4,
        "total_semesters": 8,
        "total_credits": 160,
        "status": "Active",
        "description": "4-Year Degree Program in Structural Engineering, Smart City Planning, and Geotechnical Science."
    },
    {
        "name": "B.Tech Electrical Engineering",
        "code": "BTECH-ELEC",
        "department": "Electrical Engineering",
        "degree_type": "B.Tech",
        "duration_years": 4,
        "total_semesters": 8,
        "total_credits": 160,
        "status": "Active",
        "description": "4-Year Degree Program in Smart Grids, Power Electronics, and Renewable Energy Systems."
    }
]

# Standard curriculum subjects across 4 years / 8 semesters for Computer Engineering & General Engineering
DEFAULT_SUBJECTS = [
    # 1st Year - Semester 1
    {"code": "FE101", "name": "Engineering Mathematics I", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 1, "sem": 1, "credits": 4, "type": "Core", "desc": "Linear algebra, calculus, and differential equations."},
    {"code": "FE102", "name": "Engineering Physics", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 1, "sem": 1, "credits": 4, "type": "Core", "desc": "Semiconductors, lasers, and quantum mechanics."},
    {"code": "FE103", "name": "Basic Computer Programming", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 1, "sem": 1, "credits": 3, "type": "Core", "desc": "C programming, control flow, functions, and pointers."},
    {"code": "FE104", "name": "Programming Lab", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 1, "sem": 1, "credits": 2, "type": "Lab", "desc": "Practical laboratory for C programming."},

    # 1st Year - Semester 2
    {"code": "FE201", "name": "Engineering Mathematics II", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 1, "sem": 2, "credits": 4, "type": "Core", "desc": "Vector calculus and Fourier transforms."},
    {"code": "FE202", "name": "Basic Electrical Engineering", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 1, "sem": 2, "credits": 3, "type": "Core", "desc": "AC/DC circuits, transformers, and electrical machines."},
    {"code": "FE203", "name": "Object Oriented Programming", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 1, "sem": 2, "credits": 4, "type": "Core", "desc": "C++ classes, inheritance, polymorphism, and STL."},
    {"code": "FE204", "name": "OOP Laboratory", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 1, "sem": 2, "credits": 2, "type": "Lab", "desc": "Hands-on object oriented software design lab."},

    # 2nd Year - Semester 3
    {"code": "CS301", "name": "Data Structures & Algorithms", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 2, "sem": 3, "credits": 4, "type": "Core", "desc": "Arrays, trees, graphs, sorting, searching, and complexity."},
    {"code": "CS302", "name": "Database Management Systems", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 2, "sem": 3, "credits": 4, "type": "Core", "desc": "Relational algebra, SQL, normalization, transactions, and indexing."},
    {"code": "CS303", "name": "Computer Organization & Architecture", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 2, "sem": 3, "credits": 3, "type": "Core", "desc": "CPU design, ALU, memory hierarchy, and instruction sets."},
    {"code": "CS304", "name": "Discrete Mathematics", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 2, "sem": 3, "credits": 4, "type": "Core", "desc": "Set theory, logic, combinatorics, and graph theory."},
    {"code": "CS305", "name": "DBMS Laboratory", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 2, "sem": 3, "credits": 2, "type": "Lab", "desc": "Hands-on MySQL database queries and transaction lab."},

    # 2nd Year - Semester 4
    {"code": "CS401", "name": "Operating Systems", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 2, "sem": 4, "credits": 4, "type": "Core", "desc": "Process scheduling, memory management, file systems, and concurrency."},
    {"code": "CS402", "name": "Theory of Computation", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 2, "sem": 4, "credits": 4, "type": "Core", "desc": "Automata theory, regular expressions, grammars, and Turing machines."},
    {"code": "CS403", "name": "Software Engineering", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 2, "sem": 4, "credits": 3, "type": "Core", "desc": "Agile methodologies, UML modeling, testing, and DevOps."},
    {"code": "CS404", "name": "OS & System Programming Lab", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 2, "sem": 4, "credits": 2, "type": "Lab", "desc": "Linux shell scripting and system calls lab."},

    # 3rd Year - Semester 5
    {"code": "CS501", "name": "Computer Networks", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 3, "sem": 5, "credits": 4, "type": "Core", "desc": "TCP/IP protocol suite, routing, sockets, and network security."},
    {"code": "CS502", "name": "Web Technology", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 3, "sem": 5, "credits": 3, "type": "Core", "desc": "Full-stack HTML/CSS, JS, Node.js, and REST APIs."},
    {"code": "CS503", "name": "Artificial Intelligence", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 3, "sem": 5, "credits": 4, "type": "Elective", "desc": "Search algorithms, knowledge representation, and expert systems."},
    {"code": "CS504", "name": "Network Systems Lab", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 3, "sem": 5, "credits": 2, "type": "Lab", "desc": "Wireshark packet analysis and socket programming."},

    # 3rd Year - Semester 6
    {"code": "CS601", "name": "Compiler Construction", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 3, "sem": 6, "credits": 4, "type": "Core", "desc": "Lexical analysis, parsing, intermediate code, and code generation."},
    {"code": "CS602", "name": "Cloud Computing", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 3, "sem": 6, "credits": 3, "type": "Elective", "desc": "AWS, virtualization, microservices, and serverless architecture."},
    {"code": "CS603", "name": "Information Security", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 3, "sem": 6, "credits": 4, "type": "Core", "desc": "Cryptography, AES/RSA algorithms, firewalls, and ethical hacking."},
    {"code": "CS604", "name": "Mini Project", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 3, "sem": 6, "credits": 3, "type": "Project", "desc": "Industry mini project implementation."},

    # 4th Year - Semester 7
    {"code": "CS701", "name": "Machine Learning", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 4, "sem": 7, "credits": 4, "type": "Core", "desc": "Supervised/unsupervised learning, neural networks, and Scikit-Learn."},
    {"code": "CS702", "name": "Distributed Systems", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 4, "sem": 7, "credits": 3, "type": "Elective", "desc": "Consensus protocols, MapReduce, and distributed consensus."},
    {"code": "CS703", "name": "Capstone Project Phase I", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 4, "sem": 7, "credits": 4, "type": "Project", "desc": "Final year major capstone project problem definition and literature review."},

    # 4th Year - Semester 8
    {"code": "CS801", "name": "Deep Learning & Vision", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 4, "sem": 8, "credits": 4, "type": "Elective", "desc": "CNNs, RNNs, Transformers, and PyTorch deep learning models."},
    {"code": "CS802", "name": "Cyber Laws & Ethics", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 4, "sem": 8, "credits": 3, "type": "Core", "desc": "IT Act, intellectual property, data privacy laws, and compliance."},
    {"code": "CS803", "name": "Capstone Project Phase II", "dept": "Computer Engineering", "program": "B.Tech Computer Engineering", "year": 4, "sem": 8, "credits": 6, "type": "Project", "desc": "Final year major project implementation, testing, and paper publication."}
]

class CourseService:

    @staticmethod
    def initialize_courses_and_subjects():
        """Ensure standard degree programs and subjects are populated into database tables"""
        # 1. Initialize Courses
        for c_item in DEFAULT_COURSES:
            existing = Course.query.filter(
                db.or_(Course.name == c_item["name"], Course.code == c_item["code"])
            ).first()
            if not existing:
                course = Course(
                    name=c_item["name"],
                    code=c_item["code"],
                    department=c_item["department"],
                    degree_type=c_item["degree_type"],
                    duration_years=c_item["duration_years"],
                    total_semesters=c_item["total_semesters"],
                    total_credits=c_item["total_credits"],
                    status=c_item["status"],
                    description=c_item["description"]
                )
                db.session.add(course)

        # 2. Initialize Subjects
        for s_item in DEFAULT_SUBJECTS:
            existing_sub = Subject.query.filter_by(code=s_item["code"]).first()
            if not existing_sub:
                sub = Subject(
                    code=s_item["code"],
                    name=s_item["name"],
                    department=s_item["dept"],
                    program=s_item["program"],
                    academic_year=s_item["year"],
                    semester=s_item["sem"],
                    credits=s_item["credits"],
                    subject_type=s_item["type"],
                    status="Active",
                    description=s_item["desc"]
                )
                db.session.add(sub)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    @staticmethod
    def get_all_courses(department="", search="", status=""):
        CourseService.initialize_courses_and_subjects()
        query = Course.query

        if department:
            query = query.filter(Course.department == department)
        if search:
            sq = search.strip()
            query = query.filter(
                db.or_(
                    Course.name.ilike(f"%{sq}%"),
                    Course.code.ilike(f"%{sq}%"),
                    Course.department.ilike(f"%{sq}%")
                )
            )
        if status:
            query = query.filter(Course.status == status)

        courses = query.order_by(Course.id.asc()).all()

        result = []
        for c in courses:
            c_dict = c.to_dict()
            subject_count = Subject.query.filter(Subject.program == c.name).count()
            c_dict["subject_count"] = subject_count
            result.append(c_dict)

        return result

    @staticmethod
    def get_curriculum(department="", program="", academic_year=None, semester=None, search="", status=""):
        CourseService.initialize_courses_and_subjects()
        
        # Build query for subjects
        query = Subject.query

        if department:
            query = query.filter(Subject.department == department)
        if program:
            query = query.filter(Subject.program == program)
        if academic_year and str(academic_year).isdigit():
            query = query.filter(Subject.academic_year == int(academic_year))
        if semester and str(semester).isdigit():
            query = query.filter(Subject.semester == int(semester))
        if status:
            query = query.filter(Subject.status == status)
        if search:
            sq = search.strip()
            query = query.filter(
                db.or_(
                    Subject.name.ilike(f"%{sq}%"),
                    Subject.code.ilike(f"%{sq}%"),
                    Subject.department.ilike(f"%{sq}%"),
                    Subject.program.ilike(f"%{sq}%")
                )
            )

        all_subjects = query.order_by(Subject.academic_year.asc(), Subject.semester.asc(), Subject.code.asc()).all()

        # Summary statistics
        total_subjects = len(all_subjects)
        total_credits = sum(s.credits or 0 for s in all_subjects)
        core_count = sum(1 for s in all_subjects if (s.subject_type or "").lower() == "core")
        elective_count = sum(1 for s in all_subjects if (s.subject_type or "").lower() == "elective")
        lab_count = sum(1 for s in all_subjects if (s.subject_type or "").lower() == "lab")
        project_count = sum(1 for s in all_subjects if (s.subject_type or "").lower() == "project")

        # Group by Year & Semester (Sem 1 to 8)
        years_breakdown = []
        
        for year_num in range(1, 5):  # 1st Year, 2nd Year, 3rd Year, 4th Year
            sem_1_num = (year_num * 2) - 1
            sem_2_num = year_num * 2

            sem_1_subs = [s.to_dict() for s in all_subjects if s.academic_year == year_num and s.semester == sem_1_num]
            sem_2_subs = [s.to_dict() for s in all_subjects if s.academic_year == year_num and s.semester == sem_2_num]

            year_obj = {
                "academic_year": year_num,
                "year_name": f"{year_num}st Year" if year_num == 1 else (f"{year_num}nd Year" if year_num == 2 else (f"{year_num}rd Year" if year_num == 3 else f"{year_num}th Year")),
                "semesters": [
                    {
                        "semester_number": sem_1_num,
                        "semester_name": f"Semester {sem_1_num}",
                        "academic_year": year_num,
                        "subject_count": len(sem_1_subs),
                        "total_credits": sum(s["credits"] for s in sem_1_subs),
                        "core_count": sum(1 for s in sem_1_subs if s["subject_type"].lower() == "core"),
                        "elective_count": sum(1 for s in sem_1_subs if s["subject_type"].lower() == "elective"),
                        "subjects": sem_1_subs
                    },
                    {
                        "semester_number": sem_2_num,
                        "semester_name": f"Semester {sem_2_num}",
                        "academic_year": year_num,
                        "subject_count": len(sem_2_subs),
                        "total_credits": sum(s["credits"] for s in sem_2_subs),
                        "core_count": sum(1 for s in sem_2_subs if s["subject_type"].lower() == "core"),
                        "elective_count": sum(1 for s in sem_2_subs if s["subject_type"].lower() == "elective"),
                        "subjects": sem_2_subs
                    }
                ]
            }
            years_breakdown.append(year_obj)

        total_courses_count = Course.query.count()

        return {
            "summary": {
                "total_programs": total_courses_count,
                "total_subjects": total_subjects,
                "total_credits": total_credits,
                "core_subjects": core_count,
                "elective_subjects": elective_count,
                "lab_subjects": lab_count,
                "project_subjects": project_count
            },
            "curriculum": years_breakdown
        }

    @staticmethod
    def get_course_by_id(course_id):
        course = Course.query.get(course_id)
        if not course:
            return None
        c_dict = course.to_dict()
        c_dict["subject_count"] = Subject.query.filter(Subject.program == course.name).count()
        return c_dict

    @staticmethod
    def create_course(data):
        name = sanitize_input(data.get("name", ""))
        code = sanitize_input(data.get("code", "")).upper()
        department = sanitize_input(data.get("department", ""))
        degree_type = sanitize_input(data.get("degree_type", "B.Tech"))
        description = sanitize_input(data.get("description", ""))
        status = sanitize_input(data.get("status", "Active"))

        try:
            duration_years = int(data.get("duration_years", 4))
            total_semesters = int(data.get("total_semesters", 8))
            total_credits = int(data.get("total_credits", 160))
        except (ValueError, TypeError):
            duration_years, total_semesters, total_credits = 4, 8, 160

        if not name or not code or not department:
            raise ValueError("Program Name, Code, and Department are required.")

        existing = Course.query.filter(
            db.or_(Course.name == name, Course.code == code)
        ).first()
        if existing:
            raise ValueError(f"A program with name '{name}' or code '{code}' already exists.")

        new_course = Course(
            name=name,
            code=code,
            department=department,
            degree_type=degree_type,
            duration_years=duration_years,
            total_semesters=total_semesters,
            total_credits=total_credits,
            status=status,
            description=description
        )

        db.session.add(new_course)
        db.session.commit()
        return new_course

    @staticmethod
    def update_course(course_id, data):
        course = Course.query.get(course_id)
        if not course:
            return None

        if "name" in data and data["name"]:
            name = sanitize_input(data["name"])
            existing = Course.query.filter(Course.name == name, Course.id != course_id).first()
            if existing:
                raise ValueError(f"Another program already uses name '{name}'.")
            
            old_name = course.name
            course.name = name
            if old_name != name:
                Subject.query.filter(Subject.program == old_name).update({"program": name})
                Student.query.filter(Student.course == old_name).update({"course": name})

        if "code" in data and data["code"]:
            code = sanitize_input(data["code"]).upper()
            existing = Course.query.filter(Course.code == code, Course.id != course_id).first()
            if existing:
                raise ValueError(f"Another program already uses code '{code}'.")
            course.code = code

        if "department" in data:
            course.department = sanitize_input(data["department"])
        if "degree_type" in data:
            course.degree_type = sanitize_input(data["degree_type"])
        if "status" in data:
            course.status = sanitize_input(data["status"])
        if "description" in data:
            course.description = sanitize_input(data["description"])

        try:
            if "total_credits" in data: course.total_credits = int(data["total_credits"])
            if "duration_years" in data: course.duration_years = int(data["duration_years"])
            if "total_semesters" in data: course.total_semesters = int(data["total_semesters"])
        except (ValueError, TypeError):
            pass

        db.session.commit()
        return course

    @staticmethod
    def delete_course(course_id):
        course = Course.query.get(course_id)
        if not course:
            return False, "Program record not found."

        # Check dependent student records
        student_count = Student.query.filter(Student.course == course.name).count()
        if student_count > 0:
            return False, f"Cannot delete program '{course.name}' because {student_count} student record(s) are enrolled in it. Please reassign students first."

        # Check dependent subjects
        sub_count = Subject.query.filter(Subject.program == course.name).count()
        if sub_count > 0:
            return False, f"Cannot delete program '{course.name}' because {sub_count} subject(s) belong to its curriculum. Delete or reassign subjects first."

        db.session.delete(course)
        db.session.commit()
        return True, f"Program '{course.name}' deleted successfully."

    # ============================================================
    # SUBJECT CRUD METHODS
    # ============================================================

    @staticmethod
    def get_subject_by_id(subject_id):
        sub = Subject.query.get(subject_id)
        return sub.to_dict() if sub else None

    @staticmethod
    def create_subject(data):
        code = sanitize_input(data.get("code", "")).upper()
        name = sanitize_input(data.get("name", ""))
        department = sanitize_input(data.get("department", ""))
        program = sanitize_input(data.get("program", ""))
        subject_type = sanitize_input(data.get("subject_type", "Core"))
        description = sanitize_input(data.get("description", ""))
        status = sanitize_input(data.get("status", "Active"))

        try:
            academic_year = int(data.get("academic_year", 1))
            semester = int(data.get("semester", 1))
            credits = int(data.get("credits", 4))
        except (ValueError, TypeError):
            academic_year, semester, credits = 1, 1, 4

        if not code or not name or not department or not program:
            raise ValueError("Subject Code, Name, Department, and Program are required.")

        if academic_year not in [1, 2, 3, 4]:
            raise ValueError("Academic Year must be between 1 and 4.")

        if semester not in range(1, 9):
            raise ValueError("Semester must be between 1 and 8.")

        existing = Subject.query.filter_by(code=code).first()
        if existing:
            raise ValueError(f"A subject with code '{code}' already exists.")

        new_sub = Subject(
            code=code,
            name=name,
            department=department,
            program=program,
            academic_year=academic_year,
            semester=semester,
            credits=credits,
            subject_type=subject_type,
            status=status,
            description=description
        )

        db.session.add(new_sub)
        db.session.commit()
        return new_sub

    @staticmethod
    def update_subject(subject_id, data):
        sub = Subject.query.get(subject_id)
        if not sub:
            return None

        if "code" in data and data["code"]:
            code = sanitize_input(data["code"]).upper()
            existing = Subject.query.filter(Subject.code == code, Subject.id != subject_id).first()
            if existing:
                raise ValueError(f"Another subject already uses code '{code}'.")
            sub.code = code

        if "name" in data and data["name"]:
            sub.name = sanitize_input(data["name"])
        if "department" in data:
            sub.department = sanitize_input(data["department"])
        if "program" in data:
            sub.program = sanitize_input(data["program"])
        if "subject_type" in data:
            sub.subject_type = sanitize_input(data["subject_type"])
        if "status" in data:
            sub.status = sanitize_input(data["status"])
        if "description" in data:
            sub.description = sanitize_input(data["description"])

        try:
            if "academic_year" in data: sub.academic_year = int(data["academic_year"])
            if "semester" in data: sub.semester = int(data["semester"])
            if "credits" in data: sub.credits = int(data["credits"])
        except (ValueError, TypeError):
            pass

        db.session.commit()
        return sub

    @staticmethod
    def delete_subject(subject_id):
        sub = Subject.query.get(subject_id)
        if not sub:
            return False, "Subject record not found."

        db.session.delete(sub)
        db.session.commit()
        return True, f"Subject '{sub.name}' ({sub.code}) deleted successfully."
