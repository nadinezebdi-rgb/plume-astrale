import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, Coins, LogOut, User, LogIn, ChevronDown, Sparkles } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const NAV_ITEMS = [
  { label: 'Accueil', to: '/' },
  {
    label: 'Tirages',
    children: [
      { to: '/tarot-oui-non', label: 'Tarot Oui / Non' },
      { to: '/tarologie', label: 'Tarologie' },
      { to: '/compatibilite-amoureuse', label: 'Compatibilite Amoureuse' },
    ],
  },
  {
    label: 'Theme Astral',
    children: [
      { to: '/formulaire', label: 'Mon Theme Astral' },
      { to: '/numerologie', label: 'Numerologie' },
      { to: '/karma-destin', label: 'Karma & Destin' },
    ],
  },
  { label: 'Horoscope', to: '/horoscope' },
  { label: 'Mon Énergie', to: '/energie' },
  { label: 'Mon Rituel', to: '/mon-rituel' },
  { label: 'Consultation', to: '/consultation' },
];

const dropdownStyle = {
  background: 'rgba(11,11,15,0.97)',
  border: '1px solid rgba(212,180,106,0.18)',
  backdropFilter: 'blur(16px)',
  boxShadow: '0 8px 32px rgba(0,0,0,0.6)',
};

const childLinkStyle = {
  color: 'rgba(212,180,106,0.75)',
  display: 'block',
  padding: '10px 16px',
  fontSize: '12px',
  letterSpacing: '0.06em',
  textTransform: 'uppercase',
  transition: 'color 0.2s',
  textDecoration: 'none',
};

