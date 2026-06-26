# 🚦 AI-Driven Smart Traffic Management and Automated Violation Detection with E-Challan System

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)
[![YOLO26](https://img.shields.io/badge/YOLO26-Ultralytics-purple.svg)](https://ultralytics.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

> An intelligent, AI-powered traffic control and enforcement system that uses computer vision for real-time vehicle detection, traffic density analysis, violation detection, automatic number plate recognition, and automated E-Challan generation.

---

## 📋 Table of Contents

- [System Architecture](#-system-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Running the System](#-running-the-system)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [AI Pipeline](#-ai-pipeline)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Performance](#-performance)

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       NGINX Reverse Proxy                       │
│                    (Rate Limiting, SSL, CORS)                    │
├──────────────────────┬──────────────────────────────────────────┤
│                      │                                          │
│   React Dashboard    │           FastAPI Backend                 │
│   (Port 3000)        │           (Port 8000)                    │
│                      │                                          │
│   • Live Feed        │    • JWT Authentication                  │
│   • Analytics        │    • REST API Endpoints                  │
│   • Violations       │    • Role-based Access                   │
│   • E-Challans       │    • Input Validation                    │
│   • Traffic Monitor  │    • Rate Limiting                       │
│                      │                                          │
├──────────────────────┴──────────────────────────────────────────┤
│                                                                  │
│                    AI Vision Service                              │
│                                                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │ YOLO26   │→ │  SORT    │→ │ Violation│→ │  ANPR    │       │
│   │ Detector │  │ Tracker  │  │ Detector │  │ (EasyOCR)│       │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│   │  PostgreSQL   │  │ Notification │  │ Payment Gateway  │     │
│   │  Database     │  │ (Email/SMS)  │  │ (Razorpay)       │     │
│   └──────────────┘  └──────────────┘  └──────────────────┘     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🎯 AI Vision Module
- **Real-time vehicle detection** using YOLO26 (car, bike, bus, truck)
- **Vehicle tracking** across frames using SORT algorithm with Kalman Filter
- **GPU acceleration** with automatic CPU fallback
- **15+ FPS** processing capability

### 📊 Traffic Density Analysis
- Per-lane vehicle counting
- Congestion index calculation (0.0 – 1.0)
- Average waiting time estimation
- **Adaptive signal timing** that responds to real traffic conditions

### 🚨 Violation Detection (5 Types)
| Violation | Method | Code |
|-----------|--------|------|
| Red Light | Stop-line crossing detection | RL001 |
| No Helmet | Head region CNN analysis | NH001 |
| No Seatbelt | Diagonal strap detection (Hough) | NS001 |
| Overspeeding | Pixel displacement → real-world speed | OS001 |
| Wrong Lane | Boundary zone checking | WL001 |

### 🔍 ANPR (Automatic Number Plate Recognition)
- Contour-based plate region detection
- Image preprocessing (CLAHE, adaptive thresholding)
- EasyOCR text extraction
- OCR error correction (O↔0, I↔1, etc.)
- Indian RTO format validation (e.g., `KA01AB1234`)

### 📄 E-Challan System
- Automated challan generation workflow
- Professional PDF challan with evidence images
- SMS notifications via Twilio
- HTML email with styled template
- Online payment integration (Razorpay)
- Payment status tracking

### 📈 Admin Dashboard
- 6 KPI stat cards with trend indicators
- Violation bar chart (by date and type)
- Revenue line chart (monthly trend)
- Pie/Doughnut charts (violation distribution)
- Radar chart (zone analysis)
- Peak hour analysis
- Live traffic feed with 3-second refresh
- Vehicle search by plate number
- CSV export functionality

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| AI/CV | Python 3.11, OpenCV, YOLO26, EasyOCR |
| Tracking | SORT (Kalman Filter + Hungarian Algorithm) |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL 15 |
| Frontend | React 18, Vite, Tailwind CSS 3.4 |
| Charts | Chart.js 4 |
| Auth | JWT + bcrypt |
| PDF | ReportLab |
| Notifications | SMTP (Email), Twilio (SMS) |
| Deployment | Docker, docker-compose, Nginx |

---

## 📁 Project Structure

```
smart-traffic-management/
├── ai_service/                     # AI Vision Module
│   ├── __init__.py
│   ├── __main__.py                 # CLI entry point
│   ├── vehicle_detector.py         # YOLO26 vehicle detection
│   ├── tracker.py                  # SORT tracking algorithm
│   ├── violation_detector.py       # 5 violation detection types
│   ├── anpr.py                     # Number plate recognition
│   ├── detector.py                 # Main detection pipeline
│   ├── analytics.py                # ML analytics module
│   ├── Dockerfile
│   └── requirements.txt
├── backend/                        # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Settings
│   │   ├── database.py             # Async SQLAlchemy
│   │   ├── models.py               # ORM models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── auth.py                 # JWT authentication
│   │   ├── notifications.py        # Email/SMS service
│   │   ├── challan_pdf.py          # PDF generator
│   │   └── routes/
│   │       ├── auth_routes.py      # Login/Register
│   │       ├── vehicle_routes.py   # Vehicle CRUD
│   │       ├── violation_routes.py # Violations & Challans
│   │       ├── traffic_routes.py   # Traffic density
│   │       ├── analytics_routes.py # Analytics & Export
│   │       └── frame_routes.py     # Frame upload
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                       # React Dashboard
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api.js                  # API client
│   │   ├── index.css               # Design system
│   │   ├── components/
│   │   │   └── Sidebar.jsx
│   │   └── pages/
│   │       ├── Login.jsx
│   │       ├── Dashboard.jsx
│   │       ├── Violations.jsx
│   │       ├── Challans.jsx
│   │       ├── Vehicles.jsx
│   │       ├── TrafficMonitor.jsx
│   │       └── Analytics.jsx
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
├── database/
│   └── init.sql                    # Schema + seed data
├── nginx/
│   └── nginx.conf                  # Reverse proxy config
├── tests/
│   └── test_system.py              # Unit tests
├── docker-compose.yml
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or Docker)
- Git

### Option 1: Docker (Recommended)

```bash
# Clone and enter project
cd smart-traffic-management

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Access:
# - Dashboard: http://localhost:3000
# - API Docs:  http://localhost:8000/docs
# - Database:  localhost:5432
```

### Option 2: Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Database
```bash
# Create database
createdb traffic_mgmt

# Run schema
psql -d traffic_mgmt -f database/init.sql
```

#### AI Service
```bash
cd ai_service
pip install -r requirements.txt

# Run with webcam
python -m ai_service --source 0 --camera-id CAM-001

# Run with video file
python -m ai_service --source traffic_video.mp4 --no-display
```

---

## 📡 API Documentation

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login, get JWT token |
| POST | `/api/auth/register` | Register user (admin only) |
| GET | `/api/auth/me` | Get current profile |

### Vehicles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vehicles` | List vehicles |
| GET | `/api/vehicles/{plate}` | Get by plate number |
| POST | `/api/vehicles` | Register vehicle |
| PUT | `/api/vehicles/{id}` | Update vehicle |

### Violations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/violations` | List with filters |
| POST | `/api/violations` | Record violation |
| POST | `/api/violations/{id}/verify` | Verify violation |

### E-Challans
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/generate-challan` | Generate E-Challan |
| GET | `/api/challans` | List challans |
| POST | `/api/update-payment` | Process payment |

### Traffic
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/traffic/density` | Record density |
| GET | `/api/traffic/density` | Get current density |
| GET | `/api/traffic/signal/{cam}` | Get signal timing |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/summary` | Dashboard summary |
| GET | `/api/analytics/violations/trend` | Violation trend |
| GET | `/api/analytics/violations/by-type` | By type distribution |
| GET | `/api/analytics/revenue/trend` | Revenue trend |
| GET | `/api/analytics/peak-hours` | Peak hour analysis |
| GET | `/api/analytics/zone-analysis` | Zone analytics |
| GET | `/api/analytics/export/csv` | Export CSV |

### Frames
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/frames/upload` | Upload frame for AI |
| GET | `/api/frames/cameras` | List cameras |

> 📖 Full interactive docs at: `http://localhost:8000/docs`

---

## 🗄 Database Schema

### Core Tables

- **users** – Admin and officer accounts (JWT auth)
- **vehicles** – Registered vehicle details with owner info
- **cameras** – CCTV camera locations and stream URLs
- **traffic_density** – Per-lane density readings with timestamps
- **violations** – Detected violations with evidence and confidence
- **challans** – Generated E-Challans with payment status
- **payments** – Payment transactions
- **signal_timings** – Adaptive signal configurations
- **violation_types** – Fine amounts and legal sections
- **analytics_logs** – Historical analytics data

### Fine Structure

| Violation | Fine (₹) | Legal Section |
|-----------|----------|---------------|
| Red Light | ₹1,000 | Sec 119/177 MVA |
| No Helmet | ₹500 | Sec 129 MVA |
| No Seatbelt | ₹500 | Sec 138(3) MVA |
| Overspeeding | ₹2,000 | Sec 183 MVA |
| Wrong Lane | ₹500 | Sec 177 MVA |

---

## 🤖 AI Pipeline

### Data Flow

```
CCTV Frame → YOLO26 Detection → SORT Tracking → Density Analysis
                                      ↓
                              Violation Detection ← Signal State
                                      ↓
                                ANPR (EasyOCR)
                                      ↓
                              Owner DB Lookup
                                      ↓
                            E-Challan Generation
                                      ↓
                          Email + SMS Notification
```

### Speed Calculation Formula

```python
speed_kmh = (pixel_displacement / pixels_per_meter) * fps * 3.6
```

### Adaptive Signal Algorithm

```python
if vehicle_count <= 5:
    green_time = max(10, current - 10)
elif vehicle_count >= 20:
    extra = ((vehicle_count - 20) // 5 + 1) * 5
    green_time = min(90, current + extra)
else:
    green_time = 30  # default
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_system.py::TestSortTracker -v

# Run with coverage
pytest tests/ --cov=ai_service --cov=backend -v
```

### Test Coverage
- ✅ SORT Tracker (IoU, initialization, speed)
- ✅ Vehicle Detector (simulation, signal)
- ✅ Violation Detector (all 5 types + duplicate prevention)
- ✅ ANPR (validation, cleaning)
- ✅ Traffic Density (adaptive signal)
- ✅ Schema Validation (Pydantic)

---

## 🐳 Deployment

### Docker Compose

```bash
# Production build
docker-compose -f docker-compose.yml up -d --build

# View logs
docker-compose logs -f

# Scale AI service
docker-compose up -d --scale ai_service=3
```

### Cloud Deployment (AWS/Azure)

1. Push Docker images to ECR/ACR
2. Deploy with ECS/AKS or EC2/VM
3. Use RDS for PostgreSQL
4. Configure ALB/Application Gateway
5. Set up CloudWatch/Azure Monitor
6. Enable HTTPS with ACM/Azure Certificates

---

## ⚡ Performance Targets

| Metric | Target | Method |
|--------|--------|--------|
| Frame Processing | ≥15 FPS | GPU acceleration |
| Detection Accuracy | ≥85% | YOLO26 fine-tuning |
| OCR Accuracy | ≥90% | Preprocessing pipeline |
| API Response | <300ms | Async + connection pooling |

---

## 🔒 Security

- ✅ JWT authentication with expiry
- ✅ bcrypt password hashing
- ✅ Role-based access control (Admin/Officer)
- ✅ API rate limiting (30 req/s API, 5 req/s uploads)
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS configuration
- ✅ Security headers (X-Frame-Options, XSS, etc.)
- ✅ Environment-based configuration (.env)
- ✅ Nginx reverse proxy

---

## 🎓 Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| officer1 | admin123 | Officer |

> ⚠️ Change these in production!

---

## 📄 License

This project is developed as a final-year engineering project for academic purposes.

---

## 👥 Contributors

- **Project Team** – AI-Driven Smart Traffic Management System
- Built with ❤️ for Smart City initiatives

---

*© 2026 Smart Traffic Management Authority*
