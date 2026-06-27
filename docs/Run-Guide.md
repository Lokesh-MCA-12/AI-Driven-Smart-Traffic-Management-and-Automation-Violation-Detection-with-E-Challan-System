# Execution and Operation Guide

## Development Modes

### Backend API Hot Reload
Runs on port 8000. Changes to the `backend/app` directory reload automatically:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Dev Server
Runs on port 5173 (or proxies via Nginx on port 3000):
```bash
npm run dev
```

### Running Tests
Unit and integration tests are managed by pytest:
```bash
pytest tests/ -v
```

## Stop & Restart Procedures

### Docker Services
- **Stop**: `docker-compose down`
- **Restart**: `docker-compose restart`
- **Clean rebuild**: `docker-compose down -v && docker-compose up -d --build`

### Clearing Temporary Files
- **Delete generated evidence uploads**:
  - Windows: `del /s /q backend\evidence\*`
  - Linux: `rm -rf backend/evidence/*`
