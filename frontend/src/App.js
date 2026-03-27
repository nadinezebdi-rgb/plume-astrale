import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';

import Index from '@/pages/Index';
import Register from '@/pages/Register';
import Login from '@/pages/Login';
import Formulaire from '@/pages/Formulaire';
import Apercu from '@/pages/Apercu';
import Resultats from '@/pages/Resultats';
import Choix from '@/pages/Choix';
import Paiement from '@/pages/Paiement';
import PaiementSucces from '@/pages/PaiementSucces';
import BuyCredits from '@/pages/BuyCredits';
import CreditSuccess from '@/pages/CreditSuccess';
import Tarot from '@/pages/Tarot';
import TarotOuiNon from '@/pages/TarotOuiNon';
import TirageTarot from '@/pages/TirageTarot';
import Numerologie from '@/pages/Numerologie';
import Quotidien from '@/pages/Quotidien';
import Tarologie from '@/pages/Tarologie';
import Horoscope from '@/pages/Horoscope';
import Compatibilite from '@/pages/Compatibilite';
import Compatibilite2 from '@/pages/Compatibilite2';
import PremiumLanding from '@/pages/PremiumLanding';
import PremiumExperience from '@/pages/PremiumExperience';
import CharteConfiance from '@/pages/CharteConfiance';
import Cercle from '@/pages/Cercle';
import Livre from '@/pages/Livre';
import CommandeSucces from '@/pages/CommandeSucces';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<Index />} />

          <Route path="/inscription" element={<Register />} />
          <Route path="/connexion" element={<Login />} />

          <Route path="/formulaire" element={<Formulaire />} />
          <Route path="/apercu" element={<Apercu />} />
          <Route path="/resultats" element={<Resultats />} />

          <Route path="/choix" element={<Choix />} />
          <Route path="/paiement" element={<Paiement />} />
          <Route path="/paiement-succes" element={<PaiementSucces />} />

          <Route path="/acheter-credits" element={<BuyCredits />} />
          <Route path="/credit-succes" element={<CreditSuccess />} />

          <Route path="/tarot" element={<Tarot />} />
          <Route path="/tirage" element={<Navigate to="/tarot" replace />} />
          <Route path="/tarot-oui-non" element={<TarotOuiNon />} />
          <Route path="/tirage-tarot" element={<TirageTarot />} />

          <Route path="/numerologie" element={<Numerologie />} />
          <Route path="/quotidien" element={<Quotidien />} />
          <Route path="/tarologie" element={<Tarologie />} />
          <Route path="/horoscope" element={<Horoscope />} />

          <Route path="/compatibilite" element={<Compatibilite />} />
          <Route path="/compatibilite-amoureuse" element={<Compatibilite2 />} />

          <Route path="/premium" element={<PremiumLanding />} />
          <Route path="/premium/experience" element={<PremiumExperience />} />

          <Route path="/charte-de-confiance" element={<CharteConfiance />} />
          <Route path="/cercle" element={<Cercle />} />
          <Route path="/livre" element={<Livre />} />
          <Route path="/commande-succes" element={<CommandeSucces />} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
