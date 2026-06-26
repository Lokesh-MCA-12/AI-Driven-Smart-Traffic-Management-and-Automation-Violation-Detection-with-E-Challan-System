import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import {
    HiOutlineSearch, HiOutlineFilter, HiOutlineShieldCheck, HiOutlineDocumentAdd,
    HiOutlinePhotograph, HiOutlineEye, HiOutlineDownload, HiOutlineClipboardList
} from 'react-icons/hi';
import simStore, { VIOLATION_TYPES } from '../simulator';

const TYPE_BADGES = {
    red_light: { label: 'Red Light', class: 'badge-danger' },
    no_helmet: { label: 'No Helmet', class: 'badge-warning' },
    no_seatbelt: { label: 'No Seatbelt', class: 'badge-info' },
    overspeed: { label: 'Overspeeding', class: 'badge-danger' },
    wrong_lane: { label: 'Wrong Lane', class: 'badge-warning' },
};

export default function Violations() {
    const [violations, setViolations] = useState([]);
    const [search, setSearch] = useState('');
    const [typeFilter, setTypeFilter] = useState('');
    const [verifiedFilter, setVerifiedFilter] = useState('');
    const [selectedViolation, setSelectedViolation] = useState(null);

    useEffect(() => {
        loadViolations();
        // Subscribe to new violations
        const unsub = simStore.subscribe((type) => {
            if (type === 'violation') loadViolations();
        });
        return unsub;
    }, []);

    const loadViolations = useCallback(() => {
        setViolations(simStore.getViolations());
    }, []);

    const handleVerify = (id) => {
        simStore.verifyViolation(id);
        toast.success('Violation verified by officer');
        loadViolations();
    };

    const handleOnSpot = (id) => {
        simStore.markOnSpot(id);
        toast.success('Violation marked as On-The-Spot');
        loadViolations();
    };

    const handleGenerateChallan = (id) => {
        const challan = simStore.generateChallan(id);
        if (challan) {
            toast.success(
                <div>
                    <p className="font-semibold">E-Challan Generated!</p>
                    <p className="text-xs mt-1 opacity-80">
                        {challan.challan_number} · ₹{challan.fine_amount}
                    </p>
                    <p className="text-xs opacity-60">📧 Email + 📱 SMS sent to owner</p>
                </div>
            );
        }
    };

    // ========== NEW: Export Violations CSV ==========
    const handleExportViolations = () => {
        const csvContent = simStore.exportViolationsCSV();
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `violations_export_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success(
            <div>
                <p className="font-semibold">📥 Violations CSV Exported!</p>
                <p className="text-xs mt-1 opacity-80">{violations.length} records saved</p>
            </div>
        );
    };

    const filtered = violations.filter(v => {
        if (search) {
            const s = search.toUpperCase();
            if (!v.plate_number?.includes(s) && !v.location?.toUpperCase().includes(s) && !v.owner_name?.toUpperCase().includes(s)) return false;
        }
        if (typeFilter && v.violation_type !== typeFilter) return false;
        if (verifiedFilter === 'true' && !v.is_verified) return false;
        if (verifiedFilter === 'false' && v.is_verified) return false;
        return true;
    });

    const stats = {
        total: violations.length,
        verified: violations.filter(v => v.is_verified).length,
        unverified: violations.filter(v => !v.is_verified).length,
        today: violations.filter(v => v.timestamp?.startsWith(new Date().toISOString().split('T')[0])).length,
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="page-title text-3xl">Violations</h1>
                    <p className="text-surface-400 text-sm mt-1">AI-detected traffic violation records</p>
                </div>
                <div className="flex items-center gap-3">
                    <span className="badge-info text-[10px]">🔬 Simulated YOLO26 + SORT Pipeline</span>
                    <button onClick={handleExportViolations} className="btn-secondary flex items-center gap-2 text-sm" id="export-violations">
                        <HiOutlineDownload size={16} /> Export CSV
                    </button>
                </div>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="stat-card stat-card-danger"><p className="text-xs text-surface-400">Total</p><p className="text-2xl font-bold text-white">{stats.total}</p></div>
                <div className="stat-card stat-card-success"><p className="text-xs text-surface-400">Verified</p><p className="text-2xl font-bold text-emerald-400">{stats.verified}</p></div>
                <div className="stat-card stat-card-warning"><p className="text-xs text-surface-400">Pending Review</p><p className="text-2xl font-bold text-amber-400">{stats.unverified}</p></div>
                <div className="stat-card stat-card-primary"><p className="text-xs text-surface-400">Today</p><p className="text-2xl font-bold text-primary-400">{stats.today}</p></div>
            </div>

            {/* Filters */}
            <div className="glass-card p-4">
                <div className="flex flex-wrap gap-3">
                    <div className="relative flex-1 min-w-[200px]">
                        <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                        <input
                            type="text" id="violation-search" placeholder="Search plate, location, or owner..."
                            value={search} onChange={(e) => setSearch(e.target.value)}
                            className="input-field pl-10 py-2.5 text-sm"
                        />
                    </div>
                    <select id="violation-type-filter" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
                        className="input-field w-auto min-w-[160px] py-2.5 text-sm">
                        <option value="">All Types</option>
                        <option value="red_light">🔴 Red Light</option>
                        <option value="no_helmet">⛑️ No Helmet</option>
                        <option value="no_seatbelt">🪢 No Seatbelt</option>
                        <option value="overspeed">💨 Overspeeding</option>
                        <option value="wrong_lane">🚧 Wrong Lane</option>
                    </select>
                    <select id="violation-verified-filter" value={verifiedFilter} onChange={(e) => setVerifiedFilter(e.target.value)}
                        className="input-field w-auto min-w-[130px] py-2.5 text-sm">
                        <option value="">All Status</option>
                        <option value="true">✅ Verified</option>
                        <option value="false">⏳ Pending</option>
                    </select>
                </div>
            </div>

            {/* Table */}
            <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-surface-700/50">
                                {['Plate', 'Owner', 'Type', 'Location', 'Speed', 'Confidence', 'Fine', 'Status', 'Time', 'Actions'].map(h => (
                                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-surface-400 uppercase tracking-wider">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.length === 0 ? (
                                <tr><td colSpan={10} className="text-center py-12 text-surface-400">No violations match your filters</td></tr>
                            ) : filtered.slice(0, 50).map((v, i) => (
                                <tr key={v.id} className="table-row cursor-pointer" onClick={() => setSelectedViolation(v)}>
                                    <td className="px-4 py-3 font-mono font-medium text-white">{v.plate_number || '—'}</td>
                                    <td className="px-4 py-3 text-surface-300 text-xs max-w-[120px] truncate">{v.owner_name || '—'}</td>
                                    <td className="px-4 py-3">
                                        <span className={TYPE_BADGES[v.violation_type]?.class || 'badge-info'}>
                                            {TYPE_BADGES[v.violation_type]?.label || v.violation_type}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-surface-300 max-w-[160px] truncate">{v.location || '—'}</td>
                                    <td className="px-4 py-3 text-surface-300">
                                        {v.speed_detected ? (
                                            <span className="text-red-400 font-medium">{v.speed_detected} <span className="text-surface-500 text-xs">/ {v.speed_limit} km/h</span></span>
                                        ) : '—'}
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-2">
                                            <div className="w-16 h-1.5 rounded-full bg-surface-700 overflow-hidden">
                                                <div className="h-full rounded-full bg-primary-500"
                                                    style={{ width: `${(v.confidence_score || 0) * 100}%` }} />
                                            </div>
                                            <span className="text-xs text-surface-400">{((v.confidence_score || 0) * 100).toFixed(0)}%</span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3 text-white font-semibold">₹{v.fine_amount?.toLocaleString()}</td>
                                    <td className="px-4 py-3">
                                        {v.is_on_spot ? <span className="badge-danger bg-rose-500/20 text-rose-400">On-Spot</span> : v.is_verified ? <span className="badge-success">Verified</span> : <span className="badge-warning">Pending</span>}
                                    </td>
                                    <td className="px-4 py-3 text-surface-400 text-xs">
                                        {new Date(v.timestamp).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                                    </td>
                                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                                        <div className="flex gap-1">
                                            {!v.is_verified && !v.is_on_spot && (
                                                <>
                                                    <button onClick={() => handleVerify(v.id)} title="Verify Violation"
                                                        className="p-1.5 rounded-lg text-emerald-400 hover:bg-emerald-500/10 transition-colors">
                                                        <HiOutlineShieldCheck size={16} />
                                                    </button>
                                                    <button onClick={() => handleOnSpot(v.id)} title="Mark On-Spot"
                                                        className="p-1.5 rounded-lg text-rose-400 hover:bg-rose-500/10 transition-colors">
                                                        <HiOutlineClipboardList size={16} />
                                                    </button>
                                                </>
                                            )}
                                            <button onClick={() => handleGenerateChallan(v.id)} title="Generate E-Challan"
                                                className="p-1.5 rounded-lg text-primary-400 hover:bg-primary-500/10 transition-colors">
                                                <HiOutlineDocumentAdd size={16} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div className="px-4 py-3 border-t border-surface-700/50 flex items-center justify-between text-xs text-surface-400">
                    <span>Showing {Math.min(filtered.length, 50)} of {filtered.length} violations</span>
                    <span className="text-surface-500">Detection: YOLO26 → SORT → Violation Engine → ANPR</span>
                </div>
            </div>

            {/* Detail Modal */}
            {selectedViolation && (
                <ViolationDetailModal violation={selectedViolation} onClose={() => setSelectedViolation(null)}
                    onVerify={handleVerify} onOnSpot={handleOnSpot} onGenerateChallan={handleGenerateChallan} />
            )}
        </div>
    );
}

function ViolationDetailModal({ violation: v, onClose, onVerify, onOnSpot, onGenerateChallan }) {
    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
            <div className="glass-card p-6 w-full max-w-lg animate-scale-in" onClick={(e) => e.stopPropagation()}>
                <div className="flex justify-between items-start mb-4">
                    <h2 className="text-lg font-bold text-white">Violation Detail</h2>
                    <button onClick={onClose} className="text-surface-400 hover:text-white text-xl">✕</button>
                </div>

                <div className="space-y-4">
                    {/* Evidence placeholder */}
                    <div className="bg-surface-800 rounded-xl p-8 flex flex-col items-center justify-center gap-2 border border-surface-700/50">
                        <HiOutlinePhotograph className="text-surface-500" size={48} />
                        <p className="text-xs text-surface-400">Evidence frame captured by CCTV</p>
                        <p className="text-[10px] text-surface-500">
                            Detection: YOLO26 → Confidence {((v.confidence_score || 0) * 100).toFixed(1)}%
                        </p>
                    </div>

                    {/* Details grid */}
                    <div className="grid grid-cols-2 gap-3 text-sm">
                        <DetailRow label="Plate Number" value={v.plate_number} mono />
                        <DetailRow label="Owner" value={v.owner_name} />
                        <DetailRow label="Type" value={TYPE_BADGES[v.violation_type]?.label} />
                        <DetailRow label="Location" value={v.location} />
                        <DetailRow label="Status" value={v.is_on_spot ? 'On-Spot' : v.is_verified ? 'Verified' : 'Pending'} />
                        <DetailRow label="Camera" value={v.camera_id} />
                        <DetailRow label="Fine" value={`₹${v.fine_amount?.toLocaleString()}`} />
                        <DetailRow label="Legal Section" value={v.legal_section} />
                        <DetailRow label="Confidence" value={`${((v.confidence_score || 0) * 100).toFixed(1)}%`} />
                        {v.speed_detected && <DetailRow label="Speed" value={`${v.speed_detected} km/h (limit: ${v.speed_limit})`} />}
                        <DetailRow label="Time" value={new Date(v.timestamp).toLocaleString('en-IN')} />
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-2">
                        {!v.is_verified && !v.is_on_spot && (
                            <>
                                <button onClick={() => { onVerify(v.id); onClose(); }} className="btn-primary flex-1 flex items-center justify-center gap-2 text-sm">
                                    <HiOutlineShieldCheck size={16} /> Verify
                                </button>
                                <button onClick={() => { onOnSpot(v.id); onClose(); }} className="btn-secondary flex items-center justify-center gap-2 text-sm border-rose-500/50 text-rose-400 hover:bg-rose-500/10">
                                    <HiOutlineClipboardList size={16} /> On-Spot
                                </button>
                            </>
                        )}
                        <button onClick={() => { onGenerateChallan(v.id); onClose(); }} className="btn-secondary flex-1 flex items-center justify-center gap-2 text-sm">
                            <HiOutlineDocumentAdd size={16} /> Generate E-Challan
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

function DetailRow({ label, value, mono }) {
    return (
        <div>
            <p className="text-xs text-surface-500">{label}</p>
            <p className={`text-surface-200 ${mono ? 'font-mono font-bold' : ''}`}>{value || '—'}</p>
        </div>
    );
}