const DropdownMenu = ({ item, isActive }) => {
  const [open, setOpen] = useState(false);
  const timerRef = useRef(null);

  const show = () => { clearTimeout(timerRef.current); setOpen(true); };
  const hide = () => { timerRef.current = setTimeout(() => setOpen(false), 120); };
  useEffect(() => function() { clearTimeout(timerRef.current); }, []);

  const btnStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    fontSize: '12px',
    letterSpacing: '0.07em',
    textTransform: 'uppercase',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    color: isActive ? '#D4B46A' : 'rgba(212,180,106,0.6)',
    fontWeight: isActive ? 500 : 400,
    whiteSpace: 'nowrap',
    padding: 0,
  };

  return (
    <div style={{ position: 'relative' }} onMouseEnter={show} onMouseLeave={hide}>
      <button style={btnStyle}>
        {item.label}
        <ChevronDown
          style={{ width: 12, height: 12, transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
          strokeWidth={1.5}
        />
      </button>
      {open && (
        <div style={Object.assign({}, dropdownStyle, {
          position: 'absolute', top: '100%', left: '50%',
          transform: 'translateX(-50%)', marginTop: 8,
          minWidth: 210, borderRadius: 12, overflow: 'hidden', zIndex: 50,
        })}>
          {item.children.map(function(child) {
            return (
              <Link
                key={child.to}
                to={child.to}
                style={childLinkStyle}
                onMouseEnter={function(e) { e.currentTarget.style.color = '#F4D98C'; e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; }}
                onMouseLeave={function(e) { e.currentTarget.style.color = 'rgba(212,180,106,0.75)'; e.currentTarget.style.background = 'transparent'; }}
              >
                {child.label}
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};

const MonCompteDropdown = ({ creditBalance, handleLogout, isAdmin }) => {
  const [open, setOpen] = useState(false);
  const timerRef = useRef(null);

  const show = () => { clearTimeout(timerRef.current); setOpen(true); };
  const hide = () => { timerRef.current = setTimeout(() => setOpen(false), 120); };
  useEffect(() => function() { clearTimeout(timerRef.current); }, []);

  const btnStyle = {
    display: 'flex', alignItems: 'center', gap: 6,
    fontSize: 12, letterSpacing: '0.08em', textTransform: 'uppercase',
    padding: '6px 12px', borderRadius: 999,
    border: '1px solid rgba(212,180,106,0.4)',
    color: '#D4B46A', background: 'transparent',
    cursor: 'pointer', fontWeight: 500, whiteSpace: 'nowrap',
  };

  const itemStyle = {
    display: 'flex', alignItems: 'center', gap: 8,
    padding: '10px 16px', fontSize: 12,
    color: 'rgba(212,180,106,0.75)',
    background: 'transparent', border: 'none',
    width: '100%', textAlign: 'left',
    cursor: 'pointer', transition: 'all 0.2s', textDecoration: 'none',
  };

  return (
    <div style={{ position: 'relative' }} onMouseEnter={show} onMouseLeave={hide}>
      <button style={btnStyle} data-testid="navbar-mon-compte">
        <User style={{ width: 14, height: 14 }} strokeWidth={1.5} />
        Mon Compte
        <ChevronDown
          style={{ width: 12, height: 12, transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
          strokeWidth={1.5}
        />
      </button>

      {open && (
        <div style={Object.assign({}, dropdownStyle, {
          position: 'absolute', top: '100%', right: 0,
          marginTop: 8, minWidth: 220, borderRadius: 12, overflow: 'hidden', zIndex: 50,
        })}>
          <Link
            to="/acheter-credits"
            style={Object.assign({}, itemStyle, { justifyContent: 'space-between' })}
            onMouseEnter={function(e) { e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; }}
            onMouseLeave={function(e) { e.currentTarget.style.background = 'transparent'; }}
            data-testid="dropdown-credits"
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Coins style={{ width: 14, height: 14 }} strokeWidth={1.5} />
              Mes credits
            </span>
            <span style={{ color: '#D4B46A', fontWeight: 600 }}>{creditBalance}</span>
          </Link>

          <Link to="/quotidien" style={itemStyle}
            onMouseEnter={function(e) { e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; e.currentTarget.style.color = '#F4D98C'; }}
            onMouseLeave={function(e) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(212,180,106,0.75)'; }}
            data-testid="dropdown-journal">
            Mon Journal
          </Link>

          <Link to="/mon-compte" style={itemStyle}
            onMouseEnter={function(e) { e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; e.currentTarget.style.color = '#F4D98C'; }}
            onMouseLeave={function(e) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(212,180,106,0.75)'; }}
            data-testid="dropdown-recompenses">
            Mes Recompenses
          </Link>

          <Link to="/mon-compte" style={itemStyle}
            onMouseEnter={function(e) { e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; e.currentTarget.style.color = '#F4D98C'; }}
            onMouseLeave={function(e) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(212,180,106,0.75)'; }}
            data-testid="dropdown-profil">
            <User style={{ width: 12, height: 12 }} strokeWidth={1.5} />
            Mon Profil
          </Link>

          <div style={{ margin: '4px 16px', borderTop: '1px solid rgba(212,180,106,0.1)' }} />

          <Link to="/premium" style={Object.assign({}, itemStyle, { color: '#F4D98C' })}
            onMouseEnter={function(e) { e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; }}
            onMouseLeave={function(e) { e.currentTarget.style.background = 'transparent'; }}
            data-testid="dropdown-premium">
            <Sparkles style={{ width: 12, height: 12 }} strokeWidth={1.5} />
            Premium 14,99€/mois
          </Link>

          {isAdmin && (
            <Link to="/admin" style={Object.assign({}, itemStyle, { color: '#C5A059', fontWeight: 600 })}
              onMouseEnter={function(e) { e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; }}
              onMouseLeave={function(e) { e.currentTarget.style.background = 'transparent'; }}
              data-testid="dropdown-admin">
              <Sparkles style={{ width: 12, height: 12 }} strokeWidth={1.5} />
              Tableau de bord
            </Link>
          )}

          <button onClick={handleLogout} style={Object.assign({}, itemStyle, { color: 'rgba(255,100,100,0.7)' })}
            onMouseEnter={function(e) { e.currentTarget.style.background = 'rgba(255,80,80,0.06)'; e.currentTarget.style.color = '#ff8080'; }}
            onMouseLeave={function(e) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(255,100,100,0.7)'; }}
            data-testid="dropdown-logout">
            <LogOut style={{ width: 14, height: 14 }} strokeWidth={1.5} />
            Deconnexion
          </button>
        </div>
      )}
    </div>
  );
};

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [mobileExpanded, setMobileExpanded] = useState(null);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, creditBalance, logout, user } = useAuth();

  useEffect(() => {
    var onScroll = function() { setScrolled(window.scrollY > 40); };
    window.addEventListener('scroll', onScroll);
    return function() { window.removeEventListener('scroll', onScroll); };
  }, []);

  useEffect(() => { setIsOpen(false); setMobileExpanded(null); }, [location]);

  var handleLogout = function() { logout(); navigate('/'); };

  var isParentActive = function(item) {
    if (!item.children) return location.pathname === item.to;
    return item.children.some(function(c) { return location.pathname === c.to; });
  };

  var navStyle = {
    position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
    transition: 'all 0.5s',
    background: scrolled || isOpen ? 'rgba(11,11,15,0.97)' : 'rgba(11,11,15,0.70)',
    backdropFilter: 'blur(12px)',
    borderBottom: scrolled ? '1px solid rgba(197,160,89,0.10)' : '1px solid transparent',
  };

  return (
    <nav style={navStyle} data-testid="navbar">
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64 }}>

          <Link to="/"
            style={{ fontFamily: 'Cinzel, serif', color: '#D4B46A', fontWeight: 500, fontSize: 16, letterSpacing: '0.14em', textShadow: '0 0 14px rgba(212,180,106,0.3)', textDecoration: 'none', flexShrink: 0 }}
            data-testid="navbar-logo">
            Plume Astrale
          </Link>

          <div style={{ display: 'none' }} className="desktop-nav">
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginLeft: 24 }}>
              {NAV_ITEMS.map(function(item) {
                return item.children ? (
                  <DropdownMenu key={item.label} item={item} isActive={isParentActive(item)} />
                ) : (
                  <Link key={item.to} to={item.to}
                    style={{ fontSize: 12, letterSpacing: '0.07em', textTransform: 'uppercase', textDecoration: 'none', whiteSpace: 'nowrap', fontWeight: location.pathname === item.to ? 500 : 400, color: location.pathname === item.to ? '#D4B46A' : 'rgba(212,180,106,0.6)' }}
                    onMouseEnter={function(e) { if (location.pathname !== item.to) e.currentTarget.style.color = '#F4D98C'; }}
                    onMouseLeave={function(e) { if (location.pathname !== item.to) e.currentTarget.style.color = 'rgba(212,180,106,0.6)'; }}>
                    {item.label}
                  </Link>
                );
              })}
              <div style={{ width: 1, height: 16, background: '#D4B46A', opacity: 0.2 }} />
              {isAuthenticated ? (
                <MonCompteDropdown creditBalance={creditBalance} handleLogout={handleLogout} isAdmin={user?.is_admin} />
              ) : (
                <div style={{ display: 'flex', gap: 6 }}>
                  <Link to="/connexion"
                    style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, letterSpacing: '0.07em', textTransform: 'uppercase', padding: '6px 10px', borderRadius: 999, border: '1px solid rgba(212,180,106,0.45)', color: '#D4B46A', textDecoration: 'none', fontWeight: 500, whiteSpace: 'nowrap' }}
                    data-testid="navbar-login-btn">
                    <LogIn style={{ width: 13, height: 13 }} strokeWidth={1.5} />
                    Connexion
                  </Link>
                  <Link to="/inscription"
                    style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, letterSpacing: '0.07em', textTransform: 'uppercase', padding: '6px 12px', borderRadius: 999, border: '1px solid rgba(212,180,106,0.6)', color: '#D4B46A', background: 'rgba(212,180,106,0.12)', textDecoration: 'none', fontWeight: 500, whiteSpace: 'nowrap' }}
                    data-testid="navbar-register-btn">
                    Creer un compte
                  </Link>
                </div>
              )}
            </div>
          </div>

          <button onClick={function() { setIsOpen(!isOpen); }}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#A9A5A0', padding: 4 }}
            className="mobile-toggle" data-testid="mobile-menu-toggle">
            {isOpen ? <X style={{ width: 20, height: 20 }} strokeWidth={1.5} /> : <Menu style={{ width: 20, height: 20 }} strokeWidth={1.5} />}
          </button>
        </div>

        {isOpen && (
          <div style={{ padding: '20px 0', borderTop: '1px solid rgba(196,168,130,0.1)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {NAV_ITEMS.map(function(item) {
                return (
                  <div key={item.label || item.to}>
                    {item.children ? (
                      <div>
                        <button
                          onClick={function() { setMobileExpanded(mobileExpanded === item.label ? null : item.label); }}
                          style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 13, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '12px 0', background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(212,180,106,0.6)' }}>
                          {item.label}
                          <ChevronDown style={{ width: 16, height: 16, transform: mobileExpanded === item.label ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }} strokeWidth={1.5} />
                        </button>
                        {mobileExpanded === item.label && (
                          <div style={{ paddingLeft: 16, paddingBottom: 4 }}>
                            {item.children.map(function(child) {
                              return (
                                <Link key={child.to} to={child.to}
                                  style={{ display: 'block', fontSize: 12, letterSpacing: '0.06em', padding: '8px 0', color: 'rgba(212,180,106,0.5)', textDecoration: 'none' }}>
                                  {child.label}
                                </Link>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    ) : (
                      <Link to={item.to}
                        style={{ display: 'block', fontSize: 13, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '12px 0', color: location.pathname === item.to ? '#D4B46A' : 'rgba(212,180,106,0.5)', textDecoration: 'none', fontWeight: location.pathname === item.to ? 500 : 400 }}>
                        {item.label}
                      </Link>
                    )}
                  </div>
                );
              })}
              <div style={{ margin: '8px 0', borderTop: '1px solid rgba(212,180,106,0.1)' }} />
              {isAuthenticated ? (
                <div>
                  <Link to="/acheter-credits" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', fontSize: 13, color: '#D4B46A', textDecoration: 'none' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Coins style={{ width: 16, height: 16 }} strokeWidth={1.5} />Mes credits</span>
                    <span style={{ fontWeight: 600 }}>{creditBalance}</span>
                  </Link>
                  <Link to="/quotidien" style={{ display: 'block', padding: '12px 0', fontSize: 13, color: 'rgba(212,180,106,0.7)', textDecoration: 'none' }}>Mon Journal</Link>
                  <Link to="/mon-compte" style={{ display: 'block', padding: '12px 0', fontSize: 13, color: 'rgba(212,180,106,0.7)', textDecoration: 'none' }}>Mes Recompenses</Link>
                  <button onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '12px 0', fontSize: 13, color: 'rgba(255,100,100,0.8)', background: 'none', border: 'none', cursor: 'pointer' }}>
                    <LogOut style={{ width: 16, height: 16 }} strokeWidth={1.5} />Deconnexion
                  </button>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
                  <Link to="/connexion" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, fontSize: 13, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '10px 24px', borderRadius: 999, border: '1px solid rgba(212,180,106,0.45)', color: '#D4B46A', textDecoration: 'none' }} data-testid="mobile-login-btn">
                    <LogIn style={{ width: 16, height: 16 }} strokeWidth={1.5} />Connexion
                  </Link>
                  <Link to="/inscription" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, fontSize: 13, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '10px 24px', borderRadius: 999, border: '1px solid rgba(212,180,106,0.6)', color: '#D4B46A', background: 'rgba(212,180,106,0.12)', textDecoration: 'none' }} data-testid="mobile-register-btn">
                    Creer un compte
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      <style>{`.desktop-nav{display:none!important}@media(min-width:1240px){.desktop-nav{display:block!important}.mobile-toggle{display:none!important}}`}</style>
    </nav>
  );
};

export default Navbar;
