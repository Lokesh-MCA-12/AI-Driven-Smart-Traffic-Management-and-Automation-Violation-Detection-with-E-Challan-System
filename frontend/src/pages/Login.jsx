import React, { useState } from 'react';
import toast from 'react-hot-toast';
import simStore from '../simulator';
import { HiOutlineLockClosed, HiOutlineUser, HiOutlineEye, HiOutlineEyeOff } from 'react-icons/hi';

export default function Login({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username || !password) {
            toast.error('Please fill in all fields');
            return;
        }

        setLoading(true);

        // Simulate network delay (like real API call would have)
        await new Promise(resolve => setTimeout(resolve, 800));

        // Use simulation store — same auth logic as FastAPI backend
        const result = simStore.login(username, password);

        if (result.error) {
            toast.error(result.error);
            setLoading(false);
            return;
        }

        toast.success(`Welcome back, ${result.user.full_name}!`);
        onLogin(result.user, result.access_token);
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-surface-950 flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background effects */}
            <div className="absolute inset-0">
                <div className="absolute top-1/4 -left-20 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl animate-pulse-slow" />
                <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-primary-700/10 rounded-full blur-3xl animate-pulse-slow" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary-500/5 rounded-full blur-3xl" />
            </div>

            {/* Grid pattern overlay */}
            <div className="absolute inset-0 opacity-[0.02]"
                style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }}
            />

            <div className="relative w-full max-w-md animate-scale-in">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 mb-4 shadow-glow">
                        <span className="text-3xl">🚦</span>
                    </div>
                    <h1 className="text-2xl font-bold text-white mb-1">Smart Traffic Management</h1>
                    <p className="text-surface-400 text-sm">AI-Driven Violation Detection & E-Challan System</p>
                </div>

                {/* Login Card */}
                <div className="glass-card p-8">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-semibold text-white">Sign In</h2>
                        <span className="badge-info text-[10px]">🔬 Simulator Mode</span>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium text-surface-300 mb-2">Username</label>
                            <div className="relative">
                                <HiOutlineUser className="absolute left-4 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                                <input
                                    type="text"
                                    id="login-username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="input-field pl-11"
                                    placeholder="Enter your username"
                                    autoComplete="username"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-surface-300 mb-2">Password</label>
                            <div className="relative">
                                <HiOutlineLockClosed className="absolute left-4 top-1/2 -translate-y-1/2 text-surface-400" size={18} />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    id="login-password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field pl-11 pr-11"
                                    placeholder="Enter your password"
                                    autoComplete="current-password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-surface-400 hover:text-white transition-colors"
                                >
                                    {showPassword ? <HiOutlineEyeOff size={18} /> : <HiOutlineEye size={18} />}
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            id="login-submit"
                            disabled={loading}
                            className="btn-primary w-full flex items-center justify-center gap-2 py-3 text-base"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    <HiOutlineLockClosed size={18} />
                                    Sign In
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 pt-6 border-t border-surface-700/50">
                        <p className="text-xs text-surface-400 text-center mb-3">Available Accounts:</p>
                        <div className="space-y-2">
                            {[
                                { user: 'admin', pass: 'admin123', role: 'Admin' },
                                { user: 'officer1', pass: 'admin123', role: 'Officer' },
                                { user: 'officer2', pass: 'admin123', role: 'Officer' },
                            ].map(({ user, pass, role }) => (
                                <button
                                    key={user}
                                    type="button"
                                    onClick={() => { setUsername(user); setPassword(pass); }}
                                    className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-surface-800/50 hover:bg-surface-700/50 transition-colors text-xs"
                                >
                                    <span className="font-mono text-surface-300">{user}</span>
                                    <span className="badge text-[10px] bg-primary-500/10 text-primary-400 border border-primary-500/20">{role}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <p className="text-center text-xs text-surface-500 mt-6">
                    © 2026 Smart Traffic Management Authority · Simulation Environment
                </p>
            </div>
        </div>
    );
}
