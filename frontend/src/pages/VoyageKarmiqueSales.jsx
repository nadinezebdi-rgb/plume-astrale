import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, Compass, ShieldCheck, Clock, Mail } from 'lucide-react';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * VoyageKarmique — Page de vente Nocturne Éditorial (49€)
 * Fusion Kabbale (39€) + Karma Destin (24€) — économie de 14€.
 */
export default function VoyageKarmiqueSales() {
  const [form, setForm] = useState({
    email: '', first_name: '', birth_date: '', birth_time: '', birth_city: '',
  });
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');

  function upd(k) {
    return (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  }

  async function submit(e) {
    e.preventDefault();
    if (!form.email || !form.first_name || !form.birth_date || !form.birth_time) {
      setErr('Prénom, date, heure et email sont nécessaires.');
      return;
    }
    setLoading(true); setErr('');
    try {
      const r = await fetch(`${API}/api/voyage-karmique/checkout`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, origin_url: window.location.origin }),
      });
      const d = await r.json();
      if (!r.ok || !d.url) {
        setErr(d?.detail || 'Impossible de créer la session Stripe.');
        setLoading(false);
        return;
      }
      window.location.href = d.url;
    } catch {
      setErr('La connexion s\'est interrompue. Réessayez.');
      setLoading(false);
    }
  }

  return (
    <div data-testid="voyage-karmique-sales">
      <SEO
        path="/voyage-karmique"
        title="Voyage Karmique · Arbre de Vie + Lignée d'Âme — 49 € · Plume Astrale"
        description="Deux livres réunis en un seul voyage. Votre Arbre de Vie Kabbalistique et votre Lignée Karmique, composés à la main, livrés en PDF premium. 49 € au lieu de 63 €."
      />

      {/* ═══ HERO ═══ */}
      <section className="ne-section ne-section-night" style={{ paddingTop: 'clamp(96px, 12vh, 160px)' }}>
        <div className="ne-container">
          <div style={{ maxWidth: 820 }}>
            <div className="ne-overline ne-reveal ne-reveal-1">Livre I & II &middot; Voyage Karmique</div>
            <h1 className="ne-display ne-reveal ne-reveal-2" style={{ marginTop: 24, color: 'var(--ne-celeste)' }}>
              Deux livres,
              <br />
              <span className="ne-serif-italic" style={{ color: 'var(--ne-laiton)' }}>un seul voyage.</span>
            </h1>
            <hr className="ne-rule-short ne-reveal ne-reveal-3" style={{ marginTop: 40, marginBottom: 32 }} />
            <p className="ne-lead ne-reveal ne-reveal-4" style={{ marginBottom: 48, maxWidth: 640 }}>
              Votre <em>Arbre de Vie Kabbalistique</em> — dix Sephiroth, vingt-deux chemins.
              Votre <em>Lignée Karmique</em> — Nœuds lunaires, Saturne, Chiron, Pluton.
              Deux textes composés pour vous seul(e), réunis en un seul écrin.
            </p>

            <div className="ne-reveal ne-reveal-5" style={{
              display: 'inline-flex', alignItems: 'baseline', gap: 20,
              padding: '20px 32px', border: '1px solid rgba(184,147,90,0.35)',
              borderRadius: 2, background: 'rgba(184,147,90,0.05)',
            }}>
              <span style={{ fontFamily: 'var(--ne-serif)', fontSize: 44, color: 'var(--ne-laiton)', fontWeight: 400 }}>49&nbsp;€</span>
              <span style={{ textDecoration: 'line-through', color: 'rgba(245,240,230,0.5)', fontFamily: 'var(--ne-sans)', fontSize: 14 }}>
                au lieu de 63&nbsp;€
              </span>
              <span className="ne-mono" style={{ fontSize: 10, letterSpacing: '0.22em', color: 'var(--ne-laiton)', textTransform: 'uppercase' }}>
                &minus;22&nbsp;%
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ LES DEUX LIVRES ═══ */}
      <section className="ne-section ne-section-paper" data-testid="voyage-livres">
        <div className="ne-container">
          <div style={{ maxWidth: 720, marginBottom: 80 }}>
            <div className="ne-overline">Le voyage en deux temps</div>
            <h2 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-fusain)' }}>
              Une <span className="ne-serif-italic" style={{ color: 'var(--ne-vigne)' }}>essence</span>.
              Une <span className="ne-serif-italic" style={{ color: 'var(--ne-vigne)' }}>direction</span>.
            </h2>
          </div>

          <div className="ne-grid-2" style={{ gap: 32 }}>
            {[
              {
                n: 'Livre I',
                titre: 'Arbre de Vie Kabbalistique',
                murmure: 'Ce qui rayonne en vous — vos dix Sephiroth, vos vingt-deux chemins.',
                bullets: [
                  '10 Sephiroth personnalisées à partir de votre thème natal',
                  '22 chemins hébraïques que vos planètes activent',
                  'Le Da\'at, votre pont vers la Connaissance intérieure',
                  'Trois rituels d\'intégration à pratiquer sur 7 jours',
                ],
                pages: '15 pages, format livre',
                icon: BookOpen,
              },
              {
                n: 'Livre II',
                titre: 'Lignée Karmique & Destinée',
                murmure: 'Ce que votre âme cherche — la direction que vous avez choisie avant même de naître.',
                bullets: [
                  'Vos Nœuds lunaires (Nord et Sud) et leur récit',
                  'Saturne, Chiron, Pluton — les gardiens de votre traversée',
                  'Vos mémoires karmiques dominantes',
                  'Le sens spirituel profond de cette incarnation',
                ],
                pages: '15 pages, format livre',
                icon: Compass,
              },
            ].map((b) => {
              const Icon = b.icon;
              return (
                <div key={b.n} className="ne-card" data-testid={`voyage-livre-${b.n.replace(' ', '-')}`} style={{ padding: 40 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
                    <div className="ne-mono" style={{ fontSize: 11, letterSpacing: '0.28em', color: 'var(--ne-laiton)' }}>
                      {b.n}
                    </div>
                    <Icon style={{ width: 22, height: 22, color: 'var(--ne-laiton)' }} strokeWidth={1.4} />
                  </div>
                  <h3 className="ne-h2" style={{ color: 'var(--ne-fusain)', fontSize: 28, marginBottom: 12 }}>
                    {b.titre}
                  </h3>
                  <p className="ne-serif-italic" style={{ color: 'rgba(10,10,15,0.72)', fontSize: 18, lineHeight: 1.5, marginBottom: 24 }}>
                    {b.murmure}
                  </p>
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0, marginBottom: 24 }}>
                    {b.bullets.map((bl, i) => (
                      <li key={i} style={{ display: 'flex', gap: 12, fontFamily: 'var(--ne-sans)', fontSize: 14, lineHeight: 1.6, color: 'rgba(10,10,15,0.78)', marginBottom: 10 }}>
                        <span style={{ color: 'var(--ne-laiton)', flexShrink: 0 }}>—</span>
                        {bl}
                      </li>
                    ))}
                  </ul>
                  <div className="ne-caption" style={{ borderTop: '1px solid var(--ne-velin)', paddingTop: 16 }}>
                    {b.pages}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ FORMULAIRE CHECKOUT ═══ */}
      <section className="ne-section ne-section-night" data-testid="voyage-form">
        <div className="ne-container">
          <div style={{ maxWidth: 640 }}>
            <div className="ne-overline">Commencer le voyage</div>
            <h2 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-celeste)' }}>
              Vos coordonnées <span className="ne-serif-italic" style={{ color: 'var(--ne-laiton)' }}>célestes</span>.
            </h2>
            <hr className="ne-rule-short" style={{ marginTop: 32, marginBottom: 40 }} />
            <p className="ne-lead" style={{ color: 'rgba(245,240,230,0.82)', marginBottom: 48 }}>
              Cinq champs suffisent. Nous composons vos deux livres et les livrons dans les cinq minutes.
            </p>

            <form onSubmit={submit} data-testid="voyage-form-el">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 32 }}>
                <div className="ne-field">
                  <label className="ne-label" htmlFor="v-fn">Prénom</label>
                  <input id="v-fn" className="ne-input" type="text" value={form.first_name}
                    onChange={upd('first_name')} required data-testid="voyage-firstname" />
                </div>
                <div className="ne-field">
                  <label className="ne-label" htmlFor="v-email">Email</label>
                  <input id="v-email" className="ne-input" type="email" value={form.email}
                    onChange={upd('email')} required data-testid="voyage-email" />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 32 }}>
                <div className="ne-field">
                  <label className="ne-label" htmlFor="v-date">Date de naissance</label>
                  <input id="v-date" className="ne-input" type="date" value={form.birth_date}
                    onChange={upd('birth_date')} required data-testid="voyage-birthdate" />
                </div>
                <div className="ne-field">
                  <label className="ne-label" htmlFor="v-time">Heure</label>
                  <input id="v-time" className="ne-input" type="time" value={form.birth_time}
                    onChange={upd('birth_time')} required data-testid="voyage-birthtime" />
                </div>
                <div className="ne-field">
                  <label className="ne-label" htmlFor="v-city">Ville</label>
                  <input id="v-city" className="ne-input" type="text" value={form.birth_city}
                    onChange={upd('birth_city')} placeholder="Paris" data-testid="voyage-birthcity" />
                </div>
              </div>

              {err && (
                <p data-testid="voyage-error" style={{ marginTop: 24, color: 'var(--ne-erreur)', fontFamily: 'var(--ne-sans)', fontSize: 14, fontStyle: 'italic' }}>
                  {err}
                </p>
              )}

              <div style={{ marginTop: 48, display: 'flex', flexWrap: 'wrap', gap: 20, alignItems: 'center' }}>
                <button type="submit" disabled={loading} className="ne-btn ne-btn-primary"
                  data-testid="voyage-submit" style={loading ? { opacity: 0.7, cursor: 'wait' } : undefined}>
                  {loading ? 'Un instant…' : 'Recevoir mon voyage — 49 €'}
                  <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={1.5} />
                </button>
                <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', color: 'rgba(245,240,230,0.55)', fontFamily: 'var(--ne-sans)', fontSize: 12 }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                    <ShieldCheck style={{ width: 14, height: 14 }} strokeWidth={1.5} /> Paiement Stripe
                  </span>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                    <Clock style={{ width: 14, height: 14 }} strokeWidth={1.5} /> Livraison 5 min
                  </span>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                    <Mail style={{ width: 14, height: 14 }} strokeWidth={1.5} /> Par email
                  </span>
                </div>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* ═══ QUE DIT SOLÉNA (épilogue) ═══ */}
      <section className="ne-section ne-section-paper" data-testid="voyage-epilogue">
        <div className="ne-container">
          <div style={{ maxWidth: 640 }}>
            <div className="ne-overline">Épilogue</div>
            <blockquote style={{ margin: '32px 0 0', padding: 0, border: 0 }}>
              <p className="ne-h2" style={{ fontStyle: 'italic', fontWeight: 300, color: 'var(--ne-fusain)', maxWidth: 620 }}>
                &laquo;&nbsp;Prenez le temps. Une lecture, un thé, une soirée.
                Ce voyage ne se parcourt pas &mdash; se contemple.&nbsp;&raquo;
              </p>
              <footer className="ne-signature" style={{ marginTop: 24, fontSize: 18 }}>
                &mdash;&nbsp;Soléna
              </footer>
            </blockquote>
            <div style={{ marginTop: 48 }}>
              <Link to="/livres" className="ne-btn-ghost" data-testid="voyage-back">
                Voir toute la bibliothèque
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
