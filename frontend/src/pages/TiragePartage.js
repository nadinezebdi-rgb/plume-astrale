import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, Moon, Sun, ArrowRight, Eye, Heart, Share2, Download, Mail, Smartphone } from 'lucide-react';
import { asset } from '../lib/assets';
import LibraryImage from '@/components/LibraryImage';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const DOMAINE_LABELS = {
  amour: 'Amour & Relations',
  travail: 'Carrière & Travail',
  argent: 'Finances & Abondance',
  sante: 'Santé & Bien-être',
  spirituel: 'Spiritualité',
  general: 'Question Générale',
};

const TYPE_LABELS = {
  marseille: 'Tirage Marseille · 3 cartes',
  celtique: 'Croix Celtique · 10 cartes',
  complet: 'Tirage Complet 78 arcanes',
};

export default function TiragePartage() {
  const { shareId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tirage, setTirage] = useState(null);
  const [copied, setCopied] = useState(false);
  const [pngLoading, setPngLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/tarot/shared/${shareId}`);
        if (!res.ok) {
          const detail = await res.json().catch(() => ({}));
          throw new Error(detail.detail || 'Tirage introuvable ou expiré');
        }
        const data = await res.json();
        if (!cancelled) setTirage(data);
      } catch (e) {
        if (!cancelled) setError(e.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [shareId]);

  const copyLink = async () => {
    // On copie l'URL OG (/api/og/tirage/{id}) plutôt que /tirage-partage/{id}
    // directement : les crawlers WhatsApp/iMessage/Discord liront les meta OG
    // et afficheront la carte PNG en grand dans le preview, puis les humains
    // seront redirigés vers la page React normale.
    const ogUrl = `${window.location.origin}/api/og/tirage/${shareId}`;
    try {
      await navigator.clipboard.writeText(ogUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2200);
    } catch (_) { /* clipboard denied */ }
  };

  const downloadCard = async (fmt = 'post') => {
    setPngLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/tarot/shared/${shareId}/card.png?format=${fmt}`);
      if (!res.ok) throw new Error('PNG unavailable');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const suffix = fmt === 'story' ? '-story' : '';
      a.download = `tirage-${(tirage?.first_name || 'plume').toLowerCase()}${suffix}.png`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
      alert("Impossible de générer la carte pour le moment. Réessayez.");
    } finally {
      setPngLoading(false);
    }
  };

  const sendByEmail = () => {
    const firstName = tirage?.first_name || 'un(e) ami(e)';
    const typeLabel = TYPE_LABELS[tirage?.type] || 'tirage de tarot';
    const q = tirage?.question ? `\n\n« ${tirage.question} »` : '';
    const ogUrl = `${window.location.origin}/api/og/tirage/${shareId}`;
    const subject = encodeURIComponent(`Le tirage de ${firstName} · Plume Astrale`);
    const body = encodeURIComponent(
      `Je t'envoie mon ${typeLabel.toLowerCase()} :` +
      `${q}\n\n` +
      `Les arcanes ont parlé — regarde ce qu'ils m'ont dit :\n${ogUrl}\n\n` +
      `✦ Plume Astrale`
    );
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  if (loading) {
    return (
      <PsPageShell>
        <SEO path={location.pathname} title="Chargement du tirage · Plume Astrale" description="Un tirage de tarot personnel partagé." noindex />
        <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-6">
          <div className="w-10 h-10 border-2 border-[#C9A24B] border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-[#232323]/70 font-light">Chargement du tirage…</p>
        </div>
      </PsPageShell>
    );
  }

  if (error || !tirage) {
    return (
      <PsPageShell>
        <SEO path={location.pathname} title="Tirage introuvable · Plume Astrale" description="Ce lien de partage est expiré ou invalide." noindex />
        <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-6" data-testid="shared-tirage-404">
          <Sparkles className="w-10 h-10 text-[#C9A24B] mb-5" strokeWidth={1} />
          <h1 className="text-2xl mb-3" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
            Ce tirage n'est plus disponible
          </h1>
          <p className="text-[#232323]/70 font-light max-w-md mb-8">
            Le lien a peut-être expiré ou été supprimé. Mais vous pouvez tirer les cartes pour vous — c'est encore mieux.
          </p>
          <button
            onClick={() => navigate('/services/tarot')}
            className="btn-mystical-filled rounded-xl py-3 px-8 flex items-center gap-2"
            data-testid="shared-404-cta"
          >
            Faire mon propre tirage <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </PsPageShell>
    );
  }

  const { data, question, domaine, first_name: firstName, type, view_count: viewCount } = tirage;
  const cartes = data?.cartes || [];
  const synth = data?.synthese || {};
  const typeLabel = TYPE_LABELS[type] || 'Tirage de tarot';
  const domaineLabel = DOMAINE_LABELS[domaine] || 'Question Générale';

  return (
    <PsPageShell>
      <SEO
        path={location.pathname}
        title={`Tirage de ${firstName} · Plume Astrale`}
        description={`Un ${typeLabel.toLowerCase()} personnel partagé par ${firstName}. Les arcanes ont parlé.`}
        noindex
      />

      <div
        className="min-h-screen bg-cover bg-center"
        style={{ backgroundImage: `url('${asset('images/tarot/tarot_cards_2.png')}')` }}
      >
        <div className="min-h-screen bg-gradient-to-b from-[#f0e5cc]/90 via-[#f8f1e3]/85 to-[#f0e5cc]/95">
          <div className="max-w-5xl mx-auto px-5 py-14">

            {/* Header */}
            <div className="text-center mb-10" data-testid="shared-tirage-header">
              <p className="text-[#C9A24B] uppercase tracking-[0.3em] text-[11px] mb-3 font-light">
                ✦ {typeLabel} · {domaineLabel} ✦
              </p>
              <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
                Le tirage de {firstName}
              </h1>
              {question && (
                <p className="text-[#232323]/75 font-light italic max-w-2xl mx-auto">
                  « {question} »
                </p>
              )}
              <div className="flex items-center justify-center gap-2 mt-5 text-xs text-[#232323]/55">
                <Eye className="w-3.5 h-3.5" strokeWidth={1.5} />
                <span>{viewCount || 1} {viewCount > 1 ? 'lectures' : 'lecture'}</span>
              </div>
            </div>

            {/* Cartes */}
            <div className={`grid gap-4 mb-12 ${
              cartes.length <= 3 ? 'md:grid-cols-3' :
              cartes.length <= 5 ? 'grid-cols-2 sm:grid-cols-3 md:grid-cols-5' :
              cartes.length <= 7 ? 'grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7' :
              'grid-cols-2 sm:grid-cols-3 md:grid-cols-5'
            }`}>
              {cartes.map((c, i) => {
                const isRev = (c.orientation || '').toLowerCase() === 'renverse';
                const isMinor = c.is_major === false;
                return (
                  <div key={i} data-testid={`shared-carte-${i}`}
                       className="rounded-xl p-4 bg-white/85 border border-[#C9A24B]/35 shadow-md">
                    <p className="text-[#C9A24B] uppercase tracking-[0.2em] text-[10px] mb-3 font-semibold text-center" style={{ fontFamily: 'Cinzel, serif' }}>
                      {c.position || `Carte ${i + 1}`}
                    </p>
                    <div
                      className="mx-auto mb-3 overflow-hidden rounded-md flex items-center justify-center"
                      style={{
                        width: 110, height: 170,
                        border: `1.5px solid ${isRev ? 'rgba(184,169,232,0.6)' : 'rgba(201,162,75,0.6)'}`,
                        transform: isRev ? 'rotate(180deg)' : 'none',
                        background: isMinor
                          ? `linear-gradient(135deg, ${c.couleur || '#C9A24B'}22, ${c.couleur || '#C9A24B'}08)`
                          : '#0e0a24',
                      }}
                    >
                      {isMinor ? (
                        <div className="text-center px-1">
                          <div className="text-4xl mb-1" style={{ color: c.couleur || '#C9A24B' }}>
                            {c.symbole || '✦'}
                          </div>
                          <div className="text-[10px] uppercase tracking-wider text-[#0F1A3C] font-bold" style={{ fontFamily: 'Cinzel, serif' }}>
                            {c.rang}
                          </div>
                          <div className="text-[10px] text-[#232323]/70">de {c.suite}</div>
                        </div>
                      ) : (
                        <LibraryImage type="tarot" name={c.nom} size={170} alt={c.nom}
                                       style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      )}
                    </div>
                    <h3 className="text-sm text-center mb-1" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
                      {c.nom}
                    </h3>
                    <p className="text-[10px] text-center text-[#232323]/60">
                      {isRev ? <><Moon className="inline w-3 h-3 mr-1" />Renversée</> : <><Sun className="inline w-3 h-3 mr-1" />Droite</>}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Synthèse — fil conducteur si disponible */}
            {(synth.fil_conducteur || synth.tendance_generale) && (
              <div className="rounded-xl p-6 bg-white/85 border border-[#C9A24B]/25 shadow-sm mb-6" data-testid="shared-synthese">
                {synth.tendance_generale && (
                  <h3 className="text-xl mb-3 text-[#C9A24B]" style={{ fontFamily: 'Playfair Display, serif' }}>
                    Tendance : {synth.tendance_generale}
                  </h3>
                )}
                {synth.fil_conducteur && (
                  <p className="text-[#232323]/85 leading-relaxed whitespace-pre-line">
                    {synth.fil_conducteur}
                  </p>
                )}
              </div>
            )}

            {/* Conseil final */}
            {data?.conseil_final && (
              <div className="rounded-xl p-6 bg-gradient-to-br from-[#C9A24B]/15 to-[#C9A24B]/5 border border-[#C9A24B]/40 mb-10" data-testid="shared-conseil">
                <div className="flex items-start gap-4">
                  <Sparkles className="w-7 h-7 text-[#C9A24B] flex-shrink-0 mt-0.5" strokeWidth={1} />
                  <div>
                    <h4 className="text-[#8B6914] text-lg mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>
                      Conseil des Arcanes
                    </h4>
                    <p className="text-[#0F1A3C] whitespace-pre-line leading-relaxed">
                      {data.conseil_final}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* CTA : refaire son propre tirage + reshare */}
            <div className="rounded-2xl p-8 bg-[#0F1A3C] text-center text-[#f0e5cc] mb-6" data-testid="shared-cta">
              <Heart className="w-10 h-10 text-[#C9A24B] mx-auto mb-4" strokeWidth={1} />
              <h3 className="text-2xl mb-3" style={{ fontFamily: 'Playfair Display, serif' }}>
                Et vous, qu'est-ce que les arcanes vous diraient ?
              </h3>
              <p className="text-[#f0e5cc]/75 max-w-xl mx-auto mb-6 text-sm font-light">
                Posez une question, choisissez un tirage, et laissez les 78 arcanes dessiner votre réponse.
                Chaque tirage est personnel, enrichi par l'IA, et exportable en PDF signature.
              </p>
              <div className="flex flex-col sm:flex-row flex-wrap gap-3 justify-center">
                <button
                  onClick={() => navigate('/services/tarot')}
                  className="btn-mystical-filled rounded-xl py-3 px-6 flex items-center gap-2 justify-center"
                  data-testid="shared-cta-tirage"
                >
                  Faire mon tirage <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => downloadCard('post')}
                  disabled={pngLoading}
                  className="rounded-xl py-3 px-5 flex items-center gap-2 justify-center border border-[#C9A24B]/50 text-[#C9A24B] hover:bg-[#C9A24B]/10 transition-colors disabled:opacity-50"
                  data-testid="shared-cta-download-png"
                  title="Format feed Instagram, WhatsApp, iMessage"
                >
                  {pngLoading ? (
                    <div className="w-4 h-4 border-2 border-[#C9A24B] border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Download className="w-4 h-4" />
                  )}
                  Offrir cette carte
                </button>
                <button
                  onClick={() => downloadCard('story')}
                  disabled={pngLoading}
                  className="rounded-xl py-3 px-5 flex items-center gap-2 justify-center border border-[#C9A24B]/50 text-[#C9A24B] hover:bg-[#C9A24B]/10 transition-colors disabled:opacity-50"
                  data-testid="shared-cta-download-story"
                  title="Format 9:16 pour Stories Instagram / TikTok"
                >
                  <Smartphone className="w-4 h-4" />
                  En Story IG
                </button>
                <button
                  onClick={sendByEmail}
                  className="rounded-xl py-3 px-5 flex items-center gap-2 justify-center border border-[#C9A24B]/50 text-[#C9A24B] hover:bg-[#C9A24B]/10 transition-colors"
                  data-testid="shared-cta-email"
                >
                  <Mail className="w-4 h-4" />
                  Envoyer par email
                </button>
                <button
                  onClick={copyLink}
                  className="rounded-xl py-3 px-5 flex items-center gap-2 justify-center border border-[#C9A24B]/50 text-[#C9A24B] hover:bg-[#C9A24B]/10 transition-colors"
                  data-testid="shared-cta-copy"
                >
                  <Share2 className="w-4 h-4" />
                  {copied ? 'Lien copié ✓' : 'Copier le lien'}
                </button>
              </div>
            </div>

            <p className="text-center text-[#232323]/50 text-xs">
              Les tirages partagés expirent après 90 jours · <a className="underline" href="/">Plume Astrale</a>
            </p>
          </div>
        </div>
      </div>
    </PsPageShell>
  );
}
