import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, LogIn, LogOut, User, ChevronDown } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

/**
 * Navbar V3 — refonte identité visuelle Feb 2026
 * - Fine, sticky, fond bleu nuit #0F1A3C
 * - Playfair pour le logo, Inter pour les liens
 * - 5 liens + 1 CTA doré unique à droite
 * - Mobile : logo + hamburger → panneau plein écran
 * - Transitions douces 200ms, contraste WCAG AA
 */

const NAV_LINKS = [
  { label: 'Accueil', to: '/' },
  { label: 'Services', to: '/nos-livres' },
  { label: 'Blog', to: '/blog' },
  { label: 'Témoignages', to: '/temoignages' },
  { label: 'Contact', to: '#contact' },
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
};

const linkActive = {
  color: '#C9A24B',
  borderBottomColor: '#C9A24B',
};

export default function NavbarV2() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, logout, user } = useAuth();

  useEffect(() => setOpen(false), [location.pathname]);

  const isActive = (to) => location.pathname === to;
  const handleLogout = () => { logout(); navigate('/'); };

  const navStyle = {
    position: 'sticky',
    top: 0,
    zIndex: 100,
    background: '#0F1A3C',
    borderBottom: '1px solid rgba(201,162,75,0.18)',
    width: '100%',
  };

  return (
    <nav style={navStyle} data-testid="navbar-v2">
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64 }}>

          {/* Logo */}
          <Link to="/" data-testid="navbar-logo-v2"
            style={{
              fontFamily: 'Playfair Display, serif',
              fontWeight: 500,
              fontSize: 22,
              letterSpacing: '0.02em',
              color: '#F7F5F0',
              textDecoration: 'none',
              display: 'flex', alignItems: 'baseline', gap: 6,
            }}>
            Plume <span style={{ color: '#C9A24B' }}>Astrale</span>
          </Link>

          {/* Desktop links */}
          <div className="ps-desktop-nav" style={{ display: 'none', alignItems: 'center', gap: 32 }}>
            {NAV_LINKS.map((l) => (
              <Link key={l.to} to={l.to}
                data-testid={`nav-v2-${l.label.toLowerCase()}`}
                style={isActive(l.to) ? { ...linkBase, ...linkActive } : linkBase}
                onMouseEnter={(e) => { if (!isActive(l.to)) e.currentTarget.style.color = '#C9A24B'; }}
                onMouseLeave={(e) => { if (!isActive(l.to)) e.currentTarget.style.color = 'rgba(247,245,240,0.78)'; }}>
                {l.label}
              </Link>
            ))}
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
          <button
            className="ps-mobile-toggle"
            onClick={() => setOpen(!open)}
            data-testid="nav-v2-mobile-toggle"
            aria-label="Menu"
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: '#F7F5F0', padding: 4,
            }}>
            {open ? <X strokeWidth={1.5} /> : <Menu strokeWidth={1.5} />}
          </button>
        </div>
      </div>

      {/* Mobile panel */}
      {open && (
        <div style={{
          position: 'fixed', top: 64, left: 0, right: 0, bottom: 0,
          background: '#0F1A3C', zIndex: 99, overflowY: 'auto',
          padding: '24px', display: 'flex', flexDirection: 'column', gap: 8,
        }} data-testid="nav-v2-mobile-panel">
          {NAV_LINKS.map((l) => (
            <Link key={l.to} to={l.to}
              data-testid={`nav-v2-mobile-${l.label.toLowerCase()}`}
              style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 24, fontWeight: 500,
                color: isActive(l.to) ? '#C9A24B' : '#F7F5F0',
                textDecoration: 'none',
                padding: '16px 0',
                borderBottom: '1px solid rgba(247,245,240,0.08)',
              }}>
              {l.label}
            </Link>
          ))}
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

function AccountMenu({ user, onLogout }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ position: 'relative' }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}>
      <button data-testid="nav-v2-account-btn"
        style={{
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
        <div style={{
          position: 'absolute', top: '100%', right: 0, marginTop: 8,
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
      )}
    </div>
  );
}

const menuItem = {
  display: 'block',
  padding: '10px 14px',
  color: 'rgba(247,245,240,0.85)',
  fontFamily: 'Inter, sans-serif',
  fontSize: 14,
  textDecoration: 'none',
  borderRadius: 8,
};
