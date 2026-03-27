import React, { useState } from 'react';
import { Download, Share2, Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || '';

const ShareableCard = () => {
  const { isAuthenticated, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateCard = async () => {
    if (!isAuthenticated || !user) return;
    setLoading(true);
    setError('');

    try {
      const userData = {
        prenom: user.email?.split('@')[0] || 'Voyageur',
        dateNaissance: user.birth_date || '1990-01-01',
        heureNaissance: user.birth_time || '12:00',
        ville: user.birth_place || 'Paris',
      };

      const response = await axios.post(`${API}/api/share/generate-card`, { user_data: userData }, {
        responseType: 'blob',
        headers: { Authorization: `Bearer ${localStorage.getItem('plume_token')}` },
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `profil_cosmique_${userData.prenom}.png`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Impossible de generer la carte. Reessayez.');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="flex flex-col items-center gap-3" data-testid="shareable-card">
      <button
        onClick={generateCard}
        disabled={loading}
        className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-sm font-medium transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
        style={{
          background: 'rgba(232,121,249,0.12)',
          border: '1px solid rgba(232,121,249,0.3)',
          color: '#E879F9',
          fontFamily: 'Inter, sans-serif',
        }}
        data-testid="download-card-btn"
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Download className="w-4 h-4" />
        )}
        {loading ? 'Generation...' : 'Telecharger ma carte cosmique'}
      </button>
      {error && (
        <p className="text-xs" style={{ color: '#E879F9' }}>{error}</p>
      )}
      <p className="text-xs" style={{ color: 'rgba(248,250,252,0.35)', fontFamily: 'Inter, sans-serif' }}>
        Image 1080x1080 — partagez sur vos reseaux
      </p>
    </div>
  );
};

export default ShareableCard;
