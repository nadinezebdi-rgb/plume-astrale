import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Coins, Sparkles, Edit3, ArrowRight, LogOut } from 'lucide-react';
import SEO from '@/components/SEO';
import BundleCard from '@/components/BundleCard';

const AuthenticatedHome = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, creditBalance, logout } = useAuth();

  // Si pas authentifié -> rediriger vers home
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <>
      <SEO path="/mon-accueil" />
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #131840 0%, #1B2150 50%, #131840 100%)',
        padding: '100px 20px 40px',
      }}>
        <div style={{ maxWidth: 1000, margin: '0 auto' }}>
          
          {/* En-tête */}
          <div className="mb-12 text-center">
            <h1 style={{
              fontSize: '2.5rem',
              fontFamily: 'Cormorant Garamond, serif',
              color: '#F0E6D3',
              marginBottom: 8,
              fontWeight: 400,
            }}>
              Bienvenue {user?.email ? `${user.email.split('@')[0]}` : ''}
            </h1>
            <p style={{
              fontSize: '0.9rem',
              color: 'rgba(240,230,211,0.7)',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
            }}>
              Votre espace de navigation
            </p>
          </div>

          {/* Bundle Découverte Soléna — offre irrésistible post-inscription */}
          <div style={{ marginBottom: 40 }}>
            <BundleCard testId="authenticated-home-bundle" />
          </div>

          {/* Crédit et profil */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 24,
            marginBottom: 40,
          }}>
            {/* Crédits disponibles */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(184,150,31,0.15) 0%, rgba(232,199,102,0.1) 100%)',
              border: '1px solid rgba(184,150,31,0.3)',
              borderRadius: 16,
              padding: 24,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Coins style={{ width: 20, height: 20, color: '#B8961F' }} strokeWidth={1.5} />
                <h3 style={{
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.15em',
                  color: 'rgba(184,150,31,0.8)',
                  margin: 0,
                  fontWeight: 500,
                }}>Mes crédits</h3>
              </div>
              <p style={{
                fontSize: '2.5rem',
                fontFamily: 'Cormorant Garamond, serif',
                color: '#E8C766',
                margin: 0,
                fontWeight: 400,
              }}>
                {creditBalance}
              </p>
              <p style={{
                fontSize: '0.85rem',
                color: 'rgba(240,230,211,0.6)',
                marginTop: 8,
                margin: '8px 0 0 0',
              }}>
                Crédits disponibles pour les services
              </p>
              <Link
                to="/acheter-credits"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  marginTop: 12,
                  padding: '8px 16px',
                  borderRadius: 8,
                  background: 'rgba(184,150,31,0.2)',
                  color: '#E8C766',
                  textDecoration: 'none',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  border: '1px solid rgba(184,150,31,0.4)',
                  transition: 'all 0.3s',
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(184,150,31,0.3)';
                  e.currentTarget.style.boxShadow = '0 4px 16px rgba(184,150,31,0.2)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(184,150,31,0.2)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                Acheter plus <ArrowRight style={{ width: 12, height: 12 }} strokeWidth={1.5} />
              </Link>
            </div>

            {/* Profil */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(167,139,250,0.1) 0%, rgba(196,181,253,0.08) 100%)',
              border: '1px solid rgba(196,181,253,0.2)',
              borderRadius: 16,
              padding: 24,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Edit3 style={{ width: 20, height: 20, color: '#A78BFA' }} strokeWidth={1.5} />
                <h3 style={{
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.15em',
                  color: 'rgba(196,181,253,0.8)',
                  margin: 0,
                  fontWeight: 500,
                }}>Mon Profil</h3>
              </div>
              <p style={{
                fontSize: '1.1rem',
                color: '#E3D7FF',
                margin: '0 0 8px 0',
                fontWeight: 500,
              }}>
                {user?.email || 'Profil utilisateur'}
              </p>
              <p style={{
                fontSize: '0.85rem',
                color: 'rgba(240,230,211,0.6)',
                marginTop: 0,
              }}>
                {user?.birth_date ? '✓ Données natales complètes' : 'Données natales à remplir'}
              </p>
              <Link
                to="/mon-compte"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  marginTop: 12,
                  padding: '8px 16px',
                  borderRadius: 8,
                  background: 'rgba(196,181,253,0.15)',
                  color: '#E3D7FF',
                  textDecoration: 'none',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  border: '1px solid rgba(196,181,253,0.3)',
                  transition: 'all 0.3s',
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(196,181,253,0.25)';
                  e.currentTarget.style.boxShadow = '0 4px 16px rgba(196,181,253,0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(196,181,253,0.15)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                Modifier <ArrowRight style={{ width: 12, height: 12 }} strokeWidth={1.5} />
              </Link>
            </div>
          </div>

          {/* Services rapides */}
          <div style={{ marginBottom: 40 }}>
            <h2 style={{
              fontSize: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.2em',
              color: 'rgba(184,150,31,0.7)',
              margin: '0 0 16px 0',
              fontFamily: 'Cinzel, serif',
              fontWeight: 500,
            }}>Services disponibles</h2>
            
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: 12,
            }}>
              {[
                { icon: '🔮', label: 'Tarot', to: '/outils/tarot' },
                { icon: '⭐', label: 'Horoscope', to: '/outils/horoscope' },
                { icon: '🔢', label: 'Numérologie', to: '/outils/numerologie' },
                { icon: '💕', label: 'Compatibilité', to: '/outils/compatibilite' },
                { icon: '💬', label: 'Chat Astral (IA)', to: '/outils/consultation' },
                { icon: '✨', label: 'Énergie du jour', to: '/outils/energie' },
              ].map((service) => (
                <Link
                  key={service.to}
                  to={service.to}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: 16,
                    borderRadius: 12,
                    background: 'rgba(184,150,31,0.08)',
                    border: '1px solid rgba(184,150,31,0.2)',
                    color: '#E8C766',
                    textDecoration: 'none',
                    fontSize: '0.9rem',
                    fontWeight: 500,
                    transition: 'all 0.3s',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(184,150,31,0.15)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(184,150,31,0.15)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(184,150,31,0.08)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <span style={{ fontSize: '1.2rem' }}>{service.icon}</span>
                  {service.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div style={{
            display: 'flex',
            gap: 12,
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}>
            <button
              onClick={handleLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '10px 20px',
                borderRadius: 8,
                background: 'rgba(220,38,38,0.15)',
                border: '1px solid rgba(220,38,38,0.3)',
                color: '#fca5a5',
                fontSize: '0.75rem',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                cursor: 'pointer',
                transition: 'all 0.3s',
                fontWeight: 500,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(220,38,38,0.25)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(220,38,38,0.15)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(220,38,38,0.15)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <LogOut style={{ width: 14, height: 14 }} strokeWidth={1.5} />
              Déconnexion
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default AuthenticatedHome;
