# Performance Optimization

## AI Pipeline Performance
- **GPU Acceleration**: Utilizes CUDA acceleration for YOLO model execution when available.
- **Multithreading**: Video capture and frame decoding run in a separate thread from detection logic to prevent frame drops.
- **SORT Tracker Efficiency**: The tracking algorithm maintains low execution latency (<5ms per frame).

## Backend & Database Performance
- **Connection Pooling**: Implements SQLAlchemy connection pooling to handle concurrent database queries efficiently.
- **Asynchronous Execution**: Uses async/await syntax to handle request concurrency without blocking threads.
- **Database Indexes**: Indexes on `plate_number`, `timestamp`, and `is_verified` optimize query speeds for analytical lookups.
