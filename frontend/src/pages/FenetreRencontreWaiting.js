import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, Download, Mail, ArrowLeft } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const FenetreRencontreWaiting = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading');
  const [pdfUrl, setPdfUrl] = useState(null);
  const [error, setError] = useState('');

  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    if (!sessionId) {
      navigate('/');
      return;
    }

    const pollStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/fenetre-rencontre-avancee/status?session_id=${sessionId}`);
        const data = await response.json();

        if (data.status === 'completed' && data.pdf_url) {
          setPdfUrl(data.pdf_url);
          setStatus('success');
        } else if (data.status === 'failed') {
          setError('Erreur lors de la génération du PDF');
          setStatus('error');
        } else {
          setStatus('waiting');
          setTimeout(pollStatus, 2000);
        }
      } catch (err) {
        setError('Erreur de connexion');
        setStatus('error');
      }
    };

    pollStatus();
  }, [sessionId, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0C0918] to-[#1A1F2E] text-[#F4E8D2] flex items-center justify-center pt-20 pb-20">
      <div className="max-w-2xl mx-auto px-4 text-center">
        {status === 'loading' || status === 'waiting' ? (
          <>
            <div className="mb-8 flex justify-center">
              <div className="w-20 h-20 border-4 border-[#D4AF37]/30 border-t-[#D4AF37] rounded-full animate-spin" />
            </div>
            <h1 className="text-4xl font-bold text-[#D4AF37] mb-4">
              ✦ Fenêtres en cours de calcul ✦
            </h1>
            <p className="text-[#E3D7FF] mb-4 text-lg">
              Nous alignons l'univers pour toi...
            </p>
            <p className="text-[#9089B5]">
              Cela prend environ 30-60 secondes. Un email avec ton rapport arrive très bientôt!
            </p>
          </>
        ) : status === 'success' ? (
          <>
            <div className="mb-8 flex justify-center">
              <CheckCircle className="w-20 h-20 text-[#D4AF37]" />
            </div>
            <h1 className="text-4xl font-bold text-[#D4AF37] mb-4">
              ✦ Fenêtres Prêtes! ✦
            </h1>
            <p className="text-[#E3D7FF] mb-8 text-lg">
              Tes Fenêtres de Rencontre ont été calculées avec succès.
            </p>

            <div className="bg-[#1A2035] border-2 border-[#D4AF37] rounded-lg p-8 mb-8">
              <Mail className="w-12 h-12 text-[#D4AF37] mx-auto mb-4" />
              <p className="text-[#F4E8D2] mb-4">
                Un lien de téléchargement a été envoyé à ton email.
              </p>
              {pdfUrl && (
                <a
                  href={pdfUrl}
                  download
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-[#D4AF37] to-[#E8C766] text-[#0C0918] font-bold py-3 px-6 rounded-lg hover:scale-105 transition"
                >
                  <Download className="w-5 h-5" />
                  Télécharger Mon Rapport
                </a>
              )}
            </div>

            <p className="text-[#9089B5] text-sm mb-8">
              Vérifie ta boîte spam si tu ne vois pas l'email dans tes messages reçus.
            </p>

            <button
              onClick={() => navigate('/fenetre-rencontre-pdf')}
              className="inline-flex items-center gap-2 text-[#D4AF37] hover:text-[#E8C766] transition"
            >
              <ArrowLeft className="w-5 h-5" />
              Retour
            </button>
          </>
        ) : (
          <>
            <div className="mb-8 flex justify-center">
              <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center">
                <span className="text-4xl">⚠️</span>
              </div>
            </div>
            <h1 className="text-4xl font-bold text-red-400 mb-4">
              Oups, une erreur est survenue
            </h1>
            <p className="text-[#E3D7FF] mb-8">
              {error || 'Impossible de générer ton rapport. Réessaye plus tard.'}
            </p>
            <button
              onClick={() => navigate('/fenetre-rencontre-pdf')}
              className="inline-flex items-center gap-2 bg-[#D4AF37] text-[#0C0918] font-bold py-3 px-6 rounded-lg hover:scale-105 transition"
            >
              <ArrowLeft className="w-5 h-5" />
              Réessayer
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default FenetreRencontreWaiting;
