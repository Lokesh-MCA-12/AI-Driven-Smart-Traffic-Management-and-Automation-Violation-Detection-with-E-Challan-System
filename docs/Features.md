# System Features and Capabilities

## Core Modules

### 1. AI Vision Pipeline
- **Vehicle Classification**: Identifies cars, motorcycles, trucks, and buses using fine-tuned YOLO26 object detection models.
- **Kalman Filter Tracking**: Utilizes the Simple Online and Realtime Tracking (SORT) algorithm to map unique IDs to moving vehicles, preventing duplicate counting.
- **Indian License Plate Extraction (ANPR)**: Preprocesses contour areas using CLAHE (Contrast Limited Adaptive Histogram Equalization) and processes them with EasyOCR to parse plates like `KA01AB1234`.

### 2. Traffic Density and Adaptive Signal Control
- Lane-by-lane spatial queue sizing.
- Calculates dynamic congestion metrics.
- Adjusts green light duration (between 10s and 90s) in real-time.

### 3. Automated Violation Enforcer
- **Red Light Violation**: Triggered if a tracked vehicle crosses the static stop-line bounding box while the signal phase is red.
- **No Helmet (2-Wheeler)**: Segments the rider's head using a secondary classification model to verify helmet presence.
- **No Seatbelt**: Uses diagonal Hough line detection and CNN classifiers to scan for seatbelt straps.
- **Overspeeding**: Computes speed by dividing pixel displacement by pixels-per-meter ratios over successive frames.
- **Wrong Lane**: Triggered when a vehicle drives in a designated opposing boundary zone.

### 4. Digital E-Challan Operations
- ReportLab-generated PDF invoices with evidence frames.
- Email delivery via SMTP and SMS alerts via Twilio.
- Online payments via Razorpay.

### 5. Web Admin Dashboard
- Live dashboard displaying KPIs: Total Income, Total Active Members, Violations count, Revenue trends, Radar distribution charts.
- Vehicle history logs and search parameters.
- CSV export reporting tools.
