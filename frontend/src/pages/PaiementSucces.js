import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Sparkles, CheckCircle, Download, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const PaiementSucces = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('checking'); // checking, success, error
  const [pollCount, setPollCount] = useState(0);
  const maxPolls = 5;

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    
    if (!sessionId) {
      setStatus('error');
      return;
    }

    const checkPaymentStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/checkout/status/${sessionId}`);
        
        if (!response.ok) {
          throw new Error('Failed to check payment status');
        }

        const data = await response.json();
        
        if (data.payment_status === 'paid') {
          setStatus('success');
          // Mark user as paid in localStorage
          localStorage.setItem('plume_astrale_paid', 'true');
          localStorage.setItem('plume_astrale_plan', 'manuscrit');
          localStorage.setItem('plume_astrale_payment_date', new Date().toISOString());
          return;
        }

        if (data.status === 'expired') {
          setStatus('error');
          return;
        }

        // Continue polling if not yet paid
        if (pollCount < maxPolls) {
          setPollCount(prev => prev + 1);
          setTimeout(checkPaymentStatus, 2000);
        } else {
          setStatus('error');
        }

      } catch (error) {
        console.error('Error checking payment status:', error);
        if (pollCount < maxPolls) {
          setPollCount(prev => prev + 1);
          setTimeout(checkPaymentStatus, 2000);
        } else {
          setStatus('error');
        }
      }
    };

    checkPaymentStatus();
  }, [searchParams, pollCount]);

  return (
    <div className="min-h-screen relative flex items-center justify-center px-4 py-12">
      
      <div className="relative z-10 w-full max-w-2xl">
        <div className="card-mystical text-center p-10 md:p-14">
          
          {status === 'checking' && (
            <>
              <Loader2 className="w-16 h-16 text-[#C5A059] mx-auto mb-8 animate-spin" />
              <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3' }}>
                Vérification en cours...
              </h1>
              <p className="text-[#B8B0C8]/70 font-light">
                Nous confirmons votre paiement auprès de Stripe
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
                Félicitations !
              </h1>
              
              <p className="text-[#C5A059] text-xl mb-6">
                Votre Manuscrit de la Plume est prêt
              </p>
              
              <p className="text-[#B8B0C8]/70 mb-10 font-light leading-relaxed">
                Ce trésor céleste vous accompagnera tout au long de votre vie.
                Conservez-le précieusement et revenez-y à chaque moment de questionnement.
              </p>
              
              <div className="space-y-4">
                <button
                  onClick={() => navigate('/resultats')}
                  className="btn-mystical-filled rounded-full flex items-center gap-3 mx-auto"
                  data-testid="btn-view-manuscrit"
                >
                  <Sparkles className="w-5 h-5" />
                  Découvrir Mon Manuscrit
                </button>
                
                <button
                  onClick={() => {/* TODO: Generate PDF */}}
                  className="btn-mystical rounded-full flex items-center gap-3 mx-auto opacity-50 cursor-not-allowed"
                  disabled
                  data-testid="btn-download-pdf"
                >
                  <Download className="w-5 h-5" />
                  Télécharger le PDF (bientôt disponible)
                </button>
              </div>
              
              <p className="text-[#B8B0C8]/40 text-sm mt-8 font-light">
                Un email de confirmation a été envoyé à votre adresse
              </p>
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
                Nous n'avons pas pu confirmer votre paiement. 
                Si vous avez été débité, contactez notre support.
              </p>
              
              <button
                onClick={() => navigate('/apercu')}
                className="btn-mystical rounded-full mx-auto"
                data-testid="btn-retry"
              >
                Retourner à l'aperçu
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaiementSucces;
