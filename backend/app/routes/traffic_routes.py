"""
Traffic Density and Signal Control Routes
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models import TrafficDensity, Camera, SignalTiming, User
from app.schemas import (
    TrafficDensityCreate, TrafficDensityResponse,
    AdaptiveSignalResponse, DensitySnapshot,
)
from app.auth import get_current_user

router = APIRouter(prefix="/traffic", tags=["Traffic Management"])

# Adaptive signal parameters
MIN_GREEN_TIME = 10  # seconds
MAX_GREEN_TIME = 90  # seconds
DEFAULT_GREEN_TIME = 30  # seconds
VEHICLE_THRESHOLD_LOW = 5
VEHICLE_THRESHOLD_HIGH = 20


def calculate_adaptive_signal(vehicle_count: int, current_green: int = DEFAULT_GREEN_TIME) -> int:
    """
    Calculate adaptive green signal time based on vehicle count.

    Algorithm:
    - Low traffic (< 5 vehicles): Decrease green time
    - Medium traffic (5-20 vehicles): Keep default
    - High traffic (> 20 vehicles): Increase green time proportionally
    """
    if vehicle_count <= VEHICLE_THRESHOLD_LOW:
        green_time = max(MIN_GREEN_TIME, current_green - 10)
    elif vehicle_count >= VEHICLE_THRESHOLD_HIGH:
        # Scale up: +5 seconds for every 5 vehicles above threshold
        extra = ((vehicle_count - VEHICLE_THRESHOLD_HIGH) // 5 + 1) * 5
        green_time = min(MAX_GREEN_TIME, current_green + extra)
    else:
        green_time = DEFAULT_GREEN_TIME

    return green_time


def calculate_congestion_index(vehicle_count: int, max_capacity: int = 50) -> float:
    """Calculate congestion index (0.0 to 1.0)."""
    return min(1.0, vehicle_count / max_capacity)


def estimate_waiting_time(vehicle_count: int, green_time: int) -> float:
    """Estimate average waiting time in seconds."""
    if vehicle_count == 0:
        return 0.0
    # Simple model: each vehicle adds ~2 seconds of delay
    cycle_time = green_time * 2  # Approximate full cycle
    avg_wait = (cycle_time / 2) * (vehicle_count / max(vehicle_count, 1))
    return round(min(avg_wait, 300), 1)  # Cap at 5 minutes


@router.post("/density", response_model=TrafficDensityResponse, status_code=201)
async def record_density(
    data: TrafficDensityCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Record traffic density reading for a lane."""
    # Verify camera exists
    cam_result = await db.execute(select(Camera).where(Camera.id == data.camera_id))
    camera = cam_result.scalar_one_or_none()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Calculate adaptive values
    congestion = calculate_congestion_index(data.vehicle_count)
    green_time = calculate_adaptive_signal(data.vehicle_count)
    waiting_time = estimate_waiting_time(data.vehicle_count, green_time)

    density = TrafficDensity(
        camera_id=data.camera_id,
        lane_id=data.lane_id,
        vehicle_count=data.vehicle_count,
        congestion_index=congestion,
        avg_waiting_time_sec=waiting_time,
        recommended_green_time_sec=green_time,
    )

    db.add(density)
    await db.flush()
    await db.refresh(density)

    # Update signal timing
    signal_result = await db.execute(
        select(SignalTiming).where(SignalTiming.camera_id == data.camera_id)
    )
    signal = signal_result.scalar_one_or_none()
    if signal and signal.is_adaptive:
        signal.green_time_sec = green_time
        signal.last_updated = datetime.utcnow()
        await db.flush()

    return TrafficDensityResponse.model_validate(density)


@router.get("/density", response_model=list[DensitySnapshot])
async def get_density(
    camera_id: Optional[UUID] = None,
    zone: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get current traffic density across cameras."""
    camera_query = select(Camera).where(Camera.is_active == True)
    if camera_id:
        camera_query = camera_query.where(Camera.id == camera_id)
    if zone:
        camera_query = camera_query.where(Camera.zone == zone)

    cam_result = await db.execute(camera_query)
    cameras = cam_result.scalars().all()

    snapshots = []
    for cam in cameras:
        # Get latest density readings per lane
        lane_query = (
            select(TrafficDensity)
            .where(TrafficDensity.camera_id == cam.id)
            .order_by(desc(TrafficDensity.timestamp))
            .limit(4)  # Up to 4 lanes
        )
        lane_result = await db.execute(lane_query)
        lanes = lane_result.scalars().all()

        lane_data = []
        total_congestion = 0.0
        for lane in lanes:
            lane_data.append({
                "lane_id": lane.lane_id,
                "vehicle_count": lane.vehicle_count,
                "congestion_index": lane.congestion_index,
                "avg_waiting_time_sec": lane.avg_waiting_time_sec,
                "recommended_green_time_sec": lane.recommended_green_time_sec,
            })
            total_congestion += lane.congestion_index

        overall = total_congestion / len(lanes) if lanes else 0.0

        snapshots.append(DensitySnapshot(
            camera_id=cam.id,
            camera_name=cam.camera_name,
            location=cam.location,
            lanes=lane_data,
            overall_congestion=round(overall, 3),
            timestamp=lanes[0].timestamp if lanes else datetime.utcnow(),
        ))

    return snapshots


@router.get("/density/history")
async def get_density_history(
    camera_id: UUID,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get traffic density history for a camera."""
    since = datetime.utcnow() - timedelta(hours=hours)

    query = (
        select(TrafficDensity)
        .where(
            TrafficDensity.camera_id == camera_id,
            TrafficDensity.timestamp >= since,
        )
        .order_by(TrafficDensity.timestamp)
    )

    result = await db.execute(query)
    readings = result.scalars().all()

    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "lane_id": r.lane_id,
            "vehicle_count": r.vehicle_count,
            "congestion_index": r.congestion_index,
            "avg_waiting_time_sec": r.avg_waiting_time_sec,
            "recommended_green_time_sec": r.recommended_green_time_sec,
        }
        for r in readings
    ]


@router.get("/signal/{camera_id}")
async def get_signal_timing(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get current signal timing for a camera/intersection."""
    result = await db.execute(
        select(SignalTiming).where(SignalTiming.camera_id == camera_id)
    )
    signal = result.scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal timing not found")

    return {
        "camera_id": str(signal.camera_id),
        "intersection_name": signal.intersection_name,
        "lane_count": signal.lane_count,
        "current_phase": signal.current_phase,
        "green_time_sec": signal.green_time_sec,
        "yellow_time_sec": signal.yellow_time_sec,
        "red_time_sec": signal.red_time_sec,
        "is_adaptive": signal.is_adaptive,
        "last_updated": signal.last_updated.isoformat() if signal.last_updated else None,
    }
