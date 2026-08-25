import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

/**
 * Politique de Confidentialité — obligatoire pour publication Meta App (Marketing API),
 * conformité RGPD et LCEN. Charte Nocturne Éditorial.
 *
 * Créée le 2026-02-24. Éditeur : LEARNACTIF (SIRET 87860206900022).
 * Section dédiée Meta Pixel + API Conversions car Meta scrute cette rubrique
 * lors de la revue de publication de l'application.
 */
export default function Confidentialite() {
  return (
    <PsPageShell background="light">
      <SEO
        path="/confidentialite"
        title="Politique de confidentialité · Plume Astrale"
        description="Comment Plume Astrale (LEARNACTIF) collecte, utilise et protège vos données personnelles. Conformité RGPD, cookies, Meta Pixel, droits utilisateurs."
      />
      <section className="ps-section ps-section-light" data-testid="privacy-page">
        <div className="ps-container">
          <div className="ps-narrow" style={{ marginLeft: 0 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Vos données, notre engagement</p>
            <h1 className="ps-h1" style={{ color: '#0F1A3C', marginBottom: 20 }}>
              Politique de <span className="ps-italic">confidentialité</span>
            </h1>
            <p style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 14, color: '#6C6C6C',
              marginBottom: 48,
            }}>
              Dernière mise à jour : 24 février 2026
            </p>

            <PrivacyIntro />

            <PrivacySection title="1. Responsable du traitement">
              <p>
                Les données personnelles collectées sur <strong>plume-astrale.fr</strong> sont traitées par :
              </p>
              <p style={{ marginTop: 12 }}>
                <strong>LEARNACTIF</strong><br />
                SIRET : 87860206900022<br />
                Siège social : 2 rue Yvan Gaussen, 30250 Sommières, France<br />
                Contact : <PrivacyLink href="mailto:contact@plume-astrale.fr">contact@plume-astrale.fr</PrivacyLink>
              </p>
              <p style={{ marginTop: 12 }}>
                LEARNACTIF exploite la marque <em>Plume Astrale</em> et agit en qualité de responsable de traitement au sens du <strong>Règlement (UE) 2016/679 (RGPD)</strong> et de la loi française &laquo; Informatique et Libertés &raquo; du 6 janvier 1978 modifiée.
              </p>
            </PrivacySection>

            <PrivacySection title="2. Données collectées et finalités">
              <p>Nous collectons uniquement les données strictement nécessaires aux services proposés.</p>

              <PrivacySubtitle>a. Données de compte</PrivacySubtitle>
              <ul style={ulStyle}>
                <li>Adresse email</li>
                <li>Prénom (facultatif)</li>
                <li>Mot de passe (chiffré, jamais lisible)</li>
              </ul>
              <p><em>Finalité :</em> création du compte, connexion, envoi des PDF, service après-vente. <em>Base légale :</em> exécution du contrat (art. 6.1.b RGPD).</p>

              <PrivacySubtitle>b. Données astrologiques (thème natal, lectures)</PrivacySubtitle>
              <ul style={ulStyle}>
                <li>Date, heure et ville de naissance</li>
                <li>Prénom associé à la lecture</li>
              </ul>
              <p><em>Finalité :</em> calcul du thème astral et génération du PDF personnalisé. Ces données ne sont <strong>jamais partagées</strong> avec des tiers à des fins commerciales. <em>Base légale :</em> exécution du contrat.</p>

              <PrivacySubtitle>c. Données de paiement</PrivacySubtitle>
              <ul style={ulStyle}>
                <li>Nom du titulaire de la carte (transmis à Stripe uniquement)</li>
                <li>Détails de la transaction (montant, produit, statut)</li>
              </ul>
              <p><em>Finalité :</em> traitement du paiement, comptabilité, prévention de la fraude. Les <strong>numéros de carte bancaire ne transitent jamais par nos serveurs</strong> — ils sont saisis directement dans l&apos;interface sécurisée <a href="https://stripe.com/fr" target="_blank" rel="noopener noreferrer" style={inlineLink}>Stripe</a> (certifié PCI-DSS Level 1). <em>Base légale :</em> exécution du contrat + obligation légale (comptabilité).</p>

              <PrivacySubtitle>d. Données techniques et de navigation</PrivacySubtitle>
              <ul style={ulStyle}>
                <li>Adresse IP (anonymisée pour les analytics)</li>
                <li>User-agent, type d&apos;appareil, résolution</li>
                <li>Pages consultées, durée, provenance (referrer)</li>
                <li>Identifiants de cookies publicitaires (voir §5)</li>
              </ul>
              <p><em>Finalité :</em> analytics anonymisés, optimisation de l&apos;expérience, mesure des performances publicitaires. <em>Base légale :</em> intérêt légitime + consentement pour les cookies non essentiels (art. 6.1.a et 6.1.f RGPD).</p>
            </PrivacySection>

            <PrivacySection title="3. Sous-traitants et partenaires">
              <p>Pour délivrer le service, nous faisons appel à des sous-traitants soumis à des engagements contractuels de confidentialité et de conformité RGPD.</p>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Partenaire</th>
                    <th style={thStyle}>Rôle</th>
                    <th style={thStyle}>Localisation</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={tdStyle}><strong>Stripe</strong></td>
                    <td style={tdStyle}>Traitement des paiements</td>
                    <td style={tdStyle}>Irlande / États-Unis (DPF)</td>
                  </tr>
                  <tr>
                    <td style={tdStyle}><strong>Supabase</strong></td>
                    <td style={tdStyle}>Base de données comptes utilisateurs</td>
                    <td style={tdStyle}>Union européenne</td>
                  </tr>
                  <tr>
                    <td style={tdStyle}><strong>Vercel</strong></td>
                    <td style={tdStyle}>Hébergement du frontend</td>
                    <td style={tdStyle}>Union européenne (Paris)</td>
                  </tr>
                  <tr>
                    <td style={tdStyle}><strong>Emergent</strong></td>
                    <td style={tdStyle}>Hébergement du backend et base astrologique</td>
                    <td style={tdStyle}>Union européenne</td>
                  </tr>
                  <tr>
                    <td style={tdStyle}><strong>Resend</strong></td>
                    <td style={tdStyle}>Envoi d&apos;emails transactionnels (livraison des PDF)</td>
                    <td style={tdStyle}>Union européenne</td>
                  </tr>
                  <tr>
                    <td style={tdStyle}><strong>Meta Platforms</strong></td>
                    <td style={tdStyle}>Pixel de tracking + API Conversions (voir §4)</td>
                    <td style={tdStyle}>Irlande / États-Unis (DPF)</td>
                  </tr>
                  <tr>
                    <td style={tdStyle}><strong>OpenAI</strong></td>
                    <td style={tdStyle}>Génération éditoriale des textes des lectures (voix Soléna, IA)</td>
                    <td style={tdStyle}>États-Unis (DPF)</td>
                  </tr>
                </tbody>
              </table>
              <p style={{ marginTop: 16, fontSize: 14, color: '#6C6C6C' }}>
                Les transferts hors UE reposent sur le <strong>Data Privacy Framework (DPF)</strong> approuvé par la Commission européenne le 10 juillet 2023 (décision d&apos;adéquation), ou sur des <strong>clauses contractuelles types</strong> validées par la CNIL.
              </p>
              <p style={{ marginTop: 16, fontSize: 14, color: '#3A3A3A', background: '#F7F5F0', borderLeft: '3px solid #C9A24B', padding: '14px 18px' }}>
                <strong>Transparence sur l&apos;usage de l&apos;IA</strong>&nbsp;: <em>Soléna</em>, la voix qui rédige vos lectures, est un système d&apos;intelligence artificielle propulsé par un modèle de langage tiers (OpenAI) piloté par nos prompts éditoriaux. Ce n&apos;est <strong>ni une personne réelle, ni une astrologue diplômée, ni une voyante</strong>. Les positions planétaires sont calculées par la bibliothèque <em>Swiss Ephemeris</em> — moteur astronomique open-source qui suit la <strong>norme NASA (JPL)</strong> et est utilisé en recherche universitaire. Le texte est ensuite composé par le LLM à partir de vos données de naissance. Les échanges avec Soléna dans le chat sont soumis aux <PrivacyLink external href="https://openai.com/policies/eu-privacy-policy/">conditions de confidentialité d&apos;OpenAI EU</PrivacyLink>.
              </p>
            </PrivacySection>

            <PrivacySection title="4. Meta Pixel et API Conversions (Facebook / Instagram)">
              <p>
                Plume Astrale utilise le <strong>Meta Pixel</strong> (identifiant <code style={codeStyle}>1801418127692821</code>) ainsi que l&apos;<strong>API Conversions Meta (CAPI)</strong> afin de mesurer l&apos;efficacité de ses campagnes publicitaires diffusées sur Facebook, Instagram et Messenger.
              </p>

              <PrivacySubtitle>a. Ce qui est transmis à Meta</PrivacySubtitle>
              <ul style={ulStyle}>
                <li>Événements de navigation : consultation de pages, ajout au panier, achat, inscription</li>
                <li>Adresse IP et user-agent (hashés côté serveur avant envoi)</li>
                <li>Adresse email et numéro de téléphone (hashés SHA-256 avant envoi, jamais en clair)</li>
                <li>Montant, devise et identifiant unique de la commande (event_id) pour la déduplication</li>
                <li>Cookies Meta <code style={codeStyle}>_fbp</code> et <code style={codeStyle}>_fbc</code> lorsque l&apos;utilisateur a consenti au dépôt de cookies publicitaires</li>
              </ul>

              <PrivacySubtitle>b. Ce qui n&apos;est JAMAIS transmis</PrivacySubtitle>
              <ul style={ulStyle}>
                <li>Vos données de naissance (date, heure, ville) et contenu des lectures astrologiques</li>
                <li>Vos numéros de carte bancaire (traités exclusivement par Stripe)</li>
                <li>Le contenu de vos PDF générés</li>
                <li>Vos données email et téléphone en clair (uniquement en version hashée SHA-256)</li>
              </ul>

              <PrivacySubtitle>c. Finalités</PrivacySubtitle>
              <ul style={ulStyle}>
                <li>Mesurer les conversions issues des publicités Meta (achats, inscriptions)</li>
                <li>Optimiser le ciblage publicitaire (audiences similaires, retargeting)</li>
                <li>Améliorer l&apos;attribution des ventes lorsque les cookies tiers sont bloqués (grâce à l&apos;API Conversions côté serveur)</li>
              </ul>

              <PrivacySubtitle>d. Base légale et consentement</PrivacySubtitle>
              <p>
                Le dépôt du Meta Pixel et l&apos;envoi d&apos;événements via l&apos;API Conversions liés à des données personnelles sont soumis à votre <strong>consentement préalable</strong> (art. 82 loi Informatique et Libertés). Vous pouvez le retirer à tout moment via le bandeau cookies ou depuis les paramètres de votre compte Meta&nbsp;:{' '}
                <PrivacyLink external href="https://www.facebook.com/adpreferences/">Préférences publicitaires Facebook</PrivacyLink>{' • '}
                <PrivacyLink external href="https://accountscenter.instagram.com/">Instagram Accounts Center</PrivacyLink>.
              </p>

              <PrivacySubtitle>e. Durée de conservation chez Meta</PrivacySubtitle>
              <p>
                Meta conserve les événements pendant une durée maximale de <strong>24 mois</strong>, conformément à sa <PrivacyLink external href="https://www.facebook.com/privacy/policy/">Politique de confidentialité</PrivacyLink>. Les données hashées ne sont pas rétro-résolubles côté Meta.
              </p>
            </PrivacySection>

            <PrivacySection title="5. Cookies et traceurs">
              <p>
                Le site utilise différentes catégories de cookies. Un bandeau vous permet, dès votre première visite, d&apos;<strong>accepter, refuser ou personnaliser</strong> le dépôt de chacun d&apos;eux.
              </p>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Catégorie</th>
                    <th style={thStyle}>Exemple</th>
                    <th style={thStyle}>Consentement requis</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={tdStyle}>Essentiels</td>
                    <td style={tdStyle}>Session utilisateur, panier</td>
                    <td style={tdStyle}>Non (art. 82 al. 2)</td>
                  </tr>
                  <tr>
                    <td style={tdStyle}>Mesure d&apos;audience anonyme</td>
                    <td style={tdStyle}>Statistiques agrégées</td>
                    <td style={tdStyle}>Non (exemption CNIL)</td>
                  </tr>
                  <tr>
                    <td style={tdStyle}>Publicitaires</td>
                    <td style={tdStyle}>Meta Pixel (<code style={codeStyle}>_fbp</code>, <code style={codeStyle}>_fbc</code>)</td>
                    <td style={tdStyle}>Oui</td>
                  </tr>
                </tbody>
              </table>
              <p style={{ marginTop: 16 }}>
                Vous pouvez à tout moment modifier vos préférences en cliquant sur le lien <em>&laquo; Gérer les cookies &raquo;</em> en pied de page.
              </p>
            </PrivacySection>

            <PrivacySection title="6. Durées de conservation">
              <ul style={ulStyle}>
                <li><strong>Compte utilisateur :</strong> tant que le compte est actif, puis <strong>3 ans</strong> après la dernière connexion (prospection commerciale — CNIL)</li>
                <li><strong>Données de commande :</strong> 10 ans après la transaction (obligation comptable — art. L.123-22 Code de commerce)</li>
                <li><strong>Données de facturation :</strong> 10 ans</li>
                <li><strong>PDF personnalisés générés :</strong> stockés tant que votre compte est actif, supprimés à la clôture du compte</li>
                <li><strong>Cookies publicitaires :</strong> 13 mois maximum (recommandation CNIL)</li>
                <li><strong>Logs techniques et sécurité :</strong> 12 mois</li>
              </ul>
            </PrivacySection>

            <PrivacySection title="7. Vos droits">
              <p>Conformément au RGPD (art. 15 à 22), vous disposez à tout moment des droits suivants sur vos données&nbsp;:</p>
              <ul style={ulStyle}>
                <li><strong>Droit d&apos;accès</strong> — obtenir une copie de toutes les données que nous détenons sur vous</li>
                <li><strong>Droit de rectification</strong> — corriger toute donnée inexacte ou incomplète</li>
                <li><strong>Droit à l&apos;effacement (&laquo; droit à l&apos;oubli &raquo;)</strong> — demander la suppression de votre compte et de vos données</li>
                <li><strong>Droit à la portabilité</strong> — recevoir vos données dans un format structuré (JSON)</li>
                <li><strong>Droit d&apos;opposition</strong> — refuser un traitement basé sur l&apos;intérêt légitime, notamment la prospection</li>
                <li><strong>Droit de limitation</strong> — restreindre certains traitements le temps d&apos;un examen</li>
                <li><strong>Droit de retirer votre consentement</strong> à tout moment, sans conséquence rétroactive</li>
              </ul>
              <p style={{ marginTop: 16 }}>
                Exercez ces droits à tout moment par email&nbsp;:{' '}
                <PrivacyLink href="mailto:contact@plume-astrale.fr?subject=Exercice%20de%20mes%20droits%20RGPD">contact@plume-astrale.fr</PrivacyLink>. Nous vous répondrons sous <strong>30 jours</strong>. Une preuve d&apos;identité pourra vous être demandée.
              </p>
              <p style={{ marginTop: 16 }}>
                Si notre réponse ne vous satisfait pas, vous pouvez déposer une réclamation auprès de la <strong>CNIL</strong>&nbsp;:{' '}
                <PrivacyLink external href="https://www.cnil.fr/fr/plaintes">cnil.fr/fr/plaintes</PrivacyLink> — 3, place de Fontenoy, TSA 80715, 75334 Paris Cedex 07.
              </p>
            </PrivacySection>

            <PrivacySection title="8. Sécurité">
              <p>
                Nous mettons en œuvre les mesures techniques et organisationnelles appropriées pour protéger vos données&nbsp;:
              </p>
              <ul style={ulStyle}>
                <li>Chiffrement HTTPS (TLS 1.3) sur l&apos;ensemble du site</li>
                <li>Mots de passe hashés avec bcrypt (jamais stockés en clair)</li>
                <li>Base de données chiffrée au repos (Supabase)</li>
                <li>Accès restreint aux données personnelles (authentification forte pour l&apos;équipe)</li>
                <li>Journalisation des accès et alertes en cas d&apos;anomalie</li>
                <li>Sous-traitants certifiés (ISO 27001, SOC 2, PCI-DSS)</li>
              </ul>
              <p style={{ marginTop: 16 }}>
                En cas de violation de données susceptible de créer un risque pour vos droits, nous vous en informerons dans les meilleurs délais et notifierons la CNIL sous 72 heures conformément à l&apos;art. 33 RGPD.
              </p>
            </PrivacySection>

            <PrivacySection title="9. Mineurs">
              <p>
                Plume Astrale est destinée à un public <strong>majeur (18 ans et plus)</strong>. Nous ne collectons pas sciemment de données concernant des personnes mineures. Si vous constatez qu&apos;un mineur nous a transmis des données, contactez-nous immédiatement pour suppression.
              </p>
            </PrivacySection>

            <PrivacySection title="10. Modifications">
              <p>
                La présente politique peut être mise à jour pour refléter des évolutions légales, techniques ou éditoriales. La date de dernière modification figure en haut de page. En cas de changement substantiel, nous vous en informerons par email ou via un bandeau visible sur le site.
              </p>
            </PrivacySection>

            <div style={{ marginTop: 64, paddingTop: 32, borderTop: '1px solid #E7E1D4' }}>
              <Link to="/" style={legalNavLink} data-testid="privacy-back-home">
                <ArrowLeft size={16} strokeWidth={1.5} /> Retour à l&apos;accueil
              </Link>
            </div>
          </div>
        </div>
      </section>
    </PsPageShell>
  );
}

