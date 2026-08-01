import React, { useState } from 'react';
import { ArrowRight, Heart, Calendar, Sparkles, Shield, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import SEO from '@/components/SEO';
import PromoCodeField from '@/components/PromoCodeField';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const FenetreRencontrePDF = () => {
  const navigate = useNavigate();
  const [tab, setTab] = useState('solo'); // solo ou duo
  const [formData, setFormData] = useState({
    email: '',
    firstName: '',
    birthDate: '',
    birthTime: '',
    birthCity: 'Paris',
    birthCountry: 'FR',
    partnerBirthDate: '',
    partnerBirthTime: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [promoState, setPromoState] = useState({ status: 'idle', final_amount: 29, code: '' });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/fenetre-rencontre-avancee/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          birth_date: formData.birthDate,
          birth_time: formData.birthTime,
          first_name: formData.firstName,
          birth_city: formData.birthCity,
          birth_country: formData.birthCountry,
          partner_birth_date: tab === 'duo' ? formData.partnerBirthDate : null,
          partner_birth_time: tab === 'duo' ? formData.partnerBirthTime : null,
          origin_url: window.location.origin,
          promo_code: promoState.status === 'ok' && promoState.code ? promoState.code : undefined,
        }),
      });

      const data = await response.json();
      if (data.url) {
        window.location.href = data.url;
      } else if (data.session_id) {
        navigate(`/fenetre-rencontre/attente?session_id=${data.session_id}`);
      }
    } catch (err) {
      setError('Erreur de connexion. Réessaye dans quelques instants.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async () => {
    try {
      const response = await fetch(`${API_URL}/api/fenetre-rencontre-avancee/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          birth_date: formData.birthDate,
          birth_time: formData.birthTime,
        }),
      });

      const data = await response.json();
      if (data.windows) {
        alert(`Aperçu de tes fenêtres:\n\n${data.windows.map(w => `${w.kind}\n${w.period}`).join('\n\n')}`);
      }
    } catch (err) {
      alert('Erreur lors du calcul');
    }
  };

  return (
    <>
      <SEO
        title="Fenêtres de Rencontre Avancées - Plume Astrale"
        description="Découvre les périodes cosmiques favorables à ta rencontre destinée. Rapport PDF 10 pages avec synastrie optionnelle."
      />

      <div className="min-h-screen bg-gradient-to-b from-[#0C0918] to-[#1A1F2E] text-[#F4E8D2] pt-20 pb-20">
        <div className="max-w-5xl mx-auto px-4">
          {/* Hero */}
          <div className="text-center mb-16">
            <div className="inline-block mb-4 bg-[#D4AF37]/20 px-4 py-2 rounded-full border border-[#D4AF37]/50">
              <span className="text-[#D4AF37] font-semibold text-sm">ASTROLOGIE AMOUREUSE</span>
            </div>

            <h1 className="text-6xl md:text-7xl font-bold text-[#D4AF37] mb-6">
              ✦ Fenêtres de<br />Rencontre ✦
            </h1>

            <p className="text-xl md:text-2xl text-[#E3D7FF] mb-8 leading-relaxed">
              Les périodes cosmiques favorables à ta rencontre destinée.<br />
              <span className="text-[#D4AF37]">Transits • Phases Lunaires • Synchronicité</span>
            </p>

            <div className="inline-block bg-[#1A2035] border-2 border-[#D4AF37] rounded-lg px-8 py-4 mb-8">
              <p className="text-3xl font-bold text-[#D4AF37]">29€</p>
              <p className="text-[#E3D7FF] text-sm">PDF 10 pages • Synastrie optionnelle</p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mb-12 justify-center">
            <button
              onClick={() => setTab('solo')}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                tab === 'solo'
                  ? 'bg-[#D4AF37] text-[#0C0918]'
                  : 'bg-[#1A2035] text-[#E3D7FF] border border-[#D4AF37]/30 hover:border-[#D4AF37]'
              }`}
            >
              Pour Moi Seul(e)
            </button>
            <button
              onClick={() => setTab('duo')}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                tab === 'duo'
                  ? 'bg-[#D4AF37] text-[#0C0918]'
                  : 'bg-[#1A2035] text-[#E3D7FF] border border-[#D4AF37]/30 hover:border-[#D4AF37]'
              }`}
            >
              + Synastrie avec Partenaire
            </button>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            <div className="bg-[#1A2035]/80 border border-[#D4AF37]/40 rounded-lg p-6 hover:border-[#D4AF37]/80 transition">
              <Calendar className="w-10 h-10 text-[#D4AF37] mb-4" />
              <h3 className="font-bold text-[#E3D7FF] mb-2 text-lg">3 Fenêtres Détaillées</h3>
              <p className="text-[#F4E8D2] text-sm">Ouverture • Synchronicité • Destin</p>
            </div>

            <div className="bg-[#1A2035]/80 border border-[#D4AF37]/40 rounded-lg p-6 hover:border-[#D4AF37]/80 transition">
              <Heart className="w-10 h-10 text-[#D4AF37] mb-4" />
              <h3 className="font-bold text-[#E3D7FF] mb-2 text-lg">Conseils d'Activation</h3>
              <p className="text-[#F4E8D2] text-sm">Rituels • Cristaux • Affirmations</p>
            </div>

            <div className="bg-[#1A2035]/80 border border-[#D4AF37]/40 rounded-lg p-6 hover:border-[#D4AF37]/80 transition">
              <Sparkles className="w-10 h-10 text-[#D4AF37] mb-4" />
              <h3 className="font-bold text-[#E3D7FF] mb-2 text-lg">Synastrie (Optionnel)</h3>
              <p className="text-[#F4E8D2] text-sm">Compatibilité + prédictions couple</p>
            </div>
          </div>

          {/* Content */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-16">
            <div>
              <h2 className="text-2xl font-bold text-[#D4AF37] mb-6">À l'Intérieur du Rapport</h2>
              <ul className="space-y-4">
                {[
                  '3 Fenêtres de Rencontre — Dates exactes',
                  'Transits de Vénus & Jupiter — Amour & expansion',
                  'Phases Lunaires — Moment optimal',
                  'Conseils d\'Activation — Comment ouvrir la fenêtre',
                  'Rituels Spécifiques — Chandelle rose, cristaux',
                  'Affirmations Puissantes — À réciter chaque jour',
                  'Synastrie (si duo) — Compatibilité + timing',
                  '10 Pages Poétiques & Cosmiques',
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-[#D4AF37] mt-0.5 flex-shrink-0" />
                    <span className="text-[#F4E8D2]">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-[#1A2035] border border-[#D4AF37]/50 rounded-lg p-8 flex flex-col justify-center">
              <h3 className="text-[#D4AF37] text-sm font-bold uppercase tracking-wider mb-4">Comment Ça Marche</h3>
              <p className="text-[#F4E8D2] leading-relaxed mb-4">
                Une fenêtre de rencontre est un period où l'univers aligné les énergies pour faciliter ta rencontre destinée.
              </p>
              <p className="text-[#E3D7FF] leading-relaxed">
                Tes transits personnels + phases lunaires = les moments parfaits pour rayonner ta meilleure énergie.
              </p>
            </div>
          </div>

          {/* Form */}
          <div className="bg-gradient-to-b from-[#1A2035] to-[#111625] border border-[#D4AF37]/50 rounded-lg p-8 md:p-12">
            <h2 className="text-3xl font-bold text-[#D4AF37] mb-8 text-center">
              {tab === 'solo' ? 'Calcule Tes Fenêtres' : 'Calcule Ta Synastrie'}
            </h2>

            <form onSubmit={handleCheckout} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-[#E3D7FF] mb-2 font-semibold">Prénom *</label>
                  <input
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleChange}
                    required
                    className="w-full bg-[#0C0918] border border-[#D4AF37]/30 rounded px-4 py-3 text-[#F4E8D2] placeholder-[#9089B5] focus:border-[#D4AF37] focus:outline-none transition"
                    placeholder="Jean"
                  />
                </div>
                <div>
                  <label className="block text-[#E3D7FF] mb-2 font-semibold">Adresse e-mail *</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full bg-[#0C0918] border border-[#D4AF37]/30 rounded px-4 py-3 text-[#F4E8D2] placeholder-[#9089B5] focus:border-[#D4AF37] focus:outline-none transition"
                    placeholder="toi@exemple.com"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-[#E3D7FF] mb-2 font-semibold">Date de naissance *</label>
                  <input
                    type="date"
                    name="birthDate"
                    value={formData.birthDate}
                    onChange={handleChange}
                    required
                    className="w-full bg-[#0C0918] border border-[#D4AF37]/30 rounded px-4 py-3 text-[#F4E8D2] focus:border-[#D4AF37] focus:outline-none transition"
                  />
                </div>
                <div>
                  <label className="block text-[#E3D7FF] mb-2 font-semibold">Heure de naissance *</label>
                  <input
                    type="time"
                    name="birthTime"
                    value={formData.birthTime}
                    onChange={handleChange}
                    required
                    className="w-full bg-[#0C0918] border border-[#D4AF37]/30 rounded px-4 py-3 text-[#F4E8D2] focus:border-[#D4AF37] focus:outline-none transition"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-[#E3D7FF] mb-2 font-semibold">Ville</label>
                  <input
                    type="text"
                    name="birthCity"
                    value={formData.birthCity}
                    onChange={handleChange}
                    className="w-full bg-[#0C0918] border border-[#D4AF37]/30 rounded px-4 py-3 text-[#F4E8D2] placeholder-[#9089B5] focus:border-[#D4AF37] focus:outline-none transition"
                    placeholder="Paris"
                  />
                </div>
                <div>
                  <label className="block text-[#E3D7FF] mb-2 font-semibold">Pays</label>
                  <select
                    name="birthCountry"
                    value={formData.birthCountry}
                    onChange={handleChange}
                    className="w-full bg-[#0C0918] border border-[#D4AF37]/30 rounded px-4 py-3 text-[#F4E8D2] focus:border-[#D4AF37] focus:outline-none transition"
                  >
                    <option value="FR">France</option>
                    <option value="BE">Belgique</option>
                    <option value="CH">Suisse</option>
                    <option value="CA">Canada</option>
                    <option value="US">États-Unis</option>
                    <option value="GB">Royaume-Uni</option>
                  </select>
                </div>
              </div>

              {tab === 'duo' && (
                <>
                  <div className="border-t border-[#D4AF37]/30 pt-6">
                    <h3 className="font-semibold text-[#D4AF37] mb-4">Données de Ton Partenaire</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-[#E3D7FF] mb-2 font-semibold">Sa date de naissance</label>
                        <input
                          type="date"
                          name="partnerBirthDate"
                          value={formData.partnerBirthDate}
                          onChange={handleChange}
                          className="w-full bg-[#0C0918] border border-[#D4AF37]/30 rounded px-4 py-3 text-[#F4E8D2] focus:border-[#D4AF37] focus:outline-none transition"
                        />
                      </div>
                      <div>
                        <label className="block text-[#E3D7FF] mb-2 font-semibold">Son heure de naissance</label>
                        <input
                          type="time"
                          name="partnerBirthTime"
                          value={formData.partnerBirthTime}
                          onChange={handleChange}
                          className="w-full bg-[#0C0918] border border-[#D4AF37]/30 rounded px-4 py-3 text-[#F4E8D2] focus:border-[#D4AF37] focus:outline-none transition"
                        />
                      </div>
                    </div>
                  </div>
                </>
              )}

              {error && (
                <div className="bg-red-500/20 border border-red-500 rounded px-4 py-3 text-red-200 text-sm">
                  ⚠️ {error}
                </div>
              )}

              <div className="pt-2">
                <PromoCodeField
                  price={29}
                  product="fenetre_rencontre_avancee"
                  testIdBase="fenetre-rencontre"
                  onStateChange={setPromoState}
                />
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-[#D4AF37] to-[#E8C766] hover:from-[#E8C766] hover:to-[#F5D97D] text-[#0C0918] font-bold py-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 transition transform hover:scale-105"
                  data-testid="fenetre-rencontre-checkout-btn"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin">⟳</div>
                      Traitement...
                    </>
                  ) : promoState.status === 'ok' && promoState.final_amount === 0 ? (
                    <>Déverrouiller mon rapport<ArrowRight className="w-5 h-5" /></>
                  ) : promoState.status === 'ok' ? (
                    <>Payer {promoState.final_amount.toFixed(2)}€<ArrowRight className="w-5 h-5" /></>
                  ) : (
                    <>Accéder à Mon Rapport<ArrowRight className="w-5 h-5" /></>
                  )}
                </button>
              </div>

              <button
                type="button"
                onClick={handlePreview}
                className="w-full border border-[#D4AF37]/50 text-[#D4AF37] py-3 rounded-lg hover:bg-[#D4AF37]/10 transition font-semibold"
              >
                Aperçu Gratuit des Fenêtres
              </button>

              <div className="flex items-center justify-center gap-6 text-[#9089B5] text-sm">
                <div className="flex items-center gap-1">
                  <Shield className="w-4 h-4" />
                  Sécurisé
                </div>
                <div>•</div>
                <div>Instantané</div>
              </div>
            </form>
          </div>

          {/* Testimonial */}
          <div className="mt-16 text-center">
            <p className="text-[#9089B5] mb-4">⭐⭐⭐⭐⭐</p>
            <p className="text-[#F4E8D2] max-w-2xl mx-auto">
              "J'ai suivi la première fenêtre et j'ai rencontré quelqu'un d'extraordinaire! Merci Solena!" — Alex B.
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default FenetreRencontrePDF;
