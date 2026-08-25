import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

/**
 * Mentions Légales — obligatoires en France (LCEN 2004). Charte v3 (light).
 * SEO P1 (2026-02-16) : noindex, follow via <SEO> component.
 */
export default function MentionsLegales() {
  return (
    <PsPageShell background="light">
      <SEO path="/mentions-legales" />
      <section className="ps-section ps-section-light" data-testid="mentions-page">
        <div className="ps-container">
          <div className="ps-narrow" style={{ marginLeft: 0 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Informations éditeur</p>
            <h1 className="ps-h1" style={{ color: '#0F1A3C', marginBottom: 48 }}>
              Mentions <span className="ps-italic">légales</span>
            </h1>

            <LegalSection title="Éditeur du site">
              <p><strong>Plume Astrale</strong><br />
              Site édité par : <strong>LEARNACTIF</strong><br />
              SIRET : 87860206900022<br />
              Siège social : 2 rue Yvan Gaussen, 30250 Sommières, France<br />
              Email : <LegalLink href="mailto:contact@plume-astrale.fr">contact@plume-astrale.fr</LegalLink><br />
              Directrice de la publication : <em>Soléna</em></p>
            </LegalSection>

            <LegalSection title="Hébergement">
              <p>Le site est hébergé par <strong>Emergent</strong> (infrastructure cloud managée). Support technique : via l&apos;interface Emergent.</p>
            </LegalSection>

            <LegalSection title="Propriété intellectuelle">
              <p>L&apos;ensemble du contenu de ce site (textes, illustrations, PDFs générés, voix Soléna, visuels des arcanes, code source visible et invisible) est protégé par les droits d&apos;auteur français et internationaux. Toute reproduction, représentation, modification ou exploitation, totale ou partielle, sans autorisation écrite préalable est interdite et pourra donner lieu à des poursuites (art. L.122-4 du Code de la propriété intellectuelle).</p>
            </LegalSection>

            <LegalSection title="Données personnelles (RGPD)">
              <p>Les données que tu confies (prénom, email, date et lieu de naissance, échanges avec Soléna) servent uniquement à générer tes lectures personnalisées et à te contacter au sujet de tes commandes. Elles ne sont jamais revendues.</p>
              <p><strong>Tes droits :</strong> accès, rectification, effacement, portabilité, opposition. Écris à <LegalLink href="mailto:contact@plume-astrale.fr">contact@plume-astrale.fr</LegalLink> — réponse sous 30 jours.<br />
              <strong>Autorité :</strong> tu peux aussi saisir la CNIL sur <LegalLink href="https://cnil.fr" external>cnil.fr</LegalLink>.</p>
            </LegalSection>

            <LegalSection title="Cookies">
              <p>Nous utilisons trois catégories de cookies&nbsp;: (i) des cookies <strong>techniques essentiels</strong> (session de connexion, panier, sécurité), (ii) des cookies de <strong>mesure d&apos;audience anonymisée</strong>, et (iii) des cookies <strong>publicitaires</strong> déposés par le Meta Pixel (Facebook / Instagram) uniquement <strong>après votre consentement explicite</strong>. Vous pouvez modifier vos préférences à tout moment via le bouton <em>&laquo; Gérer les cookies &raquo;</em> en pied de page. Détails complets dans notre <LegalLink href="/confidentialite">Politique de confidentialité</LegalLink>.</p>
            </LegalSection>

            <LegalSection title="Contact">
              <p>Pour toute question, réclamation ou demande RGPD :<br />
              <LegalLink href="mailto:contact@plume-astrale.fr">contact@plume-astrale.fr</LegalLink></p>
            </LegalSection>

            <div style={{
              marginTop: 64, paddingTop: 24,
              borderTop: '1px solid #E3E1DC',
              display: 'flex', flexWrap: 'wrap', gap: 24,
              fontFamily: 'Inter, sans-serif', fontSize: 14,
            }}>
              <Link to="/" style={legalNavLink} data-testid="mentions-back-home">
                <ArrowLeft style={{ width: 14, height: 14 }} strokeWidth={2} />
                Retour à l&apos;accueil
              </Link>
              <Link to="/cgv" style={legalNavLink} data-testid="mentions-to-cgv">
                Conditions générales de vente
              </Link>
            </div>
          </div>
        </div>
      </section>
    </PsPageShell>
  );
}

function LegalSection({ title, children }) {
  return (
    <section style={{ marginBottom: 40 }}>
      <h2 style={{
        fontFamily: 'Inter, sans-serif',
        fontSize: 12, letterSpacing: '.18em',
        textTransform: 'uppercase', color: '#C9A24B',
        marginBottom: 14, fontWeight: 600,
      }}>
        {title}
      </h2>
      <div style={{
        fontFamily: 'Inter, sans-serif',
        fontSize: 16, lineHeight: 1.7, color: '#232323',
      }}>
        {children}
      </div>
    </section>
  );
}

function LegalLink({ href, external, children }) {
  return (
    <a href={href}
      target={external ? '_blank' : undefined}
      rel={external ? 'noopener noreferrer' : undefined}
      style={{ color: '#C9A24B', textDecoration: 'underline', textUnderlineOffset: 3, fontWeight: 500 }}>
      {children}
    </a>
  );
}

const legalNavLink = {
  display: 'inline-flex', alignItems: 'center', gap: 6,
  color: '#0F1A3C', textDecoration: 'none',
  borderBottom: '1px solid transparent',
  paddingBottom: 2,
  transition: 'border-color 200ms ease',
};
