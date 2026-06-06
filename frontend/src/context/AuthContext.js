import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { supabase } from '@/lib/supabase';

const API = process.env.REACT_APP_BACKEND_URL;
const NATAL_LS_KEY = 'plume_astrale_data';
const AuthContext = createContext(null);

// Sync profile data -> localStorage so legacy pages (Horoscope/Tarot/etc.) read the right data.
// Always overwrite when a user is logged in to prevent leftover data from another session (e.g. "Saida").
const hydrateNatalLocalStorage = (user) => {
  if (!user) return;
  try {
    if (!user.birth_date) {
      // Logged-in user has no natal data yet -> clear any leftover rogue data
      localStorage.removeItem(NATAL_LS_KEY);
      return;
    }
    const payload = {
      prenom: user.prenom || '',
      genre: user.gender || 'female',
      email: user.email || '',
      dateNaissance: user.birth_date || '',
      heureNaissance: user.birth_time || '',
      ville: user.birth_place || '',
      pays: user.birth_country || '',
    };
    localStorage.setItem(NATAL_LS_KEY, JSON.stringify(payload));
  } catch {}
};

const clearNatalLocalStorage = () => {
  try { localStorage.removeItem(NATAL_LS_KEY); } catch {}
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

export const AuthProvider = ({ children }) => {
  const [session, setSession] = useState(null);
  const [user, setUser] = useState(null);
  const [creditBalance, setCreditBalance] = useState(0);
  const [loading, setLoading] = useState(true);

  const token = session?.access_token || null;

  const authHeader = useCallback(() => {
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
  }, [token]);

  // Charger profil + balance depuis backend
  const loadMe = useCallback(async (accessToken) => {
    if (!accessToken) {
      setUser(null);
      setCreditBalance(0);
      return;
    }
    try {
      const res = await axios.get(`${API}/api/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setUser(res.data.user);
      setCreditBalance(res.data.credit_balance ?? 0);
      hydrateNatalLocalStorage(res.data.user);
    } catch (err) {
      console.warn('loadMe failed', err);
      setUser(null);
      setCreditBalance(0);
    }
  }, []);

  // Init : recuperer session existante + s'abonner aux changements
  useEffect(() => {
    let mounted = true;

    supabase.auth.getSession().then(({ data }) => {
      if (!mounted) return;
      setSession(data.session);
      loadMe(data.session?.access_token).finally(() => {
        if (mounted) setLoading(false);
      });
    });

    const { data: sub } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      loadMe(newSession?.access_token);
    });

    return () => {
      mounted = false;
      sub.subscription.unsubscribe();
    };
  }, [loadMe]);

  const register = async (data) => {
    const { email, password, ...profileData } = data;
    const { data: signUpData, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: profileData },
    });
    if (error) throw new Error(error.message);

    // Si la session est creee immediatement (confirmation desactivee), on synchronise le profil
    const newSession = signUpData.session;
    if (newSession) {
      try {
        await axios.put(
          `${API}/api/auth/profile`,
          {
            prenom: profileData.prenom,
            birth_date: profileData.birth_date,
            birth_time: profileData.birth_time,
            birth_place: profileData.birth_place,
            birth_country: profileData.birth_country,
            latitude: profileData.latitude,
            longitude: profileData.longitude,
            gender: profileData.gender,
          },
          { headers: { Authorization: `Bearer ${newSession.access_token}` } }
        );
      } catch (e) { /* ignore */ }
      setSession(newSession);
      await loadMe(newSession.access_token);
    }
    return signUpData;
  };

  const login = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw new Error(error.message);
    setSession(data.session);
    await loadMe(data.session?.access_token);
    return data;
  };

  const logout = async () => {
    await supabase.auth.signOut();
    setSession(null);
    setUser(null);
    setCreditBalance(0);
    clearNatalLocalStorage();
  };

  // Update natal/profile fields and re-sync localStorage
  const updateProfile = async (fields) => {
    if (!token) throw new Error('Non authentifié');
    const res = await axios.put(`${API}/api/auth/profile`, fields, { headers: authHeader() });
    await loadMe(token);
    return res.data;
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
    user,
    session,
    token,
    creditBalance,
    loading,
    authHeader,
    register,
    login,
    logout,
    updateProfile,
    refreshBalance,
    useCredits,
    setCreditBalance,
    isAuthenticated: !!user,
        setUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
