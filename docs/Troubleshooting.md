# Troubleshooting Guide

### 1. Issue: "CUDA out of memory" error in AI Service
- **Cause**: The system does not have enough GPU memory available for the YOLO model size.
- **Solution**: Switch to CPU execution by setting the device flag or utilize a smaller YOLO model variant (e.g., `yolo26n.pt`).

### 2. Issue: "PostgreSQL connection refused" on startup
- **Cause**: The PostgreSQL service is either not running or the connection string in `.env` is incorrect.
- **Solution**: Verify the PostgreSQL status and validate the database URL credentials in the `DATABASE_URL` variable.

### 3. Issue: E-Challan PDF Generation fails
- **Cause**: The ReportLab library lacks permission to write to the designated directories.
- **Solution**: Verify that the `evidence` and `uploads` folders have read and write permissions enabled.
