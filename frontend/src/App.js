import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import Navbar from "./components/Navbar";
import TrialBanner from "./components/TrialBanner";

import Index from "./pages/Index";
import AuthPage from "./pages/AuthPage";
import Tarot from "./pages/Tarot";
import Formulaire from "./pages/Formulaire";
import Apercu from "./pages/Apercu";
import Paiement from "./pages/Paiement";
import PaiementSucces from "./pages/PaiementSucces";import Resultats from "./pages/Resultats";
import TirageTarot from "./pages/TirageTarot";
import TarotOuiNon from "./pages/TarotOuiNon";
import Tarologie from "./pages/Tarologie";
import Numerologie from "./pages/Numerologie";
import Archetype from "./pages/Archetype";
import KabbaleSales from "./pages/KabbaleSales";
import KabbaleSucces from "./pages/KabbaleSucces";
import PackKarmique from "./pages/PackKarmique";
import PackKarmiqueSucces from "./pages/PackKarmiqueSucces";
import KarmaDestin from "./pages/KarmaDestin";
import Horoscope from "./pages/Horoscope";
import Compatibilite from "./pages/Compatibilite";
import Compatibilite2 from "./pages/Compatibilite2";
import Cercle from "./pages/Cercle";import Quotidien from "./pages/Quotidien";
import BuyCredits from "./pages/BuyCredits";
import CreditSuccess from "./pages/CreditSuccess";
import Choix from "./pages/Choix";
import Livre from "./pages/Livre";
import CommandeSucces from "./pages/CommandeSucces";
import CharteConfiance from "./pages/CharteConfiance";
import MonCompte from "./pages/MonCompte";
import Admin from "./pages/Admin";
import Energie from "./pages/Energie";
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
import AuthenticatedHome from "./pages/AuthenticatedHome";
import CTATestPage from "./pages/CTATestPage";
import CookieConsent from "./components/CookieConsent";

// ─── Advanced PDF Products ────────────────────────────
import NumerologiePDF from "./pages/NumerologiePDF";
import NumerologieWaiting from "./pages/NumerologieWaiting";
import KarmaDestinPDF from "./pages/KarmaDestinPDF";
import KarmaDestinWaiting from "./pages/KarmaDestinWaiting";
import FenetreRencontrePDF from "./pages/FenetreRencontrePDF";
import FenetreRencontreWaiting from "./pages/FenetreRencontreWaiting";

// ─── Plume Design System v2 (Feb 2026) ────────────────────────────
import NoiseOverlay from "./components/design/NoiseOverlay";
import Starfield from "./components/design/Starfield";
import MobileTabBar from "./components/design/MobileTabBar";
import AuraProvider from "./components/design/AuraProvider";
import ShootingStars from "./components/design/ShootingStars";   //

