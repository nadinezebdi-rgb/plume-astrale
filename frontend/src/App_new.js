import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import Navbar from "./components/Navbar";
import TrialBanner from "./components/TrialBanner";

// Nouvelle page d'accueil
import NewHome from "./pages/NewHome";
// Ancienne page d'accueil (gardée pour référence)
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
import MotDePasseOublie from "./pages/MotDePasseOublie";
import ReinitialiserMotDePasse from "./pages/ReinitialiserMotDePasse";
import NotreCadre from "./pages/NotreCadre";
import SynastrieSales from "./pages/SynastrieSales";
import SynastrieSucces from "./pages/SynastrieSucces";
import AstroSexo from "./pages/AstroSexo";
import RencontresAstrales from "./pages/RencontresAstrales";
import RencontresUltimeSucces from "./pages/RencontresUltimeSucces";
import Bibliotheque from "./pages/Bibliotheque";
import Desabonnement from "./pages/Desabonnement";
import PremiumStickyCTA from "./components/PremiumStickyCTA";
import CookieConsent from "./components/CookieConsent";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* NOUVELLE PAGE D'ACCUEIL IMMERSIVE */}
          <Route path="/" element={<NewHome />} />
          
          {/* Pages sans Navbar (admin, funnel dédiés) */}
          <Route path="/admin" element={<Admin />} />
          <Route path="/bibliotheque" element={<Bibliotheque />} />
          <Route path="/rencontres-astrales" element={<RencontresAstrales />} />
          <Route path="/rencontres-astrales/succes" element={<RencontresUltimeSucces />} />

          {/* Toutes les autres pages — avec Navbar */}
          <Route path="*" element={
            <>
              <Navbar />
              <Routes>
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
                <Route path="/cercle-quotidien" element={<Cercle />} />
                <Route path="/cercle-dashboard" element={<Cercle />} />
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
                <Route path="/revolution-solaire" element={<RevolutionSolaire />} />
                <Route path="/love-languages" element={<LoveLanguages />} />
                <Route path="/mot-de-passe-oublie" element={<MotDePasseOublie />} />
                <Route path="/reinitialiser-mot-de-passe" element={<ReinitialiserMotDePasse />} />
                <Route path="/notre-cadre" element={<NotreCadre />} />
                <Route path="/cercle" element={<Cercle />} />
                <Route path="/synastrie" element={<SynastrieSales />} />
                <Route path="/synastrie/succes" element={<SynastrieSucces />} />
                <Route path="/astrosexo" element={<AstroSexo />} />
                <Route path="/desabonnement" element={<Desabonnement />} />
              </Routes>
              <PremiumStickyCTA />
              <CookieConsent />
            </>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
