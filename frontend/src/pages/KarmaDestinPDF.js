import React, { useState } from 'react';
import { ArrowRight, Sparkles, Moon, Zap, Shield, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import SEO from '@/components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const KarmaDestinPDF = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    firstName: '',
    birthDate: '',
    birthTime: '',
    birthCity: 'Paris',
    birthCountry: 'FR',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/karma-destin/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          birth_date: formData.birthDate,
          birth_time: formData.birthTime,
          first_name: formData.firstName,
          birth_city: formData.birthCity,
          birth_country: formData.birthCountry,
          origin_url: window.location.origin,
        }),
      });

      const data = await response.json();
      if (data.url) {
        window.location.href = data.url;
      } else if (data.session_id) {
        navigate(`/karma-destin/attente?session_id=${data.session_id}`);
      }
    } catch (err) {
      setError('Erreur de connexion. Réessaye dans quelques instants.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SEO
        title="Analyse Karmique & Destinée - Plume Astrale"
        description="Découvre tes leçons karmiques, Nœuds Lunaires, Saturne, Chiron et Pluton. Rapport PDF 15 pages."
      />

      <div className="min-h-screen bg-gradient-to-b from-[#0C0918] to-[#1A1F2E] text-[#F4E8D2] pt-20 pb-20">
        <div className="max-w-5xl mx-auto px-4">
          {/* Hero */}
          <div className="text-center mb-16">
            <div className="inline-block mb-4 bg-[#D4AF37]/20 px-4 py-2 rounded-full border border-[#D4AF37]/50">
              <span className="text-[#D4AF37] font-semibold text-sm">SPIRITUALITÉ PROFONDE</span>
            </div>

            <h1 className="text-6xl md:text-7xl font-bold text-[#D4AF37] mb-6">
              ✦ Ton Analyse<br />Karmique ✦
            </h1>

            <p className="text-xl md:text-2xl text-[#E3D7FF] mb-8 leading-relaxed">
              Déchiffre les leçons que ton âme est venue apprendre.<br />
              <span className="text-[#D4AF37]">Nœuds Lunaires • Saturne • Chiron • Pluton</span>
            </p>

            <div className="inline-block bg-[#1A2035] border-2 border-[#D4AF37] rounded-lg px-8 py-4 mb-8">
              <p className="text-3xl font-bold text-[#D4AF37]">24€</p>
              <p className="text-[#E3D7FF] text-sm">PDF 15 pages • Livraison instantanée</p>
            </div>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            <div className="bg-[#1A2035]/80 border border-[#D4AF37]/40 rounded-lg p-6 hover:border-[#D4AF37]/80 transition">
              <Moon className="w-10 h-10 text-[#D4AF37] mb-4" />
              <h3 className="font-bold text-[#E3D7FF] mb-2 text-lg">Nœuds Lunaires</h3>
              <p className="text-[#F4E8D2] text-sm">Ton chemin d'évolution spirituelle sur plusieurs vies</p>
            </div>

            <div className="bg-[#1A2035]/80 border border-[#D4AF37]/40 rounded-lg p-6 hover:border-[#D4AF37]/80 transition">
              <Sparkles className="w-10 h-10 text-[#D4AF37] mb-4" />
              <h3 className="font-bold text-[#E3D7FF] mb-2 text-lg">Blessure Sacrée</h3>
              <p className="text-[#F4E8D2] text-sm">Ta blessure (Chiron) devient ta porte de guérison</p>
            </div>

            <div className="bg-[#1A2035]/80 border border-[#D4AF37]/40 rounded-lg p-6 hover:border-[#D4AF37]/80 transition">
              <Zap className="w-10 h-10 text-[#D4AF37] mb-4" />
              <h3 className="font-bold text-[#E3D7FF] mb-2 text-lg">Karma Générationnel</h3>
              <p className="text-[#F4E8D2] text-sm">L'héritage de tes ancêtres + comment tu le guéris</p>
            </div>
          </div>

          {/* Content */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-16">
            <div>
              <h2 className="text-2xl font-bold text-[#D4AF37] mb-6">À l'Intérieur du Rapport</h2>
              <ul className="space-y-4">
                {[
                  'Nœud Nord & Sud — Ton chemin de destinée',
                  'Saturne — Tes leçons karmiques',
                  'Chiron — Ta blessure sacrée + guérison',
                  'Pluton — Transformations de pouvoir',
                  'Planètes Rétrogrades — Rétrogradations karmiques',
                  'Karma Générationnel — Héritage ancestral',
                  'Rituels de Libération — Pratiques d\'intégration',
                  '15 Pages Poétiques — Illustrations symboliques',
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-[#D4AF37] mt-0.5 flex-shrink-0" />
                    <span className="text-[#F4E8D2]">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-[#1A2035] border border-[#D4AF37]/50 rounded-lg p-8 flex flex-col justify-center">
              <h3 className="text-[#D4AF37] text-sm font-bold uppercase tracking-wider mb-4">Comprendre Ton Karma</h3>
              <p className="text-[#F4E8D2] leading-relaxed mb-4">
                Le karma n'est pas une punition — c'est un enseignement. Chaque incarnation te rapproche de ta sagesse cosmique.
              </p>
              <p className="text-[#E3D7FF] leading-relaxed">
                Cette analyse révèle les leçons que ton âme est venue apprendre et comment tu peux enfin t'en libérer.
              </p>
            </div>
          </div>

          {/* Form */}
          <div className="bg-gradient-to-b from-[#1A2035] to-[#111625] border border-[#D4AF37]/50 rounded-lg p-8 md:p-12">
            <h2 className="text-3xl font-bold text-[#D4AF37] mb-8 text-center">Commence Ton Exploration Karmique</h2>

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
                  <label className="block text-[#E3D7FF] mb-2 font-semibold">Email *</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full bg-[#0C0918] border border-[#D4AF37]/30 rounded px-4 py-3 text-[#F4E8D2] placeholder-[#9089B5] focus:border-[#D4AF37] focus:outline-none transition"
                    placeholder="toi@example.com"
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

              {error && (
                <div className="bg-red-500/20 border border-red-500 rounded px-4 py-3 text-red-200 text-sm">
                  ⚠️ {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-[#D4AF37] to-[#E8C766] hover:from-[#E8C766] hover:to-[#F5D97D] text-[#0C0918] font-bold py-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 transition transform hover:scale-105"
              >
                {loading ? (
                  <>
                    <div className="animate-spin">⟳</div>
                    Traitement...
                  </>
                ) : (
                  <>
                    Commencer Mon Analyse Karmique
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>

              <div className="flex items-center justify-center gap-6 text-[#9089B5] text-sm">
                <div className="flex items-center gap-1">
                  <Shield className="w-4 h-4" />
                  Sécurisé
                </div>
                <div>•</div>
                <div>Accès instantané</div>
              </div>
            </form>
          </div>

          {/* Testimonial */}
          <div className="mt-16 text-center">
            <p className="text-[#9089B5] mb-4">⭐⭐⭐⭐⭐</p>
            <p className="text-[#F4E8D2] max-w-2xl mx-auto">
              "Cette analyse m'a libérée des patterns familiaux qui me paralysaient. Enfin je comprends pourquoi je répète certains schémas." — Marie L.
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default KarmaDestinPDF;
