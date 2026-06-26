"""
Analytics Routes
Provides dashboard analytics, trends, and ML predictions.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract, case, and_

from app.database import get_db
from app.models import (
    Violation, Challan, Payment, Vehicle, Camera,
    TrafficDensity, User,
)
from app.schemas import AnalyticsSummary
from app.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get dashboard summary statistics."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Total violations
    total_violations = await db.execute(select(func.count(Violation.id)))
    total_v = total_violations.scalar() or 0

    # Total challans
    total_challans = await db.execute(select(func.count(Challan.id)))
    total_c = total_challans.scalar() or 0

    # Total revenue (paid challans)
    total_revenue = await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == "success")
    )
    revenue = total_revenue.scalar() or Decimal("0")

    # Pending challans
    pending = await db.execute(
        select(func.count(Challan.id)).where(Challan.payment_status == "pending")
    )
    pending_count = pending.scalar() or 0

    # Violations today
    violations_today = await db.execute(
        select(func.count(Violation.id)).where(Violation.timestamp >= today)
    )
    today_count = violations_today.scalar() or 0

    # Active cameras
    active_cameras = await db.execute(
        select(func.count(Camera.id)).where(Camera.is_active == True)
    )
    cam_count = active_cameras.scalar() or 0

    return AnalyticsSummary(
        total_violations=total_v,
        total_challans=total_c,
        total_revenue=revenue,
        pending_challans=pending_count,
        violations_today=today_count,
        active_cameras=cam_count,
    )


@router.get("/violations/trend")
async def get_violation_trend(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get daily violation trend for the last N days."""
    since = datetime.utcnow() - timedelta(days=days)

    query = (
        select(
            func.date(Violation.timestamp).label("date"),
            Violation.violation_type,
            func.count(Violation.id).label("count"),
        )
        .where(Violation.timestamp >= since)
        .group_by(func.date(Violation.timestamp), Violation.violation_type)
        .order_by(func.date(Violation.timestamp))
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {"date": str(row.date), "violation_type": row.violation_type, "count": row.count}
        for row in rows
    ]


@router.get("/violations/by-type")
async def get_violations_by_type(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get violation count grouped by type (for pie chart)."""
    query = (
        select(
            Violation.violation_type,
            func.count(Violation.id).label("count"),
        )
        .group_by(Violation.violation_type)
    )

    result = await db.execute(query)
    rows = result.all()

    labels = {
        "red_light": "Red Light",
        "no_helmet": "No Helmet",
        "no_seatbelt": "No Seatbelt",
        "overspeed": "Overspeeding",
        "wrong_lane": "Wrong Lane",
    }

    return [
        {
            "type": row.violation_type,
            "label": labels.get(row.violation_type, row.violation_type),
            "count": row.count,
        }
        for row in rows
    ]


@router.get("/revenue/trend")
async def get_revenue_trend(
    months: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get monthly revenue trend."""
    since = datetime.utcnow() - timedelta(days=months * 30)

    query = (
        select(
            func.to_char(Payment.payment_date, 'YYYY-MM').label("month"),
            func.sum(Payment.amount).label("revenue"),
            func.count(Payment.id).label("paid_count"),
        )
        .where(Payment.status == "success", Payment.payment_date >= since)
        .group_by(func.to_char(Payment.payment_date, 'YYYY-MM'))
        .order_by(func.to_char(Payment.payment_date, 'YYYY-MM'))
    )

    result = await db.execute(query)
    rows = result.all()

    # Also get pending count per month
    pending_query = (
        select(
            func.to_char(Challan.created_at, 'YYYY-MM').label("month"),
            func.count(Challan.id).label("pending_count"),
        )
        .where(Challan.payment_status == "pending", Challan.created_at >= since)
        .group_by(func.to_char(Challan.created_at, 'YYYY-MM'))
    )
    pending_result = await db.execute(pending_query)
    pending_map = {r.month: r.pending_count for r in pending_result.all()}

    return [
        {
            "month": row.month,
            "revenue": float(row.revenue),
            "paid_count": row.paid_count,
            "pending_count": pending_map.get(row.month, 0),
        }
        for row in rows
    ]


@router.get("/peak-hours")
async def get_peak_hours(
    camera_id: Optional[str] = None,
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Analyze peak traffic hours."""
    since = datetime.utcnow() - timedelta(days=days)

    query = (
        select(
            extract("hour", TrafficDensity.timestamp).label("hour"),
            func.avg(TrafficDensity.vehicle_count).label("avg_count"),
            func.avg(TrafficDensity.congestion_index).label("avg_congestion"),
        )
        .where(TrafficDensity.timestamp >= since)
        .group_by(extract("hour", TrafficDensity.timestamp))
        .order_by(extract("hour", TrafficDensity.timestamp))
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "hour": int(row.hour),
            "hour_label": f"{int(row.hour):02d}:00",
            "avg_vehicle_count": round(float(row.avg_count), 1),
            "avg_congestion": round(float(row.avg_congestion), 3),
        }
        for row in rows
    ]


@router.get("/zone-analysis")
async def get_zone_analysis(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get violation and density analysis by zone."""
    # Violations per zone (via camera)
    query = (
        select(
            Camera.zone,
            func.count(Violation.id).label("violation_count"),
        )
        .join(Violation, Violation.camera_id == Camera.id)
        .where(Camera.zone.isnot(None))
        .group_by(Camera.zone)
    )

    result = await db.execute(query)
    violation_data = {r.zone: r.violation_count for r in result.all()}

    # Average density per zone
    density_query = (
        select(
            Camera.zone,
            func.avg(TrafficDensity.congestion_index).label("avg_density"),
        )
        .join(TrafficDensity, TrafficDensity.camera_id == Camera.id)
        .where(Camera.zone.isnot(None))
        .group_by(Camera.zone)
    )

    density_result = await db.execute(density_query)
    density_data = {r.zone: round(float(r.avg_density), 3) for r in density_result.all()}

    zones = set(list(violation_data.keys()) + list(density_data.keys()))

    return [
        {
            "zone": zone,
            "violation_count": violation_data.get(zone, 0),
            "avg_density": density_data.get(zone, 0.0),
        }
        for zone in sorted(zones)
    ]


@router.get("/export/csv")
async def export_violations_csv(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export violations data as CSV."""
    from fastapi.responses import StreamingResponse
    import csv
    import io

    query = select(Violation)
    if start_date:
        query = query.where(Violation.timestamp >= start_date)
    if end_date:
        query = query.where(Violation.timestamp <= end_date)

    query = query.order_by(Violation.timestamp.desc())
    result = await db.execute(query)
    violations = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Plate Number", "Violation Type", "Violation Code",
        "Location", "Speed Detected", "Speed Limit", "Confidence",
        "Verified", "Timestamp",
    ])

    for v in violations:
        writer.writerow([
            str(v.id), v.plate_number, v.violation_type, v.violation_code,
            v.location, v.speed_detected, v.speed_limit, v.confidence_score,
            v.is_verified, v.timestamp.isoformat() if v.timestamp else "",
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=violations_export.csv"},
    )
