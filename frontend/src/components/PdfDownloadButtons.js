import React, { useMemo } from 'react';
import { Download, Printer } from 'lucide-react';

/**
 * PdfDownloadButtons — duo de boutons de téléchargement PDF :
 *   1. Standard (lecture écran, taille optimisée)
 *   2. Version imprimeur (BleedBox/TrimBox 3mm de fond perdu, prêt pour offset)
 *
 * Reçoit une URL type `/api/pdf/download?session_id=X&token=Y` ou une URL
 * complète (Supabase). Si l'URL est du domaine Emergent, on ajoute `&print_ready=1`
 * pour la version imprimeur. Sinon (Supabase, statique), on masque le second bouton.
 *
 * Props :
 *   - pdfUrl (string, required) : URL du PDF standard
 *   - apiBase (string, optional) : REACT_APP_BACKEND_URL pour préfixer les paths relatifs
 *   - label (string, optional) : texte du bouton principal (par défaut "Télécharger le PDF")
 *   - testidPrefix (string, optional) : préfixe des data-testid (par défaut "pdf-dl")
 */
export default function PdfDownloadButtons({
  pdfUrl,
  apiBase = '',
  label = 'Télécharger le PDF',
  testidPrefix = 'pdf-dl',
}) {
  const { fullUrl, printReadyUrl } = useMemo(() => {
    if (!pdfUrl) return { fullUrl: null, printReadyUrl: null };
    // Normalise : absolu ou relatif
    const isAbsolute = /^https?:\/\//i.test(pdfUrl);
    const abs = isAbsolute ? pdfUrl : `${apiBase}${pdfUrl}`;
    // Le flag print_ready n'est utile que sur /api/pdf/download (Emergent backend).
    // On skip pour les URLs Supabase Storage et les liens statiques legacy.
    if (!abs.includes('/api/pdf/download')) {
      return { fullUrl: abs, printReadyUrl: null };
    }
    const sep = abs.includes('?') ? '&' : '?';
    return { fullUrl: abs, printReadyUrl: `${abs}${sep}print_ready=1` };
  }, [pdfUrl, apiBase]);

  if (!fullUrl) return null;

  return (
    <div
      className="pdf-download-buttons"
      data-testid={`${testidPrefix}-buttons`}
      style={{
        display: 'flex',
        gap: 12,
        flexWrap: 'wrap',
        justifyContent: 'center',
        alignItems: 'stretch',
      }}
    >
      <a
        href={fullUrl}
        className="plume-btn-primary inline-flex"
        data-testid={`${testidPrefix}-standard-btn`}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          padding: '12px 22px',
          textDecoration: 'none',
        }}
      >
        <Download className="w-4 h-4" strokeWidth={1.5} />
        {label}
      </a>

      {printReadyUrl && (
        <a
          href={printReadyUrl}
          className="plume-btn-secondary inline-flex"
          data-testid={`${testidPrefix}-print-ready-btn`}
          title="PDF avec bord perdu 3 mm et TrimBox pour envoyer à l'imprimeur"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '12px 22px',
            textDecoration: 'none',
            background: 'transparent',
            color: '#D4AF37',
            border: '1px solid rgba(212, 175, 55, 0.55)',
            borderRadius: 6,
            fontFamily: '"Cinzel", serif',
            fontSize: '0.82rem',
            letterSpacing: 2,
            transition: 'background 200ms ease, border-color 200ms ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(212, 175, 55, 0.12)';
            e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.85)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.borderColor = 'rgba(212, 175, 55, 0.55)';
          }}
        >
          <Printer className="w-4 h-4" strokeWidth={1.5} />
          VERSION IMPRIMEUR
          <span
            style={{
              fontSize: '0.65rem',
              opacity: 0.7,
              letterSpacing: 1,
              marginLeft: 4,
            }}
          >
            (bord perdu 3 mm)
          </span>
        </a>
      )}
    </div>
  );
}
