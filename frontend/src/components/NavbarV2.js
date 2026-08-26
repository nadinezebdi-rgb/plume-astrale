import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, LogIn, LogOut, User, ChevronDown, ArrowRight, ChevronRight } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { LECTURES, OUTILS } from '@/config/catalog';

/**
 * Navbar V3 — refonte Feb 2026 + mega menu Services.
 * - Fine sticky navy, Playfair logo, Inter liens, doré accent
 * - Dropdown "Services" avec 2 colonnes : Lectures PDF + Outils
 * - Mobile : hamburger → panneau plein écran avec sous-menu accordéon
 */

const NAV_LINKS = [
  { label: 'Accueil', to: '/' },
  { label: 'Services', to: '/livres', hasMega: true },
  { label: 'Nos livres', to: '/livres' },
  { label: 'Manifesto', to: '/manifesto' },
  { label: 'Blog', to: '/blog' },
  { label: 'Témoignages', to: '/temoignages' },
  { label: 'Contact', to: '/contact' },
];

const linkBase = {
  fontFamily: 'Inter, sans-serif',
  fontSize: 14,
  fontWeight: 500,
  color: 'rgba(247,245,240,0.78)',
  textDecoration: 'none',
  padding: '6px 4px',
  transition: 'color 200ms ease, border-color 200ms ease',
  borderBottom: '1.5px solid transparent',
  letterSpacing: '0.02em',
  cursor: 'pointer',
  background: 'transparent',
  border: 'none',
};
const linkActive = { color: '#C9A24B', borderBottomColor: '#C9A24B' };

