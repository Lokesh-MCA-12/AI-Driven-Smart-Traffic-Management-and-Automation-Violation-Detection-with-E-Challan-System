"""
AI Service Entry Point.
Run with: python -m ai_service
"""

import os
import sys
import logging
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service.detector import DetectionPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="AI Traffic Monitoring Service"
    )
    parser.add_argument(
        "--source", type=str, default="0",
        help="Video source: file path, camera index (0), or RTSP URL"
    )
    parser.add_argument(
        "--camera-id", type=str, default="CAM-001",
        help="Camera identifier"
    )
    parser.add_argument(
        "--model", type=str, default="yolo26n.pt",
        help="Path to YOLO26 model"
    )
    parser.add_argument(
        "--confidence", type=float, default=0.5,
        help="Detection confidence threshold"
    )
    parser.add_argument(
        "--speed-limit", type=float, default=60.0,
        help="Speed limit in km/h"
    )
    parser.add_argument(
        "--fps", type=int, default=15,
        help="Expected FPS for speed estimation"
    )
    parser.add_argument(
        "--no-display", action="store_true",
        help="Disable visual display"
    )
    parser.add_argument(
        "--max-frames", type=int, default=0,
        help="Maximum frames to process (0 = unlimited)"
    )
    parser.add_argument(
        "--api-url", type=str, default="http://localhost:8000",
        help="Backend API base URL"
    )
    parser.add_argument(
        "--stop-line", type=int, default=400,
        help="Stop line Y coordinate"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("AI Traffic Monitoring Service")
    logger.info("=" * 60)
    logger.info(f"Source: {args.source}")
    logger.info(f"Camera: {args.camera_id}")
    logger.info(f"Model: {args.model}")
    logger.info(f"Speed Limit: {args.speed_limit} km/h")
    logger.info(f"API URL: {args.api_url}")

    # Initialize pipeline
    pipeline = DetectionPipeline(
        model_path=args.model,
        confidence=args.confidence,
        speed_limit=args.speed_limit,
        fps=args.fps,
        api_base_url=args.api_url,
    )

    # Configure
    pipeline.configure(
        lane_boundaries=[(0, 320), (320, 640), (640, 960), (960, 1280)],
        stop_line_y=args.stop_line,
    )

    # Determine source
    source = args.source
    if source.isdigit():
        source = int(source)

    # Process
    results = pipeline.process_video(
        source=source,
        camera_id=args.camera_id,
        display=not args.no_display,
        max_frames=args.max_frames,
    )

    logger.info("=" * 60)
    logger.info("Processing Complete")
    logger.info(f"Frames: {results.get('frames_processed', 0)}")
    logger.info(f"Violations: {results.get('total_violations', 0)}")
    logger.info(f"Plates: {results.get('unique_plates', [])}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
