import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, ArrowRight, Coins, LogOut, User, LogIn, Gift } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, creditBalance, logout } = useAuth();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    setIsOpen(false);
  }, [location]);

  const links = [
    { to: '/', label: 'Accueil' },
    { to: '/cercle', label: 'Le Cercle' },
    { to: '/tarot-oui-non', label: 'Tirage' },
    { to: '/formulaire', label: 'Th\u00e8me Astral' },
    { to: '/numerologie', label: 'Num\u00e9rologie' },
    { to: '/essai-gratuit', label: 'Essai Gratuit' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled || isOpen ? 'bg-[#0B0B0F]/95 backdrop-blur-md' : 'bg-[#0B0B0F]/60 backdrop-blur-sm'
      }`}
      style={{ borderBottom: scrolled ? '1px solid rgba(197,160,89,0.08)' : '1px solid transparent' }}
      data-testid="navbar"
    >
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            to="/"
            className="text-base tracking-widest transition-colors duration-300 hover:opacity-80 whitespace-nowrap"
            style={{ fontFamily: 'Cinzel, serif', color: '#D4B46A', fontWeight: 500, letterSpacing: '0.12em', textShadow: '0 0 12px rgba(212,180,106,0.25)' }}
            data-testid="navbar-logo"
          >
            Plume Astrale
          </Link>

          {/* Desktop links */}
          <div className="hidden lg:flex items-center gap-3">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`text-[13px] tracking-widest uppercase transition-colors duration-300 whitespace-nowrap ${
                  location.pathname === link.to
                    ? 'text-[#D4B46A]'
                    : link.to === '/essai-gratuit'
                      ? 'text-[#34D399]/80 hover:text-[#34D399]'
                      : 'text-[#D4B46A]/60 hover:text-[#F4D98C]'
                }`}
                style={{ letterSpacing: '0.08em', fontWeight: location.pathname === link.to ? 500 : 400 }}
                data-testid={`nav-link-${link.to.replace(/\//g, '') || 'home'}`}
              >
                {link.label}
              </Link>
            ))}

            {isAuthenticated ? (
              <>
                {/* Credit balance */}
                <Link
                  to="/acheter-credits"
                  className="flex items-center gap-1.5 text-[12px] tracking-widest uppercase px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-[#D4B46A]/15 whitespace-nowrap"
                  style={{ border: '1px solid rgba(212,180,106,0.4)', color: '#D4B46A', letterSpacing: '0.08em', fontWeight: 500, textShadow: '0 0 8px rgba(212,180,106,0.2)' }}
                  data-testid="navbar-credit-balance"
                >
                  <Coins className="w-3.5 h-3.5" strokeWidth={1.5} />
                  {creditBalance} cr.
                </Link>
                {/* Mon Compte */}
                <Link
                  to="/mon-compte"
                  className="flex items-center gap-1.5 text-[12px] tracking-widest uppercase px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-[#D4B46A]/15 whitespace-nowrap"
                  style={{ border: '1px solid rgba(212,180,106,0.3)', color: '#D4B46A', letterSpacing: '0.08em', fontWeight: 400 }}
                  data-testid="navbar-account-btn"
                >
                  <User className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Mon Compte
                </Link>
              </>
            ) : (
              <>
                <Link
                  to="/connexion"
                  className="flex items-center gap-1.5 text-[12px] tracking-widest uppercase px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-[#D4B46A]/15 whitespace-nowrap"
                  style={{ border: '1px solid rgba(212,180,106,0.45)', color: '#D4B46A', letterSpacing: '0.08em', fontWeight: 500, textShadow: '0 0 8px rgba(212,180,106,0.15)' }}
                  data-testid="navbar-login-btn"
                >
                  <LogIn className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Connexion
                </Link>
                <Link
                  to="/inscription"
                  className="flex items-center gap-1.5 text-[12px] tracking-widest uppercase px-4 py-1.5 rounded-full transition-all duration-500 whitespace-nowrap"
                  style={{
                    border: '1px solid rgba(212,180,106,0.6)',
                    color: '#D4B46A',
                    background: 'rgba(212,180,106,0.12)',
                    letterSpacing: '0.08em',
                    fontWeight: 500,
                    textShadow: '0 0 8px rgba(212,180,106,0.2)',
                  }}
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
          <div className="lg:hidden py-6 border-t border-[#C4A882]/10 animate-fade-in">
            <div className="flex flex-col gap-3">
              {links.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`text-[13px] tracking-widest uppercase py-2 transition-colors duration-300 ${
                    location.pathname === link.to
                      ? 'text-[#D4B46A]'
                      : link.to === '/essai-gratuit'
                        ? 'text-[#34D399]/70 hover:text-[#34D399]'
                        : 'text-[#D4B46A]/50 hover:text-[#F4D98C]'
                  }`}
                  style={{ letterSpacing: '0.12em', fontWeight: location.pathname === link.to ? 500 : 400 }}
                  data-testid={`mobile-nav-link-${link.to.replace(/\//g, '') || 'home'}`}
                >
                  {link.to === '/essai-gratuit' && <Gift className="w-3.5 h-3.5 inline mr-2" strokeWidth={1.5} />}
                  {link.label}
                </Link>
              ))}

              {isAuthenticated ? (
                <>
                  <Link
                    to="/acheter-credits"
                    className="flex items-center gap-2 text-[13px] tracking-widest uppercase py-2 transition-colors duration-300"
                    style={{ color: '#D4B46A', letterSpacing: '0.12em', fontWeight: 500 }}
                    data-testid="mobile-credit-balance"
                  >
                    <Coins className="w-4 h-4" strokeWidth={1.5} />
                    {creditBalance} crédits
                  </Link>
                  <Link
                    to="/mon-compte"
                    className="flex items-center gap-2 text-[13px] tracking-widest uppercase py-2 transition-colors duration-300"
                    style={{ color: '#D4B46A', letterSpacing: '0.12em', fontWeight: 500 }}
                    data-testid="mobile-account-btn"
                  >
                    <User className="w-4 h-4" strokeWidth={1.5} />
                    Mon Compte
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 text-[13px] tracking-widest uppercase py-2 transition-colors duration-300 text-left"
                    style={{ color: '#D4B46A', letterSpacing: '0.12em' }}
                    data-testid="mobile-logout-btn"
                  >
                    <LogOut className="w-4 h-4" strokeWidth={1.5} />
                    Déconnexion
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/connexion"
                    className="flex items-center justify-center gap-2 text-[13px] tracking-widest uppercase mt-3 px-6 py-2.5 rounded-full transition-all"
                    style={{ border: '1px solid rgba(212,180,106,0.45)', color: '#D4B46A', letterSpacing: '0.1em', fontWeight: 500 }}
                    data-testid="mobile-login-btn"
                  >
                    <LogIn className="w-4 h-4" strokeWidth={1.5} />
                    Connexion
                  </Link>
                  <Link
                    to="/inscription"
                    className="flex items-center justify-center gap-2 text-[13px] tracking-widest uppercase mt-1 px-6 py-2.5 rounded-full transition-all"
                    style={{ border: '1px solid rgba(212,180,106,0.6)', color: '#D4B46A', background: 'rgba(212,180,106,0.12)', letterSpacing: '0.1em', fontWeight: 500 }}
                    data-testid="mobile-register-btn"
                  >
                    Créer un compte
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
