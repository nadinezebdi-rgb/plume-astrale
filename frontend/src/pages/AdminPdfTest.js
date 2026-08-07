import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { FileText, ExternalLink, Loader2, RefreshCw, User, Users, ShieldAlert } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import { useAuth } from '@/context/AuthContext';

/**
 * /admin/pdf-test — dashboard admin pour prévisualiser chaque PDF prestige
 * avec des données factices. Objectif : vérifier le rendu (dorure du prénom,
 * sommaire numéroté, couverture illustrée) avant d'aller en imprimerie.
 *
 * Aucune persistance : chaque clic régénère le PDF côté backend et l'ouvre
 * dans un nouvel onglet.
 */
const PRODUCTS = [
  { key: 'astrocartographie', name: 'Astrocartographie',   desc: 'Sommaire à double-passe + carte du monde + villes' },
  { key: 'kabbale',           name: "Arbre de Vie (Kabbale)", desc: 'Sommaire I-VII + 10 séphiroth + 22 chemins' },
  { key: 'karma-destin',      name: 'Karma & Destin',       desc: 'Sommaire I-VII + nœuds + Saturne/Chiron/Pluton' },
  { key: 'numerologie',       name: 'Numérologie',          desc: 'Sommaire I-VI + nombres-clés + année perso' },
  { key: 'theme-natal',       name: 'Thème Natal',          desc: 'Cover Playfair + planètes + aspects' },
  { key: 'synastrie',         name: 'Synastrie',            desc: 'Double prénom en dorure + 25 pages cream' },
];

