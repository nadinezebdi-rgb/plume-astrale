import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';

/**
 * Conditions Générales de Vente — obligatoires pour un e-commerce FR.
 * À faire relire par un juriste avant mise en production stricte.
 */
export default function CGV() {
  useEffect(() => {
    document.title = 'Conditions générales de vente · Plume Astrale';
    const meta = document.querySelector('meta[name="description"]');
    if (meta) meta.setAttribute('content', "Conditions générales de vente Plume Astrale — droit de rétractation, livraison, garanties.");
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a1a', color: '#F5EEE0', padding: '80px 24px 120px' }}>
      <div style={{ maxWidth: 760, margin: '0 auto', lineHeight: 1.75 }}>
        <h1 style={{ fontFamily: '"Cormorant Garamond", serif', fontSize: 48, fontWeight: 500, color: '#E8C766', marginBottom: 16 }}>
          Conditions Générales de Vente
        </h1>
        <p style={{ fontSize: 13, color: 'rgba(232,230,240,0.5)', marginBottom: 40 }}>
          Applicables au 4 août 2026 · Version 1.0
        </p>

        <Section title="1. Objet">
          <p>Les présentes CGV régissent la vente sur <strong>plume-astrale.fr</strong> de lectures astrologiques personnalisées (Karma, Numérologie, Kabbale, Médiumnité, Croix Celtique, Lecture Complète, Thème Natal, Consultation avec Soléna) sous forme de fichiers PDF numériques et de crédits de conversation.</p>
        </Section>

        <Section title="2. Prix et paiement">
          <p>Les prix sont indiqués en euros TTC. Le paiement s&rsquo;effectue par carte bancaire via <strong>Stripe</strong> (paiement sécurisé, PCI-DSS niveau 1). Aucune donnée bancaire n&rsquo;est stockée sur nos serveurs.</p>
          <ul>
            <li>Karma &amp; Destin — 29 €</li>
            <li>Numérologie sacrée — 29 €</li>
            <li>Kabbale · Arbre de Vie — 39 €</li>
            <li>Pack Karmique (Karma + Kabbale) — 89 €</li>
            <li>Lecture Complète (5 PDFs) — 97 €</li>
            <li>Crédits de conversation avec Soléna — à partir de 5 €</li>
          </ul>
        </Section>

        <Section title="3. Livraison">
          <p>Les fichiers PDF sont livrés instantanément par email après validation du paiement (5 minutes maximum). Les crédits sont crédités sur ton compte dans la seconde qui suit le paiement.</p>
          <p>Si tu ne reçois pas ton PDF après 10 minutes, vérifie tes spams, puis écris-nous : <a href="mailto:contact@plume-astrale.fr" style={{ color: '#E8C766' }}>contact@plume-astrale.fr</a>.</p>
        </Section>

        <Section title="4. Droit de rétractation">
          <p><strong>Contenu numérique</strong> : conformément à l&rsquo;article L221-28 13° du Code de la consommation, le droit de rétractation ne s&rsquo;applique pas aux fichiers numériques téléchargés et à leur exécution après acceptation expresse du client. En validant ton paiement, tu acceptes le début immédiat de la génération et renonces au délai de 14 jours.</p>
          <p><strong>Exception commerciale Plume Astrale</strong> : si la lecture reçue ne te correspond manifestement pas (erreur de calcul, contenu manquant), écris-nous dans les 7 jours — nous étudions chaque cas et remboursons intégralement si l&rsquo;erreur est de notre fait.</p>
        </Section>

        <Section title="5. Garantie de conformité">
          <p>Chaque lecture est générée sur la base des informations que tu fournis (prénom, date, heure, lieu). Vérifie leur exactitude avant validation — nous ne pouvons pas régénérer une lecture pour cause d&rsquo;erreur de saisie client.</p>
        </Section>

        <Section title="6. Propriété intellectuelle des lectures">
          <p>Ta lecture t&rsquo;est destinée à titre personnel. Tu ne peux pas la revendre, la diffuser en ligne, ni l&rsquo;utiliser à des fins commerciales sans notre accord écrit.</p>
        </Section>

        <Section title="7. Responsabilité">
          <p>Plume Astrale propose un contenu <strong>de développement personnel et spirituel</strong>. Nos lectures ne remplacent en aucun cas un avis médical, psychologique, juridique ou financier. En cas de difficulté grave, consulte un professionnel qualifié.</p>
        </Section>

        <Section title="8. Litiges & médiation">
          <p>En cas de litige, la loi française s&rsquo;applique. Avant toute action judiciaire, tu peux saisir gratuitement un médiateur de la consommation (Article L612-1 du Code de la consommation). Tribunal compétent : <em>[à compléter selon siège social]</em>.</p>
        </Section>

        <div style={{ marginTop: 60, borderTop: '1px solid rgba(232,199,102,0.2)', paddingTop: 20, fontSize: 13, color: 'rgba(232,230,240,0.5)' }}>
          <Link to="/" style={{ color: '#E8C766' }}>← Retour à l&rsquo;accueil</Link> · <Link to="/mentions-legales" style={{ color: '#E8C766' }}>Mentions légales</Link>
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <section style={{ marginBottom: 34 }}>
      <h2 style={{ fontSize: 17, letterSpacing: '.12em', textTransform: 'uppercase', color: '#E8C766', marginBottom: 10, fontWeight: 600 }}>{title}</h2>
      <div style={{ fontSize: 15, color: 'rgba(232,230,240,0.85)' }}>{children}</div>
    </section>
  );
}
