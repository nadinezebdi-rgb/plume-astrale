import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import StarField from "./components/StarField/StarField";

import Index from "./pages/Index";
import Formulaire from "./pages/Formulaire";
import Apercu from "./pages/Apercu";
import Choix from "./pages/Choix";
import Paiement from "./pages/Paiement";
import PaiementSucces from "./pages/PaiementSucces";
import Resultats from "./pages/Resultats";
import Tarot from "./pages/Tarot";
import Compatibilite from "./pages/Compatibilite";
import Horoscope from "./pages/Horoscope";
import Livre from "./pages/Livre";
import CommandeSucces from "./pages/CommandeSucces";
import Quotidien from "./pages/Quotidien";
import TarotOuiNon from "./pages/TarotOuiNon";
import Tarologie from "./pages/Tarologie";
import Compatibilite2 from "./pages/Compatibilite2";
import Numerologie from "./pages/Numerologie";
import PremiumLanding from "./pages/PremiumLanding";
import PremiumExperience from "./pages/PremiumExperience";
import CharteConfiance from "./pages/CharteConfiance";
import TirageTarot from "./pages/TirageTarot";
import Login from "./pages/Login";
import Register from "./pages/Register";
import BuyCredits from "./pages/BuyCredits";
import CreditSuccess from "./pages/CreditSuccess";
import Cercle from "./pages/Cercle";

console.log("APP OK");

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App relative min-h-screen overflow-x-hidden bg-[#0B0B0F]">
          <StarField />
          <Navbar />
          <main className="relative z-10">
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/formulaire" element={<Formulaire />} />
              <Route path="/apercu" element={<Apercu />} />
              <Route path="/choix" element={<Choix />} />
              <Route path="/paiement" element={<Paiement />} />
              <Route path="/paiement-succes" element={<PaiementSucces />} />
              <Route path="/resultats" element={<Resultats />} />
              <Route path="/tarot" element={<Tarot />} />
              <Route path="/compatibilite" element={<Compatibilite />} />
              <Route path="/compatibilite-amoureuse" element={<Compatibilite2 />} />
              <Route path="/horoscope" element={<Horoscope />} />
              <Route path="/livre" element={<Livre />} />
              <Route path="/commande-succes" element={<CommandeSucces />} />
              <Route path="/quotidien" element={<Quotidien />} />
              <Route path="/tarot-oui-non" element={<TarotOuiNon />} />
              <Route path="/tarologie" element={<Tarologie />} />
              <Route path="/numerologie" element={<Numerologie />} />
              <Route path="/premium" element={<PremiumLanding />} />
              <Route path="/premium/experience" element={<PremiumExperience />} />
              <Route path="/charte-de-confiance" element={<CharteConfiance />} />
              <Route path="/tirage-tarot" element={<TirageTarot />} />
              <Route path="/connexion" element={<Login />} />
              <Route path="/inscription" element={<Register />} />
              <Route path="/acheter-credits" element={<BuyCredits />} />
              <Route path="/credit-success" element={<CreditSuccess />} />
              <Route path="/credits/success" element={<CreditSuccess />} />
              <Route path="/credit/success" element={<CreditSuccess />} />
              <Route path="/credits/succes" element={<CreditSuccess />} />
              <Route path="/cercle" element={<Cercle />} />
              <Route path="/tirage" element={<TarotOuiNon />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
