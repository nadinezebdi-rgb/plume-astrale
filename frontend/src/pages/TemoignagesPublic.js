import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

/* ═══════════════════════════════════════════════════════════
   Page /temoignages — Public wall
   Liste tous les temoignages approuves avec filtre par signe astro
   ═══════════════════════════════════════════════════════════ */

const styles = `
  .pw-page{min-height:100vh;background:#0b0f24;color:#e8e6f0;
    font-family:Georgia,'Times New Roman',serif;padding:60px 20px 100px;}
  .pw-wrap{max-width:1100px;margin:0 auto;}
  .pw-eyebrow{font-size:11px;letter-spacing:.24em;text-transform:uppercase;
    color:#c9a24b;margin:0 0 12px;}
  .pw-title{font-size:clamp(2rem,3.5vw,2.8rem);color:#e8e6f0;margin:0 0 12px;
    font-weight:400;line-height:1.15;}
  .pw-title em{color:#c9a24b;font-style:italic;}
  .pw-lead{color:#b8b4c9;font-size:1rem;margin:0 0 32px;max-width:640px;}

  .pw-filters{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 28px;
    padding:14px;background:rgba(20,26,51,.5);border-radius:12px;
    border:1px solid rgba(201,162,75,.15);}
  .pw-search{flex:1;min-width:200px;background:rgba(11,15,36,.7);color:#e8e6f0;
    border:1px solid rgba(201,162,75,.2);padding:10px 14px;border-radius:10px;
    font-family:Georgia,serif;font-size:.9rem;}
  .pw-search:focus{outline:none;border-color:#c9a24b;box-shadow:0 0 0 2px rgba(201,162,75,.15);}
  .pw-chip{background:transparent;color:#b8b4c9;border:1px solid rgba(255,255,255,.1);
    padding:6px 12px;border-radius:999px;cursor:pointer;font-family:Georgia,serif;
    font-size:.82rem;transition:all .18s;letter-spacing:.02em;}
  .pw-chip:hover{border-color:rgba(201,162,75,.4);color:#e8e6f0;}
  .pw-chip-active{background:linear-gradient(135deg,#c9a24b,#e2c07c);color:#1a1030;
    border-color:transparent;font-weight:600;}

  .pw-count{color:#7d7a90;font-size:.85rem;margin-bottom:20px;letter-spacing:.03em;}

  .pw-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;}
  .pw-card{background:rgba(20,26,51,.5);border:1px solid rgba(201,162,75,.15);
    border-radius:16px;padding:22px;transition:transform .2s ease,border-color .2s ease;}
  .pw-card:hover{transform:translateY(-3px);border-color:rgba(201,162,75,.35);}
  .pw-card-head{display:flex;align-items:center;gap:12px;margin-bottom:14px;}
  .pw-avatar{width:46px;height:46px;border-radius:50%;
    background:linear-gradient(135deg,#c9a24b,#e2c07c);color:#1a1030;
    display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:600;}
  .pw-name{color:#e8e6f0;font-size:.95rem;font-weight:600;}
  .pw-sub{color:#8a86a0;font-size:.78rem;margin-top:2px;}
  .pw-stars{color:#c9a24b;font-size:.78rem;letter-spacing:.06em;margin-top:2px;}
  .pw-quote{color:#e8e6f0;font-size:.9rem;line-height:1.55;font-style:italic;
    padding-left:12px;border-left:2px solid #c9a24b;}
  .pw-transform{margin-top:14px;padding-top:12px;border-top:1px dashed rgba(201,162,75,.2);
    font-size:.78rem;color:#b8b4c9;line-height:1.5;}
  .pw-transform strong{color:#c9a24b;}

  .pw-empty{padding:60px 20px;text-align:center;color:#7d7a90;
    background:rgba(20,26,51,.3);border-radius:12px;border:1px dashed rgba(255,255,255,.1);}

  .pw-cta{display:inline-block;margin-top:32px;
    background:linear-gradient(135deg,#c9a24b,#e2c07c);color:#1a1030;
    padding:12px 26px;border-radius:999px;text-decoration:none;font-weight:600;
    box-shadow:0 4px 20px rgba(201,162,75,.35);}
  .pw-share{display:inline-block;margin-left:14px;color:#c9a24b;
    text-decoration:none;border-bottom:1px dashed rgba(201,162,75,.4);
    font-size:.9rem;padding-bottom:2px;}
`;

const SIGNS = [
  'Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge',
  'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons',
];

