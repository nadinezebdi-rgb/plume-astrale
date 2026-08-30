/* eslint-disable react/no-unescaped-entities */
/**
 * ComposerPage.jsx — L'Atelier · Wizard 4 étapes /composer (2026-03 pivot)
 *
 * Le seul tunnel de commande du livre Plume Astrale.
 * 1. Données de naissance (heure optionnelle → active L'Heure Retrouvée)
 * 2. Choix des chapitres avec pricing live (+29 / +19 / plafond 99)
 * 3. Choix de l'édition (Numérique 24 · Brochée 69 · Reliée 119)
 * 4. Récap + destinataire optionnel (Broché/Reliée) + redirect Stripe
 *
 * Le prix est TOUJOURS recalculé côté serveur — le front affiche `total_eur`
 * retourné par /api/composer/quote (source de vérité).
 */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL || '';
const STEPS = ['Vos données', 'Vos chapitres', 'Votre édition', 'Récapitulatif'];

export default function ComposerPage() {
  const [step, setStep] = useState(0);
  const [catalog, setCatalog] = useState(null);
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [catalogError, setCatalogError] = useState(null);

  // ── State partagé ───────────────────────────────────────────
  const [birth, setBirth] = useState({
    email: '',
    first_name: '',
    birth_date: '',
    birth_time: '',
    birth_city: '',
    birth_country: 'FR',
  });
  const [selectedChapters, setSelectedChapters] = useState([]);
  const [edition, setEdition] = useState('numerique');
  const [recipient, setRecipient] = useState({ recipient_first_name: '', dedication: '' });
  const [promo, setPromo] = useState({ code: '', applied: false, message: null, total_eur: 0, original_total_eur: 0 });

  const noBirthTime = !birth.birth_time;

  // ── Catalogue ───────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoadingCatalog(true);
    fetch(`${API}/api/composer/chapters?no_birth_time=${noBirthTime}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r)))
      .then((data) => { if (!cancelled) setCatalog(data); })
      .catch(() => { if (!cancelled) setCatalogError('Impossible de charger le catalogue. Rechargez la page.'); })
      .finally(() => { if (!cancelled) setLoadingCatalog(false); });
    return () => { cancelled = true; };
  }, [noBirthTime]);

  // Si l'utilisateur change son heure et que le chapitre "heure_retrouvee"
  // était sélectionné, on le retire proprement.
  useEffect(() => {
    if (!noBirthTime && selectedChapters.includes('heure_retrouvee')) {
      setSelectedChapters((cs) => cs.filter((s) => s !== 'heure_retrouvee'));
    }
  }, [noBirthTime, selectedChapters]);

  // ── Quote live ──────────────────────────────────────────────
  const [quote, setQuote] = useState(null);
  const [quoting, setQuoting] = useState(false);

  const refreshQuote = useCallback(async () => {
    setQuoting(true);
    try {
      const r = await fetch(`${API}/api/composer/quote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          edition,
          chapter_slugs: selectedChapters,
          no_birth_time: noBirthTime,
        }),
      });
      if (r.ok) setQuote(await r.json());
    } finally {
      setQuoting(false);
    }
  }, [edition, selectedChapters, noBirthTime]);

  useEffect(() => { refreshQuote(); }, [refreshQuote]);

  // ── Application code promo ───────────────────────────────────
  const applyPromo = useCallback(async () => {
    if (!promo.code) return;
    try {
      const r = await fetch(`${API}/api/composer/apply-promo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: promo.code,
          edition,
          chapter_slugs: selectedChapters,
          no_birth_time: noBirthTime,
        }),
      });
      const d = await r.json();
      if (!r.ok || !d.valid) {
        setPromo((p) => ({ ...p, applied: false, message: 'Code invalide ou expiré.' }));
        return;
      }
      setPromo({
        code: d.code,
        applied: true,
        total_eur: d.total_eur,
        original_total_eur: d.original_total_eur,
        message: `Code «\u00A0${d.label}\u00A0» appliqué — ${d.discount_pct}% de réduction.`,
      });
    } catch {
      setPromo((p) => ({ ...p, applied: false, message: 'Erreur réseau. Réessayez.' }));
    }
  }, [promo.code, edition, selectedChapters, noBirthTime]);

  // Reset promo si l'utilisateur change édition/chapitres après application
  useEffect(() => {
    if (promo.applied) setPromo((p) => ({ ...p, applied: false, message: null }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [edition, selectedChapters]);

  // ── Navigation ──────────────────────────────────────────────
  const canGoNext = useMemo(() => {
    if (step === 0) {
      return (
        birth.email.includes('@') &&
        birth.first_name.trim().length > 0 &&
        /^\d{4}-\d{2}-\d{2}$/.test(birth.birth_date) &&
        birth.birth_city.trim().length > 1
      );
    }
    return true;
  }, [step, birth]);

  const goNext = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const goPrev = () => setStep((s) => Math.max(s - 1, 0));

  // ── Checkout ────────────────────────────────────────────────
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const submit = async () => {
    setSubmitError(null);
    setSubmitting(true);
    try {
      const payload = {
        edition,
        chapter_slugs: selectedChapters,
        email: birth.email.trim().toLowerCase(),
        first_name: birth.first_name.trim(),
        birth_date: birth.birth_date,
        birth_time: birth.birth_time || null,
        birth_city: birth.birth_city.trim(),
        birth_country: birth.birth_country || 'FR',
        origin_url: window.location.origin,
      };
      if (promo.applied && promo.code) {
        payload.promo_code = promo.code;
      }
      if (edition !== 'numerique') {
        if (recipient.recipient_first_name.trim()) {
          payload.recipient_first_name = recipient.recipient_first_name.trim();
        }
        if (recipient.dedication.trim()) {
          payload.dedication = recipient.dedication.trim();
        }
      }
      const r = await fetch(`${API}/api/composer/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        setSubmitError(d.detail || 'Erreur lors de la création du paiement.');
        setSubmitting(false);
        return;
      }
      const data = await r.json();
      if (data.url) { window.location.href = data.url; return; }
      setSubmitError('Réponse inattendue du serveur.');
      setSubmitting(false);
    } catch {
      setSubmitError('Impossible de contacter le serveur.');
      setSubmitting(false);
    }
  };

  return (
    <PsPageShell background="dark">
      <SEO
        path="/composer"
        title="L'Atelier · Composer votre livre Plume Astrale"
        description="Composez votre livre à partir de votre ciel de naissance. Six chapitres au choix, trois éditions. Le seul livre écrit pour vous."
        noindex={false}
      />
      <div data-testid="composer-page" style={pageWrap}>

        {/* Header stepper */}
        <header style={headerStyle}>
          <p style={eyebrow}>L'ATELIER · COMPOSEZ VOTRE LIVRE</p>
          <h1 style={h1Style}>Un livre. Écrit pour vous.</h1>
          <Stepper current={step} steps={STEPS} onGoTo={(i) => i < step && setStep(i)} />
        </header>

        {/* Corps des étapes */}
        <main style={mainCard}>
          {step === 0 && (
            <StepBirthData
              birth={birth}
              setBirth={setBirth}
            />
          )}
          {step === 1 && (
            <StepChapters
              catalog={catalog}
              loading={loadingCatalog}
              error={catalogError}
              selected={selectedChapters}
              onToggle={(slug) =>
                setSelectedChapters((cs) =>
                  cs.includes(slug) ? cs.filter((s) => s !== slug) : [...cs, slug]
                )
              }
              onApplyFormula={(addons) => setSelectedChapters(addons)}
              quote={quote}
              noBirthTime={noBirthTime}
            />
          )}
          {step === 2 && (
            <StepEdition
              catalog={catalog}
              edition={edition}
              setEdition={setEdition}
              quote={quote}
            />
          )}
          {step === 3 && (
            <StepRecap
              birth={birth}
              edition={edition}
              recipient={recipient}
              setRecipient={setRecipient}
              quote={quote}
              catalog={catalog}
              submitting={submitting}
              submitError={submitError}
              onSubmit={submit}
              promo={promo}
              setPromo={setPromo}
              applyPromo={applyPromo}
            />
          )}
        </main>

        {/* Footer sticky : prix + navigation */}
        <PriceRail quote={quote} quoting={quoting} />
        <NavBar
          step={step}
          totalSteps={STEPS.length}
          canGoNext={canGoNext}
          onPrev={goPrev}
          onNext={goNext}
        />
      </div>
    </PsPageShell>
  );
}

