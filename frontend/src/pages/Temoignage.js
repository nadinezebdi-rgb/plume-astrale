import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

/* ═══════════════════════════════════════════════════════════
   Page /temoignage — Partager mon témoignage
   Accès authentifié uniquement (login required)
   Statut initial "pending" → validation admin dans /admin
   ═══════════════════════════════════════════════════════════ */

const styles = `
  .pat-page{min-height:100vh;background:#0b0f24;color:#e8e6f0;
    font-family:Georgia,'Times New Roman',serif;padding:60px 20px;}
  .pat-wrap{max-width:640px;margin:0 auto;}
  .pat-title{font-size:clamp(1.8rem,3vw,2.4rem);color:#c9a24b;margin:0 0 14px;line-height:1.2;}
  .pat-lead{color:#b8b4c9;font-size:1rem;margin:0 0 28px;}
  .pat-form{background:rgba(20,26,51,.7);border:1px solid rgba(201,162,75,.25);
    border-radius:16px;padding:28px;display:flex;flex-direction:column;gap:14px;}
  .pat-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
  @media(max-width:520px){.pat-row{grid-template-columns:1fr;}}
  .pat-label{font-size:.78rem;color:#b8b4c9;letter-spacing:.08em;
    text-transform:uppercase;margin-bottom:6px;display:block;}
  .pat-input,.pat-ta{background:rgba(11,15,36,.7);border:1px solid rgba(201,162,75,.2);
    color:#e8e6f0;padding:12px 14px;border-radius:10px;
    font-family:Georgia,serif;font-size:.95rem;width:100%;box-sizing:border-box;}
  .pat-input:focus,.pat-ta:focus{outline:none;border-color:#c9a24b;
    box-shadow:0 0 0 3px rgba(201,162,75,.15);}
  .pat-ta{min-height:120px;resize:vertical;}
  .pat-count{font-size:.75rem;color:#7d7a90;text-align:right;margin-top:2px;}
  .pat-cta{background:linear-gradient(135deg,#c9a24b,#e2c07c);color:#1a1030;
    font-weight:600;padding:14px 24px;border-radius:999px;border:none;cursor:pointer;
    font-size:1rem;letter-spacing:.02em;font-family:Georgia,serif;
    box-shadow:0 4px 20px rgba(201,162,75,.35);transition:transform .18s ease;}
  .pat-cta:hover{transform:translateY(-2px);}
  .pat-cta:disabled{opacity:.6;cursor:not-allowed;transform:none;}
  .pat-note{color:#b8b4c9;font-size:.82rem;text-align:center;margin-top:12px;}
  .pat-ok{background:rgba(74,222,128,.1);border:1px solid rgba(74,222,128,.3);
    color:#4ADE80;padding:14px 18px;border-radius:12px;font-size:.95rem;}
  .pat-err{background:rgba(248,113,113,.1);border:1px solid rgba(248,113,113,.35);
    color:#f87171;padding:10px 14px;border-radius:8px;font-size:.88rem;}
  .pat-link{color:#c9a24b;text-decoration:none;border-bottom:1px dashed rgba(201,162,75,.4);}
`;

