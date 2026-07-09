import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { UserRound, Sparkles, Gem } from 'lucide-react';

/**
 * Mobile Tab Bar sticky bottom — signature "app native" a la Calm/Headspace.
 * 3 icones fines : Mon Espace / Consulter / Tarifs.
 * Auto-hide sur >= 768px.
 */
const items = [
  { to: '/dashboard', label: 'Mon Espace', Icon: UserRound, testid: 'tabbar-espace' },
  { to: '/consultation', label: 'Consulter', Icon: Sparkles, testid: 'tabbar-consulter', primary: true },
  { to: '/tarifs', label: 'Tarifs', Icon: Gem, testid: 'tabbar-tarifs' },
];

const MobileTabBar = () => {
  const { pathname } = useLocation();
  // On masque la TabBar sur les pages de checkout / auth pour eviter les distractions
  if (pathname.startsWith('/auth') || pathname.startsWith('/checkout') || pathname.startsWith('/paiement')) {
    return null;
  }
  return (
    <nav className="plume-tabbar" role="navigation" aria-label="Menu principal mobile" data-testid="mobile-tabbar">
      <ul className="flex items-center justify-around gap-1 max-w-md mx-auto">
        {items.map(({ to, label, Icon, testid, primary }) => (
          <li key={to} className="flex-1">
            <NavLink
              to={to}
              end
              data-testid={testid}
              className={({ isActive }) => `
                flex flex-col items-center justify-center gap-1 py-1 px-2 rounded-xl
                transition-colors duration-200 ease-plume-silk
                ${isActive
                  ? 'text-plume-gold'
                  : 'text-plume-lavender/70 hover:text-plume-lavender'}
                ${primary ? '' : ''}
              `}
            >
              <Icon strokeWidth={1.5} className={`w-5 h-5 ${primary ? 'drop-shadow-[0_0_8px_rgba(212,175,55,0.45)]' : ''}`} />
              <span className="text-[10px] font-plume-body uppercase tracking-widest">{label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default MobileTabBar;