// ═══════════════════════════════════════════════════════════════
// Stepper
// ═══════════════════════════════════════════════════════════════
function Stepper({ current, steps, onGoTo }) {
  return (
    <ol data-testid="composer-stepper" style={stepperWrap}>
      {steps.map((label, i) => {
        const state = i < current ? 'done' : i === current ? 'active' : 'todo';
        return (
          <li
            key={label}
            onClick={() => onGoTo(i)}
            data-testid={`composer-step-${i}`}
            data-state={state}
            style={{ ...stepperItem, ...(state === 'active' ? stepperActive : {}), ...(state === 'done' ? stepperDone : {}) }}
          >
            <span style={stepperNum}>{String(i + 1).padStart(2, '0')}</span>
            <span style={stepperLabel}>{label}</span>
          </li>
        );
      })}
    </ol>
  );
}

// ═══════════════════════════════════════════════════════════════
// STEP 1 · Données de naissance
// ═══════════════════════════════════════════════════════════════
function StepBirthData({ birth, setBirth }) {
  const update = (k) => (e) => setBirth((b) => ({ ...b, [k]: e.target.value }));
  return (
    <section data-testid="composer-step-birth">
      <h2 style={h2Style}>Vos données de naissance</h2>
      <p style={bodyStyle}>
        Elles servent au calcul du ciel — jamais partagées, jamais revendues.
        L'heure exacte permet le calcul des maisons et de l'ascendant. Si vous ne
        l'avez pas, laissez le champ vide : nous vous proposerons un chapitre spécial.
      </p>

      <p style={fieldLabel}>Votre email</p>
      <input type="email" required value={birth.email} onChange={update('email')}
             placeholder="vous@exemple.fr"
             data-testid="composer-input-email" style={input}/>

      <p style={fieldLabel}>Votre prénom</p>
      <input type="text" required value={birth.first_name} onChange={update('first_name')}
             placeholder="Marie"
             data-testid="composer-input-firstname" style={input}/>

      <div style={twoCols}>
        <div>
          <p style={fieldLabel}>Date de naissance</p>
          <input type="date" required value={birth.birth_date} onChange={update('birth_date')}
                 data-testid="composer-input-birthdate" style={input}/>
        </div>
        <div>
          <p style={fieldLabel}>Heure exacte <span style={optional}>(optionnel)</span></p>
          <input type="time" value={birth.birth_time} onChange={update('birth_time')}
                 data-testid="composer-input-birthtime" style={input}/>
        </div>
      </div>

      <p style={fieldLabel}>Ville de naissance</p>
      <input type="text" required value={birth.birth_city} onChange={update('birth_city')}
             placeholder="Marseille"
             data-testid="composer-input-birthcity" style={input}/>

      {!birth.birth_time && (
        <div data-testid="composer-no-time-hint" style={hintBox}>
          <strong style={{ color: '#E8C766' }}>Vous n'avez pas votre heure exacte ?</strong>
          <p style={{ margin: '6px 0 0', fontSize: '0.95rem', lineHeight: 1.5 }}>
            Le chapitre <em>L'Heure Retrouvée</em> vous sera proposé à l'étape suivante.
            Nous cherchons son écho dans votre biographie plutôt que d'inventer une valeur.
          </p>
        </div>
      )}
    </section>
  );
}

