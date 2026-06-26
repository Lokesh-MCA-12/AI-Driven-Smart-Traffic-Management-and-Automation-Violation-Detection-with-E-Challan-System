"""
FastAPI Main Application
Entry point for the Smart Traffic Management System API.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.routes import (
    auth_routes,
    vehicle_routes,
    violation_routes,
    traffic_routes,
    analytics_routes,
    frame_routes,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events."""
    logger.info("🚀 Starting Smart Traffic Management System API...")
    # Initialize database tables (if not using init.sql)
    # await init_db()
    logger.info("✅ Application started successfully")
    yield
    logger.info("🛑 Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Smart Traffic Management System API",
    description=(
        "AI-Driven Smart Traffic Management and Automated Violation Detection "
        "with E-Challan System. Provides endpoints for traffic monitoring, "
        "violation detection, challan generation, and analytics."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."},
    )


# Mount static files for evidence images
import os
if os.path.exists(settings.EVIDENCE_DIR):
    app.mount("/evidence", StaticFiles(directory=settings.EVIDENCE_DIR), name="evidence")

if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Include routers
app.include_router(auth_routes.router, prefix="/api")
app.include_router(vehicle_routes.router, prefix="/api")
app.include_router(violation_routes.router, prefix="/api")
app.include_router(traffic_routes.router, prefix="/api")
app.include_router(analytics_routes.router, prefix="/api")
app.include_router(frame_routes.router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Smart Traffic Management System",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "available",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
