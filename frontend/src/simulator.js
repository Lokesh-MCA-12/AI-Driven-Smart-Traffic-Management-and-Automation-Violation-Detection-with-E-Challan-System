/**
 * =========================================================
 * SMART TRAFFIC MANAGEMENT SYSTEM — SIMULATION ENGINE
 * =========================================================
 * This module generates realistic simulated data that
 * mirrors EXACTLY what the real-time system would produce.
 * 
 * In production, this is replaced by actual API calls to:
 *   - YOLO26 vehicle detection
 *   - SORT tracker (Kalman Filter + Hungarian Algorithm)
 *   - ANPR (EasyOCR number plate recognition)
 *   - PostgreSQL database
 *   - FastAPI backend
 *   - Twilio SMS + SMTP Email notifications
 * =========================================================
 */

// ============================================================
// SEED DATA — Same as database/init.sql
// ============================================================

const USERS = [
    { id: 1, username: 'admin', password: 'admin123', full_name: 'Admin User', email: 'admin@traffic.gov.in', role: 'admin' },
    { id: 2, username: 'officer1', password: 'admin123', full_name: 'Inspector Rajesh', email: 'rajesh@traffic.gov.in', role: 'officer' },
    { id: 3, username: 'officer2', password: 'admin123', full_name: 'Inspector Priya', email: 'priya@traffic.gov.in', role: 'officer' },
];

const CAMERAS = [
    { id: 'CAM-001', name: 'MG Road Junction', location: 'MG Road & Brigade Road', zone: 'Zone-A', lat: 12.9716, lng: 77.5946, status: 'online', stream_url: 'rtsp://cam1.traffic.gov.in/live' },
    { id: 'CAM-002', name: 'Silk Board Junction', location: 'Silk Board Signal', zone: 'Zone-A', lat: 12.9172, lng: 77.6228, status: 'online', stream_url: 'rtsp://cam2.traffic.gov.in/live' },
    { id: 'CAM-003', name: 'Hebbal Flyover', location: 'Hebbal Outer Ring Road', zone: 'Zone-B', lat: 13.0358, lng: 77.5970, status: 'online', stream_url: 'rtsp://cam3.traffic.gov.in/live' },
    { id: 'CAM-004', name: 'KR Puram Bridge', location: 'KR Puram Junction', zone: 'Zone-C', lat: 13.0012, lng: 77.6836, status: 'online', stream_url: 'rtsp://cam4.traffic.gov.in/live' },
    { id: 'CAM-005', name: 'Electronic City', location: 'Electronic City Phase-1', zone: 'Zone-D', lat: 12.8456, lng: 77.6603, status: 'online', stream_url: 'rtsp://cam5.traffic.gov.in/live' },
    { id: 'CAM-006', name: 'Marathahalli Bridge', location: 'Marathahalli ORR', zone: 'Zone-B', lat: 12.9591, lng: 77.7008, status: 'online', stream_url: 'rtsp://cam6.traffic.gov.in/live' },
];

