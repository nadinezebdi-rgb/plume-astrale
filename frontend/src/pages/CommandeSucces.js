import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Sparkles, CheckCircle, Truck, Calendar, Package, Loader2, Download } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CommandeSucces = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('checking'); // checking, success, error
  const [order, setOrder] = useState(null);
  const [pollCount, setPollCount] = useState(0);
  const maxPolls = 5;

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    
    if (!sessionId) {
      setStatus('error');
      return;
    }

    const checkOrderStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/order/book/${sessionId}`);
        
        if (!response.ok) {
          throw new Error('Failed to check order status');
        }

        const data = await response.json();
        setOrder(data);
        
        if (data.payment_status === 'paid') {
          setStatus('success');
          localStorage.setItem('plume_astrale_book_paid', 'true');
          return;
        }

        // Continue polling if not yet paid
        if (pollCount < maxPolls) {
          setPollCount(prev => prev + 1);
          setTimeout(checkOrderStatus, 2000);
        } else {
          setStatus('error');
        }

      } catch (error) {
        console.error('Error checking order status:', error);
        if (pollCount < maxPolls) {
          setPollCount(prev => prev + 1);
          setTimeout(checkOrderStatus, 2000);
        } else {
          setStatus('error');
        }
      }
    };

    checkOrderStatus();
  }, [searchParams, pollCount]);

  const downloadPDF = async () => {
    try {
      const userData = JSON.parse(localStorage.getItem('plume_astrale_data') || '{}');
      
      const response = await fetch(`${API_URL}/api/pdf/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_data: userData })
      });

      if (!response.ok) throw new Error('PDF generation failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `manuscrit_plume_${userData.prenom || 'celestial'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      alert('Erreur lors du téléchargement. Veuillez réessayer.');
    }
  };

  // Calculate estimated delivery date
  const getDeliveryDate = () => {
    const date = new Date();
    date.setDate(date.getDate() + 5);
    return date.toLocaleDateString('fr-FR', { 
      weekday: 'long', 
      day: 'numeric', 
      month: 'long' 
    });
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center px-4 py-12">
      
      <div className="relative z-10 w-full max-w-2xl">
        <div className="card-mystical text-center p-10 md:p-14">
          
          {status === 'checking' && (
            <>
              <Loader2 className="w-16 h-16 text-[#C5A059] mx-auto mb-8 animate-spin" />
              <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                Vérification de votre commande...
              </h1>
              <p className="text-[#B8B0C8]/70 font-light">
                Nous confirmons votre paiement
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="relative mb-8">
                <CheckCircle className="w-20 h-20 text-emerald-500 mx-auto" strokeWidth={1.5} />
                <Sparkles className="w-8 h-8 text-[#C5A059] absolute top-0 right-1/3 animate-pulse" />
              </div>
              
              <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                Commande Confirmée !
              </h1>
              
              <p className="text-[#C5A059] text-xl mb-6">
                Votre Livre de la Plume est en préparation
              </p>
              
              {/* Order details */}
              <div className="bg-[#15112A]/50 rounded-sm p-6 mb-8 text-left">
                <h3 className="text-[#F0E6D3] mb-4" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                  Détails de la commande
                </h3>
                
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-3 text-[#B8B0C8]/70">
                    <Package className="w-4 h-4 text-[#C5A059]" />
                    <span>Le Livre de la Plume - Édition reliée</span>
                  </div>
                  
                  {order?.shipping_address && (
                    <div className="flex items-start gap-3 text-[#B8B0C8]/70">
                      <Truck className="w-4 h-4 text-[#C5A059] mt-1" />
                      <div>
                        <p>{order.shipping_address.name}</p>
                        <p>{order.shipping_address.street}</p>
                        {order.shipping_address.street2 && <p>{order.shipping_address.street2}</p>}
                        <p>{order.shipping_address.postal_code} {order.shipping_address.city}</p>
                        <p>{order.shipping_address.country}</p>
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-3 text-[#B8B0C8]/70">
                    <Calendar className="w-4 h-4 text-[#C5A059]" />
                    <span>Livraison estimée : {getDeliveryDate()}</span>
                  </div>
                </div>
              </div>
              
              <p className="text-[#B8B0C8]/60 mb-8 font-light">
                Un email de confirmation a été envoyé. 
                Vous recevrez un numéro de suivi dès l'expédition.
              </p>
              
              <div className="space-y-4">
                <button
                  onClick={downloadPDF}
                  className="btn-mystical-filled rounded-full flex items-center gap-3 mx-auto"
                  data-testid="btn-download-pdf"
                >
                  <Download className="w-5 h-5" />
                  Télécharger la version PDF en attendant
                </button>
                
                <button
                  onClick={() => navigate('/')}
                  className="btn-mystical rounded-full mx-auto"
                >
                  Retour à l'accueil
                </button>
              </div>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-8">
                <span className="text-4xl text-red-400">!</span>
              </div>
              
              <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                Une erreur est survenue
              </h1>
              
              <p className="text-[#B8B0C8]/70 mb-10 font-light">
                Nous n'avons pas pu confirmer votre commande. 
                Si vous avez été débité, contactez notre support.
              </p>
              
              <button
                onClick={() => navigate('/livre')}
                className="btn-mystical rounded-full mx-auto"
              >
                Réessayer
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommandeSucces;
