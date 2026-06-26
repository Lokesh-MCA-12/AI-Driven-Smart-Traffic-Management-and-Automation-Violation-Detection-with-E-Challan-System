"""
ANPR (Automatic Number Plate Recognition) Module.
Detects and reads vehicle number plates using EasyOCR.
Validates against Indian RTO format.
"""

import os
import re
import cv2
import numpy as np
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


# Indian vehicle plate regex patterns
INDIAN_PLATE_PATTERNS = [
    # Standard format: XX00XX0000 (e.g., KA01AB1234)
    r'^[A-Z]{2}\d{2}[A-Z]{1,3}\d{4}$',
    # Older format: XXX0000 (e.g., KA1234)
    r'^[A-Z]{2,3}\d{4}$',
    # BH series (Bharat series): 00BH0000XX
    r'^\d{2}BH\d{4}[A-Z]{2}$',
]


class ANPRModule:
    """
    Automatic Number Plate Recognition.
    
    Pipeline:
    1. Detect number plate region in vehicle crop
    2. Pre-process plate image
    3. OCR text extraction
    4. Clean and validate against Indian formats
    """

    def __init__(self, use_gpu: bool = False):
        """
        Initialize ANPR module.
        
        Args:
            use_gpu: Whether to use GPU for OCR
        """
        self.reader = None
        self.use_gpu = use_gpu

        try:
            import easyocr
            self.reader = easyocr.Reader(
                ['en'],
                gpu=use_gpu,
                verbose=False,
            )
            logger.info(f"EasyOCR initialized (GPU: {use_gpu})")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            logger.info("ANPR will use simulation mode")

    def detect_plate_region(
        self,
        vehicle_crop: np.ndarray,
    ) -> Optional[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """
        Detect number plate region in a vehicle crop.
        
        Uses morphological operations and contour detection
        to find rectangular plate-like regions.
        
        Returns:
            Tuple of (plate_image, (x1, y1, x2, y2)) or None
        """
        if vehicle_crop is None or vehicle_crop.size == 0:
            return None

        h, w = vehicle_crop.shape[:2]
        if h < 20 or w < 20:
            return None

        # Convert to grayscale
        gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)

        # Apply bilateral filter to reduce noise
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)

        # Edge detection
        edges = cv2.Canny(filtered, 30, 200)

        # Dilate to connect edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Sort by area (descending)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        plate_contour = None
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            # Number plates are approximately rectangular (4 corners)
            if len(approx) == 4:
                x, y, cw, ch = cv2.boundingRect(approx)
                aspect_ratio = cw / float(ch) if ch > 0 else 0

                # Indian plates typically have aspect ratio 2:1 to 5:1
                if 1.5 <= aspect_ratio <= 6.0:
                    # Check minimum size
                    if cw > w * 0.1 and ch > h * 0.03:
                        plate_contour = (x, y, x + cw, y + ch)
                        break

        if plate_contour is None:
            # Fallback: use bottom portion of vehicle (common plate location)
            plate_y1 = int(h * 0.65)
            plate_y2 = int(h * 0.95)
            plate_x1 = int(w * 0.2)
            plate_x2 = int(w * 0.8)
            plate_contour = (plate_x1, plate_y1, plate_x2, plate_y2)

        x1, y1, x2, y2 = plate_contour
        plate_img = vehicle_crop[y1:y2, x1:x2]

        if plate_img.size == 0:
            return None

        return plate_img, plate_contour

    def preprocess_plate(self, plate_img: np.ndarray) -> np.ndarray:
        """
        Pre-process plate image for better OCR accuracy.
        
        Steps:
        1. Resize to standard height
        2. Convert to grayscale
        3. Apply adaptive thresholding
        4. Remove noise
        """
        # Resize to standard height
        target_height = 60
        aspect = plate_img.shape[1] / plate_img.shape[0]
        target_width = int(target_height * aspect)
        resized = cv2.resize(plate_img, (target_width, target_height))

        # Convert to grayscale
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2,
        )

        # Morphological opening to remove noise
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        return cleaned

    def read_plate(self, plate_img: np.ndarray) -> Optional[str]:
        """
        Extract text from a plate image using OCR.
        
        Returns:
            Cleaned plate text or None
        """
        if self.reader is None:
            return self._simulate_plate_reading()

        try:
            # Try with original image first
            results = self.reader.readtext(plate_img, detail=1)

            if not results:
                # Try with preprocessed image
                processed = self.preprocess_plate(plate_img)
                results = self.reader.readtext(processed, detail=1)

            if not results:
                return None

            # Combine all detected text
            texts = []
            for (_, text, confidence) in results:
                if confidence > 0.3:
                    texts.append(text)

            raw_text = " ".join(texts)
            cleaned = self.clean_plate_text(raw_text)

            return cleaned if cleaned else None

        except Exception as e:
            logger.error(f"OCR error: {e}")
            return None

    def clean_plate_text(self, text: str) -> str:
        """
        Clean OCR output to extract valid plate number.
        
        Handles common OCR mistakes:
        - O vs 0
        - I vs 1
        - S vs 5
        - B vs 8
        """
        # Remove whitespace and special characters
        cleaned = re.sub(r'[^A-Za-z0-9]', '', text.upper())

        # Common OCR corrections
        corrections = {
            'O': '0', 'I': '1', 'S': '5', 'B': '8',
            'Z': '2', 'G': '6', 'T': '7', 'Q': '0',
        }

        if len(cleaned) >= 6:
            # First 2 chars should be letters (state code)
            result = list(cleaned)

            # Fix state code (positions 0-1: should be letters)
            for i in range(min(2, len(result))):
                if result[i].isdigit():
                    # Reverse corrections for letters
                    rev_corrections = {'0': 'O', '1': 'I', '5': 'S', '8': 'B'}
                    result[i] = rev_corrections.get(result[i], result[i])

            # Fix district code (positions 2-3: should be digits)
            for i in range(2, min(4, len(result))):
                if result[i].isalpha():
                    result[i] = corrections.get(result[i], result[i])

            # Last 4 characters should be digits
            for i in range(max(len(result) - 4, 4), len(result)):
                if result[i].isalpha():
                    result[i] = corrections.get(result[i], result[i])

            cleaned = ''.join(result)

        return cleaned

    def validate_plate(self, plate_text: str) -> bool:
        """Validate plate number against Indian RTO format."""
        if not plate_text or len(plate_text) < 6:
            return False

        for pattern in INDIAN_PLATE_PATTERNS:
            if re.match(pattern, plate_text):
                return True

        return False

    def process_vehicle(
        self,
        frame: np.ndarray,
        bbox: list,
    ) -> Optional[str]:
        """
        Full ANPR pipeline for a detected vehicle.
        
        Steps:
        1. Crop vehicle
        2. Detect plate region
        3. Read plate text
        4. Clean and validate
        
        Returns:
            Validated plate number or None
        """
        x1, y1, x2, y2 = [int(v) for v in bbox]

        # Bounds check
        h, w = frame.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        vehicle_crop = frame[y1:y2, x1:x2]
        if vehicle_crop.size == 0:
            return None

        # Step 1: Detect plate region
        plate_result = self.detect_plate_region(vehicle_crop)
        if plate_result is None:
            return None

        plate_img, _ = plate_result

        # Step 2: Read plate text
        plate_text = self.read_plate(plate_img)
        if plate_text is None:
            return None

        # Step 3: Validate
        if self.validate_plate(plate_text):
            logger.info(f"Valid plate detected: {plate_text}")
            return plate_text
        else:
            logger.debug(f"Invalid plate format: {plate_text}")
            return None

    def _simulate_plate_reading(self) -> Optional[str]:
        """Simulate plate reading for testing."""
        import random
        plates = [
            "KA01AB1234", "KA02CD5678", "TN01GH3456",
            "MH01KL2345", "DL01OP0123", "KA05IJ7890",
        ]
        if random.random() > 0.3:
            return random.choice(plates)
        return None
