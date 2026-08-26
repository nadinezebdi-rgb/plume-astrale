import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Gift, Loader2, Download } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * /carte-cadeau/redeem/{code} — le destinataire renseigne SES données pour recevoir son livre.
 */
export default function GiftCardRedeem() {
  const { code } = useParams();
  const [card, setCard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({
    first_name: '',
    birth_date: '',
    birth_time: '',
    birth_place: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!code) return;
    fetch(`${API}/api/gift-cards/${code}`)
      .then(async (r) => {
        if (!r.ok) throw new Error((await r.json()).detail || 'Cadeau introuvable');
        return r.json();
      })
      .then((d) => {
        setCard(d);
        if (d.recipient_first_name) setForm((f) => ({ ...f, first_name: d.recipient_first_name }));
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [code]);

  async function submit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/gift-cards/${code}/redeem`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Génération impossible pour l\'instant.');
        setSubmitting(false);
        return;
      }
      setResult(data);
      setSubmitting(false);
    } catch (err) {
      setError('Connexion interrompue. Réessayez.');
      setSubmitting(false);
    }
  }

  return (
    <PsPageShell background="dark">
      <SEO path={`/carte-cadeau/redeem/${code}`} title="Recevoir mon livre Plume Astrale" description="Complétez vos données pour recevoir votre livre offert." />
      <div style={{ maxWidth: 640, margin: '0 auto', padding: '64px 24px', color: '#F5EEE0', fontFamily: '"Cormorant Garamond", serif' }}>
        {loading && (
          <div data-testid="gift-redeem-loading" style={{ textAlign: 'center', padding: 60 }}>
            <Loader2 size={28} className="animate-spin" />
            <p>Chargement de votre cadeau…</p>
          </div>
        )}

        {!loading && error && !card && (
          <div data-testid="gift-redeem-error" style={{ textAlign: 'center', padding: 40 }}>
            <Gift size={40} color="#D4AF37" strokeWidth={1.4} style={{ opacity: 0.4 }} />
            <h1 style={{ fontFamily: '"Playfair Display", serif', fontSize: '1.8rem', marginTop: 20 }}>
              Ce code ne correspond à aucun cadeau
            </h1>
            <p style={{ color: '#B9B0D5' }}>{error}</p>
            <p style={{ color: '#B9B0D5', fontSize: '0.9rem', marginTop: 16 }}>
              Vérifiez que le code est correctement recopié, ou écrivez-nous à{' '}
              <a href="mailto:contact@plume-astrale.fr" style={{ color: '#D4AF37' }}>contact@plume-astrale.fr</a>.
            </p>
          </div>
        )}

        {!loading && card && (result || card.already_redeemed) && (
          <div data-testid="gift-redeem-success" style={{ textAlign: 'center', padding: 20 }}>
            <Gift size={44} color="#D4AF37" strokeWidth={1.4} />
            <h1 style={{ fontFamily: '"Playfair Display", serif', fontSize: '2rem', marginTop: 20 }}>
              Votre livre est prêt
            </h1>
            <p style={{ color: '#B9B0D5', lineHeight: 1.6, maxWidth: 480, margin: '16px auto 24px' }}>
              {card.purchaser_first_name} vous offre <em>{card.product_label}</em>.
              Cliquez pour ouvrir votre livre — pensez à le sauvegarder.
            </p>
            <a
              href={(result && result.pdf_url) || card.redeemed_pdf_url}
              target="_blank" rel="noreferrer"
              data-testid="gift-redeem-download"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 10,
                padding: '14px 28px', background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                color: '#0F1A3C', textDecoration: 'none', borderRadius: 4,
                fontFamily: '"Cinzel", serif', fontSize: '0.9rem', letterSpacing: 3,
              }}
            >
              <Download size={16} /> OUVRIR MON LIVRE
            </a>
          </div>
        )}

        {!loading && card && !result && !card.already_redeemed && (
          <>
            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <Gift size={40} color="#D4AF37" strokeWidth={1.4} />
              <h1 style={{ fontFamily: '"Playfair Display", serif', fontSize: '2rem', margin: '18px 0 6px' }}>
                {card.purchaser_first_name} vous offre <em>{card.product_label}</em>
              </h1>
              {card.personal_message && (
                <blockquote style={{
                  borderLeft: '3px solid #D4AF37', padding: '12px 20px', margin: '24px auto',
                  maxWidth: 480, textAlign: 'left', fontStyle: 'italic', color: '#B9B0D5',
                }}>
                  {card.personal_message}
                </blockquote>
              )}
              <p style={{ color: '#B9B0D5', fontSize: '0.95rem' }}>
                Complétez vos données de naissance ci-dessous — le livre est composé en quelques minutes.
              </p>
            </div>

            <form onSubmit={submit} data-testid="gift-redeem-form" style={{ display: 'grid', gap: 16 }}>
              <input required placeholder="Votre prénom" value={form.first_name}
                     onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                     data-testid="gift-redeem-firstname" style={inputStyle} />
              <div style={rowStyle}>
                <label style={{ display: 'grid', gap: 4 }}>
                  <small style={smallLabel}>Date de naissance</small>
                  <input required type="date" value={form.birth_date}
                         onChange={(e) => setForm({ ...form, birth_date: e.target.value })}
                         data-testid="gift-redeem-birthdate" style={inputStyle} />
                </label>
                <label style={{ display: 'grid', gap: 4 }}>
                  <small style={smallLabel}>Heure (si connue)</small>
                  <input type="time" value={form.birth_time}
                         onChange={(e) => setForm({ ...form, birth_time: e.target.value })}
                         data-testid="gift-redeem-birthtime" style={inputStyle} />
                </label>
              </div>
              <input required placeholder="Ville de naissance" value={form.birth_place}
                     onChange={(e) => setForm({ ...form, birth_place: e.target.value })}
                     data-testid="gift-redeem-birthplace" style={inputStyle} />

              {error && (
                <div style={{ padding: 14, background: 'rgba(220,60,60,0.12)', border: '1px solid rgba(220,60,60,0.4)', borderRadius: 4, color: '#F5C6C6' }}>
                  {error}
                </div>
              )}

              <button type="submit" disabled={submitting} data-testid="gift-redeem-submit"
                      style={{
                        padding: '16px 32px', background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                        color: '#0F1A3C', border: 'none', borderRadius: 4,
                        cursor: submitting ? 'wait' : 'pointer',
                        fontFamily: '"Cinzel", serif', fontSize: '0.95rem', letterSpacing: 3,
                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 10,
                      }}>
                {submitting ? <><Loader2 size={16} className="animate-spin" /> Composition en cours…</> : 'RECEVOIR MON LIVRE'}
              </button>
            </form>
          </>
        )}
      </div>
    </PsPageShell>
  );
}

const inputStyle = {
  padding: '12px 14px', background: 'rgba(15,26,60,0.55)',
  border: '1px solid rgba(212,175,55,0.28)', borderRadius: 4,
  color: '#F5EEE0', fontSize: '1rem', fontFamily: '"Cormorant Garamond", serif',
  width: '100%', boxSizing: 'border-box',
};
const rowStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 };
const smallLabel = { color: '#B9B0D5', fontSize: '0.78rem', letterSpacing: 1 };
