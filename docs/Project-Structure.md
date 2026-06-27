# Project Structure

```
smart-traffic-management/
├── ai_service/                     # AI Vision Module
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
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Settings
│   │   ├── database.py             # Async SQLAlchemy
│   │   ├── models.py               # ORM models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── auth.py                 # JWT authentication
│   │   ├── notifications.py        # Email/SMS service
│   │   ├── challan_pdf.py          # PDF generator
│   │   └── routes/                 # Endpoint routers
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                       # React Dashboard
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api.js                  # Axios client
│   │   ├── index.css               # Design system
│   │   ├── components/             # Reusable UI parts
│   │   └── pages/                  # Dashboard view templates
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── database/
│   └── init.sql                    # Schema + seed data
├── nginx/
│   └── nginx.conf                  # Nginx proxy config
└── tests/
    └── test_system.py              # Pytest files
```

## Major Directories & Responsibilities
- **ai_service**: Focuses purely on computer vision processing, frames analyzing, object tracking, and posting findings to the REST API.
- **backend**: Serves as the security boundary, handles PostgreSQL operations, parses transactions, issues PDFs, and manages user accounts.
- **frontend**: Provides a responsive management interface for admins and traffic officers.
- **nginx**: Distributes incoming traffic and enforces CORS policies.
