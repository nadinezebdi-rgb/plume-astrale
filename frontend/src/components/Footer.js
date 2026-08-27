import React from 'react';
import { Link, useLocation } from 'react-router-dom';

/**
 * Footer global — présent sur toutes les pages sauf /admin et /dashboard.
 * Contient les liens légaux obligatoires (mentions, CGV) + navigation secondaire.
 * Style discret (navy sombre, texte muted) pour ne pas concurrencer les CTAs.
 */
export default function Footer() {
  const { pathname } = useLocation();
  // Ne pas afficher sur les pages admin / dashboard / process de commande
  // Ne pas afficher sur / non plus — la Homepage v3 embarque son propre FooterV2
  if (
    pathname === '/' ||
    pathname === '/experience' ||
    pathname.startsWith('/experience/') ||
    pathname === '/home-experience-v3' ||
    pathname.startsWith('/home-experience-v3/') ||
    pathname.startsWith('/admin') ||
    pathname.startsWith('/dashboard') ||
    pathname.startsWith('/formulaire') ||
    pathname.startsWith('/resultats') ||
    pathname.startsWith('/paiement')
  ) {
    return null;
  }

  const year = new Date().getFullYear();

  return (
    <footer
      data-testid="global-footer"
      style={{
        marginTop: 40,
        padding: '48px 24px 32px',
        background: '#0a0a1a',
        borderTop: '1px solid rgba(232,199,102,0.12)',
        color: 'rgba(232,230,240,0.55)',
        fontSize: 13,
        lineHeight: 1.7,
      }}
    >
      <div
        style={{
          maxWidth: 1180,
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 32,
        }}
      >
        {/* Colonne 1 · Marque */}
        <div>
          <div
            style={{
              fontFamily: '"Cormorant Garamond", serif',
              fontSize: 22,
              color: '#E8C766',
              marginBottom: 12,
              letterSpacing: '.05em',
            }}
          >
            Plume Astrale
          </div>
          <p style={{ margin: 0, fontSize: 12 }}>
            L&rsquo;astrologie qui sait ton prénom.<br/>
            Signature éditoriale Plume Astrale.
          </p>
        </div>

        {/* Colonne 2 · Explorer */}
        <div>
          <FooterHeading>Explorer</FooterHeading>
          <FooterLink to="/blog">Blog</FooterLink>
          <FooterLink to="/premium">Lecture Complète 97€</FooterLink>
          <FooterLink to="/bibliotheque">Bibliothèque</FooterLink>
          <FooterLink to="/services/tarot">Tarot</FooterLink>
          <FooterLink to="/quotidien">Horoscope du jour</FooterLink>
        </div>

        {/* Colonne 3 · Aide */}
        <div>
          <FooterHeading>Aide</FooterHeading>
          <FooterLink to="/inscription">Créer un compte · 20 crédits</FooterLink>
          <FooterLink to="/connexion">Se connecter</FooterLink>
          <FooterLink to="/mon-accueil">Mon espace</FooterLink>
          <a
            href="mailto:contact@plume-astrale.fr"
            style={footerLinkStyle}
          >
            contact@plume-astrale.fr
          </a>
        </div>

        {/* Colonne 4 · Légal */}
        <div>
          <FooterHeading>Légal</FooterHeading>
          <FooterLink to="/mentions-legales" testid="footer-mentions-link">
            Mentions légales
          </FooterLink>
          <FooterLink to="/cgv" testid="footer-cgv-link">
            Conditions générales de vente
          </FooterLink>
          <div style={{ fontSize: 11, color: 'rgba(232,230,240,0.35)', marginTop: 10 }}>
            RGPD · CNIL · Stripe PCI-DSS
          </div>
        </div>
      </div>

      <div
        style={{
          maxWidth: 1180,
          margin: '32px auto 0',
          paddingTop: 20,
          borderTop: '1px solid rgba(232,199,102,0.08)',
          textAlign: 'center',
          fontSize: 11,
          color: 'rgba(232,230,240,0.35)',
          letterSpacing: '.08em',
        }}
      >
        © {year} Plume Astrale · Tous droits réservés · Fait avec ✦ en France
      </div>
    </footer>
  );
}

const footerLinkStyle = {
  display: 'block',
  padding: '4px 0',
  fontSize: 12,
  color: 'rgba(232,230,240,0.65)',
  textDecoration: 'none',
  transition: 'color .2s',
};

function FooterHeading({ children }) {
  return (
    <div
      style={{
        fontSize: 11,
        letterSpacing: '.16em',
        textTransform: 'uppercase',
        color: 'rgba(232,199,102,0.9)',
        fontWeight: 600,
        marginBottom: 12,
      }}
    >
      {children}
    </div>
  );
}

function FooterLink({ to, children, testid }) {
  return (
    <Link
      to={to}
      data-testid={testid}
      style={footerLinkStyle}
      onMouseEnter={(e) => (e.currentTarget.style.color = '#E8C766')}
      onMouseLeave={(e) => (e.currentTarget.style.color = 'rgba(232,230,240,0.65)')}
    >
      {children}
    </Link>
  );
}
