import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, ArrowRight } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isPaid, setIsPaid] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const paid = localStorage.getItem('plume_astrale_paid');
    setIsPaid(paid === 'true');
  }, [location]);

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
    { to: '/tarot-oui-non', label: 'Tirage' },
    { to: '/formulaire', label: 'Theme Astral' },
    { to: '/numerologie', label: 'Numerologie' },
    { to: '/tarologie', label: 'Tarologie' },
    { to: '/compatibilite-amoureuse', label: 'Compatibilite' },
    { to: '/charte-de-confiance', label: 'Charte de Confiance' },
    { to: '/premium', label: 'Premium', accent: true },
  ];

  if (isPaid) {
    links.push({ to: '/resultats', label: 'Mon Manuscrit' });
  }

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
          <div className="hidden lg:flex items-center gap-6">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`text-[10px] tracking-widest uppercase transition-colors duration-300 ${
                  link.accent
                    ? 'text-[#C5A059] hover:text-[#D4B46A]'
                    : location.pathname === link.to
                    ? 'text-[#C4A882]'
                    : 'text-[#A9A5A0]/70 hover:text-[#C4A882]'
                }`}
                style={{ letterSpacing: '0.1em' }}
                data-testid={`nav-link-${link.to.replace(/\//g, '') || 'home'}`}
              >
                {link.label}
              </Link>
            ))}
            {/* CTA */}
            <button
              onClick={() => navigate('/tarot-oui-non')}
              className="flex items-center gap-1.5 text-[10px] tracking-widest uppercase px-4 py-1.5 rounded-full transition-all duration-300 hover:bg-[#C5A059]/20"
              style={{
                border: '1px solid rgba(197,160,89,0.4)',
                color: '#C5A059',
                letterSpacing: '0.08em',
              }}
              data-testid="navbar-cta"
            >
              Recevoir une reponse <ArrowRight className="w-3 h-3" strokeWidth={1.5} />
            </button>
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
                    link.accent
                      ? 'text-[#C5A059]'
                      : location.pathname === link.to
                      ? 'text-[#C4A882]'
                      : 'text-[#A9A5A0]/70 hover:text-[#C4A882]'
                  }`}
                  style={{ letterSpacing: '0.12em' }}
                  data-testid={`mobile-nav-link-${link.to.replace(/\//g, '') || 'home'}`}
                >
                  {link.label}
                </Link>
              ))}
              {/* Mobile CTA */}
              <button
                onClick={() => navigate('/tarot-oui-non')}
                className="flex items-center justify-center gap-2 text-xs tracking-widest uppercase mt-3 px-6 py-2.5 rounded-full transition-all"
                style={{
                  border: '1px solid rgba(197,160,89,0.4)',
                  color: '#C5A059',
                  letterSpacing: '0.1em',
                }}
                data-testid="mobile-navbar-cta"
              >
                Recevoir une reponse <ArrowRight className="w-3.5 h-3.5" strokeWidth={1.5} />
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