// ═══════════════════════════════════════════════════════════════
// STEP 2 · Choix des chapitres
// ═══════════════════════════════════════════════════════════════
function StepChapters({ catalog, loading, error, selected, onToggle, quote, noBirthTime, onApplyFormula }) {
  if (loading) return <p style={bodyStyle}>Chargement du catalogue…</p>;
  if (error) return <p style={{ ...bodyStyle, color: '#E8916B' }}>{error}</p>;
  if (!catalog) return null;

  const formulas = [
    { slug: 'essentiel', label: "L'Essentiel", tagline: 'Je veux comprendre mon ciel, sans plus.', addons: [] },
    { slug: 'traversee_interieure', label: 'La Traversée intérieure', tagline: "Je me cherche, je veux savoir d'où je viens et où je vais.", addons: ['karma_destin', 'arbre_de_vie'] },
    { slug: 'ailleurs', label: "L'Ailleurs qui appelle", tagline: "J'hésite entre plusieurs lieux, plusieurs vies.", addons: ['astrocartographie'] },
    { slug: 'heure_retrouvee', label: "L'Heure Retrouvée", tagline: "Je n'ai pas mon heure exacte, mais je veux un vrai livre.", addons: ['heure_retrouvee', 'symboles_sabiens'] },
    { slug: 'complet', label: 'Le Livre Complet', tagline: 'Je veux tout, sans compromis.',
      addons: ['arbre_de_vie', 'astrocartographie', 'karma_destin', 'etoiles_fixes', 'symboles_sabiens'] },
  ];

  return (
    <section data-testid="composer-step-chapters">
      <h2 style={h2Style}>Vos chapitres</h2>
      <p style={bodyStyle}>
        Le Thème Natal complet est <b>toujours inclus</b> — 49 pages qui composent le socle.
        Choisissez une formule adaptée à ce que vous cherchez, ou composez vous-même votre livre.
      </p>

      {/* 5 Formules — accès rapide */}
      <p style={{ ...eyebrow, marginTop: 22 }}>NOS FORMULES</p>
      <div data-testid="composer-formulas" style={formulasGrid}>
        {formulas.map((f) => {
          const selectedSlugs = new Set(selected);
          const formulaSlugs = new Set(f.addons);
          const isActive = formulaSlugs.size === selectedSlugs.size &&
            [...formulaSlugs].every((s) => selectedSlugs.has(s));
          return (
            <button
              key={f.slug}
              type="button"
              onClick={() => onApplyFormula(f.addons)}
              data-testid={`composer-formula-${f.slug}`}
              data-active={isActive}
              style={{ ...formulaCard, ...(isActive ? formulaCardActive : {}) }}
            >
              <span style={formulaLabel}>{f.label}</span>
              <span style={formulaTagline}>« {f.tagline} »</span>
              {isActive && <span style={formulaCheck} aria-hidden>✓</span>}
            </button>
          );
        })}
      </div>

      {/* Composition à la carte */}
      <p style={{ ...eyebrow, marginTop: 28 }}>À LA CARTE</p>
      <p style={{ ...bodyStyle, fontSize: '0.92rem', color: '#B9B0D5', margin: '4px 0 14px' }}>
        Le premier chapitre coûte 29 €, chaque suivant 19 €, et le pack "tout compris" est plafonné à 99 €.
      </p>

      <div style={chaptersGrid}>
        {catalog.chapters.map((c) => {
          const isSelected = selected.includes(c.slug);
          const positionIfSelected = selected.indexOf(c.slug);
          const priceHint = isSelected
            ? (positionIfSelected === 0 ? '+29 €' : '+19 €')
            : (selected.length === 0 ? '+29 € pour le 1er' : '+19 €');
          return (
            <button
              key={c.slug}
              type="button"
              onClick={() => onToggle(c.slug)}
              data-testid={`composer-chapter-${c.slug}`}
              data-selected={isSelected}
              style={{ ...chapterCard, ...(isSelected ? chapterCardSelected : {}) }}
            >
              <div style={chapterHead}>
                <span style={chapterName}>{c.name}</span>
                <span style={{ ...chapterPrice, opacity: isSelected ? 1 : 0.65 }}>{priceHint}</span>
              </div>
              {c.subtitle && <p style={chapterSubtitle}>{c.subtitle}</p>}
              {c.tagline && <p style={chapterTagline}>{c.tagline}</p>}
              <p style={chapterMeta}>+ {c.pages_added} pages</p>
              {isSelected && <span style={chapterCheck} aria-hidden>✓</span>}
            </button>
          );
        })}
      </div>

      {quote?.chapters_cap_applied && (
        <p data-testid="composer-cap-notice" style={capNotice}>
          Plafond 99 € atteint — vous prenez l'intégralité des chapitres au meilleur prix.
        </p>
      )}
      {!noBirthTime && (
        <p style={{ ...bodyStyle, fontSize: '0.95rem', color: '#B9B0D5', marginTop: 24 }}>
          Vous avez indiqué votre heure de naissance — le chapitre <em>L'Heure Retrouvée</em>{' '}
          n'est donc pas nécessaire.
        </p>
      )}
    </section>
  );
}

