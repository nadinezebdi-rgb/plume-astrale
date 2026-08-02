import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

/* ═══════════════════════════════════════════════════════════
   PLUME ASTRALE — LANDING v2
   Cible : femmes 35-70 ans · promesse guidance de vie
   Design fidèle au brief user (Georgia serif, palette #d9b26a/#6a5acd).
   ═══════════════════════════════════════════════════════════ */

const styles = `
  .pa-page{background:#0b1020;color:#e8e6f0;
    font-family:Georgia,'Times New Roman',serif;line-height:1.6;margin:0;min-height:100vh;}
  .pa-wrap{max-width:920px;margin:0 auto;padding:0 20px;}
  .pa-band{background:linear-gradient(90deg,#1a1030,#241640);
    color:#d9b26a;text-align:center;font-size:14px;
    letter-spacing:1px;padding:10px;text-transform:uppercase;}
  .pa-section{padding:64px 0;border-bottom:1px solid #ffffff12;}
  .pa-h1{font-size:2.4rem;line-height:1.25;margin:0 0 18px;color:#e8e6f0;}
  .pa-h2{font-size:1.8rem;color:#d9b26a;margin:0 0 20px;}
  .pa-em{color:#d9b26a;font-style:italic;}
  .pa-lead{font-size:1.15rem;color:#b8b4c9;}
  .pa-cta{display:inline-block;background:#d9b26a;color:#1a1030;
    font-weight:bold;text-decoration:none;padding:18px 34px;border-radius:40px;
    font-size:1.05rem;letter-spacing:.5px;margin:14px 0;text-transform:uppercase;
    border:none;cursor:pointer;transition:transform .15s ease, box-shadow .15s ease;}
  .pa-cta:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(217,178,106,.35);}
  .pa-cta.sec{background:transparent;color:#d9b26a;border:1px solid #d9b26a;}
  .pa-cta:disabled{opacity:.6;cursor:not-allowed;}
  .pa-mini{font-size:.9rem;color:#b8b4c9;}
  .pa-grid{display:flex;flex-wrap:wrap;gap:18px;margin-top:24px;}
  .pa-card{flex:1 1 260px;background:#141a33;border:1px solid #ffffff14;
    border-radius:14px;padding:22px;}
  .pa-table{width:100%;border-collapse:collapse;margin-top:20px;}
  .pa-table td{padding:12px 8px;border-bottom:1px solid #ffffff10;color:#e8e6f0;}
  .pa-old{text-decoration:line-through;color:#8a86a0;}
  .pa-total{font-size:1.5rem;color:#d9b26a;font-weight:bold;}
  .pa-guar{background:#141a33;border:1px solid #d9b26a;
    border-radius:16px;padding:32px;text-align:center;}
  .pa-quote{background:#141a33;border-left:3px solid #d9b26a;
    border-radius:8px;padding:18px 22px;margin:16px 0;font-style:italic;color:#e8e6f0;}
  .pa-quote span{display:block;font-style:normal;color:#d9b26a;
    margin-top:10px;font-size:.9rem;}
  .pa-faq{margin:14px 0;}
  .pa-faq summary{cursor:pointer;color:#d9b26a;font-size:1.1rem;padding:10px 0;list-style:none;}
  .pa-faq summary::-webkit-details-marker{display:none;}
  .pa-faq summary::before{content:'✦ ';color:#d9b26a;}
  .pa-faq[open] summary::before{content:'✧ ';}
  .pa-legal{font-size:.8rem;color:#7d7a90;text-align:center;padding:30px 20px;}
  .pa-error{color:#f87171;font-size:.9rem;margin-top:10px;}
  .pa-form{display:flex;flex-direction:column;gap:12px;margin:20px auto 0;max-width:520px;text-align:left;}
  .pa-input{background:#0f1428;border:1px solid #ffffff20;color:#e8e6f0;
    padding:12px 16px;border-radius:10px;font-family:Georgia,serif;font-size:1rem;}
  .pa-input:focus{outline:none;border-color:#d9b26a;}
  .pa-label{font-size:.85rem;color:#b8b4c9;letter-spacing:.5px;text-transform:uppercase;}
  .pa-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
  @media(max-width:600px){
    .pa-h1{font-size:1.9rem;}
    .pa-h2{font-size:1.5rem;}
    .pa-row{grid-template-columns:1fr;}
  }
`;

