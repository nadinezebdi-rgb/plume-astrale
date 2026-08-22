import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Mail, Shield, Clock } from 'lucide-react';

/**
 * NocturneClosing — Le Retour. Épilogue et proposition finale.
 * Papier Céleste. Une invitation, pas un push.
 */
export default function NocturneClosing({ signupPath }) {
  return (
    <section className="ne-section ne-section-paper" data-testid="nocturne-closing">
      <div className="ne-container">
        <div style={{ maxWidth: 640 }}>
          <div className="ne-overline">Épilogue</div>
          <h2 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-fusain)' }}>
            Souhaitez-vous que ce texte vous <span className="ne-serif-italic" style={{ color: 'var(--ne-vigne)' }}>accompagne</span>&nbsp;?
          </h2>
          <hr className="ne-rule-short" style={{ marginTop: 32, marginBottom: 32 }} />
          <p className="ne-lead" style={{ marginBottom: 48, color: 'rgba(10,10,15,0.72)' }}>
            Nous vous offrons un <em>aperçu de 5 pages</em> — vos trois luminaires, votre saison
            en cours, une invitation littéraire. Un cadeau, jamais une conversion.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'center' }}>
            <Link
              to={signupPath || '/inscription'}
              className="ne-btn ne-btn-primary"
              data-testid="nocturne-closing-cta"
            >
              Recevoir mon aperçu
              <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={1.5} />
            </Link>
            <Link
              to="/manifesto"
              className="ne-btn-ghost"
              data-testid="nocturne-closing-manifesto"
            >
              Lire notre manifeste
            </Link>
          </div>

          <div
            style={{
              marginTop: 64, display: 'flex', flexWrap: 'wrap', gap: 32,
              color: 'rgba(10,10,15,0.55)', fontFamily: 'var(--ne-sans)', fontSize: 13,
            }}
            data-testid="nocturne-closing-trust"
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Shield style={{ width: 14, height: 14 }} strokeWidth={1.5} color="var(--ne-succes)" />
              Paiement Stripe sécurisé
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Clock style={{ width: 14, height: 14 }} strokeWidth={1.5} color="var(--ne-info)" />
              Livraison instantanée
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Mail style={{ width: 14, height: 14 }} strokeWidth={1.5} color="var(--ne-laiton)" />
              Reçu par email
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