// ═══════════════════════════════════════════════════════════════
// STEP 3 · Choix de l'édition
// ═══════════════════════════════════════════════════════════════
function StepEdition({ catalog, edition, setEdition, quote }) {
  if (!catalog) return null;
  return (
    <section data-testid="composer-step-edition">
      <h2 style={h2Style}>Votre édition</h2>
      <p style={bodyStyle}>
        Trois manières de recevoir votre livre. Le contenu — et le nombre de chapitres —
        est identique. Vous choisissez seulement la matière.
      </p>

      <div style={editionsList}>
        {catalog.editions.map((ed) => {
          const isSelected = ed.slug === edition;
          return (
            <button
              key={ed.slug}
              type="button"
              onClick={() => setEdition(ed.slug)}
              data-testid={`composer-edition-${ed.slug}`}
              data-selected={isSelected}
              style={{ ...editionCard, ...(isSelected ? editionCardSelected : {}) }}
            >
              <div style={editionHead}>
                <span style={editionName}>{ed.label}</span>
                <span style={editionPrice}>{ed.price_eur} €</span>
              </div>
              <p style={editionDelivery}>{ed.delivery}</p>
              <p style={editionBase}>Socle : {ed.pages_base} pages du Thème Natal</p>
              {isSelected && <span style={chapterCheck} aria-hidden>✓</span>}
            </button>
          );
        })}
      </div>

      {quote && (
        <div style={runningTotal} data-testid="composer-running-total">
          <span>Total avec cette édition</span>
          <strong>{quote.total_eur} €</strong>
        </div>
      )}
    </section>
  );
}

