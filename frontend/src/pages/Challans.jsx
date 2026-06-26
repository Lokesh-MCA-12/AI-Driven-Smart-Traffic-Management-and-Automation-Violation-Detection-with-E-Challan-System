import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import {
    HiOutlineSearch, HiOutlineDownload, HiOutlineCurrencyRupee, HiOutlineCash,
    HiOutlineMail, HiOutlineDeviceMobile, HiOutlineRefresh, HiOutlineBell
} from 'react-icons/hi';
import simStore from '../simulator';

const STATUS_BADGE = {
    pending: 'badge-warning', paid: 'badge-success', overdue: 'badge-danger',
    disputed: 'badge-info', cancelled: 'badge bg-surface-500/20 text-surface-400 border border-surface-500/30',
};

export default function Challans() {
    const [challans, setChallans] = useState([]);
    const [statusFilter, setStatusFilter] = useState('');
    const [search, setSearch] = useState('');
    const [selectedChallan, setSelectedChallan] = useState(null);

    useEffect(() => {
        loadChallans();
        const unsub = simStore.subscribe((type) => {
            if (type === 'challan' || type === 'notification') loadChallans();
        });
        return unsub;
    }, []);

    const loadChallans = useCallback(() => {
        setChallans(simStore.getChallans());
    }, []);

    const handlePayment = (challanId) => {
        const methods = ['UPI', 'Net Banking', 'Credit Card', 'Razorpay'];
        const method = methods[Math.floor(Math.random() * methods.length)];
        simStore.processPayment(challanId, method);
        toast.success(
            <div>
                <p className="font-semibold">Payment Processed!</p>
                <p className="text-xs mt-1 opacity-80">via {method}</p>
            </div>
        );
        loadChallans();
    };

    // ========== NEW: Send Email Notification ==========
    const handleSendEmail = (challanId, e) => {
        e?.stopPropagation();
        const result = simStore.sendNotification(challanId, 'email');
        if (result.success) {
            toast.success(
                <div>
                    <p className="font-semibold">📧 Email Sent!</p>
                    <p className="text-xs mt-1 opacity-80">To: {result.recipient}</p>
                    <p className="text-xs opacity-60">Challan: {result.challan_number}</p>
                </div>
            );
        } else {
            toast.error(`Email failed: ${result.error}`);
        }
        loadChallans();
    };

    // ========== NEW: Send SMS Notification ==========
    const handleSendSMS = (challanId, e) => {
        e?.stopPropagation();
        const result = simStore.sendNotification(challanId, 'sms');
        if (result.success) {
            toast.success(
                <div>
                    <p className="font-semibold">📱 SMS Sent!</p>
                    <p className="text-xs mt-1 opacity-80">To: {result.recipient}</p>
                    <p className="text-xs opacity-60">Challan: {result.challan_number}</p>
                </div>
            );
        } else {
            toast.error(`SMS failed: ${result.error}`);
        }
        loadChallans();
    };

    // ========== NEW: Send Both Notifications ==========
    const handleSendAllNotifications = (challanId, e) => {
        e?.stopPropagation();
        const results = simStore.sendAllNotifications(challanId);
        const emailOk = results.email?.success;
        const smsOk = results.sms?.success;
        toast.success(
            <div>
                <p className="font-semibold">🔔 Notifications Sent!</p>
                <p className="text-xs mt-1 opacity-80">
                    {emailOk ? `📧 Email → ${results.email.recipient}` : '📧 Email failed'}
                </p>
                <p className="text-xs opacity-80">
                    {smsOk ? `📱 SMS → ${results.sms.recipient}` : '📱 SMS failed'}
                </p>
            </div>
        );
        loadChallans();
    };

    // ========== IMPROVED: CSV Export with more data ==========
    const handleExport = () => {
        const csvContent = simStore.exportChallansCSV();
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `challans_export_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success(
            <div>
                <p className="font-semibold">📥 CSV Exported!</p>
                <p className="text-xs mt-1 opacity-80">{challans.length} challans saved to file</p>
            </div>
        );
    };

    const filtered = challans.filter(c => {
        if (search && !c.challan_number?.toUpperCase().includes(search.toUpperCase()) && !c.plate_number?.includes(search.toUpperCase())) return false;
        if (statusFilter && c.payment_status !== statusFilter) return false;
        return true;
    });

    const totalFine = filtered.reduce((sum, c) => sum + Number(c.fine_amount), 0);
    const paidChallans = filtered.filter(c => c.payment_status === 'paid');
    const paidAmount = paidChallans.reduce((sum, c) => sum + Number(c.fine_amount), 0);
    const pendingCount = filtered.filter(c => c.payment_status === 'pending').length;
    const overdueCount = filtered.filter(c => c.payment_status === 'overdue').length;

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="page-title text-3xl">E-Challans</h1>
                    <p className="text-surface-400 text-sm mt-1">Automated challan generation, payment tracking & notifications</p>
                </div>
                <div className="flex items-center gap-2">
                    <button onClick={handleExport} className="btn-secondary flex items-center gap-2 text-sm" id="export-challans">
                        <HiOutlineDownload size={16} /> Export CSV
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="stat-card stat-card-primary">
                    <p className="text-xs text-surface-400 mb-1">Total Fines</p>
                    <p className="text-2xl font-bold text-white">₹{totalFine.toLocaleString()}</p>
                    <p className="text-xs text-surface-500 mt-1">{filtered.length} challans</p>
                </div>
                <div className="stat-card stat-card-success">
                    <p className="text-xs text-surface-400 mb-1">Collected</p>
                    <p className="text-2xl font-bold text-emerald-400">₹{paidAmount.toLocaleString()}</p>
                    <p className="text-xs text-surface-500 mt-1">{paidChallans.length} paid</p>
                </div>
                <div className="stat-card stat-card-warning">
                    <p className="text-xs text-surface-400 mb-1">Pending</p>
                    <p className="text-2xl font-bold text-amber-400">{pendingCount}</p>
                    <p className="text-xs text-surface-500 mt-1">Awaiting payment</p>
                </div>
                <div className="stat-card stat-card-danger">
                    <p className="text-xs text-surface-400 mb-1">Overdue</p>
                    <p className="text-2xl font-bold text-red-400">{overdueCount}</p>
                    <p className="text-xs text-surface-500 mt-1">Past due date</p>
                </div>
            </div>

            {/* Filters */}
            <div className="glass-card p-4">
                <div className="flex flex-wrap gap-3">
                    <div className="relative flex-1 min-w-[200px]">
                        <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                        <input type="text" id="challan-search" placeholder="Search challan number or plate..."
                            value={search} onChange={(e) => setSearch(e.target.value)}
                            className="input-field pl-10 py-2.5 text-sm" />
                    </div>
                    <select id="challan-status-filter" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
                        className="input-field w-auto min-w-[140px] py-2.5 text-sm">
                        <option value="">All Status</option>
                        <option value="paid">✅ Paid</option>
                        <option value="pending">⏳ Pending</option>
                        <option value="overdue">⚠️ Overdue</option>
                    </select>
                </div>
            </div>

            {/* Table */}
            <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-surface-700/50">
                                {['Challan No.', 'Plate', 'Owner', 'Type', 'Fine', 'Issue Date', 'Due Date', 'Status', 'Notified', 'Action'].map(h => (
                                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-surface-400 uppercase tracking-wider">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.length === 0 ? (
                                <tr><td colSpan={10} className="text-center py-12 text-surface-400">No challans found</td></tr>
                            ) : filtered.slice(0, 50).map(c => (
                                <tr key={c.id} className="table-row">
                                    <td className="px-4 py-3 font-mono font-medium text-white text-xs">{c.challan_number}</td>
                                    <td className="px-4 py-3 font-mono text-surface-300 text-xs">{c.plate_number}</td>
                                    <td className="px-4 py-3 text-surface-300 text-xs max-w-[120px] truncate">{c.owner_name}</td>
                                    <td className="px-4 py-3">
                                        <span className={({
                                            red_light: 'badge-danger', no_helmet: 'badge-warning', no_seatbelt: 'badge-info',
                                            overspeed: 'badge-danger', wrong_lane: 'badge-warning',
                                        })[c.violation_type] || 'badge-info'}>
                                            {c.violation_type?.replace(/_/g, ' ').replace(/\b\w/g, x => x.toUpperCase())}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="flex items-center gap-1 text-white font-semibold">
                                            <HiOutlineCurrencyRupee size={14} className="text-surface-400" />
                                            {Number(c.fine_amount).toLocaleString()}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-surface-300 text-xs">{c.issue_date}</td>
                                    <td className="px-4 py-3 text-surface-300 text-xs">{c.due_date}</td>
                                    <td className="px-4 py-3">
                                        <span className={STATUS_BADGE[c.payment_status] || 'badge-info'}>
                                            {c.payment_status?.charAt(0).toUpperCase() + c.payment_status?.slice(1)}
                                        </span>
                                    </td>
                                    {/* ========== FIXED: Notified column — NOW CLICKABLE BUTTONS ========== */}
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-1.5">
                                            <button
                                                onClick={(e) => handleSendEmail(c.id, e)}
                                                title={c.notification_email ? "Email sent ✓ — Click to resend" : "Send Email notification"}
                                                className={`p-1 rounded-md transition-all duration-200 ${
                                                    c.notification_email 
                                                        ? 'text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20' 
                                                        : 'text-surface-500 hover:text-amber-400 hover:bg-amber-500/10'
                                                }`}
                                            >
                                                <HiOutlineMail size={15} />
                                            </button>
                                            <button
                                                onClick={(e) => handleSendSMS(c.id, e)}
                                                title={c.notification_sms ? "SMS sent ✓ — Click to resend" : "Send SMS notification"}
                                                className={`p-1 rounded-md transition-all duration-200 ${
                                                    c.notification_sms 
                                                        ? 'text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20' 
                                                        : 'text-surface-500 hover:text-amber-400 hover:bg-amber-500/10'
                                                }`}
                                            >
                                                <HiOutlineDeviceMobile size={15} />
                                            </button>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-1.5">
                                            {c.payment_status !== 'paid' && (
                                                <button onClick={() => handlePayment(c.id)} className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1" title="Process Payment">
                                                    <HiOutlineCash size={14} /> Pay
                                                </button>
                                            )}
                                            {c.payment_status === 'paid' && (
                                                <span className="text-xs text-emerald-400">✓ {c.payment_method}</span>
                                            )}
                                            {/* Notify All button */}
                                            {(!c.notification_email || !c.notification_sms) && (
                                                <button
                                                    onClick={(e) => handleSendAllNotifications(c.id, e)}
                                                    className="p-1.5 rounded-lg text-amber-400 hover:bg-amber-500/10 transition-colors"
                                                    title="Send Email + SMS"
                                                >
                                                    <HiOutlineBell size={14} />
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div className="px-4 py-3 border-t border-surface-700/50 flex items-center justify-between text-xs text-surface-400">
                    <span>Showing {Math.min(filtered.length, 50)} of {filtered.length} challans</span>
                    <span className="text-surface-500">Notifications: SMTP Email + Twilio SMS | PDF: ReportLab</span>
                </div>
            </div>
        </div>
    );
}
