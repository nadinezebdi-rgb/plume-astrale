import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

// composants
import Navbar from "./components/Navbar";

// pages
import Index from "./pages/Index";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Tarot from "./pages/Tarot";
import TarotOuiNon from "./pages/TarotOuiNon";
import TirageTarot from "./pages/TirageTarot";
import Tarologie from "./pages/Tarologie";
import Formulaire from "./pages/Formulaire";
import Apercu from "./pages/Apercu";
import Choix from "./pages/Choix";
import Paiement from "./pages/Paiement";
import PaiementSucces from "./pages/PaiementSucces";
import Resultats from "./pages/Resultats";
import Numerologie from "./pages/Numerologie";
import Compatibilite from "./pages/Compatibilite";
import Compatibilite2 from "./pages/Compatibilite2";
import Cercle from "./pages/Cercle";
import Horoscope from "./pages/Horoscope";
import Quotidien from "./pages/Quotidien";
import BuyCredits from "./pages/BuyCredits";
import CreditSuccess from "./pages/CreditSuccess";
import PremiumLanding from "./pages/PremiumLanding";
import PremiumExperience from "./pages/PremiumExperience";
import Livre from "./pages/Livre";
import CommandeSucces from "./pages/CommandeSucces";
import CharteConfiance from "./pages/CharteConfiance";

// fallback
const NotFound = () => (
  <div style={{ color: "white", textAlign: "center", marginTop: "100px" }}>
    Page non trouvée
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div style={{ minHeight: "100vh", background: "#0C0918" }}>
          <Navbar />

          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/inscription" element={<Register />} />
            <Route path="/connexion" element={<Login />} />
            <Route path="/tarot" element={<Tarot />} />
            <Route path="/tarot-oui-non" element={<TarotOuiNon />} />
            <Route path="/tirage-tarot" element={<TirageTarot />} />
            <Route path="/tarologie" element={<Tarologie />} />
            <Route path="/formulaire" element={<Formulaire />} />
            <Route path="/apercu" element={<Apercu />} />
            <Route path="/choix" element={<Choix />} />
            <Route path="/paiement" element={<Paiement />} />
            <Route path="/paiement-succes" element={<PaiementSucces />} />
            <Route path="/resultats" element={<Resultats />} />
            <Route path="/numerologie" element={<Numerologie />} />
            <Route path="/compatibilite-amoureuse" element={<Compatibilite />} />
            <Route path="/compatibilite-resultat" element={<Compatibilite2 />} />
            <Route path="/cercle" element={<Cercle />} />
            <Route path="/horoscope" element={<Horoscope />} />
            <Route path="/quotidien" element={<Quotidien />} />
            <Route path="/acheter-credits" element={<BuyCredits />} />
            <Route path="/credit-success" element={<CreditSuccess />} />
            <Route path="/premium" element={<PremiumLanding />} />
            <Route path="/premium/experience" element={<PremiumExperience />} />
            <Route path="/livre" element={<Livre />} />
            <Route path="/commande-succes" element={<CommandeSucces />} />
            <Route path="/charte-confiance" element={<CharteConfiance />} />

            {/* fallback */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