// ═══════════════════════════════════════════════════════════════
// STEP 4 · Récapitulatif + destinataire optionnel + submit
// ═══════════════════════════════════════════════════════════════
function StepRecap({ birth, edition, recipient, setRecipient, quote, catalog, submitting, submitError, onSubmit, promo, setPromo, applyPromo }) {
  const updateRecipient = (k) => (e) => setRecipient((r) => ({ ...r, [k]: e.target.value }));
  const isPhysical = edition === 'brochee' || edition === 'reliee';
  const editionMeta = catalog?.editions?.find((e) => e.slug === edition);
  const finalTotal = promo?.applied ? promo.total_eur : (quote?.total_eur || 0);

  return (
    <section data-testid="composer-step-recap">
      <h2 style={h2Style}>Récapitulatif</h2>

      <div style={recapBlock}>
        <p style={recapLine}><span>Édition</span><b>{editionMeta?.label} · {editionMeta?.price_eur} €</b></p>
        <p style={recapLine}><span>Chapitres</span><b>{quote?.chapters?.length || 0} choisi{(quote?.chapters?.length || 0) > 1 ? 's' : ''} · {quote?.chapters_price_eur || 0} €</b></p>
        {quote?.chapters?.map((c) => (
          <p key={c.slug} style={{ ...recapLine, fontSize: '0.9rem', color: '#B9B0D5', borderBottom: 'none', padding: '4px 0' }}>
            <span>· {c.name}</span><span>{c.unit_eur} €</span>
          </p>
        ))}
        <p style={recapLine}><span>Livre pour</span><b>{birth.first_name}</b></p>
        <p style={recapLine}><span>Livraison</span><b>{birth.email}</b></p>
        <p style={recapLine}><span>Pages estimées</span><b>{quote?.total_pages || 49}</b></p>
      </div>

      {isPhysical && (
        <div style={{ marginTop: 32 }}>
          <p style={eyebrow}>PERSONNALISATION DU LIVRE PHYSIQUE</p>
          <p style={fieldLabel}>Prénom imprimé sur la couverture <span style={optional}>(par défaut : votre prénom)</span></p>
          <input type="text" value={recipient.recipient_first_name} onChange={updateRecipient('recipient_first_name')}
                 placeholder={birth.first_name}
                 data-testid="composer-input-recipient" style={input} maxLength={80}/>
          <p style={fieldLabel}>Dédicace imprimée en tête d'ouvrage <span style={optional}>(optionnel)</span></p>
          <textarea rows={3} maxLength={400} value={recipient.dedication} onChange={updateRecipient('dedication')}
                    placeholder="Pour Marie, qui prend soin de ce que d'autres oublient."
                    data-testid="composer-input-dedication"
                    style={{ ...input, resize: 'vertical', fontFamily: 'inherit' }}/>
        </div>
      )}

      <div style={totalBox}>
        <span style={totalLabel}>Total à régler</span>
        <span style={totalValue} data-testid="composer-total">
          {promo?.applied && (
            <span style={{ fontSize: '1rem', color: '#B9B0D5', textDecoration: 'line-through', marginRight: 10 }}>
              {promo.original_total_eur} €
            </span>
          )}
          {finalTotal} €
        </span>
      </div>

      {/* Code promo — universel, disponible pour tous */}
      <div style={{ marginTop: 20, padding: '14px 16px', border: '1px dashed rgba(212,175,55,0.35)', borderRadius: 4 }}>
        <p style={{ ...eyebrow, textAlign: 'left', margin: 0 }}>J'AI UN CODE PROMO</p>
        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          <input
            type="text"
            value={promo?.code || ''}
            onChange={(e) => setPromo((p) => ({ ...p, code: e.target.value.toUpperCase(), applied: false, message: null }))}
            placeholder="Votre code (ex : TOUT2026)"
            data-testid="composer-input-promo"
            style={{ ...input, marginTop: 0, flex: 1, textTransform: 'uppercase' }}
          />
          <button
            type="button"
            onClick={applyPromo}
            data-testid="composer-apply-promo"
            disabled={!promo?.code}
            style={{ ...ctaGhost, minWidth: 110, opacity: promo?.code ? 1 : 0.5, cursor: promo?.code ? 'pointer' : 'not-allowed' }}
          >
            Appliquer
          </button>
        </div>
        {promo?.message && (
          <p data-testid="composer-promo-message"
             style={{ margin: '10px 0 0', fontSize: '0.9rem', color: promo.applied ? '#E8C766' : '#E8916B' }}>
            {promo.message}
          </p>
        )}
      </div>

      {submitError && (
        <p data-testid="composer-submit-error" style={errorBox}>{submitError}</p>
      )}

      <button
        type="button"
        onClick={onSubmit}
        disabled={submitting}
        data-testid="composer-submit"
        style={{ ...ctaPrimary, width: '100%', textAlign: 'center', padding: '18px 28px', marginTop: 20,
                 cursor: submitting ? 'wait' : 'pointer', opacity: submitting ? 0.7 : 1 }}
      >
        {submitting ? 'Redirection…'
          : (promo?.applied && finalTotal === 0)
            ? 'Générer mon livre (offert)'
            : `Payer ${finalTotal} € en toute sécurité`}
      </button>
      <p style={reassure}>
        Paiement sécurisé Stripe · Composition dans l'heure · Édition Reliée : approbation 72 h avant impression
      </p>
    </section>
  );
}

