from datetime import datetime
from models import db, Notice
from utils import sanitize_input

class NoticeService:

    ALLOWED_CATEGORIES = [
        "General", "Academic", "Examination", "Admission",
        "Fees & Payments", "Attendance", "Library", "Transport",
        "Events", "Placement", "Emergency"
    ]

    ALLOWED_PRIORITIES = ["Normal", "Important", "Urgent"]
    ALLOWED_STATUSES = ["Draft", "Published", "Scheduled", "Expired", "Archived"]
    ALLOWED_AUDIENCES = [
        "Everyone", "Students", "Faculty", "Staff",
        "Specific Department", "Specific Course", "Specific Year"
    ]

    # =========================================================
    # GET ALL NOTICES (ADMIN / MANAGEMENT LISTING WITH FILTERS)
    # =========================================================
    @staticmethod
    def get_all_notices(
        page=1,
        limit=20,
        search="",
        category="",
        priority="",
        status="",
        audience="",
        department="",
        academic_year="",
        is_pinned=None
    ):
        now = datetime.utcnow()
        query = Notice.query

        if search:
            sq = search.strip()
            query = query.filter(
                db.or_(
                    Notice.title.ilike(f"%{sq}%"),
                    Notice.content.ilike(f"%{sq}%"),
                    Notice.category.ilike(f"%{sq}%")
                )
            )

        if category:
            query = query.filter(Notice.category == category)

        if priority:
            query = query.filter(Notice.priority == priority)

        if audience:
            query = query.filter(Notice.audience == audience)

        if department:
            query = query.filter(Notice.department == department)

        if academic_year:
            query = query.filter(Notice.academic_year == academic_year)

        if is_pinned is not None:
            query = query.filter(Notice.is_pinned == is_pinned)

        # Status filtering (accounting for calculated effective status)
        if status:
            if status == "Archived":
                query = query.filter(Notice.status == "Archived")
            elif status == "Draft":
                query = query.filter(Notice.status == "Draft")
            elif status == "Expired":
                query = query.filter(
                    Notice.status != "Archived",
                    Notice.status != "Draft",
                    Notice.expiry_date.isnot(None),
                    Notice.expiry_date <= now
                )
            elif status == "Scheduled":
                query = query.filter(
                    Notice.status != "Archived",
                    Notice.status != "Draft",
                    Notice.publish_date.isnot(None),
                    Notice.publish_date > now,
                    db.or_(Notice.expiry_date.is_(None), Notice.expiry_date > now)
                )
            elif status == "Published":
                query = query.filter(
                    Notice.status == "Published",
                    db.or_(Notice.publish_date.is_(None), Notice.publish_date <= now),
                    db.or_(Notice.expiry_date.is_(None), Notice.expiry_date > now)
                )

        # Primary Sort: Pinned notices first, then newest first
        query = query.order_by(Notice.is_pinned.desc(), Notice.created_at.desc())

        total = query.count()
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        notices = [n.to_dict() for n in pagination.items]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pagination.pages,
            "notices": notices
        }

    # =========================================================
    # GET ACTIVE PUBLIC / STUDENT NOTICES
    # =========================================================
    @staticmethod
    def get_active_notices(audience=None, department=None, course=None, academic_year=None, limit=10):
        now = datetime.utcnow()
        query = Notice.query.filter(
            Notice.status == "Published",
            db.or_(Notice.publish_date.is_(None), Notice.publish_date <= now),
            db.or_(Notice.expiry_date.is_(None), Notice.expiry_date > now)
        )

        if audience:
            query = query.filter(db.or_(Notice.audience == "Everyone", Notice.audience == audience))

        if department:
            query = query.filter(db.or_(Notice.department.is_(None), Notice.department == "", Notice.department == department))

        if course:
            query = query.filter(db.or_(Notice.course.is_(None), Notice.course == "", Notice.course == course))

        if academic_year:
            query = query.filter(db.or_(Notice.academic_year.is_(None), Notice.academic_year == "", Notice.academic_year == academic_year))

        query = query.order_by(Notice.is_pinned.desc(), Notice.created_at.desc())
        notices = query.limit(limit).all()
        return [n.to_dict() for n in notices]

    # =========================================================
    # GET SINGLE NOTICE
    # =========================================================
    @staticmethod
    def get_notice_by_id(notice_id):
        return Notice.query.get(notice_id)

    # =========================================================
    # CREATE NOTICE
    # =========================================================
    @staticmethod
    def create_notice(data, created_by="Admin"):
        title = sanitize_input(data.get("title", "")).strip()
        content = sanitize_input(data.get("content", "")).strip()
        if not title:
            raise ValueError("Notice title is required.")
        if not content:
            raise ValueError("Notice content is required.")

        category = data.get("category", "General")
        priority = data.get("priority", "Normal")
        status = data.get("status", "Draft")
        audience = data.get("audience", "Everyone")

        department = data.get("department", "").strip() or None
        course = data.get("course", "").strip() or None
        academic_year = data.get("academic_year", "").strip() or None
        semester = data.get("semester", "").strip() or None

        publish_date = NoticeService._parse_datetime(data.get("publish_date"))
        expiry_date = NoticeService._parse_datetime(data.get("expiry_date"))

        if publish_date and expiry_date and expiry_date < publish_date:
            raise ValueError("Expiry date cannot be before publish date.")

        is_pinned = bool(data.get("is_pinned", False))

        notice = Notice(
            title=title,
            content=content,
            category=category,
            priority=priority,
            status=status,
            audience=audience,
            department=department,
            course=course,
            academic_year=academic_year,
            semester=semester,
            publish_date=publish_date,
            expiry_date=expiry_date,
            is_pinned=is_pinned,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(notice)
        db.session.commit()
        return notice

    # =========================================================
    # UPDATE NOTICE
    # =========================================================
    @staticmethod
    def update_notice(notice_id, data):
        notice = Notice.query.get(notice_id)
        if not notice:
            raise ValueError(f"Notice with ID {notice_id} not found.")

        if "title" in data:
            title = sanitize_input(data["title"]).strip()
            if not title:
                raise ValueError("Notice title cannot be empty.")
            notice.title = title

        if "content" in data:
            content = sanitize_input(data["content"]).strip()
            if not content:
                raise ValueError("Notice content cannot be empty.")
            notice.content = content

        if "category" in data:
            notice.category = data["category"]

        if "priority" in data:
            notice.priority = data["priority"]

        if "status" in data:
            notice.status = data["status"]

        if "audience" in data:
            notice.audience = data["audience"]

        if "department" in data:
            notice.department = data["department"].strip() or None

        if "course" in data:
            notice.course = data["course"].strip() or None

        if "academic_year" in data:
            notice.academic_year = data["academic_year"].strip() or None

        if "semester" in data:
            notice.semester = data["semester"].strip() or None

        if "publish_date" in data:
            notice.publish_date = NoticeService._parse_datetime(data.get("publish_date"))

        if "expiry_date" in data:
            notice.expiry_date = NoticeService._parse_datetime(data.get("expiry_date"))

        if notice.publish_date and notice.expiry_date and notice.expiry_date < notice.publish_date:
            raise ValueError("Expiry date cannot be before publish date.")

        if "is_pinned" in data:
            notice.is_pinned = bool(data["is_pinned"])

        notice.updated_at = datetime.utcnow()
        db.session.commit()
        return notice

    # =========================================================
    # DELETE NOTICE
    # =========================================================
    @staticmethod
    def delete_notice(notice_id):
        notice = Notice.query.get(notice_id)
        if not notice:
            raise ValueError(f"Notice with ID {notice_id} not found.")

        db.session.delete(notice)
        db.session.commit()
        return True

    # =========================================================
    # PUBLISH NOTICE
    # =========================================================
    @staticmethod
    def publish_notice(notice_id):
        notice = Notice.query.get(notice_id)
        if not notice:
            raise ValueError(f"Notice with ID {notice_id} not found.")

        notice.status = "Published"
        if not notice.publish_date:
            notice.publish_date = datetime.utcnow()
        notice.updated_at = datetime.utcnow()
        db.session.commit()
        return notice

    # =========================================================
    # ARCHIVE NOTICE
    # =========================================================
    @staticmethod
    def archive_notice(notice_id):
        notice = Notice.query.get(notice_id)
        if not notice:
            raise ValueError(f"Notice with ID {notice_id} not found.")

        notice.status = "Archived"
        notice.updated_at = datetime.utcnow()
        db.session.commit()
        return notice

    # =========================================================
    # TOGGLE PIN NOTICE
    # =========================================================
    @staticmethod
    def toggle_pin_notice(notice_id):
        notice = Notice.query.get(notice_id)
        if not notice:
            raise ValueError(f"Notice with ID {notice_id} not found.")

        notice.is_pinned = not notice.is_pinned
        notice.updated_at = datetime.utcnow()
        db.session.commit()
        return notice

    # =========================================================
    # GET NOTICE KPI STATS
    # =========================================================
    @staticmethod
    def get_notice_kpi_stats():
        now = datetime.utcnow()
        all_notices = Notice.query.all()

        total = len(all_notices)
        published = 0
        drafts = 0
        scheduled = 0
        expired = 0
        archived = 0
        pinned = 0
        urgent = 0

        for n in all_notices:
            if n.is_pinned:
                pinned += 1
            if n.priority == "Urgent":
                urgent += 1

            eff = n.effective_status
            if eff == "Published":
                published += 1
            elif eff == "Draft":
                drafts += 1
            elif eff == "Scheduled":
                scheduled += 1
            elif eff == "Expired":
                expired += 1
            elif eff == "Archived":
                archived += 1

        return {
            "total_notices": total,
            "published": published,
            "drafts": drafts,
            "scheduled": scheduled,
            "expired": expired,
            "archived": archived,
            "pinned": pinned,
            "urgent": urgent
        }

    # =========================================================
    # SEED DEFAULT CAMPUS NOTICES
    # =========================================================
    @staticmethod
    def seed_default_notices():
        if Notice.query.count() == 0:
            samples = [
                {
                    "title": "Official Academic Calendar & Commencement of 2026-27 Session",
                    "content": "Zeal College of Engineering & Research announces the official commencement of classes for all B.Tech programs for Academic Year 2026-27 starting from September 1st, 2026. All enrolled candidates must submit remaining admission documents and register for semester courses.",
                    "category": "Academic",
                    "priority": "Important",
                    "status": "Published",
                    "audience": "Everyone",
                    "department": "",
                    "is_pinned": True,
                    "created_by": "Principal Office"
                },
                {
                    "title": "Semester Examination Hall Ticket & Fee Clearance Circular",
                    "content": "All engineering students are hereby informed that semester hall tickets for upcoming mid-term examinations will be issued subject to clearing outstanding tuition fees and library books clearance.",
                    "category": "Examination",
                    "priority": "Urgent",
                    "status": "Published",
                    "audience": "Students",
                    "department": "Computer Engineering",
                    "is_pinned": False,
                    "created_by": "Controller of Examinations"
                },
                {
                    "title": "Campus Recruitment Drive - Tata Consultancy Services (TCS Digital)",
                    "content": "Placement Cell presents TCS Digital recruitment drive for final year Computer, IT, and AI & Data Science B.Tech students. Interested eligible candidates with minimum 65% aggregate must register on Training & Placement portal.",
                    "category": "Placement",
                    "priority": "Important",
                    "status": "Published",
                    "audience": "Students",
                    "department": "Computer Engineering",
                    "is_pinned": True,
                    "created_by": "Placement Officer"
                },
                {
                    "title": "Annual State Level Technical & Cultural Fest 'UDAAN 2026'",
                    "content": "Zeal Education Society warmly invites all students and faculty to participate in UDAAN 2026 featuring project exhibitions, hackathons, robotics competitions, and cultural events. Registrations open on official portal.",
                    "category": "Events",
                    "priority": "Normal",
                    "status": "Published",
                    "audience": "Everyone",
                    "department": "",
                    "is_pinned": False,
                    "created_by": "Student Affairs"
                },
                {
                    "title": "Draft Policy on AI & Robotics Research Lab Usage Guidelines",
                    "content": "Draft guidelines for advanced AI server utilization and evening lab access by research scholars and B.Tech project groups. Under review by Academic Advisory Committee.",
                    "category": "General",
                    "priority": "Normal",
                    "status": "Draft",
                    "audience": "Faculty",
                    "department": "Artificial Intelligence & Data Science",
                    "is_pinned": False,
                    "created_by": "Head of AI Department"
                }
            ]

            for data in samples:
                NoticeService.create_notice(data, created_by=data.get("created_by", "Admin"))
            print("Default campus notices seeded successfully.")

    # Helper: Datetime parsing
    @staticmethod
    def _parse_datetime(dt_str):
        if not dt_str:
            return None
        if isinstance(dt_str, datetime):
            return dt_str

        dt_str = dt_str.strip()
        for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                pass
        return None
