"""
Violation and Challan Routes
Handles violation recording, challan generation, and payment processing.
"""

import os
import random
import string
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database import get_db
from app.models import Violation, Challan, Payment, Vehicle, ViolationType, User
from app.schemas import (
    ViolationCreate, ViolationResponse, ChallanCreate, ChallanResponse,
    PaymentCreate, PaymentResponse, PaymentUpdate,
)
from app.auth import get_current_user, require_officer_or_admin, require_admin
from app.notifications import NotificationService
from app.challan_pdf import generate_challan_pdf
from app.config import settings

router = APIRouter(tags=["Violations & Challans"])

VIOLATION_CODE_MAP = {
    "red_light": "RL001",
    "no_helmet": "NH001",
    "no_seatbelt": "NS001",
    "overspeed": "OS001",
    "wrong_lane": "WL001",
}


def generate_challan_number() -> str:
    """Generate a unique challan number."""
    prefix = "ECH"
    timestamp = datetime.now().strftime("%y%m%d")
    random_part = "".join(random.choices(string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_part}"


# ============================================================
# VIOLATION ENDPOINTS
# ============================================================

@router.post("/violations", response_model=ViolationResponse, status_code=201)
async def create_violation(
    data: ViolationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_officer_or_admin),
):
    """Record a new traffic violation."""
    violation_code = VIOLATION_CODE_MAP.get(data.violation_type, "UK001")

    # Try to match vehicle
    vehicle_id = None
    if data.plate_number:
        result = await db.execute(
            select(Vehicle).where(Vehicle.plate_number == data.plate_number)
        )
        vehicle = result.scalar_one_or_none()
        if vehicle:
            vehicle_id = vehicle.id

    violation = Violation(
        plate_number=data.plate_number,
        vehicle_id=vehicle_id,
        camera_id=data.camera_id,
        violation_type=data.violation_type,
        violation_code=violation_code,
        location=data.location,
        speed_detected=data.speed_detected,
        speed_limit=data.speed_limit,
        evidence_image=data.evidence_image,
        confidence_score=data.confidence_score,
    )
    db.add(violation)
    await db.flush()
    await db.refresh(violation)

    return ViolationResponse.model_validate(violation)


@router.get("/violations", response_model=list[ViolationResponse])
async def list_violations(
    violation_type: Optional[str] = None,
    plate_number: Optional[str] = None,
    camera_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    is_verified: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List violations with filters and pagination."""
    query = select(Violation)

    if violation_type:
        query = query.where(Violation.violation_type == violation_type)
    if plate_number:
        query = query.where(Violation.plate_number == plate_number.upper())
    if camera_id:
        query = query.where(Violation.camera_id == camera_id)
    if start_date:
        query = query.where(Violation.timestamp >= start_date)
    if end_date:
        query = query.where(Violation.timestamp <= end_date)
    if is_verified is not None:
        query = query.where(Violation.is_verified == is_verified)

    query = query.order_by(Violation.timestamp.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    violations = result.scalars().all()

    return [ViolationResponse.model_validate(v) for v in violations]


@router.get("/violations/{violation_id}", response_model=ViolationResponse)
async def get_violation(
    violation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get violation details by ID."""
    result = await db.execute(select(Violation).where(Violation.id == violation_id))
    violation = result.scalar_one_or_none()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    return ViolationResponse.model_validate(violation)


@router.post("/violations/{violation_id}/verify", response_model=ViolationResponse)
async def verify_violation(
    violation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_officer_or_admin),
):
    """Verify a violation (officer or admin)."""
    result = await db.execute(select(Violation).where(Violation.id == violation_id))
    violation = result.scalar_one_or_none()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    violation.is_verified = True
    violation.verified_by = user.id
    await db.flush()
    await db.refresh(violation)

    return ViolationResponse.model_validate(violation)


# ============================================================
# CHALLAN ENDPOINTS
# ============================================================

