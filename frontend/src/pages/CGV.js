import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

/**
 * Conditions Générales de Vente — obligatoires pour un e-commerce FR. Charte v3.
 * SEO P1 (2026-02-16) : noindex, follow via <SEO>.
 */
export default function CGV() {
  return (
    <PsPageShell background="light">
      <SEO path="/cgv" />
      <section className="ps-section ps-section-light" data-testid="cgv-page">
        <div className="ps-container">
          <div className="ps-narrow" style={{ marginLeft: 0 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Cadre commercial</p>
            <h1 className="ps-h1" style={{ color: '#0F1A3C', marginBottom: 12 }}>
              Conditions <span className="ps-italic">Générales de Vente</span>
            </h1>
            <p className="ps-caption" style={{ marginBottom: 48 }}>
              Applicables au 4 août 2026 · Version 1.0
            </p>

            <LegalSection title="1. Objet">
              <p>Les présentes CGV régissent la vente sur <strong>plume-astrale.fr</strong> de lectures astrologiques personnalisées (Karma, Numérologie, Kabbale, Médiumnité, Croix Celtique, Lecture Complète, Thème Natal, Consultation avec Soléna) sous forme de fichiers PDF numériques et de crédits de conversation.</p>
            </LegalSection>

            <LegalSection title="2. Prix et paiement">
              <p>Les prix sont indiqués en euros TTC. Le paiement s&apos;effectue par carte bancaire via <strong>Stripe</strong> (paiement sécurisé, PCI-DSS niveau 1). Aucune donnée bancaire n&apos;est stockée sur nos serveurs.</p>
              <ul style={{ paddingLeft: 20, marginTop: 12 }}>
                <li>Karma &amp; Destin — 29 €</li>
                <li>Numérologie sacrée — 29 €</li>
                <li>Kabbale · Arbre de Vie — 39 €</li>
                <li>Pack Karmique (Karma + Kabbale) — 89 €</li>
                <li>Lecture Complète (5 PDFs) — 97 €</li>
                <li>Crédits de conversation avec Soléna — à partir de 5 €</li>
              </ul>
            </LegalSection>

            <LegalSection title="3. Livraison">
              <p>Les fichiers PDF sont livrés instantanément par email après validation du paiement (5 minutes maximum). Les crédits sont crédités sur ton compte dans la seconde qui suit le paiement.</p>
              <p>Si tu ne reçois pas ton PDF après 10 minutes, vérifie tes spams, puis écris-nous : <LegalLink href="mailto:contact@plume-astrale.fr">contact@plume-astrale.fr</LegalLink>.</p>
            </LegalSection>

            <LegalSection title="4. Droit de rétractation">
              <p><strong>Contenu numérique</strong> : conformément à l&apos;article L221-28 13° du Code de la consommation, le droit de rétractation ne s&apos;applique pas aux fichiers numériques téléchargés et à leur exécution après acceptation expresse du client. En validant ton paiement, tu acceptes le début immédiat de la génération et renonces au délai de 14 jours.</p>
              <p><strong>Exception commerciale Plume Astrale</strong> : si la lecture reçue ne te correspond manifestement pas (erreur de calcul, contenu manquant), écris-nous dans les 7 jours — nous étudions chaque cas et remboursons intégralement si l&apos;erreur est de notre fait.</p>
            </LegalSection>

            <LegalSection title="5. Garantie de conformité">
              <p>Chaque lecture est générée sur la base des informations que tu fournis (prénom, date, heure, lieu). Vérifie leur exactitude avant validation — nous ne pouvons pas régénérer une lecture pour cause d&apos;erreur de saisie client.</p>
            </LegalSection>

            <LegalSection title="6. Propriété intellectuelle des lectures">
              <p>Ta lecture t&apos;est destinée à titre personnel. Tu ne peux pas la revendre, la diffuser en ligne, ni l&apos;utiliser à des fins commerciales sans notre accord écrit.</p>
            </LegalSection>

            <LegalSection title="7. Responsabilité">
              <p>Plume Astrale propose un contenu <strong>de développement personnel et spirituel</strong>. Nos lectures ne remplacent en aucun cas un avis médical, psychologique, juridique ou financier. En cas de difficulté grave, consulte un professionnel qualifié.</p>
            </LegalSection>

            <LegalSection title="8. Litiges & médiation">
              <p>En cas de litige, la loi française s&apos;applique. Avant toute action judiciaire, tu peux saisir gratuitement un médiateur de la consommation (Article L612-1 du Code de la consommation). Tribunal compétent : <em>[à compléter selon siège social]</em>.</p>
            </LegalSection>

            <div style={{
              marginTop: 64, paddingTop: 24,
              borderTop: '1px solid #E3E1DC',
              display: 'flex', flexWrap: 'wrap', gap: 24,
              fontFamily: 'Inter, sans-serif', fontSize: 14,
            }}>
              <Link to="/" style={legalNavLink} data-testid="cgv-back-home">
                <ArrowLeft style={{ width: 14, height: 14 }} strokeWidth={2} />
                Retour à l&apos;accueil
              </Link>
              <Link to="/mentions-legales" style={legalNavLink} data-testid="cgv-to-mentions">
                Mentions légales
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

function LegalLink({ href, children }) {
  return (
    <a href={href}
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
};
