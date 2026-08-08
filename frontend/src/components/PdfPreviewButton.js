import React, { useState } from 'react';
import { Download, FileText, Loader2, BookOpen } from 'lucide-react';

/**
 * PdfPreviewButton — bouton de téléchargement d'un aperçu 3 pages du PDF prestige
 * pour rassurer les acheteurs de livres (surtout campagne Noël).
 *
 * L'aperçu est un PDF signé (couverture illustrée, sommaire, chapter opener I,
 * extrait d'introduction) généré côté backend par /api/pdf-preview/{product}.
 *
 * Props :
 *   product : identifiant produit ('astrocartographie', 'kabbale', 'karma-destin',
 *             'numerologie', 'theme-natal', 'synastrie')
 *   variant : 'inline' (défaut) | 'ghost' — style visuel
 *   testid  : suffixe data-testid
 */
export default function PdfPreviewButton({ product, variant = 'inline', testid }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleDownload = async () => {
    setLoading(true);
    setError(null);
    try {
      const url = `${process.env.REACT_APP_BACKEND_URL}/api/pdf-preview/${product}?download=true`;
      // Ouvre en nouvel onglet pour permettre au navigateur de gérer l'affichage
      window.open(url, '_blank', 'noopener');
    } catch (e) {
      setError("Impossible de télécharger l'aperçu. Réessaie dans un instant.");
    } finally {
      setTimeout(() => setLoading(false), 800);
    }
  };

  const baseStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 10,
    padding: '12px 22px',
    borderRadius: 999,
    fontFamily: 'Inter, sans-serif',
    fontSize: 13,
    fontWeight: 600,
    letterSpacing: '0.10em',
    textTransform: 'uppercase',
    cursor: loading ? 'wait' : 'pointer',
    transition: 'all 0.25s ease',
    textDecoration: 'none',
  };

  const style = variant === 'ghost'
    ? {
        ...baseStyle,
        background: 'transparent',
        border: '1px solid rgba(143,110,36,0.55)',
        color: '#8F6E24',  /* deeper gold — AA on white */
      }
    : {
        ...baseStyle,
        background: '#FFFFFF',
        border: '1px solid rgba(15,26,60,0.12)',
        color: '#0F1A3C',
        boxShadow: '0 6px 20px -10px rgba(15,26,60,0.15)',
      };

  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
      <button
        type="button"
        onClick={handleDownload}
        disabled={loading}
        data-testid={testid || `pdf-preview-btn-${product}`}
        style={style}
        onMouseEnter={(e) => {
          if (loading) return;
          e.currentTarget.style.background = variant === 'ghost' ? 'rgba(143,110,36,0.10)' : '#F7F5F0';
          e.currentTarget.style.transform = 'translateY(-1px)';
        }}
        onMouseLeave={(e) => {
          if (loading) return;
          e.currentTarget.style.background = variant === 'ghost' ? 'transparent' : '#FFFFFF';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        {loading ? (
          <>
            <Loader2 style={{ width: 15, height: 15 }} className="animate-spin" strokeWidth={2} />
            <span>Génération…</span>
          </>
        ) : (
          <>
            <BookOpen style={{ width: 15, height: 15 }} strokeWidth={1.8} />
            <span>Aperçu 3 pages gratuit</span>
          </>
        )}
      </button>
      <p
        style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 11,
          color: 'rgba(15,26,60,0.72)',
          margin: 0,
          textAlign: 'center',
        }}
      >
        Couverture, sommaire et extrait — sans engagement
      </p>
      {error && (
        <p
          role="alert"
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 11,
            color: '#B0533F',
            margin: 0,
          }}
        >
          {error}
        </p>
      )}
    </div>
  );
}
