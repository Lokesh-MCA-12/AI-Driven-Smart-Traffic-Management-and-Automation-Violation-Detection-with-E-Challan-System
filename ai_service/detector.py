"""
Main Detection Pipeline.
Orchestrates Vehicle Detection (YOLO26) → Tracking (SORT) → Density Analysis →
Violation Detection → ANPR (EasyOCR) → Evidence Storage.
"""

import os
import cv2
import time
import logging
import numpy as np
import requests
from datetime import datetime
from typing import Dict, List, Optional

from .vehicle_detector import VehicleDetector, TrafficSignalDetector
from .tracker import Sort
from .violation_detector import ViolationDetector
from .anpr import ANPRModule

logger = logging.getLogger(__name__)


class TrafficDensityAnalyzer:
    """Analyzes traffic density per lane."""

    def __init__(self, lane_boundaries: List[tuple] = None):
        self.lane_boundaries = lane_boundaries or []

    def analyze(self, tracked_vehicles: np.ndarray) -> Dict:
        """
        Analyze traffic density from tracked vehicles.
        
        Returns:
            Dictionary with per-lane and overall density metrics
        """
        total = len(tracked_vehicles)

        if not self.lane_boundaries:
            # No lane config: return overall count
            congestion = min(1.0, total / 50.0)
            green_time = self._adaptive_green_time(total)
            return {
                "total_vehicles": total,
                "congestion_index": round(congestion, 3),
                "avg_waiting_time_sec": round(total * 2.5, 1),
                "recommended_green_time_sec": green_time,
                "lanes": [],
            }

        lanes = {}
        for i, (lx1, lx2) in enumerate(self.lane_boundaries):
            lanes[i] = {"vehicle_count": 0, "lane_id": i}

        # Assign vehicles to lanes
        for trk in tracked_vehicles:
            cx = (trk[0] + trk[2]) / 2
            for i, (lx1, lx2) in enumerate(self.lane_boundaries):
                if lx1 <= cx <= lx2:
                    lanes[i]["vehicle_count"] += 1
                    break

        # Calculate per-lane metrics
        lane_results = []
        for lane_id, data in lanes.items():
            count = data["vehicle_count"]
            congestion = min(1.0, count / 15.0)
            green_time = self._adaptive_green_time(count)
            waiting_time = count * 2.5

            lane_results.append({
                "lane_id": lane_id,
                "vehicle_count": count,
                "congestion_index": round(congestion, 3),
                "avg_waiting_time_sec": round(waiting_time, 1),
                "recommended_green_time_sec": green_time,
            })

        overall_congestion = sum(l["congestion_index"] for l in lane_results) / max(len(lane_results), 1)

        return {
            "total_vehicles": total,
            "congestion_index": round(overall_congestion, 3),
            "avg_waiting_time_sec": round(total * 2.0, 1),
            "recommended_green_time_sec": self._adaptive_green_time(total),
            "lanes": lane_results,
        }

    @staticmethod
    def _adaptive_green_time(vehicle_count: int) -> int:
        """Calculate adaptive green signal time."""
        if vehicle_count <= 5:
            return max(10, 30 - 10)
        elif vehicle_count >= 20:
            extra = ((vehicle_count - 20) // 5 + 1) * 5
            return min(90, 30 + extra)
        else:
            return 30


class DetectionPipeline:
    """
    Main AI processing pipeline.
    
    Processes video frames through:
    1. Vehicle Detection (YOLO26)
    2. Vehicle Tracking (SORT — Kalman Filter + Hungarian Algorithm)
    3. Traffic Density Analysis
    4. Traffic Signal Detection (HSV color analysis)
    5. Violation Detection (5 types)
    6. ANPR (EasyOCR — Automatic Number Plate Recognition)
    """

    def __init__(
        self,
        model_path: str = "yolo26n.pt",
        confidence: float = 0.5,
        speed_limit: float = 60.0,
        fps: int = 15,
        evidence_dir: str = "./evidence",
        api_base_url: str = "http://localhost:8000",
    ):
        """Initialize all pipeline components."""
        # Vehicle detector
        self.detector = VehicleDetector(
            model_path=model_path,
            confidence=confidence,
        )

        # Signal detector
        self.signal_detector = TrafficSignalDetector()

        # Object tracker
        self.tracker = Sort(max_age=5, min_hits=3, iou_threshold=0.3)

        # Density analyzer
        self.density_analyzer = TrafficDensityAnalyzer()

        # Violation detector
        self.violation_detector = ViolationDetector(
            evidence_dir=evidence_dir,
            speed_limit_kmh=speed_limit,
            fps=fps,
        )

        # ANPR module
        self.anpr = ANPRModule()

        # API endpoint
        self.api_base_url = api_base_url

        # Track vehicle types by track_id
        self.vehicle_types: Dict[int, str] = {}

        # Statistics
        self.frame_count = 0
        self.total_violations = 0
        self.total_plates_recognized = 0

        logger.info("Detection pipeline initialized")

    def configure(
        self,
        lane_boundaries: List[tuple] = None,
        stop_line_y: int = 0,
        signal_roi: tuple = None,
    ):
        """Configure pipeline parameters for a specific camera."""
        if lane_boundaries:
            self.density_analyzer.lane_boundaries = lane_boundaries
            self.violation_detector.configure_lanes(lane_boundaries)

        if stop_line_y:
            self.violation_detector.configure_stop_line(stop_line_y)

        self.signal_roi = signal_roi

    def process_frame(self, frame: np.ndarray, camera_id: str = "default") -> Dict:
        """
        Process a single video frame through the complete pipeline.
        
        Returns:
            Dictionary with all processing results
        """
        start_time = time.time()
        self.frame_count += 1

        result = {
            "frame_id": self.frame_count,
            "camera_id": camera_id,
            "timestamp": datetime.now().isoformat(),
            "vehicles_detected": 0,
            "tracked_vehicles": 0,
            "violations_found": 0,
            "violations": [],
            "plates": [],
            "density": {},
            "signal_state": "unknown",
            "processing_time_ms": 0,
        }

        # Step 1: Detect vehicles
        detections = self.detector.detect(frame)
        result["vehicles_detected"] = len(detections)

        if not detections:
            result["processing_time_ms"] = (time.time() - start_time) * 1000
            return result

        # Step 2: Prepare detections for tracker [x1,y1,x2,y2,conf]
        det_array = np.array([
            d["bbox"] + [d["confidence"]] for d in detections
        ])

        # Map detection types
        det_types = {i: d["class_name"] for i, d in enumerate(detections)}

        # Step 3: Track vehicles
        tracked = self.tracker.update(det_array)
        result["tracked_vehicles"] = len(tracked)

        # Store vehicle types for tracked IDs
        for trk in tracked:
            track_id = int(trk[4])
            # Find closest detection to assign type
            cx, cy = (trk[0] + trk[2]) / 2, (trk[1] + trk[3]) / 2
            min_dist = float('inf')
            closest_type = "car"
            for i, d in enumerate(detections):
                dx = (d["bbox"][0] + d["bbox"][2]) / 2
                dy = (d["bbox"][1] + d["bbox"][3]) / 2
                dist = np.sqrt((cx - dx)**2 + (cy - dy)**2)
                if dist < min_dist:
                    min_dist = dist
                    closest_type = d["class_name"]
            self.vehicle_types[track_id] = closest_type

        # Step 4: Traffic density analysis
        density = self.density_analyzer.analyze(tracked)
        result["density"] = density

        # Step 5: Detect traffic signal state
        signal_state = self.signal_detector.detect_signal_state(
            frame,
            getattr(self, 'signal_roi', None),
        )
        result["signal_state"] = signal_state

        # Step 6: Check violations for each tracked vehicle
        all_violations = []
        all_plates = []

        for trk in tracked:
            bbox = trk[:4].tolist()
            track_id = int(trk[4])
            vehicle_type = self.vehicle_types.get(track_id, "car")

            # Get speed from tracker
            tracker_obj = self.tracker.get_tracker_by_id(track_id)
            speed_ppf = tracker_obj.get_speed_pixels_per_frame() if tracker_obj else 0.0

            # Check all violations
            violations = self.violation_detector.check_all_violations(
                frame=frame,
                track_id=track_id,
                bbox=bbox,
                vehicle_type=vehicle_type,
                signal_state=signal_state,
                speed_pixels_per_frame=speed_ppf,
                all_detections=detections,
            )

            if violations:
                all_violations.extend(violations)

                # Run ANPR on vehicles with violations
                plate = self.anpr.process_vehicle(frame, bbox)
                if plate:
                    all_plates.append(plate)
                    # Attach plate to violations
                    for v in violations:
                        v["plate_number"] = plate

        result["violations"] = all_violations
        result["violations_found"] = len(all_violations)
        result["plates"] = all_plates
        self.total_violations += len(all_violations)
        self.total_plates_recognized += len(all_plates)

        # Step 7: Report to backend API
        self._report_to_api(result, camera_id)

        result["processing_time_ms"] = round((time.time() - start_time) * 1000, 2)

        return result

    def _report_to_api(self, result: Dict, camera_id: str):
        """Send processing results to the backend API."""
        try:
            # Report violations
            for violation in result.get("violations", []):
                payload = {
                    "plate_number": violation.get("plate_number"),
                    "camera_id": camera_id,
                    "violation_type": violation["violation_type"],
                    "location": f"Camera {camera_id}",
                    "speed_detected": violation.get("speed_detected"),
                    "speed_limit": violation.get("speed_limit"),
                    "evidence_image": violation.get("evidence_image"),
                    "confidence_score": violation.get("confidence"),
                }
                requests.post(
                    f"{self.api_base_url}/api/violations",
                    json=payload,
                    timeout=5,
                )

            # Report density
            density = result.get("density", {})
            for lane in density.get("lanes", []):
                payload = {
                    "camera_id": camera_id,
                    "lane_id": lane["lane_id"],
                    "vehicle_count": lane["vehicle_count"],
                    "congestion_index": lane["congestion_index"],
                    "avg_waiting_time_sec": lane["avg_waiting_time_sec"],
                    "recommended_green_time_sec": lane["recommended_green_time_sec"],
                }
                requests.post(
                    f"{self.api_base_url}/api/traffic/density",
                    json=payload,
                    timeout=5,
                )

        except Exception as e:
            logger.warning(f"Failed to report to API: {e}")

    def process_video(
        self,
        source,  # Video file path, camera index, or RTSP URL
        camera_id: str = "default",
        display: bool = True,
        max_frames: int = 0,
    ) -> Dict:
        """
        Process a video stream through the pipeline.
        
        Args:
            source: Video source (file path, camera index, or RTSP URL)
            camera_id: Camera identifier
            display: Whether to show annotated frames
            max_frames: Maximum frames to process (0 = unlimited)
        """
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            logger.error(f"Failed to open video source: {source}")
            return {"error": "Failed to open video source"}

        fps = cap.get(cv2.CAP_PROP_FPS) or 15
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logger.info(f"Processing video: {source} ({total_frames} frames, {fps} FPS)")

        frame_count = 0
        total_violations = 0
        all_plates = set()

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                if max_frames > 0 and frame_count > max_frames:
                    break

                # Process frame
                result = self.process_frame(frame, camera_id)
                total_violations += result["violations_found"]
                all_plates.update(result["plates"])

                # Display annotated frame
                if display:
                    annotated = self._annotate_frame(frame, result)
                    cv2.imshow(f"Traffic Monitor - {camera_id}", annotated)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                # Log progress
                if frame_count % 100 == 0:
                    logger.info(
                        f"Processed {frame_count}/{total_frames} frames | "
                        f"Violations: {total_violations} | "
                        f"Plates: {len(all_plates)}"
                    )

        finally:
            cap.release()
            if display:
                cv2.destroyAllWindows()

        return {
            "frames_processed": frame_count,
            "total_violations": total_violations,
            "unique_plates": list(all_plates),
            "camera_id": camera_id,
        }

    def _annotate_frame(self, frame: np.ndarray, result: Dict) -> np.ndarray:
        """Draw annotations on the frame for display."""
        annotated = frame.copy()
        h, w = annotated.shape[:2]

        # Draw info overlay
        overlay = annotated.copy()
        cv2.rectangle(overlay, (10, 10), (350, 140), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, annotated, 0.4, 0, annotated)

        # Text info
        y_offset = 35
        texts = [
            f"Vehicles: {result['vehicles_detected']}",
            f"Tracked: {result['tracked_vehicles']}",
            f"Signal: {result['signal_state'].upper()}",
            f"Violations: {result['violations_found']}",
            f"FPS: {1000 / max(result['processing_time_ms'], 1):.1f}",
        ]

        for text in texts:
            cv2.putText(
                annotated, text, (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
            )
            y_offset += 22

        # Draw stop line if configured
        if self.violation_detector.stop_line_y > 0:
            cv2.line(
                annotated, (0, self.violation_detector.stop_line_y),
                (w, self.violation_detector.stop_line_y),
                (0, 0, 255), 2,
            )

        # Draw lane boundaries
        for lx1, lx2 in self.violation_detector.lane_boundaries:
            cv2.line(annotated, (lx1, 0), (lx1, h), (255, 255, 0), 1)
            cv2.line(annotated, (lx2, 0), (lx2, h), (255, 255, 0), 1)

        return annotated

    def get_stats(self) -> Dict:
        """Get pipeline statistics."""
        return {
            "frames_processed": self.frame_count,
            "total_violations": self.total_violations,
            "total_plates_recognized": self.total_plates_recognized,
            "active_trackers": len(self.tracker.trackers),
        }


def process_frame(frame_path: str, camera_id: str) -> Dict:
    """
    Convenience function to process a single frame.
    Used by the backend API.
    """
    pipeline = DetectionPipeline()
    frame = cv2.imread(frame_path)
    if frame is None:
        return {"error": "Failed to read frame"}
    return pipeline.process_frame(frame, camera_id)