export default function AdminPdfTest() {
  const { user, session, loading: authLoading } = useAuth();
  const isAdmin = user?.is_admin || user?.role === 'admin' || user?.email === 'admin@plume-astrale.fr';
  const [firstName, setFirstName] = useState('Léa');
  const [partnerName, setPartnerName] = useState('Adrien');
  const [loading, setLoading] = useState(null);
  const [errMsg, setErrMsg] = useState(null);

  const backend = process.env.REACT_APP_BACKEND_URL;

  // ─── Gate : chargement / non-authent / non-admin ───
  if (authLoading) {
    return (
      <PsPageShell background="light">
        <div style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Loader2 style={{ width: 22, height: 22, color: '#C9A24B' }} className="animate-spin" />
        </div>
      </PsPageShell>
    );
  }
  if (!user) {
    return <Navigate to={`/connexion?redirect=${encodeURIComponent('/admin/pdf-test')}`} replace />;
  }
  if (!isAdmin) {
    return (
      <PsPageShell background="light">
        <section
          data-testid="admin-pdf-test-denied"
          style={{
            padding: '120px 24px 60px',
            maxWidth: 640,
            margin: '0 auto',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              display: 'inline-flex',
              width: 60, height: 60,
              alignItems: 'center', justifyContent: 'center',
              borderRadius: 999,
              background: 'rgba(176,83,63,0.10)',
              border: '1px solid rgba(176,83,63,0.30)',
              marginBottom: 24,
            }}
          >
            <ShieldAlert style={{ width: 26, height: 26, color: '#B0533F' }} strokeWidth={1.6} />
          </div>
          <h1 style={{ fontFamily: 'Playfair Display, serif', fontSize: 32, color: '#0F1A3C', fontWeight: 500, marginBottom: 12 }}>
            Accès réservé aux administrateurs
          </h1>
          <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 15, color: 'rgba(15,26,60,0.65)' }}>
            Ce dashboard est un outil interne de vérification des rapports imprimés.
            Contacte l&apos;équipe Plume Astrale si tu penses devoir y accéder.
          </p>
        </section>
      </PsPageShell>
    );
  }

  const token = session?.access_token || null;

  const buildUrl = (product, download = false) => {
    const params = new URLSearchParams({
      first_name: firstName || 'Léa',
      ...(product === 'synastrie' && partnerName ? { partner_name: partnerName } : {}),
      ...(download ? { download: 'true' } : {}),
    });
    return `${backend}/api/admin/pdf-test/${product}?${params.toString()}`;
  };

  const handleOpen = async (product, download = false) => {
    setLoading(product);
    setErrMsg(null);
    try {
      // Auth-protected endpoint : on récupère le PDF via fetch avec Bearer, puis blob → new tab
      const res = await fetch(buildUrl(product, download), {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.status === 401 || res.status === 403) {
        setErrMsg("Session expirée ou droits insuffisants. Reconnecte-toi.");
        return;
      }
      if (!res.ok) {
        setErrMsg(`Génération impossible (HTTP ${res.status}).`);
        return;
      }
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const win = window.open(blobUrl, '_blank', 'noopener');
      if (download && win) {
        // Force download name via anchor
        setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000);
      }
    } catch (e) {
      setErrMsg("Erreur réseau. Vérifie ta connexion.");
    } finally {
      setTimeout(() => setLoading(null), 900);
    }
  };

  return (
    <PsPageShell background="light">
      <section
        data-testid="admin-pdf-test-hero"
        style={{
          padding: '96px 24px 48px',
          maxWidth: 980,
          margin: '0 auto',
        }}
      >
        <p className="ps-eyebrow" style={{ color: '#B0533F', marginBottom: 10 }}>
          Admin · Interne
        </p>
        <h1
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(30px, 5vw, 42px)',
            color: '#0F1A3C',
            fontWeight: 500,
            lineHeight: 1.15,
            marginBottom: 12,
          }}
        >
          Prévisualisation <span style={{ fontStyle: 'italic', color: '#C9A24B' }}>des livres imprimés</span>
        </h1>
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 15,
            lineHeight: 1.65,
            color: 'rgba(15,26,60,0.75)',
            marginBottom: 32,
          }}
        >
          Génère un PDF complet de chaque rapport avec des données factices, pour vérifier
          la dorure du prénom, le sommaire numéroté, les couvertures illustrées et
          la mise en page avant impression.
        </p>

        {/* ═══ Formulaire prénom ═══ */}
        <div
          style={{
            background: '#FFFFFF',
            border: '1px solid #E3E1DC',
            borderRadius: 14,
            padding: 24,
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 20,
            marginBottom: 40,
          }}
        >
          <label style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <span
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                color: 'rgba(15,26,60,0.55)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <User style={{ width: 12, height: 12 }} strokeWidth={2} />
              Prénom (destinataire)
            </span>
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              data-testid="admin-pdf-test-firstname"
              style={{
                padding: '10px 14px',
                fontFamily: 'Inter, sans-serif',
                fontSize: 14,
                color: '#0F1A3C',
                background: '#F7F5F0',
                border: '1px solid #E3E1DC',
                borderRadius: 8,
                outline: 'none',
              }}
              placeholder="Léa"
            />
          </label>

          <label style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <span
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                color: 'rgba(15,26,60,0.55)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <Users style={{ width: 12, height: 12 }} strokeWidth={2} />
              Partenaire (synastrie)
            </span>
            <input
              type="text"
              value={partnerName}
              onChange={(e) => setPartnerName(e.target.value)}
              data-testid="admin-pdf-test-partner"
              style={{
                padding: '10px 14px',
                fontFamily: 'Inter, sans-serif',
                fontSize: 14,
                color: '#0F1A3C',
                background: '#F7F5F0',
                border: '1px solid #E3E1DC',
                borderRadius: 8,
                outline: 'none',
              }}
              placeholder="Adrien"
            />
          </label>
        </div>
      </section>

      {/* ═══ Grille des 6 produits ═══ */}
      <section
        style={{
          padding: '0 24px 96px',
          maxWidth: 980,
          margin: '0 auto',
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 20,
          }}
        >
          {PRODUCTS.map((p) => (
            <article
              key={p.key}
              data-testid={`admin-pdf-test-card-${p.key}`}
              style={{
                background: '#FFFFFF',
                border: '1px solid #E3E1DC',
                borderRadius: 14,
                padding: 22,
                display: 'flex',
                flexDirection: 'column',
                gap: 14,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: 8,
                    background: 'rgba(201,162,75,0.12)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <FileText style={{ width: 16, height: 16, color: '#C9A24B' }} strokeWidth={1.8} />
                </div>
                <h3
                  style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 19,
                    fontWeight: 500,
                    color: '#0F1A3C',
                    lineHeight: 1.25,
                    margin: 0,
                  }}
                >
                  {p.name}
                </h3>
              </div>
              <p
                style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 12.5,
                  lineHeight: 1.55,
                  color: 'rgba(15,26,60,0.65)',
                  margin: 0,
                  flexGrow: 1,
                }}
              >
                {p.desc}
              </p>

              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => handleOpen(p.key, false)}
                  disabled={loading === p.key}
                  data-testid={`admin-pdf-test-open-${p.key}`}
                  style={{
                    flex: 1,
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 6,
                    padding: '10px 12px',
                    borderRadius: 8,
                    background: '#0F1A3C',
                    color: '#F7F5F0',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 12,
                    fontWeight: 600,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    border: 'none',
                    cursor: loading === p.key ? 'wait' : 'pointer',
                    transition: 'transform 0.2s',
                  }}
                >
                  {loading === p.key ? (
                    <Loader2 style={{ width: 13, height: 13 }} className="animate-spin" strokeWidth={2} />
                  ) : (
                    <ExternalLink style={{ width: 13, height: 13 }} strokeWidth={2} />
                  )}
                  Ouvrir
                </button>
                <button
                  type="button"
                  onClick={() => handleOpen(p.key, true)}
                  disabled={loading === p.key}
                  data-testid={`admin-pdf-test-download-${p.key}`}
                  style={{
                    padding: '10px 12px',
                    borderRadius: 8,
                    background: 'transparent',
                    color: '#0F1A3C',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 12,
                    fontWeight: 600,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    border: '1px solid #E3E1DC',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                  }}
                  title="Télécharger le PDF"
                >
                  <RefreshCw style={{ width: 12, height: 12 }} strokeWidth={2} />
                  DL
                </button>
              </div>
            </article>
          ))}
        </div>

        <div
          style={{
            marginTop: 40,
            padding: 24,
            background: 'rgba(176,83,63,0.08)',
            border: '1px solid rgba(176,83,63,0.25)',
            borderRadius: 14,
          }}
        >
          <p
            style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 12,
              lineHeight: 1.6,
              color: 'rgba(15,26,60,0.75)',
              margin: 0,
            }}
          >
            <strong style={{ color: '#B0533F' }}>Note interne :</strong> les PDF sont générés à la volée
            (pas de cache) pour refléter les changements de code en direct. Aucun crédit n&apos;est débité.
            Cette page est protégée par is_admin — un utilisateur non-admin est redirigé.
          </p>
        </div>

        {errMsg && (
          <div
            role="alert"
            data-testid="admin-pdf-test-error"
            style={{
              marginTop: 16,
              padding: '12px 16px',
              background: 'rgba(176,83,63,0.10)',
              border: '1px solid rgba(176,83,63,0.35)',
              borderRadius: 10,
              fontFamily: 'Inter, sans-serif',
              fontSize: 13,
              color: '#B0533F',
              textAlign: 'center',
            }}
          >
            {errMsg}
          </div>
        )}
      </section>
    </PsPageShell>
  );
}
