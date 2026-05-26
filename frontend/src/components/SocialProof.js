import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Users } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/** Auto-hidden si activite < seuil (100). N'affiche jamais "1 personne". */
export default function SocialProof() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let cancelled = false;
    axios.get(`${API}/api/stats/social-proof`)
      .then(r => { if (!cancelled) setData(r.data); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  if (!data || !data.visible) return null;

  return (
    <div
      data-testid="social-proof-badge"
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 8,
        padding: '6px 14px', borderRadius: 999,
        background: 'rgba(212,180,106,0.1)',
        border: '1px solid rgba(212,180,106,0.3)',
        fontSize: 11, letterSpacing: '0.06em',
        color: 'rgba(212,180,106,0.95)',
        fontFamily: 'Cinzel, serif',
      }}>
      <Users style={{ width: 11, height: 11 }} strokeWidth={1.5} />
      <span>{data.label}</span>
    </div>
  );
}