function PrivacyIntro() {
  return (
    <div style={{
      background: '#F7F5F0',
      borderLeft: '3px solid #C9A24B',
      padding: '20px 24px',
      marginBottom: 48,
      fontFamily: 'Inter, sans-serif',
      fontSize: 15, lineHeight: 1.7, color: '#232323',
    }}>
      <p style={{ margin: 0 }}>
        Chez <strong>Plume Astrale</strong>, votre intimité astrale n&apos;est pas un produit. Cette politique explique <em>précisément</em> quelles données nous collectons, pourquoi, avec qui elles sont partagées, et comment vous gardez le contrôle. Aucune donnée de naissance n&apos;est jamais transmise à un tiers publicitaire.
      </p>
    </div>
  );
}

function PrivacySection({ title, children }) {
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

function PrivacySubtitle({ children }) {
  return (
    <h3 style={{
      fontFamily: 'Playfair Display, Georgia, serif',
      fontSize: 18, color: '#0F1A3C',
      marginTop: 20, marginBottom: 8, fontWeight: 500,
    }}>
      {children}
    </h3>
  );
}

function PrivacyLink({ href, external, children }) {
  return (
    <a href={href}
      target={external ? '_blank' : undefined}
      rel={external ? 'noopener noreferrer' : undefined}
      style={{ color: '#C9A24B', textDecoration: 'underline', textUnderlineOffset: 3, fontWeight: 500 }}>
      {children}
    </a>
  );
}

const ulStyle = { paddingLeft: 22, marginTop: 8, marginBottom: 12 };
const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
  marginTop: 16,
  fontSize: 14,
};
const thStyle = {
  textAlign: 'left',
  padding: '10px 12px',
  borderBottom: '2px solid #0F1A3C',
  fontFamily: 'Inter, sans-serif',
  fontSize: 12,
  letterSpacing: '.08em',
  textTransform: 'uppercase',
  color: '#0F1A3C',
  fontWeight: 600,
};
const tdStyle = {
  padding: '10px 12px',
  borderBottom: '1px solid #E7E1D4',
  verticalAlign: 'top',
};
const codeStyle = {
  fontFamily: 'ui-monospace, Menlo, monospace',
  fontSize: 13,
  background: '#F0EDE3',
  padding: '1px 6px',
  borderRadius: 3,
  color: '#0F1A3C',
};
const inlineLink = { color: '#C9A24B', textDecoration: 'underline', textUnderlineOffset: 3 };
const legalNavLink = {
  display: 'inline-flex', alignItems: 'center', gap: 6,
  color: '#0F1A3C', textDecoration: 'none',
  borderBottom: '1px solid transparent',
  paddingBottom: 2,
  transition: 'border-color 200ms ease',
};
