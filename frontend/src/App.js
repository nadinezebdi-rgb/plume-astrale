import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import Navbar from "./components/Navbar";

import Index from "./pages/Index";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Tarot from "./pages/Tarot";
import Formulaire from "./pages/Formulaire";
import Apercu from "./pages/Apercu";
import Paiement from "./pages/Paiement";
import PaiementSucces from "./pages/PaiementSucces";
import Resultats from "./pages/Resultats";
import TirageTarot from "./pages/TirageTarot";
import TarotOuiNon from "./pages/TarotOuiNon";
import Tarologie from "./pages/Tarologie";
import Numerologie from "./pages/Numerologie";
import KarmaDestin from "./pages/KarmaDestin";
import Horoscope from "./pages/Horoscope";
import Compatibilite from "./pages/Compatibilite";
import Compatibilite2 from "./pages/Compatibilite2";
import Cercle from "./pages/Cercle";
import Quotidien from "./pages/Quotidien";
import BuyCredits from "./pages/BuyCredits";
import CreditSuccess from "./pages/CreditSuccess";
import Choix from "./pages/Choix";
import Livre from "./pages/Livre";
import CommandeSucces from "./pages/CommandeSucces";
import PremiumLanding from "./pages/PremiumLanding";
import PremiumExperience from "./pages/PremiumExperience";
import CharteConfiance from "./pages/CharteConfiance";
import MonCompte from "./pages/MonCompte";
import Admin from "./pages/Admin";
import Energie from "./pages/Energie";
import Premium from "./pages/Premium";
import ChatIA from "./pages/ChatIA";
import Oracle from "./pages/Oracle";
import MonRituel from "./pages/MonRituel";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Page admin — sans Navbar */}
          <Route path="/admin" element={<Admin />} />

          {/* Toutes les autres pages — avec Navbar */}
          <Route path="*" element={
            <>
              <Navbar />
              <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/inscription" element={<Register />} />
                <Route path="/connexion" element={<Login />} />
                <Route path="/formulaire" element={<Formulaire />} />
                <Route path="/apercu" element={<Apercu />} />
                <Route path="/choix" element={<Choix />} />
                <Route path="/paiement" element={<Paiement />} />
                <Route path="/paiement/succes" element={<PaiementSucces />} />
                <Route path="/resultats" element={<Resultats />} />
                <Route path="/numerologie" element={<Numerologie />} />
                <Route path="/karma-destin" element={<KarmaDestin />} />
                <Route path="/tarot" element={<Tarot />} />
                <Route path="/tirage-tarot" element={<TirageTarot />} />
                <Route path="/tarot-oui-non" element={<TarotOuiNon />} />
                <Route path="/tarologie" element={<Tarologie />} />
                <Route path="/horoscope" element={<Horoscope />} />
                <Route path="/compatibilite" element={<Compatibilite />} />
                <Route path="/compatibilite-amoureuse" element={<Compatibilite2 />} />
                <Route path="/quotidien" element={<Quotidien />} />
                <Route path="/cercle" element={<Cercle />} />
                <Route path="/premium" element={<Premium />} />
                <Route path="/premium/decouvrir" element={<PremiumLanding />} />
                <Route path="/premium/experience" element={<PremiumExperience />} />
                <Route path="/acheter-credits" element={<BuyCredits />} />
                <Route path="/credits/succes" element={<CreditSuccess />} />
                <Route path="/livre" element={<Livre />} />
                <Route path="/commande/succes" element={<CommandeSucces />} />
                <Route path="/mon-compte" element={<MonCompte />} />
                <Route path="/charte-de-confiance" element={<CharteConfiance />} />
                <Route path="/consultation" element={<ChatIA />} />
                <Route path="/energie" element={<Energie />} />
                <Route path="/premium/succes" element={<Premium />} />
                <Route path="/chat-astral" element={<ChatIA />} />
                <Route path="/oracle" element={<Oracle />} />
                <Route path="/mon-rituel" element={<MonRituel />} />
              </Routes>
            </>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
