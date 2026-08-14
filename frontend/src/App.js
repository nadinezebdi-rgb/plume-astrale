import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import Navbar from "./components/NavbarV2";
import TrialBanner from "./components/TrialBanner";

import Index from "./pages/Homepage";
import LectureCompleteSucces from "./pages/LectureCompleteSucces";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Tarot from "./pages/Tarot";
import Formulaire from "./pages/Formulaire";
import Apercu from "./pages/Apercu";
import Paiement from "./pages/Paiement";
import PaiementSucces from "./pages/PaiementSucces";import Resultats from "./pages/Resultats";
import TirageTarot from "./pages/TirageTarot";
import TarotOuiNon from "./pages/TarotOuiNon";
import TarotCroixCeltique from "./pages/TarotCroixCeltique";
import TarotAmour from "./pages/TarotAmour";
import Tarologie from "./pages/Tarologie";
import Numerologie from "./pages/Numerologie";
import Archetype from "./pages/Archetype";
import KabbaleSales from "./pages/KabbaleSales";
import ThemeNatalLuxe from "./pages/ThemeNatalLuxe";
import NosLivres from "./pages/NosLivres";
import Blog from "./pages/Blog";
import BlogArticle from "./pages/BlogArticle";
import Decouvrir from "./pages/Decouvrir";
import Manifesto from "./pages/Manifesto";
import Barometre2026 from "./pages/Barometre2026";
import HoroscopeSign from "./pages/HoroscopeSign";
import Contact from "./pages/Contact";
import MentionsLegales from "./pages/MentionsLegales";
import CGV from "./pages/CGV";
import Footer from "./components/FooterV2";
import KabbaleSucces from "./pages/KabbaleSucces";
import AstrocartographieSales from "./pages/AstrocartographieSales";
import AstrocartographieSucces from "./pages/AstrocartographieSucces";
import PackKarmique from "./pages/PackKarmique";
import PackKarmiqueSucces from "./pages/PackKarmiqueSucces";
import KarmaDestin from "./pages/KarmaDestin";
import Horoscope from "./pages/Horoscope";
import Compatibilite from "./pages/Compatibilite";
import Compatibilite2 from "./pages/Compatibilite2";
import Cercle from "./pages/Cercle";import Quotidien from "./pages/Quotidien";
import CercleSolena from "./pages/CercleSolena";
import AnalyticsAdmin from "./pages/AnalyticsAdmin";
import BuyCredits from "./pages/BuyCredits";
import CreditSuccess from "./pages/CreditSuccess";
import Choix from "./pages/Choix";
import CharteConfiance from "./pages/CharteConfiance";
import MonCompte from "./pages/MonCompte";
import Temoignage from "./pages/Temoignage";
import TemoignagesPublic from "./pages/TemoignagesPublic";
import SupportChat from "./components/SupportChat";
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
import CreditsInfo from "./pages/CreditsInfo";
import LivresLanding from "./pages/LivresLanding";
import AdminPdfTest from "./pages/AdminPdfTest";
import CookieConsent from "./components/CookieConsent";

// ─── Advanced PDF Products ────────────────────────────
import NumerologiePDF from "./pages/NumerologiePDF";
import NumerologieWaiting from "./pages/NumerologieWaiting";
import KarmaDestinPDF from "./pages/KarmaDestinPDF";
import KarmaDestinWaiting from "./pages/KarmaDestinWaiting";
// ThemeNatal one-shot 29€ (Gary Vee refonte Feb 2026)
import ThemeNatalOneshot from "./pages/ThemeNatalOneshot";
import ThemeNatalOneshotSucces from "./pages/ThemeNatalOneshotSucces";
// Trio Découverte 79€ (Gary Vee refonte Feb 2026)
import TrioDecouverte from "./pages/TrioDecouverte";
import TrioDecouverteSucces from "./pages/TrioDecouverteSucces";
// Duo Complémentaire 50€ (cross-sell post-Thème Natal, Gary Vee Feb 2026)
import DuoCompletionSucces from "./pages/DuoCompletionSucces";

// ─── Plume Design System v2 (Feb 2026) ────────────────────────────
import NoiseOverlay from "./components/design/NoiseOverlay";
import Starfield from "./components/design/Starfield";
import MobileTabBar from "./components/design/MobileTabBar";
import AuraProvider from "./components/design/AuraProvider";
import LiveSalesCounter from "./components/LiveSalesCounter";
import { captureReferralFromURL } from "./lib/referral";
import { useLocation } from "react-router-dom";

function GlobalOverlays() {
  const location = useLocation();
  // Landing v3 a sa propre topbar + pas d'artefacts de fausse urgence
  const isLanding = location.pathname === '/';
  return (
    <>
      <Starfield />
      <NoiseOverlay />
      <MobileTabBar />
      {!isLanding && <LiveSalesCounter />}
      <SupportChat />
    </>
  );
}

