import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

// Composants
import Navbar from "./components/Navbar";
import TrialBanner from "./components/TrialBanner";
import StickyBanner from "./components/StickyBanner";
import ErrorBoundary from "./components/ErrorBoundary";
import PremiumStickyCTA from "./components/PremiumStickyCTA";
import CookieConsent from "./components/CookieConsent";

// Pages
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
import RevolutionSolaire from "./pages/RevolutionSolaire";
import LoveLanguages from "./pages/LoveLanguages";
import AstrologieVedique from "./pages/AstrologieVedique";
import MotDePasseOublie from "./pages/MotDePasseOublie";
import ReinitialiserMotDePasse from "./pages/ReinitialiserMotDePasse";
import NotreCadre from "./pages/NotreCadre";
import SynastrieSales from "./pages/SynastrieSales";
import SynastrieSucces from "./pages/SynastrieSucces";
import AstroSexo from "./pages/AstroSexo";
import Bibliotheque from "./pages/Bibliotheque";
import Desabonnement from "./pages/Desabonnement";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <StickyBanner />
        <div style={{ padding: '20px', textAlign: 'center', color: 'white' }}>
          <h1>Plume Astrale - Test StickyBanner</h1>
          <p>StickyBanner enabled, routes disabled</p>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