const CheckoutForm = ({ onSubmit, loading, error }) => {
  const [form, setForm] = useState({
    email: '',
    first_name: '',
    birth_date: '',
    birth_time: '',
    birth_city: 'Paris',
    birth_country: 'FR',
  });
  const upd = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  const handle = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form className="pa-form" onSubmit={handle} data-testid="lecture-complete-form">
      <div>
        <div className="pa-label">Prénom</div>
        <input
          className="pa-input"
          value={form.first_name}
          onChange={(e) => upd('first_name', e.target.value)}
          required
          data-testid="lecture-first-name"
          style={{ width: '100%' }}
        />
      </div>
      <div>
        <div className="pa-label">Email</div>
        <input
          className="pa-input"
          type="email"
          value={form.email}
          onChange={(e) => upd('email', e.target.value)}
          required
          data-testid="lecture-email"
          style={{ width: '100%' }}
        />
      </div>
      <div className="pa-row">
        <div>
          <div className="pa-label">Date de naissance</div>
          <input
            className="pa-input"
            type="date"
            value={form.birth_date}
            onChange={(e) => upd('birth_date', e.target.value)}
            required
            data-testid="lecture-birth-date"
            style={{ width: '100%' }}
          />
        </div>
        <div>
          <div className="pa-label">Heure de naissance</div>
          <input
            className="pa-input"
            type="time"
            value={form.birth_time}
            onChange={(e) => upd('birth_time', e.target.value)}
            data-testid="lecture-birth-time"
            style={{ width: '100%' }}
          />
        </div>
      </div>
      <div>
        <div className="pa-label">Ville de naissance</div>
        <input
          className="pa-input"
          value={form.birth_city}
          onChange={(e) => upd('birth_city', e.target.value)}
          data-testid="lecture-birth-city"
          style={{ width: '100%' }}
        />
      </div>
      <button
        type="submit"
        className="pa-cta"
        disabled={loading}
        data-testid="lecture-checkout-btn"
        style={{ marginTop: 10 }}
      >
        {loading ? 'Redirection…' : 'Je demande ma lecture complète · 97€'}
      </button>
      {error && <div className="pa-error" data-testid="lecture-error">{error}</div>}
    </form>
  );
};

