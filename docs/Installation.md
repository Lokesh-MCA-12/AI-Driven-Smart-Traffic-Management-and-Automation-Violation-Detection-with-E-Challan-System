# Installation Guide

## Option 1: Docker (Recommended for Quickstart)

1. Clone the repository and navigate to the directory:
   ```bash
   git clone <repo-url>
   cd smart-traffic-management
   ```

2. Setup your environment variables:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and update details (e.g. SMTP credentials, Twilio tokens, Razorpay keys).

4. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```

5. The system will be available at:
   - Dashboard: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`

---

## Option 2: Manual Development Setup

### 1. PostgreSQL Database
- Create a database called `traffic_mgmt`.
- Execute the initialization script:
  ```bash
  psql -U postgres -d traffic_mgmt -f database/init.sql
  ```

### 2. Backend API Setup
```bash
cd backend
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend App Setup
```bash
cd frontend
npm install
npm run dev
```
The application will launch on `http://localhost:5173`.

### 4. Running the AI Service
```bash
cd ai_service
pip install -r requirements.txt
# Run with a local camera
python -m ai_service --source 0 --camera-id CAM-001
# Run with a video file
python -m ai_service --source sample_traffic.mp4 --no-display
```
