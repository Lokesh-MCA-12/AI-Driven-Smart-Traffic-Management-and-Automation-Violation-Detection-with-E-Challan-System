import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { HiOutlineSearch, HiOutlinePlus, HiOutlineLocationMarker } from 'react-icons/hi';
import simStore from '../simulator';

const TYPE_ICONS = { car: '🚗', bike: '🏍️', bus: '🚌', truck: '🚛', auto: '🛺', other: '🚙' };

export default function Vehicles() {
    const [vehicles, setVehicles] = useState([]);
    const [search, setSearch] = useState('');
    const [showAddModal, setShowAddModal] = useState(false);
    const [searchResult, setSearchResult] = useState(null);
    const [selectedVehicle, setSelectedVehicle] = useState(null);

    useEffect(() => {
        setVehicles(simStore.getVehicles());
    }, []);

    const handleSearch = () => {
        if (!search) return;
        const found = simStore.getVehicleByPlate(search);
        if (found) {
            setSearchResult(found);
            // Find violations for this vehicle
            const violations = simStore.getViolations({ search: found.plate_number });
            setSearchResult({ ...found, violation_count: violations.length });
        } else {
            toast.error(`Vehicle ${search.toUpperCase()} not found in RTO database`);
            setSearchResult(null);
        }
    };

    const handleAdd = (formData) => {
        const vehicle = simStore.addVehicle(formData);
        toast.success(`Vehicle ${vehicle.plate_number} registered`);
        setVehicles(simStore.getVehicles());
        setShowAddModal(false);
    };

    const filtered = vehicles.filter(v => {
        if (!search) return true;
        const s = search.toUpperCase();
        return v.plate_number?.includes(s) || v.owner_name?.toUpperCase().includes(s) || v.make?.toUpperCase().includes(s);
    });

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="page-title text-3xl">Vehicle Database</h1>
                    <p className="text-surface-400 text-sm mt-1">Registered vehicles & RTO records ({vehicles.length} entries)</p>
                </div>
                <button onClick={() => setShowAddModal(true)} className="btn-primary flex items-center gap-2 text-sm" id="add-vehicle-btn">
                    <HiOutlinePlus size={16} /> Register Vehicle
                </button>
            </div>

            {/* ANPR Search */}
            <div className="glass-card p-5">
                <div className="flex items-center gap-2 mb-3">
                    <span className="text-sm font-medium text-white">🔍 ANPR Plate Lookup</span>
                    <span className="badge-info text-[10px]">Simulated EasyOCR</span>
                </div>
                <div className="flex gap-3">
                    <div className="relative flex-1">
                        <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                        <input type="text" id="vehicle-search" placeholder="Enter plate number (e.g., KA01AB1234)..."
                            value={search} onChange={(e) => setSearch(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            className="input-field pl-10 py-2.5 text-sm font-mono uppercase" />
                    </div>
                    <button onClick={handleSearch} className="btn-primary text-sm px-5" id="vehicle-search-btn">
                        Lookup
                    </button>
                </div>
            </div>

            {/* Search result card */}
            {searchResult && (
                <div className="glass-card p-6 border-l-4 border-primary-500 animate-scale-in">
                    <div className="flex items-start justify-between">
                        <div className="flex-1">
                            <div className="flex items-center gap-4 mb-4">
                                <span className="text-4xl">{TYPE_ICONS[searchResult.vehicle_type] || '🚙'}</span>
                                <div>
                                    <h3 className="text-xl font-bold text-white font-mono tracking-wider">{searchResult.plate_number}</h3>
                                    <p className="text-sm text-surface-400">{searchResult.make} {searchResult.model} · {searchResult.year} · {searchResult.color}</p>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                <div><span className="text-surface-500 text-xs">Owner</span><p className="text-white font-medium">{searchResult.owner_name}</p></div>
                                <div><span className="text-surface-500 text-xs">Phone</span><p className="text-white font-mono text-xs">{searchResult.phone}</p></div>
                                <div><span className="text-surface-500 text-xs">Email</span><p className="text-surface-300 text-xs">{searchResult.email}</p></div>
                                <div><span className="text-surface-500 text-xs">Violations</span><p className={`font-bold ${searchResult.violation_count > 0 ? 'text-red-400' : 'text-emerald-400'}`}>{searchResult.violation_count || 0}</p></div>
                            </div>
                            {searchResult.address && (
                                <div className="flex items-center gap-1 mt-3 text-xs text-surface-400">
                                    <HiOutlineLocationMarker size={12} />
                                    {searchResult.address}
                                </div>
                            )}
                        </div>
                        <button onClick={() => setSearchResult(null)} className="text-surface-400 hover:text-white text-lg ml-4">✕</button>
                    </div>
                </div>
            )}

            {/* Vehicle Grid Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filtered.map(v => {
                    const violations = simStore.getViolations({ search: v.plate_number });
                    return (
                        <div key={v.id} className="glass-card-hover p-5 cursor-pointer" onClick={() => setSelectedVehicle(v)}>
                            <div className="flex items-center gap-3 mb-3">
                                <span className="text-2xl">{TYPE_ICONS[v.vehicle_type] || '🚙'}</span>
                                <div className="flex-1 min-w-0">
                                    <p className="font-mono font-bold text-white tracking-wide">{v.plate_number}</p>
                                    <p className="text-xs text-surface-400">{v.make} {v.model} · {v.year}</p>
                                </div>
                                {violations.length > 0 && (
                                    <span className="badge-danger text-[10px]">{violations.length} violations</span>
                                )}
                            </div>
                            <div className="flex items-center justify-between text-xs">
                                <span className="text-surface-400">{v.owner_name}</span>
                                <span className="capitalize text-surface-500 bg-surface-800/50 px-2 py-0.5 rounded">{v.vehicle_type}</span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Add Vehicle Modal */}
            {showAddModal && <AddVehicleModal onClose={() => setShowAddModal(false)} onSubmit={handleAdd} />}

            {/* Vehicle Detail Modal */}
            {selectedVehicle && (
                <VehicleDetailModal vehicle={selectedVehicle} onClose={() => setSelectedVehicle(null)} />
            )}
        </div>
    );
}

function VehicleDetailModal({ vehicle: v, onClose }) {
    const violations = simStore.getViolations({ search: v.plate_number });
    const challans = simStore.getChallans({ search: v.plate_number });

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
            <div className="glass-card p-6 w-full max-w-lg animate-scale-in max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl">{TYPE_ICONS[v.vehicle_type] || '🚙'}</span>
                        <div>
                            <h2 className="text-lg font-bold text-white font-mono">{v.plate_number}</h2>
                            <p className="text-xs text-surface-400">{v.make} {v.model} · {v.color} · {v.year}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="text-surface-400 hover:text-white text-xl">✕</button>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                    <div><p className="text-xs text-surface-500">Owner</p><p className="text-white">{v.owner_name}</p></div>
                    <div><p className="text-xs text-surface-500">Phone</p><p className="text-white font-mono text-xs">{v.phone}</p></div>
                    <div><p className="text-xs text-surface-500">Email</p><p className="text-surface-300 text-xs">{v.email}</p></div>
                    <div><p className="text-xs text-surface-500">Address</p><p className="text-surface-300 text-xs">{v.address}</p></div>
                </div>

                {/* Violation history */}
                <div className="border-t border-surface-700/50 pt-4">
                    <h3 className="text-sm font-semibold text-white mb-3">Violation History ({violations.length})</h3>
                    {violations.length === 0 ? (
                        <p className="text-xs text-surface-400 text-center py-4">No violations recorded</p>
                    ) : (
                        <div className="space-y-2 max-h-[200px] overflow-y-auto">
                            {violations.slice(0, 10).map((vl, i) => (
                                <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-surface-800/50 text-xs">
                                    <div>
                                        <span className="text-surface-300">{vl.violation_type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                                        <span className="text-surface-500 ml-2">{vl.location}</span>
                                    </div>
                                    <span className="text-red-400 font-semibold">₹{vl.fine_amount}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function AddVehicleModal({ onClose, onSubmit }) {
    const [form, setForm] = useState({
        plate_number: '', vehicle_type: 'car', owner_name: '', phone: '',
        email: '', address: '', make: '', model: '', year: 2024, color: '',
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!form.plate_number || !form.owner_name || !form.phone) {
            toast.error('Please fill required fields');
            return;
        }
        onSubmit(form);
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
            <div className="glass-card p-6 w-full max-w-md animate-scale-in" onClick={(e) => e.stopPropagation()}>
                <h2 className="text-lg font-bold text-white mb-4">Register Vehicle</h2>
                <form onSubmit={handleSubmit} className="space-y-3">
                    <input placeholder="Plate Number (e.g., KA01AB1234) *" className="input-field text-sm font-mono uppercase"
                        value={form.plate_number} onChange={(e) => setForm({ ...form, plate_number: e.target.value })} required />
                    <div className="grid grid-cols-2 gap-3">
                        <select className="input-field text-sm" value={form.vehicle_type}
                            onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })}>
                            <option value="car">🚗 Car</option>
                            <option value="bike">🏍️ Bike</option>
                            <option value="bus">🚌 Bus</option>
                            <option value="truck">🚛 Truck</option>
                            <option value="auto">🛺 Auto</option>
                        </select>
                        <input placeholder="Color" className="input-field text-sm"
                            value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <input placeholder="Make (e.g., Maruti)" className="input-field text-sm"
                            value={form.make} onChange={(e) => setForm({ ...form, make: e.target.value })} />
                        <input placeholder="Model (e.g., Swift)" className="input-field text-sm"
                            value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} />
                    </div>
                    <input placeholder="Owner Name *" className="input-field text-sm"
                        value={form.owner_name} onChange={(e) => setForm({ ...form, owner_name: e.target.value })} required />
                    <input placeholder="Phone Number *" className="input-field text-sm"
                        value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} required />
                    <input placeholder="Email" type="email" className="input-field text-sm"
                        value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                    <input placeholder="Address" className="input-field text-sm"
                        value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
                    <div className="flex gap-3 pt-2">
                        <button type="button" onClick={onClose} className="btn-secondary flex-1 text-sm">Cancel</button>
                        <button type="submit" className="btn-primary flex-1 text-sm">Register</button>
                    </div>
                </form>
            </div>
        </div>
    );
}
