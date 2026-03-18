import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const AuthContext = createContext(null);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

/* ── Admin email — this account gets unlimited free access ── */
const ADMIN_EMAIL = 'admin@plumeastrale.fr';

/* ── Demo helpers ── */
const DEMO_KEY = 'pa_demo_user';
const HISTORY_KEY = 'pa_history';
const NOTIF_KEY = 'pa_notifications';

const loadDemoUser = () => {
  try { return JSON.parse(localStorage.getItem(DEMO_KEY)); } catch { return null; }
};

const saveDemoUser = (u) => localStorage.setItem(DEMO_KEY, JSON.stringify(u));

const createDemoUser = (data = {}) => ({
  id: 'demo_' + Date.now(),
  email: data.email || 'demo@plumeastrale.fr',
  name: data.name || 'Utilisateur',
  birth_date: data.birth_date || '1992-05-15',
  birth_time: data.birth_time || '14:30',
  birth_place: data.birth_place || 'Paris',
  birth_country: data.birth_country || 'France',
  created_at: new Date().toISOString(),
  is_demo: true,
});

/* ── History helpers ── */
export const getHistory = () => {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; } catch { return []; }
};

export const addHistory = (entry) => {
  const history = getHistory();
  history.unshift({ ...entry, date: new Date().toISOString(), id: Date.now() });
  if (history.length > 100) history.length = 100;
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
};

/* ── Notification helpers ── */
export const getNotifPrefs = () => {
  try { return JSON.parse(localStorage.getItem(NOTIF_KEY)) || { enabled: false, hour: 8 }; } catch { return { enabled: false, hour: 8 }; }
};

export const setNotifPrefs = (prefs) => {
  localStorage.setItem(NOTIF_KEY, JSON.stringify(prefs));
};

export const requestNotifPermission = async () => {
  if (!('Notification' in window)) return false;
  if (Notification.permission === 'granted') return true;
  const perm = await Notification.requestPermission();
  return perm === 'granted';
};