export default function Index() {
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [scarcity, setScarcity] = useState(null);

  React.useEffect(() => {
    let cancel = false;
    fetch(`${API}/api/lecture-complete/scarcity`)
      .then((r) => r.json())
      .then((d) => { if (!cancel) setScarcity(d); })
      .catch(() => {});
    return () => { cancel = true; };
  }, []);

  const startCheckout = async (form) => {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lecture-complete/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          ...form,
          origin_url: window.location.origin,
        }),
      });
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      } else {
        setError(data.detail || 'Impossible de créer la session.');
        setLoading(false);
      }
    } catch (e) {
      setError('Erreur de connexion. Réessaie dans quelques instants.');
      setLoading(false);
    }
  };

  const scrollToForm = () => {
    setShowForm(true);
    setTimeout(() => {
      document.getElementById('checkout')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 50);
  };

  return (
    <>
      <SEO
        path="/"
        title="Plume Astrale · La Lecture Complète de ton Ciel"
        description="Une lecture personnelle de ton thème natal par Soléna. Guidance symbolique pour les femmes qui cherchent à comprendre le présent — sans horoscope générique."
      />
      <style>{styles}</style>

      <div className="pa-page" data-testid="landing-v2">
        {/* ═══ BANDEAU HAUT ═══ */}
        <div className="pa-band" data-testid="landing-band">
          {scarcity && scarcity.sold_out ? (
            <>
              ✦ Complet pour ce cycle · Solena a lu plus de 2&nbsp;000 ciels · Prochaine ouverture le prochain cycle lunaire ✦
            </>
          ) : (
            <>
              ✦ Solena a lu plus de 2&nbsp;000 ciels · Il reste{' '}
              <strong data-testid="scarcity-remaining">
                {scarcity ? scarcity.remaining : 12}
              </strong>
              {' '}lectures complètes pour ce cycle lunaire ✦
            </>
          )}
        </div>

        {/* ═══ HERO ═══ */}
        <section className="pa-section" style={{ textAlign: 'center' }}>
          <div className="pa-wrap">
            <h1 className="pa-h1">
              Si tu me lis à cette heure-ci,<br />
              c'est que quelque chose en toi cherche une <span className="pa-em">réponse</span>.
            </h1>
            <p className="pa-lead">
              Ton ciel de naissance contient une carte : ce que ta vie essaie de te dire
              sur l'amour, ta famille, ton chemin, ce qui se répète — et ce qui s'apprête à changer.
              {' '}<strong>Soléna la lit avec toi.</strong>
            </p>
            <p className="pa-lead">
              Pas d'horoscope générique. Une lecture personnelle de ton thème,
              à partir de ta vraie date et de ton vrai lieu de naissance.
            </p>
            <Link
              to={user ? '/mon-compte' : '/inscription'}
              className="pa-cta"
              data-testid="landing-hero-signup"
            >
              Demander ma lecture · 20 crédits offerts
            </Link>
            <p className="pa-mini">
              Sans carte bancaire · Première réponse en 2 minutes · Guidance symbolique personnalisée
            </p>
            <p className="pa-mini">
              ✓ Données astro réelles · ✓ Éphémérides professionnelles · ✓ Paiement sécurisé Stripe
            </p>
          </div>
        </section>

        {/* ═══ SECTION 1 · LE MIROIR ═══ */}
        <section className="pa-section">
          <div className="pa-wrap">
            <h2 className="pa-h2">Il y a des soirs où tout remonte.</h2>
            <p className="pa-lead">
              Les questions qu'on n'ose dire à personne.{' '}
              <em>
                Pourquoi ma vie a pris ce tournant. Pourquoi cette relation, encore.
                Est-ce que je fais le bon choix. Qu'est-ce qui m'attend, vraiment.
              </em>
            </p>
            <p className="pa-lead">
              On a traversé beaucoup. Des amours, des ruptures, des deuils, des recommencements.
              Et parfois, au milieu de la nuit, on aimerait juste que quelqu'un nous aide
              à <strong>y voir clair</strong> — sans nous juger, sans nous vendre du rêve.
            </p>
            <p className="pa-lead">
              <strong>Ce n'est pas de la faiblesse. C'est de la lucidité. Et ça se lit.</strong>
            </p>
          </div>
        </section>

        {/* ═══ SECTION 2 · SOLÉNA ═══ */}
        <section className="pa-section">
          <div className="pa-wrap">
            <h2 className="pa-h2">Je suis Soléna.</h2>
            <p className="pa-lead">
              Depuis quinze ans, j'accompagne des femmes qui, comme toi, sentent qu'il y a{' '}
              <span className="pa-em">une logique</span> derrière leurs histoires.
              Une femme sur deux vient me voir non pas pour connaître l'avenir —
              mais pour <strong>comprendre le présent</strong>.
            </p>
            <p className="pa-lead">
              Ma méthode ne relève pas de la magie. C'est une lecture : ton thème natal calculé à la minute près,
              la symbolique du tarot, la trame karmique. Je te montre les cycles, les répétitions, les tournants.{' '}
              <strong>Pas un destin figé — des clés de compréhension.</strong>
            </p>
            <p className="pa-lead">
              Ce que tu fais de ces clés t'appartient. Mais au moins, tu ne marcheras plus dans le noir.
            </p>
            <p className="pa-mini">
              — Soléna, Plume Astrale · 4.9/5 · plus de 2&nbsp;000 âmes accompagnées
            </p>
          </div>
        </section>

        {/* ═══ SECTION 3 · POUR QUOI ═══ */}
        <section className="pa-section">
          <div className="pa-wrap">
            <h2 className="pa-h2">Ce que Soléna éclaire pour toi</h2>
            <div className="pa-grid">
              <div className="pa-card">
                💜 <strong>Tes liens du cœur</strong>
                <br />
                comprendre tes relations, ce qui se rejoue, ce qui peut s'apaiser.
              </div>
              <div className="pa-card">
                🏡 <strong>Ta famille &amp; tes racines</strong>
                <br />
                les héritages, les nœuds, les réconciliations possibles.
              </div>
              <div className="pa-card">
                🌿 <strong>Ton chemin de vie</strong>
                <br />
                les transitions, les grands passages, le sens de cette période.
              </div>
              <div className="pa-card">
                ✨ <strong>Ta trame karmique</strong>
                <br />
                pourquoi certaines épreuves reviennent, et comment les traverser.
              </div>
              <div className="pa-card">
                🌙 <strong>Tes cycles à venir</strong>
                <br />
                les fenêtres favorables des prochains mois, mois par mois.
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 4 · EMPILEMENT DE VALEUR ═══ */}
        <section className="pa-section" id="checkout">
          <div className="pa-wrap">
            <h2 className="pa-h2">La Lecture Complète de ton Ciel</h2>
            <p className="pa-lead">Tout réuni pour la première fois.</p>
            <table className="pa-table">
              <tbody>
                <tr>
                  <td>
                    ✦ <strong>Ton Thème Natal décodé</strong> — la carte complète de ton ciel de naissance
                  </td>
                  <td className="pa-old">29€</td>
                </tr>
                <tr>
                  <td>
                    ✦ <strong>Ton Guide de Cycles 2026</strong> — mois par mois, tes périodes clés
                  </td>
                  <td className="pa-old">34,99€</td>
                </tr>
                <tr>
                  <td>
                    ✦ <strong>Ta Lecture Karmique + Arbre de Vie</strong> — la racine de ce qui se répète
                  </td>
                  <td className="pa-old">39€</td>
                </tr>
                <tr>
                  <td>
                    ✦ <strong>Ton Analyse des Liens</strong> — comprendre tes relations proches
                  </td>
                  <td className="pa-old">24€</td>
                </tr>
                <tr>
                  <td>
                    ✦ <strong>Tes 12 fenêtres favorables 2026</strong> — le calendrier de tes bons moments
                  </td>
                  <td className="pa-old">29€</td>
                </tr>
                <tr>
                  <td>
                    ✦ <strong>Soléna à tes côtés · 90 jours</strong> — pose tes questions, le jour où elles viennent
                  </td>
                  <td className="pa-old">59€</td>
                </tr>
                <tr>
                  <td><strong>VALEUR TOTALE</strong></td>
                  <td className="pa-old"><strong>214€</strong></td>
                </tr>
              </tbody>
            </table>
            <p className="pa-total" style={{ textAlign: 'center', marginTop: 24 }}>
              👉 Aujourd'hui, tout est à toi pour 97€.
            </p>
            <div style={{ textAlign: 'center' }}>
              {!showForm ? (
                <button
                  className="pa-cta"
                  onClick={scrollToForm}
                  data-testid="landing-open-form-btn"
                >
                  Je demande ma lecture complète · 97€
                </button>
              ) : (
                <CheckoutForm onSubmit={startCheckout} loading={loading} error={error} />
              )}
            </div>
          </div>
        </section>

        {/* ═══ SECTION 5 · BONUS ═══ */}
        <section className="pa-section">
          <div className="pa-wrap">
            <h2 className="pa-h2">Et parce que tu commences maintenant, 4 présents (valeur 90€)</h2>
            <div className="pa-grid">
              <div className="pa-card">
                🎁 <strong>Le Rituel du Soir apaisant</strong> <span className="pa-old">27€</span>
                <br />pour les nuits où tout remonte.
              </div>
              <div className="pa-card">
                🎁 <strong>Ta Carte des Liens</strong> <span className="pa-old">19€</span>
                <br />comment aimer et te faire comprendre, selon ton profil.
              </div>
              <div className="pa-card">
                🎁 <strong>Ton calendrier des 12 fenêtres 2026</strong> <span className="pa-old">29€</span>
                <br />imprimable, à garder près de toi.
              </div>
              <div className="pa-card">
                🎁 <strong>Une question longue prioritaire à Soléna</strong> <span className="pa-old">15€</span>
                <br />une vraie réponse posée, prise à cœur.
              </div>
            </div>
            <p className="pa-mini" style={{ textAlign: 'center', marginTop: 20 }}>
              ⏳ Ces présents repartent avec le cycle lunaire.
            </p>
          </div>
        </section>

        {/* ═══ SECTION 6 · GARANTIE ═══ */}
        <section className="pa-section">
          <div className="pa-wrap">
            <div className="pa-guar">
              <h2 className="pa-h2" style={{ marginBottom: 12 }}>
                🛡️ Garantie «&nbsp;Clarté ou remboursée&nbsp;»
              </h2>
              <p className="pa-lead">
                Reçois ta lecture. Si dans les 14 jours elle ne t'a{' '}
                <strong>pas apporté au moins une vraie clarté sur ce que tu traverses</strong> —
                tu écris un mot à Soléna, et on te rembourse.
                Intégralement. Sans avoir à te justifier.
              </p>
              <p className="pa-em">Le risque est pour moi. La tranquillité est pour toi.</p>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 7 · TÉMOIGNAGES ═══ */}
        <section className="pa-section">
          <div className="pa-wrap">
            <h2 className="pa-h2">Des femmes qui ont enfin vu clair</h2>
            <div className="pa-quote">
              ✦ VÉRIFIÉ — «&nbsp;Rien de générique, rien de flou. Soléna m'a expliqué pourquoi je revivais toujours
              le même schéma — et comment le comprendre. Je me sens plus alignée.&nbsp;»
              <span>Léa M., Poissons · Lyon</span>
            </div>
            <div className="pa-quote">
              ✦ VÉRIFIÉ — «&nbsp;J'étais sceptique. La finesse de la lecture m'a scotchée. Ça m'a aidée à faire
              la paix avec une histoire de famille.&nbsp;»
              <span>Sarah T., Cancer · Bordeaux</span>
            </div>
            <div className="pa-quote">
              ✦ VÉRIFIÉ — «&nbsp;Je relis ma lecture chaque semaine. Plus apaisant que trois ans à ressasser toute seule.&nbsp;»
              <span>Manon D., Lion · Marseille</span>
            </div>
          </div>
        </section>

        {/* ═══ SECTION 8 · CTA FINAL ═══ */}
        <section className="pa-section" style={{ textAlign: 'center' }}>
          <div className="pa-wrap">
            <h2 className="pa-h2">La nuit est le bon moment pour écouter.</h2>
            <p className="pa-lead">
              Tu peux refermer cette page et continuer à porter tes questions seule…
              ou laisser Soléna t'aider à lire ce qui se joue vraiment, dès maintenant.
            </p>
            <button
              className="pa-cta"
              onClick={scrollToForm}
              data-testid="landing-final-cta"
            >
              Je demande ma lecture complète · 97€
            </button>
            <br />
            <Link
              to={user ? '/mon-compte' : '/inscription'}
              className="pa-cta sec"
              data-testid="landing-final-signup"
            >
              Ou commence gratuitement · 20 crédits offerts
            </Link>
            <p className="pa-mini">
              ✓ Réponse sous 2h · ✓ Sans engagement · ✓ Garantie 14 jours «&nbsp;Clarté ou remboursée&nbsp;»
            </p>
          </div>
        </section>

        {/* ═══ SECTION 9 · FAQ ═══ */}
        <section className="pa-section">
          <div className="pa-wrap">
            <h2 className="pa-h2">Questions fréquentes</h2>
            <details className="pa-faq" data-testid="faq-sceptique">
              <summary>Est-ce que ça marche si je suis sceptique ?</summary>
              <p className="pa-lead">
                C'est même souvent là que la lecture surprend le plus. Soléna ne te demande pas
                d'y croire — juste de lire ce que ton ciel révèle. Beaucoup arrivent sceptiques et repartent
                troublées de justesse.
              </p>
            </details>
            <details className="pa-faq" data-testid="faq-avenir">
              <summary>Est-ce que Soléna prédit l'avenir ?</summary>
              <p className="pa-lead">
                Non. Soléna offre une <strong>guidance symbolique et personnalisée</strong> : elle éclaire
                les cycles, les tendances, le sens — pas un destin figé. Les choix restent les tiens. C'est un
                accompagnement de compréhension et de mieux-être, pas une science exacte.
              </p>
            </details>
            <details className="pa-faq" data-testid="faq-tech">
              <summary>Je ne suis pas très à l'aise avec la technologie.</summary>
              <p className="pa-lead">
                Tout se fait en quelques clics, et Soléna te guide pas à pas. Si tu sais envoyer
                un message, tu sais lui parler.
              </p>
            </details>
            <details className="pa-faq" data-testid="faq-retour">
              <summary>Et si ça ne me correspond pas ?</summary>
              <p className="pa-lead">
                La garantie «&nbsp;Clarté ou remboursée&nbsp;» de 14 jours existe exactement pour ça.
                Aucun risque.
              </p>
            </details>
          </div>
        </section>

        {/* ═══ MENTION LÉGALE ═══ */}
        <p className="pa-legal">
          Plume Astrale propose une guidance symbolique à visée de divertissement et de développement personnel.
          Soléna est un guide incarné par un avatar. Les lectures ne constituent ni un avis médical,
          ni psychologique, ni financier.
          <br />
          <Link to="/notre-cadre" style={{ color: '#d9b26a', textDecoration: 'underline', marginRight: 12 }}>
            Notre cadre
          </Link>
          <Link to="/charte-confiance" style={{ color: '#d9b26a', textDecoration: 'underline' }}>
            Charte de confiance
          </Link>
        </p>
      </div>
    </>
  );
}
