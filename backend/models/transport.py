from datetime import datetime, date
from .database import db

class TransportDriver(db.Model):
    __tablename__ = "transport_drivers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    license_expiry = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="Active", nullable=False)  # Active, Inactive, On Leave
    emergency_contact = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assigned_vehicles = db.relationship("TransportVehicle", backref="driver", lazy=True)

    def to_dict(self):
        assigned_veh = self.assigned_vehicles[0].vehicle_number if self.assigned_vehicles else "Unassigned"
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "license_number": self.license_number,
            "license_expiry": self.license_expiry.strftime("%Y-%m-%d") if self.license_expiry else "",
            "status": self.status,
            "emergency_contact": self.emergency_contact or "-",
            "assigned_vehicle": assigned_veh
        }


class TransportRoute(db.Model):
    __tablename__ = "transport_routes"

    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    route_code = db.Column(db.String(50), unique=True, nullable=False)
    start_point = db.Column(db.String(100), default="College Campus", nullable=False)
    destination = db.Column(db.String(100), default="College Campus", nullable=False)
    distance_km = db.Column(db.Float, default=15.0, nullable=False)
    estimated_time = db.Column(db.String(50), default="45 Mins", nullable=False)
    status = db.Column(db.String(20), default="Active", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    stops = db.relationship("TransportStop", backref="route", cascade="all, delete-orphan", lazy=True, order_by="TransportStop.sequence_number")
    vehicles = db.relationship("TransportVehicle", backref="route", lazy=True)
    assignments = db.relationship("TransportAssignment", backref="route", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        assigned_count = len([a for a in self.assignments if a.status == "Active"])
        total_capacity = sum(v.capacity for v in self.vehicles if v.status == "Active") or 40
        return {
            "id": self.id,
            "route_name": self.route_name,
            "route_code": self.route_code,
            "start_point": self.start_point,
            "destination": self.destination,
            "distance_km": self.distance_km,
            "estimated_time": self.estimated_time,
            "status": self.status,
            "stops_count": len(self.stops),
            "vehicles_count": len(self.vehicles),
            "assigned_students": assigned_count,
            "total_capacity": total_capacity,
            "available_seats": max(0, total_capacity - assigned_count),
            "stops": [s.to_dict() for s in self.stops]
        }


class TransportStop(db.Model):
    __tablename__ = "transport_stops"

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("transport_routes.id"), nullable=False)
    stop_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(150), nullable=True)
    sequence_number = db.Column(db.Integer, nullable=False, default=1)
    pickup_time = db.Column(db.String(20), default="07:30 AM", nullable=False)
    drop_time = db.Column(db.String(20), default="05:30 PM", nullable=False)
    status = db.Column(db.String(20), default="Active", nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "route_id": self.route_id,
            "route_name": self.route.route_name if self.route else "-",
            "stop_name": self.stop_name,
            "location": self.location or self.stop_name,
            "sequence_number": self.sequence_number,
            "pickup_time": self.pickup_time,
            "drop_time": self.drop_time,
            "status": self.status
        }


class TransportVehicle(db.Model):
    __tablename__ = "transport_vehicles"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), default="Bus", nullable=False)
    capacity = db.Column(db.Integer, default=40, nullable=False)
    assigned_driver_id = db.Column(db.Integer, db.ForeignKey("transport_drivers.id"), nullable=True)
    assigned_route_id = db.Column(db.Integer, db.ForeignKey("transport_routes.id"), nullable=True)
    status = db.Column(db.String(20), default="Active", nullable=False)  # Active, Inactive, Maintenance
    insurance_expiry = db.Column(db.Date, nullable=True)
    fitness_expiry = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignments = db.relationship("TransportAssignment", backref="vehicle", lazy=True)

    def to_dict(self):
        active_assignments = len([a for a in self.assignments if a.status == "Active"])
        return {
            "id": self.id,
            "vehicle_number": self.vehicle_number,
            "registration_number": self.registration_number,
            "vehicle_type": self.vehicle_type,
            "capacity": self.capacity,
            "assigned_driver_id": self.assigned_driver_id,
            "driver_name": self.driver.name if self.driver else "Unassigned",
            "driver_phone": self.driver.phone if self.driver else "-",
            "assigned_route_id": self.assigned_route_id,
            "route_name": self.route.route_name if self.route else "Unassigned",
            "route_code": self.route.route_code if self.route else "-",
            "status": self.status,
            "insurance_expiry": self.insurance_expiry.strftime("%Y-%m-%d") if self.insurance_expiry else "",
            "fitness_expiry": self.fitness_expiry.strftime("%Y-%m-%d") if self.fitness_expiry else "",
            "description": self.description or "",
            "assigned_students": active_assignments,
            "available_seats": max(0, self.capacity - active_assignments)
        }


class TransportAssignment(db.Model):
    __tablename__ = "transport_assignments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey("transport_routes.id"), nullable=False)
    stop_id = db.Column(db.Integer, db.ForeignKey("transport_stops.id"), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("transport_vehicles.id"), nullable=True)
    academic_year = db.Column(db.String(20), default="2026-27", nullable=False)
    start_date = db.Column(db.Date, default=date.today, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="Active", nullable=False)  # Active, Cancelled, Expired
    fee_amount = db.Column(db.Float, default=15000.0, nullable=False)
    fee_status = db.Column(db.String(20), default="Paid", nullable=False)  # Paid, Pending, Partial
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="transport_assignments", lazy=True)
    stop = db.relationship("TransportStop", backref="assignments", lazy=True)

    def to_dict(self):
        s = self.student
        r = self.route
        st = self.stop
        v = self.vehicle
        return {
            "id": self.id,
            "student_id": self.student_id,
            "zprn": s.enrollment_number or f"ZPRN-2026-{s.id:04d}" if s else "-",
            "student_name": s.fullName if s else "Unknown Student",
            "department": s.department if s else "-",
            "course": s.course if s else "-",
            "academic_year": self.academic_year,
            "route_id": self.route_id,
            "route_name": r.route_name if r else "-",
            "route_code": r.route_code if r else "-",
            "stop_id": self.stop_id,
            "stop_name": st.stop_name if st else "-",
            "vehicle_id": self.vehicle_id,
            "vehicle_number": v.vehicle_number if v else "Auto-assigned",
            "status": self.status,
            "fee_amount": self.fee_amount,
            "fee_status": self.fee_status,
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else "",
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else ""
        }
