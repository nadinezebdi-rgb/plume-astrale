/* eslint-disable react/no-unescaped-entities */
import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const CTA_PRICE = 149;
const API = process.env.REACT_APP_BACKEND_URL || '';

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
  const [showForm, setShowForm] = useState(false);

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
          <button
            type="button"
            onClick={() => setShowForm(true)}
            data-testid="er-cta-primary-top"
            style={ctaPrimary}
          >
            Composer son livre — {CTA_PRICE}&nbsp;€
          </button>
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

        {/* B6.5 · Sceau fondatrice */}
        <section data-testid="er-block-6b-sceau" style={sceauWrap}>
          <div style={sceauCard}>
            <div style={sceauSeal} aria-hidden="true">
              <span style={sceauSealMark}>N</span>
              <span style={sceauSealRing}>· PLUME ASTRALE · ATELIER FRANÇAIS ·</span>
            </div>
            <p style={sceauEyebrow}>LE SCEAU DE LA FONDATRICE</p>
            <p style={sceauBody}>
              Je m'appelle <b>Nadine</b>. J'ai fondé Plume Astrale à Marseille, en 2024,
              pour écrire les livres que je cherchais et ne trouvais pas :
              des ouvrages qui prennent une vie au sérieux, et qui prennent le temps.
            </p>
            <p style={sceauBody}>
              Chaque exemplaire de l'Édition Reliée passe entre mes mains :
              je relis chaque page, je corrige ce qui sonne faux, je signe le colophon,
              je numérote le coffret. Je ne délègue rien de tout ça.
            </p>
            <div style={sceauSignatureLine}>
              <span style={sceauSignatureName}>Nadine</span>
              <span style={sceauSignatureRole}>fondatrice · relectrice · signataire</span>
            </div>
          </div>
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
          <button
            type="button"
            onClick={() => setShowForm(true)}
            data-testid="er-cta-primary-bottom"
            style={ctaPrimary}
          >
            Composer son livre — {CTA_PRICE}&nbsp;€
          </button>
          <p style={reassure}>
            Vous lisez avant qu'on imprime · Paiement sécurisé Stripe · Expédié de France
          </p>
        </section>
      </div>

      {showForm && (
        <CheckoutModal onClose={() => setShowForm(false)} />
      )}
    </PsPageShell>
  );
}

