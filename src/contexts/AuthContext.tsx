import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface User {
    id: number;
    email: string;
    username: string;
    full_name?: string;
    role: string;
    is_active: boolean;
    is_verified: boolean;
    telegram_enabled: boolean;
    email_enabled: boolean;
    created_at: string;
    last_login?: string;
}

interface AuthContextType {
    user: User | null;
    accessToken: string | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
    logout: () => void;
    updateUser: (data: Partial<User>) => Promise<void>;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [accessToken, setAccessToken] = useState<string | null>(
        localStorage.getItem('accessToken')
    );
    const [refreshToken, setRefreshToken] = useState<string | null>(
        localStorage.getItem('refreshToken')
    );
    const [loading, setLoading] = useState(true);

    // Configure axios defaults
    useEffect(() => {
        if (accessToken) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
        } else {
            delete axios.defaults.headers.common['Authorization'];
        }
    }, [accessToken]);

    // Load user on mount
    useEffect(() => {
        const loadUser = async () => {
            if (accessToken) {
                try {
                    const response = await axios.get(`${API_URL}/auth/me`);
                    setUser(response.data);
                } catch (error) {
                    console.error('Failed to load user:', error);
                    // Try to refresh token
                    if (refreshToken) {
                        try {
                            await refreshAccessToken();
                        } catch (refreshError) {
                            // Refresh failed, logout
                            logout();
                        }
                    } else {
                        logout();
                    }
                }
            }
            setLoading(false);
        };

        loadUser();
    }, []);

    const refreshAccessToken = async () => {
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        try {
            const response = await axios.post(`${API_URL}/auth/refresh`, {
                refresh_token: refreshToken
            });

            const { access_token, refresh_token: new_refresh_token } = response.data;

            setAccessToken(access_token);
            setRefreshToken(new_refresh_token);
            localStorage.setItem('accessToken', access_token);
            localStorage.setItem('refreshToken', new_refresh_token);

            // Load user with new token
            const userResponse = await axios.get(`${API_URL}/auth/me`, {
                headers: { Authorization: `Bearer ${access_token}` }
            });
            setUser(userResponse.data);
        } catch (error) {
            console.error('Token refresh failed:', error);
            throw error;
        }
    };

    const login = async (email: string, password: string) => {
        try {
            const response = await axios.post(`${API_URL}/auth/login`, {
                email,
                password
            });

            const { access_token, refresh_token } = response.data;

            setAccessToken(access_token);
            setRefreshToken(refresh_token);
            localStorage.setItem('accessToken', access_token);
            localStorage.setItem('refreshToken', refresh_token);

            // Load user data
            const userResponse = await axios.get(`${API_URL}/auth/me`, {
                headers: { Authorization: `Bearer ${access_token}` }
            });
            setUser(userResponse.data);
        } catch (error: any) {
            console.error('Login failed:', error);
            throw new Error(error.response?.data?.detail || 'Login failed');
        }
    };

    const register = async (
        email: string,
        username: string,
        password: string,
        fullName?: string
    ) => {
        try {
            const response = await axios.post(`${API_URL}/auth/register`, {
                email,
                username,
                password,
                full_name: fullName
            });

            // Auto-login after registration
            await login(email, password);
        } catch (error: any) {
            console.error('Registration failed:', error);
            throw new Error(error.response?.data?.detail || 'Registration failed');
        }
    };

    const logout = () => {
        setUser(null);
        setAccessToken(null);
        setRefreshToken(null);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        delete axios.defaults.headers.common['Authorization'];
    };

    const updateUser = async (data: Partial<User>) => {
        try {
            const response = await axios.put(`${API_URL}/auth/me`, data);
            setUser(response.data);
        } catch (error: any) {
            console.error('Update user failed:', error);
            throw new Error(error.response?.data?.detail || 'Update failed');
        }
    };

    const value: AuthContextType = {
        user,
        accessToken,
        loading,
        login,
        register,
        logout,
        updateUser,
        isAuthenticated: !!user
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

