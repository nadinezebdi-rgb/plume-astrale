import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, Coins, LogOut, User, LogIn, ChevronDown } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const NAV_ITEMS = [
  { label: 'Accueil', to: '/' },
  {
    label: 'Tirages',
    children: [
      { to: '/tarot-oui-non', label: '🃏 Tarot Oui / Non' },
      { to: '/tarologie',     label: '✨ Tarologie' },
      { to: '/compatibilite-amoureuse', label: '💑 Compatibilité Amoureuse' },
    ],
  },
  {
    label: 'Thème Astral',
    children: [
      { to: '/formulaire',   label: '🌟 Mon Thème Astral' },
      { to: '/numerologie',  label: '🔢 Numérologie' },
      { to: '/karma-destin', label: '🔮 Karma & Destin' },
    ],
  },
  { label: 'Horoscope', to: '/horoscope' },
];

const DropdownMenu = ({ item, isActive }) => {
  const [open, setOpen] = useState(false);
  const timerRef = useRef(null);

  const handleMouseEnter = () => { clearTimeout(timerRef.current); setOpen(true); };
  const handleMouseLeave = () => { timerRef.current = setTimeout(() => setOpen(false), 120); };
  useEffect(() => () => clearTimeout(timerRef.current), []);

  return (
    <div className="relative" onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave}>
      <button
        className={`flex items-center gap-1 text-[13px] tracking-widest uppercase transition-colors duration-300 whitespace-nowrap ${
          isActive ? 'text-[#D4B46A]' : 'text-[#D4B46A]/60 hover:text-[#F4D98C]'
        }`}
        style={{ letterSpacing: '0.08em', fontWeight: isActive ? 500 : 400 }}
      >
        {item.label}
        <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} strokeWidth={1.5} />
      </button>

      {open && (
        <div
          className="absolute top-full left-1/2 -translate-x-1/2 mt-2 min-w-[210px] rounded-xl overflow-hidden z-50"
          style={{
            background: 'rgba(11,11,15,0.97)',
            border: '1px solid rgba(212)',
            border: '1px solid rgba(212,180,106,0.18)',
            backdropFilter: 'blur(16px)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.6)',
          }}
        >
          <div
            className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 rotate-45"
            style={{ background: 'rgba(11,11,15,0.97)', border: '1px solid rgba(212,180,106,0.18)', borderBottom: 'none', borderRight: 'none' }}
          />
          <div className="py-1.5">
            {item.children.map((child) => (
              <Link
                key={child.to}
                to={child.to}
                className="flex items-center gap-2 px-4 py-2.5 text-[12px] tracking-wider uppercase transition-all duration-200"
                style={{ color: 'rgba(212,180,106,0.75)', letterSpacing: '0.06em' }}
                onMouseEnter={e => e.currentTarget.style.color = '#F4D98C'}
                onMouseLeave={e => e.currentTarget.style.color = 'rgba(212,180,106,0.75)'}
              >
                {child.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const MonCompteDropdown = ({ creditBalance, handleLogout }) => {
  const [open, setOpen] = useState(false);
  const timerRef = useRef(null);

  const handleMouseEnter = () => { clearTimeout(timerRef.current); setOpen(true); };
  const handleMouseLeave = () => { timerRef.current = setTimeout(() => setOpen(false), 120); };
  useEffect(() => () => clearTimeout(timerRef.current), []);

  return (
    <div className="relative" onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave}>
      <button
        className="flex items-center gap-1.5 text-[12px] tracking-widest uppercase px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-[#D4B46A]/15 whitespace-nowrap"
        style={{ border: '1px solid rgba(212,180,106,0.4)', color: '#D4B46A', letterSpacing: '0.08em', fontWeight: 500 }}
        data-testid="navbar-mon-compte"
      >
        <User className="w-3.5 h-3.5" strokeWidth={1.5} />
        Mon Compte
        <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} strokeWidth={1.5} />
      </button>

      {open && (
        <div
          className="absolute top-full right-0 mt-2 min-w-[220px] rounded-xl overflow-hidden z-50"
          style={{
            background: 'rgba(11,11,15,0.97)',
            border: '1px solid rgba(212,180,106,0.18)',
            backdropFilter: 'blur(16px)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.6)',
          }}
        >
          <div className="py-1.5">
            <Link
              to="/acheter-credits"
              className="flex items-center justify-between px-4 py-2.5 text-[12px] transition-all duration-200"
              style={{ color: 'rgba(212,180,106,0.85)' }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(212,180,106,0.06)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              data-testid="dropdown-credits"
            >
              <span className="flex items-center gap-2">
                <Coins className="w-3.5 h-3.5" strokeWidth={1.5} />
                Mes crédits
              </span>
              <span className="font-semibold" style={{ color: '#D4B46A' }}>{creditBalance}</span>
            </Link>

            <Link
              to="/quotidien"
              className="flex items-center gap-2 px-4 py-2.5 text-[12px] tracking-wider transition-all duration-200"
              style={{ color: 'rgba(212,180,106,0.75)' }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; e.currentTarget.style.color = '#F4D98C'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(212,180,106,0.75)'; }}
              data-testid="dropdown-journal"
            >
              📖 Mon Journal
            </Link>

            <Link
              to="/mon-compte"
              className="flex items-center gap-2 px-4 py-2.5 text-[12px] tracking-wider transition-all duration-200"
              style={{ color: 'rgba(212,180,106,0.75)' }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; e.currentTarget.style.color = '#F4D98C'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(212,180,106,0.75)'; }}
              data-testid="dropdown-recompenses"
            >
              🏆 Mes Récompenses
            </Link>

            <Link
              to="/mon-compte"
              className="flex items-center gap-2 px-4 py-2.5 text-[12px] tracking-wider transition-all duration-200"
              style={{ color: 'rgba(212,180,106,0.75)' }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(212,180,106,0.06)'; e.currentTarget.style.color = '#F4D98C'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(212,180,106,0.75)'; }}
              data-testid="dropdown-profil"
            >
              <User className="w-3 h-3" strokeWidth={1.5} />
              Mon Profil
            </Link>

            <div className="my-1 mx-4" style={{ borderTop: '1px solid rgba(212,180,106,0.1)' }} />

            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-4 py-2.5 text-[12px] tracking-wider transition-all duration-200 text-left"
              style={{ color: 'rgba(255,100,100,0.7)' }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,80,80,0.06)'; e.currentTarget.style.color = '#ff8080'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(255,100,100,0.7)'; }}
              data-testid="dropdown-logout"
            >
              <LogOut className="w-3.5 h-3.5" strokeWidth={1.5} />
              Déconnexion
            </button>
          </div>
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
  const { isAuthenticated, creditBalance, logout } = useAuth();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => { setIsOpen(false); setMobileExpanded(null); }, [location]);

  const handleLogout = () => { logout(); navigate('/'); };

  const isParentActive = (item) => {
    if (!item.children) return location.pathname === item.to;
    return item.children.some(c => location.pathname === c.to);
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled || isOpen ? 'bg-[#0B0B0F]/97 backdrop-blur-md' : 'bg-[#0B0B0F]/70 backdrop-blur-sm'
      }`}
      style={{ borderBottom: scrolled ? '1px solid rgba(197,160,89,0.10)' : '1px solid transparent' }}
      data-testid="navbar"
    >
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">

          <Link
            to="/"
            className="text-base tracking-widest transition-opacity duration-300 hover:opacity-75 whitespace-nowrap flex-shrink-0"
            style={{ fontFamily: 'Cinzel, serif', color: '#D4B46A', fontWeight: 500, letterSpacing: '0.14em', textShadow: '0 0 14px rgba(212,180,106,0.3)' }}
            data-testid="navbar-logo"
          >
            Plume Astrale
          </Link>

          {/* Desktop */}
          <div className="hidden lg:flex items-center gap-5">
            {NAV_ITEMS.map((item) =>
              item.children ? (
                <DropdownMenu key={item.label} item={item} isActive={isParentActive(item)} />
              ) : (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`text-[13px] tracking-widest uppercase transition-colors duration-300 whitespace-nowrap ${
                    location.pathname === item.to ? 'text-[#D4B46A]' : 'text-[#D4B46A]/60 hover:text-[#F4D98C]'
                  }`}
                  style={{ letterSpacing: '0.08em', fontWeight: location.pathname === item.to ? 500 : 400 }}
                >
                  {item.label}
                </Link>
              )
            )}

            <div className="w-px h-4 opacity-20" style={{ background: '#D4B46A' }} />

            {isAuthenticated ? (
              <MonCompteDropdown creditBalance={creditBalance} handleLogout={handleLogout} />
            ) : (
              <>
                <Link
                  to="/connexion"
                  className="flex items-center gap-1.5 text-[12px] tracking-widest uppercase px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-[#D4B46A]/15 whitespace-nowrap"
                  style={{ border: '1px solid rgba(212,180,106,0.45)', color: '#D4B46A', letterSpacing: '0.08em', fontWeight: 500 }}
                  data-testid="navbar-login-btn"
                >
                  <LogIn className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Connexion
                </Link>
                <Link
                  to="/inscription"
                  className="flex items-center gap-1.5 text-[12px] tracking-widest uppercase px-4 py-1.5 rounded-full transition-all duration-500 whitespace-nowrap"
                  style={{ border: '1px solid rgba(212,180,106,0.6)', color: '#D4B46A', background: 'rgba(212,180,106,0.12)', letterSpacing: '0.08em', fontWeight: 500 }}
                  data-testid="navbar-register-btn"
                >
                  Créer un compte
                </Link>
              </>
            )}
          </div>

          {/* Mobile toggle */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="lg:hidden text-[#A9A5A0] hover:text-[#C4A882] transition-colors"
            data-testid="mobile-menu-toggle"
          >
            {isOpen ? <X className="w-5 h-5" strokeWidth={1.5} /> : <Menu className="w-5 h-5" strokeWidth={1.5} />}
          </button>
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <div className="lg:hidden py-5 border-t border-[#C4A882]/10 animate-fade-in">
            <div className="flex flex-col gap-1">
              {NAV_ITEMS.map((item) => (
                <div key={item.label || item.to}>
                  {item.children ? (
                    <>
                      <button
                        onClick={() => setMobileExpanded(mobileExpanded === item.label ? null : item.label)}
                        className="w-full flex items-center justify-between text-[13px] tracking-widest uppercase py-3 transition-colors duration-300 text-[#D4B46A]/60"
                        style={{ letterSpacing: '0.1em' }}
                      >
                        {item.label}
                        <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${mobileExpanded === item.label ? 'rotate-180' : ''}`} strokeWidth={1.5} />
                      </button>
                      {mobileExpanded === item.label && (
                        <div className="pl-4 pb-1 flex flex-col gap-1">
                          {item.children.map(child => (
                            <Link
                              key={child.to}
                              to={child.to}
                              className="text-[12px] tracking-wider py-2 transition-colors duration-200 text-[#D4B46A]/50 hover:text-[#F4D98C]"
                            >
                              {child.label}
                            </Link>
                          ))}
                        </div>
                      )}
                    </>
                  ) : (
                    <Link
                      to={item.to}
                      className={`text-[13px] tracking-widest uppercase py-3 block transition-colors duration-300 ${
                        location.pathname === item.to ? 'text-[#D4B46A]' : 'text-[#D4B46A]/50 hover:text-[#F4D98C]'
                      }`}
                      style={{ letterSpacing: '0.1em' }}
                    >
                      {item.label}
                    </Link>
                  )}
                </div>
              ))}

              <div className="my-2" style={{ borderTop: '1px solid rgba(212,180,106,0.1)' }} />

              {isAuthenticated ? (
                <>
                  <Link to="/acheter-credits" className="flex items-center justify-between py-3 text-[13px]" style={{ color: '#D4B46A' }}>
                    <span className="flex items-center gap-2"><Coins className="w-4 h-4" strokeWidth={1.5} />Mes crédits</span>
                    <span className="font-semibold">{creditBalance}</span>
                  </Link>
                  <Link to="/quotidien" className="flex items-center gap-2 py-3 text-[13px]" style={{ color: 'rgba(212,180,106,0.7)' }}>
                    📖 Mon Journal
                  </Link>
                  <Link to="/mon-compte" className="flex items-center gap-2 py-3 text-[13px]" style={{ color: 'rgba(212,180,106,0.7)' }}>
                    🏆 Mes Récompenses
                  </Link>
                  <button onClick={handleLogout} className="flex items-center gap-2 py-3 text-[13px] text-left" style={{ color: 'rgba(255,100,100,0.8)' }}>
                    <LogOut className="w-4 h-4" strokeWidth={1.5} />Déconnexion
                  </button>
                </>
              ) : (
                <>
                  <Link to="/connexion" className="flex items-center justify-center gap-2 text-[13px] tracking-widest uppercase mt-2 px-6 py-2.5 rounded-full"
                    style={{ border: '1px solid rgba(212,180,106,0.45)', color: '#D4B46A', letterSpacing: '0.1em' }} data-testid="mobile-login-btn">
                    <LogIn className="w-4 h-4" strokeWidth={1.5} />Connexion
                  </Link>
                  <Link to="/inscription" className="flex items-center justify-center gap-2 text-[13px] tracking-widest uppercase mt-1 px-6 py-2.5 rounded-full"
                    style={{ border: '1px solid rgba(212,180,106,0.6)', color: '#D4B46A', background: 'rgba(212,180,106,0.12)', letterSpacing: '0.1em' }} data-testid="mobile-register-btn">
                    Créer un compte
                  </Link>
                </>