// ── Modal Checkout Édition Reliée ─────────────────────────────
function CheckoutModal({ onClose }) {
  const [form, setForm] = useState({
    purchaser_email: '',
    purchaser_first_name: '',
    recipient_first_name: '',
    birth_date: '',
    birth_time: '',
    birth_city: '',
    dedication: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const update = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!form.birth_time) {
      setError("Sans heure de naissance, la carte du ciel perd les maisons. Deux options : ouvrez la carte cadeau, ou écrivez-nous et nous adaptons.");
      return;
    }
    setSubmitting(true);
    try {
      const r = await fetch(`${API}/api/edition-reliee/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          birth_country: 'FR',
          origin_url: window.location.origin,
        }),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        setError(d.detail || 'Erreur lors de la création du paiement. Réessayez ou écrivez-nous à contact@plume-astrale.fr.');
        setSubmitting(false);
        return;
      }
      const data = await r.json();
      if (data.url) {
        window.location.href = data.url;
        return;
      }
      setError('Réponse inattendue du serveur. Écrivez-nous à contact@plume-astrale.fr.');
      setSubmitting(false);
    } catch {
      setError('Impossible de contacter le serveur. Vérifiez votre connexion.');
      setSubmitting(false);
    }
  };

  return (
    <div data-testid="er-checkout-modal" style={modalBackdrop} onClick={onClose}>
      <div style={modalCard} onClick={(e) => e.stopPropagation()}>
        <button
          type="button"
          onClick={onClose}
          aria-label="Fermer"
          data-testid="er-checkout-modal-close"
          style={modalClose}
        >
          ×
        </button>
        <p style={{ ...eyebrow, textAlign: 'center' }}>ÉDITION RELIÉE · 149 €</p>
        <h2 style={{ ...h2, textAlign: 'center', marginTop: 12, marginBottom: 8 }}>
          Composons son livre.
        </h2>
        <p style={{ ...body, textAlign: 'center', color: '#B9B0D5', margin: '0 0 24px' }}>
          Vous ne payez que si le texte la touche. Garantie 72 h.
        </p>

        <form onSubmit={submit}>
          <p style={formGroupLabel}>Votre email — le PDF y sera envoyé</p>
          <input type="email" required value={form.purchaser_email} onChange={update('purchaser_email')}
                 placeholder="vous@exemple.fr" data-testid="er-form-email" style={input}/>

          <p style={formGroupLabel}>Votre prénom</p>
          <input type="text" required value={form.purchaser_first_name} onChange={update('purchaser_first_name')}
                 placeholder="Marie" data-testid="er-form-purchaser" style={input}/>

          <div style={{ height: 22 }} />
          <p style={{ ...eyebrow, textAlign: 'left' }}>SES DONNÉES DE NAISSANCE</p>

          <p style={formGroupLabel}>Son prénom (imprimé sur la couverture)</p>
          <input type="text" required value={form.recipient_first_name} onChange={update('recipient_first_name')}
                 placeholder="Julie" data-testid="er-form-recipient" style={input}/>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 6 }}>
            <div>
              <p style={formGroupLabel}>Sa date de naissance</p>
              <input type="date" required value={form.birth_date} onChange={update('birth_date')}
                     data-testid="er-form-birth-date" style={input}/>
            </div>
            <div>
              <p style={formGroupLabel}>Son heure exacte</p>
              <input type="time" required value={form.birth_time} onChange={update('birth_time')}
                     data-testid="er-form-birth-time" style={input}/>
            </div>
          </div>

          <p style={formGroupLabel}>Sa ville de naissance</p>
          <input type="text" required value={form.birth_city} onChange={update('birth_city')}
                 placeholder="Marseille" data-testid="er-form-birth-city" style={input}/>

          <p style={formGroupLabel}>Une dédicace imprimée en tête d'ouvrage (optionnel)</p>
          <textarea rows={3} maxLength={400} value={form.dedication} onChange={update('dedication')}
                    placeholder="Pour Julie, qui prend soin de ce que d'autres oublient."
                    data-testid="er-form-dedication" style={{ ...input, resize: 'vertical', fontFamily: 'inherit' }}/>

          <p style={{ ...body, margin: '16px 0', color: '#B9B0D5', fontSize: '0.9rem', fontStyle: 'italic' }}>
            Vous n'avez pas son heure de naissance ? Prenez la{' '}
            <Link to="/carte-cadeau" style={linkGold}>carte cadeau</Link>{' '}
            à la place — elle la renseignera elle-même.
          </p>

          {error && (
            <p data-testid="er-form-error" style={{ ...body, color: '#E8916B', background: 'rgba(180,117,98,0.14)', padding: '12px 14px', borderRadius: 4, fontSize: '0.95rem', margin: '12px 0' }}>
              {error}
            </p>
          )}

          <button type="submit" disabled={submitting} data-testid="er-form-submit"
                  style={{ ...ctaPrimary, width: '100%', textAlign: 'center', padding: '18px 28px', marginTop: 16, cursor: submitting ? 'wait' : 'pointer', opacity: submitting ? 0.7 : 1 }}>
            {submitting ? 'Redirection vers Stripe…' : `Payer ${CTA_PRICE} € en toute sécurité`}
          </button>
          <p style={{ ...reassure, textAlign: 'center', marginTop: 14 }}>
            Paiement sécurisé Stripe · PDF dans l'heure · 72h pour relire avant impression
          </p>
        </form>
      </div>
    </div>
  );
}

const modalBackdrop = {
  position: 'fixed', inset: 0, background: 'rgba(6,10,26,0.88)', backdropFilter: 'blur(6px)',
  zIndex: 9999, display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
  padding: '32px 16px', overflowY: 'auto',
};
const modalCard = {
  position: 'relative', maxWidth: 560, width: '100%',
  background: 'linear-gradient(180deg, #0F1A3C 0%, #15112A 100%)',
  border: '1px solid rgba(212,175,55,0.35)', borderRadius: 10,
  padding: '40px 32px 32px', color: '#F5EEE0',
  boxShadow: '0 24px 60px -20px rgba(0,0,0,0.6)',
  fontFamily: '"Cormorant Garamond", serif',
};
const modalClose = {
  position: 'absolute', top: 12, right: 16, width: 32, height: 32,
  background: 'transparent', border: 'none', color: 'rgba(240,230,211,0.7)',
  fontSize: 28, lineHeight: 1, cursor: 'pointer', padding: 0,
};
const formGroupLabel = {
  fontFamily: '"Cinzel", serif', fontSize: '0.68rem', letterSpacing: 2,
  color: 'rgba(212,175,55,0.85)', textTransform: 'uppercase',
  margin: '18px 0 6px',
};

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

// ── Sceau fondatrice ──
const sceauWrap = { margin: '80px 0', display: 'flex', justifyContent: 'center' };
const sceauCard = {
  position: 'relative', maxWidth: 620, width: '100%',
  padding: '56px 40px 44px', textAlign: 'center',
  background: 'radial-gradient(circle at 50% 0%, rgba(212,175,55,0.10), rgba(15,26,60,0.4) 70%)',
  border: '1px solid rgba(212,175,55,0.3)', borderRadius: 8,
};
const sceauSeal = {
  position: 'absolute', top: -44, left: '50%', transform: 'translateX(-50%)',
  width: 88, height: 88, borderRadius: '50%',
  background: 'radial-gradient(circle, #1A1030 40%, #0F1A3C 100%)',
  border: '1.5px solid #D4AF37', display: 'flex', alignItems: 'center', justifyContent: 'center',
  boxShadow: '0 0 24px rgba(212,175,55,0.35), inset 0 0 12px rgba(212,175,55,0.15)',
};
const sceauSealMark = {
  fontFamily: '"Playfair Display", serif', fontStyle: 'italic',
  fontSize: 42, color: '#E8C766', fontWeight: 400, lineHeight: 1,
};
const sceauSealRing = {
  position: 'absolute', inset: 0, borderRadius: '50%',
  fontFamily: '"Cinzel", serif', fontSize: 6, letterSpacing: 1.5, color: 'rgba(232,199,102,0.35)',
  display: 'none', // décoratif potentiel — masqué par défaut
};
const sceauEyebrow = { fontFamily: '"Cinzel", serif', fontSize: '0.7rem', letterSpacing: 3, color: '#D4AF37', margin: '18px 0 20px' };
const sceauBody = { fontSize: '1.02rem', color: '#F5EEE0', margin: '14px 0', lineHeight: 1.65 };
const sceauSignatureLine = { marginTop: 28, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 };
const sceauSignatureName = {
  fontFamily: '"Playfair Display", serif', fontStyle: 'italic',
  fontSize: '2.1rem', color: '#E8C766', lineHeight: 1,
};
const sceauSignatureRole = {
  fontFamily: '"Cinzel", serif', fontSize: '0.65rem', letterSpacing: 2.5,
  color: 'rgba(232,199,102,0.6)', textTransform: 'uppercase',
};
