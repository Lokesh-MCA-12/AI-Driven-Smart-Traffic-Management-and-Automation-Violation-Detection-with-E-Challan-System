import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
    HiOutlineViewGrid,
    HiOutlineExclamationCircle,
    HiOutlineDocumentText,
    HiOutlineTruck,
    HiOutlineStatusOnline,
    HiOutlineChartBar,
    HiOutlineLogout,
    HiOutlineMenuAlt2,
    HiOutlineChevronLeft,
} from 'react-icons/hi';

const navItems = [
    { path: '/', label: 'Dashboard', icon: HiOutlineViewGrid },
    { path: '/violations', label: 'Violations', icon: HiOutlineExclamationCircle },
    { path: '/challans', label: 'E-Challans', icon: HiOutlineDocumentText },
    { path: '/vehicles', label: 'Vehicles', icon: HiOutlineTruck },
    { path: '/traffic', label: 'Traffic Monitor', icon: HiOutlineStatusOnline },
    { path: '/analytics', label: 'Analytics', icon: HiOutlineChartBar },
];

export default function Sidebar({ user, isOpen, onToggle, onLogout }) {
    const location = useLocation();

    return (
        <aside
            className={`fixed left-0 top-0 h-screen bg-surface-900/95 backdrop-blur-xl border-r border-surface-700/50 
      transition-all duration-300 z-50 flex flex-col ${isOpen ? 'w-64' : 'w-20'}`}
        >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-surface-700/50">
                {isOpen && (
                    <div className="flex items-center gap-3 animate-fade-in">
                        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                            <span className="text-white text-lg">🚦</span>
                        </div>
                        <div>
                            <h1 className="text-sm font-bold text-white leading-tight">Smart Traffic</h1>
                            <p className="text-[10px] text-surface-400">Management System</p>
                        </div>
                    </div>
                )}
                <button
                    onClick={onToggle}
                    className="p-2 rounded-lg text-surface-400 hover:text-white hover:bg-surface-800 transition-colors"
                    id="sidebar-toggle"
                >
                    {isOpen ? <HiOutlineChevronLeft size={18} /> : <HiOutlineMenuAlt2 size={18} />}
                </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
                {navItems.map(({ path, label, icon: Icon }) => {
                    const isActive = location.pathname === path;
                    return (
                        <NavLink
                            key={path}
                            to={path}
                            id={`nav-${label.toLowerCase().replace(/\s+/g, '-')}`}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group
                ${isActive
                                    ? 'bg-primary-500/15 text-primary-400 border border-primary-500/20 shadow-glow'
                                    : 'text-surface-400 hover:bg-surface-800/80 hover:text-white border border-transparent'
                                }`}
                            title={!isOpen ? label : undefined}
                        >
                            <Icon size={20} className={`flex-shrink-0 ${isActive ? 'text-primary-400' : 'group-hover:text-primary-300'}`} />
                            {isOpen && <span className="text-sm font-medium animate-fade-in">{label}</span>}
                            {isActive && isOpen && (
                                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-400 animate-pulse-slow" />
                            )}
                        </NavLink>
                    );
                })}
            </nav>

            {/* User section */}
            <div className="p-3 border-t border-surface-700/50">
                {isOpen && (
                    <div className="flex items-center gap-3 px-3 py-2 mb-2 animate-fade-in">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                            <span className="text-white text-xs font-bold">
                                {user?.full_name?.charAt(0) || 'A'}
                            </span>
                        </div>
                        <div className="min-w-0">
                            <p className="text-xs font-semibold text-white truncate">{user?.full_name}</p>
                            <p className="text-[10px] text-surface-400 capitalize">{user?.role}</p>
                        </div>
                    </div>
                )}
                <button
                    onClick={onLogout}
                    id="logout-btn"
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-surface-400 
                     hover:bg-red-500/10 hover:text-red-400 transition-all duration-200"
                    title={!isOpen ? 'Logout' : undefined}
                >
                    <HiOutlineLogout size={20} />
                    {isOpen && <span className="text-sm font-medium">Logout</span>}
                </button>
            </div>
        </aside>
    );
}
