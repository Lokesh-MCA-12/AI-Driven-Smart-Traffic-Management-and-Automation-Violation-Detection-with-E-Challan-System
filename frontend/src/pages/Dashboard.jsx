import React, { useState, useEffect, useMemo } from 'react';
import {
    Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend,
    ArcElement, PointElement, LineElement, Filler,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';
import {
    HiOutlineExclamationCircle, HiOutlineDocumentText, HiOutlineCurrencyRupee,
    HiOutlineClock, HiOutlineVideoCamera, HiOutlineShieldCheck, HiOutlineLightningBolt,
    HiOutlineChip
} from 'react-icons/hi';
import simStore from '../simulator';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement, Filler);

const CHART_COLORS = {
    red_light: '#ef4444', no_helmet: '#f59e0b', no_seatbelt: '#3b82f6',
    overspeed: '#8b5cf6', wrong_lane: '#10b981',
};

export default function Dashboard() {
    const [summary, setSummary] = useState(null);
    const [recentViolations, setRecentViolations] = useState([]);
    const [tick, setTick] = useState(0);

    useEffect(() => {
        // Load from simulation store
        setSummary(simStore.getSummary());
        setRecentViolations(simStore.violations.slice(0, 8));

        // Subscribe to live violations
        const unsub = simStore.subscribe((type, data) => {
            if (type === 'violation') {
                setRecentViolations(prev => [data, ...prev.slice(0, 7)]);
                setSummary(simStore.getSummary());
            }
        });

        // Simulate live violation detection every 8-15 seconds
        const interval = setInterval(() => {
            const frames = simStore.getLiveDensityAll();
            frames.forEach(frame => {
                frame.violations.forEach(v => {
                    v.is_verified = false;
                    v.fine_amount = simStore.violations[0]?.fine_amount || 1000;
                    simStore.addLiveViolation(v);
                });
            });
            setTick(t => t + 1);
            setSummary(simStore.getSummary());
        }, randomInterval(8000, 15000));

        return () => { unsub(); clearInterval(interval); };
    }, []);

    // Memoized chart data
    const violationTrend = useMemo(() => simStore.getViolationTrend(14), [tick]);
    const violationsByType = useMemo(() => simStore.getViolationsByType(), [tick]);
    const revenueTrend = useMemo(() => simStore.getRevenueTrend(8), [tick]);

    const statCards = summary ? [
        { label: 'Total Violations', value: summary.total_violations?.toLocaleString(), icon: HiOutlineExclamationCircle, variant: 'danger', change: `+${summary.violations_today} today` },
        { label: 'E-Challans Issued', value: summary.total_challans?.toLocaleString(), icon: HiOutlineDocumentText, variant: 'warning', change: `${summary.pending_challans} pending` },
        { label: 'Revenue Collected', value: `₹${(summary.total_revenue / 1000).toFixed(0)}K`, icon: HiOutlineCurrencyRupee, variant: 'success', change: '+15% this month' },
        { label: 'Pending Challans', value: summary.pending_challans?.toLocaleString(), icon: HiOutlineClock, variant: 'primary', change: `${summary.overdue_challans} overdue` },
        { label: 'Detection Accuracy', value: `${summary.detection_accuracy}%`, icon: HiOutlineChip, variant: 'success', change: 'YOLO26 + SORT' },
        { label: 'Active Cameras', value: summary.active_cameras?.toLocaleString(), icon: HiOutlineVideoCamera, variant: 'success', change: 'All Online' },
    ] : [];

    // Violation trend bar chart
    const trendDates = [...new Set(violationTrend.map(v => v.date))].slice(-14);
    const trendDatasets = Object.entries(CHART_COLORS).map(([type, color]) => ({
        label: type.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
        data: trendDates.map(d => violationTrend.find(v => v.date === d && v.violation_type === type)?.count || 0),
        backgroundColor: color + '80',
        borderColor: color,
        borderWidth: 1, borderRadius: 4,
    }));

    const violationBarData = { labels: trendDates.map(d => d.slice(5)), datasets: trendDatasets };

    // Pie chart
    const pieData = {
        labels: violationsByType.map(v => v.label),
        datasets: [{
            data: violationsByType.map(v => v.count),
            backgroundColor: violationsByType.map(v => (CHART_COLORS[v.type] || '#64748b') + 'cc'),
            borderColor: violationsByType.map(v => CHART_COLORS[v.type] || '#64748b'),
            borderWidth: 2,
        }],
    };

    // Revenue line chart
    const revenueData = {
        labels: revenueTrend.map(r => r.month),
        datasets: [{
            label: 'Revenue (₹)',
            data: revenueTrend.map(r => r.revenue),
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true, tension: 0.4, pointRadius: 4,
            pointBackgroundColor: '#10b981',
        }],
    };

    const chartOptions = {
        responsive: true, maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#94a3b8', font: { family: 'Inter' }, padding: 16 } },
            tooltip: { backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: 1, titleColor: '#f8fafc', bodyColor: '#cbd5e1', padding: 12, cornerRadius: 8 },
        },
        scales: {
            x: { grid: { color: 'rgba(71, 85, 105, 0.2)' }, ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } } },
            y: { grid: { color: 'rgba(71, 85, 105, 0.2)' }, ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } } },
        },
    };

    if (!summary) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="w-12 h-12 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="page-title text-3xl">Dashboard</h1>
                    <p className="text-surface-400 text-sm mt-1">Real-time traffic monitoring overview</p>
                </div>
                <div className="flex items-center gap-3">
                    <span className="badge-info text-[10px]">🔬 Simulator</span>
                    <span className="pulse-dot" />
                    <span className="text-xs text-surface-400">Live</span>
                </div>
            </div>

            {/* Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
                {statCards.map((card, i) => (
                    <div key={i} className={`stat-card stat-card-${card.variant} animate-slide-in`} style={{ animationDelay: `${i * 50}ms` }}>
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-xs text-surface-400 font-medium mb-1">{card.label}</p>
                                <p className="text-2xl font-bold text-white">{card.value}</p>
                            </div>
                            <card.icon className="text-surface-500 flex-shrink-0" size={22} />
                        </div>
                        <p className={`text-xs mt-2 font-medium ${card.change?.startsWith('+') ? 'text-emerald-400' : card.change?.includes('overdue') ? 'text-red-400' : 'text-surface-400'}`}>
                            {card.change}
                        </p>
                    </div>
                ))}
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 glass-card p-6">
                    <h2 className="section-title">Daily Violations (Last 14 Days)</h2>
                    <div className="h-[320px]">
                        <Bar data={violationBarData} options={{ ...chartOptions, plugins: { ...chartOptions.plugins, legend: { ...chartOptions.plugins.legend, position: 'bottom' } } }} />
                    </div>
                </div>

                <div className="glass-card p-6">
                    <h2 className="section-title">Violations by Type</h2>
                    <div className="h-[320px] flex items-center justify-center">
                        <Pie data={pieData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 }, padding: 12 } } } }} />
                    </div>
                </div>
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-card p-6">
                    <h2 className="section-title">Monthly Revenue Trend</h2>
                    <div className="h-[280px]">
                        <Line data={revenueData} options={chartOptions} />
                    </div>
                </div>

                <div className="glass-card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="section-title mb-0">Live Violation Feed</h2>
                        <div className="flex items-center gap-1.5">
                            <HiOutlineLightningBolt className="text-amber-400" size={14} />
                            <span className="text-xs text-amber-400 font-medium">Auto-detecting</span>
                        </div>
                    </div>
                    <div className="space-y-2.5 max-h-[280px] overflow-y-auto pr-1">
                        {recentViolations.map((item, i) => (
                            <div key={`${item.id}-${i}`} className="flex items-center gap-3 p-3 rounded-xl bg-surface-800/50 hover:bg-surface-800 transition-colors animate-slide-in"
                                style={{ animationDelay: `${i * 30}ms` }}>
                                <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: CHART_COLORS[item.violation_type] }} />
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-white font-medium truncate">
                                        {item.violation_type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                                    </p>
                                    <p className="text-xs text-surface-400">
                                        <span className="font-mono">{item.plate_number || '—'}</span>
                                        {item.location ? ` · ${item.location}` : ''}
                                        {item.speed_detected ? ` · ${item.speed_detected} km/h` : ''}
                                    </p>
                                </div>
                                <span className="text-[10px] text-surface-500 flex-shrink-0 font-mono">
                                    {timeSince(item.timestamp)}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* AI Pipeline Status */}
            <div className="glass-card p-6">
                <h2 className="section-title">AI Pipeline Status</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                    {[
                        { label: 'YOLO26 Detector', status: 'Active', color: 'emerald' },
                        { label: 'SORT Tracker', status: 'Active', color: 'emerald' },
                        { label: 'Violation Engine', status: '5 Types', color: 'emerald' },
                        { label: 'ANPR (EasyOCR)', status: 'Active', color: 'emerald' },
                        { label: 'Density Analyzer', status: 'Active', color: 'emerald' },
                        { label: 'Notifications', status: 'Email + SMS', color: 'emerald' },
                    ].map((item, i) => (
                        <div key={i} className="bg-surface-800/50 rounded-xl p-3 flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full bg-${item.color}-400 animate-pulse-slow`} />
                            <div>
                                <p className="text-xs text-surface-300 font-medium">{item.label}</p>
                                <p className={`text-[10px] text-${item.color}-400`}>{item.status}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function timeSince(timestamp) {
    const seconds = Math.floor((Date.now() - new Date(timestamp)) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

function randomInterval(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}
