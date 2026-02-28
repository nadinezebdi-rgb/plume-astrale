import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sparkles, Menu, X, Star, Moon, Heart, Sun, Eye, BookOpen, Hash } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isPaid, setIsPaid] = useState(false);
  const [plan, setPlan] = useState(null);
  const location = useLocation();

  useEffect(() => {
    const paid = localStorage.getItem('plume_astrale_paid');
    const userPlan = localStorage.getItem('plume_astrale_plan');
    setIsPaid(paid === 'true');
    setPlan(userPlan);
  }, [location]);

  const publicLinks = [
    { to: '/', label: 'Accueil', icon: <Sparkles className="w-4 h-4" strokeWidth={1} /> },
    { to: '/compatibilite-amoureuse', label: 'Compatibilite', icon: <Heart className="w-4 h-4" strokeWidth={1} />, highlight: true },
    { to: '/quotidien', label: 'Guidance du Jour', icon: <Sun className="w-4 h-4" strokeWidth={1} /> },
    { to: '/tarot-oui-non', label: 'Tarot Oui/Non', icon: <Eye className="w-4 h-4" strokeWidth={1} /> },
    { to: '/numerologie', label: 'Numerologie', icon: <Hash className="w-4 h-4" strokeWidth={1} /> },
    { to: '/tarologie', label: 'Tarologie', icon: <BookOpen className="w-4 h-4" strokeWidth={1} /> },
  ];

  const premiumLinks = [
    { to: '/resultats', label: 'Mon Manuscrit', icon: <Star className="w-4 h-4" strokeWidth={1} /> },
    { to: '/horoscope', label: 'Horoscope', icon: <Moon className="w-4 h-4" strokeWidth={1} /> },
    { to: '/tarot', label: 'Tarot Avance', icon: <Moon className="w-4 h-4" strokeWidth={1} />, premium: true },
    { to: '/compatibilite', label: 'Compatibilite', icon: <Heart className="w-4 h-4" strokeWidth={1} />, premium: true }
  ];

  const links = isPaid ? [...publicLinks, ...premiumLinks] : publicLinks;

  // Ne pas afficher la navbar sur certaines pages
  const hideNavbarPaths = ['/', '/formulaire', '/apercu', '/choix', '/paiement'];
  if (hideNavbarPaths.includes(location.pathname)) {
    return null;
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0F0518]/90 backdrop-blur-lg border-b border-[#C5A059]/10">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-[#C5A059]" strokeWidth={1} />
            <span className="text-lg" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Plume Astrale
            </span>
          </Link>

          {/* Desktop Links */}
          <div className="hidden md:flex items-center gap-6">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-2 text-sm transition-colors ${
                  link.highlight
                    ? 'px-3 py-1.5 rounded-full border border-[#C5A059] text-[#C5A059] hover:bg-[#C5A059]/10 font-medium'
                    : location.pathname === link.to
                      ? 'text-[#C5A059]'
                      : 'text-[#E0D9F6]/70 hover:text-[#C5A059]'
                }`}
              >
                {link.icon}
                <span>{link.label}</span>
                {link.premium && plan !== 'premium' && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#C5A059]/20 text-[#C5A059]">
                    Premium
                  </span>
                )}
              </Link>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-[#E0D9F6]/70 hover:text-[#C5A059]"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 border-t border-[#C5A059]/10">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 py-3 px-2 rounded-lg transition-colors ${
                  location.pathname === link.to
                    ? 'text-[#C5A059] bg-[#C5A059]/10'
                    : 'text-[#E0D9F6]/70 hover:text-[#C5A059]'
                }`}
              >
                {link.icon}
                <span>{link.label}</span>
                {link.premium && plan !== 'premium' && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#C5A059]/20 text-[#C5A059]">
                    Premium
                  </span>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
