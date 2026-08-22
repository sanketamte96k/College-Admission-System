import os
import re
from datetime import datetime
from models import db, SystemSetting, AcademicYear, Admin, Student, Department, Payment, Notice

class SettingService:

    @staticmethod
    def seed_default_settings():
        """Seed default system configuration settings and academic years if database is empty."""
        try:
            default_settings = [
                # General Category
                {"key": "app_name", "value": "Zeal College ERP", "group": "general", "description": "Application Title"},
                {"key": "institution_name", "value": "Zeal College of Engineering and Research", "group": "general", "description": "Official Institution Name"},
                {"key": "institution_email", "value": "contact@zeal.edu.in", "group": "general", "description": "Official Institution Email"},
                {"key": "institution_phone", "value": "+91 20 6720 6000", "group": "general", "description": "Main Contact Phone"},
                {"key": "institution_address", "value": "Survey No. 39, Narhe, Haveli, Pune, Maharashtra", "group": "general", "description": "Physical Address"},
                {"key": "timezone", "value": "Asia/Kolkata (IST)", "group": "general", "description": "System Timezone"},
                {"key": "date_format", "value": "YYYY-MM-DD", "group": "general", "description": "Display Date Format"},
                {"key": "currency", "value": "INR (₹)", "group": "general", "description": "Default Currency"},

                # College Information Category
                {"key": "college_code", "value": "ZEAL-PUNE-6155", "group": "college", "description": "DTE College Code"},
                {"key": "city", "value": "Pune", "group": "college", "description": "City"},
                {"key": "state", "value": "Maharashtra", "group": "college", "description": "State"},
                {"key": "pincode", "value": "411041", "group": "college", "description": "Pincode"},
                {"key": "website", "value": "https://zeal.edu.in", "group": "college", "description": "Official Website URL"},
                {"key": "principal_name", "value": "Dr. A. B. Tech", "group": "college", "description": "Principal Name"},

                # Academic Configuration Category
                {"key": "current_academic_year", "value": "2026-27", "group": "academic", "description": "Active Campus Academic Year"},
                {"key": "current_semester", "value": "Semester 1", "group": "academic", "description": "Active Semester"},
                {"key": "default_pagination_limit", "value": "20", "group": "academic", "description": "Default Records Per Page"},

                # Notifications Category
                {"key": "notify_email", "value": "true", "group": "notifications", "description": "Email Notification Switch"},
                {"key": "notify_notices", "value": "true", "group": "notifications", "description": "Notice Circular Alerts"},
                {"key": "notify_admissions", "value": "true", "group": "notifications", "description": "Admission System Alerts"},
                {"key": "notify_fees", "value": "true", "group": "notifications", "description": "Fee Payment Alerts"},
                {"key": "notify_attendance", "value": "true", "group": "notifications", "description": "Attendance Percentage Alerts"},
                {"key": "notify_exams", "value": "true", "group": "notifications", "description": "Examination Timetable Alerts"},

                # System Preferences Category
                {"key": "system_theme", "value": "light", "group": "system", "description": "ERP Interface Theme"},
                {"key": "cache_ttl_minutes", "value": "15", "group": "system", "description": "API Cache Refresh Interval"}
            ]

            for s in default_settings:
                existing = SystemSetting.query.filter_by(key=s["key"]).first()
                if not existing:
                    db.session.add(SystemSetting(
                        key=s["key"],
                        value=s["value"],
                        group=s["group"],
                        description=s["description"]
                    ))

            # Seed Default Academic Years
            default_years = [
                {"year_name": "2025-26", "is_active": False, "status": "Closed"},
                {"year_name": "2026-27", "is_active": True, "status": "Active"},
                {"year_name": "2027-28", "is_active": False, "status": "Upcoming"}
            ]

            for ay in default_years:
                existing_yr = AcademicYear.query.filter_by(year_name=ay["year_name"]).first()
                if not existing_yr:
                    db.session.add(AcademicYear(
                        year_name=ay["year_name"],
                        is_active=ay["is_active"],
                        status=ay["status"]
                    ))

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"SettingService.seed_default_settings note: {e}")

    @staticmethod
    def get_all_settings():
        """Retrieve all system settings structured by group."""
        settings = SystemSetting.query.all()
        result = {}
        flat_map = {}

        for s in settings:
            flat_map[s.key] = s.value
            if s.group not in result:
                result[s.group] = {}
            result[s.group][s.key] = s.value

        return {
            "grouped": result,
            "flat": flat_map
        }

    @staticmethod
    def update_settings_group(group_name, settings_dict):
        """Update a group of system settings after validating format."""
        if not isinstance(settings_dict, dict):
            raise ValueError("Settings data must be a key-value dictionary.")

        # Validation rules
        email = settings_dict.get("institution_email")
        if email and not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            raise ValueError("Invalid email format.")

        pincode = settings_dict.get("pincode")
        if pincode and not re.match(r"^\d{6}$", str(pincode).strip()):
            raise ValueError("Pincode must be a 6-digit Indian postal code.")

        phone = settings_dict.get("institution_phone")
        if phone and len(re.sub(r"\D", "", str(phone))) < 7:
            raise ValueError("Phone number must contain at least 7 digits.")

        updated_keys = []
        for key, val in settings_dict.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                setting = SystemSetting(key=key, group=group_name, value=str(val))
                db.session.add(setting)
            else:
                setting.value = str(val)
                setting.updated_at = datetime.utcnow()
            updated_keys.append(key)

        db.session.commit()

        # If current_academic_year was updated, sync active AcademicYear entry
        if "current_academic_year" in settings_dict:
            new_ay = settings_dict["current_academic_year"].strip()
            ay_obj = AcademicYear.query.filter_by(year_name=new_ay).first()
            if ay_obj:
                AcademicYear.query.update({"is_active": False})
                ay_obj.is_active = True
                ay_obj.status = "Active"
                db.session.commit()

        return SettingService.get_all_settings()

    @staticmethod
    def get_academic_years():
        """Retrieve all registered academic years."""
        years = AcademicYear.query.order_by(AcademicYear.year_name.desc()).all()
        return [y.to_dict() for y in years]

    @staticmethod
    def create_academic_year(year_name, start_date=None, end_date=None):
        """Create a new academic year entry."""
        year_name = year_name.strip()
        if not year_name:
            raise ValueError("Academic year name is required.")

        existing = AcademicYear.query.filter_by(year_name=year_name).first()
        if existing:
            raise ValueError(f"Academic year '{year_name}' already exists.")

        s_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        e_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        ay = AcademicYear(
            year_name=year_name,
            is_active=False,
            status="Upcoming",
            start_date=s_date,
            end_date=e_date
        )
        db.session.add(ay)
        db.session.commit()

        return ay.to_dict()

    @staticmethod
    def set_active_academic_year(year_id):
        """Set a single academic year as active campus-wide."""
        ay = AcademicYear.query.get(year_id)
        if not ay:
            raise ValueError("Academic year not found.")

        # Deactivate all other academic years
        AcademicYear.query.update({"is_active": False})

        ay.is_active = True
        ay.status = "Active"

        # Sync in system_settings
        setting = SystemSetting.query.filter_by(key="current_academic_year").first()
        if setting:
            setting.value = ay.year_name
            setting.updated_at = datetime.utcnow()
        else:
            db.session.add(SystemSetting(key="current_academic_year", value=ay.year_name, group="academic"))

        db.session.commit()
        return ay.to_dict()

    @staticmethod
    def close_academic_year(year_id):
        """Close an academic year safely."""
        ay = AcademicYear.query.get(year_id)
        if not ay:
            raise ValueError("Academic year not found.")

        if ay.is_active:
            raise ValueError("Cannot close the currently active academic year. Please activate another academic year first.")

        ay.status = "Closed"
        ay.is_active = False
        db.session.commit()
        return ay.to_dict()

    @staticmethod
    def update_user_profile(admin_id, data):
        """Update logged-in admin user profile safely."""
        admin = Admin.query.get(admin_id)
        if not admin:
            raise ValueError("User not found.")

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()

        if username and username != admin.username:
            existing_user = Admin.query.filter(Admin.username == username, Admin.id != admin_id).first()
            if existing_user:
                raise ValueError("Username is already taken.")
            admin.username = username

        if email and email != admin.email:
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                raise ValueError("Invalid email format.")
            existing_email = Admin.query.filter(Admin.email == email, Admin.id != admin_id).first()
            if existing_email:
                raise ValueError("Email is already registered to another account.")
            admin.email = email

        db.session.commit()
        return admin.to_dict()

    @staticmethod
    def change_user_password(admin_id, current_password, new_password, confirm_password):
        """Change user password with strict verification."""
        admin = Admin.query.get(admin_id)
        if not admin:
            raise ValueError("User not found.")

        if not current_password or not admin.check_password(current_password):
            raise ValueError("Current password is incorrect.")

        if not new_password or len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters long.")

        if new_password != confirm_password:
            raise ValueError("New password and confirmation do not match.")

        admin.set_password(new_password)
        db.session.commit()
        return {"message": "Password changed successfully."}

    @staticmethod
    def get_maintenance_status():
        """Retrieve system maintenance, database info and application status without exposing secrets."""
        db_type = "MySQL (Production)" if "mysql" in str(db.engine.url) else "SQLite (Local/Embedded)"
        
        return {
            "application_status": "Healthy / Operational",
            "database_engine": db_type,
            "database_connected": True,
            "total_students": Student.query.count(),
            "total_departments": Department.query.count(),
            "total_notices": Notice.query.count(),
            "total_payments": Payment.query.count(),
            "server_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "environment_mode": os.getenv("FLASK_ENV", "dev")
        }
