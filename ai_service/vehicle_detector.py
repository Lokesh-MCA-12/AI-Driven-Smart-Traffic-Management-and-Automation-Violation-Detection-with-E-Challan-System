"""
Vehicle Detector using YOLO26 (Ultralytics).
Detects vehicles and classifies them (car, bike, bus, truck).
Also handles traffic signal state detection.

Upgraded to YOLO26 for improved accuracy and speed.
YOLO26 offers better feature extraction.
"""

import os
import logging
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# COCO class IDs for vehicles
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",  # bike
    5: "bus",
    7: "truck",
}

# Alternative labels mapping
VEHICLE_LABELS = {
    "car": "car",
    "motorcycle": "bike",
    "bus": "bus",
    "truck": "truck",
    "motorbike": "bike",
}


class VehicleDetector:
    """
    YOLO26-based vehicle detector (Ultralytics).
    
    Upgraded to YOLO26 for:
    - Better accuracy
    - Faster inference on both GPU and CPU
    - Improved small object detection
    
    Supports GPU acceleration with automatic CPU fallback.
    """

    def __init__(
        self,
        model_path: str = "yolo26n.pt",
        confidence: float = 0.5,
        device: Optional[str] = None,
    ):
        """
        Initialize the vehicle detector.
        
        Args:
            model_path: Path to YOLO26 model weights (e.g., yolo26n.pt, yolo26s.pt)
            confidence: Minimum confidence threshold
            device: Force device ('cuda', 'cpu', or None for auto)
        """
        self.confidence = confidence
        self.model = None
        self.device = device

        try:
            from ultralytics import YOLO

            self.model = YOLO(model_path)

            # Auto-detect GPU
            if device is None:
                try:
                    import torch
                    self.device = "cuda" if torch.cuda.is_available() else "cpu"
                except ImportError:
                    self.device = "cpu"

            logger.info(f"YOLO26 model loaded from {model_path} on {self.device}")

        except Exception as e:
            logger.error(f"Failed to load YOLO26 model: {e}")
            logger.info("Running in simulation mode (YOLO26 not available)")

    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect vehicles in a frame.
        
        Args:
            frame: BGR image as numpy array
            
        Returns:
            List of detections, each with:
            - bbox: [x1, y1, x2, y2]
            - confidence: float
            - class_name: str (car, bike, bus, truck)
            - class_id: int
        """
        if self.model is None:
            return self._simulate_detections(frame)

        start = time.time()

        results = self.model(
            frame,
            conf=self.confidence,
            device=self.device,
            verbose=False,
        )

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                # Filter only vehicle classes
                if cls_id not in VEHICLE_CLASSES:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                class_name = VEHICLE_CLASSES[cls_id]

                detections.append({
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": conf,
                    "class_name": VEHICLE_LABELS.get(class_name, class_name),
                    "class_id": cls_id,
                })

        elapsed = (time.time() - start) * 1000
        logger.debug(f"Detection: {len(detections)} vehicles in {elapsed:.1f}ms")

        return detections

    def detect_all(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect all objects (including persons for helmet/seatbelt detection).
        """
        if self.model is None:
            return []

        results = self.model(
            frame,
            conf=self.confidence,
            device=self.device,
            verbose=False,
        )

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                class_name = result.names.get(cls_id, "unknown")

                detections.append({
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": conf,
                    "class_name": class_name,
                    "class_id": cls_id,
                })

        return detections

    def _simulate_detections(self, frame: np.ndarray) -> List[Dict]:
        """Generate simulated detections for testing without a model."""
        h, w = frame.shape[:2]
        np.random.seed(int(time.time()) % 1000)
        n_vehicles = np.random.randint(2, 8)

        detections = []
        for _ in range(n_vehicles):
            cx = np.random.randint(w // 4, 3 * w // 4)
            cy = np.random.randint(h // 4, 3 * h // 4)
            bw = np.random.randint(60, 200)
            bh = np.random.randint(50, 150)

            x1 = max(0, cx - bw // 2)
            y1 = max(0, cy - bh // 2)
            x2 = min(w, cx + bw // 2)
            y2 = min(h, cy + bh // 2)

            vehicle_type = np.random.choice(["car", "bike", "bus", "truck"], p=[0.5, 0.25, 0.15, 0.1])

            detections.append({
                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                "confidence": np.random.uniform(0.6, 0.99),
                "class_name": vehicle_type,
                "class_id": {"car": 2, "bike": 3, "bus": 5, "truck": 7}[vehicle_type],
            })

        return detections


class TrafficSignalDetector:
    """
    Detects traffic signal state (red, yellow, green) using color analysis.
    """

    def __init__(self):
        # HSV color ranges for traffic lights
        self.color_ranges = {
            "red": {
                "lower1": np.array([0, 100, 100]),
                "upper1": np.array([10, 255, 255]),
                "lower2": np.array([160, 100, 100]),
                "upper2": np.array([180, 255, 255]),
            },
            "yellow": {
                "lower": np.array([20, 100, 100]),
                "upper": np.array([35, 255, 255]),
            },
            "green": {
                "lower": np.array([35, 100, 100]),
                "upper": np.array([85, 255, 255]),
            },
        }

    def detect_signal_state(
        self,
        frame: np.ndarray,
        signal_roi: Optional[Tuple[int, int, int, int]] = None,
    ) -> str:
        """
        Detect the current traffic signal state.
        
        Args:
            frame: BGR image
            signal_roi: (x1, y1, x2, y2) region of interest for the signal
            
        Returns:
            Signal state: 'red', 'yellow', 'green', or 'unknown'
        """
        if signal_roi:
            x1, y1, x2, y2 = signal_roi
            roi = frame[y1:y2, x1:x2]
        else:
            # Default: top portion of frame
            h, w = frame.shape[:2]
            roi = frame[0:h // 4, w // 3:2 * w // 3]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Detect red (two ranges due to HSV wrapping)
        red_mask1 = cv2.inRange(hsv, self.color_ranges["red"]["lower1"], self.color_ranges["red"]["upper1"])
        red_mask2 = cv2.inRange(hsv, self.color_ranges["red"]["lower2"], self.color_ranges["red"]["upper2"])
        red_pixels = cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)

        # Detect yellow
        yellow_mask = cv2.inRange(hsv, self.color_ranges["yellow"]["lower"], self.color_ranges["yellow"]["upper"])
        yellow_pixels = cv2.countNonZero(yellow_mask)

        # Detect green
        green_mask = cv2.inRange(hsv, self.color_ranges["green"]["lower"], self.color_ranges["green"]["upper"])
        green_pixels = cv2.countNonZero(green_mask)

        total = roi.shape[0] * roi.shape[1]
        min_threshold = total * 0.01  # At least 1% coverage

        pixel_counts = {
            "red": red_pixels,
            "yellow": yellow_pixels,
            "green": green_pixels,
        }

        max_color = max(pixel_counts, key=pixel_counts.get)

        if pixel_counts[max_color] > min_threshold:
            return max_color

        return "unknown"
