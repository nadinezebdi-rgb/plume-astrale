import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';

/**
 * Mentions Légales — obligatoires en France (LCEN 2004).
 * Contenu à personnaliser par l'éditeur (email, adresse, hébergeur exact).
 */
export default function MentionsLegales() {
  useEffect(() => {
    document.title = 'Mentions légales · Plume Astrale';
    const meta = document.querySelector('meta[name="description"]');
    if (meta) meta.setAttribute('content', "Mentions légales et informations éditeur de Plume Astrale — astrologie personnalisée par Soléna.");
    // Empêche l'indexation profonde de cette page (mais elle reste crawlable pour E-A-T)
    let robots = document.querySelector('meta[name="robots"]');
    if (!robots) {
      robots = document.createElement('meta');
      robots.setAttribute('name', 'robots');
      document.head.appendChild(robots);
    }
    robots.setAttribute('content', 'index, follow');
    return () => { robots.setAttribute('content', 'index, follow'); };
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a1a', color: '#F5EEE0', padding: '80px 24px 120px' }}>
      <div style={{ maxWidth: 760, margin: '0 auto', lineHeight: 1.75 }}>
        <h1 style={{ fontFamily: '"Cormorant Garamond", serif', fontSize: 48, fontWeight: 500, color: '#E8C766', marginBottom: 40 }}>
          Mentions légales
        </h1>

        <Section title="Éditeur du site">
          <p><strong>Plume Astrale</strong><br/>
          Site édité par : <em>[à compléter : raison sociale, forme juridique]</em><br/>
          SIRET : <em>[à compléter]</em><br/>
          Capital social : <em>[le cas échéant]</em><br/>
          Adresse du siège : <em>[à compléter]</em><br/>
          Email : <a href="mailto:contact@plume-astrale.fr" style={{ color: '#E8C766' }}>contact@plume-astrale.fr</a><br/>
          Directrice de la publication : <em>Soléna [nom complet]</em></p>
        </Section>

        <Section title="Hébergement">
          <p>Le site est hébergé par <strong>Emergent</strong> (infrastructure cloud managée).<br/>
          Support technique : via l&rsquo;interface Emergent.</p>
        </Section>

        <Section title="Propriété intellectuelle">
          <p>L&rsquo;ensemble du contenu de ce site (textes, illustrations, PDFs générés, voix Soléna, visuels des arcanes, code source visible et invisible) est protégé par les droits d&rsquo;auteur français et internationaux. Toute reproduction, représentation, modification ou exploitation, totale ou partielle, sans autorisation écrite préalable est interdite et pourra donner lieu à des poursuites (art. L.122-4 du Code de la propriété intellectuelle).</p>
        </Section>

        <Section title="Données personnelles (RGPD)">
          <p>Les données que tu confies (prénom, email, date et lieu de naissance, échanges avec Soléna) servent uniquement à générer tes lectures personnalisées et à te contacter au sujet de tes commandes. Elles ne sont jamais revendues.</p>
          <p><strong>Tes droits :</strong> accès, rectification, effacement, portabilité, opposition. Écris à <a href="mailto:contact@plume-astrale.fr" style={{ color: '#E8C766' }}>contact@plume-astrale.fr</a> — réponse sous 30 jours.<br/>
          <strong>Autorité :</strong> tu peux aussi saisir la CNIL sur <a href="https://cnil.fr" style={{ color: '#E8C766' }} rel="noopener">cnil.fr</a>.</p>
        </Section>

        <Section title="Cookies">
          <p>Nous utilisons des cookies techniques (session de connexion, panier) et des cookies de mesure d&rsquo;audience anonymes. Aucun cookie publicitaire. Tu peux les désactiver depuis ton navigateur.</p>
        </Section>

        <Section title="Contact">
          <p>Pour toute question, réclamation ou demande RGPD :<br/>
          <a href="mailto:contact@plume-astrale.fr" style={{ color: '#E8C766' }}>contact@plume-astrale.fr</a></p>
        </Section>

        <div style={{ marginTop: 60, borderTop: '1px solid rgba(232,199,102,0.2)', paddingTop: 20, fontSize: 13, color: 'rgba(232,230,240,0.5)' }}>
          <Link to="/" style={{ color: '#E8C766' }}>← Retour à l&rsquo;accueil</Link> · <Link to="/cgv" style={{ color: '#E8C766' }}>Conditions générales de vente</Link>
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <section style={{ marginBottom: 40 }}>
      <h2 style={{ fontSize: 18, letterSpacing: '.14em', textTransform: 'uppercase', color: '#E8C766', marginBottom: 12, fontWeight: 600 }}>{title}</h2>
      <div style={{ fontSize: 15, color: 'rgba(232,230,240,0.85)' }}>{children}</div>
    </section>
  );
}
