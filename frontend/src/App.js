import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';

// Pages
import Index from '@/pages/Index';
import Formulaire from '@/pages/Formulaire';
import Resultats from '@/pages/Resultats';
import Tarot from '@/pages/Tarot';
import TirageTarot from '@/pages/TirageTarot';
import TarotOuiNon from '@/pages/TarotOuiNon';
import Tarologie from '@/pages/Tarologie';
import Numerologie from '@/pages/Numerologie';
import Horoscope from '@/pages/Horoscope';
import Compatibilite from '@/pages/Compatibilite';
import Compatibilite2 from '@/pages/Compatibilite2';
import Cercle from '@/pages/Cercle';
import Choix from '@/pages/Choix';
import Apercu from '@/pages/Apercu';
import Quotidien from '@/pages/Quotidien';
import Livre from '@/pages/Livre';
import CharteConfiance from '@/pages/CharteConfiance';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import BuyCredits from '@/pages/BuyCredits';
import CreditSuccess from '@/pages/CreditSuccess';
import PremiumExperience from '@/pages/PremiumExperience';
import PremiumLanding from '@/pages/PremiumLanding';
import Paiement from '@/pages/Paiement';
import PaiementSucces from '@/pages/PaiementSucces';
import CommandeSucces from '@/pages/CommandeSucces';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/formulaire" element={<Formulaire />} />
          <Route path="/resultats" element={<Resultats />} />
          <Route path="/tarot" element={<Tarot />} />
          <Route path="/tirage-tarot" element={<TirageTarot />} />
          <Route path="/tarot-oui-non" element={<TarotOuiNon />} />
          <Route path="/tarologie" element={<Tarologie />} />
          <Route path="/numerologie" element={<Numerologie />} />
          <Route path="/horoscope" element={<Horoscope />} />
          <Route path="/compatibilite-amoureuse" element={<Compatibilite />} />
          <Route path="/compatibilite-2" element={<Compatibilite2 />} />
          <Route path="/cercle" element={<Cercle />} />
          <Route path="/choix" element={<Choix />} />
          <Route path="/apercu" element={<Apercu />} />
          <Route path="/quotidien" element={<Quotidien />} />
          <Route path="/livre" element={<Livre />} />
          <Route path="/charte-confiance" element={<CharteConfiance />} />
          <Route path="/connexion" element={<Login />} />
          <Route path="/inscription" element={<Register />} />
          <Route path="/acheter-credits" element={<BuyCredits />} />
          <Route path="/credit-success" element={<CreditSuccess />} />
          <Route path="/premium" element={<PremiumExperience />} />
          <Route path="/premium/experience" element={<PremiumExperience />} />
          <Route path="/premium-landing" element={<PremiumLanding />} />
          <Route path="/paiement" element={<Paiement />} />
          <Route path="/paiement-succes" element={<PaiementSucces />} />
          <Route path="/commande-succes" element={<CommandeSucces />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