// ═══════════════════════════════════════════════════════════════
// Composants transverses
// ═══════════════════════════════════════════════════════════════
function PriceRail({ quote, quoting }) {
  return (
    <aside data-testid="composer-price-rail" style={priceRail}>
      <span style={priceRailLabel}>{quoting ? 'Recalcul…' : 'Prix actuel'}</span>
      <strong style={priceRailValue}>{quote?.total_eur ?? '—'} €</strong>
      {quote?.chapters?.length ? (
        <span style={priceRailChapters}>
          {quote.chapters.length} chapitre{quote.chapters.length > 1 ? 's' : ''} · {quote.total_pages} pages
        </span>
      ) : (
        <span style={priceRailChapters}>Thème Natal seul · {quote?.total_pages || 49} pages</span>
      )}
    </aside>
  );
}

function NavBar({ step, totalSteps, canGoNext, onPrev, onNext }) {
  const isLast = step === totalSteps - 1;
  if (isLast) return null; // Le CTA de paiement est dans StepRecap
  return (
    <nav style={navBar}>
      <button
        type="button"
        onClick={onPrev}
        disabled={step === 0}
        data-testid="composer-nav-prev"
        style={{ ...ctaGhost, opacity: step === 0 ? 0.4 : 1, cursor: step === 0 ? 'not-allowed' : 'pointer' }}
      >
        ← Précédent
      </button>
      <button
        type="button"
        onClick={onNext}
        disabled={!canGoNext}
        data-testid="composer-nav-next"
        style={{ ...ctaPrimary, opacity: canGoNext ? 1 : 0.5, cursor: canGoNext ? 'pointer' : 'not-allowed' }}
      >
        Suivant →
      </button>
    </nav>
  );
}

// ═══════════════════════════════════════════════════════════════
// Styles (inline pour cohérence avec EditionReliee.js)
// ═══════════════════════════════════════════════════════════════
const pageWrap = { maxWidth: 860, margin: '0 auto', padding: '72px 24px 160px', color: '#F5EEE0', fontFamily: '"Cormorant Garamond", serif', lineHeight: 1.65 };
const headerStyle = { textAlign: 'center', marginBottom: 40 };
const eyebrow = { fontFamily: '"Cinzel", serif', fontSize: '0.72rem', letterSpacing: 3, color: '#D4AF37', margin: 0 };
const h1Style = { fontFamily: '"Playfair Display", serif', fontSize: 'clamp(2rem, 5vw, 3rem)', color: '#F5EEE0', margin: '10px 0 32px', fontWeight: 400, lineHeight: 1.2 };
const h2Style = { fontFamily: '"Playfair Display", serif', fontSize: '1.75rem', color: '#F5EEE0', margin: '0 0 14px', fontWeight: 400, lineHeight: 1.25 };
const bodyStyle = { fontSize: '1.05rem', color: '#F5EEE0', margin: '10px 0' };
const optional = { color: '#B9B0D5', fontSize: '0.8em' };
const reassure = { color: '#B9B0D5', fontSize: '0.88rem', margin: '14px 0 0', letterSpacing: 0.3, textAlign: 'center' };

