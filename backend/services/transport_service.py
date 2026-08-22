import io
from datetime import datetime, date
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from models import db, Student, TransportDriver, TransportRoute, TransportStop, TransportVehicle, TransportAssignment

class TransportService:

    @staticmethod
    def initialize_default_transport():
        """Seed default transport fleet, routes, stops and drivers if database is empty."""
        try:
            if TransportRoute.query.count() == 0:
                # 1. Seed Drivers
                d1 = TransportDriver(name="Ramesh Patil", phone="9822112233", license_number="MH12-2015-001234", status="Active", emergency_contact="9822110000")
                d2 = TransportDriver(name="Suresh Shinde", phone="9822112244", license_number="MH12-2016-005678", status="Active", emergency_contact="9822110001")
                d3 = TransportDriver(name="Ganesh Kadam", phone="9822112255", license_number="MH12-2018-009012", status="Active", emergency_contact="9822110002")
                d4 = TransportDriver(name="Mahesh Pawar", phone="9822112266", license_number="MH12-2019-003456", status="Active", emergency_contact="9822110003")
                db.session.add_all([d1, d2, d3, d4])
                db.session.commit()

                # 2. Seed Routes & Stops
                r1 = TransportRoute(route_name="Route 1 - Swargate Express", route_code="R-01", start_point="Swargate Junction", destination="Zeal College Narhe", distance_km=12.5, estimated_time="35 Mins", status="Active")
                r2 = TransportRoute(route_name="Route 2 - Kothrud Via Karve Nagar", route_code="R-02", start_point="Kothrud Depot", destination="Zeal College Narhe", distance_km=14.0, estimated_time="40 Mins", status="Active")
                r3 = TransportRoute(route_name="Route 3 - Pimpri Chinchwad Route", route_code="R-03", start_point="Bhakti Shakti Pimpri", destination="Zeal College Narhe", distance_km=25.0, estimated_time="60 Mins", status="Active")
                r4 = TransportRoute(route_name="Route 4 - Hadapsar / Katraj Highway", route_code="R-04", start_point="Hadapsar Gadital", destination="Zeal College Narhe", distance_km=18.0, estimated_time="45 Mins", status="Active")
                db.session.add_all([r1, r2, r3, r4])
                db.session.commit()

                # Add Stops for Route 1
                s1_1 = TransportStop(route_id=r1.id, stop_name="Swargate Bus Stand", sequence_number=1, pickup_time="07:30 AM", drop_time="05:30 PM")
                s1_2 = TransportStop(route_id=r1.id, stop_name="Market Yard Corner", sequence_number=2, pickup_time="07:40 AM", drop_time="05:20 PM")
                s1_3 = TransportStop(route_id=r1.id, stop_name="Katraj Bus Depot", sequence_number=3, pickup_time="07:55 AM", drop_time="05:05 PM")
                s1_4 = TransportStop(route_id=r1.id, stop_name="Zeal College Campus", sequence_number=4, pickup_time="08:15 AM", drop_time="04:45 PM")

                # Add Stops for Route 2
                s2_1 = TransportStop(route_id=r2.id, stop_name="Kothrud Stand", sequence_number=1, pickup_time="07:25 AM", drop_time="05:35 PM")
                s2_2 = TransportStop(route_id=r2.id, stop_name="Karve Nagar Chowk", sequence_number=2, pickup_time="07:40 AM", drop_time="05:20 PM")
                s2_3 = TransportStop(route_id=r2.id, stop_name="Warje Flyover", sequence_number=3, pickup_time="07:50 AM", drop_time="05:10 PM")
                s2_4 = TransportStop(route_id=r2.id, stop_name="Zeal College Campus", sequence_number=4, pickup_time="08:10 AM", drop_time="04:50 PM")

                db.session.add_all([s1_1, s1_2, s1_3, s1_4, s2_1, s2_2, s2_3, s2_4])
                db.session.commit()

                # 3. Seed Vehicles
                v1 = TransportVehicle(vehicle_number="MH-12-PQ-1001", registration_number="BUS-REG-1001", vehicle_type="AC Bus", capacity=40, assigned_driver_id=d1.id, assigned_route_id=r1.id, status="Active", insurance_expiry=date(2027, 3, 31), fitness_expiry=date(2027, 5, 30), description="40 Seater Luxury AC Bus")
                v2 = TransportVehicle(vehicle_number="MH-12-PQ-1002", registration_number="BUS-REG-1002", vehicle_type="Non-AC Bus", capacity=45, assigned_driver_id=d2.id, assigned_route_id=r2.id, status="Active", insurance_expiry=date(2027, 4, 30), fitness_expiry=date(2027, 6, 30), description="45 Seater Standard Bus")
                v3 = TransportVehicle(vehicle_number="MH-12-PQ-1003", registration_number="BUS-REG-1003", vehicle_type="AC Bus", capacity=35, assigned_driver_id=d3.id, assigned_route_id=r3.id, status="Active", insurance_expiry=date(2027, 1, 15), fitness_expiry=date(2027, 2, 28), description="35 Seater Mini Bus")
                v4 = TransportVehicle(vehicle_number="MH-12-PQ-1004", registration_number="BUS-REG-1004", vehicle_type="Non-AC Bus", capacity=40, assigned_driver_id=d4.id, assigned_route_id=r4.id, status="Active", insurance_expiry=date(2026, 12, 31), fitness_expiry=date(2027, 1, 31), description="40 Seater Standard Bus")
                db.session.add_all([v1, v2, v3, v4])
                db.session.commit()

        except Exception as e:
            db.session.rollback()

    @staticmethod
    def get_dashboard_summary():
        TransportService.initialize_default_transport()

        total_vehicles = TransportVehicle.query.count()
        active_vehicles = TransportVehicle.query.filter_by(status="Active").count()
        total_routes = TransportRoute.query.count()
        total_drivers = TransportDriver.query.count()

        active_assignments = TransportAssignment.query.filter_by(status="Active").all()
        total_transport_students = len(active_assignments)

        total_capacity = sum(v.capacity for v in TransportVehicle.query.filter_by(status="Active").all()) or 160
        available_seats = max(0, total_capacity - total_transport_students)

        pending_fees = sum(a.fee_amount for a in active_assignments if a.fee_status in ["Pending", "Partial"])

        return {
            "total_vehicles": total_vehicles,
            "active_vehicles": active_vehicles,
            "total_routes": total_routes,
            "total_drivers": total_drivers,
            "total_transport_students": total_transport_students,
            "total_capacity": total_capacity,
            "available_seats": available_seats,
            "pending_fees": round(pending_fees, 2)
        }

    # =========================================================
    # VEHICLE MANAGEMENT
    # =========================================================
    @staticmethod
    def get_vehicles(status="", search=""):
        query = TransportVehicle.query

        if status and status.strip() and status.lower() != "all":
            query = query.filter(TransportVehicle.status == status.strip())

        if search and search.strip():
            sq = f"%{search.strip()}%"
            query = query.filter(
                db.or_(
                    TransportVehicle.vehicle_number.ilike(sq),
                    TransportVehicle.registration_number.ilike(sq),
                    TransportVehicle.vehicle_type.ilike(sq)
                )
            )

        vehicles = query.order_by(TransportVehicle.id.asc()).all()
        return [v.to_dict() for v in vehicles]

    @staticmethod
    def add_vehicle(data):
        v_num = (data.get("vehicle_number") or "").strip().upper()
        reg_num = (data.get("registration_number") or "").strip().upper()

        if not v_num or not reg_num:
            return False, "Vehicle Number and Registration Number are required.", None

        dup = TransportVehicle.query.filter(
            db.or_(
                TransportVehicle.vehicle_number == v_num,
                TransportVehicle.registration_number == reg_num
            )
        ).first()

        if dup:
            return False, f"Vehicle with number '{v_num}' or registration '{reg_num}' already exists.", None

        capacity = int(data.get("capacity") or 40)
        driver_id = data.get("assigned_driver_id")
        route_id = data.get("assigned_route_id")

        ins_exp = None
        if data.get("insurance_expiry"):
            try:
                ins_exp = datetime.strptime(data.get("insurance_expiry").strip(), "%Y-%m-%d").date()
            except Exception:
                pass

        fit_exp = None
        if data.get("fitness_expiry"):
            try:
                fit_exp = datetime.strptime(data.get("fitness_expiry").strip(), "%Y-%m-%d").date()
            except Exception:
                pass

        veh = TransportVehicle(
            vehicle_number=v_num,
            registration_number=reg_num,
            vehicle_type=data.get("vehicle_type", "Bus").strip(),
            capacity=capacity,
            assigned_driver_id=int(driver_id) if driver_id else None,
            assigned_route_id=int(route_id) if route_id else None,
            status=data.get("status", "Active").strip(),
            insurance_expiry=ins_exp,
            fitness_expiry=fit_exp,
            description=data.get("description", "").strip()
        )

        try:
            db.session.add(veh)
            db.session.commit()
            return True, "Vehicle registered successfully.", veh.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to register vehicle: {str(e)}", None

    @staticmethod
    def update_vehicle(vehicle_id, data):
        veh = TransportVehicle.query.get(vehicle_id)
        if not veh:
            return False, "Vehicle record not found.", None

        if data.get("vehicle_number"):
            v_num = data.get("vehicle_number").strip().upper()
            dup = TransportVehicle.query.filter(TransportVehicle.vehicle_number == v_num, TransportVehicle.id != vehicle_id).first()
            if dup:
                return False, f"Vehicle number '{v_num}' is already in use.", None
            veh.vehicle_number = v_num

        if data.get("registration_number"):
            reg_num = data.get("registration_number").strip().upper()
            dup = TransportVehicle.query.filter(TransportVehicle.registration_number == reg_num, TransportVehicle.id != vehicle_id).first()
            if dup:
                return False, f"Registration number '{reg_num}' is already in use.", None
            veh.registration_number = reg_num

        if "vehicle_type" in data:
            veh.vehicle_type = data["vehicle_type"].strip()

        if "capacity" in data and data["capacity"]:
            veh.capacity = int(data["capacity"])

        if "assigned_driver_id" in data:
            veh.assigned_driver_id = int(data["assigned_driver_id"]) if data["assigned_driver_id"] else None

        if "assigned_route_id" in data:
            veh.assigned_route_id = int(data["assigned_route_id"]) if data["assigned_route_id"] else None

        if "status" in data:
            veh.status = data["status"].strip()

        if "description" in data:
            veh.description = data["description"].strip()

        try:
            db.session.commit()
            return True, "Vehicle updated successfully.", veh.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to update vehicle: {str(e)}", None

    @staticmethod
    def delete_vehicle(vehicle_id):
        veh = TransportVehicle.query.get(vehicle_id)
        if not veh:
            return False, "Vehicle not found."

        active_tx = TransportAssignment.query.filter_by(vehicle_id=vehicle_id, status="Active").first()
        if active_tx:
            return False, f"Cannot delete vehicle '{veh.vehicle_number}' because active student assignments exist."

        try:
            db.session.delete(veh)
            db.session.commit()
            return True, "Vehicle deleted successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to delete vehicle: {str(e)}"

    # =========================================================
    # ROUTE MANAGEMENT
    # =========================================================
    @staticmethod
    def get_routes(status="", search=""):
        query = TransportRoute.query

        if status and status.strip() and status.lower() != "all":
            query = query.filter(TransportRoute.status == status.strip())

        if search and search.strip():
            sq = f"%{search.strip()}%"
            query = query.filter(
                db.or_(
                    TransportRoute.route_name.ilike(sq),
                    TransportRoute.route_code.ilike(sq)
                )
            )

        routes = query.order_by(TransportRoute.id.asc()).all()
        return [r.to_dict() for r in routes]

    @staticmethod
    def add_route(data):
        r_name = (data.get("route_name") or "").strip()
        r_code = (data.get("route_code") or "").strip().upper()

        if not r_name or not r_code:
            return False, "Route Name and Route Code are required.", None

        dup = TransportRoute.query.filter_by(route_code=r_code).first()
        if dup:
            return False, f"Route code '{r_code}' already exists.", None

        r = TransportRoute(
            route_name=r_name,
            route_code=r_code,
            start_point=data.get("start_point", "College Campus").strip(),
            destination=data.get("destination", "College Campus").strip(),
            distance_km=float(data.get("distance_km") or 15.0),
            estimated_time=data.get("estimated_time", "45 Mins").strip(),
            status=data.get("status", "Active").strip()
        )

        try:
            db.session.add(r)
            db.session.commit()
            return True, "Route created successfully.", r.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to create route: {str(e)}", None

    @staticmethod
    def update_route(route_id, data):
        r = TransportRoute.query.get(route_id)
        if not r:
            return False, "Route record not found.", None

        if "route_name" in data and data["route_name"]:
            r.route_name = data["route_name"].strip()

        if "route_code" in data and data["route_code"]:
            r_code = data["route_code"].strip().upper()
            dup = TransportRoute.query.filter(TransportRoute.route_code == r_code, TransportRoute.id != route_id).first()
            if dup:
                return False, f"Route code '{r_code}' is already in use.", None
            r.route_code = r_code

        if "start_point" in data:
            r.start_point = data["start_point"].strip()

        if "destination" in data:
            r.destination = data["destination"].strip()

        if "distance_km" in data and data["distance_km"]:
            r.distance_km = float(data["distance_km"])

        if "estimated_time" in data:
            r.estimated_time = data["estimated_time"].strip()

        if "status" in data:
            r.status = data["status"].strip()

        try:
            db.session.commit()
            return True, "Route updated successfully.", r.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to update route: {str(e)}", None

    @staticmethod
    def delete_route(route_id):
        r = TransportRoute.query.get(route_id)
        if not r:
            return False, "Route not found."

        active_tx = TransportAssignment.query.filter_by(route_id=route_id, status="Active").first()
        if active_tx:
            return False, f"Cannot delete route '{r.route_name}' because active student transport passes exist."

        try:
            db.session.delete(r)
            db.session.commit()
            return True, "Route deleted successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to delete route: {str(e)}"

    # =========================================================
    # STOP MANAGEMENT
    # =========================================================
    @staticmethod
    def add_stop(data):
        route_id = data.get("route_id")
        stop_name = (data.get("stop_name") or "").strip()

        if not route_id or not stop_name:
            return False, "Route ID and Stop Name are required.", None

        route = TransportRoute.query.get(route_id)
        if not route:
            return False, "Selected route does not exist.", None

        seq = int(data.get("sequence_number") or (len(route.stops) + 1))

        stop = TransportStop(
            route_id=int(route_id),
            stop_name=stop_name,
            location=data.get("location", stop_name).strip(),
            sequence_number=seq,
            pickup_time=data.get("pickup_time", "07:30 AM").strip(),
            drop_time=data.get("drop_time", "05:30 PM").strip(),
            status=data.get("status", "Active").strip()
        )

        try:
            db.session.add(stop)
            db.session.commit()
            return True, "Bus stop added successfully.", stop.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to add stop: {str(e)}", None

    @staticmethod
    def delete_stop(stop_id):
        stop = TransportStop.query.get(stop_id)
        if not stop:
            return False, "Bus stop not found."

        active_tx = TransportAssignment.query.filter_by(stop_id=stop_id, status="Active").first()
        if active_tx:
            return False, f"Cannot delete stop '{stop.stop_name}' because active student assignments are linked to it."

        try:
            db.session.delete(stop)
            db.session.commit()
            return True, "Bus stop deleted successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to delete stop: {str(e)}"

    # =========================================================
    # DRIVER MANAGEMENT
    # =========================================================
    @staticmethod
    def get_drivers(status="", search=""):
        query = TransportDriver.query

        if status and status.strip() and status.lower() != "all":
            query = query.filter(TransportDriver.status == status.strip())

        if search and search.strip():
            sq = f"%{search.strip()}%"
            query = query.filter(
                db.or_(
                    TransportDriver.name.ilike(sq),
                    TransportDriver.phone.ilike(sq),
                    TransportDriver.license_number.ilike(sq)
                )
            )

        drivers = query.order_by(TransportDriver.id.asc()).all()
        return [d.to_dict() for d in drivers]

    @staticmethod
    def add_driver(data):
        name = (data.get("name") or "").strip()
        phone = (data.get("phone") or "").strip()
        lic_num = (data.get("license_number") or "").strip().upper()

        if not name or not phone or not lic_num:
            return False, "Driver Name, Phone, and License Number are required.", None

        dup = TransportDriver.query.filter_by(license_number=lic_num).first()
        if dup:
            return False, f"Driver with license number '{lic_num}' already exists.", None

        lic_exp = None
        if data.get("license_expiry"):
            try:
                lic_exp = datetime.strptime(data.get("license_expiry").strip(), "%Y-%m-%d").date()
            except Exception:
                pass

        d = TransportDriver(
            name=name,
            phone=phone,
            license_number=lic_num,
            license_expiry=lic_exp,
            status=data.get("status", "Active").strip(),
            emergency_contact=data.get("emergency_contact", "").strip()
        )

        try:
            db.session.add(d)
            db.session.commit()
            return True, "Driver registered successfully.", d.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to register driver: {str(e)}", None

    @staticmethod
    def delete_driver(driver_id):
        d = TransportDriver.query.get(driver_id)
        if not d:
            return False, "Driver not found."

        if d.assigned_vehicles:
            return False, f"Cannot delete driver '{d.name}' because vehicle '{d.assigned_vehicles[0].vehicle_number}' is assigned to them."

        try:
            db.session.delete(d)
            db.session.commit()
            return True, "Driver record deleted successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to delete driver: {str(e)}"

    # =========================================================
    # ZPRN VERIFICATION FOR TRANSPORT
    # =========================================================
    @staticmethod
    def verify_student_by_zprn(zprn_input):
        if not zprn_input or not str(zprn_input).strip():
            return False, "Student not found in college records", None

        zprn_clean = str(zprn_input).strip()

        # 1. Direct match on enrollment_number
        student = Student.query.filter(
            db.func.lower(Student.enrollment_number) == zprn_clean.lower()
        ).first()

        # 2. Try integer PK match
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
            return False, f"Student '{student.fullName}' is not an enrolled student of this college.", None

        active_tx = TransportAssignment.query.filter_by(student_id=student.id, status="Active").first()

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
            "already_assigned": bool(active_tx),
            "existing_route": active_tx.route.route_name if (active_tx and active_tx.route) else None,
            "status": "Officially Enrolled"
        }

    # =========================================================
    # STUDENT TRANSPORT ASSIGNMENT & CAPACITY CHECK
    # =========================================================
    @staticmethod
    def assign_student_transport(zprn_or_student_id, route_id, stop_id, vehicle_id=None, fee_amount=15000.0):
        # Resolve student
        success, msg, student_data = TransportService.verify_student_by_zprn(zprn_or_student_id)
        if not success:
            return False, msg, None

        student_id = student_data["student_id"]
        student = Student.query.get(student_id)

        route = TransportRoute.query.get(route_id)
        if not route:
            return False, "Selected transport route does not exist.", None

        stop = TransportStop.query.get(stop_id)
        if not stop or stop.route_id != route.id:
            return False, "Selected bus stop is not valid for this route.", None

        # Auto-assign vehicle if not specified
        if not vehicle_id:
            assigned_veh = TransportVehicle.query.filter_by(assigned_route_id=route.id, status="Active").first()
            if assigned_veh:
                vehicle_id = assigned_veh.id

        vehicle = TransportVehicle.query.get(vehicle_id) if vehicle_id else None

        # VEHICLE CAPACITY CHECK
        if vehicle:
            active_veh_count = TransportAssignment.query.filter_by(vehicle_id=vehicle.id, status="Active").count()
            if active_veh_count >= vehicle.capacity:
                return False, f"Vehicle capacity is full ({active_veh_count}/{vehicle.capacity} seats taken). Cannot assign more students to Vehicle {vehicle.vehicle_number}.", None

        # Check duplicate active pass for same student
        dup_pass = TransportAssignment.query.filter_by(student_id=student.id, status="Active").first()
        if dup_pass:
            return False, f"Student '{student.fullName}' (ZPRN: {student_data['zprn']}) already has an active transport pass for {dup_pass.route.route_name}.", None

        assignment = TransportAssignment(
            student_id=student.id,
            route_id=route.id,
            stop_id=stop.id,
            vehicle_id=vehicle.id if vehicle else None,
            academic_year=student.academic_year or "2026-27",
            start_date=date.today(),
            status="Active",
            fee_amount=float(fee_amount or 15000.0),
            fee_status="Paid"
        )

        try:
            db.session.add(assignment)
            db.session.commit()
            return True, f"Transport pass issued successfully for {student.fullName} (ZPRN: {student_data['zprn']})!", assignment.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to issue transport assignment: {str(e)}", None

    @staticmethod
    def get_assignments(route_id=None, search=""):
        query = TransportAssignment.query

        if route_id:
            query = query.filter(TransportAssignment.route_id == route_id)

        assignments = query.order_by(TransportAssignment.id.desc()).all()
        result = [a.to_dict() for a in assignments]

        if search and search.strip():
            sq = search.strip().lower()
            result = [a for a in result if sq in a["zprn"].lower() or sq in a["student_name"].lower() or sq in a["route_name"].lower()]

        return result

    @staticmethod
    def cancel_assignment(assignment_id):
        tx = TransportAssignment.query.get(assignment_id)
        if not tx:
            return False, "Transport assignment not found."

        tx.status = "Cancelled"
        try:
            db.session.commit()
            return True, "Transport pass cancelled successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to cancel assignment: {str(e)}"

    # =========================================================
    # PDF REPORT GENERATOR
    # =========================================================
    @staticmethod
    def generate_pdf_transport_report(report_type="vehicle"):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#0F172A"), alignment=1)
        sub_style = ParagraphStyle("DocSub", parent=styles["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#64748B"), alignment=1)
        cell_style = ParagraphStyle("CellText", parent=styles["Normal"], fontSize=9, leading=11, textColor=colors.HexColor("#1E293B"))
        header_cell_style = ParagraphStyle("HeaderCell", parent=styles["Normal"], fontSize=9, leading=11, textColor=colors.white, fontName="Helvetica-Bold")

        elements.append(Paragraph("ZEAL EDUCATION SOCIETY", title_style))
        elements.append(Paragraph("Official Transport Management & Fleet Report", sub_style))
        elements.append(Paragraph(f"Generated Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", sub_style))
        elements.append(Spacer(1, 15))

        if report_type == "route":
            routes = TransportService.get_routes()
            table_data = [[Paragraph("Route Code", header_cell_style), Paragraph("Route Name", header_cell_style), Paragraph("Distance", header_cell_style), Paragraph("Stops", header_cell_style), Paragraph("Capacity", header_cell_style), Paragraph("Assigned", header_cell_style)]]
            for r in routes:
                table_data.append([
                    Paragraph(r["route_code"], cell_style),
                    Paragraph(r["route_name"], cell_style),
                    Paragraph(f"{r['distance_km']} km", cell_style),
                    Paragraph(str(r["stops_count"]), cell_style),
                    Paragraph(str(r["total_capacity"]), cell_style),
                    Paragraph(str(r["assigned_students"]), cell_style)
                ])
        elif report_type == "driver":
            drivers = TransportService.get_drivers()
            table_data = [[Paragraph("Name", header_cell_style), Paragraph("Phone", header_cell_style), Paragraph("License No", header_cell_style), Paragraph("Expiry", header_cell_style), Paragraph("Assigned Bus", header_cell_style), Paragraph("Status", header_cell_style)]]
            for d in drivers:
                table_data.append([
                    Paragraph(d["name"], cell_style),
                    Paragraph(d["phone"], cell_style),
                    Paragraph(d["license_number"], cell_style),
                    Paragraph(d["license_expiry"] or "-", cell_style),
                    Paragraph(d["assigned_vehicle"], cell_style),
                    Paragraph(d["status"], cell_style)
                ])
        elif report_type == "student":
            passes = TransportService.get_assignments()
            table_data = [[Paragraph("ZPRN", header_cell_style), Paragraph("Student Name", header_cell_style), Paragraph("Department", header_cell_style), Paragraph("Route", header_cell_style), Paragraph("Stop", header_cell_style), Paragraph("Fee Status", header_cell_style)]]
            for p in passes:
                table_data.append([
                    Paragraph(p["zprn"], cell_style),
                    Paragraph(p["student_name"], cell_style),
                    Paragraph(p["department"], cell_style),
                    Paragraph(p["route_name"], cell_style),
                    Paragraph(p["stop_name"], cell_style),
                    Paragraph(p["fee_status"], cell_style)
                ])
        else: # Vehicle report
            vehicles = TransportService.get_vehicles()
            table_data = [[Paragraph("Vehicle No", header_cell_style), Paragraph("Type", header_cell_style), Paragraph("Capacity", header_cell_style), Paragraph("Driver", header_cell_style), Paragraph("Route", header_cell_style), Paragraph("Status", header_cell_style)]]
            for v in vehicles:
                table_data.append([
                    Paragraph(v["vehicle_number"], cell_style),
                    Paragraph(v["vehicle_type"], cell_style),
                    Paragraph(str(v["capacity"]), cell_style),
                    Paragraph(v["driver_name"], cell_style),
                    Paragraph(v["route_name"], cell_style),
                    Paragraph(v["status"], cell_style)
                ])

        t = Table(table_data, colWidths=[90, 110, 80, 100, 100, 60])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer, None
