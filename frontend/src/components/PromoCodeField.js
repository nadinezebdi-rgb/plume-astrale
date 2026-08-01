import React, { useState } from 'react';
import axios from 'axios';
import { Loader2, Check, X } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Champ Code promo réutilisable — cohérent avec ThemeNatalOneshot.
 * Props :
 *   - price       : montant original (nombre, EUR)
 *   - product     : identifiant produit envoyé à /api/promo/validate
 *   - testIdBase  : préfixe des data-testid (ex: "numerologie")
 *   - onStateChange(state) : callback avec { status, discount_percent, discount_amount, final_amount, admin_only, code }
 *
 * Le composant ne connaît pas le checkout — le parent lit le state pour envoyer promo_code lors du checkout.
 */
export default function PromoCodeField({ price, product, testIdBase = 'promo', onStateChange }) {
  const [code, setCode] = useState('');
  const [validating, setValidating] = useState(false);
  const [state, setState] = useState({
    status: 'idle',
    message: '',
    discount_percent: 0,
    discount_amount: 0,
    final_amount: price,
    admin_only: false,
    code: '',
  });

  const updateState = (next) => {
    setState(next);
    if (onStateChange) onStateChange(next);
  };

  const apply = async () => {
    const c = code.trim();
    if (!c) return;
    setValidating(true);
    try {
      const r = await axios.post(`${API}/api/promo/validate`, {
        code: c,
        product,
        amount: price,
      });
      const d = r.data || {};
      if (d.valid) {
        updateState({
          status: 'ok',
          message: d.message || 'Code appliqué.',
          discount_percent: d.discount_percent || 0,
          discount_amount: d.discount_amount || 0,
          final_amount: typeof d.final_amount === 'number' ? d.final_amount : price,
          admin_only: !!d.admin_only,
          stripe_promo_id: d.stripe_promo_id || null,
          code: c,
        });
      } else {
        updateState({
          status: 'ko',
          message: d.message || 'Code invalide.',
          discount_percent: 0,
          discount_amount: 0,
          final_amount: price,
          admin_only: false,
          code: c,
        });
      }
    } catch (e) {
      updateState({
        status: 'ko',
        message: 'Impossible de valider le code (connexion).',
        discount_percent: 0,
        discount_amount: 0,
        final_amount: price,
        admin_only: false,
        code: c,
      });
    } finally {
      setValidating(false);
    }
  };

  return (
    <div data-testid={`${testIdBase}-promo-field`}>
      <label
        className="text-xs uppercase block mb-2"
        style={{ color: 'rgba(212,175,55,0.75)', letterSpacing: '0.2em', fontFamily: 'Cinzel, serif' }}
      >
        Code promo (optionnel)
      </label>
      <div className="flex gap-2">
        <input
          type="text"
          value={code}
          onChange={(e) => {
            setCode(e.target.value.toUpperCase());
            if (state.status !== 'idle') {
              updateState({
                status: 'idle',
                message: '',
                discount_percent: 0,
                discount_amount: 0,
                final_amount: price,
                admin_only: false,
                code: '',
              });
            }
          }}
          placeholder="Ex: TOUT2026"
          data-testid={`${testIdBase}-promo-input`}
          className="flex-1 px-4 py-3 rounded-xl focus:outline-none"
          style={{
            background: 'rgba(12,9,24,0.6)',
            border: '1px solid rgba(212,175,55,0.25)',
            color: '#F4E8D2',
            letterSpacing: '0.2em',
            fontFamily: 'Cinzel, serif',
            fontSize: 13,
          }}
        />
        <button
          type="button"
          onClick={apply}
          disabled={!code.trim() || validating}
          data-testid={`${testIdBase}-promo-apply`}
          style={{
            padding: '0 20px',
            borderRadius: 12,
            background: 'rgba(212,175,55,0.12)',
            color: '#D4AF37',
            border: '1px solid rgba(212,175,55,0.4)',
            fontSize: 11,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            fontFamily: 'Cinzel, serif',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
          }}
        >
          {validating ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Appliquer'}
        </button>
      </div>

      {state.status === 'ok' && (
        <div
          className="mt-3 p-3 rounded-lg flex items-start gap-2"
          data-testid={`${testIdBase}-promo-ok`}
          style={{ background: 'rgba(74,222,128,0.10)', border: '1px solid rgba(74,222,128,0.35)' }}
        >
          <Check className="w-4 h-4 shrink-0 mt-0.5" style={{ color: '#4ADE80' }} strokeWidth={2} />
          <div className="text-xs flex-1">
            <div style={{ color: '#4ADE80', fontFamily: 'Cinzel, serif', letterSpacing: '0.1em', marginBottom: 4 }}>
              CODE APPLIQUÉ
            </div>
            <div style={{ color: 'rgba(227,215,255,0.85)', lineHeight: 1.5 }}>{state.message}</div>
            <div className="mt-2 flex items-baseline gap-2">
              <span style={{ color: 'rgba(227,215,255,0.5)', textDecoration: 'line-through', fontSize: 14 }}>
                {price.toFixed(2)}€
              </span>
              <span
                style={{
                  color: '#D4AF37',
                  fontSize: 22,
                  fontFamily: 'Cormorant Garamond, serif',
                  fontWeight: 400,
                }}
              >
                {state.final_amount === 0 ? 'Gratuit' : `${state.final_amount.toFixed(2)}€`}
              </span>
            </div>
            {state.admin_only && (
              <div style={{ color: 'rgba(232,199,102,0.75)', fontSize: 11, fontStyle: 'italic', marginTop: 4 }}>
                Ce code nécessite un compte administrateur pour être appliqué.
              </div>
            )}
          </div>
        </div>
      )}

      {state.status === 'ko' && (
        <div
          className="mt-3 p-3 rounded-lg flex items-start gap-2"
          data-testid={`${testIdBase}-promo-ko`}
          style={{ background: 'rgba(248,113,113,0.10)', border: '1px solid rgba(248,113,113,0.35)' }}
        >
          <X className="w-4 h-4 shrink-0 mt-0.5" style={{ color: '#F87171' }} strokeWidth={2} />
          <div className="text-xs" style={{ color: '#F87171' }}>{state.message}</div>
        </div>
      )}
    </div>
  );
}
