"""
SQLAlchemy ORM Models
Defines all database tables as Python classes.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, Date,
    DateTime, ForeignKey, JSON, Numeric, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="officer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    verified_violations = relationship("Violation", back_populates="verified_by_user")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_number = Column(String(20), unique=True, nullable=False, index=True)
    vehicle_type = Column(String(30), nullable=False)
    owner_name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(100))
    address = Column(Text)
    registration_date = Column(Date)
    insurance_expiry = Column(Date)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    violations = relationship("Violation", back_populates="vehicle")
    challans = relationship("Challan", back_populates="vehicle")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    zone = Column(String(50))
    is_active = Column(Boolean, default=True)
    stream_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    density_logs = relationship("TrafficDensity", back_populates="camera")
    violations = relationship("Violation", back_populates="camera")
    signal_timings = relationship("SignalTiming", back_populates="camera")


class TrafficDensity(Base):
    __tablename__ = "traffic_density"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="SET NULL"))
    lane_id = Column(Integer, nullable=False)
    vehicle_count = Column(Integer, nullable=False, default=0)
    congestion_index = Column(Float, nullable=False, default=0.0)
    avg_waiting_time_sec = Column(Float, default=0.0)
    recommended_green_time_sec = Column(Integer, default=30)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    camera = relationship("Camera", back_populates="density_logs")


class Violation(Base):
    __tablename__ = "violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_number = Column(String(20), index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"))
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="SET NULL"))
    violation_type = Column(String(30), nullable=False, index=True)
    violation_code = Column(String(10), nullable=False)
    location = Column(String(200))
    speed_detected = Column(Float)
    speed_limit = Column(Float)
    evidence_image = Column(String(500))
    confidence_score = Column(Float)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="violations")
    camera = relationship("Camera", back_populates="violations")
    verified_by_user = relationship("User", back_populates="verified_violations")
    challan = relationship("Challan", back_populates="violation", uselist=False)


class Challan(Base):
    __tablename__ = "challans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challan_number = Column(String(20), unique=True, nullable=False)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id", ondelete="CASCADE"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"))
    fine_amount = Column(Numeric(10, 2), nullable=False)
    issue_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    payment_status = Column(String(20), default="pending")
    payment_link = Column(String(500))
    pdf_path = Column(String(500))
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    violation = relationship("Violation", back_populates="challan")
    vehicle = relationship("Vehicle", back_populates="challans")
    payments = relationship("Payment", back_populates="challan")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challan_id = Column(UUID(as_uuid=True), ForeignKey("challans.id", ondelete="CASCADE"), nullable=False)
    payment_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_id = Column(String(100), unique=True)
    payment_method = Column(String(30))
    gateway_response = Column(JSON)
    status = Column(String(20), default="success")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    challan = relationship("Challan", back_populates="payments")


class SignalTiming(Base):
    __tablename__ = "signal_timings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="SET NULL"))
    intersection_name = Column(String(100))
    lane_count = Column(Integer, default=4)
    current_phase = Column(Integer, default=1)
    green_time_sec = Column(Integer, default=30)
    yellow_time_sec = Column(Integer, default=5)
    red_time_sec = Column(Integer, default=30)
    is_adaptive = Column(Boolean, default=True)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow)

    camera = relationship("Camera", back_populates="signal_timings")


class ViolationType(Base):
    __tablename__ = "violation_types"

    code = Column(String(10), primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    fine_amount = Column(Numeric(10, 2), nullable=False)
    severity = Column(String(20))


class AnalyticsLog(Base):
    __tablename__ = "analytics_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(JSON, nullable=False)
    zone = Column(String(50))
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