function App() {
  // Capture ?ref=CODE au tout premier render de l'app (avant même le login)
  React.useEffect(() => { captureReferralFromURL(); }, []);
  return (
    <AuthProvider>
      <AuraProvider>
      <BrowserRouter>
        {/* ─── Overlays globaux Plume Design System v2 ─── */}
        <GlobalOverlays />
        <Navbar />
        <Routes>
          {/* Pages sans Navbar (home immersive, admin, funnel dédiés) */}
          <Route path="/" element={<Index />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/blog/:slug" element={<BlogArticle />} />
          <Route path="/decouvrir" element={<Decouvrir />} />
          <Route path="/manifesto" element={<Manifesto />} />
          <Route path="/barometre-2026" element={<Barometre2026 />} />
          <Route path="/horoscope" element={<Horoscope />} />
          <Route path="/horoscope/:sign" element={<HoroscopeSign />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/mentions-legales" element={<MentionsLegales />} />
          <Route path="/cgv" element={<CGV />} />
          <Route path="/nos-livres" element={<NosLivres />} />
          <Route path="/temoignages" element={<TemoignagesPublic />} />
          <Route path="/theme-natal-luxe" element={<ThemeNatalLuxe />} />
          <Route path="/kabbale" element={<KabbaleSales />} />
          <Route path="/astrocartographie" element={<AstrocartographieSales />} />
          <Route path="/pack-karmique" element={<PackKarmique />} />
          <Route path="/synastrie" element={<SynastrieSales />} />
          <Route path="/lecture-complete/succes" element={<LectureCompleteSucces />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/bibliotheque" element={<Bibliotheque />} />
          <Route path="/rencontres-astrales" element={<RencontresAstrales />} />
          <Route path="/rencontres-astrales/succes" element={<RencontresUltimeSucces />} />
          <Route path="/test/cta" element={<CTATestPage />} />
          <Route path="/credits" element={<CreditsInfo />} />
          <Route path="/livres" element={<LivresLanding />} />
          <Route path="/numerologie-pdf" element={<NumerologiePDF />} />
          <Route path="/numerologie-pdf/attente" element={<NumerologieWaiting />} />
          <Route path="/karma-destin-pdf" element={<KarmaDestinPDF />} />
          <Route path="/karma-destin/attente" element={<KarmaDestinWaiting />} />
          {/* Thème Natal one-shot 29€ (Gary Vee refonte Feb 2026) */}
          <Route path="/theme-natal" element={<ThemeNatalOneshot />} />
          <Route path="/theme-natal/succes" element={<ThemeNatalOneshotSucces />} />
          {/* Trio Découverte 79€ (Gary Vee refonte Feb 2026) */}
          <Route path="/trio-decouverte" element={<TrioDecouverte />} />
          <Route path="/trio-decouverte/succes" element={<TrioDecouverteSucces />} />
          {/* Duo Complémentaire 50€ — page succès (checkout déclenché depuis /theme-natal/succes) */}
          <Route path="/duo-completion/succes" element={<DuoCompletionSucces />} />
          {/* Anciennes routes Fenêtres de Rencontre — consolidées dans Rencontres Ultime */}
          <Route path="/fenetre-rencontre-pdf" element={<Navigate to="/rencontres-astrales" replace />} />
          <Route path="/fenetre-rencontre/attente" element={<Navigate to="/rencontres-astrales" replace />} />

          {/* Toutes les autres pages */}
          <Route path="*" element={
            <>
              <Routes>
                <Route path="/inscription" element={<Register />} />
                <Route path="/connexion" element={<Login />} />
                <Route path="/mon-accueil" element={<AuthenticatedHome />} />
                <Route path="/formulaire" element={<Formulaire />} />
                <Route path="/apercu" element={<Apercu />} />
                <Route path="/choix" element={<Choix />} />
                
                {/* ─── Routes canoniques /services/* (rebranding Feb 2026) ─── */}
                <Route path="/services/theme-natal" element={<Formulaire />} />
                <Route path="/services/tarot" element={<TirageTarot />} />
                <Route path="/services/tarot/oui-non" element={<TarotOuiNon />} />
                <Route path="/services/tarot/croix-celtique" element={<TarotCroixCeltique />} />
                <Route path="/services/tarot/amour" element={<TarotAmour />} />
                <Route path="/services/horoscope" element={<Horoscope />} />
                <Route path="/services/numerologie" element={<Numerologie />} />
                <Route path="/services/archetype" element={<Archetype />} />
                <Route path="/services/compatibilite" element={<Compatibilite2 />} />
                <Route path="/services/revolution-solaire" element={<RevolutionSolaire />} />
                <Route path="/services/oracle" element={<Oracle />} />
                <Route path="/services/energie" element={<Energie />} />
                <Route path="/services/rituel" element={<MonRituel />} />
                <Route path="/services/consultation" element={<ChatIA />} />
                <Route path="/services/astrosexo" element={<AstroSexo />} />
                <Route path="/services/love-languages" element={<LoveLanguages />} />
                <Route path="/communaute" element={<Cercle />} />
                <Route path="/cercle-solena" element={<CercleSolena />} />
                <Route path="/cercle-solena/succes" element={<CercleSolena />} />
                <Route path="/admin/analytics" element={<AnalyticsAdmin />} />
                <Route path="/admin/pdf-test" element={<AdminPdfTest />} />

                {/* ─── Redirections /outils/* → /services/* (compat legacy) ─── */}
                <Route path="/outils/theme-natal" element={<Navigate to="/services/theme-natal" replace />} />
                <Route path="/outils/tarot" element={<Navigate to="/services/tarot" replace />} />
                <Route path="/outils/tarot/oui-non" element={<Navigate to="/services/tarot/oui-non" replace />} />
                <Route path="/outils/tarot/croix-celtique" element={<Navigate to="/services/tarot/croix-celtique" replace />} />
                <Route path="/outils/tarot/amour" element={<Navigate to="/services/tarot/amour" replace />} />
                <Route path="/outils/horoscope" element={<Navigate to="/services/horoscope" replace />} />
                <Route path="/outils/numerologie" element={<Navigate to="/services/numerologie" replace />} />
                <Route path="/outils/archetype" element={<Navigate to="/services/archetype" replace />} />
                <Route path="/outils/compatibilite" element={<Navigate to="/services/compatibilite" replace />} />
                <Route path="/outils/revolution-solaire" element={<Navigate to="/services/revolution-solaire" replace />} />
                <Route path="/outils/oracle" element={<Navigate to="/services/oracle" replace />} />
                <Route path="/outils/energie" element={<Navigate to="/services/energie" replace />} />
                <Route path="/outils/rituel" element={<Navigate to="/services/rituel" replace />} />
                <Route path="/outils/consultation" element={<Navigate to="/services/consultation" replace />} />
                <Route path="/outils/astrosexo" element={<Navigate to="/services/astrosexo" replace />} />
                <Route path="/outils/love-languages" element={<Navigate to="/services/love-languages" replace />} />

                {/* ─── Backward compatibility redirects ─── */}
                <Route path="/tirage-tarot" element={<Navigate to="/services/tarot" replace />} />
                <Route path="/tarot-oui-non" element={<Navigate to="/services/tarot/oui-non" replace />} />
                <Route path="/tarot" element={<Navigate to="/services/tarot" replace />} />
                <Route path="/compatibilite-amoureuse" element={<Navigate to="/services/compatibilite" replace />} />
                <Route path="/mon-rituel" element={<Navigate to="/services/rituel" replace />} />
                <Route path="/chat-astral" element={<Navigate to="/services/consultation" replace />} />
                <Route path="/cercle-quotidien" element={<Navigate to="/communaute" replace />} />
                <Route path="/cercle-dashboard" element={<Navigate to="/communaute" replace />} />
                <Route path="/cercle" element={<Navigate to="/communaute" replace />} />
                
                <Route path="/paiement" element={<Paiement />} />
                <Route path="/paiement/succes" element={<PaiementSucces />} />
                <Route path="/resultats" element={<Resultats />} />
                <Route path="/kabbale/succes" element={<KabbaleSucces />} />
                <Route path="/astrocartographie/succes" element={<AstrocartographieSucces />} />
                <Route path="/pack-karmique/succes" element={<PackKarmiqueSucces />} />
                <Route path="/karma-destin" element={<KarmaDestin />} />
                <Route path="/tarologie" element={<Tarologie />} />
                <Route path="/quotidien" element={<Quotidien />} />
                <Route path="/premium" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/premium/decouvrir" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/premium/experience" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/acheter-credits" element={<BuyCredits />} />
                <Route path="/credits/succes" element={<CreditSuccess />} />
                <Route path="/livre" element={<Navigate to="/nos-livres" replace />} />
                <Route path="/commande/succes" element={<Navigate to="/nos-livres" replace />} />
                <Route path="/mon-compte" element={<MonCompte />} />
                <Route path="/temoignage" element={<Temoignage />} />
                <Route path="/charte-de-confiance" element={<CharteConfiance />} />
                <Route path="/consultation" element={<Navigate to="/services/consultation" replace />} />
                <Route path="/energie" element={<Navigate to="/services/energie" replace />} />
                <Route path="/premium/succes" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/chat-astral" element={<Navigate to="/services/consultation" replace />} />
                <Route path="/oracle" element={<Navigate to="/services/oracle" replace />} />
                <Route path="/mon-rituel" element={<Navigate to="/services/rituel" replace />} />
                <Route path="/revolution-solaire" element={<Navigate to="/services/revolution-solaire" replace />} />
                <Route path="/love-languages" element={<Navigate to="/services/love-languages" replace />} />
                <Route path="/mot-de-passe-oublie" element={<MotDePasseOublie />} />
                <Route path="/reinitialiser-mot-de-passe" element={<ReinitialiserMotDePasse />} />
                <Route path="/notre-cadre" element={<NotreCadre />} />
                <Route path="/cercle" element={<Navigate to="/communaute" replace />} />
                <Route path="/synastrie/succes" element={<SynastrieSucces />} />
                <Route path="/astrosexo" element={<Navigate to="/services/astrosexo" replace />} />
                <Route path="/desabonnement" element={<Desabonnement />} />
              </Routes>
              <CookieConsent />
            </>
          } />
        </Routes>
        <Footer />
      </BrowserRouter>
      </AuraProvider>
    </AuthProvider>
  );
}

export default App;