export default function Temoignage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [form, setForm] = useState({
    name: '', sign: '', city: '', quote: '',
    transform_before: '', transform_after: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Pré-remplissage depuis email J+2 (?prenom=Camille&session=xxx&utm_source=email)
  useEffect(() => {
    const prenomQ = params.get('prenom');
    if (prenomQ) {
      setForm((s) => (s.name ? s : { ...s, name: prenomQ }));
    }
  }, [params]);

  useEffect(() => {
    if (!user) {
      const t = setTimeout(() => navigate('/connexion?redirect=/temoignage'), 1200);
      return () => clearTimeout(t);
    }
  }, [user, navigate]);

  const upd = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    if (form.name.length < 2 || form.quote.length < 20) {
      setError('Prénom (min 2) et témoignage (min 20 caractères) requis.');
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API}/api/landing/testimonials`, form, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur envoi. Réessaie dans quelques instants.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SEO path="/temoignage" title="Partager mon témoignage · Plume Astrale"
        description="Ton retour aide d'autres femmes à se lancer. Partage ce que ta lecture t'a apporté." />
      <style>{styles}</style>
      <div className="pat-page" data-testid="temoignage-page">
        <div className="pat-wrap">
          {!user ? (
            <>
              <h1 className="pat-title">Connecte-toi pour partager</h1>
              <p className="pat-lead">On te redirige vers la page de connexion…</p>
            </>
          ) : success ? (
            <>
              <h1 className="pat-title">Merci pour ton témoignage 🌙</h1>
              <div className="pat-ok" data-testid="temoignage-success">
                Ton témoignage a été envoyé à Soléna pour validation. Il apparaîtra sur la page
                d&apos;accueil dans les prochaines heures.
              </div>
              <p className="pat-note" style={{ marginTop: 20 }}>
                <Link to="/mon-compte" className="pat-link">Retour à mon espace</Link>
              </p>
            </>
          ) : (
            <>
              <h1 className="pat-title">Partager mon témoignage</h1>
              <p className="pat-lead">
                Ton retour aide d&apos;autres femmes à se lancer.
                Reste simple et sincère — pas besoin d&apos;en faire trop.
              </p>
              <form className="pat-form" onSubmit={submit} data-testid="temoignage-form">
                <div className="pat-row">
                  <div>
                    <label className="pat-label">Prénom (obligatoire)</label>
                    <input className="pat-input" value={form.name}
                      onChange={(e) => upd('name', e.target.value)}
                      maxLength={60} required data-testid="temoignage-name" />
                  </div>
                  <div>
                    <label className="pat-label">Signe astro (optionnel)</label>
                    <input className="pat-input" value={form.sign}
                      onChange={(e) => upd('sign', e.target.value)}
                      placeholder="Poissons, Lion…" maxLength={20} data-testid="temoignage-sign" />
                  </div>
                </div>
                <div>
                  <label className="pat-label">Ville (optionnel)</label>
                  <input className="pat-input" value={form.city}
                    onChange={(e) => upd('city', e.target.value)}
                    placeholder="Lyon, Bordeaux…" maxLength={60} data-testid="temoignage-city" />
                </div>
                <div>
                  <label className="pat-label">Ton témoignage (min 20 caractères)</label>
                  <textarea className="pat-ta" value={form.quote}
                    onChange={(e) => upd('quote', e.target.value)}
                    placeholder="Ce que la lecture t'a permis de comprendre ou d'apaiser…"
                    minLength={20} maxLength={500} required data-testid="temoignage-quote" />
                  <div className="pat-count">{form.quote.length} / 500</div>
                </div>
                <div className="pat-row">
                  <div>
                    <label className="pat-label">Avant (optionnel)</label>
                    <input className="pat-input" value={form.transform_before}
                      onChange={(e) => upd('transform_before', e.target.value)}
                      placeholder="Où tu en étais avant la lecture" maxLength={200}
                      data-testid="temoignage-before" />
                  </div>
                  <div>
                    <label className="pat-label">Après (optionnel)</label>
                    <input className="pat-input" value={form.transform_after}
                      onChange={(e) => upd('transform_after', e.target.value)}
                      placeholder="Ce qui a changé depuis" maxLength={200}
                      data-testid="temoignage-after" />
                  </div>
                </div>
                {error && <div className="pat-err" data-testid="temoignage-error">{error}</div>}
                <button type="submit" className="pat-cta" disabled={loading}
                  data-testid="temoignage-submit">
                  {loading ? 'Envoi…' : 'Envoyer mon témoignage'}
                </button>
                <p className="pat-note">
                  Soléna valide chaque témoignage avant publication. Ton email n&apos;apparaîtra jamais.
                </p>
              </form>
            </>
          )}
        </div>
      </div>
    </>
  );
}
