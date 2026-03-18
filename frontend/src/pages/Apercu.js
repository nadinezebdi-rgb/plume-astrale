import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Loader2, Lock, Tag } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PdfPreview = ({ userData }) => {
  const [previews, setPreviews] = useState([]);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userData) return;
    const fetchPreviews = async () => {
      try {
        const res = await fetch(`${API_URL}/api/pdf/preview`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_data: userData }),
        });
        const data = await res.json();
        setPreviews(data.previews || []);
        setTotalPages(data.total_pages || 0);
      } catch (e) {
        console.error('Preview error:', e);
      }
      setLoading(false);
    };
    fetchPreviews();
  }, [userData]);

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 className="w-5 h-5 animate-spin" style={{ color: 'var(--pa-accent)' }} />
      </div>
    );
  }

  if (previews.length === 0) return null;

  return (
    <div data-testid="pdf-preview-section">
      <p className="text-xs tracking-widest uppercase text-center mb-6" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
        Aper&ccedil;u de votre manuscrit — {totalPages} pages
      </p>
      <div className="flex gap-3 justify-center overflow-x-auto pb-4">
        {previews.map((src, i) => (
          <div key={i} className="relative flex-shrink-0">
            <img
              src={src}
              alt={`Page ${i + 1}`}
              className="w-36 md:w-44 rounded-sm"
              style={{ border: '1px solid var(--pa-divider)' }}
              data-testid={`pdf-preview-page-${i}`}
            />
            {i === previews.length - 1 && (
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#1A1050] rounded-sm" />
            )}
          </div>
        ))}
        <div className="relative flex-shrink-0 w-36 md:w-44 rounded-sm flex items-center justify-center"
             style={{ border: '1px dashed var(--pa-divider)', minHeight: '220px' }}>
          <div className="text-center p-4">
            <Lock className="w-5 h-5 mx-auto mb-2" style={{ color: 'var(--pa-muted)' }} strokeWidth={1} />
            <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>+{totalPages - previews.length} pages</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const Apercu = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [cheminVie, setCheminVie] = useState(0);
  const [anneePersonnelle, setAnneePersonnelle] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [showDiscountInput, setShowDiscountInput] = useState(false);
  const [discountCode, setDiscountCode] = useState('');
  const [discountError, setDiscountError] = useState('');
  const [discountSuccess, setDiscountSuccess] = useState('');

  const handleApplyDiscount = async () => {
    if (!discountCode.trim()) { setDiscountError('Veuillez entrer un code'); return; }
    setIsLoading(true);
    setDiscountError('');
    setDiscountSuccess('');
    try {
      const validateResponse = await fetch(`${API_URL}/api/discount/validate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: discountCode })
      });
      const validateData = await validateResponse.json();
      if (!validateData.valid) { setDiscountError(validateData.message); setIsLoading(false); return; }
      if (validateData.discount_percent === 100) {
        const accessResponse = await fetch(`${API_URL}/api/access/free`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: 'manuscrit', origin_url: window.location.origin, user_email: userData?.email, user_data: userData, discount_code: discountCode })
        });
        const accessData = await accessResponse.json();
        if (accessData.success) {
          localStorage.setItem('plume_astrale_paid', 'true');
          localStorage.setItem('plume_astrale_plan', 'manuscrit');
          localStorage.setItem('plume_astrale_payment_date', new Date().toISOString());
          setDiscountSuccess('Acces accorde ! Redirection...');
          setTimeout(() => navigate('/resultats'), 1500);
        } else { setDiscountError('Erreur lors de l\'activation'); }
      }
    } catch (error) { setDiscountError('Une erreur est survenue'); }
    setIsLoading(false);
  };

  const handlePurchase = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/checkout/create`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: 'manuscrit', origin_url: window.location.origin, user_email: userData?.email, user_data: userData })
      });
      const data = await response.json();
      if (data.url) { window.location.href = data.url; }
    } catch (error) {
      console.error('Payment error:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (!data) { navigate('/formulaire'); return; }
    const parsedData = JSON.parse(data);
    setUserData(parsedData);
    const dateNaissance = new Date(parsedData.dateNaissance);
    setCheminVie(calculerCheminVie(dateNaissance));
    setAnneePersonnelle(calculerAnneePersonnelle(dateNaissance));
  }, [navigate]);

  const calculerCheminVie = (date) => {
    let somme = date.getDate() + (date.getMonth() + 1) + date.getFullYear();
    while (somme > 9 && somme !== 11 && somme !== 22 && somme !== 33) {
      somme = somme.toString().split('').reduce((acc, d) => acc + parseInt(d), 0);
    }
    return somme;
  };

  const calculerAnneePersonnelle = (dateNaissance) => {
    let somme = dateNaissance.getDate() + (dateNaissance.getMonth() + 1) + new Date().getFullYear();
    while (somme > 9) { somme = somme.toString().split('').reduce((acc, d) => acc + parseInt(d), 0); }
    return somme;
  };

  const getCheminVieInfo = (chemin) => {
    const i = {
      1: { titre: "Le Pionnier", apercu: "Vous \u00eates n\u00e9(e) pour diriger et innover. Votre \u00e9nergie naturelle vous pousse vers l'ind\u00e9pendance et la cr\u00e9ation de nouveaux chemins." },
      2: { titre: "Le Diplomate", apercu: "Votre don pour l'harmonie fait de vous un mediateur naturel. Sensibilite et cooperation sont vos forces." },
      3: { titre: "L'Artiste", apercu: "Creativite et communication sont vos forces. Vous inspirez les autres par votre joie de vivre." },
      4: { titre: "Le Batisseur", apercu: "Stabilite et methode caracterisent votre approche. Vous construisez des fondations solides." },
      5: { titre: "L'Aventurier", apercu: "Liberté et changement nourrissent votre ame. Vous êtes fait(e) pour explorer de nouveaux horizons." },
      6: { titre: "Le Guérisseur", apercu: "Amour et service aux autres définissent votre essence. Vous êtes un pilier de soutien." },
      7: { titre: "Le Sage", apercu: "Recherche spirituelle et analyse profonde vous caracterisent. Vous cherchez la verite." },
      8: { titre: "Le Leader", apercu: "Ambition et reussite materielle vous motivent. Vous transformez les idees en succes." },
      9: { titre: "L'Humanitaire", apercu: "Compassion universelle et service a l'humanite vous animent." },
      11: { titre: "L'Inspirateur", apercu: "Intuition et inspiration vous connectent aux dimensions superieures." },
      22: { titre: "Le Maitre Batisseur", apercu: "Vision et realisation se conjuguent en vous." },
      33: { titre: "Le Maitre Guerisseur", apercu: "Amour inconditionnel et sagesse universelle emanent de vous." }
    };
    return i[chemin] || i[1];
  };

  const getAnneePersonnelleInfo = (annee) => {
    const i = {
      1: { titre: "Nouveaux Departs", apercu: "2026 marque un nouveau cycle. C'est le moment d'initier des projets majeurs." },
      2: { titre: "Cooperation", apercu: "Cette annee favorise les partenariats. Patience et diplomatie sont vos atouts." },
      3: { titre: "Creativite", apercu: "Votre creativite s'epanouit. Expression et communication sont favorisees." },
      4: { titre: "Construction", apercu: "Travail et organisation sont a l'honneur. Posez des bases solides." },
      5: { titre: "Liberte", apercu: "Changements et nouvelles experiences vous attendent." },
      6: { titre: "Responsabilite", apercu: "Famille et responsabilites sont au centre." },
      7: { titre: "Reflexion", apercu: "Introspection et developpement spirituel sont favorises." },
      8: { titre: "Reussite", apercu: "Succes materiel et reconnaissance sont a portee." },
      9: { titre: "Accomplissement", apercu: "Fin d'un cycle. C'est le moment de partager vos acquis." }
    };
    return i[annee] || i[1];
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-5 h-5 animate-spin" style={{ color: 'var(--pa-accent)' }} />
      </div>
    );
  }

  const cheminVieInfo = getCheminVieInfo(cheminVie);
  const anneePersonnelleInfo = getAnneePersonnelleInfo(anneePersonnelle);

  return (
    <div className="min-h-screen relative">
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="mb-16">
          <p className="section-label">Votre apercu</p>
          <h1
            className="text-3xl md:text-5xl mb-4"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
          >
            {userData.prenom ? `${userData.prenom}, ` : ''}les etoiles vous parlent.
          </h1>
          <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
            Découvrez les premiers secrets de votre destinée
          </p>
        </div>

        {/* Chemin de Vie */}
        <div className="mb-16" data-testid="chemin-vie-card">
          <div className="flex items-baseline gap-4 mb-6">
            <span className="text-5xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              {cheminVie}
            </span>
            <div>
              <p className="text-xs tracking-widest uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                Chemin de Vie
              </p>
              <p className="text-sm mt-1" style={{ color: 'var(--pa-heading)' }}>{cheminVieInfo.titre}</p>
            </div>
          </div>
          <p className="text-sm leading-relaxed mb-6" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            {cheminVieInfo.apercu}
          </p>
          <div className="flex items-start gap-3 py-4 px-5 rounded-sm" style={{ background: 'var(--pa-glass)', border: '1px solid var(--pa-divider)' }}>
            <Lock className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: 'var(--pa-muted)' }} strokeWidth={1} />
            <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
              <span style={{ color: 'var(--pa-body)' }}>Dans l'etude complete :</span> Dons naturels, défis principaux, mission de vie detaillee, conseils d'evolution...
            </p>
          </div>
        </div>

        {/* Annee Personnelle */}
        <div className="mb-16" data-testid="annee-personnelle-card">
          <div className="flex items-baseline gap-4 mb-6">
            <span className="text-5xl" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              {anneePersonnelle}
            </span>
            <div>
              <p className="text-xs tracking-widest uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                Annee Personnelle 2026
              </p>
              <p className="text-sm mt-1" style={{ color: 'var(--pa-heading)' }}>{anneePersonnelleInfo.titre}</p>
            </div>
          </div>
          <p className="text-sm leading-relaxed mb-6" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
            {anneePersonnelleInfo.apercu}
          </p>
          <div className="flex items-start gap-3 py-4 px-5 rounded-sm" style={{ background: 'var(--pa-glass)', border: '1px solid var(--pa-divider)' }}>
            <Lock className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: 'var(--pa-muted)' }} strokeWidth={1} />
            <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
              <span style={{ color: 'var(--pa-body)' }}>Dans l'etude complete :</span> Conseils mois par mois, periodes favorables, défis a anticiper...
            </p>
          </div>
        </div>

        {/* Locked sections */}
        <div className="mb-16">
          <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>
            Contenu verrouille
          </p>
          <div className="grid grid-cols-2 gap-4">
            {['Identite Celeste', 'Coeur & Relations', 'Defis & Talents', 'Conseil de la Plume'].map((title, i) => (
              <div key={i} className="py-5 px-4 text-center rounded-sm" style={{ border: '1px solid var(--pa-divider)', background: 'var(--pa-glass)' }} data-testid={`locked-section-${i}`}>
                <Lock className="w-4 h-4 mx-auto mb-2" style={{ color: 'var(--pa-muted)' }} strokeWidth={1} />
                <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>{title}</p>
              </div>
            ))}
          </div>
        </div>

        {/* PDF Preview */}
        <div className="mb-16">
          <PdfPreview userData={userData} />
        </div>

        <div className="divider-subtle" />

        {/* CTA Manuscrit */}
        <div className="text-center py-8">
          <h2
            className="text-2xl md:text-3xl mb-4"
            style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
          >
            Le Manuscrit de la Plume
          </h2>
          <p className="text-sm mb-3 max-w-md mx-auto" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
            Un tresor celeste a conserver precieusement toute votre vie.
          </p>
          <p className="text-sm mb-10 max-w-md mx-auto" style={{ color: 'var(--pa-muted)', lineHeight: '1.9' }}>
            Ce manuscrit unique deviendra votre guide spirituel personnel.
          </p>

          <div className="mb-10 py-6" style={{ borderTop: '1px solid var(--pa-divider)', borderBottom: '1px solid var(--pa-divider)' }}>
            <div className="text-4xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              29,90 EUR
            </div>
            <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
              Acces immediat, PDF telechargeable
            </p>
          </div>

          <button
            onClick={handlePurchase}
            disabled={isLoading}
            className="btn-editorial-filled mx-auto mb-6 disabled:opacity-50"
            data-testid="cta-unlock-full"
          >
            {isLoading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Redirection...</>
            ) : (
              <>Recevoir mon manuscrit</>
            )}
          </button>

          {/* Discount */}
          <div className="mt-6">
            {!showDiscountInput ? (
              <button onClick={() => setShowDiscountInput(true)}
                className="text-xs transition-colors duration-300 hover:text-[#C5A059]" style={{ color: 'var(--pa-muted)' }}
                data-testid="btn-show-discount">
                <Tag className="w-3 h-3 inline mr-1" strokeWidth={1} /> J'ai un code de reduction
              </button>
            ) : (
              <div className="max-w-sm mx-auto space-y-2">
                <div className="flex gap-2">
                  <input type="text" value={discountCode}
                    onChange={(e) => { setDiscountCode(e.target.value.toUpperCase()); setDiscountError(''); }}
                    placeholder="Code promo" className="input-boxed flex-1 text-center text-sm"
                    data-testid="input-discount-code" />
                  <button onClick={handleApplyDiscount} disabled={isLoading}
                    className="btn-editorial text-xs px-5 py-2 disabled:opacity-50"
                    data-testid="btn-apply-discount">
                    {isLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Appliquer'}
                  </button>
                </div>
                {discountError && <p className="text-red-400/70 text-xs">{discountError}</p>}
                {discountSuccess && <p className="text-emerald-400 text-xs">{discountSuccess}</p>}
              </div>
            )}
          </div>
        </div>
      </div>
      </div>
    </div>
  );
};

export default Apercu;
