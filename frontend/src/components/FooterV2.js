import React from 'react';
import { Link } from 'react-router-dom';
import { Instagram, Mail, Facebook, Twitter } from 'lucide-react';
import CelestialBackdrop from './CelestialBackdrop';

// Configuration des réseaux sociaux — URLs à mettre à jour quand les comptes
// sont créés. Passer une chaîne vide pour masquer une icône.
const SOCIAL_LINKS = {
  instagram: 'https://instagram.com/plumeastrale.fr',
  facebook: 'https://www.facebook.com/plumeastrale',  // à créer/vérifier
  x:        'https://x.com/plumeastrale',              // à créer/vérifier
  // linkedin retiré — pas de compte Plume Astrale sur LinkedIn.
};

/**
 * Footer V3 — refonte identité visuelle Feb 2026
 * Fond bleu nuit #0F1A3C, liens secondaires + mentions légales + réseaux
 */
export default function FooterV2() {
  const year = new Date().getFullYear();

  return (
    <footer data-testid="footer-v2" style={{
      background: '#0F1A3C',
      color: 'rgba(247,245,240,0.72)',
      borderTop: '1px solid rgba(201,162,75,0.15)',
      fontFamily: 'Inter, sans-serif',
      position: 'relative',
      overflow: 'hidden',
    }}>
      <CelestialBackdrop density={50} shootingStars={false} />
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '64px 24px 32px', position: 'relative', zIndex: 1 }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 48,
        }}>
          {/* Brand */}
          <div>
            <div style={{
              fontFamily: 'Playfair Display, serif',
              fontSize: 24, fontWeight: 500,
              color: '#F7F5F0', marginBottom: 12,
            }}>
              Plume <span style={{ color: '#C9A24B' }}>Astrale</span>
            </div>
            <p style={{
              fontSize: 14, lineHeight: 1.6, margin: 0,
              color: 'rgba(247,245,240,0.60)', maxWidth: 260,
            }}>
              L&apos;astrologie qui sait ton prénom.<br />
              Personnalisée à partir de ton ciel.
            </p>
          </div>

          {/* Explorer */}
          <div>
            <FooterHeading>Explorer</FooterHeading>
            <FooterLink to="/">Accueil</FooterLink>
            <FooterLink to="/livres">Services</FooterLink>
            <FooterLink to="/blog">Blog</FooterLink>
            <FooterLink to="/temoignages">Témoignages</FooterLink>
            <FooterLink to="/quotidien">Horoscope du jour</FooterLink>
          </div>

          {/* Aide */}
          <div>
            <FooterHeading>Aide</FooterHeading>
            <FooterLink to="/contact" testid="footer-v2-contact-link">Contact</FooterLink>
            <FooterLink to="/inscription">Créer un compte</FooterLink>
            <FooterLink to="/connexion">Se connecter</FooterLink>
            <FooterLink to="/mon-compte">Mon espace</FooterLink>
            <FooterLink to="/livres" testid="footer-v2-livres-link">Nos livres prestige</FooterLink>
            <FooterLink to="/credits" testid="footer-v2-credits-link">Comprendre les crédits</FooterLink>
            <a href="mailto:contact@plume-astrale.fr" style={footerLinkStyle} data-testid="footer-v2-contact">
              contact@plume-astrale.fr
            </a>
          </div>

          {/* Légal */}
          <div>
            <FooterHeading>Légal</FooterHeading>
            <FooterLink to="/mentions-legales" testid="footer-v2-mentions">Mentions légales</FooterLink>
            <FooterLink to="/cgv" testid="footer-v2-cgv">Conditions générales</FooterLink>
            <div style={{
              fontSize: 12, color: 'rgba(247,245,240,0.4)',
              marginTop: 14, letterSpacing: '0.04em',
            }}>
              RGPD · CNIL · Stripe PCI-DSS
            </div>

            {/* Réseaux sociaux */}
            <div style={{ display: 'flex', gap: 12, marginTop: 20, flexWrap: 'wrap' }}>
              {SOCIAL_LINKS.instagram && (
                <a href={SOCIAL_LINKS.instagram} aria-label="Instagram · @plumeastrale.fr"
                  target="_blank" rel="noopener noreferrer"
                  data-testid="footer-v2-instagram"
                  style={socialIcon}>
                  <Instagram style={{ width: 18, height: 18 }} strokeWidth={1.6} />
                </a>
              )}
              {SOCIAL_LINKS.facebook && (
                <a href={SOCIAL_LINKS.facebook} aria-label="Facebook"
                  target="_blank" rel="noopener noreferrer"
                  data-testid="footer-v2-facebook"
                  style={socialIcon}>
                  <Facebook style={{ width: 18, height: 18 }} strokeWidth={1.6} />
                </a>
              )}
              {SOCIAL_LINKS.x && (
                <a href={SOCIAL_LINKS.x} aria-label="X (Twitter)"
                  target="_blank" rel="noopener noreferrer"
                  data-testid="footer-v2-x"
                  style={socialIcon}>
                  <Twitter style={{ width: 18, height: 18 }} strokeWidth={1.6} />
                </a>
              )}
              <a href="mailto:contact@plume-astrale.fr" aria-label="Email"
                data-testid="footer-v2-email-icon"
                style={socialIcon}>
                <Mail style={{ width: 18, height: 18 }} strokeWidth={1.6} />
              </a>
            </div>
          </div>
        </div>

        <div style={{
          marginTop: 48,
          paddingTop: 24,
          borderTop: '1px solid rgba(247,245,240,0.08)',
          fontSize: 12,
          color: 'rgba(247,245,240,0.42)',
          textAlign: 'center',
          letterSpacing: '0.06em',
        }}>
          © {year} Plume Astrale · Tous droits réservés · Fait avec soin en France
        </div>
      </div>
    </footer>
  );
}

const footerLinkStyle = {
  display: 'block',
  padding: '5px 0',
  fontSize: 14,
  color: 'rgba(247,245,240,0.72)',
  textDecoration: 'none',
  transition: 'color 200ms ease',
  fontFamily: 'Inter, sans-serif',
};

const socialIcon = {
  display: 'inline-flex',
  alignItems: 'center', justifyContent: 'center',
  width: 40, height: 40,
  borderRadius: 999,
  border: '1px solid rgba(201,162,75,0.35)',
  color: '#C9A24B',
  transition: 'background 200ms ease, border-color 200ms ease',
  textDecoration: 'none',
};

function FooterHeading({ children }) {
  return (
    <div style={{
      fontFamily: 'Inter, sans-serif',
      fontSize: 12, fontWeight: 600,
      letterSpacing: '0.14em',
      textTransform: 'uppercase',
      color: '#C9A24B',
      marginBottom: 16,
    }}>
      {children}
    </div>
  );
}

function FooterLink({ to, children, testid }) {
  return (
    <Link to={to} data-testid={testid} style={footerLinkStyle}
      onMouseEnter={(e) => (e.currentTarget.style.color = '#C9A24B')}
      onMouseLeave={(e) => (e.currentTarget.style.color = 'rgba(247,245,240,0.72)')}>
      {children}
    </Link>
  );
}
