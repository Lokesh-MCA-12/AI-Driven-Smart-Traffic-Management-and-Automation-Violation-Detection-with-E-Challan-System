-- ============================================================
-- AI-Driven Smart Traffic Management System
-- Database Schema Initialization
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USERS TABLE (Admin, Officers)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'officer' CHECK (role IN ('admin', 'officer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- VEHICLES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(30) NOT NULL CHECK (vehicle_type IN ('car', 'bike', 'bus', 'truck', 'auto', 'other')),
    owner_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    address TEXT,
    registration_date DATE,
    insurance_expiry DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- TRAFFIC CAMERAS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS cameras (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    zone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    stream_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- TRAFFIC DENSITY LOGS
-- ============================================================
CREATE TABLE IF NOT EXISTS traffic_density (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID REFERENCES cameras(id) ON DELETE SET NULL,
    lane_id INTEGER NOT NULL,
    vehicle_count INTEGER NOT NULL DEFAULT 0,
    congestion_index DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    avg_waiting_time_sec DOUBLE PRECISION DEFAULT 0.0,
    recommended_green_time_sec INTEGER DEFAULT 30,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- VIOLATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS violations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plate_number VARCHAR(20),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    camera_id UUID REFERENCES cameras(id) ON DELETE SET NULL,
    violation_type VARCHAR(30) NOT NULL CHECK (violation_type IN (
        'red_light', 'no_helmet', 'no_seatbelt', 'overspeed', 'wrong_lane'
    )),
    violation_code VARCHAR(10) NOT NULL,
    location VARCHAR(200),
    speed_detected DOUBLE PRECISION,
    speed_limit DOUBLE PRECISION,
    evidence_image VARCHAR(500),
    confidence_score DOUBLE PRECISION,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- CHALLANS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS challans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    challan_number VARCHAR(20) UNIQUE NOT NULL,
    violation_id UUID NOT NULL REFERENCES violations(id) ON DELETE CASCADE,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    fine_amount DECIMAL(10,2) NOT NULL,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN (
        'pending', 'paid', 'overdue', 'disputed', 'cancelled'
    )),
    payment_link VARCHAR(500),
    pdf_path VARCHAR(500),
    notification_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- PAYMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    challan_id UUID NOT NULL REFERENCES challans(id) ON DELETE CASCADE,
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    amount DECIMAL(10,2) NOT NULL,
    transaction_id VARCHAR(100) UNIQUE,
    payment_method VARCHAR(30) CHECK (payment_method IN (
        'online', 'upi', 'card', 'netbanking', 'cash'
    )),
    gateway_response JSONB,
    status VARCHAR(20) DEFAULT 'success' CHECK (status IN (
        'success', 'failed', 'refunded', 'pending'
    )),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- SIGNAL TIMING TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS signal_timings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID REFERENCES cameras(id) ON DELETE SET NULL,
    intersection_name VARCHAR(100),
    lane_count INTEGER DEFAULT 4,
    current_phase INTEGER DEFAULT 1,
    green_time_sec INTEGER DEFAULT 30,
    yellow_time_sec INTEGER DEFAULT 5,
    red_time_sec INTEGER DEFAULT 30,
    is_adaptive BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- ANALYTICS LOGS
-- ============================================================
CREATE TABLE IF NOT EXISTS analytics_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(50) NOT NULL,
    metric_value JSONB NOT NULL,
    zone VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- INDEXES for Performance
-- ============================================================
CREATE INDEX idx_violations_plate ON violations(plate_number);
CREATE INDEX idx_violations_type ON violations(violation_type);
CREATE INDEX idx_violations_timestamp ON violations(timestamp);
CREATE INDEX idx_violations_camera ON violations(camera_id);
CREATE INDEX idx_challans_status ON challans(payment_status);
CREATE INDEX idx_challans_violation ON challans(violation_id);
CREATE INDEX idx_traffic_density_camera ON traffic_density(camera_id);
CREATE INDEX idx_traffic_density_timestamp ON traffic_density(timestamp);
CREATE INDEX idx_vehicles_plate ON vehicles(plate_number);
CREATE INDEX idx_payments_challan ON payments(challan_id);
CREATE INDEX idx_payments_transaction ON payments(transaction_id);

-- ============================================================
-- SEED DATA: Default Admin User
-- Password: admin123 (bcrypt hash)
-- ============================================================
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@smarttraffic.gov.in', '$2b$12$LJ3m4ys3uz4K9PYxQ.4fJeHMwP0Rg5B4q5bD4EeL3bN8TnHJKvVi2', 'System Administrator', 'admin'),
('officer1', 'officer1@smarttraffic.gov.in', '$2b$12$LJ3m4ys3uz4K9PYxQ.4fJeHMwP0Rg5B4q5bD4EeL3bN8TnHJKvVi2', 'Traffic Officer 1', 'officer');

-- ============================================================
-- SEED DATA: Sample Cameras
-- ============================================================
INSERT INTO cameras (camera_name, location, latitude, longitude, zone, stream_url) VALUES
('CAM-001', 'MG Road Junction, Bangalore', 12.9716, 77.5946, 'Zone-A', 'rtsp://localhost:8554/cam001'),
('CAM-002', 'Silk Board Junction, Bangalore', 12.9172, 77.6227, 'Zone-A', 'rtsp://localhost:8554/cam002'),
('CAM-003', 'Hebbal Flyover, Bangalore', 13.0358, 77.5970, 'Zone-B', 'rtsp://localhost:8554/cam003'),
('CAM-004', 'KR Puram Bridge, Bangalore', 13.0012, 77.6869, 'Zone-C', 'rtsp://localhost:8554/cam004');

-- ============================================================
-- SEED DATA: Sample Vehicles
-- ============================================================
INSERT INTO vehicles (plate_number, vehicle_type, owner_name, phone, email, address) VALUES
('KA01AB1234', 'car', 'Rajesh Kumar', '+919876543210', 'rajesh@email.com', '123, MG Road, Bangalore'),
('KA02CD5678', 'bike', 'Priya Sharma', '+919876543211', 'priya@email.com', '456, Jayanagar, Bangalore'),
('KA03EF9012', 'bus', 'BMTC Transport', '+919876543212', 'bmtc@email.com', 'BMTC Depot, Bangalore'),
('TN01GH3456', 'truck', 'Suresh Logistics', '+919876543213', 'suresh@email.com', '789, Anna Nagar, Chennai'),
('KA05IJ7890', 'car', 'Anita Desai', '+919876543214', 'anita@email.com', '321, Koramangala, Bangalore'),
('MH01KL2345', 'bike', 'Amit Patil', '+919876543215', 'amit@email.com', '654, Bandra, Mumbai'),
('KA01MN6789', 'auto', 'Ravi Shankar', '+919876543216', 'ravi@email.com', '987, Malleshwaram, Bangalore'),
('DL01OP0123', 'car', 'Neha Singh', '+919876543217', 'neha@email.com', '147, Connaught Place, Delhi');

-- ============================================================
-- SEED DATA: Signal Timings
-- ============================================================
INSERT INTO signal_timings (camera_id, intersection_name, lane_count, green_time_sec, yellow_time_sec, red_time_sec)
SELECT id, location, 4, 30, 5, 30 FROM cameras;

-- ============================================================
-- VIOLATION TYPE REFERENCE (Fine amounts)
-- ============================================================
CREATE TABLE IF NOT EXISTS violation_types (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    fine_amount DECIMAL(10,2) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical'))
);

INSERT INTO violation_types (code, name, description, fine_amount, severity) VALUES
('RL001', 'Red Light Violation', 'Vehicle crossed stop line during red signal', 1000.00, 'high'),
('NH001', 'No Helmet', 'Two-wheeler rider without helmet', 500.00, 'medium'),
('NS001', 'No Seatbelt', 'Driver not wearing seatbelt', 500.00, 'medium'),
('OS001', 'Overspeeding', 'Vehicle exceeded speed limit', 2000.00, 'critical'),
('WL001', 'Wrong Lane', 'Vehicle in wrong lane or improper lane change', 500.00, 'medium');
