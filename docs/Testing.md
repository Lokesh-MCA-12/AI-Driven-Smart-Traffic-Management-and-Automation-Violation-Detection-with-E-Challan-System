# Testing Strategy

## Unit and Integration Tests
The project features an automated test suite driven by `pytest`:
- File path: [tests/test_system.py](file:///l:/Projects/Project/AI-Driven%20Smart%20Traffic%20Management%20and%20Automation%20Violation%20Detection%20with%20E-Challan%20System/tests/test_system.py)

### Running the Test Suite
Ensure the virtual environment is active, then run:
```bash
pytest tests/ -v
```

To generate a test coverage report:
```bash
pytest tests/ --cov=ai_service --cov=backend -v
```

### Testing Coverage Includes:
1. **SORT Tracker**: Frame transition tracking, track ID mapping, bounding box overlaps (IoU).
2. **ANPR Cleaning**: Normalization patterns for plate strings.
3. **Violation Engine**: Bounding box crossings, wrong lane boundary overlaps, duplicate warning checks.
4. **REST API**: Authentication scopes, schemas validations, and upload limits.
