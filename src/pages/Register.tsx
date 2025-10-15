import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Brain, Mail, Lock, User, AlertCircle, CheckCircle } from 'lucide-react';

interface RegisterProps {
    onSwitchToLogin: () => void;
}

export const Register: React.FC<RegisterProps> = ({ onSwitchToLogin }) => {
    const { register } = useAuth();
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [fullName, setFullName] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const passwordRequirements = [
        { label: 'At least 8 characters', met: password.length >= 8 },
        { label: 'One uppercase letter', met: /[A-Z]/.test(password) },
        { label: 'One lowercase letter', met: /[a-z]/.test(password) },
        { label: 'One number', met: /\d/.test(password) },
    ];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Validation
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (!passwordRequirements.every(req => req.met)) {
            setError('Password does not meet requirements');
            return;
        }

        setLoading(true);

        try {
            await register(email, username, password, fullName || undefined);
        } catch (err: any) {
            setError(err.message || 'Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4 py-12">
            <div className="max-w-md w-full">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center space-x-2 mb-4">
                        <Brain className="text-blue-400" size={48} />
                        <h1 className="text-3xl font-bold text-white">
                            <span className="text-blue-400">Bolt</span> AI Crypto
                        </h1>
                    </div>
                    <p className="text-gray-400">Create your account</p>
                </div>

                {/* Register Form */}
                <div className="bg-gray-900 rounded-lg border border-gray-800 p-8">
                    {error && (
                        <div className="mb-6 p-4 bg-red-900/20 border border-red-500/50 rounded-lg flex items-start space-x-3">
                            <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
                            <p className="text-red-400 text-sm">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Email */}
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                                Email Address
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="you@example.com"
                                />
                            </div>
                        </div>

                        {/* Username */}
                        <div>
                            <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                                Username
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                                <input
                                    id="username"
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                    minLength={3}
                                    className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="username"
                                />
                            </div>
                        </div>

                        {/* Full Name (Optional) */}
                        <div>
                            <label htmlFor="fullName" className="block text-sm font-medium text-gray-300 mb-2">
                                Full Name <span className="text-gray-500">(optional)</span>
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                                <input
                                    id="fullName"
                                    type="text"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="John Doe"
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                                <input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="••••••••"
                                />
                            </div>

                            {/* Password Requirements */}
                            {password && (
                                <div className="mt-3 space-y-1">
                                    {passwordRequirements.map((req, index) => (
                                        <div key={index} className="flex items-center space-x-2 text-xs">
                                            {req.met ? (
                                                <CheckCircle className="text-green-400" size={14} />
                                            ) : (
                                                <div className="w-3.5 h-3.5 rounded-full border border-gray-600" />
                                            )}
                                            <span className={req.met ? 'text-green-400' : 'text-gray-500'}>
                                                {req.label}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Confirm Password */}
                        <div>
                            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                                Confirm Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                                <input
                                    id="confirmPassword"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                    className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="••••••••"
                                />
                            </div>
                            {confirmPassword && password !== confirmPassword && (
                                <p className="mt-2 text-xs text-red-400">Passwords do not match</p>
                            )}
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-medium py-3 rounded-lg transition-colors"
                        >
                            {loading ? 'Creating account...' : 'Create Account'}
                        </button>
                    </form>

                    {/* Login Link */}
                    <div className="mt-6 text-center">
                        <p className="text-gray-400 text-sm">
                            Already have an account?{' '}
                            <button
                                onClick={onSwitchToLogin}
                                className="text-blue-400 hover:text-blue-300 font-medium"
                            >
                                Sign in
                            </button>
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <p className="mt-8 text-center text-gray-500 text-sm">
                    © 2025 Bolt AI Crypto. Not financial advice.
                </p>
            </div>
        </div>
    );
};