export default function NavbarV2() {
  const [open, setOpen] = useState(false);
  const [megaOpen, setMegaOpen] = useState(false);
  const [mobileServicesOpen, setMobileServicesOpen] = useState(false);
  const megaTimer = useRef(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, logout, user } = useAuth();

  useEffect(() => {
    setOpen(false);
    setMegaOpen(false);
    setMobileServicesOpen(false);
  }, [location.pathname]);

  // Pages immersives sans navbar (prototype /experience, à étendre si besoin).
  // Placé ici APRÈS tous les hooks pour respecter les rules-of-hooks.
  if (location.pathname === '/experience' || location.pathname.startsWith('/experience/')) {
    return null;
  }

  const isActive = (to) => location.pathname === to;
  const isServicesActive = () =>
    location.pathname === '/livres'
    || LECTURES.some(l => location.pathname === l.to)
    || OUTILS.some(o => location.pathname === o.to);

  const handleLogout = () => { logout(); navigate('/'); };

  const openMega = () => {
    if (megaTimer.current) clearTimeout(megaTimer.current);
    setMegaOpen(true);
  };
  const closeMegaSoon = () => {
    if (megaTimer.current) clearTimeout(megaTimer.current);
    megaTimer.current = setTimeout(() => setMegaOpen(false), 160);
  };

  const navStyle = {
    position: 'sticky', top: 0, zIndex: 100,
    background: '#0F1A3C',
    borderBottom: '1px solid rgba(201,162,75,0.18)',
    width: '100%',
  };

  return (
    <nav style={navStyle} data-testid="navbar-v2">
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64 }}>

          <Link to="/" data-testid="navbar-logo-v2" style={{
            fontFamily: 'Playfair Display, serif',
            fontWeight: 500, fontSize: 22, letterSpacing: '0.02em',
            color: '#F7F5F0', textDecoration: 'none',
            display: 'flex', alignItems: 'baseline', gap: 6,
          }}>
            Plume <span style={{ color: '#C9A24B' }}>Astrale</span>
          </Link>

          {/* Desktop links */}
          <div className="ps-desktop-nav" style={{ display: 'none', alignItems: 'center', gap: 32 }}>
            {NAV_LINKS.map((l) => {
              const active = l.hasMega ? isServicesActive() : isActive(l.to);
              if (l.hasMega) {
                return (
                  <div key={l.label} style={{ position: 'relative' }}
                    onMouseEnter={openMega} onMouseLeave={closeMegaSoon}>
                    <button
                      type="button"
                      data-testid="nav-v2-services-btn"
                      onClick={() => navigate(l.to)}
                      style={{
                        ...(active ? { ...linkBase, ...linkActive } : linkBase),
                        display: 'inline-flex', alignItems: 'center', gap: 4,
                      }}>
                      {l.label}
                      <ChevronDown style={{
                        width: 14, height: 14,
                        transform: megaOpen ? 'rotate(180deg)' : 'none',
                        transition: 'transform 200ms ease',
                      }} strokeWidth={1.8} />
                    </button>
                  </div>
                );
              }
              return (
                <Link key={l.label} to={l.to}
                  data-testid={`nav-v2-${l.label.toLowerCase().replace(/\s+/g, '-')}`}
                  style={active ? { ...linkBase, ...linkActive } : linkBase}
                  onMouseEnter={(e) => { if (!active) e.currentTarget.style.color = '#C9A24B'; }}
                  onMouseLeave={(e) => { if (!active) e.currentTarget.style.color = 'rgba(247,245,240,0.78)'; }}>
                  {l.label}
                </Link>
              );
            })}
          </div>

          {/* CTA doré + auth (desktop) */}
          <div className="ps-desktop-nav" style={{ display: 'none', alignItems: 'center', gap: 16 }}>
            {isAuthenticated ? (
              <AccountMenu user={user} onLogout={handleLogout} />
            ) : (
              <Link to="/connexion" data-testid="nav-v2-login"
                style={{ ...linkBase, display: 'inline-flex', alignItems: 'center', gap: 6 }}
                onMouseEnter={(e) => { e.currentTarget.style.color = '#C9A24B'; }}
                onMouseLeave={(e) => { e.currentTarget.style.color = 'rgba(247,245,240,0.78)'; }}>
                <LogIn style={{ width: 15, height: 15 }} strokeWidth={1.8} />
                Connexion
              </Link>
            )}
            <Link to="/inscription" className="ps-btn ps-btn-primary" data-testid="nav-v2-cta"
              style={{ padding: '10px 20px', fontSize: 14, minHeight: 40 }}>
              Recevoir ma lecture
            </Link>
          </div>

          {/* Mobile toggle */}
          <button className="ps-mobile-toggle"
            onClick={() => setOpen(!open)}
            data-testid="nav-v2-mobile-toggle"
            aria-label="Menu"
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#F7F5F0', padding: 4 }}>
            {open ? <X strokeWidth={1.5} /> : <Menu strokeWidth={1.5} />}
          </button>
        </div>
      </div>

      {/* ══════ MEGA MENU (desktop) ══════ */}
      {megaOpen && (
        <div
          onMouseEnter={openMega}
          onMouseLeave={closeMegaSoon}
          data-testid="nav-v2-mega"
          style={{
            position: 'absolute', top: '100%', left: 0, right: 0,
            background: '#0F1A3C',
            borderTop: '1px solid rgba(201,162,75,0.18)',
            borderBottom: '1px solid rgba(201,162,75,0.18)',
            boxShadow: '0 24px 48px rgba(0,0,0,0.35)',
          }}>
          <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 48 }}>

              {/* Colonne Lectures Premium PDF */}
              <div>
                <MegaHeading>Lectures premium — PDF à télécharger</MegaHeading>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  {LECTURES.map((l) => (
                    <MegaLink key={l.key} to={l.to} testid={`mega-lecture-${l.key}`}
                      title={l.title} tagline={l.tagline} price={l.price} highlight={l.highlight} />
                  ))}
                </div>
                <Link to="/livres" data-testid="mega-all-lectures" style={megaFooterLink}>
                  Voir toute la bibliothèque
                  <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
                </Link>
              </div>

              {/* Colonne Services complémentaires */}
              <div>
                <MegaHeading>Services complémentaires</MegaHeading>
                {OUTILS.map((o) => (
                  <MegaLink key={o.key} to={o.to} testid={`mega-outil-${o.key}`}
                    title={o.title} tagline={o.tagline} compact />
                ))}
              </div>

            </div>
          </div>
        </div>
      )}

      {/* ══════ MOBILE PANEL ══════ */}
      {open && (
        <div style={{
          position: 'fixed', top: 64, left: 0, right: 0, bottom: 0,
          background: '#0F1A3C', zIndex: 99, overflowY: 'auto',
          padding: '24px', display: 'flex', flexDirection: 'column', gap: 8,
        }} data-testid="nav-v2-mobile-panel">
          {NAV_LINKS.map((l) => {
            if (l.hasMega) {
              return (
                <div key={l.label}>
                  <button
                    onClick={() => setMobileServicesOpen(!mobileServicesOpen)}
                    data-testid="nav-v2-mobile-services-toggle"
                    style={{ ...mobileLinkStyle, display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', background: 'transparent', border: 'none', cursor: 'pointer' }}>
                    {l.label}
                    <ChevronRight style={{
                      width: 18, height: 18,
                      transform: mobileServicesOpen ? 'rotate(90deg)' : 'none',
                      transition: 'transform 200ms ease',
                    }} strokeWidth={1.8} />
                  </button>
                  {mobileServicesOpen && (
                    <div style={{ padding: '4px 8px 20px', display: 'flex', flexDirection: 'column', gap: 4 }}>
                      <div style={mobileSubHeading}>Lectures premium PDF</div>
                      {LECTURES.map((it) => (
                        <Link key={it.key} to={it.to} data-testid={`mob-lecture-${it.key}`} style={mobileSubLink}>
                          <span>{it.title}</span>
                          <span style={{ color: '#C9A24B', fontSize: 13, fontWeight: 500 }}>{it.price}</span>
                        </Link>
                      ))}
                      <div style={{ ...mobileSubHeading, marginTop: 12 }}>Services complémentaires</div>
                      {OUTILS.map((it) => (
                        <Link key={it.key} to={it.to} data-testid={`mob-outil-${it.key}`} style={mobileSubLink}>
                          {it.title}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              );
            }
            return (
              <Link key={l.label} to={l.to}
                data-testid={`nav-v2-mobile-${l.label.toLowerCase().replace(/\s+/g, '-')}`}
                style={{
                  ...mobileLinkStyle,
                  color: isActive(l.to) ? '#C9A24B' : '#F7F5F0',
                }}>
                {l.label}
              </Link>
            );
          })}
          <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 12 }}>
            {isAuthenticated ? (
              <>
                <Link to="/mon-compte" className="ps-btn ps-btn-outline" style={{ justifyContent: 'center' }}>
                  <User style={{ width: 16, height: 16 }} strokeWidth={1.8} />
                  Mon compte
                </Link>
                <button onClick={handleLogout} className="ps-btn ps-btn-outline" style={{ justifyContent: 'center' }}>
                  <LogOut style={{ width: 16, height: 16 }} strokeWidth={1.8} />
                  Déconnexion
                </button>
              </>
            ) : (
              <>
                <Link to="/connexion" className="ps-btn ps-btn-outline" style={{ justifyContent: 'center' }}>
                  Connexion
                </Link>
                <Link to="/inscription" className="ps-btn ps-btn-primary" style={{ justifyContent: 'center' }}>
                  Recevoir ma lecture
                </Link>
              </>
            )}
          </div>
        </div>
      )}

      <style>{`
        .ps-desktop-nav { display: none !important; }
        .ps-mobile-toggle { display: inline-flex !important; }
        @media (min-width: 1024px) {
          .ps-desktop-nav { display: flex !important; }
          .ps-mobile-toggle { display: none !important; }
        }
      `}</style>
    </nav>
  );
}

/* ═══ SOUS-COMPOSANTS ═══ */

function MegaHeading({ children }) {
  return (
    <div style={{
      fontFamily: 'Inter, sans-serif',
      fontSize: 11, fontWeight: 600,
      letterSpacing: '0.18em', textTransform: 'uppercase',
      color: '#C9A24B', marginBottom: 16,
    }}>{children}</div>
  );
}

function MegaLink({ to, title, tagline, price, testid, highlight, compact }) {
  return (
    <Link to={to} data-testid={testid} style={{
      display: 'block',
      padding: compact ? '8px 10px' : '12px 14px',
      borderRadius: 10,
      textDecoration: 'none',
      transition: 'background 200ms ease, transform 200ms ease',
      border: highlight ? '1px solid rgba(201,162,75,0.35)' : '1px solid transparent',
      background: highlight ? 'rgba(201,162,75,0.06)' : 'transparent',
    }}
      onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(30,42,94,0.6)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.background = highlight ? 'rgba(201,162,75,0.06)' : 'transparent'; }}>
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        gap: 12, marginBottom: 2,
      }}>
        <span style={{
          fontFamily: 'Playfair Display, serif',
          fontSize: 16, color: '#F7F5F0', fontWeight: 500,
        }}>{title}</span>
        {price && (
          <span style={{
            fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 600,
            color: '#C9A24B', flexShrink: 0,
          }}>{price}</span>
        )}
      </div>
      {tagline && (
        <div style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 12, color: 'rgba(247,245,240,0.55)', lineHeight: 1.4,
        }}>{tagline}</div>
      )}
    </Link>
  );
}

