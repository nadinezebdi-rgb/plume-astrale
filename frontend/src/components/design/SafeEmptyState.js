import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Sparkles, MessageCircle, RefreshCw, Mail } from 'lucide-react';

/**
 * SafeEmptyState — filet de sécurité pour toute page produit.
 *
 * À afficher LORSQUE :
 *  - L'API a répondu 200 (donc `result` existe)
 *  - MAIS aucun contenu attendu n'a été trouvé dans la réponse (schéma cassé,
 *    changement de contrat côté fournisseur, timeout partiel, etc.)
 *
 * Objectif : sauvegarder la conversion émotionnelle. L'utilisatrice ne doit
 * JAMAIS se retrouver devant une page blanche — elle doit être guidée vers
 * Soléna qui prend le relais humain (et convertit vers un service premium).
 *
 * Usage :
 *   <SafeEmptyState
 *     productName="votre Révolution Solaire"
 *     onRetry={handleGenerate}
 *   />
 */

const SafeEmptyState = ({
  productName = 'votre lecture',
  onRetry = null,
  showChatCTA = true,
  supportEmail = 'contact@plume-astrale.fr',
  extraContext = null,
}) => {
  const navigate = useNavigate();
  const openSolena = () => {
    // Redirection vers la page de discussion avec Soléna
    navigate('/services/consultation');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="card-mystical text-center py-12 md:py-16 px-6"
      data-testid="safe-empty-state"
      style={{
        background: 'linear-gradient(160deg, rgba(212,175,55,0.06) 0%, rgba(26,32,53,0.75) 100%)',
        border: '1px solid rgba(212,175,55,0.28)',
        borderRadius: 24,
        backdropFilter: 'blur(14px)',
      }}
    >
      <div
        className="mx-auto mb-6 flex items-center justify-center rounded-full"
        style={{
          width: 64,
          height: 64,
          background: 'radial-gradient(circle, rgba(212,175,55,0.25), rgba(212,175,55,0.05) 70%)',
          border: '1px solid rgba(212,175,55,0.35)',
        }}
      >
        <Sparkles style={{ width: 26, height: 26, color: '#D4AF37' }} strokeWidth={1.4} />
      </div>

      <p
        className="text-[10px] uppercase mb-3"
        style={{
          color: 'rgba(212,175,55,0.8)',
          letterSpacing: '0.32em',
          fontFamily: 'Cinzel, serif',
        }}
      >
        ✦ Une pause dans les étoiles ✦
      </p>

      <h3
        className="text-2xl md:text-3xl mb-4"
        style={{
          fontFamily: 'Cormorant Garamond, serif',
          color: '#F5EEE0',
          fontWeight: 300,
          lineHeight: 1.15,
        }}
      >
        Le ciel est <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>momentanément silencieux</em>
      </h3>

      <p
        className="max-w-md mx-auto mb-8 text-sm md:text-base"
        style={{
          fontFamily: 'Cormorant Garamond, serif',
          color: 'rgba(227,215,255,0.75)',
          fontStyle: 'italic',
          lineHeight: 1.6,
        }}
      >
        Nous avons bien reçu vos données, mais {productName} n&apos;a pas pu se composer complètement à
        l&apos;instant. Ce n&apos;est jamais anodin — un signe que le moment demande un&nbsp;accompagnement plus personnel.
      </p>

      {extraContext && (
        <div
          className="max-w-md mx-auto mb-6 px-4 py-3 rounded-lg text-xs"
          style={{
            background: 'rgba(212,175,55,0.06)',
            border: '1px solid rgba(212,175,55,0.15)',
            color: 'rgba(227,215,255,0.55)',
          }}
        >
          {extraContext}
        </div>
      )}

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 max-w-md mx-auto">
        {showChatCTA && (
          <button
            onClick={openSolena}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-xs uppercase transition-all hover:scale-[1.02] w-full sm:w-auto justify-center"
            style={{
              background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
              color: '#111625',
              letterSpacing: '0.2em',
              fontWeight: 700,
              boxShadow: '0 12px 40px rgba(212,175,55,0.30)',
              border: 'none',
              cursor: 'pointer',
              fontFamily: 'Cinzel, serif',
            }}
            data-testid="safe-empty-solena-btn"
          >
            <MessageCircle style={{ width: 14, height: 14 }} strokeWidth={2} />
            Parler à Solena
          </button>
        )}

        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-xs uppercase w-full sm:w-auto justify-center hover:opacity-100 transition-opacity"
            style={{
              background: 'transparent',
              color: 'rgba(212,175,55,0.85)',
              letterSpacing: '0.2em',
              fontWeight: 500,
              border: '1px solid rgba(212,175,55,0.35)',
              cursor: 'pointer',
              fontFamily: 'Cinzel, serif',
              opacity: 0.85,
            }}
            data-testid="safe-empty-retry-btn"
          >
            <RefreshCw style={{ width: 13, height: 13 }} strokeWidth={2} />
            Réessayer
          </button>
        )}
      </div>

      <p
        className="mt-8 text-[10px]"
        style={{
          color: 'rgba(227,215,255,0.35)',
          letterSpacing: '0.15em',
        }}
      >
        <Mail style={{ display: 'inline', width: 10, height: 10, marginRight: 4, verticalAlign: 'middle' }} strokeWidth={2} />
        <a
          href={`mailto:${supportEmail}`}
          style={{ color: 'rgba(227,215,255,0.55)', textDecoration: 'underline', textUnderlineOffset: 3 }}
          data-testid="safe-empty-mail-link"
        >
          {supportEmail}
        </a>
        {' · nos gardiennes vous répondent en 24h'}
      </p>
    </motion.div>
  );
};

export default SafeEmptyState;
