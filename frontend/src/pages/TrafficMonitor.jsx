import React, { useState, useEffect, useRef } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { HiOutlineStatusOnline, HiOutlineRefresh, HiOutlineChip, HiOutlineVideoCamera } from 'react-icons/hi';
import simStore, { CAMERAS } from '../simulator';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler, Title, Tooltip, Legend);

export default function TrafficMonitor() {
    const [liveData, setLiveData] = useState([]);
    const [history, setHistory] = useState([]);
    const [selectedCamera, setSelectedCamera] = useState(null);
    const [lastViolation, setLastViolation] = useState(null);
    const canvasRefs = useRef({});

    useEffect(() => {
        // Initial load
        setLiveData(simStore.getLiveDensityAll());

        // Live data refresh every 3 seconds — simulates real CCTV processing
        const interval = setInterval(() => {
            const data = simStore.getLiveDensityAll();
            setLiveData(data);

            // Update history chart
            setHistory(prev => {
                const now = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                const total = data.reduce((sum, c) => sum + c.total_vehicles, 0);
                return [...prev.slice(-59), { time: now, count: total }];
            });

            // Check for new violations
            data.forEach(cam => {
                cam.violations.forEach(v => {
                    setLastViolation(v);
                    simStore.addLiveViolation({
                        ...v,
                        is_verified: false,
                        fine_amount: 1000,
                    });
                });
            });

            // Draw simulated vehicle detections on canvases
            data.forEach(cam => drawSimulatedDetections(canvasRefs.current[cam.camera_id], cam));
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    const signalColors = { red: 'bg-red-500', yellow: 'bg-yellow-500', green: 'bg-emerald-500' };
    const signalGlow = { red: 'shadow-[0_0_12px_rgba(239,68,68,0.5)]', yellow: 'shadow-[0_0_12px_rgba(234,179,8,0.5)]', green: 'shadow-[0_0_12px_rgba(16,185,129,0.5)]' };
    const congestionColor = (c) => c > 0.7 ? 'text-red-400' : c > 0.4 ? 'text-amber-400' : 'text-emerald-400';
    const congestionBg = (c) => c > 0.7 ? 'from-red-500/20 to-red-500/5' : c > 0.4 ? 'from-amber-500/20 to-amber-500/5' : 'from-emerald-500/20 to-emerald-500/5';

    const liveChartData = {
        labels: history.map(h => h.time),
        datasets: [{
            label: 'Total Vehicles (All Cameras)',
            data: history.map(h => h.count),
            borderColor: '#3478ff', backgroundColor: 'rgba(52, 120, 255, 0.1)',
            fill: true, tension: 0.4, pointRadius: 1,
        }],
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="page-title text-3xl">Traffic Monitor</h1>
                    <p className="text-surface-400 text-sm mt-1">Real-time CCTV processing with YOLO26 + SORT tracking</p>
                </div>
                <div className="flex items-center gap-3">
                    <span className="badge-info text-[10px]">🔬 Simulated Pipeline</span>
                    <span className="pulse-dot" /><span className="text-xs text-surface-400">Live (3s cycle)</span>
                </div>
            </div>

            {/* Live violation alert */}
            {lastViolation && (
                <div className="glass-card p-4 border-l-4 border-red-500 animate-slide-in">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center animate-pulse">
                            <span className="text-red-400 text-lg">⚠️</span>
                        </div>
                        <div>
                            <p className="text-sm font-semibold text-white">
                                {lastViolation.violation_type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} Detected!
                            </p>
                            <p className="text-xs text-surface-400">
                                {lastViolation.plate_number} · {lastViolation.location}
                                {lastViolation.speed_detected ? ` · ${lastViolation.speed_detected} km/h` : ''}
                            </p>
                        </div>
                        <span className="ml-auto text-xs text-surface-500">ANPR: {lastViolation.plate_number}</span>
                    </div>
                </div>
            )}

            {/* Live chart */}
            <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="section-title mb-0">Live Vehicle Count (All Cameras)</h2>
                    <div className="flex items-center gap-2 text-xs text-surface-400">
                        <HiOutlineChip size={14} />
                        Processing: ~{liveData[0]?.processing_time_ms?.toFixed(0) || 67}ms / frame
                    </div>
                </div>
                <div className="h-[180px]">
                    <Line data={liveChartData} options={{
                        responsive: true, maintainAspectRatio: false, animation: { duration: 500 },
                        scales: { x: { grid: { color: 'rgba(71,85,105,0.2)' }, ticks: { color: '#64748b', font: { size: 9 }, maxRotation: 0 } }, y: { grid: { color: 'rgba(71,85,105,0.2)' }, ticks: { color: '#64748b' } } },
                        plugins: { legend: { display: false } },
                    }} />
                </div>
            </div>

            {/* Camera cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {liveData.map(cam => (
                    <div key={cam.camera_id} className="glass-card-hover overflow-hidden">
                        {/* Simulated video feed */}
                        <div className="relative bg-surface-900 aspect-video">
                            <canvas
                                ref={el => canvasRefs.current[cam.camera_id] = el}
                                className="w-full h-full"
                                width={640}
                                height={360}
                            />
                            {/* Overlay info */}
                            <div className="absolute top-3 left-3 bg-black/60 backdrop-blur-sm rounded-lg px-3 py-2">
                                <div className="flex items-center gap-2">
                                    <HiOutlineVideoCamera className="text-red-400" size={14} />
                                    <span className="text-xs text-white font-medium">{cam.camera_name}</span>
                                    <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                                    <span className="text-[10px] text-surface-300">REC</span>
                                </div>
                            </div>
                            <div className="absolute top-3 right-3 bg-black/60 backdrop-blur-sm rounded-lg px-3 py-2">
                                <span className="text-xs text-surface-300 font-mono">
                                    {new Date().toLocaleTimeString('en-IN')}
                                </span>
                            </div>
                            <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-sm rounded-lg px-3 py-2 flex items-center gap-2">
                                <span className="text-xs text-surface-300">YOLO26</span>
                                <span className="text-[10px] text-emerald-400">●</span>
                                <span className="text-xs text-surface-300">SORT</span>
                                <span className="text-[10px] text-emerald-400">●</span>
                                <span className="text-xs text-surface-300">{cam.total_vehicles} vehicles</span>
                            </div>
                            <div className="absolute bottom-3 right-3 flex items-center gap-1.5">
                                <span className={`w-4 h-4 rounded-full ${signalColors[cam.signal_state]} ${signalGlow[cam.signal_state]}`} />
                            </div>
                        </div>

                        {/* Camera info */}
                        <div className="p-5">
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h3 className="font-bold text-white">{cam.camera_name}</h3>
                                    <p className="text-xs text-surface-400">{cam.location} · {cam.zone}</p>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className={`w-3 h-3 rounded-full ${signalColors[cam.signal_state]} animate-pulse-slow`} />
                                    <span className="text-xs text-surface-400 uppercase font-semibold">{cam.signal_state}</span>
                                </div>
                            </div>

                            {/* Overall stats */}
                            <div className={`bg-gradient-to-r ${congestionBg(cam.avg_congestion)} rounded-xl p-4 mb-4`}>
                                <div className="flex justify-between items-center">
                                    <div>
                                        <p className="text-xs text-surface-400">Total Vehicles</p>
                                        <p className="text-2xl font-bold text-white">{cam.total_vehicles}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-xs text-surface-400">Congestion</p>
                                        <p className={`text-2xl font-bold ${congestionColor(cam.avg_congestion)}`}>
                                            {(cam.avg_congestion * 100).toFixed(0)}%
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Lane details */}
                            <div className="grid grid-cols-2 gap-2">
                                {cam.lanes.map(lane => (
                                    <div key={lane.lane_id} className="bg-surface-800/50 rounded-lg p-3">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-xs text-surface-400">Lane {lane.lane_id + 1}</span>
                                            <span className="text-xs font-mono text-surface-300">{lane.vehicle_count} 🚗</span>
                                        </div>
                                        <div className="w-full h-1.5 bg-surface-700 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full transition-all duration-1000 ${lane.congestion_index > 0.7 ? 'bg-red-500' : lane.congestion_index > 0.4 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                                                style={{ width: `${lane.congestion_index * 100}%` }}
                                            />
                                        </div>
                                        <div className="flex justify-between mt-1 text-[10px] text-surface-500">
                                            <span>Wait: {lane.avg_waiting_time_sec.toFixed(0)}s</span>
                                            <span>Green: {lane.recommended_green_time_sec}s</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ============================================================
// SIMULATED CCTV CANVAS DRAWING
// Mimics what YOLO26 bounding boxes and SORT tracking IDs
// would look like on a real CCTV feed
// ============================================================

function drawSimulatedDetections(canvas, camData) {
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    // Draw dark road background
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, w, h);

    // Draw road markings
    ctx.strokeStyle = '#333355';
    ctx.lineWidth = 2;

    // Lane dividers
    const lanes = 4;
    for (let i = 1; i < lanes; i++) {
        const x = (w / lanes) * i;
        ctx.setLineDash([20, 15]);
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
    }
    ctx.setLineDash([]);

    // Draw stop line
    ctx.strokeStyle = '#cc0000';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, h * 0.7);
    ctx.lineTo(w, h * 0.7);
    ctx.stroke();

    // Draw simulated vehicles with YOLO26 bounding boxes
    const vehicleEmojis = { car: '■', bike: '▪', bus: '▬', truck: '▬', auto: '▪' };
    const colors = ['#00ff88', '#00bbff', '#ff6644', '#ffaa00', '#aa66ff'];

    camData.detections?.forEach((det, i) => {
        const laneWidth = w / lanes;
        const lane = i % lanes;
        const x = lane * laneWidth + Math.random() * (laneWidth - 60) + 10;
        const y = 30 + (i * 42) % (h - 80);
        const bw = det.class_name === 'bus' || det.class_name === 'truck' ? 70 : det.class_name === 'bike' ? 25 : 45;
        const bh = det.class_name === 'bus' || det.class_name === 'truck' ? 35 : det.class_name === 'bike' ? 20 : 28;

        const color = colors[i % colors.length];

        // Detection bounding box
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, bw, bh);

        // Fill vehicle
        ctx.fillStyle = color + '30';
        ctx.fillRect(x, y, bw, bh);

        // Label: "car 0.92 | ID:1003"
        const label = `${det.class_name} ${det.confidence.toFixed(2)}`;
        ctx.fillStyle = color;
        ctx.font = '9px monospace';
        const textWidth = ctx.measureText(label).width;
        ctx.fillStyle = '#000000cc';
        ctx.fillRect(x, y - 12, textWidth + 6, 12);
        ctx.fillStyle = color;
        ctx.fillText(label, x + 3, y - 2);

        // Track ID
        const idLabel = `ID:${det.track_id}`;
        ctx.fillStyle = '#000000cc';
        ctx.fillRect(x + bw - 30, y - 12, 30, 12);
        ctx.fillStyle = '#ffffff';
        ctx.font = '8px monospace';
        ctx.fillText(idLabel, x + bw - 28, y - 3);
    });

    // Signal state indicator
    const sigColor = { red: '#ff3333', yellow: '#ffcc00', green: '#33ff88' }[camData.signal_state] || '#666';
    ctx.fillStyle = '#000000aa';
    ctx.fillRect(w - 80, 10, 70, 22);
    ctx.fillStyle = sigColor;
    ctx.beginPath();
    ctx.arc(w - 65, 21, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 9px sans-serif';
    ctx.fillText(camData.signal_state?.toUpperCase(), w - 55, 25);

    // Frame info
    ctx.fillStyle = '#ffffff50';
    ctx.font = '9px monospace';
    ctx.fillText(`${camData.ai_model} | ${camData.tracker} | ${camData.processing_time_ms?.toFixed(0)}ms`, 10, h - 8);
}
