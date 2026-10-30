import { Link, useLocation } from 'react-router-dom';
import { Instagram, Mail, Facebook, Twitter } from 'lucide-react';

// Configuration des réseaux sociaux
const SOCIAL_LINKS = {
  instagram: 'https://instagram.com/plumeastrale.fr',
  facebook: 'https://www.facebook.com/plumeastrale',
  x:        'https://x.com/plumeastrale',
};

/**
 * Footer V3 — version simplifiée Feb 2026
 * Fond bleu nuit uni, uniquement logo + mentions légales + réseaux sociaux.
 * La navigation commerciale/éditoriale est désormais gérée par la section
 * "Explore ton univers" juste au-dessus du footer sur la home.
 */
export default function FooterV2() {
  const { pathname } = useLocation();
  if (pathname === '/experience' || pathname.startsWith('/experience/')) {
    return null;
  }
  const year = new Date().getFullYear();

  return (
    <footer
      data-testid="footer-v2"
      style={{
        background: '#0A1130',
        color: 'rgba(244,239,230,0.72)',
        borderTop: '1px solid rgba(212,175,55,0.18)',
        fontFamily: 'Inter, sans-serif',
      }}
    >
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '48px 24px 28px' }}>
        <div
          className="footer-v2__row"
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 32,
          }}
        >
          {/* Brand */}
          <Link
            to="/"
            data-testid="footer-v2-brand"
            style={{
              fontFamily: "'Fraunces', 'Playfair Display', serif",
              fontSize: 24,
              fontWeight: 400,
              letterSpacing: '-0.015em',
              fontVariationSettings: "'opsz' 144, 'SOFT' 50",
              color: 'var(--plume-ivory)',
              textDecoration: 'none',
            }}
          >
            Plume <span style={{ color: 'var(--plume-gold)' }}>Astrale</span>
          </Link>

          {/* Legal links */}
          <nav
            aria-label="Liens légaux"
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              gap: 24,
            }}
          >
            <FooterLink to="/mentions-legales" testid="footer-v2-mentions">Mentions légales</FooterLink>
            <FooterLink to="/cgv" testid="footer-v2-cgv">CGV</FooterLink>
            <FooterLink to="/confidentialite" testid="footer-v2-confidentialite">Confidentialité</FooterLink>
            <FooterLink to="/contact" testid="footer-v2-contact-link">Contact</FooterLink>
            <button
              type="button"
              onClick={() => window.dispatchEvent(new Event('open-cookie-preferences'))}
              data-testid="footer-v2-cookies"
              style={{
                background: 'transparent',
                border: 'none',
                padding: 0,
                margin: 0,
                color: 'rgba(244,239,230,0.72)',
                fontFamily: 'Inter, sans-serif',
                fontSize: 13,
                cursor: 'pointer',
                letterSpacing: '0.02em',
              }}
            >
              Cookies
            </button>
          </nav>

          {/* Socials */}
          <div
            style={{ display: 'flex', gap: 10, alignItems: 'center' }}
            data-testid="footer-v2-socials"
          >
            {SOCIAL_LINKS.instagram && (
              <a
                href={SOCIAL_LINKS.instagram}
                aria-label="Instagram · @plumeastrale.fr"
                target="_blank"
                rel="noopener noreferrer"
                data-testid="footer-v2-instagram"
                style={socialIcon}
              >
                <Instagram style={{ width: 16, height: 16 }} strokeWidth={1.6} />
              </a>
            )}
            {SOCIAL_LINKS.facebook && (
              <a
                href={SOCIAL_LINKS.facebook}
                aria-label="Facebook"
                target="_blank"
                rel="noopener noreferrer"
                data-testid="footer-v2-facebook"
                style={socialIcon}
              >
                <Facebook style={{ width: 16, height: 16 }} strokeWidth={1.6} />
              </a>
            )}
            {SOCIAL_LINKS.x && (
              <a
                href={SOCIAL_LINKS.x}
                aria-label="X (Twitter)"
                target="_blank"
                rel="noopener noreferrer"
                data-testid="footer-v2-x"
                style={socialIcon}
              >
                <Twitter style={{ width: 16, height: 16 }} strokeWidth={1.6} />
              </a>
            )}
            <a
              href="mailto:contact@plume-astrale.fr"
              aria-label="Email"
              data-testid="footer-v2-email-icon"
              style={socialIcon}
            >
              <Mail style={{ width: 16, height: 16 }} strokeWidth={1.6} />
            </a>
          </div>
        </div>

        <div
          style={{
            marginTop: 32,
            paddingTop: 20,
            borderTop: '1px solid rgba(244,239,230,0.08)',
            fontSize: 12,
            color: 'rgba(244,239,230,0.45)',
            textAlign: 'center',
            letterSpacing: '0.06em',
          }}
        >
          © {year} Plume Astrale · Tous droits réservés · Fait avec soin en France
        </div>
      </div>
    </footer>
  );
}

const footerLinkStyle = {
  fontSize: 13,
  color: 'rgba(244,239,230,0.72)',
  textDecoration: 'none',
  transition: 'color 200ms ease',
  fontFamily: 'Inter, sans-serif',
  letterSpacing: '0.02em',
};

const socialIcon = {
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: 34,
  height: 34,
  borderRadius: 999,
  border: '1px solid rgba(212,175,55,0.35)',
  color: 'var(--plume-gold)',
  transition: 'background 200ms ease, border-color 200ms ease',
  textDecoration: 'none',
};

function FooterLink({ to, children, testid }) {
  return (
    <Link
      to={to}
      data-testid={testid}
      style={footerLinkStyle}
      onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--plume-gold)')}
      onMouseLeave={(e) => (e.currentTarget.style.color = 'rgba(244,239,230,0.72)')}
    >
      {children}
    </Link>
  );
}
