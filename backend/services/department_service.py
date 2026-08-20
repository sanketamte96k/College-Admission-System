from datetime import datetime
from models import db, Department, Student, SeatMatrix
from utils import sanitize_input

DEFAULT_DEPARTMENTS = [
    {
        "name": "Computer Engineering",
        "code": "COMP",
        "hod_name": "Dr. A. R. Sharma",
        "hod_email": "hod.comp@zeal.edu.in",
        "description": "Software systems, algorithms, computing labs, database architectures, and full-stack engineering.",
        "total_seats": 120,
        "status": "Active"
    },
    {
        "name": "Information Technology",
        "code": "IT",
        "hod_name": "Prof. S. P. Kulkarni",
        "hod_email": "hod.it@zeal.edu.in",
        "description": "Web systems, cloud computing, cyber network security, and enterprise infrastructure solutions.",
        "total_seats": 60,
        "status": "Active"
    },
    {
        "name": "Artificial Intelligence & Data Science",
        "code": "AI & DS",
        "hod_name": "Dr. M. V. Joshi",
        "hod_email": "hod.aids@zeal.edu.in",
        "description": "Machine learning, neural networks, predictive analytics, computer vision, and deep learning algorithms.",
        "total_seats": 60,
        "status": "Active"
    },
    {
        "name": "Electronics & Telecommunication",
        "code": "E&TC",
        "hod_name": "Prof. R. N. Deshmukh",
        "hod_email": "hod.entc@zeal.edu.in",
        "description": "Embedded systems, IoT architecture, wireless signal processing, and telecommunication hardware.",
        "total_seats": 60,
        "status": "Active"
    },
    {
        "name": "Mechanical Engineering",
        "code": "MECH",
        "hod_name": "Dr. V. K. Patil",
        "hod_email": "hod.mech@zeal.edu.in",
        "description": "Thermodynamics, robotics automation, CAD/CAM drafting, mechatronics, and manufacturing systems.",
        "total_seats": 60,
        "status": "Active"
    },
    {
        "name": "Civil Engineering",
        "code": "CIVIL",
        "hod_name": "Prof. G. B. Pawar",
        "hod_email": "hod.civil@zeal.edu.in",
        "description": "Structural engineering, geotechnical surveying, smart city planning, and sustainable construction.",
        "total_seats": 60,
        "status": "Active"
    },
    {
        "name": "Electrical Engineering",
        "code": "ELEC",
        "hod_name": "Dr. S. M. Gaikwad",
        "hod_email": "hod.elec@zeal.edu.in",
        "description": "Power systems, renewable smart grids, industrial motor control, and electronic energy devices.",
        "total_seats": 60,
        "status": "Active"
    }
]

