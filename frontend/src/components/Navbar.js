import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, ArrowRight, Coins, LogOut, User, LogIn } from 'lucide-react';
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
    { to: '/tarologie', label: 'Tarologie' },
    { to: '/compatibilite-amoureuse', label: 'Compatibilit\u00e9' },
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
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            to="/"
            className="text-base tracking-widest transition-colors duration-300 hover:opacity-70"
            style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400, letterSpacing: '0.15em' }}
            data-testid="navbar-logo"
          >
            Plume Astrale
          </Link>

          {/* Desktop links */}
          <div className="hidden lg:flex items-center gap-5">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`text-[10px] tracking-widest uppercase transition-colors duration-300 ${
                  location.pathname === link.to
                    ? 'text-[#C4A882]'
                    : 'text-[#A9A5A0]/70 hover:text-[#C4A882]'
                }`}
                style={{ letterSpacing: '0.1em' }}
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
                  className="flex items-center gap-1.5 text-[10px] tracking-widest uppercase px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-[#C5A059]/10"
                  style={{ border: '1px solid rgba(197,160,89,0.25)', color: '#C5A059', letterSpacing: '0.08em' }}
                  data-testid="navbar-credit-balance"
                >
                  <Coins className="w-3 h-3" strokeWidth={1.5} />
                  {creditBalance} crédits
                </Link>
                {/* User menu */}
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 text-[10px] tracking-widest uppercase px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-red-500/10"
                  style={{ border: '1px solid rgba(169,165,160,0.2)', color: '#A9A5A0', letterSpacing: '0.08em' }}
                  data-testid="navbar-logout-btn"
                >
                  <LogOut className="w-3 h-3" strokeWidth={1.5} />
                  Déconnexion
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/connexion"
                  className="flex items-center gap-1.5 text-[10px] tracking-widest uppercase px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-[#C5A059]/10"
                  style={{ border: '1px solid rgba(197,160,89,0.35)', color: '#C5A059', letterSpacing: '0.08em' }}
                  data-testid="navbar-login-btn"
                >
                  <LogIn className="w-3 h-3" strokeWidth={1.5} />
                  Connexion
                </Link>
                <Link
                  to="/inscription"
                  className="flex items-center gap-1.5 text-[10px] tracking-widest uppercase px-4 py-1.5 rounded-full transition-all duration-500"
                  style={{
                    border: '1px solid rgba(197,160,89,0.5)',
                    color: '#C5A059',
                    background: 'rgba(197,160,89,0.08)',
                    letterSpacing: '0.08em',
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
                  className={`text-xs tracking-widest uppercase py-2 transition-colors duration-300 ${
                    location.pathname === link.to
                      ? 'text-[#C4A882]'
                      : 'text-[#A9A5A0]/70 hover:text-[#C4A882]'
                  }`}
                  style={{ letterSpacing: '0.12em' }}
                  data-testid={`mobile-nav-link-${link.to.replace(/\//g, '') || 'home'}`}
                >
                  {link.label}
                </Link>
              ))}

              {isAuthenticated ? (
                <>
                  <Link
                    to="/acheter-credits"
                    className="flex items-center gap-2 text-xs tracking-widest uppercase py-2 transition-colors duration-300"
                    style={{ color: '#C5A059', letterSpacing: '0.12em' }}
                    data-testid="mobile-credit-balance"
                  >
                    <Coins className="w-3.5 h-3.5" strokeWidth={1.5} />
                    {creditBalance} crédits
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 text-xs tracking-widest uppercase py-2 transition-colors duration-300 text-left"
                    style={{ color: '#A9A5A0', letterSpacing: '0.12em' }}
                    data-testid="mobile-logout-btn"
                  >
                    <LogOut className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Déconnexion
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/connexion"
                    className="flex items-center justify-center gap-2 text-xs tracking-widest uppercase mt-3 px-6 py-2.5 rounded-full transition-all"
                    style={{ border: '1px solid rgba(197,160,89,0.35)', color: '#C5A059', letterSpacing: '0.1em' }}
                    data-testid="mobile-login-btn"
                  >
                    <LogIn className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Connexion
                  </Link>
                  <Link
                    to="/inscription"
                    className="flex items-center justify-center gap-2 text-xs tracking-widest uppercase mt-1 px-6 py-2.5 rounded-full transition-all"
                    style={{ border: '1px solid rgba(197,160,89,0.5)', color: '#C5A059', background: 'rgba(197,160,89,0.08)', letterSpacing: '0.1em' }}
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
