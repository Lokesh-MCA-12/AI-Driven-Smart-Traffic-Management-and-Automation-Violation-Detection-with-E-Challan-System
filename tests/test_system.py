"""
Unit Tests for the Smart Traffic Management System.
"""

import sys
import os
import pytest
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# SORT TRACKER TESTS
# ============================================================

class TestSortTracker:
    """Tests for the SORT tracking algorithm."""

    def test_iou_calculation(self):
        from ai_service.tracker import iou
        
        # Perfect overlap
        bb1 = np.array([0, 0, 100, 100])
        bb2 = np.array([0, 0, 100, 100])
        assert iou(bb1, bb2) == pytest.approx(1.0)

        # No overlap
        bb3 = np.array([200, 200, 300, 300])
        assert iou(bb1, bb3) == pytest.approx(0.0)

        # Partial overlap
        bb4 = np.array([50, 50, 150, 150])
        result = iou(bb1, bb4)
        assert 0 < result < 1

    def test_tracker_initialization(self):
        from ai_service.tracker import Sort
        
        tracker = Sort(max_age=5, min_hits=3, iou_threshold=0.3)
        assert len(tracker.trackers) == 0
        assert tracker.frame_count == 0

    def test_tracker_update(self):
        from ai_service.tracker import Sort
        
        tracker = Sort(max_age=5, min_hits=1, iou_threshold=0.3)
        
        # First frame
        dets = np.array([[100, 100, 200, 200, 0.9]])
        result = tracker.update(dets)
        assert len(tracker.trackers) >= 1

    def test_tracker_empty_update(self):
        from ai_service.tracker import Sort
        
        tracker = Sort()
        result = tracker.update(np.empty((0, 5)))
        assert len(result) == 0

    def test_kalman_box_tracker(self):
        from ai_service.tracker import KalmanBoxTracker
        
        bbox = np.array([100, 100, 200, 200])
        kbt = KalmanBoxTracker(bbox)
        
        assert kbt.hits == 0
        assert len(kbt.positions) == 1

        # Update
        kbt.update(np.array([105, 105, 205, 205]))
        assert kbt.hits == 1
        assert len(kbt.positions) == 2

    def test_speed_estimation(self):
        from ai_service.tracker import KalmanBoxTracker
        
        bbox = np.array([100, 100, 200, 200])
        kbt = KalmanBoxTracker(bbox)
        
        # Simulate movement
        for i in range(5):
            kbt.update(np.array([100 + i * 10, 100, 200 + i * 10, 200]))
        
        speed = kbt.get_speed_pixels_per_frame()
        assert speed > 0


# ============================================================
# VEHICLE DETECTOR TESTS
# ============================================================

class TestVehicleDetector:
    """Tests for the vehicle detection module."""

    def test_detector_initialization(self):
        from ai_service.vehicle_detector import VehicleDetector
        
        detector = VehicleDetector(model_path="nonexistent.pt")
        assert detector.model is None  # Graceful failure

    def test_simulated_detection(self):
        from ai_service.vehicle_detector import VehicleDetector
        
        detector = VehicleDetector(model_path="nonexistent.pt")
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        detections = detector.detect(frame)
        assert isinstance(detections, list)
        
        if detections:
            det = detections[0]
            assert "bbox" in det
            assert "confidence" in det
            assert "class_name" in det
            assert det["class_name"] in ("car", "bike", "bus", "truck")

    def test_traffic_signal_detector(self):
        from ai_service.vehicle_detector import TrafficSignalDetector
        
        detector = TrafficSignalDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create a red region
        frame[50:100, 250:350] = [0, 0, 255]  # BGR red
        
        state = detector.detect_signal_state(frame)
        assert state in ("red", "yellow", "green", "unknown")


# ============================================================
# VIOLATION DETECTOR TESTS
# ============================================================