const VEHICLE_DB = [
    { id: 1, plate_number: 'KA01AB1234', vehicle_type: 'car', owner_name: 'Rajesh Kumar', phone: '+919876543210', email: 'rajesh.kumar@gmail.com', address: '123, MG Road, Bangalore', color: 'Silver', make: 'Maruti Suzuki', model: 'Swift', year: 2022, created_at: '2025-08-15T10:30:00' },
    { id: 2, plate_number: 'KA02CD5678', vehicle_type: 'bike', owner_name: 'Priya Sharma', phone: '+919876543211', email: 'priya.sharma@gmail.com', address: '45, Indiranagar, Bangalore', color: 'Black', make: 'Honda', model: 'Activa', year: 2023, created_at: '2025-09-20T14:15:00' },
    { id: 3, plate_number: 'KA03EF9012', vehicle_type: 'bus', owner_name: 'BMTC Transport Corp', phone: '+919876543212', email: 'bmtc@karnataka.gov.in', address: 'Shantinagar Depot, Bangalore', color: 'Green', make: 'Ashok Leyland', model: 'Viking', year: 2021, created_at: '2025-06-10T09:00:00' },
    { id: 4, plate_number: 'TN01GH3456', vehicle_type: 'truck', owner_name: 'Suresh Logistics Pvt Ltd', phone: '+919876543213', email: 'suresh.logistics@gmail.com', address: '78, Anna Nagar, Chennai', color: 'Blue', make: 'Tata', model: 'LPT 1613', year: 2020, created_at: '2025-10-05T11:45:00' },
    { id: 5, plate_number: 'KA05IJ7890', vehicle_type: 'car', owner_name: 'Anita Desai', phone: '+919876543214', email: 'anita.desai@yahoo.com', address: '56, Koramangala, Bangalore', color: 'White', make: 'Hyundai', model: 'i20', year: 2023, created_at: '2025-11-12T16:30:00' },
    { id: 6, plate_number: 'MH01KL2345', vehicle_type: 'bike', owner_name: 'Amit Patil', phone: '+919876543215', email: 'amit.patil@outlook.com', address: '90, Bandra West, Mumbai', color: 'Red', make: 'Royal Enfield', model: 'Classic 350', year: 2022, created_at: '2025-07-01T08:20:00' },
    { id: 7, plate_number: 'KA01MN6789', vehicle_type: 'auto', owner_name: 'Ravi Shankar', phone: '+919876543216', email: 'ravi.auto@gmail.com', address: '34, Jayanagar, Bangalore', color: 'Yellow', make: 'Bajaj', model: 'RE Auto', year: 2021, created_at: '2025-12-15T12:10:00' },
    { id: 8, plate_number: 'DL01OP0123', vehicle_type: 'car', owner_name: 'Neha Singh', phone: '+919876543217', email: 'neha.singh@gmail.com', address: '12, Connaught Place, New Delhi', color: 'Red', make: 'Kia', model: 'Seltos', year: 2024, created_at: '2026-01-20T10:00:00' },
    { id: 9, plate_number: 'KA04PQ4567', vehicle_type: 'bike', owner_name: 'Vikram Rao', phone: '+919876543218', email: 'vikram.rao@gmail.com', address: '67, Whitefield, Bangalore', color: 'Blue', make: 'Yamaha', model: 'FZ-S', year: 2023, created_at: '2026-01-25T09:30:00' },
    { id: 10, plate_number: 'KA02RS8901', vehicle_type: 'car', owner_name: 'Deepa Nair', phone: '+919876543219', email: 'deepa.nair@gmail.com', address: '23, HSR Layout, Bangalore', color: 'Grey', make: 'Toyota', model: 'Innova Crysta', year: 2022, created_at: '2026-02-01T15:45:00' },
    { id: 11, plate_number: 'TN03TU2345', vehicle_type: 'truck', owner_name: 'Chennai Cargo Services', phone: '+919876543220', email: 'ccs@gmail.com', address: '45, Ambattur, Chennai', color: 'Orange', make: 'Eicher', model: 'Pro 2049', year: 2021, created_at: '2025-05-10T07:00:00' },
    { id: 12, plate_number: 'KA01VW6789', vehicle_type: 'car', owner_name: 'Kavitha Reddy', phone: '+919876543221', email: 'kavitha.r@gmail.com', address: '89, BTM Layout, Bangalore', color: 'Black', make: 'Honda', model: 'City', year: 2024, created_at: '2026-02-10T13:20:00' },
];

const VIOLATION_TYPES = {
    red_light: { code: 'RL001', label: 'Red Light Violation', fine: 1000, section: 'Sec 119/177 MVA' },
    no_helmet: { code: 'NH001', label: 'No Helmet', fine: 500, section: 'Sec 129 MVA' },
    no_seatbelt: { code: 'NS001', label: 'No Seatbelt', fine: 500, section: 'Sec 138(3) MVA' },
    overspeed: { code: 'OS001', label: 'Overspeeding', fine: 2000, section: 'Sec 183 MVA' },
    wrong_lane: { code: 'WL001', label: 'Wrong Lane Driving', fine: 500, section: 'Sec 177 MVA' },
};

