import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Star, ArrowRight, Search } from 'lucide-react';
import SEO from '@/components/SEO';
import PsPageShell from '@/components/PsPageShell';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * /temoignages — Mur des témoignages public · Charte v3 (light).
 * Filtre par signe + recherche texte + affichage grid.
 */

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
        || (t.sign || '').toLowerCase().includes(q));
    }
    return out;
  }, [items, query, signFilter]);

  const signsWithData = useMemo(() => {
    const set = new Set(items.map((t) => (t.sign || '').trim()).filter(Boolean));
    return SIGNS.filter((s) => set.has(s));
  }, [items]);

  return (
    <PsPageShell background="light">
      <SEO
        path="/temoignages"
        title="Témoignages · Plume Astrale"
        description="Découvrez ce que les lectrices Plume Astrale partagent après leur lecture — filtrable par signe astrologique."
      />

      <section className="ps-section ps-section-light" data-testid="temoignages-public-page">
        <div className="ps-container">
          {/* Header */}
          <div style={{ maxWidth: 720, marginBottom: 48 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Communauté Plume Astrale</p>
            <h1 className="ps-h1" style={{ color: '#0F1A3C', marginBottom: 20 }}>
              Ce que les femmes ont <span className="ps-italic">trouvé</span> ici.
            </h1>
            <p className="ps-body" style={{ color: '#232323' }}>
              Chaque témoignage est validé par Soléna avant publication. Prénom et signe seulement — pas d&apos;email visible.
            </p>
          </div>

          {/* Filtres */}
          <div style={{
            background: '#fff',
            border: '1px solid #E3E1DC',
            borderRadius: 12,
            padding: 20,
            marginBottom: 32,
            display: 'flex', flexWrap: 'wrap', gap: 10,
            alignItems: 'center',
          }}>
            <div style={{ position: 'relative', flex: '1 1 240px', minWidth: 240 }}>
              <Search style={{
                position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)',
                width: 16, height: 16, color: '#6B7280', pointerEvents: 'none',
              }} strokeWidth={1.8} />
              <input
                type="text"
                placeholder="Rechercher un prénom, une ville, un mot…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                data-testid="temoignages-search"
                className="ps-input"
                style={{ paddingLeft: 40, width: '100%' }}
              />
            </div>
            <FilterChip active={!signFilter} onClick={() => setSignFilter(null)} testid="temoignages-chip-all">
              Tous les signes
            </FilterChip>
            {signsWithData.map((s) => (
              <FilterChip key={s}
                active={signFilter === s}
                onClick={() => setSignFilter(signFilter === s ? null : s)}
                testid={`temoignages-chip-${s.toLowerCase()}`}>
                {s}
              </FilterChip>
            ))}
          </div>

          <div className="ps-caption" style={{ marginBottom: 24 }} data-testid="temoignages-count">
            {loading ? 'Chargement…' :
              `${filtered.length} témoignage${filtered.length > 1 ? 's' : ''}`
              + (signFilter ? ` · signe ${signFilter}` : '')
              + (query.trim() ? ` · recherche « ${query.trim()} »` : '')}
          </div>

          {!loading && filtered.length === 0 && (
            <div style={{
              padding: '60px 24px', textAlign: 'center',
              background: '#fff', border: '1px dashed #E3E1DC',
              borderRadius: 12,
              fontFamily: 'Inter, sans-serif', color: '#6B7280',
            }} data-testid="temoignages-empty">
              {items.length === 0 ? (
                <>
                  <div style={{ fontFamily: 'Playfair Display, serif', fontStyle: 'italic', fontSize: 20, color: '#0F1A3C', marginBottom: 12 }}>
                    Les premiers témoignages arrivent bientôt.
                  </div>
                  <div style={{ maxWidth: 480, margin: '0 auto', lineHeight: 1.6 }}>
                    Vous avez reçu une lecture Plume Astrale ? <Link to="/temoignage" style={{ color: '#C9A24B', textDecoration: 'underline', textUnderlineOffset: 3 }}>Partagez votre expérience</Link> — nous validons chaque témoignage avant publication.
                  </div>
                </>
              ) : (
                'Aucun témoignage ne correspond à ta recherche.'
              )}
            </div>
          )}

          {/* Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: 20,
          }}>
            {filtered.map((t) => (
              <TestimonialCard key={t.id} t={t} />
            ))}
          </div>

          {/* CTA */}
          <div style={{
            marginTop: 56, paddingTop: 40,
            borderTop: '1px solid #E3E1DC',
            display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'center',
          }}>
            <Link to="/inscription" className="ps-btn ps-btn-primary"
              data-testid="temoignages-cta-home">
              Découvrir ma lecture
              <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
            </Link>
            <Link to="/temoignage" className="ps-btn ps-btn-outline"
              data-testid="temoignages-cta-share">
              Partager mon témoignage
            </Link>
          </div>
        </div>
      </section>
    </PsPageShell>
  );
}

