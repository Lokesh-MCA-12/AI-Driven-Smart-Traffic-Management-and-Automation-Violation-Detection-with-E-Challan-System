"""
Violation Detection Engine.
Detects: Red light, No helmet, No seatbelt, Overspeeding, Wrong lane.
"""

import os
import cv2
import numpy as np
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# FINE AMOUNTS MAP
# ============================================================
VIOLATION_FINES = {
    "red_light": 1000.0,
    "no_helmet": 500.0,
    "no_seatbelt": 500.0,
    "overspeed": 2000.0,
    "wrong_lane": 500.0,
}

VIOLATION_CODES = {
    "red_light": "RL001",
    "no_helmet": "NH001",
    "no_seatbelt": "NS001",
    "overspeed": "OS001",
    "wrong_lane": "WL001",
}


class ViolationDetector:
    """
    Comprehensive violation detection system.
    Analyzes tracked vehicles against traffic rules.
    """

    def __init__(
        self,
        evidence_dir: str = "./evidence",
        speed_limit_kmh: float = 60.0,
        fps: int = 15,
        pixels_per_meter: float = 8.0,
    ):
        """
        Initialize violation detector.
        
        Args:
            evidence_dir: Directory to save violation evidence images
            speed_limit_kmh: Speed limit in km/h
            fps: Video frames per second
            pixels_per_meter: Calibration factor for speed calculation
        """
        self.evidence_dir = evidence_dir
        self.speed_limit_kmh = speed_limit_kmh
        self.fps = fps
        self.pixels_per_meter = pixels_per_meter
        
        os.makedirs(evidence_dir, exist_ok=True)

        # Lane boundaries (configurable per camera)
        # Format: list of (x_start, x_end) tuples for each lane
        self.lane_boundaries: List[Tuple[int, int]] = []

        # Stop line y-coordinate for red light detection
        self.stop_line_y: int = 0

        # Track which vehicles have been flagged (avoid duplicate violations)
        self.flagged_vehicles: Dict[int, set] = {}

    def configure_lanes(self, lanes: List[Tuple[int, int]]):
        """Configure lane boundaries for wrong-lane detection."""
        self.lane_boundaries = sorted(lanes, key=lambda x: x[0])
        logger.info(f"Lane boundaries configured: {self.lane_boundaries}")

    def configure_stop_line(self, y_position: int):
        """Configure stop line position for red-light detection."""
        self.stop_line_y = y_position
        logger.info(f"Stop line configured at y={y_position}")

    def save_evidence(
        self,
        frame: np.ndarray,
        track_id: int,
        violation_type: str,
        bbox: list,
    ) -> str:
        """
        Save violation evidence image with bounding box overlay.
        
        Returns: Path to saved evidence image
        """
        evidence = frame.copy()
        x1, y1, x2, y2 = [int(v) for v in bbox]

        # Draw violation bounding box
        color = (0, 0, 255)  # Red for violations
        cv2.rectangle(evidence, (x1, y1), (x2, y2), color, 3)

        # Add violation label
        label = f"VIOLATION: {violation_type.upper()} [ID:{track_id}]"
        cv2.putText(
            evidence, label, (x1, y1 - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2,
        )

        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            evidence, timestamp, (10, evidence.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2,
        )

        # Save
        filename = f"{violation_type}_{track_id}_{int(time.time())}.jpg"
        filepath = os.path.join(self.evidence_dir, filename)
        cv2.imwrite(filepath, evidence)

        logger.info(f"Evidence saved: {filepath}")
        return filepath

    def was_already_flagged(self, track_id: int, violation_type: str) -> bool:
        """Check if a vehicle was already flagged for this violation type."""
        if track_id not in self.flagged_vehicles:
            return False
        return violation_type in self.flagged_vehicles[track_id]

    def flag_vehicle(self, track_id: int, violation_type: str):
        """Mark a vehicle as flagged for a violation type."""
        if track_id not in self.flagged_vehicles:
            self.flagged_vehicles[track_id] = set()
        self.flagged_vehicles[track_id].add(violation_type)

    # ============================================================
    # A) RED LIGHT VIOLATION
    # ============================================================
    def detect_red_light_violation(
        self,
        frame: np.ndarray,
        track_id: int,
        bbox: list,
        signal_state: str,
        vehicle_type: str,
    ) -> Optional[Dict]:
        """
        Detect red light violation.
        
        A violation occurs when:
        - Signal is RED
        - Vehicle crosses the stop line
        """
        if signal_state != "red":
            return None

        if self.was_already_flagged(track_id, "red_light"):
            return None

        if self.stop_line_y == 0:
            return None

        # Check if vehicle bottom edge crosses stop line
        _, _, _, y2 = bbox
        if y2 > self.stop_line_y:
            evidence_path = self.save_evidence(frame, track_id, "red_light", bbox)
            self.flag_vehicle(track_id, "red_light")

            return {
                "violation_type": "red_light",
                "violation_code": VIOLATION_CODES["red_light"],
                "track_id": track_id,
                "vehicle_type": vehicle_type,
                "evidence_image": evidence_path,
                "confidence": 0.90,
                "timestamp": datetime.now().isoformat(),
            }

        return None

    # ============================================================
    # B) HELMET DETECTION
    # ============================================================
    def detect_no_helmet(
        self,
        frame: np.ndarray,
        track_id: int,
        bbox: list,
        vehicle_type: str,
        all_detections: List[Dict] = None,
    ) -> Optional[Dict]:
        """
        Detect riders without helmets on two-wheelers.
        
        Method:
        1. Only check motorcycles/bikes
        2. Look for person detections overlapping the bike bbox
        3. Analyze head region for helmet presence using color/shape analysis
        """
        if vehicle_type not in ("bike", "motorcycle"):
            return None

        if self.was_already_flagged(track_id, "no_helmet"):
            return None

        x1, y1, x2, y2 = [int(v) for v in bbox]

        # Crop the rider area (upper portion of bike bbox)
        rider_height = int((y2 - y1) * 0.4)
        head_region = frame[max(0, y1 - rider_height):y1, x1:x2]

        if head_region.size == 0:
            return None

        # Simple helmet detection using color analysis
        # Helmets typically have uniform color in the head region
        hsv = cv2.cvtColor(head_region, cv2.COLOR_BGR2HSV)

        # Check for typical helmet colors (dark, uniform regions)
        gray = cv2.cvtColor(head_region, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)

        # Calculate dark pixel ratio (helmets are usually darker)
        dark_ratio = 1 - (np.sum(binary > 0) / max(binary.size, 1))

        # Check color uniformity (helmets have more uniform color)
        std_dev = np.std(gray)

        # Heuristic: No helmet if head region is bright and non-uniform
        # (hair/skin tends to be varied, helmets are uniform and often dark)
        has_helmet = dark_ratio > 0.4 and std_dev < 50

        if not has_helmet:
            evidence_path = self.save_evidence(frame, track_id, "no_helmet", bbox)
            self.flag_vehicle(track_id, "no_helmet")

            return {
                "violation_type": "no_helmet",
                "violation_code": VIOLATION_CODES["no_helmet"],
                "track_id": track_id,
                "vehicle_type": vehicle_type,
                "evidence_image": evidence_path,
                "confidence": 0.75,
                "timestamp": datetime.now().isoformat(),
            }

        return None

    # ============================================================
    # C) SEATBELT DETECTION
    # ============================================================
    def detect_no_seatbelt(
        self,
        frame: np.ndarray,
        track_id: int,
        bbox: list,
        vehicle_type: str,
    ) -> Optional[Dict]:
        """
        Detect drivers not wearing seatbelts in cars.
        
        Method:
        - Only check cars/trucks
        - Crop driver area (left portion of vehicle)
        - Look for diagonal line pattern (seatbelt strap)
        """
        if vehicle_type not in ("car", "truck"):
            return None

        if self.was_already_flagged(track_id, "no_seatbelt"):
            return None

        x1, y1, x2, y2 = [int(v) for v in bbox]

        # Estimate driver area (left side of car, upper portion)
        car_width = x2 - x1
        car_height = y2 - y1
        driver_x1 = x1
        driver_x2 = x1 + car_width // 3
        driver_y1 = y1
        driver_y2 = y1 + car_height // 2

        # Bounds check
        driver_x2 = min(driver_x2, frame.shape[1])
        driver_y2 = min(driver_y2, frame.shape[0])

        driver_region = frame[driver_y1:driver_y2, driver_x1:driver_x2]
        if driver_region.size == 0 or driver_region.shape[0] < 20 or driver_region.shape[1] < 20:
            return None

        # Detect diagonal lines (seatbelt strap)
        gray = cv2.cvtColor(driver_region, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Use Hough Line Transform to find diagonal lines
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30, minLineLength=20, maxLineGap=10)

        has_seatbelt = False
        if lines is not None:
            for line in lines:
                lx1, ly1, lx2, ly2 = line[0]
                # Check for diagonal line (seatbelt angle ~30-60 degrees)
                if lx2 - lx1 != 0:
                    angle = abs(np.arctan2(ly2 - ly1, lx2 - lx1) * 180 / np.pi)
                    if 20 <= angle <= 70:
                        has_seatbelt = True
                        break

        if not has_seatbelt:
            evidence_path = self.save_evidence(frame, track_id, "no_seatbelt", bbox)
            self.flag_vehicle(track_id, "no_seatbelt")

            return {
                "violation_type": "no_seatbelt",
                "violation_code": VIOLATION_CODES["no_seatbelt"],
                "track_id": track_id,
                "vehicle_type": vehicle_type,
                "evidence_image": evidence_path,
                "confidence": 0.65,
                "timestamp": datetime.now().isoformat(),
            }

        return None

    # ============================================================
    # D) OVERSPEED DETECTION
    # ============================================================
    def detect_overspeed(
        self,
        frame: np.ndarray,
        track_id: int,
        bbox: list,
        vehicle_type: str,
        speed_pixels_per_frame: float,
    ) -> Optional[Dict]:
        """
        Detect overspeeding vehicles.
        
        Method:
        1. Get pixel displacement per frame from tracker
        2. Convert to real-world speed: speed_kmh = (px/frame) * fps / px_per_meter * 3.6
        3. Compare with speed limit
        """
        if self.was_already_flagged(track_id, "overspeed"):
            return None

        if speed_pixels_per_frame <= 0:
            return None

        # Convert pixel speed to km/h
        meters_per_frame = speed_pixels_per_frame / self.pixels_per_meter
        meters_per_second = meters_per_frame * self.fps
        speed_kmh = meters_per_second * 3.6

        if speed_kmh > self.speed_limit_kmh:
            evidence_path = self.save_evidence(frame, track_id, "overspeed", bbox)
            self.flag_vehicle(track_id, "overspeed")

            return {
                "violation_type": "overspeed",
                "violation_code": VIOLATION_CODES["overspeed"],
                "track_id": track_id,
                "vehicle_type": vehicle_type,
                "speed_detected": round(speed_kmh, 1),
                "speed_limit": self.speed_limit_kmh,
                "evidence_image": evidence_path,
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat(),
            }

        return None

    # ============================================================
    # E) WRONG LANE DETECTION
    # ============================================================
    def detect_wrong_lane(
        self,
        frame: np.ndarray,
        track_id: int,
        bbox: list,
        vehicle_type: str,
        expected_lane: int = -1,
    ) -> Optional[Dict]:
        """
        Detect vehicles in wrong lanes.
        
        Method:
        1. Determine which lane the vehicle center falls in
        2. Compare with expected lane (based on vehicle direction/type)
        3. Flag if vehicle is in a restricted or wrong lane
        """
        if not self.lane_boundaries:
            return None

        if self.was_already_flagged(track_id, "wrong_lane"):
            return None

        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2

        # Determine current lane
        current_lane = -1
        for i, (lx1, lx2) in enumerate(self.lane_boundaries):
            if lx1 <= center_x <= lx2:
                current_lane = i
                break

        if current_lane == -1:
            # Vehicle is outside all defined lanes
            evidence_path = self.save_evidence(frame, track_id, "wrong_lane", bbox)
            self.flag_vehicle(track_id, "wrong_lane")

            return {
                "violation_type": "wrong_lane",
                "violation_code": VIOLATION_CODES["wrong_lane"],
                "track_id": track_id,
                "vehicle_type": vehicle_type,
                "evidence_image": evidence_path,
                "confidence": 0.80,
                "timestamp": datetime.now().isoformat(),
                "details": "Vehicle outside defined lanes",
            }

        # Check if in expected lane
        if expected_lane >= 0 and current_lane != expected_lane:
            evidence_path = self.save_evidence(frame, track_id, "wrong_lane", bbox)
            self.flag_vehicle(track_id, "wrong_lane")

            return {
                "violation_type": "wrong_lane",
                "violation_code": VIOLATION_CODES["wrong_lane"],
                "track_id": track_id,
                "vehicle_type": vehicle_type,
                "evidence_image": evidence_path,
                "confidence": 0.78,
                "timestamp": datetime.now().isoformat(),
                "details": f"Expected lane {expected_lane}, found in lane {current_lane}",
            }

        return None

    # ============================================================
    # COMPREHENSIVE CHECK
    # ============================================================
    def check_all_violations(
        self,
        frame: np.ndarray,
        track_id: int,
        bbox: list,
        vehicle_type: str,
        signal_state: str = "unknown",
        speed_pixels_per_frame: float = 0.0,
        all_detections: List[Dict] = None,
    ) -> List[Dict]:
        """
        Run all violation checks on a tracked vehicle.
        
        Returns:
            List of detected violations
        """
        violations = []

        # Red light violation
        v = self.detect_red_light_violation(frame, track_id, bbox, signal_state, vehicle_type)
        if v:
            violations.append(v)

        # Helmet detection (bikes only)
        v = self.detect_no_helmet(frame, track_id, bbox, vehicle_type, all_detections)
        if v:
            violations.append(v)

        # Seatbelt detection (cars only)
        v = self.detect_no_seatbelt(frame, track_id, bbox, vehicle_type)
        if v:
            violations.append(v)

        # Overspeed detection
        v = self.detect_overspeed(frame, track_id, bbox, vehicle_type, speed_pixels_per_frame)
        if v:
            violations.append(v)

        # Wrong lane detection
        v = self.detect_wrong_lane(frame, track_id, bbox, vehicle_type)
        if v:
            violations.append(v)

        return violations