const megaFooterLink = {
  marginTop: 20, display: 'inline-flex', alignItems: 'center', gap: 6,
  fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 500,
  color: '#C9A24B', textDecoration: 'none',
  paddingBottom: 2, borderBottom: '1px solid transparent',
};

const mobileLinkStyle = {
  fontFamily: 'Playfair Display, serif',
  fontSize: 24, fontWeight: 500,
  color: '#F7F5F0', textDecoration: 'none',
  padding: '16px 0',
  borderBottom: '1px solid rgba(247,245,240,0.08)',
};

const mobileSubHeading = {
  fontFamily: 'Inter, sans-serif',
  fontSize: 10, fontWeight: 600,
  letterSpacing: '0.18em', textTransform: 'uppercase',
  color: '#C9A24B', margin: '8px 0 4px',
};

const mobileSubLink = {
  fontFamily: 'Inter, sans-serif', fontSize: 15, fontWeight: 400,
  color: 'rgba(247,245,240,0.85)',
  padding: '10px 0',
  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
  textDecoration: 'none',
  borderBottom: '1px solid rgba(247,245,240,0.05)',
};

function AccountMenu({ user, onLogout }) {
  const [open, setOpen] = useState(false);
  const closeTimer = useRef(null);
  const openNow = () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    setOpen(true);
  };
  const closeSoon = () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    closeTimer.current = setTimeout(() => setOpen(false), 220);
  };
  return (
    <div style={{ position: 'relative' }}
      onMouseEnter={openNow} onMouseLeave={closeSoon}>
      <button data-testid="nav-v2-account-btn" style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        background: 'transparent', border: 'none', cursor: 'pointer',
        color: 'rgba(247,245,240,0.85)',
        fontFamily: 'Inter, sans-serif', fontSize: 14, fontWeight: 500,
        padding: '6px 4px',
      }}>
        <User style={{ width: 16, height: 16 }} strokeWidth={1.8} />
        {user?.prenom || 'Mon compte'}
        <ChevronDown style={{ width: 14, height: 14 }} strokeWidth={1.8} />
      </button>
      {open && (
        <div
          onMouseEnter={openNow}
          onMouseLeave={closeSoon}
          style={{
            position: 'absolute', top: '100%', right: 0,
            paddingTop: 8,  // gap visuel invisible mais survolable
          }}>
          <div style={{
            background: '#1E2A5E', border: '1px solid rgba(201,162,75,0.20)',
            borderRadius: 12, padding: 8, minWidth: 200,
            boxShadow: '0 12px 32px rgba(0,0,0,0.4)',
          }} data-testid="nav-v2-account-menu">
            <Link to="/mon-compte" style={menuItem}>Mon espace</Link>
            <Link to="/acheter-credits" style={menuItem}>Mes crédits</Link>
            {user?.is_admin && <Link to="/admin" style={{ ...menuItem, color: '#C9A24B' }}>Administration</Link>}
            <button onClick={onLogout} style={{ ...menuItem, background: 'none', border: 'none', textAlign: 'left', width: '100%', cursor: 'pointer' }}>
              Déconnexion
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const menuItem = {
  display: 'block', padding: '10px 14px',
  color: 'rgba(247,245,240,0.85)',
  fontFamily: 'Inter, sans-serif', fontSize: 14,
  textDecoration: 'none', borderRadius: 8,
};