const stepperWrap = { display: 'flex', flexWrap: 'wrap', gap: 8, listStyle: 'none', padding: 0, margin: 0, justifyContent: 'center' };
const stepperItem = { display: 'flex', alignItems: 'baseline', gap: 8, padding: '10px 16px', border: '1px solid rgba(212,175,55,0.22)', borderRadius: 4, background: 'rgba(15,26,60,0.4)', cursor: 'pointer', color: 'rgba(245,238,224,0.55)', transition: 'all 0.2s' };
const stepperActive = { color: '#F5EEE0', borderColor: '#D4AF37', background: 'rgba(212,175,55,0.08)' };
const stepperDone = { color: 'rgba(212,175,55,0.85)', borderColor: 'rgba(212,175,55,0.45)' };
const stepperNum = { fontFamily: '"Cinzel", serif', fontSize: '0.7rem', letterSpacing: 2, color: '#D4AF37' };
const stepperLabel = { fontFamily: '"Cinzel", serif', fontSize: '0.72rem', letterSpacing: 2, textTransform: 'uppercase' };

const mainCard = { background: 'rgba(15,26,60,0.55)', border: '1px solid rgba(212,175,55,0.22)', borderRadius: 8, padding: '36px 32px', margin: '24px 0', backdropFilter: 'blur(8px)' };

const fieldLabel = { fontFamily: '"Cinzel", serif', fontSize: '0.68rem', letterSpacing: 2, color: 'rgba(212,175,55,0.85)', textTransform: 'uppercase', margin: '18px 0 6px' };
const input = { display: 'block', width: '100%', marginTop: 6, padding: '11px 14px', background: 'rgba(15,26,60,0.6)', border: '1px solid rgba(212,175,55,0.3)', borderRadius: 4, color: '#F5EEE0', fontSize: '1rem', fontFamily: 'inherit', boxSizing: 'border-box' };
const twoCols = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 };
const hintBox = { marginTop: 24, padding: '16px 18px', background: 'rgba(232,199,102,0.06)', border: '1px solid rgba(212,175,55,0.22)', borderRadius: 4, color: '#F5EEE0' };

