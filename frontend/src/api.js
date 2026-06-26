import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// =============================================
// AUTH
// =============================================
export const login = (username, password) =>
    api.post('/auth/login', { username, password });

export const getProfile = () => api.get('/auth/me');

// =============================================
// VEHICLES
// =============================================
export const getVehicleByPlate = (plate) => api.get(`/vehicles/${plate}`);
export const listVehicles = (params) => api.get('/vehicles', { params });
export const createVehicle = (data) => api.post('/vehicles', data);

// =============================================
// VIOLATIONS
// =============================================
export const listViolations = (params) => api.get('/violations', { params });
export const getViolation = (id) => api.get(`/violations/${id}`);
export const verifyViolation = (id) => api.post(`/violations/${id}/verify`);

// =============================================
// CHALLANS
// =============================================
export const listChallans = (params) => api.get('/challans', { params });
export const generateChallan = (violationId) =>
    api.post('/generate-challan', { violation_id: violationId });

// =============================================
// PAYMENTS
// =============================================
export const processPayment = (data) => api.post('/update-payment', data);

// =============================================
// TRAFFIC
// =============================================
export const getTrafficDensity = (params) =>
    api.get('/traffic/density', { params });
export const getDensityHistory = (cameraId, hours = 24) =>
    api.get(`/traffic/density/history`, { params: { camera_id: cameraId, hours } });
export const getSignalTiming = (cameraId) =>
    api.get(`/traffic/signal/${cameraId}`);

// =============================================
// ANALYTICS
// =============================================
export const getAnalyticsSummary = () => api.get('/analytics/summary');
export const getViolationTrend = (days = 30) =>
    api.get('/analytics/violations/trend', { params: { days } });
export const getViolationsByType = () => api.get('/analytics/violations/by-type');
export const getRevenueTrend = (months = 12) =>
    api.get('/analytics/revenue/trend', { params: { months } });
export const getPeakHours = (days = 7) =>
    api.get('/analytics/peak-hours', { params: { days } });
export const getZoneAnalysis = () => api.get('/analytics/zone-analysis');
export const exportCSV = (params) =>
    api.get('/analytics/export/csv', { params, responseType: 'blob' });

// =============================================
// CAMERAS
// =============================================
export const listCameras = () => api.get('/frames/cameras');

// =============================================
// FRAME UPLOAD
// =============================================
export const uploadFrame = (file, cameraId) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/frames/upload?camera_id=${cameraId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};

export default api;