export const sendNotification = (title, body) => {
  if (Notification.permission === 'granted') {
    new Notification(title, { body, icon: '/favicon.ico', badge: '/favicon.ico' });
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('pa_token'));
  const [creditBalance, setCreditBalance] = useState(0);
  const [loading, setLoading] = useState(true);
  const [isDemo, setIsDemo] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  const authHeader = useCallback(() => {
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
  }, [token]);

  const checkAdmin = (email) => {
    return email && email.toLowerCase() === ADMIN_EMAIL;
  };

  // Fetch user profile on mount / token change
  useEffect(() => {
    // Try real backend first
    if (token && API) {
      axios.get(`${API}/api/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then(res => {
          setUser(res.data.user);
          setCreditBalance(res.data.credit_balance);
          setIsDemo(false);
          setIsAdmin(checkAdmin(res.data.user?.email));
        })
        .catch(() => {
          localStorage.removeItem('pa_token');
          setToken(null);
          // Fall back to demo user if saved
          const demo = loadDemoUser();
          if (demo) {
            setUser(demo);
            setCreditBalance(demo.credits || 20);
            setIsDemo(true);
            setIsAdmin(checkAdmin(demo.email));
          }
        })
        .finally(() => setLoading(false));
      return;
    }

    // No token or no API — check demo user
    const demo = loadDemoUser();
    if (demo) {
      setUser(demo);
      setCreditBalance(demo.credits || 20);
      setIsDemo(true);
      setIsAdmin(checkAdmin(demo.email));
    }
    setLoading(false);
  }, [token]);

  // Check for daily journal notification
  useEffect(() => {
    if (!user) return;
    const prefs = getNotifPrefs();
    if (!prefs.enabled) return;

    const lastNotif = localStorage.getItem('pa_last_notif_date');
    const today = new Date().toISOString().slice(0, 10);
    if (lastNotif === today) return;

    // Send daily notification
    const now = new Date();
    if (now.getHours() >= (prefs.hour || 8)) {
      sendNotification(
        'Plume Astrale — Votre journal du jour',
        'Votre guidance cosmique quotidienne est prête. Découvrez les énergies de la journée.'
      );
      localStorage.setItem('pa_last_notif_date', today);
    }
  }, [user]);

  const register = async (data) => {
    // Try real backend first
    if (API) {
      try {
        const res = await axios.post(`${API}/api/auth/register`, data);
        localStorage.setItem('pa_token', res.data.token);
        setToken(res.data.token);
        setUser(res.data.user);
        setCreditBalance(res.data.credit_balance);
        setIsDemo(false);
        setIsAdmin(checkAdmin(res.data.user?.email));
        return res.data;
      } catch (err) {
        // If backend is unreachable (network error), fall back to demo
        if (!err.response) {
          return registerDemo(data);
        }
        throw err;
      }
    }
    // No API configured — use demo mode
    return registerDemo(data);
  };

  const registerDemo = (data) => {
    const demoUser = createDemoUser(data);
    demoUser.credits = 20;
    saveDemoUser(demoUser);
    setUser(demoUser);
    setCreditBalance(20);
    setIsDemo(true);
    setIsAdmin(checkAdmin(demoUser.email));
    addHistory({ type: 'inscription', label: 'Inscription', service: 'account' });
    return { user: demoUser, credit_balance: 20 };
  };

  const login = async (email, password) => {
    // Try real backend first
    if (API) {
      try {
        const res = await axios.post(`${API}/api/auth/login`, { email, password });
        localStorage.setItem('pa_token', res.data.token);
        setToken(res.data.token);
        setUser(res.data.user);
        setCreditBalance(res.data.credit_balance);
        setIsDemo(false);
        setIsAdmin(checkAdmin(res.data.user?.email));
        return res.data;
      } catch (err) {
        if (!err.response) {
          // Network error — try demo mode
          return loginDemo(email);
        }
        throw err;
      }
    }
    // No API — use demo
    return loginDemo(email);
  };

  const loginDemo = (email) => {
    let demoUser = loadDemoUser();
    if (demoUser && demoUser.email === email) {
      setUser(demoUser);
      setCreditBalance(demoUser.credits || 20);
      setIsDemo(true);
      setIsAdmin(checkAdmin(email));
      return { user: demoUser, credit_balance: demoUser.credits || 20 };
    }
    // Create new demo user with this email
    demoUser = createDemoUser({ email });
    demoUser.credits = 20;
    saveDemoUser(demoUser);
    setUser(demoUser);
    setCreditBalance(20);
    setIsDemo(true);
    setIsAdmin(checkAdmin(email));
    return { user: demoUser, credit_balance: 20 };
  };

  const logout = () => {
    localStorage.removeItem('pa_token');
    localStorage.removeItem(DEMO_KEY);
    setToken(null);
    setUser(null);
    setCreditBalance(0);
    setIsDemo(false);
    setIsAdmin(false);
  };

  const refreshBalance = useCallback(async () => {
    if (isDemo) {
      const demo = loadDemoUser();
      if (demo) setCreditBalance(demo.credits || 0);
      return;
    }
    if (!token) return;
    try {
      const res = await axios.get(`${API}/api/wallet/balance`, { headers: { Authorization: `Bearer ${token}` } });
      setCreditBalance(res.data.credit_balance);
    } catch { /* ignore */ }
  }, [token, isDemo]);

  const useCredits = async (serviceId) => {
    // Admin bypass — free access to everything
    if (isAdmin) {
      addHistory({ type: 'consultation', label: serviceId, service: serviceId, credits: 0, admin: true });
      return { credit_balance: creditBalance };
    }

    if (isDemo) {
      const demo = loadDemoUser();
      const cost = 10; // default cost
      if (!demo || (demo.credits || 0) < cost) {
        throw { response: { data: { detail: 'Crédits insuffisants' } } };
      }
      demo.credits = (demo.credits || 0) - cost;
      saveDemoUser(demo);
      setCreditBalance(demo.credits);
      addHistory({ type: 'consultation', label: serviceId, service: serviceId, credits: cost });
      return { credit_balance: demo.credits };
    }
    const res = await axios.post(`${API}/api/credits/use`, { service_id: serviceId }, { headers: authHeader() });
    setCreditBalance(res.data.credit_balance);
    addHistory({ type: 'consultation', label: serviceId, service: serviceId });
    return res.data;
  };

  const updateDemoProfile = (updates) => {
    if (!isDemo) return;
    const demo = loadDemoUser();
    if (!demo) return;
    const updated = { ...demo, ...updates };
    saveDemoUser(updated);
    setUser(updated);
  };

  const value = {
    user, token, creditBalance, loading, isDemo, isAdmin,
    authHeader, register, login, logout,
    refreshBalance, useCredits, setCreditBalance,
    updateDemoProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
