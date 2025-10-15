import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
    Users,
    Activity,
    Settings,
    BarChart3,
    AlertTriangle,
    Database,
    Server,
    Bot
} from 'lucide-react';

interface SystemMetrics {
    active_users: number;
    total_users: number;
    api_requests: number;
    websocket_connections: number;
    ai_predictions: number;
    alerts_triggered: number;
    database_queries: number;
    redis_hits: number;
    redis_misses: number;
    error_rate: number;
    avg_response_time: number;
    memory_usage: number;
    cpu_usage: number;
}

interface User {
    id: number;
    username: string;
    email: string;
    created_at: string;
    is_active: boolean;
    is_admin: boolean;
    last_login: string;
}

interface ModelMetrics {
    model_name: string;
    accuracy: number;
    loss: number;
    last_trained: string;
    training_status: string;
}

const Admin: React.FC = () => {
    const { user, token } = useAuth();
    const [activeTab, setActiveTab] = useState('dashboard');
    const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
    const [users, setUsers] = useState<User[]>([]);
    const [modelMetrics, setModelMetrics] = useState<ModelMetrics | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (user?.is_admin) {
            fetchAdminData();
        }
    }, [user]);

    const fetchAdminData = async () => {
        try {
            setLoading(true);
            const [metricsRes, usersRes, modelRes] = await Promise.all([
                fetch('/api/admin/metrics', {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                fetch('/api/admin/users', {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                fetch('/api/admin/model-status', {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ]);

            if (metricsRes.ok) {
                const metricsData = await metricsRes.json();
                setMetrics(metricsData);
            }

            if (usersRes.ok) {
                const usersData = await usersRes.json();
                setUsers(usersData);
            }

            if (modelRes.ok) {
                const modelData = await modelRes.json();
                setModelMetrics(modelData);
            }
        } catch (err) {
            setError('Failed to fetch admin data');
        } finally {
            setLoading(false);
        }
    };

    const handleUserAction = async (userId: number, action: string) => {
        try {
            const response = await fetch(`/api/admin/users/${userId}/${action}`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.ok) {
                fetchAdminData(); // Refresh data
            }
        } catch (err) {
            setError(`Failed to ${action} user`);
        }
    };

    const handleModelRetrain = async () => {
        try {
            const response = await fetch('/api/admin/model/retrain', {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.ok) {
                alert('Model retraining started');
                fetchAdminData();
            }
        } catch (err) {
            setError('Failed to start model retraining');
        }
    };

    if (user?.role !== 'admin') {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <AlertTriangle className="mx-auto h-12 w-12 text-red-500" />
                    <h2 className="mt-4 text-2xl font-bold text-gray-900">Access Denied</h2>
                    <p className="mt-2 text-gray-600">You don't have admin privileges.</p>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                    <p className="mt-2 text-gray-600">System monitoring and management</p>
                </div>

                {error && (
                    <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
                        <div className="flex">
                            <AlertTriangle className="h-5 w-5 text-red-400" />
                            <div className="ml-3">
                                <h3 className="text-sm font-medium text-red-800">Error</h3>
                                <div className="mt-2 text-sm text-red-700">{error}</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Navigation Tabs */}
                <div className="mb-8">
                    <nav className="flex space-x-8">
                        {[
                            { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
                            { id: 'users', name: 'Users', icon: Users },
                            { id: 'system', name: 'System', icon: Server },
                            { id: 'ai', name: 'AI Model', icon: Bot },
                            { id: 'settings', name: 'Settings', icon: Settings }
                        ].map((tab) => {
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center space-x-2 px-3 py-2 border-b-2 font-medium text-sm ${activeTab === tab.id
                                            ? 'border-blue-500 text-blue-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                        }`}
                                >
                                    <Icon className="h-4 w-4" />
                                    <span>{tab.name}</span>
                                </button>
                            );
                        })}
                    </nav>
                </div>

                {/* Dashboard Tab */}
                {activeTab === 'dashboard' && metrics && (
                    <div className="space-y-6">
                        {/* Key Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <Users className="h-6 w-6 text-gray-400" />
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">
                                                    Active Users
                                                </dt>
                                                <dd className="text-lg font-medium text-gray-900">
                                                    {metrics.active_users}
                                                </dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <Activity className="h-6 w-6 text-gray-400" />
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">
                                                    API Requests
                                                </dt>
                                                <dd className="text-lg font-medium text-gray-900">
                                                    {metrics.api_requests.toLocaleString()}
                                                </dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <Bot className="h-6 w-6 text-gray-400" />
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">
                                                    AI Predictions
                                                </dt>
                                                <dd className="text-lg font-medium text-gray-900">
                                                    {metrics.ai_predictions.toLocaleString()}
                                                </dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <AlertTriangle className="h-6 w-6 text-gray-400" />
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">
                                                    Alerts Triggered
                                                </dt>
                                                <dd className="text-lg font-medium text-gray-900">
                                                    {metrics.alerts_triggered.toLocaleString()}
                                                </dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* System Health */}
                        <div className="bg-white shadow rounded-lg">
                            <div className="px-4 py-5 sm:p-6">
                                <h3 className="text-lg leading-6 font-medium text-gray-900">
                                    System Health
                                </h3>
                                <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-3">
                                    <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
                                        <div className="p-5">
                                            <div className="flex items-center">
                                                <div className="flex-shrink-0">
                                                    <Server className="h-6 w-6 text-gray-400" />
                                                </div>
                                                <div className="ml-5 w-0 flex-1">
                                                    <dl>
                                                        <dt className="text-sm font-medium text-gray-500 truncate">
                                                            Error Rate
                                                        </dt>
                                                        <dd className="text-lg font-medium text-gray-900">
                                                            {metrics.error_rate.toFixed(2)}%
                                                        </dd>
                                                    </dl>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
                                        <div className="p-5">
                                            <div className="flex items-center">
                                                <div className="flex-shrink-0">
                                                    <Activity className="h-6 w-6 text-gray-400" />
                                                </div>
                                                <div className="ml-5 w-0 flex-1">
                                                    <dl>
                                                        <dt className="text-sm font-medium text-gray-500 truncate">
                                                            Avg Response Time
                                                        </dt>
                                                        <dd className="text-lg font-medium text-gray-900">
                                                            {metrics.avg_response_time.toFixed(0)}ms
                                                        </dd>
                                                    </dl>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
                                        <div className="p-5">
                                            <div className="flex items-center">
                                                <div className="flex-shrink-0">
                                                    <Database className="h-6 w-6 text-gray-400" />
                                                </div>
                                                <div className="ml-5 w-0 flex-1">
                                                    <dl>
                                                        <dt className="text-sm font-medium text-gray-500 truncate">
                                                            Memory Usage
                                                        </dt>
                                                        <dd className="text-lg font-medium text-gray-900">
                                                            {metrics.memory_usage.toFixed(1)}%
                                                        </dd>
                                                    </dl>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Users Tab */}
                {activeTab === 'users' && (
                    <div className="bg-white shadow overflow-hidden sm:rounded-md">
                        <div className="px-4 py-5 sm:px-6">
                            <h3 className="text-lg leading-6 font-medium text-gray-900">
                                User Management
                            </h3>
                            <p className="mt-1 max-w-2xl text-sm text-gray-500">
                                Manage user accounts and permissions
                            </p>
                        </div>
                        <ul className="divide-y divide-gray-200">
                            {users.map((user) => (
                                <li key={user.id}>
                                    <div className="px-4 py-4 flex items-center justify-between">
                                        <div className="flex items-center">
                                            <div className="flex-shrink-0">
                                                <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                                                    <span className="text-sm font-medium text-gray-700">
                                                        {user.username.charAt(0).toUpperCase()}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="ml-4">
                                                <div className="text-sm font-medium text-gray-900">
                                                    {user.username}
                                                </div>
                                                <div className="text-sm text-gray-500">{user.email}</div>
                                                <div className="text-xs text-gray-400">
                                                    Joined: {new Date(user.created_at).toLocaleDateString()}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                }`}>
                                                {user.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                            {user.role === 'admin' && (
                                                <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                                                    Admin
                                                </span>
                                            )}
                                            <div className="flex space-x-1">
                                                <button
                                                    onClick={() => handleUserAction(user.id, 'toggle-active')}
                                                    className="text-sm text-blue-600 hover:text-blue-900"
                                                >
                                                    {user.is_active ? 'Deactivate' : 'Activate'}
                                                </button>
                                                <button
                                                    onClick={() => handleUserAction(user.id, 'delete')}
                                                    className="text-sm text-red-600 hover:text-red-900"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* AI Model Tab */}
                {activeTab === 'ai' && modelMetrics && (
                    <div className="space-y-6">
                        <div className="bg-white shadow rounded-lg">
                            <div className="px-4 py-5 sm:p-6">
                                <h3 className="text-lg leading-6 font-medium text-gray-900">
                                    AI Model Status
                                </h3>
                                <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2">
                                    <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
                                        <div className="p-5">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">
                                                    Model Accuracy
                                                </dt>
                                                <dd className="text-lg font-medium text-gray-900">
                                                    {(modelMetrics.accuracy * 100).toFixed(2)}%
                                                </dd>
                                            </dl>
                                        </div>
                                    </div>

                                    <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
                                        <div className="p-5">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">
                                                    Training Loss
                                                </dt>
                                                <dd className="text-lg font-medium text-gray-900">
                                                    {modelMetrics.loss.toFixed(4)}
                                                </dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                                <div className="mt-5">
                                    <button
                                        onClick={handleModelRetrain}
                                        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                                    >
                                        Retrain Model
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* System Tab */}
                {activeTab === 'system' && (
                    <div className="space-y-6">
                        <div className="bg-white shadow rounded-lg">
                            <div className="px-4 py-5 sm:p-6">
                                <h3 className="text-lg leading-6 font-medium text-gray-900">
                                    System Information
                                </h3>
                                <div className="mt-5">
                                    <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">WebSocket Connections</dt>
                                            <dd className="mt-1 text-sm text-gray-900">{metrics?.websocket_connections}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Database Queries</dt>
                                            <dd className="mt-1 text-sm text-gray-900">{metrics?.database_queries.toLocaleString()}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Redis Cache Hits</dt>
                                            <dd className="mt-1 text-sm text-gray-900">{metrics?.redis_hits.toLocaleString()}</dd>
                                        </div>
                                        <div>
                                            <dt className="text-sm font-medium text-gray-500">Redis Cache Misses</dt>
                                            <dd className="mt-1 text-sm text-gray-900">{metrics?.redis_misses.toLocaleString()}</dd>
                                        </div>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Settings Tab */}
                {activeTab === 'settings' && (
                    <div className="bg-white shadow rounded-lg">
                        <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg leading-6 font-medium text-gray-900">
                                System Settings
                            </h3>
                            <p className="mt-1 text-sm text-gray-500">
                                Configure system parameters and maintenance tasks
                            </p>
                            <div className="mt-5">
                                <button className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded mr-4">
                                    Clear Cache
                                </button>
                                <button className="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded mr-4">
                                    Restart Services
                                </button>
                                <button className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
                                    Emergency Stop
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Admin;