class DepartmentService:

    @staticmethod
    def initialize_departments():
        """Ensure standard departments are seeded into the database table"""
        for item in DEFAULT_DEPARTMENTS:
            existing = Department.query.filter(
                db.or_(Department.name == item["name"], Department.code == item["code"])
            ).first()
            if not existing:
                dept = Department(
                    name=item["name"],
                    code=item["code"],
                    hod_name=item["hod_name"],
                    hod_email=item["hod_email"],
                    description=item["description"],
                    total_seats=item["total_seats"],
                    status=item["status"]
                )
                db.session.add(dept)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    @staticmethod
    def get_all_departments(search="", status=""):
        DepartmentService.initialize_departments()
        query = Department.query

        if search:
            sq = search.strip()
            query = query.filter(
                db.or_(
                    Department.name.ilike(f"%{sq}%"),
                    Department.code.ilike(f"%{sq}%"),
                    Department.hod_name.ilike(f"%{sq}%")
                )
            )

        if status:
            query = query.filter(Department.status == status)

        departments = query.order_by(Department.id.asc()).all()

        total_depts = len(departments)
        active_depts = sum(1 for d in departments if d.status == "Active")
        total_students_across = Student.query.count()

        result = []
        for d in departments:
            d_dict = d.to_dict()
            student_count = Student.query.filter(Student.department == d.name).count()
            d_dict["student_count"] = student_count
            d_dict["course_count"] = 1  # Standard B.Tech degree program per department
            d_dict["occupancy_rate"] = round((student_count / d.total_seats * 100), 1) if d.total_seats > 0 else 0.0
            result.append(d_dict)

        return {
            "summary": {
                "total_departments": total_depts,
                "active_departments": active_depts,
                "total_students": total_students_across,
                "total_courses": total_depts
            },
            "departments": result
        }

    @staticmethod
    def get_department_by_id(dept_id):
        dept = Department.query.get(dept_id)
        if not dept:
            return None
        
        d_dict = dept.to_dict()
        student_count = Student.query.filter(Student.department == dept.name).count()
        enrolled_count = Student.query.filter(Student.department == dept.name, db.or_(Student.status == "Enrolled", Student.is_enrolled == True)).count()
        d_dict["student_count"] = student_count
        d_dict["enrolled_count"] = enrolled_count
        d_dict["course_count"] = 1
        d_dict["occupancy_rate"] = round((student_count / dept.total_seats * 100), 1) if dept.total_seats > 0 else 0.0
        return d_dict

    @staticmethod
    def create_department(data):
        name = sanitize_input(data.get("name", ""))
        code = sanitize_input(data.get("code", "")).upper()
        hod_name = sanitize_input(data.get("hod_name", "")) or "To Be Appointed"
        hod_email = sanitize_input(data.get("hod_email", "")).lower()
        description = sanitize_input(data.get("description", ""))
        status = sanitize_input(data.get("status", "Active"))
        
        try:
            total_seats = int(data.get("total_seats", 60))
        except (ValueError, TypeError):
            total_seats = 60

        if not name or not code:
            raise ValueError("Department Name and Code are required.")

        existing = Department.query.filter(
            db.or_(Department.name == name, Department.code == code)
        ).first()
        if existing:
            raise ValueError(f"A department with name '{name}' or code '{code}' already exists.")

        new_dept = Department(
            name=name,
            code=code,
            hod_name=hod_name,
            hod_email=hod_email,
            description=description,
            total_seats=total_seats,
            status=status
        )

        db.session.add(new_dept)
        
        # Also sync to SeatMatrix table if not present
        if not SeatMatrix.query.filter_by(department=name).first():
            sm = SeatMatrix(department=name, total_seats=total_seats, filled_seats=0)
            db.session.add(sm)

        db.session.commit()
        return new_dept

    @staticmethod
    def update_department(dept_id, data):
        dept = Department.query.get(dept_id)
        if not dept:
            return None

        if "name" in data and data["name"]:
            name = sanitize_input(data["name"])
            existing = Department.query.filter(Department.name == name, Department.id != dept_id).first()
            if existing:
                raise ValueError(f"Another department already uses the name '{name}'.")
            
            # If department name changed, update connected student & seat matrix records
            old_name = dept.name
            dept.name = name

            if old_name != name:
                Student.query.filter(Student.department == old_name).update({"department": name})
                SeatMatrix.query.filter(SeatMatrix.department == old_name).update({"department": name})

        if "code" in data and data["code"]:
            code = sanitize_input(data["code"]).upper()
            existing = Department.query.filter(Department.code == code, Department.id != dept_id).first()
            if existing:
                raise ValueError(f"Another department already uses code '{code}'.")
            dept.code = code

        if "hod_name" in data:
            dept.hod_name = sanitize_input(data["hod_name"]) or "To Be Appointed"
        if "hod_email" in data:
            dept.hod_email = sanitize_input(data["hod_email"]).lower()
        if "description" in data:
            dept.description = sanitize_input(data["description"])
        if "status" in data:
            dept.status = sanitize_input(data["status"])
        if "total_seats" in data:
            try:
                dept.total_seats = int(data["total_seats"])
            except (ValueError, TypeError):
                pass

        db.session.commit()
        return dept

    @staticmethod
    def delete_department(dept_id):
        dept = Department.query.get(dept_id)
        if not dept:
            return False, "Department not found."

        # Check for dependent student records
        student_count = Student.query.filter(Student.department == dept.name).count()
        if student_count > 0:
            return False, f"Cannot delete department '{dept.name}' because {student_count} student record(s) are attached to it. Please reassign students before deleting."

        db.session.delete(dept)
        
        # Also clean up matching seat matrix entry
        sm = SeatMatrix.query.filter_by(department=dept.name).first()
        if sm:
            db.session.delete(sm)

        db.session.commit()
        return True, f"Department '{dept.name}' deleted successfully."
