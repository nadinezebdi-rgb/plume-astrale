/* eslint-disable react/no-unescaped-entities */
import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const CTA_PRICE = 149;

function computeDeadline(birthDateStr) {
  if (!birthDateStr) return null;
  const [_, m, d] = birthDateStr.split('-').map(Number);
  if (!m || !d) return null;
  const now = new Date();
  let target = new Date(now.getFullYear(), m - 1, d);
  if (target < now) target = new Date(now.getFullYear() + 1, m - 1, d);
  const orderBy = new Date(target.getTime() - 8 * 86400000);
  const fmt = (dt) => dt.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
  return { anniversary: fmt(target), orderBy: fmt(orderBy) };
}

export default function EditionReliee() {
  const [birthDate, setBirthDate] = useState('');
  const deadline = useMemo(() => computeDeadline(birthDate), [birthDate]);

  return (
    <PsPageShell background="dark">
      <SEO
        path="/edition-reliee"
        title="Un exemplaire au monde · Édition Reliée Plume Astrale"
        description="Le seul livre qui porte son nom. Composé, imprimé et relié à la main, en cinq jours. Vous lisez avant qu'on imprime — 149€."
      />
      <div style={{ maxWidth: 780, margin: '0 auto', padding: '80px 24px', color: '#F5EEE0', fontFamily: '"Cormorant Garamond", serif', lineHeight: 1.65 }}>

        {/* B1 · Ouverture */}
        <section data-testid="er-block-1-hero" style={{ textAlign: 'center', marginBottom: 88 }}>
          <p style={eyebrow}>UN EXEMPLAIRE AU MONDE</p>
          <h1 style={{ ...h1, marginTop: 12 }}>Le seul livre qui porte son nom.</h1>
          <p style={{ ...body, maxWidth: 620, margin: '24px auto' }}>
            À partir de sa date, son heure et son lieu de naissance, nous composons un livre de
            <b> 49 pages qui n'existe qu'en un exemplaire</b>. Relu à la main. Imprimé, cousu, numéroté.
            Chez elle en cinq jours.
          </p>
          <a href="/carte-cadeau" data-testid="er-cta-primary-top" style={ctaPrimary}>
            Composer son livre — {CTA_PRICE}&nbsp;€
          </a>
          <p style={reassure}>
            Vous lisez le texte entier avant qu'on imprime · Expédié sous 5 jours · Livré en France
          </p>
        </section>

        {/* B2 · Le problème */}
        <section data-testid="er-block-2-problem" style={{ margin: '80px 0', textAlign: 'center' }}>
          <p style={{ ...body, maxWidth: 560, margin: '0 auto', fontStyle: 'italic' }}>
            Vous cherchez depuis une heure. Vous avez vu la bougie, le coffret, le bracelet gravé.<br/>
            Tous ces cadeaux disent la même chose : <em>j'ai pensé à toi</em>.<br/>
            <b style={{ color: '#D4AF37' }}>Aucun ne dit : je te connais.</b>
          </p>
        </section>

        {/* B3 · L'objet */}
        <section data-testid="er-block-3-object" style={sectionCard}>
          <h2 style={h2}>Regardez-le avant de décider.</h2>
          <p style={body}>
            Ouvrez un exemplaire, tournez les pages. Ce n'est pas une affiche à encadrer ni un
            fichier à télécharger : c'est un livre, avec une couverture, une table des matières,
            des chapitres et un colophon.
          </p>
          <ul style={list}>
            <li><b>La couverture</b>, gravée à son prénom</li>
            <li><b>La première page</b> : sa carte du ciel, à sa minute de naissance</li>
            <li><b>Le colophon</b> : sa date, son heure, son lieu, et le numéro de son exemplaire</li>
          </ul>
          <p style={{ marginTop: 20 }}>
            <Link to="/livres" data-testid="er-link-feuilleter" style={linkGold}>Feuilleter un exemplaire →</Link>
          </p>
        </section>

        {/* B4 · Contenu */}
        <section data-testid="er-block-4-content">
          <p style={eyebrow}>CE QUE LE LIVRE CONTIENT</p>
          <h2 style={h2}>49 pages. Onze planètes. Une seule personne.</h2>
          <div style={{ display: 'grid', gap: 18, marginTop: 24 }}>
            {[
              ['Sa signature dans le ciel', 'Soleil, Lune et Ascendant : ce qu’elle poursuit, ce dont elle a besoin, ce qu’elle montre.'],
              ['Ses onze planètes', 'Un chapitre par planète, dans son signe et sa maison. Ni symboles, ni jargon : des phrases.'],
              ['Ses maisons', 'Le couple, le travail, le foyer, la transformation — où chaque domaine de sa vie s’inscrit dans son ciel.'],
              ['Sa saison en cours', 'Les cycles qu’elle traverse cette année, et ce qu’ils demandent.'],
              ['Sa carte du ciel imprimée', 'En grand format, à part, à encadrer.'],
            ].map(([title, desc]) => (
              <div key={title} style={rowItem}>
                <b style={{ color: '#E8C766' }}>{title}</b> — {desc}
              </div>
            ))}
          </div>
          <p style={{ ...body, marginTop: 24, color: '#B9B0D5' }}>
            Rien n'est pré-écrit. Il n'existe aucune version « pour les Balances ». Chaque phrase
            est composée à partir de ses données exactes, calculées avec les éphémérides
            <b> Swiss Ephemeris</b> — la même bibliothèque astronomique que celle utilisée en recherche universitaire.
          </p>
        </section>

        {/* B5 · Comment ça se passe */}
        <section data-testid="er-block-5-how" style={sectionCard}>
          <h2 style={h2}>Comment ça se passe</h2>
          <ol style={{ ...list, listStyle: 'decimal', paddingLeft: 20 }}>
            <li>
              <b>Vous donnez son ciel</b> — prénom, date, heure et lieu de naissance.
              <br/><small style={{ color: '#B9B0D5' }}>Vous n'avez pas ces informations ? Prenez la <Link to="/carte-cadeau" style={linkGold}>carte cadeau</Link> : elle les renseignera elle-même, et la surprise reste entière.</small>
            </li>
            <li>
              <b>Vous lisez avant qu'on imprime</b> — dans l'heure, vous recevez le livre entier en PDF.
              Pas un extrait : le texte complet. Vous avez 72 heures pour le lire.
            </li>
            <li>
              <b>On imprime, on relie, on expédie</b> — dès votre accord. Chez elle en cinq jours ouvrés.
            </li>
          </ol>
        </section>

        {/* B6 · Garantie */}
        <section data-testid="er-block-6-guarantee" style={{ ...sectionCard, borderColor: '#D4AF37', background: 'rgba(212,175,55,0.06)' }}>
          <p style={eyebrow}>LA GARANTIE</p>
          <h2 style={{ ...h2, color: '#E8C766' }}>Vous ne payez que si le texte vous touche.</h2>
          <p style={body}>
            Vous recevez le livre complet en PDF avant toute impression. S'il ne vous touche pas,
            un mot suffit : <b>remboursement intégral, et rien n'est imprimé</b>.
          </p>
          <p style={{ ...body, fontStyle: 'italic', color: '#E8C766' }}>
            Vous n'offrirez jamais un livre que vous n'avez pas lu.
          </p>
        </section>

        {/* B7 · Ce qui est compris */}
        <section data-testid="er-block-7-included">
          <p style={eyebrow}>CE QUI EST COMPRIS</p>
          <h2 style={h2}>L'Édition Reliée — {CTA_PRICE}&nbsp;€</h2>
          <ul style={{ ...list, marginTop: 20 }}>
            <li>Le livre imprimé, cousu, dans son coffret — numéroté et signé à la main</li>
            <li>Sa carte du ciel en grand format, à encadrer</li>
            <li>Votre dédicace, imprimée en tête d'ouvrage</li>
            <li>L'exemplaire numérique, pour vous, le jour de la commande</li>
            <li>La carte cadeau à imprimer, si vous n'avez pas ses données</li>
            <li>Relu et corrigé à la main avant impression</li>
          </ul>
          <p style={{ ...body, color: '#B9B0D5', marginTop: 20, fontSize: '0.95rem' }}>
            Édition numérique seule : <b>49 €</b>. Coffret Deux Vies (deux livres + celui de votre lien) : <b>249 €</b>.
          </p>
        </section>

        {/* B8 · Pourquoi maintenant */}
        <section data-testid="er-block-8-urgency" style={sectionCard}>
          <p style={eyebrow}>POURQUOI MAINTENANT</p>
          <label style={{ display: 'block', marginTop: 12 }}>
            <small style={{ color: '#B9B0D5', letterSpacing: 1 }}>Sa date d'anniversaire</small>
            <input type="date" value={birthDate} onChange={(e) => setBirthDate(e.target.value)}
                   data-testid="er-anniversary-input" style={input} />
          </label>
          {deadline && (
            <p style={{ ...body, marginTop: 12 }} data-testid="er-deadline-computed">
              Son anniversaire : <b>{deadline.anniversary}</b>. Pour qu'il arrive à temps,
              commandez avant <b style={{ color: '#E8C766' }}>{deadline.orderBy}</b>.
            </p>
          )}
          <p style={{ ...body, marginTop: 24 }}>
            <b>Les Cent Premières.</b> Je relis et signe chaque exemplaire à la main. Je ne peux
            pas en faire plus de cent. Les numéros <b>1 à 100 sont à 149 €</b> — ensuite, le prix
            passe à 199 €.
          </p>
          <p style={{ marginTop: 12, textAlign: 'right', fontStyle: 'italic', color: '#D4AF37' }}>— Nadine</p>
        </section>

        {/* B9 · FAQ */}
        <section data-testid="er-block-9-faq">
          <p style={eyebrow}>VOS QUESTIONS</p>
          <h2 style={h2}>Vos questions</h2>
          {[
            ['Qui écrit ces livres ?',
              'Les positions planétaires sont calculées par Swiss Ephemeris, la bibliothèque astronomique de précision. Le texte est composé par Soléna, notre voix éditoriale portée par une intelligence artificielle, à partir du vocabulaire et du cadre que nous avons écrits pour elle. Puis je le relis, ligne à ligne, et je corrige ce qui sonne faux avant impression. Une machine calcule. Une personne relit.'],
            ['Je n’ai pas son heure de naissance.',
              'Deux solutions : la carte cadeau, qu’elle complète elle-même, ou une version sans heure — le livre perd les maisons, il garde tout le reste. Dites-le-nous, nous adaptons.'],
            ['Et si elle ne croit pas à l’astrologie ?',
              'Nous ne prédisons rien et nous ne parlons pas de destin. Le ciel est traité ici comme un calendrier poétique : une manière de nommer ce qu’on traverse. Beaucoup de nos lecteurs n’y « croient » pas. Ils lisent un livre écrit pour eux.'],
            ['149 €, ce n’est pas cher pour un livre ?',
              'C’est le prix d’un livre d’art tiré à un seul exemplaire, relu à la main et fabriqué pour une personne. Et vous ne payez que si le texte vous touche.'],
            ['Combien de temps pour la livraison ?',
              'Le PDF dans l’heure. Le livre relié sous cinq jours ouvrés après votre accord.'],
          ].map(([q, a], i) => (
            <details key={i} data-testid={`er-faq-${i}`} style={faqItem}>
              <summary style={faqSummary}>{q}</summary>
              <p style={{ ...body, margin: '12px 0 0', color: '#B9B0D5' }}>{a}</p>
            </details>
          ))}
        </section>

        {/* B10 · Dernier appel */}
        <section data-testid="er-block-10-final" style={{ marginTop: 96, textAlign: 'center' }}>
          <p style={{ ...body, fontStyle: 'italic', fontSize: '1.3rem', color: '#E8C766', marginBottom: 32 }}>
            Il lui restera longtemps après que le dîner sera oublié.
          </p>
          <a href="/carte-cadeau" data-testid="er-cta-primary-bottom" style={ctaPrimary}>
            Composer son livre — {CTA_PRICE}&nbsp;€
          </a>
          <p style={reassure}>
            Vous lisez avant qu'on imprime · Paiement sécurisé Stripe · Expédié de France
          </p>
        </section>
      </div>
    </PsPageShell>
  );
}

