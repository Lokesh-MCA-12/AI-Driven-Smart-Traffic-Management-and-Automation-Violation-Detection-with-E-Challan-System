"""
Vehicle Management Routes
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Vehicle, User
from app.schemas import VehicleCreate, VehicleResponse
from app.auth import get_current_user, require_officer_or_admin

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post("/", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    data: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_officer_or_admin),
):
    """Register a new vehicle."""
    existing = await db.execute(
        select(Vehicle).where(Vehicle.plate_number == data.plate_number)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Vehicle already registered")

    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    await db.flush()
    await db.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)


@router.get("/{plate_number}", response_model=VehicleResponse)
async def get_vehicle(
    plate_number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get vehicle details by plate number."""
    cleaned = plate_number.upper().replace(" ", "").replace("-", "")
    result = await db.execute(select(Vehicle).where(Vehicle.plate_number == cleaned))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return VehicleResponse.model_validate(vehicle)


@router.get("/", response_model=list[VehicleResponse])
async def list_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    vehicle_type: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List vehicles with pagination and filters."""
    query = select(Vehicle)

    if vehicle_type:
        query = query.where(Vehicle.vehicle_type == vehicle_type)

    if search:
        search_term = f"%{search.upper()}%"
        query = query.where(
            (Vehicle.plate_number.ilike(search_term)) |
            (Vehicle.owner_name.ilike(search_term))
        )

    query = query.order_by(Vehicle.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    vehicles = result.scalars().all()

    return [VehicleResponse.model_validate(v) for v in vehicles]


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    data: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_officer_or_admin),
):
    """Update vehicle details."""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, key, value)

    await db.flush()
    await db.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)
