import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isPaid, setIsPaid] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const paid = localStorage.getItem('plume_astrale_paid');
    setIsPaid(paid === 'true');
  }, [location]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const links = [
    { to: '/tarot-oui-non', label: 'Tirage' },
    { to: '/formulaire', label: 'Theme Astral' },
    { to: '/numerologie', label: 'Numerologie' },
    { to: '/quotidien', label: 'Guidance' },
    { to: '/tarologie', label: 'Tarologie' },
    { to: '/compatibilite-amoureuse', label: 'Compatibilite' },
    { to: '/premium', label: 'Premium', accent: true },
  ];

  if (isPaid) {
    links.push({ to: '/resultats', label: 'Mon Manuscrit' });
  }

  // Hide on homepage
  if (location.pathname === '/') return null;

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled ? 'bg-[#0B0B0F]/95 backdrop-blur-md' : 'bg-transparent'
      }`}
      data-testid="navbar"
    >
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <Link
            to="/"
            className="text-base tracking-widest transition-colors duration-300 hover:opacity-70"
            style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400, letterSpacing: '0.15em' }}
          >
            Plume Astrale
          </Link>

          {/* Desktop */}
          <div className="hidden md:flex items-center gap-8">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`text-xs tracking-widest uppercase transition-colors duration-300 ${
                  location.pathname === link.to
                    ? 'text-[#C4A882]'
                    : 'text-[#A9A5A0]/70 hover:text-[#C4A882]'
                }`}
                style={{ letterSpacing: '0.12em' }}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Mobile toggle */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-[#A9A5A0] hover:text-[#C4A882] transition-colors"
            data-testid="mobile-menu-toggle"
          >
            {isOpen ? <X className="w-5 h-5" strokeWidth={1.5} /> : <Menu className="w-5 h-5" strokeWidth={1.5} />}
          </button>
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <div className="md:hidden py-6 border-t border-[#C4A882]/10 animate-fade-in">
            <div className="flex flex-col gap-4">
              {links.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={() => setIsOpen(false)}
                  className={`text-xs tracking-widest uppercase py-2 transition-colors duration-300 ${
                    location.pathname === link.to
                      ? 'text-[#C4A882]'
                      : 'text-[#A9A5A0]/70 hover:text-[#C4A882]'
                  }`}
                  style={{ letterSpacing: '0.12em' }}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
