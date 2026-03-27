import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [creditBalance, setCreditBalance] = useState(0);
  const [loading, setLoading] = useState(true);

  // Restore user from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem('plume_astrale_data');
      if (stored) {
        const parsed = JSON.parse(stored);
        setUser(parsed);
        const balance = parseInt(localStorage.getItem('plume_astrale_credits') || '3', 10);
        setCreditBalance(balance);
      }
    } catch { /* ignore */ }
    setLoading(false);
  }, []);

  const register = async (data) => {
    const userData = {
      email: data.email || 'Utilisateur',
      prenom: data.email?.split('@')[0] || 'Utilisateur',
      ...data,
    };
    localStorage.setItem('plume_astrale_data', JSON.stringify(userData));
    localStorage.setItem('plume_astrale_paid', 'false');
    localStorage.setItem('plume_astrale_plan', 'free');
    localStorage.setItem('plume_astrale_credits', '3');
    setUser(userData);
    setCreditBalance(3);
    return { user: userData, credit_balance: 3 };
  };

  const login = async (email, password) => {
    // Check if user was previously registered in localStorage
    const stored = localStorage.getItem('plume_astrale_data');
    if (stored) {
      const parsed = JSON.parse(stored);
      if (parsed.email === email) {
        setUser(parsed);
        const balance = parseInt(localStorage.getItem('plume_astrale_credits') || '3', 10);
        setCreditBalance(balance);
        return { user: parsed, credit_balance: balance };
      }
    }
    // Allow login with any email/password for demo (store locally)
    const userData = {
      email,
      prenom: email.split('@')[0] || 'Utilisateur',
    };
    localStorage.setItem('plume_astrale_data', JSON.stringify(userData));
    localStorage.setItem('plume_astrale_credits', '3');
    setUser(userData);
    setCreditBalance(3);
    return { user: userData, credit_balance: 3 };
  };

  const logout = () => {
    localStorage.removeItem('plume_astrale_data');
    localStorage.removeItem('plume_astrale_paid');
    localStorage.removeItem('plume_astrale_plan');
    localStorage.removeItem('plume_astrale_credits');
    setUser(null);
    setCreditBalance(0);
  };

  const refreshBalance = useCallback(async () => {
    const balance = parseInt(localStorage.getItem('plume_astrale_credits') || '0', 10);
    setCreditBalance(balance);
  }, []);

  const useCredits = async (serviceId) => {
    const current = parseInt(localStorage.getItem('plume_astrale_credits') || '0', 10);
    if (current <= 0) throw new Error('Pas assez de crédits');
    const newBalance = current - 1;
    localStorage.setItem('plume_astrale_credits', String(newBalance));
    setCreditBalance(newBalance);
    return { credit_balance: newBalance };
  };

  const authHeader = useCallback(() => {
    return {};
  }, []);

  const value = {
    user, token: null, creditBalance, loading,
    authHeader, register, login, logout,
    refreshBalance, useCredits, setCreditBalance,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
