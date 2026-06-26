import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Violations from './pages/Violations';
import Challans from './pages/Challans';
import Vehicles from './pages/Vehicles';
import TrafficMonitor from './pages/TrafficMonitor';
import Analytics from './pages/Analytics';
import Login from './pages/Login';

function App() {
    const [user, setUser] = useState(null);
    const [sidebarOpen, setSidebarOpen] = useState(true);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        if (storedUser && token) {
            try {
                setUser(JSON.parse(storedUser));
            } catch {
                localStorage.removeItem('user');
                localStorage.removeItem('token');
            }
        }
    }, []);

    const handleLogin = (userData, token) => {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('token', token);
    };

    const handleLogout = () => {
        setUser(null);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    };

    if (!user) {
        return (
            <>
                <Toaster position="top-right" toastOptions={{
                    style: { background: '#1e293b', color: '#e2e8f0', border: '1px solid #334155' },
                    duration: 3000,
                }} />
                <Login onLogin={handleLogin} />
            </>
        );
    }

    return (
        <Router>
            <Toaster position="top-right" toastOptions={{
                style: { background: '#1e293b', color: '#e2e8f0', border: '1px solid #334155' },
                success: { iconTheme: { primary: '#10b981', secondary: '#1e293b' } },
                error: { iconTheme: { primary: '#ef4444', secondary: '#1e293b' } },
                duration: 4000,
            }} />

            <div className="flex h-screen overflow-hidden bg-surface-950">
                <Sidebar
                    user={user}
                    isOpen={sidebarOpen}
                    onToggle={() => setSidebarOpen(!sidebarOpen)}
                    onLogout={handleLogout}
                />

                <main className={`flex-1 overflow-y-auto transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
                    {/* Simulator banner */}
                    <div className="bg-gradient-to-r from-primary-500/10 to-purple-500/10 border-b border-primary-500/20 px-6 py-2 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <span className="text-sm">🔬</span>
                            <span className="text-xs text-primary-300 font-medium">Simulation Mode</span>
                            <span className="text-xs text-surface-400">— Using same pipeline as production: YOLO26 → SORT → Violation Engine → ANPR (EasyOCR) → E-Challan</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                            <span className="text-xs text-emerald-400">All Systems Online</span>
                        </div>
                    </div>

                    <div className="p-6 max-w-[1600px] mx-auto">
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/violations" element={<Violations />} />
                            <Route path="/challans" element={<Challans />} />
                            <Route path="/vehicles" element={<Vehicles />} />
                            <Route path="/traffic" element={<TrafficMonitor />} />
                            <Route path="/analytics" element={<Analytics />} />
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Routes>
                    </div>
                </main>
            </div>
        </Router>
    );
}

export default App;
