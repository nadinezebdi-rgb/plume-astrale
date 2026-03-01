import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Book, Sparkles, Truck, Clock, Gift, CheckCircle, Loader2, ArrowLeft, Tag } from 'lucide-react';
import StarField from '@/components/StarField/StarField';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Livre = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [promoError, setPromoError] = useState('');
  const [promoSuccess, setPromoSuccess] = useState('');
  const [promoLoading, setPromoLoading] = useState(false);
  const [address, setAddress] = useState({
    name: '',
    street: '',
    street2: '',
    city: '',
    postal_code: '',
    country: 'France'
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (data) {
      const parsed = JSON.parse(data);
      setUserData(parsed);
      setAddress(prev => ({
        ...prev,
        name: parsed.prenom || ''
      }));
    }
  }, []);

  const validateForm = () => {
    const newErrors = {};
    if (!address.name.trim()) newErrors.name = 'Nom requis';
    if (!address.street.trim()) newErrors.street = 'Adresse requise';
    if (!address.city.trim()) newErrors.city = 'Ville requise';
    if (!address.postal_code.trim()) newErrors.postal_code = 'Code postal requis';
    if (!address.country.trim()) newErrors.country = 'Pays requis';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleOrder = async () => {
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    try {
      const email = userData?.email || `${address.name.toLowerCase().replace(/\s+/g, '.')}@client.plume-astrale.fr`;
      
      const response = await fetch(`${API_URL}/api/order/book`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: 'livre',
          origin_url: window.location.origin,
          user_email: email,
          user_data: userData,
          shipping_address: address
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors de la commande');
      }

      const data = await response.json();
      
      if (data.url) {
        // Store order info
        localStorage.setItem('plume_astrale_book_order', JSON.stringify({
          order_id: data.order_id,
          session_id: data.session_id,
          address: address
        }));
        
        window.location.href = data.url;
      }
    } catch (error) {
      console.error('Order error:', error);
      alert('Une erreur est survenue. Veuillez réessayer.');
    }
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen relative">
      <StarField />
      
      <div className="relative z-10 max-w-4xl mx-auto px-4 py-12">
        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-[#C5A059] hover:text-[#F3E5AB] mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour
        </button>
        
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#C5A059]/10 border border-[#C5A059]/30 mb-6">
            <Gift className="w-4 h-4 text-[#C5A059]" />
            <span className="text-[#C5A059] text-sm">Édition limitée</span>
          </div>
          
          <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
            Le Livre de la Plume
          </h1>
          <p className="text-[#E0D9F6]/70 text-lg font-light">
            Votre manuscrit céleste imprimé en livre relié
          </p>
        </div>
        
        {/* Product showcase */}
        <div className="card-mystical p-8 md:p-12 mb-8 glow-gold">
          <div className="flex flex-col md:flex-row gap-8 items-center">
            {/* Book visual */}
            <div className="w-full md:w-1/3">
              <div className="aspect-[3/4] rounded-lg bg-gradient-to-br from-[#1A0B2E] to-[#0F0518] border-2 border-[#C5A059]/30 flex items-center justify-center shadow-2xl">
                <div className="text-center p-6">
                  <Book className="w-16 h-16 text-[#C5A059] mx-auto mb-4" strokeWidth={1} />
                  <p className="text-[#F3E5AB] text-sm" style={{ fontFamily: 'Cinzel, serif' }}>
                    Le Manuscrit<br />de la Plume
                  </p>
                  <p className="text-[#C5A059]/60 text-xs mt-2">
                    {userData?.prenom || 'Votre nom'}
                  </p>
                </div>
              </div>
            </div>
            
            {/* Details */}
            <div className="flex-1">
              <h2 className="text-2xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
                Un Trésor à Offrir ou à S'Offrir
              </h2>
              
              <p className="text-[#E0D9F6]/70 font-light mb-6 leading-relaxed">
                Recevez votre manuscrit céleste imprimé sur papier premium, 
                relié avec soin. Un objet précieux à garder sur votre table de chevet 
                ou à offrir à un être cher.
              </p>
              
              <div className="space-y-3 mb-8">
                <div className="flex items-center gap-3 text-[#E0D9F6]/80">
                  <CheckCircle className="w-5 h-5 text-[#C5A059]" />
                  <span>Impression haute qualité sur papier premium</span>
                </div>
                <div className="flex items-center gap-3 text-[#E0D9F6]/80">
                  <CheckCircle className="w-5 h-5 text-[#C5A059]" />
                  <span>Couverture rigide avec finition mate</span>
                </div>
                <div className="flex items-center gap-3 text-[#E0D9F6]/80">
                  <CheckCircle className="w-5 h-5 text-[#C5A059]" />
                  <span>Illustrations exclusives pour chaque signe</span>
                </div>
                <div className="flex items-center gap-3 text-[#E0D9F6]/80">
                  <CheckCircle className="w-5 h-5 text-[#C5A059]" />
                  <span>Format élégant 15x21cm</span>
                </div>
              </div>
              
              <div className="flex items-center gap-4 mb-6">
                <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-[#C5A059]/10 border border-[#C5A059]/30">
                  <Truck className="w-4 h-4 text-[#C5A059]" />
                  <span className="text-[#C5A059] text-sm">Livraison incluse</span>
                </div>
                <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-[#C5A059]/10 border border-[#C5A059]/30">
                  <Clock className="w-4 h-4 text-[#C5A059]" />
                  <span className="text-[#C5A059] text-sm">Expédié sous 5 jours</span>
                </div>
              </div>
              
              {/* Price */}
              <div className="border-t border-[#C5A059]/20 pt-6">
                <div className="flex items-end gap-3 mb-4">
                  <span className="text-4xl font-bold text-gold-gradient" style={{ fontFamily: 'Cinzel, serif' }}>
                    49,90€
                  </span>
                  <span className="text-[#E0D9F6]/50 text-sm mb-1">
                    Livraison offerte
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Order section */}
        {!showAddressForm ? (
          <div className="text-center">
            <button
              onClick={() => setShowAddressForm(true)}
              className="btn-mystical-filled rounded-full flex items-center gap-3 mx-auto text-lg px-10 py-4"
              data-testid="btn-order-book"
            >
              <Gift className="w-6 h-6" />
              Commander Mon Livre
            </button>
            <p className="text-[#E0D9F6]/50 text-sm mt-4">
              Paiement sécurisé par Stripe • Satisfait ou remboursé
            </p>
          </div>
        ) : (
          <div className="card-mystical p-8">
            <h3 className="text-xl mb-6" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>
              Adresse de Livraison
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-[#E0D9F6]/70 text-sm mb-2">Nom complet *</label>
                <input
                  type="text"
                  value={address.name}
                  onChange={(e) => setAddress({ ...address, name: e.target.value })}
                  className="w-full px-4 py-3 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059]"
                  placeholder="Marie Dupont"
                  data-testid="input-name"
                />
                {errors.name && <p className="text-red-400 text-sm mt-1">{errors.name}</p>}
              </div>
              
              <div>
                <label className="block text-[#E0D9F6]/70 text-sm mb-2">Adresse *</label>
                <input
                  type="text"
                  value={address.street}
                  onChange={(e) => setAddress({ ...address, street: e.target.value })}
                  className="w-full px-4 py-3 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059]"
                  placeholder="12 rue des Étoiles"
                  data-testid="input-street"
                />
                {errors.street && <p className="text-red-400 text-sm mt-1">{errors.street}</p>}
              </div>
              
              <div>
                <label className="block text-[#E0D9F6]/70 text-sm mb-2">Complément d'adresse</label>
                <input
                  type="text"
                  value={address.street2}
                  onChange={(e) => setAddress({ ...address, street2: e.target.value })}
                  className="w-full px-4 py-3 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059]"
                  placeholder="Appartement 3B"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[#E0D9F6]/70 text-sm mb-2">Code postal *</label>
                  <input
                    type="text"
                    value={address.postal_code}
                    onChange={(e) => setAddress({ ...address, postal_code: e.target.value })}
                    className="w-full px-4 py-3 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059]"
                    placeholder="75001"
                    data-testid="input-postal"
                  />
                  {errors.postal_code && <p className="text-red-400 text-sm mt-1">{errors.postal_code}</p>}
                </div>
                <div>
                  <label className="block text-[#E0D9F6]/70 text-sm mb-2">Ville *</label>
                  <input
                    type="text"
                    value={address.city}
                    onChange={(e) => setAddress({ ...address, city: e.target.value })}
                    className="w-full px-4 py-3 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059]"
                    placeholder="Paris"
                    data-testid="input-city"
                  />
                  {errors.city && <p className="text-red-400 text-sm mt-1">{errors.city}</p>}
                </div>
              </div>
              
              <div>
                <label className="block text-[#E0D9F6]/70 text-sm mb-2">Pays *</label>
                <select
                  value={address.country}
                  onChange={(e) => setAddress({ ...address, country: e.target.value })}
                  className="w-full px-4 py-3 bg-[#1A0B2E] border border-[#C5A059]/30 rounded-lg text-[#E0D9F6] focus:outline-none focus:border-[#C5A059]"
                  data-testid="input-country"
                >
                  <option value="France">France</option>
                  <option value="Belgique">Belgique</option>
                  <option value="Suisse">Suisse</option>
                  <option value="Luxembourg">Luxembourg</option>
                  <option value="Canada">Canada</option>
                </select>
              </div>
              
              <div className="flex gap-4 pt-4">
                <button
                  onClick={() => setShowAddressForm(false)}
                  className="btn-mystical rounded-full flex-1"
                >
                  Annuler
                </button>
                <button
                  onClick={handleOrder}
                  disabled={isLoading}
                  className="btn-mystical-filled rounded-full flex-1 flex items-center justify-center gap-2"
                  data-testid="btn-confirm-order"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Traitement...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Payer 49,90€
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Trust badges */}
        <div className="flex flex-wrap justify-center gap-6 mt-12 text-[#E0D9F6]/50 text-sm">
          <span>🔒 Paiement sécurisé</span>
          <span>📦 Livraison suivie</span>
          <span>✨ Qualité premium</span>
          <span>💝 Idéal cadeau</span>
        </div>
      </div>
    </div>
  );
};

export default Livre;