const chaptersGrid = { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 14, marginTop: 12 };
const formulasGrid = { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 12, marginTop: 10 };
const formulaCard = { position: 'relative', padding: '16px 18px', background: 'rgba(11,26,46,0.7)', border: '1px solid rgba(212,175,55,0.22)', borderRadius: 6, color: '#F5EEE0', textAlign: 'left', cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.18s', display: 'flex', flexDirection: 'column', gap: 6 };
const formulaCardActive = { borderColor: '#D4AF37', background: 'rgba(212,175,55,0.10)', boxShadow: '0 0 20px rgba(212,175,55,0.14)' };
const formulaLabel = { fontFamily: '"Playfair Display", serif', fontSize: '1.05rem', color: '#F5EEE0' };
const formulaTagline = { fontSize: '0.85rem', color: '#B9B0D5', fontStyle: 'italic', lineHeight: 1.4 };
const formulaCheck = { position: 'absolute', top: 8, right: 10, width: 22, height: 22, borderRadius: '50%', background: '#D4AF37', color: '#0F1A3C', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: '"Cinzel", serif', fontWeight: 700, fontSize: '0.75rem' };
const chapterCard = { position: 'relative', padding: '20px 18px', background: 'rgba(11,26,46,0.7)', border: '1px solid rgba(212,175,55,0.25)', borderRadius: 6, color: '#F5EEE0', textAlign: 'left', cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.18s' };
const chapterCardSelected = { borderColor: '#D4AF37', background: 'rgba(212,175,55,0.10)', boxShadow: '0 0 24px rgba(212,175,55,0.15)' };
const chapterHead = { display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 10 };
const chapterName = { fontFamily: '"Playfair Display", serif', fontSize: '1.15rem', color: '#F5EEE0' };
const chapterPrice = { fontFamily: '"Cinzel", serif', fontSize: '0.78rem', letterSpacing: 1.5, color: '#E8C766' };
const chapterSubtitle = { fontSize: '0.92rem', color: '#B9B0D5', margin: '4px 0 8px', fontStyle: 'italic' };
const chapterTagline = { fontSize: '0.9rem', color: 'rgba(245,238,224,0.75)', margin: '4px 0 10px', lineHeight: 1.45 };
const chapterMeta = { fontFamily: '"Cinzel", serif', fontSize: '0.66rem', letterSpacing: 1.5, color: 'rgba(212,175,55,0.7)', margin: 0, textTransform: 'uppercase' };
const chapterCheck = { position: 'absolute', top: 10, right: 12, width: 26, height: 26, borderRadius: '50%', background: '#D4AF37', color: '#0F1A3C', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: '"Cinzel", serif', fontWeight: 700, fontSize: '0.85rem' };
const capNotice = { marginTop: 22, padding: '14px 16px', background: 'rgba(232,199,102,0.08)', border: '1px dashed rgba(212,175,55,0.45)', borderRadius: 4, color: '#E8C766', textAlign: 'center', fontStyle: 'italic' };

const editionsList = { display: 'grid', gridTemplateColumns: '1fr', gap: 14, marginTop: 20 };
const editionCard = { position: 'relative', padding: '22px 22px 20px', background: 'rgba(11,26,46,0.7)', border: '1px solid rgba(212,175,55,0.25)', borderRadius: 6, color: '#F5EEE0', textAlign: 'left', cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.18s' };
const editionCardSelected = { borderColor: '#D4AF37', background: 'rgba(212,175,55,0.10)', boxShadow: '0 0 24px rgba(212,175,55,0.15)' };
const editionHead = { display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' };
const editionName = { fontFamily: '"Playfair Display", serif', fontSize: '1.35rem' };
const editionPrice = { fontFamily: '"Cinzel", serif', fontSize: '1.05rem', letterSpacing: 2, color: '#E8C766' };
const editionDelivery = { fontSize: '0.95rem', color: '#B9B0D5', margin: '8px 0 4px' };
const editionBase = { fontFamily: '"Cinzel", serif', fontSize: '0.66rem', letterSpacing: 1.5, color: 'rgba(212,175,55,0.65)', margin: 0, textTransform: 'uppercase' };
const runningTotal = { marginTop: 24, padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.28)', borderRadius: 4, fontFamily: '"Playfair Display", serif', fontSize: '1.2rem' };

const recapBlock = { marginTop: 12, padding: '10px 0' };
const recapLine = { display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '10px 0', borderBottom: '1px solid rgba(212,175,55,0.14)', margin: 0 };
const totalBox = { marginTop: 26, padding: '18px 20px', display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', background: 'rgba(212,175,55,0.08)', border: '1px solid #D4AF37', borderRadius: 4 };
const totalLabel = { fontFamily: '"Cinzel", serif', fontSize: '0.85rem', letterSpacing: 2, color: '#F5EEE0' };
const totalValue = { fontFamily: '"Playfair Display", serif', fontSize: '2rem', color: '#E8C766', fontWeight: 500 };
const errorBox = { marginTop: 16, padding: '12px 14px', background: 'rgba(232,144,107,0.14)', border: '1px solid rgba(232,144,107,0.35)', borderRadius: 4, color: '#F5EEE0' };

const priceRail = { position: 'sticky', bottom: 96, marginTop: 24, padding: '14px 20px', display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12, background: 'rgba(15,26,60,0.9)', border: '1px solid rgba(212,175,55,0.28)', borderRadius: 4, backdropFilter: 'blur(6px)' };
const priceRailLabel = { fontFamily: '"Cinzel", serif', fontSize: '0.7rem', letterSpacing: 2, color: '#D4AF37', textTransform: 'uppercase' };
const priceRailValue = { fontFamily: '"Playfair Display", serif', fontSize: '1.75rem', color: '#F5EEE0' };
const priceRailChapters = { fontSize: '0.85rem', color: '#B9B0D5', textAlign: 'right', flex: '1 1 auto' };

const navBar = { display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 20 };
const ctaPrimary = { display: 'inline-block', padding: '14px 26px', background: 'linear-gradient(135deg, #D4AF37, #E8C766)', color: '#0F1A3C', textDecoration: 'none', border: 'none', borderRadius: 4, fontFamily: '"Cinzel", serif', fontSize: '0.88rem', letterSpacing: 2.5, fontWeight: 600, cursor: 'pointer' };
const ctaGhost = { display: 'inline-block', padding: '14px 26px', background: 'transparent', color: '#F5EEE0', border: '1px solid rgba(212,175,55,0.35)', borderRadius: 4, fontFamily: '"Cinzel", serif', fontSize: '0.85rem', letterSpacing: 2, cursor: 'pointer' };