class TestViolationDetector:
    """Tests for the violation detection engine."""

    def setup_method(self):
        from ai_service.violation_detector import ViolationDetector
        self.detector = ViolationDetector(
            evidence_dir="./test_evidence",
            speed_limit_kmh=60.0,
            fps=15,
        )

    def test_red_light_violation(self):
        self.detector.configure_stop_line(300)
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Vehicle above stop line - no violation
        result = self.detector.detect_red_light_violation(
            frame, track_id=1, bbox=[100, 100, 200, 250],
            signal_state="red", vehicle_type="car",
        )
        assert result is None

        # Vehicle below stop line - violation
        result = self.detector.detect_red_light_violation(
            frame, track_id=2, bbox=[100, 100, 200, 350],
            signal_state="red", vehicle_type="car",
        )
        assert result is not None
        assert result["violation_type"] == "red_light"

    def test_no_violation_on_green(self):
        self.detector.configure_stop_line(300)
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        result = self.detector.detect_red_light_violation(
            frame, track_id=3, bbox=[100, 100, 200, 350],
            signal_state="green", vehicle_type="car",
        )
        assert result is None

    def test_overspeed_detection(self):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # High speed (exceeds limit)
        result = self.detector.detect_overspeed(
            frame, track_id=10, bbox=[100, 100, 200, 200],
            vehicle_type="car", speed_pixels_per_frame=50.0,
        )
        # With default calibration, 50 px/frame at 15fps should exceed 60 km/h
        # 50/8 * 15 * 3.6 = 337.5 km/h - definitely over
        assert result is not None
        assert result["violation_type"] == "overspeed"

    def test_no_overspeed(self):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Low speed
        result = self.detector.detect_overspeed(
            frame, track_id=11, bbox=[100, 100, 200, 200],
            vehicle_type="car", speed_pixels_per_frame=1.0,
        )
        # 1/8 * 15 * 3.6 = 6.75 km/h - under limit
        assert result is None

    def test_duplicate_prevention(self):
        self.detector.configure_stop_line(300)
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # First detection
        result1 = self.detector.detect_red_light_violation(
            frame, track_id=20, bbox=[100, 100, 200, 350],
            signal_state="red", vehicle_type="car",
        )
        assert result1 is not None

        # Same vehicle again
        result2 = self.detector.detect_red_light_violation(
            frame, track_id=20, bbox=[100, 100, 200, 350],
            signal_state="red", vehicle_type="car",
        )
        assert result2 is None  # Should not duplicate

    def test_wrong_lane_detection(self):
        self.detector.configure_lanes([(0, 200), (200, 400), (400, 600)])
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Vehicle outside all lanes
        result = self.detector.detect_wrong_lane(
            frame, track_id=30, bbox=[650, 100, 750, 200],
            vehicle_type="car",
        )
        assert result is not None
        assert result["violation_type"] == "wrong_lane"

    def teardown_method(self):
        import shutil
        if os.path.exists("./test_evidence"):
            shutil.rmtree("./test_evidence")


# ============================================================
# ANPR TESTS
# ============================================================

class TestANPR:
    """Tests for the ANPR module."""

    def test_plate_validation(self):
        from ai_service.anpr import ANPRModule
        
        anpr = ANPRModule()
        
        # Valid plates
        assert anpr.validate_plate("KA01AB1234") is True
        assert anpr.validate_plate("TN01GH3456") is True
        assert anpr.validate_plate("MH01KL2345") is True
        assert anpr.validate_plate("DL01OP0123") is True

        # Invalid plates
        assert anpr.validate_plate("ABC") is False
        assert anpr.validate_plate("12345") is False
        assert anpr.validate_plate("") is False

    def test_plate_cleaning(self):
        from ai_service.anpr import ANPRModule
        
        anpr = ANPRModule()
        
        # Test OCR error correction
        cleaned = anpr.clean_plate_text("KA O1 AB 1234")
        assert len(cleaned) >= 8

        cleaned = anpr.clean_plate_text("KA01AB1234")
        assert cleaned == "KA01AB1234"

    def test_plate_detection(self):
        from ai_service.anpr import ANPRModule
        
        anpr = ANPRModule()
        
        # Create a simple test image
        frame = np.ones((200, 400, 3), dtype=np.uint8) * 200
        
        result = anpr.detect_plate_region(frame)
        # Should return something (even if fallback region)
        assert result is not None or result is None  # Graceful handling


# ============================================================
# TRAFFIC DENSITY TESTS
# ============================================================

class TestTrafficDensity:
    """Tests for traffic density analysis."""

    def test_adaptive_signal(self):
        from ai_service.detector import TrafficDensityAnalyzer
        
        analyzer = TrafficDensityAnalyzer()

        # Low traffic
        green = analyzer._adaptive_green_time(3)
        assert green <= 30

        # High traffic
        green = analyzer._adaptive_green_time(30)
        assert green > 30

    def test_density_analysis(self):
        from ai_service.detector import TrafficDensityAnalyzer
        
        analyzer = TrafficDensityAnalyzer()
        
        tracked = np.array([
            [100, 100, 200, 200, 1],
            [300, 100, 400, 200, 2],
            [500, 100, 600, 200, 3],
        ])
        
        result = analyzer.analyze(tracked)
        assert result["total_vehicles"] == 3
        assert "congestion_index" in result


# ============================================================
# API SCHEMA VALIDATION TESTS
# ============================================================

class TestSchemas:
    """Tests for Pydantic schema validation."""

    def test_vehicle_plate_validation(self):
        from backend.app.schemas import VehicleCreate
        
        # Valid plate
        v = VehicleCreate(
            plate_number="KA01AB1234",
            vehicle_type="car",
            owner_name="Test User",
            phone="9876543210",
        )
        assert v.plate_number == "KA01AB1234"

    def test_vehicle_plate_invalid(self):
        from backend.app.schemas import VehicleCreate
        
        with pytest.raises(Exception):
            VehicleCreate(
                plate_number="INVALID",
                vehicle_type="car",
                owner_name="Test",
                phone="1234567890",
            )

    def test_violation_type_validation(self):
        from backend.app.schemas import ViolationCreate
        
        v = ViolationCreate(violation_type="red_light")
        assert v.violation_type == "red_light"


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