@router.post("/generate-challan", response_model=ChallanResponse, status_code=201)
async def generate_challan(
    data: ChallanCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_officer_or_admin),
):
    """Generate an E-Challan for a violation."""
    # Get violation
    result = await db.execute(select(Violation).where(Violation.id == data.violation_id))
    violation = result.scalar_one_or_none()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    # Check if challan already exists
    existing = await db.execute(
        select(Challan).where(Challan.violation_id == data.violation_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Challan already generated for this violation")

    # Get fine amount from violation types table
    vt_result = await db.execute(
        select(ViolationType).where(ViolationType.code == violation.violation_code)
    )
    violation_type_record = vt_result.scalar_one_or_none()
    fine_amount = float(violation_type_record.fine_amount) if violation_type_record else 500.0

    # Generate challan
    challan_number = generate_challan_number()
    due_date = date.today() + timedelta(days=30)

    challan = Challan(
        challan_number=challan_number,
        violation_id=violation.id,
        vehicle_id=violation.vehicle_id,
        fine_amount=Decimal(str(fine_amount)),
        due_date=due_date,
    )

    # Generate PDF
    try:
        vehicle = None
        if violation.vehicle_id:
            v_result = await db.execute(select(Vehicle).where(Vehicle.id == violation.vehicle_id))
            vehicle = v_result.scalar_one_or_none()

        pdf_path = generate_challan_pdf(
            challan_number=challan_number,
            owner_name=vehicle.owner_name if vehicle else "Unknown",
            plate_number=violation.plate_number or "Unknown",
            vehicle_type=vehicle.vehicle_type if vehicle else "Unknown",
            violation_type=violation.violation_type,
            location=violation.location or "Unknown",
            timestamp=violation.timestamp.strftime("%d-%m-%Y %H:%M:%S") if violation.timestamp else "",
            fine_amount=fine_amount,
            due_date=due_date.strftime("%d-%m-%Y"),
            evidence_image_path=violation.evidence_image,
        )
        challan.pdf_path = pdf_path
    except Exception as e:
        import logging
        logging.error(f"PDF generation failed: {e}")

    db.add(challan)
    await db.flush()
    await db.refresh(challan)

    # Send notifications
    if violation.vehicle_id:
        try:
            v_result = await db.execute(select(Vehicle).where(Vehicle.id == violation.vehicle_id))
            vehicle = v_result.scalar_one_or_none()
            if vehicle:
                ns = NotificationService()

                # Send Email
                if vehicle.email:
                    email_body = ns.build_challan_email(
                        owner_name=vehicle.owner_name,
                        challan_number=challan_number,
                        violation_type=violation.violation_type,
                        fine_amount=fine_amount,
                        due_date=due_date.strftime("%d-%m-%Y"),
                        location=violation.location or "Unknown",
                        timestamp=violation.timestamp.strftime("%d-%m-%Y %H:%M:%S") if violation.timestamp else "",
                    )
                    await ns.send_email(
                        vehicle.email,
                        f"Traffic Violation Notice - {challan_number}",
                        email_body,
                        challan.pdf_path,
                    )

                # Send SMS
                if vehicle.phone:
                    sms_text = ns.build_challan_sms(
                        owner_name=vehicle.owner_name,
                        challan_number=challan_number,
                        violation_type=violation.violation_type,
                        fine_amount=fine_amount,
                        due_date=due_date.strftime("%d-%m-%Y"),
                    )
                    await ns.send_sms(vehicle.phone, sms_text)

                challan.notification_sent = True
                await db.flush()

        except Exception as e:
            import logging
            logging.error(f"Notification failed: {e}")

    return ChallanResponse.model_validate(challan)


@router.get("/challans", response_model=list[ChallanResponse])
async def list_challans(
    payment_status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List challans with filters."""
    query = select(Challan)

    if payment_status:
        query = query.where(Challan.payment_status == payment_status)

    query = query.order_by(Challan.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    challans = result.scalars().all()

    return [ChallanResponse.model_validate(c) for c in challans]


# ============================================================
# PAYMENT ENDPOINTS
# ============================================================

@router.post("/update-payment", response_model=PaymentResponse, status_code=201)
async def process_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Process a payment for a challan."""
    # Get challan
    result = await db.execute(select(Challan).where(Challan.id == data.challan_id))
    challan = result.scalar_one_or_none()

    if not challan:
        raise HTTPException(status_code=404, detail="Challan not found")

    if challan.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Challan already paid")

    # Check transaction ID uniqueness
    existing = await db.execute(
        select(Payment).where(Payment.transaction_id == data.transaction_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Transaction ID already used")

    # Create payment record
    payment = Payment(
        challan_id=data.challan_id,
        amount=data.amount,
        transaction_id=data.transaction_id,
        payment_method=data.payment_method,
        status="success",
    )
    db.add(payment)

    # Update challan status
    challan.payment_status = "paid"
    await db.flush()
    await db.refresh(payment)

    return PaymentResponse.model_validate(payment)