export default function TemoignagesPublic() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [signFilter, setSignFilter] = useState(null);

  useEffect(() => {
    let cancel = false;
    fetch(`${API}/api/landing/testimonials?limit=100`)
      .then((r) => r.json())
      .then((d) => { if (!cancel) setItems(d?.testimonials || []); })
      .catch(() => {})
      .finally(() => { if (!cancel) setLoading(false); });
    return () => { cancel = true; };
  }, []);

  const filtered = useMemo(() => {
    let out = items;
    if (signFilter) out = out.filter((t) => (t.sign || '').toLowerCase() === signFilter.toLowerCase());
    if (query.trim()) {
      const q = query.trim().toLowerCase();
      out = out.filter((t) =>
        (t.name || '').toLowerCase().includes(q)
        || (t.city || '').toLowerCase().includes(q)
        || (t.quote || '').toLowerCase().includes(q)
        || (t.sign || '').toLowerCase().includes(q)
      );
    }
    return out;
  }, [items, query, signFilter]);

  const signsWithData = useMemo(() => {
    const set = new Set(items.map((t) => (t.sign || '').trim()).filter(Boolean));
    return SIGNS.filter((s) => set.has(s));
  }, [items]);

  return (
    <>
      <SEO path="/temoignages"
        title="Témoignages · Plume Astrale"
        description="Plus de mille femmes ont partagé ce que Soléna leur a apporté. Lis leurs mots — filtre par signe astrologique." />
      <style>{styles}</style>
      <div className="pw-page" data-testid="temoignages-public-page">
        <div className="pw-wrap">
          <div className="pw-eyebrow">Communauté Plume Astrale</div>
          <h1 className="pw-title">Ce que les femmes ont <em>trouvé</em> ici.</h1>
          <p className="pw-lead">
            Chaque témoignage est validé par Soléna avant publication.
            Prénom et signe seulement — pas d'email visible.
          </p>

          <div className="pw-filters">
            <input
              type="text"
              className="pw-search"
              placeholder="Rechercher un prénom, une ville, un mot…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              data-testid="temoignages-search"
            />
            <button
              type="button"
              className={`pw-chip ${!signFilter ? 'pw-chip-active' : ''}`}
              onClick={() => setSignFilter(null)}
              data-testid="temoignages-chip-all"
            >
              Tous les signes
            </button>
            {signsWithData.map((s) => (
              <button
                key={s}
                type="button"
                className={`pw-chip ${signFilter === s ? 'pw-chip-active' : ''}`}
                onClick={() => setSignFilter(signFilter === s ? null : s)}
                data-testid={`temoignages-chip-${s.toLowerCase()}`}
              >
                {s}
              </button>
            ))}
          </div>

          <div className="pw-count" data-testid="temoignages-count">
            {loading ? 'Chargement…' :
              `${filtered.length} témoignage${filtered.length > 1 ? 's' : ''}`
              + (signFilter ? ` · signe ${signFilter}` : '')
              + (query.trim() ? ` · recherche « ${query.trim()} »` : '')}
          </div>

          {!loading && filtered.length === 0 && (
            <div className="pw-empty" data-testid="temoignages-empty">
              Aucun témoignage ne correspond à ta recherche.
            </div>
          )}

          <div className="pw-grid">
            {filtered.map((t) => (
              <div key={t.id} className="pw-card" data-testid={`temoignages-card-${t.id}`}>
                <div className="pw-card-head">
                  <div className="pw-avatar">{t.initial || (t.name || '?')[0]}</div>
                  <div style={{ flex: 1 }}>
                    <div className="pw-name">{t.name}</div>
                    <div className="pw-sub">
                      {t.sign && <span>{t.sign}</span>}
                      {t.sign && t.city && <span> · </span>}
                      {t.city && <span>{t.city}</span>}
                    </div>
                    <div className="pw-stars">{'★'.repeat(t.stars || 5)}</div>
                  </div>
                </div>
                <div className="pw-quote">« {t.quote} »</div>
                {(t.transform_before || t.transform_after) && (
                  <div className="pw-transform">
                    {t.transform_before && <><strong>Avant :</strong> {t.transform_before}<br /></>}
                    {t.transform_after && <><strong>Après :</strong> {t.transform_after}</>}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div style={{ marginTop: 40, textAlign: 'center' }}>
            <Link to="/" className="pw-cta" data-testid="temoignages-cta-home">
              Découvrir ma lecture · 97€
            </Link>
            <Link to="/temoignage" className="pw-share" data-testid="temoignages-cta-share">
              Partager mon témoignage →
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