const ZONES = ['Zone-A', 'Zone-B', 'Zone-C', 'Zone-D'];

// ============================================================
// UTILITY HELPERS
// ============================================================

let _violationIdCounter = 1000;
let _challanIdCounter = 500;
let _paymentIdCounter = 100;

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomFloat(min, max, decimals = 2) {
    return parseFloat((Math.random() * (max - min) + min).toFixed(decimals));
}

function randomChoice(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function randomDate(daysBack, daysForward = 0) {
    const now = Date.now();
    const back = daysBack * 86400000;
    const fwd = daysForward * 86400000;
    return new Date(now - back + Math.random() * (back + fwd));
}

function formatDate(d) {
    return d.toISOString().split('T')[0];
}

function generateChallanNumber() {
    const date = new Date();
    const y = date.getFullYear().toString().slice(2);
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    const seq = String(_challanIdCounter++).padStart(4, '0');
    return `ECH-${y}${m}${d}-${seq}`;
}

// ============================================================
// GENERATE HISTORICAL VIOLATIONS (last 90 days)
// ============================================================

const _violationTypes = Object.keys(VIOLATION_TYPES);

function generateHistoricalViolations(count = 150) {
    const violations = [];
    for (let i = 0; i < count; i++) {
        const type = randomChoice(_violationTypes);
        const vehicle = randomChoice(VEHICLE_DB);
        const camera = randomChoice(CAMERAS);
        const timestamp = randomDate(90);
        const isVerified = Math.random() > 0.2; // 80% are verified
        const speed = type === 'overspeed' ? randomInt(70, 140) : null;

        violations.push({
            id: _violationIdCounter++,
            plate_number: vehicle.plate_number,
            vehicle_type: vehicle.vehicle_type,
            owner_name: vehicle.owner_name,
            violation_type: type,
            violation_code: VIOLATION_TYPES[type].code,
            location: camera.name,
            camera_id: camera.id,
            zone: camera.zone,
            speed_detected: speed,
            speed_limit: type === 'overspeed' ? 60 : null,
            confidence_score: randomFloat(0.75, 0.98),
            is_verified: isVerified,
            is_on_spot: false,
            evidence_image: `/evidence/${type}_${vehicle.plate_number}_${Date.now()}.jpg`,
            timestamp: timestamp.toISOString(),
            fine_amount: VIOLATION_TYPES[type].fine,
            legal_section: VIOLATION_TYPES[type].section,
        });
    }
    return violations.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}

// ============================================================
// GENERATE HISTORICAL CHALLANS
// ============================================================

function generateHistoricalChallans(violations) {
    const verifiedViolations = violations.filter(v => v.is_verified);
    const challans = [];

    for (let i = 0; i < Math.min(verifiedViolations.length, 100); i++) {
        const v = verifiedViolations[i];
        const issueDate = new Date(v.timestamp);
        issueDate.setHours(issueDate.getHours() + randomInt(1, 24));
        const dueDate = new Date(issueDate);
        dueDate.setDate(dueDate.getDate() + 30);

        const statuses = ['paid', 'pending', 'pending', 'paid', 'paid', 'overdue'];
        const status = randomChoice(statuses);

        challans.push({
            id: _challanIdCounter++,
            challan_number: generateChallanNumber(),
            violation_id: v.id,
            plate_number: v.plate_number,
            owner_name: v.owner_name,
            violation_type: v.violation_type,
            fine_amount: v.fine_amount,
            issue_date: formatDate(issueDate),
            due_date: formatDate(dueDate),
            payment_status: status,
            payment_date: status === 'paid' ? formatDate(new Date(issueDate.getTime() + randomInt(1, 20) * 86400000)) : null,
            payment_method: status === 'paid' ? randomChoice(['UPI', 'Net Banking', 'Card', 'Razorpay']) : null,
            notification_sent: true,
            notification_email: true,
            notification_sms: Math.random() > 0.3,
            created_at: issueDate.toISOString(),
        });
    }

    return challans.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
}

// ============================================================
// GENERATE TRAFFIC DENSITY (last 7 days, per hour)
// ============================================================

function generateDensityHistory(hoursBack = 168) {
    const records = [];
    const now = new Date();

    for (let h = hoursBack; h >= 0; h--) {
        const ts = new Date(now - h * 3600000);
        const hour = ts.getHours();

        for (const cam of CAMERAS) {
            for (let lane = 0; lane < 4; lane++) {
                // Realistic traffic patterns — peak hours
                let baseCount;
                if (hour >= 8 && hour <= 10) baseCount = randomInt(20, 45);       // Morning rush
                else if (hour >= 17 && hour <= 19) baseCount = randomInt(25, 50);  // Evening rush
                else if (hour >= 12 && hour <= 14) baseCount = randomInt(15, 30);  // Lunch
                else if (hour >= 0 && hour <= 5) baseCount = randomInt(1, 8);      // Night
                else baseCount = randomInt(8, 20);                                   // Normal

                const count = Math.max(1, baseCount + randomInt(-5, 5));
                const congestion = Math.min(1.0, count / 40);

                records.push({
                    camera_id: cam.id,
                    camera_name: cam.name,
                    lane_id: lane,
                    vehicle_count: count,
                    congestion_index: parseFloat(congestion.toFixed(3)),
                    avg_waiting_time_sec: parseFloat((count * 2.5).toFixed(1)),
                    recommended_green_time_sec: count > 25 ? Math.min(90, 30 + Math.floor(count / 5) * 5) : count > 5 ? 30 : Math.max(10, 20),
                    timestamp: ts.toISOString(),
                });
            }
        }
    }
    return records;
}

// ============================================================
// LIVE SIMULATION — called every 3 seconds
// ============================================================

function generateLiveFrame(cameraId) {
    const cam = CAMERAS.find(c => c.id === cameraId) || CAMERAS[0];
    const now = new Date();
    const hour = now.getHours();

    // Base vehicle count depends on time of day
    let baseDensity;
    if (hour >= 8 && hour <= 10) baseDensity = randomInt(18, 40);
    else if (hour >= 17 && hour <= 19) baseDensity = randomInt(22, 45);
    else if (hour >= 0 && hour <= 5) baseDensity = randomInt(1, 6);
    else baseDensity = randomInt(8, 22);

    const lanes = Array.from({ length: 4 }, (_, i) => {
        const count = Math.max(0, baseDensity + randomInt(-8, 8));
        const congestion = Math.min(1.0, count / 30);
        return {
            lane_id: i,
            vehicle_count: count,
            congestion_index: parseFloat(congestion.toFixed(3)),
            avg_waiting_time_sec: parseFloat((count * 2.5).toFixed(1)),
            recommended_green_time_sec: count > 20 ? Math.min(90, 30 + Math.floor((count - 20) / 5 + 1) * 5) : count > 5 ? 30 : Math.max(10, 20),
        };
    });

    const totalVehicles = lanes.reduce((s, l) => s + l.vehicle_count, 0);
    const avgCongestion = lanes.reduce((s, l) => s + l.congestion_index, 0) / lanes.length;

    // Signal state cycles: ~30s each
    const signalCycle = Math.floor(Date.now() / 30000) % 3;
    const signal = ['green', 'yellow', 'red'][signalCycle];

    // Simulated detections (what YOLO26 would output)
    const vehicleTypes = ['car', 'car', 'car', 'bike', 'bike', 'bus', 'truck', 'auto'];
    const detections = Array.from({ length: Math.min(totalVehicles, 20) }, (_, i) => ({
        track_id: 1000 + i,
        bbox: [randomInt(50, 1000), randomInt(100, 400), randomInt(150, 200), randomInt(150, 200)],
        class_name: randomChoice(vehicleTypes),
        confidence: randomFloat(0.75, 0.98),
        speed_px_per_frame: randomFloat(1, 15),
    }));

    // Random violations (simulating what violation_detector.py would catch)
    const violations = [];
    if (Math.random() < 0.15) { // ~15% chance per frame tick
        const type = randomChoice(_violationTypes);
        const vehicle = randomChoice(VEHICLE_DB);
        violations.push({
            violation_type: type,
            violation_code: VIOLATION_TYPES[type].code,
            plate_number: vehicle.plate_number,
            vehicle_type: vehicle.vehicle_type,
            owner_name: vehicle.owner_name,
            confidence: randomFloat(0.75, 0.95),
            is_verified: false,
            is_on_spot: false,
            speed_detected: type === 'overspeed' ? randomInt(70, 130) : null,
            speed_limit: type === 'overspeed' ? 60 : null,
            location: cam.name,
            camera_id: cam.id,
            timestamp: now.toISOString(),
        });
    }

    return {
        camera_id: cam.id,
        camera_name: cam.name,
        location: cam.location,
        zone: cam.zone,
        timestamp: now.toISOString(),
        signal_state: signal,
        total_vehicles: totalVehicles,
        avg_congestion: parseFloat(avgCongestion.toFixed(3)),
        lanes,
        detections,
        violations,
        processing_time_ms: randomFloat(45, 120, 1),
        ai_model: 'YOLO26n',
        tracker: 'SORT',
    };
}

// ============================================================
// ANALYTICS GENERATORS
// ============================================================

function generateAnalyticsSummary(violations, challans) {
    const today = formatDate(new Date());
    const todayViolations = violations.filter(v => v.timestamp.startsWith(today));
    const paidChallans = challans.filter(c => c.payment_status === 'paid');
    const totalRevenue = paidChallans.reduce((s, c) => s + c.fine_amount, 0);

    return {
        total_violations: violations.length,
        total_challans: challans.length,
        total_revenue: totalRevenue,
        pending_challans: challans.filter(c => c.payment_status === 'pending').length,
        overdue_challans: challans.filter(c => c.payment_status === 'overdue').length,
        violations_today: todayViolations.length,
        active_cameras: CAMERAS.length,
        detection_accuracy: 92.4,
        avg_processing_time_ms: 67.3,
        plates_recognized_today: Math.floor(todayViolations.length * 0.85),
    };
}

function generateViolationTrend(violations, days = 30) {
    const data = [];
    for (let d = days; d >= 0; d--) {
        const date = new Date();
        date.setDate(date.getDate() - d);
        const dateStr = formatDate(date);

        for (const type of _violationTypes) {
            const dayViolations = violations.filter(v =>
                v.timestamp.startsWith(dateStr) && v.violation_type === type
            );
            // Use actual data if available, otherwise simulate
            data.push({
                date: dateStr,
                violation_type: type,
                count: dayViolations.length || randomInt(1, 12),
            });
        }
    }
    return data;
}

function generateViolationsByType(violations) {
    const labels = { red_light: 'Red Light', no_helmet: 'No Helmet', no_seatbelt: 'No Seatbelt', overspeed: 'Overspeeding', wrong_lane: 'Wrong Lane' };
    return _violationTypes.map(type => ({
        type,
        label: labels[type],
        count: violations.filter(v => v.violation_type === type).length,
        fine: VIOLATION_TYPES[type].fine,
    }));
}

function generateRevenueTrend(challans, months = 8) {
    const data = [];
    for (let m = months; m >= 0; m--) {
        const date = new Date();
        date.setMonth(date.getMonth() - m);
        const monthStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        const monthLabel = date.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' });

        const monthChallans = challans.filter(c => c.issue_date?.startsWith(monthStr.slice(0, 7)));
        const paid = monthChallans.filter(c => c.payment_status === 'paid');
        const pending = monthChallans.filter(c => c.payment_status !== 'paid');

        data.push({
            month: monthLabel,
            month_key: monthStr,
            revenue: paid.reduce((s, c) => s + c.fine_amount, 0) || randomInt(40000, 180000),
            paid_count: paid.length || randomInt(30, 90),
            pending_count: pending.length || randomInt(5, 25),
        });
    }
    return data;
}

function generatePeakHours(densityHistory) {
    const hourlyData = {};
    for (let h = 0; h < 24; h++) {
        hourlyData[h] = { counts: [], congestions: [] };
    }

    densityHistory.forEach(r => {
        const hour = new Date(r.timestamp).getHours();
        hourlyData[hour].counts.push(r.vehicle_count);
        hourlyData[hour].congestions.push(r.congestion_index);
    });

    return Array.from({ length: 24 }, (_, h) => {
        const counts = hourlyData[h].counts;
        const congs = hourlyData[h].congestions;
        const avgCount = counts.length ? counts.reduce((a, b) => a + b, 0) / counts.length : randomInt(5, 15);
        const avgCong = congs.length ? congs.reduce((a, b) => a + b, 0) / congs.length : randomFloat(0.1, 0.5);

        return {
            hour: h,
            hour_label: `${String(h).padStart(2, '0')}:00`,
            avg_vehicle_count: parseFloat(avgCount.toFixed(1)),
            avg_congestion: parseFloat(avgCong.toFixed(3)),
        };
    });
}

function generateZoneAnalysis(violations, densityHistory) {
    return ZONES.map(zone => {
        const zoneViolations = violations.filter(v => v.zone === zone);
        const zoneDensity = densityHistory.filter(d => {
            const cam = CAMERAS.find(c => c.id === d.camera_id);
            return cam?.zone === zone;
        });
        const avgDensity = zoneDensity.length
            ? zoneDensity.reduce((s, d) => s + d.congestion_index, 0) / zoneDensity.length
            : randomFloat(0.2, 0.8);

        return {
            zone,
            violation_count: zoneViolations.length || randomInt(50, 300),
            avg_density: parseFloat(avgDensity.toFixed(3)),
            cameras: CAMERAS.filter(c => c.zone === zone).length,
            top_violation: (() => {
                const counts = {};
                zoneViolations.forEach(v => { counts[v.violation_type] = (counts[v.violation_type] || 0) + 1; });
                return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'red_light';
            })(),
        };
    });
}

// ============================================================
// SIMULATION STATE STORE
// ============================================================

class SimulationStore {
    constructor() {
        this.violations = generateHistoricalViolations(150);
        this.challans = generateHistoricalChallans(this.violations);
        this.densityHistory = generateDensityHistory(168); // 7 days
        this.vehicles = [...VEHICLE_DB];
        this.liveViolationLog = [];
        this._listeners = [];
    }

    // AUTH
    login(username, password) {
        const user = USERS.find(u => u.username === username && u.password === password);
        if (!user) return { error: 'Invalid credentials' };
        const token = 'sim_jwt_' + btoa(JSON.stringify({ id: user.id, role: user.role, exp: Date.now() + 86400000 }));
        return { access_token: token, user: { id: user.id, username: user.username, full_name: user.full_name, email: user.email, role: user.role } };
    }

    getProfile(token) {
        try {
            const payload = JSON.parse(atob(token.replace('sim_jwt_', '')));
            return USERS.find(u => u.id === payload.id);
        } catch { return null; }
    }

    // VEHICLES
    getVehicles(search = '') {
        if (search) {
            const s = search.toUpperCase();
            return this.vehicles.filter(v =>
                v.plate_number.includes(s) || v.owner_name.toUpperCase().includes(s)
            );
        }
        return this.vehicles;
    }

    getVehicleByPlate(plate) {
        return this.vehicles.find(v => v.plate_number === plate.toUpperCase()) || null;
    }

    addVehicle(data) {
        const vehicle = {
            id: this.vehicles.length + 1,
            ...data,
            plate_number: data.plate_number.toUpperCase(),
            created_at: new Date().toISOString(),
        };
        this.vehicles.push(vehicle);
        return vehicle;
    }

    // VIOLATIONS
    getViolations(filters = {}) {
        let result = [...this.violations];
        if (filters.type) result = result.filter(v => v.violation_type === filters.type);
        if (filters.verified === 'true') result = result.filter(v => v.is_verified);
        if (filters.verified === 'false') result = result.filter(v => !v.is_verified);
        if (filters.search) {
            const s = filters.search.toUpperCase();
            result = result.filter(v => v.plate_number?.includes(s) || v.location?.toUpperCase().includes(s));
        }
        return result;
    }

    verifyViolation(id) {
        const v = this.violations.find(x => x.id === id);
        if (v) { v.is_verified = true; return v; }
        return null;
    }

    markOnSpot(id) {
        const v = this.violations.find(x => x.id === id);
        if (v) {
            v.is_verified = true;
            v.is_on_spot = true;
            return v;
        }
        return null;
    }

    // Add a live violation (from simulation ticker)
    addLiveViolation(violation) {
        violation.id = _violationIdCounter++;
        this.violations.unshift(violation);
        this.liveViolationLog.unshift(violation);
        if (this.liveViolationLog.length > 50) this.liveViolationLog.pop();
        this._notify('violation', violation);
        return violation;
    }

    // CHALLANS
    getChallans(filters = {}) {
        let result = [...this.challans];
        if (filters.status) result = result.filter(c => c.payment_status === filters.status);
        if (filters.search) {
            const s = filters.search.toUpperCase();
            result = result.filter(c => c.challan_number?.toUpperCase().includes(s) || c.plate_number?.includes(s));
        }
        return result;
    }

    generateChallan(violationId) {
        const v = this.violations.find(x => x.id === violationId);
        if (!v) return null;

        const challan = {
            id: _challanIdCounter++,
            challan_number: generateChallanNumber(),
            violation_id: v.id,
            plate_number: v.plate_number,
            owner_name: v.owner_name,
            violation_type: v.violation_type,
            fine_amount: v.fine_amount,
            issue_date: formatDate(new Date()),
            due_date: formatDate(new Date(Date.now() + 30 * 86400000)),
            payment_status: 'pending',
            payment_date: null,
            notification_sent: true,
            notification_email: true,
            notification_sms: true,
            created_at: new Date().toISOString(),
        };
        this.challans.unshift(challan);
        this._notify('challan', challan);
        return challan;
    }

    processPayment(challanId, method = 'UPI') {
        const c = this.challans.find(x => x.id === challanId);
        if (c) {
            c.payment_status = 'paid';
            c.payment_date = formatDate(new Date());
            c.payment_method = method;
            return c;
        }
        return null;
    }

    // NOTIFICATIONS — Send/Resend email and SMS for a challan
    sendNotification(challanId, channel) {
        // channel: 'email' or 'sms'
        const challan = this.challans.find(x => x.id === challanId);
        if (!challan) return { success: false, error: 'Challan not found' };

        const vehicle = this.vehicles.find(v => v.plate_number === challan.plate_number);
        if (!vehicle) return { success: false, error: 'Vehicle owner not found' };

        if (channel === 'email') {
            challan.notification_email = true;
            challan.notification_sent = true;
            challan.email_sent_at = new Date().toISOString();
            this._notify('notification', {
                type: 'email',
                challan_number: challan.challan_number,
                recipient: vehicle.email,
                owner_name: vehicle.owner_name,
                status: 'sent',
            });
            return {
                success: true,
                channel: 'email',
                recipient: vehicle.email,
                owner_name: vehicle.owner_name,
                challan_number: challan.challan_number,
                message: `E-Challan email sent to ${vehicle.email}`,
            };
        }

        if (channel === 'sms') {
            challan.notification_sms = true;
            challan.notification_sent = true;
            challan.sms_sent_at = new Date().toISOString();
            this._notify('notification', {
                type: 'sms',
                challan_number: challan.challan_number,
                recipient: vehicle.phone,
                owner_name: vehicle.owner_name,
                status: 'sent',
            });
            return {
                success: true,
                channel: 'sms',
                recipient: vehicle.phone,
                owner_name: vehicle.owner_name,
                challan_number: challan.challan_number,
                message: `SMS sent to ${vehicle.phone}`,
            };
        }

        return { success: false, error: 'Invalid channel' };
    }

    // Send both email and SMS
    sendAllNotifications(challanId) {
        const emailResult = this.sendNotification(challanId, 'email');
        const smsResult = this.sendNotification(challanId, 'sms');
        return { email: emailResult, sms: smsResult };
    }

    // EXPORT — Generate CSV string for challans data
    exportChallansCSV() {
        const header = 'Challan No,Plate Number,Owner Name,Violation Type,Fine Amount (₹),Issue Date,Due Date,Payment Status,Payment Method,Payment Date,Email Sent,SMS Sent\n';
        const rows = this.challans.map(c => {
            const violationLabel = VIOLATION_TYPES[c.violation_type]?.label || c.violation_type;
            return [
                c.challan_number,
                c.plate_number,
                `"${c.owner_name || ''}"`,
                violationLabel,
                c.fine_amount,
                c.issue_date,
                c.due_date,
                c.payment_status,
                c.payment_method || '',
                c.payment_date || '',
                c.notification_email ? 'Yes' : 'No',
                c.notification_sms ? 'Yes' : 'No',
            ].join(',');
        }).join('\n');
        return header + rows;
    }

    // EXPORT — Generate CSV string for violations data
    exportViolationsCSV() {
        const header = 'ID,Plate Number,Owner,Violation Type,Code,Location,Camera,Zone,Speed Detected,Speed Limit,Confidence,Fine (₹),Verified,Timestamp\n';
        const rows = this.violations.map(v => {
            return [
                v.id,
                v.plate_number,
                `"${v.owner_name || ''}"`,
                v.violation_type,
                v.violation_code,
                `"${v.location || ''}"`,
                v.camera_id,
                v.zone,
                v.speed_detected || '',
                v.speed_limit || '',
                ((v.confidence_score || 0) * 100).toFixed(1) + '%',
                v.fine_amount,
                v.is_verified ? 'Yes' : 'No',
                v.timestamp,
            ].join(',');
        }).join('\n');
        return header + rows;
    }

    // TRAFFIC DENSITY
    getLiveDensityAll() {
        return CAMERAS.map(cam => generateLiveFrame(cam.id));
    }

    getLiveDensitySingle(cameraId) {
        return generateLiveFrame(cameraId);
    }

    getDensityHistory(cameraId, hours = 24) {
        const cutoff = new Date(Date.now() - hours * 3600000);
        return this.densityHistory
            .filter(d => d.camera_id === cameraId && new Date(d.timestamp) > cutoff)
            .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    }

    // ANALYTICS
    getSummary() { return generateAnalyticsSummary(this.violations, this.challans); }
    getViolationTrend(days = 30) { return generateViolationTrend(this.violations, days); }
    getViolationsByType() { return generateViolationsByType(this.violations); }
    getRevenueTrend(months = 8) { return generateRevenueTrend(this.challans, months); }
    getPeakHours() { return generatePeakHours(this.densityHistory); }
    getZoneAnalysis() { return generateZoneAnalysis(this.violations, this.densityHistory); }

    // CAMERAS
    getCameras() { return CAMERAS; }

    // EVENT SYSTEM (for live updates)
    subscribe(callback) {
        this._listeners.push(callback);
        return () => { this._listeners = this._listeners.filter(l => l !== callback); };
    }

    _notify(type, data) {
        this._listeners.forEach(cb => cb(type, data));
    }
}

// Singleton for the app
export const simStore = new SimulationStore();
export { CAMERAS, VEHICLE_DB, VIOLATION_TYPES, USERS, ZONES };
export default simStore;
