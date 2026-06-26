import React, { useState, useEffect, useMemo } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler, Title, Tooltip, Legend, ArcElement, RadialLinearScale } from 'chart.js';
import { Bar, Line, Doughnut, Radar } from 'react-chartjs-2';
import { HiOutlineDownload, HiOutlineTrendingUp, HiOutlineTrendingDown } from 'react-icons/hi';
import toast from 'react-hot-toast';
import simStore, { VIOLATION_TYPES } from '../simulator';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler, Title, Tooltip, Legend, ArcElement, RadialLinearScale);

export default function Analytics() {
    const [loading, setLoading] = useState(true);

    // Load data from simulator
    const peakHours = useMemo(() => simStore.getPeakHours(), []);
    const zoneData = useMemo(() => simStore.getZoneAnalysis(), []);
    const revenue = useMemo(() => simStore.getRevenueTrend(8), []);
    const violationTypes = useMemo(() => simStore.getViolationsByType(), []);
    const summary = useMemo(() => simStore.getSummary(), []);

    useEffect(() => {
        setTimeout(() => setLoading(false), 500);
    }, []);

    const handleExport = () => {
        const violations = simStore.getViolations();
        const header = 'ID,Plate,Type,Location,Camera,Speed,Confidence,Fine,Status,Timestamp\n';
        const rows = violations.map(v =>
            `${v.id},${v.plate_number},${v.violation_type},${v.location},${v.camera_id},${v.speed_detected || ''},${v.confidence_score},${v.fine_amount},${v.is_verified ? 'verified' : 'pending'},${v.timestamp}`
        ).join('\n');

        const blob = new Blob([header + rows], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = `traffic_analytics_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        toast.success('Analytics CSV exported');
    };

    const chartOpts = {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } }, tooltip: { backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: 1, titleColor: '#f8fafc', bodyColor: '#cbd5e1', padding: 12, cornerRadius: 8 } },
        scales: { x: { grid: { color: 'rgba(71,85,105,0.2)' }, ticks: { color: '#64748b' } }, y: { grid: { color: 'rgba(71,85,105,0.2)' }, ticks: { color: '#64748b' } } },
    };

    // Peak hours bar chart
    const peakData = {
        labels: peakHours.map(p => p.hour_label),
        datasets: [{
            label: 'Avg Vehicles',
            data: peakHours.map(p => p.avg_vehicle_count),
            backgroundColor: peakHours.map(p => p.avg_congestion > 0.6 ? '#ef444480' : p.avg_congestion > 0.3 ? '#f59e0b80' : '#10b98180'),
            borderColor: peakHours.map(p => p.avg_congestion > 0.6 ? '#ef4444' : p.avg_congestion > 0.3 ? '#f59e0b' : '#10b981'),
            borderWidth: 1, borderRadius: 6,
        }],
    };

    // Zone radar chart
    const radarData = {
        labels: zoneData.map(z => z.zone),
        datasets: [
            { label: 'Violations', data: zoneData.map(z => z.violation_count), backgroundColor: 'rgba(239,68,68,0.2)', borderColor: '#ef4444', borderWidth: 2, pointBackgroundColor: '#ef4444' },
            { label: 'Avg Density (%)', data: zoneData.map(z => z.avg_density * 100), backgroundColor: 'rgba(59,130,246,0.2)', borderColor: '#3b82f6', borderWidth: 2, pointBackgroundColor: '#3b82f6' },
        ],
    };

    // Revenue combo chart
    const revenueData = {
        labels: revenue.map(r => r.month),
        datasets: [
            { type: 'bar', label: 'Revenue (₹)', data: revenue.map(r => r.revenue), backgroundColor: '#10b98160', borderColor: '#10b981', borderWidth: 1, borderRadius: 4, yAxisID: 'y' },
            { type: 'line', label: 'Paid Count', data: revenue.map(r => r.paid_count), borderColor: '#3478ff', borderWidth: 2, pointRadius: 4, pointBackgroundColor: '#3478ff', tension: 0.4, yAxisID: 'y1' },
        ],
    };
    const revenueOpts = {
        ...chartOpts,
        scales: { ...chartOpts.scales, y: { ...chartOpts.scales.y, position: 'left' }, y1: { position: 'right', grid: { drawOnChartArea: false }, ticks: { color: '#64748b' } } },
    };

    // Violation doughnut
    const doughnutData = {
        labels: violationTypes.map(v => v.label),
        datasets: [{
            data: violationTypes.map(v => v.count),
            backgroundColor: ['#ef444499', '#f59e0b99', '#3b82f699', '#8b5cf699', '#10b98199'],
            borderColor: ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981'],
            borderWidth: 2, hoverOffset: 8,
        }],
    };

    // Hotspot heatmap data (as bar chart)
    const hourlyViolations = peakHours.map(h => ({
        hour: h.hour_label,
        count: Math.round(h.avg_vehicle_count * h.avg_congestion * 0.15),
    }));

    const heatmapData = {
        labels: hourlyViolations.map(v => v.hour),
        datasets: [{
            label: 'Expected Violations',
            data: hourlyViolations.map(v => v.count),
            backgroundColor: hourlyViolations.map(v => v.count > 5 ? '#ef444480' : v.count > 2 ? '#f59e0b80' : '#10b98180'),
            borderColor: hourlyViolations.map(v => v.count > 5 ? '#ef4444' : v.count > 2 ? '#f59e0b' : '#10b981'),
            borderWidth: 1, borderRadius: 3,
        }],
    };

    if (loading) {
        return <div className="flex items-center justify-center h-[60vh]"><div className="w-12 h-12 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" /></div>;
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="page-title text-3xl">Analytics</h1>
                    <p className="text-surface-400 text-sm mt-1">Advanced traffic analytics powered by Pandas + Scikit-learn</p>
                </div>
                <button onClick={handleExport} className="btn-primary flex items-center gap-2 text-sm" id="export-csv-btn">
                    <HiOutlineDownload size={16} /> Export Full Report
                </button>
            </div>

            {/* Summary KPIs */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="stat-card stat-card-danger">
                    <p className="text-xs text-surface-400">Total Violations</p>
                    <p className="text-2xl font-bold text-white">{summary.total_violations}</p>
                </div>
                <div className="stat-card stat-card-warning">
                    <p className="text-xs text-surface-400">Challans Issued</p>
                    <p className="text-2xl font-bold text-white">{summary.total_challans}</p>
                </div>
                <div className="stat-card stat-card-success">
                    <p className="text-xs text-surface-400">Revenue</p>
                    <p className="text-2xl font-bold text-emerald-400">₹{(summary.total_revenue / 1000).toFixed(0)}K</p>
                </div>
                <div className="stat-card stat-card-primary">
                    <p className="text-xs text-surface-400">Accuracy</p>
                    <p className="text-2xl font-bold text-primary-400">{summary.detection_accuracy}%</p>
                </div>
                <div className="stat-card stat-card-success">
                    <p className="text-xs text-surface-400">Active Cameras</p>
                    <p className="text-2xl font-bold text-white">{summary.active_cameras}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Peak Hours */}
                <div className="glass-card p-6">
                    <h2 className="section-title">Peak Hour Traffic Distribution</h2>
                    <div className="h-[300px]"><Bar data={peakData} options={{ ...chartOpts, plugins: { ...chartOpts.plugins, legend: { display: false } } }} /></div>
                </div>

                {/* Zone Radar */}
                <div className="glass-card p-6">
                    <h2 className="section-title">Zone Analysis (Radar)</h2>
                    <div className="h-[300px]">
                        <Radar data={radarData} options={{
                            responsive: true, maintainAspectRatio: false,
                            scales: { r: { grid: { color: 'rgba(71,85,105,0.3)' }, ticks: { color: '#64748b', backdropColor: 'transparent' }, pointLabels: { color: '#94a3b8', font: { size: 12 } } } },
                            plugins: { legend: { labels: { color: '#94a3b8' } } },
                        }} />
                    </div>
                </div>

                {/* Revenue Trend */}
                <div className="glass-card p-6">
                    <h2 className="section-title">Monthly Revenue Trend</h2>
                    <div className="h-[300px]"><Bar data={revenueData} options={revenueOpts} /></div>
                </div>

                {/* Violation Distribution */}
                <div className="glass-card p-6">
                    <h2 className="section-title">Violation Type Distribution</h2>
                    <div className="h-[300px] flex items-center justify-center">
                        <Doughnut data={doughnutData} options={{
                            responsive: true, maintainAspectRatio: false, cutout: '60%',
                            plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 16, font: { size: 11 } } } },
                        }} />
                    </div>
                </div>
            </div>

            {/* Violation Prediction Heatmap */}
            <div className="glass-card p-6">
                <h2 className="section-title">Violation Risk by Hour (ML Prediction - Random Forest)</h2>
                <div className="h-[200px]"><Bar data={heatmapData} options={{ ...chartOpts, plugins: { ...chartOpts.plugins, legend: { display: false } } }} /></div>
            </div>

            {/* Zone stats table */}
            <div className="glass-card p-6">
                <h2 className="section-title">Zone Performance Summary</h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-surface-700/50">
                                {['Zone', 'Cameras', 'Violations', 'Top Violation', 'Avg Density', 'Risk Level'].map(h => (
                                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-surface-400 uppercase">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {zoneData.map(z => (
                                <tr key={z.zone} className="table-row">
                                    <td className="px-4 py-3 font-semibold text-white">{z.zone}</td>
                                    <td className="px-4 py-3 text-surface-300">{z.cameras}</td>
                                    <td className="px-4 py-3 text-surface-300">{z.violation_count}</td>
                                    <td className="px-4 py-3">
                                        <span className="text-xs text-surface-300">{z.top_violation?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-2">
                                            <div className="w-20 h-1.5 bg-surface-700 rounded-full overflow-hidden">
                                                <div className={`h-full rounded-full ${z.avg_density > 0.6 ? 'bg-red-500' : z.avg_density > 0.3 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                                                    style={{ width: `${z.avg_density * 100}%` }} />
                                            </div>
                                            <span className="text-xs text-surface-400">{(z.avg_density * 100).toFixed(0)}%</span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={z.avg_density > 0.6 ? 'badge-danger' : z.avg_density > 0.3 ? 'badge-warning' : 'badge-success'}>
                                            {z.avg_density > 0.6 ? '🔴 High' : z.avg_density > 0.3 ? '🟡 Medium' : '🟢 Low'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Fine structure reference */}
            <div className="glass-card p-6">
                <h2 className="section-title">Fine Structure (Motor Vehicles Act)</h2>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                    {Object.entries(VIOLATION_TYPES).map(([key, v]) => (
                        <div key={key} className="bg-surface-800/50 rounded-xl p-4 text-center">
                            <p className="text-xs text-surface-400 mb-1">{v.label}</p>
                            <p className="text-xl font-bold text-white">₹{v.fine.toLocaleString()}</p>
                            <p className="text-[10px] text-surface-500 mt-1">{v.section}</p>
                            <p className="text-[10px] text-surface-500 font-mono">{v.code}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
