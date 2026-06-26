"""
Pydantic Schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
import re


# ============================================================
# AUTH SCHEMAS
# ============================================================

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default="officer", pattern="^(admin|officer)$")


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================================
# VEHICLE SCHEMAS
# ============================================================

class VehicleCreate(BaseModel):
    plate_number: str = Field(..., min_length=4, max_length=20)
    vehicle_type: str = Field(..., pattern="^(car|bike|bus|truck|auto|other)$")
    owner_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    registration_date: Optional[date] = None
    insurance_expiry: Optional[date] = None

    @validator("plate_number")
    def validate_plate(cls, v):
        """Validate Indian vehicle plate format."""
        pattern = r'^[A-Z]{2}\d{2}[A-Z]{0,3}\d{4}$'
        cleaned = v.upper().replace(" ", "").replace("-", "")
        if not re.match(pattern, cleaned):
            raise ValueError("Invalid plate format. Expected: XX00XX0000 (e.g., KA01AB1234)")
        return cleaned


class VehicleResponse(BaseModel):
    id: UUID
    plate_number: str
    vehicle_type: str
    owner_name: str
    phone: str
    email: Optional[str]
    address: Optional[str]
    registration_date: Optional[date]
    insurance_expiry: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


class VehicleSearch(BaseModel):
    plate_number: str


# ============================================================
# CAMERA SCHEMAS
# ============================================================

class CameraCreate(BaseModel):
    camera_name: str = Field(..., max_length=100)
    location: str = Field(..., max_length=200)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    zone: Optional[str] = None
    stream_url: Optional[str] = None


class CameraResponse(BaseModel):
    id: UUID
    camera_name: str
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    zone: Optional[str]
    is_active: bool
    stream_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# TRAFFIC DENSITY SCHEMAS
# ============================================================

class TrafficDensityCreate(BaseModel):
    camera_id: UUID
    lane_id: int
    vehicle_count: int = Field(ge=0)
    congestion_index: float = Field(ge=0.0, le=1.0)
    avg_waiting_time_sec: float = Field(ge=0.0)
    recommended_green_time_sec: int = Field(ge=5, le=120)


class TrafficDensityResponse(BaseModel):
    id: UUID
    camera_id: Optional[UUID]
    lane_id: int
    vehicle_count: int
    congestion_index: float
    avg_waiting_time_sec: float
    recommended_green_time_sec: int
    timestamp: datetime

    class Config:
        from_attributes = True


class AdaptiveSignalResponse(BaseModel):
    camera_id: UUID
    intersection: str
    lanes: List[dict]
    recommended_cycle: dict
    timestamp: datetime


# ============================================================
# VIOLATION SCHEMAS
# ============================================================

class ViolationCreate(BaseModel):
    plate_number: Optional[str] = None
    camera_id: Optional[UUID] = None
    violation_type: str = Field(..., pattern="^(red_light|no_helmet|no_seatbelt|overspeed|wrong_lane)$")
    location: Optional[str] = None
    speed_detected: Optional[float] = None
    speed_limit: Optional[float] = None
    evidence_image: Optional[str] = None
    confidence_score: Optional[float] = None


class ViolationResponse(BaseModel):
    id: UUID
    plate_number: Optional[str]
    violation_type: str
    violation_code: str
    location: Optional[str]
    speed_detected: Optional[float]
    speed_limit: Optional[float]
    evidence_image: Optional[str]
    confidence_score: Optional[float]
    is_verified: bool
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ViolationFilter(BaseModel):
    violation_type: Optional[str] = None
    plate_number: Optional[str] = None
    camera_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_verified: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ============================================================
# CHALLAN SCHEMAS
# ============================================================

class ChallanCreate(BaseModel):
    violation_id: UUID


class ChallanResponse(BaseModel):
    id: UUID
    challan_number: str
    violation_id: UUID
    vehicle_id: Optional[UUID]
    fine_amount: Decimal
    issue_date: date
    due_date: date
    payment_status: str
    payment_link: Optional[str]
    pdf_path: Optional[str]
    notification_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# PAYMENT SCHEMAS
# ============================================================

class PaymentCreate(BaseModel):
    challan_id: UUID
    amount: Decimal = Field(gt=0)
    transaction_id: str
    payment_method: str = Field(pattern="^(online|upi|card|netbanking|cash)$")


class PaymentResponse(BaseModel):
    id: UUID
    challan_id: UUID
    payment_date: datetime
    amount: Decimal
    transaction_id: str
    payment_method: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentUpdate(BaseModel):
    challan_id: UUID
    transaction_id: str
    status: str = Field(pattern="^(success|failed|refunded|pending)$")


# ============================================================
# ANALYTICS SCHEMAS
# ============================================================

class AnalyticsSummary(BaseModel):
    total_violations: int
    total_challans: int
    total_revenue: Decimal
    pending_challans: int
    violations_today: int
    active_cameras: int


class ViolationTrend(BaseModel):
    date: str
    count: int
    violation_type: str


class RevenueTrend(BaseModel):
    month: str
    revenue: Decimal
    paid_count: int
    pending_count: int


class ZoneAnalytics(BaseModel):
    zone: str
    violation_count: int
    avg_density: float
    peak_hour: str


class DensitySnapshot(BaseModel):
    camera_id: UUID
    camera_name: str
    location: str
    lanes: List[dict]
    overall_congestion: float
    timestamp: datetime


# ============================================================
# FRAME UPLOAD SCHEMA
# ============================================================

class FrameProcessingResult(BaseModel):
    frame_id: str
    vehicles_detected: int
    violations_found: int
    density: dict
    plates_recognized: List[str]
    processing_time_ms: float