function FilterChip({ active, onClick, testid, children }) {
  return (
    <button type="button" onClick={onClick} data-testid={testid}
      style={{
        background: active ? '#0F1A3C' : 'transparent',
        color: active ? '#F7F5F0' : '#232323',
        border: active ? '1px solid #0F1A3C' : '1px solid #E3E1DC',
        padding: '8px 14px', borderRadius: 999,
        fontFamily: 'Inter, sans-serif', fontSize: 13,
        fontWeight: active ? 500 : 400,
        cursor: 'pointer',
        letterSpacing: '0.02em',
        transition: 'background 200ms ease, border-color 200ms ease',
      }}
      onMouseEnter={(e) => { if (!active) e.currentTarget.style.borderColor = '#C9A24B'; }}
      onMouseLeave={(e) => { if (!active) e.currentTarget.style.borderColor = '#E3E1DC'; }}>
      {children}
    </button>
  );
}

function TestimonialCard({ t }) {
  return (
    <div className="ps-card" data-testid={`temoignages-card-${t.id}`}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <div style={{
          width: 44, height: 44, borderRadius: 999,
          background: 'linear-gradient(135deg, #C9A24B 0%, #A88536 100%)',
          color: '#0F1A3C',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'Playfair Display, serif',
          fontSize: 18, fontWeight: 600,
          flexShrink: 0,
        }}>
          {t.initial || (t.name || '?')[0]}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontFamily: 'Inter, sans-serif', fontSize: 15, fontWeight: 600,
            color: '#0F1A3C', lineHeight: 1.2,
          }}>{t.name}</div>
          <div style={{
            fontFamily: 'Inter, sans-serif', fontSize: 12,
            color: '#6B7280', marginTop: 2,
          }}>
            {t.sign && <span>{t.sign}</span>}
            {t.sign && t.city && <span> · </span>}
            {t.city && <span>{t.city}</span>}
          </div>
          <div style={{ display: 'flex', gap: 2, marginTop: 4 }}>
            {[...Array(t.stars || 5)].map((_, i) => (
              <Star key={i} style={{ width: 12, height: 12, color: '#C9A24B', fill: '#C9A24B' }} strokeWidth={0} />
            ))}
          </div>
        </div>
      </div>
      <p style={{
        fontFamily: 'Playfair Display, serif',
        fontSize: 16, lineHeight: 1.55, fontStyle: 'italic',
        color: '#232323', margin: 0,
        paddingLeft: 14, borderLeft: '2px solid #C9A24B',
      }}>
        « {t.quote} »
      </p>
      {(t.transform_before || t.transform_after) && (
        <div style={{
          marginTop: 14, paddingTop: 14,
          borderTop: '1px dashed #E3E1DC',
          fontFamily: 'Inter, sans-serif', fontSize: 13,
          color: '#6B7280', lineHeight: 1.55,
        }}>
          {t.transform_before && <div><strong style={{ color: '#C9A24B' }}>Avant :</strong> {t.transform_before}</div>}
          {t.transform_after && <div><strong style={{ color: '#C9A24B' }}>Après :</strong> {t.transform_after}</div>}
        </div>
      )}
    </div>
  );
}
