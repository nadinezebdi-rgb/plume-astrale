import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import Navbar from "./components/Navbar";
import TrialBanner from "./components/TrialBanner";
import ErrorBoundary from "./components/ErrorBoundary";
import PremiumStickyCTA from "./components/PremiumStickyCTA";
import CookieConsent from "./components/CookieConsent";

import Index from "./pages/Index";

const Register = lazy(() => import("./pages/Register"));
const Login = lazy(() => import("./pages/Login"));
const Tarot = lazy(() => import("./pages/Tarot"));
const Formulaire = lazy(() => import("./pages/Formulaire"));
const Apercu = lazy(() => import("./pages/Apercu"));
const Paiement = lazy(() => import("./pages/Paiement"));
const PaiementSucces = lazy(() => import("./pages/PaiementSucces"));
const Resultats = lazy(() => import("./pages/Resultats"));
const TirageTarot = lazy(() => import("./pages/TirageTarot"));
const TarotOuiNon = lazy(() => import("./pages/TarotOuiNon"));
const Tarologie = lazy(() => import("./pages/Tarologie"));
const Numerologie = lazy(() => import("./pages/Numerologie"));
const KarmaDestin = lazy(() => import("./pages/KarmaDestin"));
const Horoscope = lazy(() => import("./pages/Horoscope"));
const Compatibilite = lazy(() => import("./pages/Compatibilite"));
const Compatibilite2 = lazy(() => import("./pages/Compatibilite2"));
const Cercle = lazy(() => import("./pages/Cercle"));
const Quotidien = lazy(() => import("./pages/Quotidien"));
const BuyCredits = lazy(() => import("./pages/BuyCredits"));
const CreditSuccess = lazy(() => import("./pages/CreditSuccess"));
const Choix = lazy(() => import("./pages/Choix"));
const Livre = lazy(() => import("./pages/Livre"));
const CommandeSucces = lazy(() => import("./pages/CommandeSucces"));
const PremiumLanding = lazy(() => import("./pages/PremiumLanding"));
const PremiumExperience = lazy(() => import("./pages/PremiumExperience"));
const CharteConfiance = lazy(() => import("./pages/CharteConfiance"));
const MonCompte = lazy(() => import("./pages/MonCompte"));
const Admin = lazy(() => import("./pages/Admin"));
const Energie = lazy(() => import("./pages/Energie"));
const Premium = lazy(() => import("./pages/Premium"));
const ChatIA = lazy(() => import("./pages/ChatIA"));
const Oracle = lazy(() => import("./pages/Oracle"));
const MonRituel = lazy(() => import("./pages/MonRituel"));
const RevolutionSolaire = lazy(() => import("./pages/RevolutionSolaire"));
const LoveLanguages = lazy(() => import("./pages/LoveLanguages"));
const AstrologieVedique = lazy(() => import("./pages/AstrologieVedique"));
const MotDePasseOublie = lazy(() => import("./pages/MotDePasseOublie"));
const ReinitialiserMotDePasse = lazy(() => import("./pages/ReinitialiserMotDePasse"));
const NotreCadre = lazy(() => import("./pages/NotreCadre"));
const SynastrieSales = lazy(() => import("./pages/SynastrieSales"));
const SynastrieSucces = lazy(() => import("./pages/SynastrieSucces"));
const AstroSexo = lazy(() => import("./pages/AstroSexo"));
const Bibliotheque = lazy(() => import("./pages/Bibliotheque"));
const Desabonnement = lazy(() => import("./pages/Desabonnement"));

const RouteFallback = (
  <div className="min-h-screen flex items-center justify-center" style={{ background: "#0C0918", color: "#B8B0C8" }}>
    Chargement...
  </div>
);

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ErrorBoundary>
          <Navbar />
        </ErrorBoundary>
        <ErrorBoundary>
          <TrialBanner />
        </ErrorBoundary>
        <Suspense fallback={RouteFallback}>
          <Routes>
            <Route path="/admin" element={<Admin />} />
            <Route path="/bibliotheque" element={<Bibliotheque />} />

            <Route
              path="*"
              element={
                <>
                  <ErrorBoundary>
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
                      <Route path="/astrologie-vedique" element={<AstrologieVedique />} />
                      <Route path="/mot-de-passe-oublie" element={<MotDePasseOublie />} />
                      <Route path="/reinitialiser-mot-de-passe" element={<ReinitialiserMotDePasse />} />
                      <Route path="/notre-cadre" element={<NotreCadre />} />
                      <Route path="/cercle" element={<Cercle />} />
                      <Route path="/synastrie" element={<SynastrieSales />} />
                      <Route path="/synastrie/succes" element={<SynastrieSucces />} />
                      <Route path="/astrosexo" element={<AstroSexo />} />
                      <Route path="/desabonnement" element={<Desabonnement />} />
                    </Routes>
                  </ErrorBoundary>
                  <PremiumStickyCTA />
                  <CookieConsent />
                </>
              }
            />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
