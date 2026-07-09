import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import CercleSales from './CercleSales';
import CercleDashboard from '@/components/CercleDashboard';
import { Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Page /cercle :
 * - non connecté ou non-premium → CercleSales (page de vente)
 * - connecté + premium (is_premium ou admin) → CercleDashboard (rituel quotidien)
 *
 * Source de vérité : GET /api/premium/status (au lieu de user.is_premium qui peut être stale).
 */
export default function Cercle() {
  const { token, user, loading: authLoading } = useAuth();
  const [premium, setPremium] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!token || !user) {
      setPremium(false);
      setLoading(false);
      return;
    }
    // user is loaded — check admin first (synchronous)
    if (user.is_admin) {
      setPremium(true);
      setLoading(false);
      return;
    }
    axios
      .get(`${API}/api/premium/status`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => setPremium(!!r.data.is_premium))
      .catch(() => setPremium(!!user?.is_premium))
      .finally(() => setLoading(false));
  }, [token, authLoading, user]);

  if (loading || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" data-testid="cercle-gate-loading">
        <Loader2 className="w-6 h-6 animate-spin" style={{ color: '#D4AF37' }} />
      </div>
    );
  }

  return (
    <>
      <SEO path="/cercle" />
      {premium ? <CercleDashboard /> : <CercleSales />}
    </>
  );
}
