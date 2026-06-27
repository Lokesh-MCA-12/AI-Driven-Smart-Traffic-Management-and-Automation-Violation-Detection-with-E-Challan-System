# Database Schema Documentation

## Database Type
PostgreSQL 15+

## Schema Details

### 1. `users`
- `id`: UUID (Primary Key)
- `username`: VARCHAR(50) (Unique, Index)
- `email`: VARCHAR(100) (Unique)
- `password_hash`: VARCHAR(255)
- `full_name`: VARCHAR(100)
- `role`: VARCHAR(20) (`admin` or `officer`)
- `is_active`: BOOLEAN
- `created_at`: TIMESTAMP

### 2. `vehicles`
- `id`: UUID (Primary Key)
- `plate_number`: VARCHAR(20) (Unique, Index)
- `vehicle_type`: VARCHAR(30)
- `owner_name`: VARCHAR(100)
- `phone`: VARCHAR(15)
- `email`: VARCHAR(100)
- `address`: TEXT
- `insurance_expiry`: DATE

### 3. `violations`
- `id`: UUID (Primary Key)
- `plate_number`: VARCHAR(20)
- `vehicle_id`: UUID (Foreign Key -> vehicles.id)
- `camera_id`: UUID (Foreign Key -> cameras.id)
- `violation_type`: VARCHAR(30)
- `violation_code`: VARCHAR(10)
- `speed_detected`: FLOAT (Optional)
- `evidence_image`: VARCHAR(500)
- `confidence_score`: FLOAT
- `is_verified`: BOOLEAN
- `verified_by`: UUID (Foreign Key -> users.id)
- `timestamp`: TIMESTAMP

### 4. `challans`
- `id`: UUID (Primary Key)
- `challan_number`: VARCHAR(20) (Unique)
- `violation_id`: UUID (Foreign Key -> violations.id)
- `fine_amount`: NUMERIC(10,2)
- `payment_status`: VARCHAR(20) (`pending`, `paid`, `cancelled`)
- `pdf_path`: VARCHAR(500)