const eyebrow = { fontFamily: '"Cinzel", serif', fontSize: '0.75rem', letterSpacing: 3, color: '#D4AF37', margin: 0 };
const h1 = { fontFamily: '"Playfair Display", serif', fontSize: 'clamp(2.2rem, 5vw, 3.4rem)', color: '#F5EEE0', margin: 0, fontWeight: 400, lineHeight: 1.15 };
const h2 = { fontFamily: '"Playfair Display", serif', fontSize: '1.9rem', color: '#F5EEE0', margin: '0 0 12px', fontWeight: 400, lineHeight: 1.25 };
const body = { fontSize: '1.08rem', color: '#F5EEE0', margin: '12px 0' };
const reassure = { color: '#B9B0D5', fontSize: '0.9rem', margin: '16px 0 0', letterSpacing: 0.3 };
const ctaPrimary = {
  display: 'inline-block', padding: '16px 36px',
  background: 'linear-gradient(135deg, #D4AF37, #E8C766)', color: '#0F1A3C',
  textDecoration: 'none', borderRadius: 4, fontFamily: '"Cinzel", serif',
  fontSize: '0.95rem', letterSpacing: 3, fontWeight: 600,
};
const sectionCard = {
  background: 'rgba(15,26,60,0.55)', border: '1px solid rgba(212,175,55,0.22)',
  borderRadius: 8, padding: '32px 28px', margin: '72px 0', backdropFilter: 'blur(8px)',
};
const list = { paddingLeft: 20, margin: '12px 0', color: '#F5EEE0', lineHeight: 1.8 };
const rowItem = { padding: '14px 0', borderBottom: '1px solid rgba(212,175,55,0.14)', color: '#F5EEE0' };
const input = { display: 'block', marginTop: 6, padding: '10px 14px', background: 'rgba(15,26,60,0.6)', border: '1px solid rgba(212,175,55,0.3)', borderRadius: 4, color: '#F5EEE0', fontSize: '1rem', fontFamily: 'inherit' };
const linkGold = { color: '#D4AF37', textDecoration: 'underline', textDecorationColor: 'rgba(212,175,55,0.4)' };
const faqItem = { padding: '18px 0', borderBottom: '1px solid rgba(212,175,55,0.16)', cursor: 'pointer' };
const faqSummary = { fontFamily: '"Cinzel", serif', fontSize: '0.95rem', letterSpacing: 1, color: '#F5EEE0', outline: 'none' };
