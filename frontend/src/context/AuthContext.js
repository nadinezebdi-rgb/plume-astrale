import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || '';

const AuthContext = createContext(null);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('pa_token'));
  const [creditBalance, setCreditBalance] = useState(0);
  const [loading, setLoading] = useState(true);

  const authHeader = useCallback(() => {
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
  }, [token]);

  // Fetch user profile on mount / token change
  useEffect(() => {
    if (!token) { setLoading(false); return; }
    axios.get(`${API}/api/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => {
        setUser(res.data.user);
        setCreditBalance(res.data.credit_balance);
      })
      .catch(() => { localStorage.removeItem('pa_token'); setToken(null); })
      .finally(() => setLoading(false));
  }, [token]);

  const register = async (data) => {
    const res = await axios.post(`${API}/api/auth/register`, data);
    localStorage.setItem('pa_token', res.data.token);
    setToken(res.data.token);
    setUser(res.data.user);
    setCreditBalance(res.data.credit_balance);
    return res.data;
  };

  const login = async (email, password) => {
    const res = await axios.post(`${API}/api/auth/login`, { email, password });
    localStorage.setItem('pa_token', res.data.token);
    setToken(res.data.token);
    setUser(res.data.user);
    setCreditBalance(res.data.credit_balance);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('pa_token');
    setToken(null);
    setUser(null);
    setCreditBalance(0);
  };

  const refreshBalance = useCallback(async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API}/api/wallet/balance`, { headers: { Authorization: `Bearer ${token}` } });
      setCreditBalance(res.data.credit_balance);
    } catch { /* ignore */ }
  }, [token]);

  const useCredits = async (serviceId) => {
    const res = await axios.post(`${API}/api/credits/use`, { service_id: serviceId }, { headers: authHeader() });
    setCreditBalance(res.data.credit_balance);
    return res.data;
  };

  const value = {
    user, token, creditBalance, loading,
    authHeader, register, login, logout,
    refreshBalance, useCredits, setCreditBalance,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
