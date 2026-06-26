"""
Frame Upload and AI Processing Routes
Handles video frame uploads for real-time processing.
"""

import os
import uuid
import time
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import FrameProcessingResult
from app.auth import get_current_user
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/frames", tags=["Frame Processing"])


@router.post("/upload", response_model=FrameProcessingResult)
async def upload_frame(
    file: UploadFile = File(...),
    camera_id: str = "default",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Upload a video frame for AI processing.
    
    The frame will be processed through:
    1. Vehicle detection (YOLO26)
    2. Vehicle tracking (SORT)
    3. Traffic density calculation
    4. Violation detection
    5. ANPR (if violation detected)
    
    Returns processing results including detected vehicles,
    violations, and recognized plates.
    """
    start_time = time.time()

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save frame
    frame_id = str(uuid.uuid4())
    frame_dir = os.path.join(settings.UPLOAD_DIR, "frames", camera_id)
    os.makedirs(frame_dir, exist_ok=True)

    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    frame_path = os.path.join(frame_dir, f"{frame_id}.{ext}")

    content = await file.read()
    with open(frame_path, "wb") as f:
        f.write(content)

    # Process frame through AI pipeline
    # In production, this would call the AI service
    # For now, return a structured response
    processing_time = (time.time() - start_time) * 1000

    try:
        # Attempt to use AI service if available
        from ai_service.detector import process_frame
        result = process_frame(frame_path, camera_id)
        return FrameProcessingResult(
            frame_id=frame_id,
            vehicles_detected=result.get("vehicles_detected", 0),
            violations_found=result.get("violations_found", 0),
            density=result.get("density", {}),
            plates_recognized=result.get("plates", []),
            processing_time_ms=processing_time,
        )
    except ImportError:
        logger.info("AI service not available, returning frame metadata only")
        return FrameProcessingResult(
            frame_id=frame_id,
            vehicles_detected=0,
            violations_found=0,
            density={"status": "ai_service_not_connected"},
            plates_recognized=[],
            processing_time_ms=processing_time,
        )


@router.get("/cameras")
async def list_cameras(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all registered cameras."""
    from sqlalchemy import select
    from app.models import Camera

    result = await db.execute(select(Camera).where(Camera.is_active == True))
    cameras = result.scalars().all()

    return [
        {
            "id": str(c.id),
            "name": c.camera_name,
            "location": c.location,
            "zone": c.zone,
            "stream_url": c.stream_url,
            "latitude": c.latitude,
            "longitude": c.longitude,
        }
        for c in cameras
    ]
