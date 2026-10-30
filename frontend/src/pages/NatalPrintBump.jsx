/**
 * NatalPrintBump — Page de bump "Livre relié Lulu" 79€
 * Entrée via l'email de livraison du Thème Natal :
 *   /natal-print?token={session_id}&prenom={prenom}
 */
import {useState, useMemo} from 'react';
import { useSearchParams } from 'react-router-dom';

const API = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/+$/, '') + '/api';

const COUNTRIES = [
  { code: 'FR', name: 'France' },
  { code: 'BE', name: 'Belgique' },
  { code: 'CH', name: 'Suisse' },
  { code: 'LU', name: 'Luxembourg' },
  { code: 'MC', name: 'Monaco' },
  { code: 'DE', name: 'Allemagne' },
  { code: 'ES', name: 'Espagne' },
  { code: 'IT', name: 'Italie' },
  { code: 'PT', name: 'Portugal' },
  { code: 'NL', name: 'Pays-Bas' },
  { code: 'GB', name: 'Royaume-Uni' },
  { code: 'US', name: 'États-Unis' },
  { code: 'CA', name: 'Canada' },
];

export default function NatalPrintBump() {
  const [sp] = useSearchParams();
  const token = sp.get('token') || '';
  const prenom = sp.get('prenom') || '';
  const dob = sp.get('dob') || '';

  const [form, setForm] = useState({
    name: '', street1: '', street2: '', city: '', postcode: '',
    country_code: 'FR', phone_number: '', email: '',
  });
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');

  const canQuote = useMemo(() => (
    form.name.trim().length >= 2 &&
    form.street1.trim().length >= 3 &&
    form.city.trim().length >= 1 &&
    form.postcode.trim().length >= 2 &&
    form.country_code.length === 2 &&
    form.phone_number.trim().length >= 4
  ), [form]);

  const canCheckout = canQuote && !!quote && /^\S+@\S+\.\S+$/.test(form.email);

  const h = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const getQuote = async () => {
    setErr(''); setLoading(true);
    try {
      const r = await fetch(`${API}/natal-print-bump/quote`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: { ...form } }),
      });
      if (!r.ok) throw new Error(`Devis indisponible (${r.status})`);
      setQuote(await r.json());
    } catch (e) {
      setErr(e.message || String(e)); setQuote(null);
    } finally { setLoading(false); }
  };

  const goCheckout = async () => {
    setErr(''); setLoading(true);
    try {
      const r = await fetch(`${API}/natal-print-bump/checkout`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_session_id: token, purchaser_email: form.email,
          first_name: prenom || form.name.split(' ')[0] || 'Voyageuse',
          birth_date_iso: dob || '1990-01-01',
          address: { ...form },
        }),
      });
      if (!r.ok) throw new Error(`Paiement impossible (${r.status})`);
      const data = await r.json();
      if (data?.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error('Pas de lien de paiement');
      }
    } catch (e) {
      setErr(e.message || String(e));
      setLoading(false);
    }
  };

  return (
    <div data-testid="natal-print-bump-page" style={{
      minHeight: '100vh', background: 'linear-gradient(135deg,#F0E6D2 0%,#E8DBC0 50%,#F0E6D2 100%)',
      padding: '48px 20px', fontFamily: '"Cormorant Garamond", Georgia, serif', color: '#1C1B26',
    }}>
      <div style={{ maxWidth: 720, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <div style={{ fontSize: 11, letterSpacing: '0.42em', textTransform: 'uppercase',
                        color: '#A8823F', fontFamily: 'Cinzel, serif' }}>
            Plume Astrale · Livre relié
          </div>
          <h1 style={{ fontWeight: 300, fontSize: '2.6rem', margin: '14px 0 10px',
                        lineHeight: 1.1 }}>
            {prenom ? <>Pour que ton livre, <em style={{ color: '#A8823F' }}>{prenom}</em>,<br/>dure.</>
                     : <>Pour que ton livre dure.</>}
          </h1>
          <p style={{ fontSize: 15, lineHeight: 1.6, color: '#3A3022', maxWidth: 540, margin: '0 auto' }}>
            Reçois chez toi l'exemplaire relié hardcover A5 de ton Thème Natal.
            Couverture rigide crème, impression haute qualité, un objet qui traverse les années.
          </p>
        </div>

        <div style={{ background: '#FBF5E8', border: '1px solid rgba(168,130,63,0.3)',
                      borderRadius: 16, padding: 28, boxShadow: '0 2px 20px rgba(168,130,63,0.08)' }}>
          <h2 style={{ fontSize: 20, fontWeight: 400, margin: '0 0 20px', color: '#A8823F',
                        letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            Adresse de livraison
          </h2>
          <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr 1fr' }}>
            <Field label="Nom complet" testid="field-name" value={form.name} onChange={h('name')} span={2}/>
            <Field label="Adresse" testid="field-street1" value={form.street1} onChange={h('street1')} span={2}/>
            <Field label="Complément (facultatif)" testid="field-street2" value={form.street2} onChange={h('street2')} span={2}/>
            <Field label="Code postal" testid="field-postcode" value={form.postcode} onChange={h('postcode')}/>
            <Field label="Ville" testid="field-city" value={form.city} onChange={h('city')}/>
            <div>
              <label style={labelStyle}>Pays</label>
              <select data-testid="field-country" value={form.country_code} onChange={h('country_code')}
                      style={inputStyle}>
                {COUNTRIES.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
              </select>
            </div>
            <Field label="Téléphone" testid="field-phone" value={form.phone_number} onChange={h('phone_number')}/>
            <Field label="Email" testid="field-email" value={form.email} onChange={h('email')} span={2}
                   placeholder="Pour recevoir le suivi d'expédition"/>
          </div>

          <div style={{ marginTop: 20, display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
            <button data-testid="btn-get-quote" onClick={getQuote} disabled={!canQuote || loading}
                    style={{ ...buttonStyle, background: '#A8823F' }}>
              {loading ? 'Calcul…' : (quote ? 'Recalculer le prix' : 'Afficher le prix exact')}
            </button>
            {quote && (
              <div data-testid="quote-display" style={{ fontSize: 15, color: '#1C1B26' }}>
                <strong style={{ fontSize: 22 }}>{quote.client_price_eur.toFixed(0)} €</strong>
                <span style={{ marginLeft: 10, color: '#8B7355', fontSize: 13 }}>
                  TTC — impression + livraison incluses
                  ({quote.quote?.estimated_shipping_days}j ouvrés)
                </span>
                {quote.quote?.mock && (
                  <div style={{ color: '#B36A00', fontSize: 11, marginTop: 4, fontStyle: 'italic' }}>
                    (devis simulé — compte Lulu non branché)
                  </div>
                )}
              </div>
            )}
          </div>

          {err && (
            <div data-testid="error-display" style={{
              marginTop: 14, padding: 10, background: '#FEE', border: '1px solid #FCC',
              color: '#A33', borderRadius: 8, fontSize: 13,
            }}>{err}</div>
          )}

          {quote && (
            <div style={{ marginTop: 24, paddingTop: 20, borderTop: '1px solid rgba(168,130,63,0.3)' }}>
              <button data-testid="btn-checkout" onClick={goCheckout} disabled={!canCheckout || loading}
                      style={{ ...buttonStyle, background: '#1C1B26', color: '#F0E6D2',
                                padding: '14px 32px', fontSize: 13 }}>
                {loading ? 'Redirection…' : `Payer ${quote.client_price_eur.toFixed(0)} €`}
              </button>
              <div style={{ fontSize: 11, color: '#8B7355', marginTop: 10, fontStyle: 'italic' }}>
                Paiement sécurisé Stripe · 3-5j d'impression + livraison
              </div>
            </div>
          )}
        </div>

        <div style={{ textAlign: 'center', marginTop: 32, fontSize: 12, color: '#8B7355',
                      lineHeight: 1.6 }}>
          Hardcover A5 148×210 mm · reliure cartonnée · intérieur blanc<br/>
          Imprimé & expédié par notre partenaire d'impression à la demande
        </div>
      </div>
    </div>
  );
}

const labelStyle = {
  display: 'block', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase',
  color: '#8B7355', marginBottom: 4, fontFamily: 'Cinzel, serif',
};
const inputStyle = {
  width: '100%', padding: '10px 12px', border: '1px solid rgba(168,130,63,0.3)',
  background: 'rgba(255,255,255,0.6)', borderRadius: 8, fontSize: 14,
  fontFamily: '"Cormorant Garamond", serif', color: '#1C1B26', boxSizing: 'border-box',
};
const buttonStyle = {
  padding: '10px 22px', border: 'none', borderRadius: 999, color: '#FBF5E8',
  fontFamily: 'Cinzel, serif', fontSize: 11, letterSpacing: '0.18em', textTransform: 'uppercase',
  cursor: 'pointer', fontWeight: 500,
};

function Field({ label, value, onChange, span = 1, placeholder, testid }) {
  return (
    <div style={{ gridColumn: `span ${span}` }}>
      <label style={labelStyle}>{label}</label>
      <input data-testid={testid} value={value} onChange={onChange} placeholder={placeholder || ''}
             style={inputStyle}/>
    </div>
  );
}