function App() {
  return (
    <AuthProvider>
      <AuraProvider>
      <BrowserRouter>
        {/* ─── Overlays globaux Plume Design System v2 ─── */}
        <Starfield />
    <ShootingStars />
        <NoiseOverlay />
        <MobileTabBar />
        <Routes>
          {/* Pages sans Navbar (home immersive, admin, funnel dédiés) */}
          <Route path="/" element={<Index />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/bibliotheque" element={<Bibliotheque />} />
          <Route path="/rencontres-astrales" element={<RencontresAstrales />} />
          <Route path="/rencontres-astrales/succes" element={<RencontresUltimeSucces />} />
          <Route path="/test/cta" element={<CTATestPage />} />
          <Route path="/numerologie-pdf" element={<NumerologiePDF />} />
          <Route path="/numerologie-pdf/attente" element={<NumerologieWaiting />} />
          <Route path="/karma-destin-pdf" element={<KarmaDestinPDF />} />
          <Route path="/karma-destin/attente" element={<KarmaDestinWaiting />} />
          <Route path="/fenetre-rencontre-pdf" element={<FenetreRencontrePDF />} />
          <Route path="/fenetre-rencontre/attente" element={<FenetreRencontreWaiting />} />

          {/* Toutes les autres pages — avec Navbar */}
          <Route path="*" element={
            <>
              <Navbar />
              <Routes>
                <Route path="/inscription" element={<AuthPage />} />
                <Route path="/connexion" element={<AuthPage />} />
                <Route path="/mon-accueil" element={<AuthenticatedHome />} />
                <Route path="/formulaire" element={<Formulaire />} />
                <Route path="/apercu" element={<Apercu />} />
                <Route path="/choix" element={<Choix />} />
                
                {/* ─── Routes canoniques /outils/* ─── */}
                <Route path="/outils/theme-natal" element={<Formulaire />} />
                <Route path="/outils/tarot" element={<TirageTarot />} />
                <Route path="/outils/tarot/oui-non" element={<TarotOuiNon />} />
                <Route path="/outils/horoscope" element={<Horoscope />} />
                <Route path="/outils/numerologie" element={<Numerologie />} />
                <Route path="/outils/archetype" element={<Archetype />} />
                <Route path="/outils/compatibilite" element={<Compatibilite2 />} />
                <Route path="/outils/revolution-solaire" element={<RevolutionSolaire />} />
                <Route path="/outils/oracle" element={<Oracle />} />
                <Route path="/outils/energie" element={<Energie />} />
                <Route path="/outils/rituel" element={<MonRituel />} />
                <Route path="/outils/consultation" element={<ChatIA />} />
                <Route path="/outils/astrosexo" element={<AstroSexo />} />
                <Route path="/outils/love-languages" element={<LoveLanguages />} />
                <Route path="/communaute" element={<Cercle />} />

                {/* ─── Backward compatibility redirects ─── */}
                <Route path="/tirage-tarot" element={<Navigate to="/outils/tarot" replace />} />
                <Route path="/tarot-oui-non" element={<Navigate to="/outils/tarot/oui-non" replace />} />
                <Route path="/tarot" element={<Navigate to="/outils/tarot" replace />} />
                <Route path="/compatibilite-amoureuse" element={<Navigate to="/outils/compatibilite" replace />} />
                <Route path="/mon-rituel" element={<Navigate to="/outils/rituel" replace />} />
                <Route path="/chat-astral" element={<Navigate to="/outils/consultation" replace />} />
                <Route path="/cercle-quotidien" element={<Navigate to="/communaute" replace />} />
                <Route path="/cercle-dashboard" element={<Navigate to="/communaute" replace />} />
                <Route path="/cercle" element={<Navigate to="/communaute" replace />} />
                
                <Route path="/paiement" element={<Paiement />} />
                <Route path="/paiement/succes" element={<PaiementSucces />} />
                <Route path="/resultats" element={<Resultats />} />
                <Route path="/kabbale" element={<KabbaleSales />} />
                <Route path="/kabbale/succes" element={<KabbaleSucces />} />
                <Route path="/pack-karmique" element={<PackKarmique />} />
                <Route path="/pack-karmique/succes" element={<PackKarmiqueSucces />} />
                <Route path="/karma-destin" element={<KarmaDestin />} />
                <Route path="/tarologie" element={<Tarologie />} />
                <Route path="/quotidien" element={<Quotidien />} />
                <Route path="/premium" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/premium/decouvrir" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/premium/experience" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/acheter-credits" element={<BuyCredits />} />
                <Route path="/credits/succes" element={<CreditSuccess />} />
                <Route path="/livre" element={<Livre />} />
                <Route path="/commande/succes" element={<CommandeSucces />} />
                <Route path="/mon-compte" element={<MonCompte />} />
                <Route path="/charte-de-confiance" element={<CharteConfiance />} />
                <Route path="/consultation" element={<Navigate to="/outils/consultation" replace />} />
                <Route path="/energie" element={<Navigate to="/outils/energie" replace />} />
                <Route path="/premium/succes" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/chat-astral" element={<Navigate to="/outils/consultation" replace />} />
                <Route path="/oracle" element={<Navigate to="/outils/oracle" replace />} />
                <Route path="/mon-rituel" element={<Navigate to="/outils/rituel" replace />} />
                <Route path="/revolution-solaire" element={<Navigate to="/outils/revolution-solaire" replace />} />
                <Route path="/love-languages" element={<Navigate to="/outils/love-languages" replace />} />
                <Route path="/mot-de-passe-oublie" element={<MotDePasseOublie />} />
                <Route path="/reinitialiser-mot-de-passe" element={<ReinitialiserMotDePasse />} />
                <Route path="/notre-cadre" element={<NotreCadre />} />
                <Route path="/cercle" element={<Navigate to="/communaute" replace />} />
                <Route path="/synastrie" element={<SynastrieSales />} />
                <Route path="/synastrie/succes" element={<SynastrieSucces />} />
                <Route path="/astrosexo" element={<Navigate to="/outils/astrosexo" replace />} />
                <Route path="/desabonnement" element={<Desabonnement />} />
              </Routes>
              <CookieConsent />
            </>
          } />
        </Routes>
      </BrowserRouter>
      </AuraProvider>
    </AuthProvider>
  );
}

export default App;
