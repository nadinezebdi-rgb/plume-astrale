import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider, CartCheckoutBridge } from "./context/CartContext";

import Navbar from "./components/NavbarV2";
import TrialBanner from "./components/TrialBanner";

// AUDIT P2 (2026-10-30 · Nao) : Code splitting pour LCP mobile <2.5s
// Seules la home immersive + le catch-all 404 restent eager (99 % des landings).
// Toutes les autres pages sont chargées à la demande (React.lazy).
import HomeExperienceV3 from "./pages/HomeExperienceV3";
import NotFound from "./pages/NotFound";

const Index = React.lazy(() => import("./pages/Homepage"));
const ABTestHome = React.lazy(() => import("./components/ABTestHome"));
const LectureCompleteSucces = React.lazy(() => import("./pages/LectureCompleteSucces"));
const AuthPage = React.lazy(() => import("./pages/AuthPage"));
const Tarot = React.lazy(() => import("./pages/Tarot"));
const Formulaire = React.lazy(() => import("./pages/Formulaire"));
const Apercu = React.lazy(() => import("./pages/Apercu"));
const Paiement = React.lazy(() => import("./pages/Paiement"));
const PaiementSucces = React.lazy(() => import("./pages/PaiementSucces"));
const Resultats = React.lazy(() => import("./pages/Resultats"));
const TirageTarot = React.lazy(() => import("./pages/TirageTarot"));
const TiragePartage = React.lazy(() => import("./pages/TiragePartage"));
const TarotOuiNon = React.lazy(() => import("./pages/TarotOuiNon"));
const TarotCroixCeltique = React.lazy(() => import("./pages/TarotCroixCeltique"));
const TarotAmour = React.lazy(() => import("./pages/TarotAmour"));
const Tarologie = React.lazy(() => import("./pages/Tarologie"));
const Numerologie = React.lazy(() => import("./pages/Numerologie"));
const Archetype = React.lazy(() => import("./pages/Archetype"));
const KabbaleSales = React.lazy(() => import("./pages/KabbaleSales"));
const VoyageKarmiqueSales = React.lazy(() => import("./pages/VoyageKarmiqueSales"));
const VoyageKarmiqueSucces = React.lazy(() => import("./pages/VoyageKarmiqueSucces"));
const ThemeNatalLuxe = React.lazy(() => import("./pages/ThemeNatalLuxe"));
const NosLivres = React.lazy(() => import("./pages/NosLivres"));
const Blog = React.lazy(() => import("./pages/Blog"));
const BlogArticle = React.lazy(() => import("./pages/BlogArticle"));
const Decouvrir = React.lazy(() => import("./pages/Decouvrir"));
const FAQ = React.lazy(() => import("./pages/FAQ"));
const CartPage = React.lazy(() => import("./pages/CartPage"));
const Manifesto = React.lazy(() => import("./pages/Manifesto"));
const Barometre2026 = React.lazy(() => import("./pages/Barometre2026"));
const HoroscopeSign = React.lazy(() => import("./pages/HoroscopeSign"));
const Contact = React.lazy(() => import("./pages/Contact"));
const MentionsLegales = React.lazy(() => import("./pages/MentionsLegales"));
const CGV = React.lazy(() => import("./pages/CGV"));
const Confidentialite = React.lazy(() => import("./pages/Confidentialite"));
const KabbaleSucces = React.lazy(() => import("./pages/KabbaleSucces"));
const AstrocartographieSales = React.lazy(() => import("./pages/AstrocartographieSales"));
const AstrocartographieSucces = React.lazy(() => import("./pages/AstrocartographieSucces"));
const PackKarmique = React.lazy(() => import("./pages/PackKarmique"));
const PackKarmiqueSucces = React.lazy(() => import("./pages/PackKarmiqueSucces"));
const KarmaDestin = React.lazy(() => import("./pages/KarmaDestin"));
const Horoscope = React.lazy(() => import("./pages/Horoscope"));
const Compatibilite = React.lazy(() => import("./pages/Compatibilite"));
const Compatibilite2 = React.lazy(() => import("./pages/Compatibilite2"));
const Cercle = React.lazy(() => import("./pages/Cercle"));
const Quotidien = React.lazy(() => import("./pages/Quotidien"));
const CercleSolena = React.lazy(() => import("./pages/CercleSolena"));
const AnalyticsAdmin = React.lazy(() => import("./pages/AnalyticsAdmin"));
const AdminPaymentsHealth = React.lazy(() => import("./pages/AdminPaymentsHealth"));
const BuyCredits = React.lazy(() => import("./pages/BuyCredits"));
const CreditSuccess = React.lazy(() => import("./pages/CreditSuccess"));
const Choix = React.lazy(() => import("./pages/Choix"));
const CharteConfiance = React.lazy(() => import("./pages/CharteConfiance"));
const MonCompte = React.lazy(() => import("./pages/MonCompte"));
const Temoignage = React.lazy(() => import("./pages/Temoignage"));
const TemoignagesPublic = React.lazy(() => import("./pages/TemoignagesPublic"));
const Admin = React.lazy(() => import("./pages/Admin"));
const Energie = React.lazy(() => import("./pages/Energie"));
const ChatIA = React.lazy(() => import("./pages/ChatIA"));
const Oracle = React.lazy(() => import("./pages/Oracle"));
const MonRituel = React.lazy(() => import("./pages/MonRituel"));
const RevolutionSolaire = React.lazy(() => import("./pages/RevolutionSolaire"));
const LoveLanguages = React.lazy(() => import("./pages/LoveLanguages"));
const MotDePasseOublie = React.lazy(() => import("./pages/MotDePasseOublie"));
const ReinitialiserMotDePasse = React.lazy(() => import("./pages/ReinitialiserMotDePasse"));
const NotreCadre = React.lazy(() => import("./pages/NotreCadre"));
const SynastrieSales = React.lazy(() => import("./pages/SynastrieSales"));
const SynastrieSucces = React.lazy(() => import("./pages/SynastrieSucces"));
const SynastrieLeadThanks = React.lazy(() => import("./pages/SynastrieLeadThanks"));
const SynastrieCheckout = React.lazy(() => import("./pages/SynastrieCheckout"));
const AstroSexo = React.lazy(() => import("./pages/AstroSexo"));
const RencontresAstrales = React.lazy(() => import("./pages/RencontresAstrales"));
const RencontresUltimeSucces = React.lazy(() => import("./pages/RencontresUltimeSucces"));
const Bibliotheque = React.lazy(() => import("./pages/Bibliotheque"));
const Desabonnement = React.lazy(() => import("./pages/Desabonnement"));
const ComposerPage = React.lazy(() => import("./pages/ComposerPage"));
const ComposerSucces = React.lazy(() => import("./pages/ComposerSucces"));
const MonLivrePage = React.lazy(() => import("./pages/MonLivrePage"));
const AuthenticatedHome = React.lazy(() => import("./pages/AuthenticatedHome"));
const CTATestPage = React.lazy(() => import("./pages/CTATestPage"));
const CreditsInfo = React.lazy(() => import("./pages/CreditsInfo"));
const LivresLanding = React.lazy(() => import("./pages/LivresLanding"));
const AdminPdfTest = React.lazy(() => import("./pages/AdminPdfTest"));
const AdminQrStats = React.lazy(() => import("./pages/AdminQrStats"));
const AdminLuluOrders = React.lazy(() => import("./pages/AdminLuluOrders"));
const AdminAlerts = React.lazy(() => import("./pages/AdminAlerts"));
const GiftCardPurchase = React.lazy(() => import("./pages/GiftCardPurchase"));
const GiftCardRedeem = React.lazy(() => import("./pages/GiftCardRedeem"));
const EditionRelieeMerci = React.lazy(() => import("./pages/EditionRelieeMerci"));
const RelectureRefus = React.lazy(() => import("./pages/RelectureRefus"));
const ExperiencePage = React.lazy(() => import("./pages/Experience"));

// ─── Advanced PDF Products ────────────────────────────
const NumerologiePDF = React.lazy(() => import("./pages/NumerologiePDF"));
const NumerologieWaiting = React.lazy(() => import("./pages/NumerologieWaiting"));
const KarmaDestinPDF = React.lazy(() => import("./pages/KarmaDestinPDF"));
const KarmaDestinWaiting = React.lazy(() => import("./pages/KarmaDestinWaiting"));
// ThemeNatal one-shot 24€
const ThemeNatalOneshot = React.lazy(() => import("./pages/ThemeNatalOneshot"));
const ThemeNatalOneshotSucces = React.lazy(() => import("./pages/ThemeNatalOneshotSucces"));
const NatalPrintBump = React.lazy(() => import("./pages/NatalPrintBump"));
// Trio Découverte 79€
const TrioDecouverte = React.lazy(() => import("./pages/TrioDecouverte"));
const TrioDecouverteSucces = React.lazy(() => import("./pages/TrioDecouverteSucces"));
// Duo Complémentaire 50€
const DuoCompletionSucces = React.lazy(() => import("./pages/DuoCompletionSucces"));

import RouteTracker from "./components/RouteTracker";
import Footer from "./components/FooterV2";
import SupportChat from "./components/SupportChat";
import ScrollToTop from "./components/ScrollToTop";
import CookieConsent from "./components/CookieConsent";

// ─── Plume Design System v2 (Feb 2026) ────────────────────────────
import NoiseOverlay from "./components/design/NoiseOverlay";
import Starfield from "./components/design/Starfield";
import MobileTabBar from "./components/design/MobileTabBar";
import AuraProvider from "./components/design/AuraProvider";
import LiveSalesCounter from "./components/LiveSalesCounter";
import { captureReferralFromURL } from "./lib/referral";
import ShootingStars from "./components/design/ShootingStars";
import { useLocation } from "react-router-dom";

function GlobalOverlays() {
  const location = useLocation();
  // Landing v3 a sa propre topbar + pas d'artefacts de fausse urgence
  const isLanding = location.pathname === '/';
  return (
    <>
      <Starfield />
      <ShootingStars />
      <NoiseOverlay />
      {!isLanding && <MobileTabBar />}
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
      <CartProvider>
      <AuraProvider>
      <BrowserRouter>
        {/* AUDIT P2-8 (2026-10-30 · Nao) : lien d'évitement RGAA 12.7 */}
        <a href="#main-content" className="skip-link" data-testid="skip-link">Aller au contenu</a>
        {/* ─── Overlays globaux Plume Design System v2 ─── */}
        <ScrollToTop />
        <GlobalOverlays />
        <RouteTracker />
        <Navbar />
        <CookieConsent />
        <main id="main-content" tabIndex="-1" style={{ outline: 'none' }}>
        <React.Suspense fallback={
          <div style={{
            minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'Cormorant Garamond, serif', color: 'rgba(240,230,211,0.6)', fontSize: 15,
            letterSpacing: '0.08em',
          }} aria-live="polite" data-testid="route-suspense-fallback">
            <span style={{ opacity: 0.75 }}>Chargement…</span>
          </div>
        }>
        <Routes>
          {/* Pages sans Navbar (home immersive, admin, funnel dédiés) */}
          <Route path="/" element={<HomeExperienceV3 />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/blog/:slug" element={<BlogArticle />} />
          <Route path="/decouvrir" element={<Decouvrir />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/panier" element={<CartPage />} />
          <Route path="/manifesto" element={<Manifesto />} />
          <Route path="/barometre-2026" element={<Barometre2026 />} />
          <Route path="/horoscope" element={<Horoscope />} />
          <Route path="/horoscope/:sign" element={<HoroscopeSign />} />
          {/* SEO Rebuild P1 (2026-02) : sous-routes semaine/mois — même composant, période lue via param */}
          <Route path="/horoscope/:sign/:period" element={<HoroscopeSign />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/mentions-legales" element={<MentionsLegales />} />
          <Route path="/cgv" element={<CGV />} />
          <Route path="/confidentialite" element={<Confidentialite />} />
          {/* Alias fréquents pour la Politique de confidentialité */}
          <Route path="/politique-de-confidentialite" element={<Navigate to="/confidentialite" replace />} />
          <Route path="/privacy" element={<Navigate to="/confidentialite" replace />} />
          <Route path="/nos-livres" element={<Navigate to="/livres" replace />} />
          <Route path="/temoignages" element={<TemoignagesPublic />} />
          <Route path="/theme-natal-luxe" element={<Navigate to="/theme-natal" replace />} />
          {/* Voyage Karmique — fusion Kabbale + Karma Destin (49€, Feb 2026 Nocturne) */}
          <Route path="/voyage-karmique" element={<VoyageKarmiqueSales />} />
          <Route path="/voyage-karmique/succes" element={<VoyageKarmiqueSucces />} />
          {/* Ancienne route Kabbale — 301 vers Voyage Karmique */}
          <Route path="/kabbale" element={<Navigate to="/voyage-karmique" replace />} />
          {/* Ancienne route Karma Destin — 301 vers Voyage Karmique */}
          <Route path="/karma-destin" element={<Navigate to="/voyage-karmique" replace />} />
          <Route path="/karma-destin-pdf" element={<Navigate to="/voyage-karmique" replace />} />
          <Route path="/astrocartographie" element={<AstrocartographieSales />} />
          <Route path="/pack-karmique" element={<PackKarmique />} />
          <Route path="/synastrie" element={<SynastrieSales />} />
          <Route path="/synastrie/checkout" element={<SynastrieCheckout />} />
          <Route path="/synastrie/extrait-envoye" element={<SynastrieLeadThanks />} />
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
          {/* Ancienne route karma-destin-pdf — 301 vers Voyage Karmique (déclaré plus haut) */}
          <Route path="/karma-destin/attente" element={<Navigate to="/voyage-karmique" replace />} />
          {/* Thème Natal one-shot 24€ */}
          <Route path="/theme-natal" element={<ThemeNatalOneshot />} />
          <Route path="/theme-natal/succes" element={<ThemeNatalOneshotSucces />} />
          {/* Bump livre relié Lulu 79€ — entrée via l'email de livraison */}
          <Route path="/natal-print" element={<NatalPrintBump />} />
          <Route path="/natal-print/merci" element={<NatalPrintBump />} />
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
                <Route path="/inscription" element={<AuthPage />} />
                <Route path="/connexion" element={<AuthPage />} />
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
                <Route path="/admin/qr-stats" element={<AdminQrStats />} />
                <Route path="/admin/lulu-orders" element={<AdminLuluOrders />} />
                <Route path="/admin/alerts" element={<AdminAlerts />} />
                <Route path="/admin/payments-health" element={<AdminPaymentsHealth />} />
                <Route path="/carte-cadeau" element={<GiftCardPurchase />} />
                <Route path="/carte-cadeau/redeem/:code" element={<GiftCardRedeem />} />
                <Route path="/carte-cadeau/merci" element={<GiftCardPurchase />} />
                <Route path="/edition-reliee" element={<Navigate to="/composer?edition=reliee" replace />} />
                <Route path="/edition-reliee/merci" element={<EditionRelieeMerci />} />
                <Route path="/relecture/:token" element={<RelectureRefus />} />
                <Route path="/experience" element={<ExperiencePage />} />
                <Route path="/home-experience-v3" element={<Navigate to="/" replace />} />

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
                <Route path="/tirage-partage/:shareId" element={<TiragePartage />} />
                <Route path="/tarot-oui-non" element={<Navigate to="/services/tarot/oui-non" replace />} />
                <Route path="/tarot" element={<Navigate to="/services/tarot" replace />} />
                <Route path="/compatibilite-amoureuse" element={<Navigate to="/services/compatibilite" replace />} />
                <Route path="/mon-rituel" element={<Navigate to="/services/rituel" replace />} />
                <Route path="/chat-astral" element={<Navigate to="/services/consultation" replace />} />
                <Route path="/compatibilite" element={<Navigate to="/services/compatibilite" replace />} />
                <Route path="/cercle-quotidien" element={<Navigate to="/communaute" replace />} />
                <Route path="/cercle-dashboard" element={<Navigate to="/communaute" replace />} />
                <Route path="/cercle" element={<Navigate to="/communaute" replace />} />
                
                <Route path="/paiement" element={<Paiement />} />
                <Route path="/paiement/succes" element={<PaiementSucces />} />
                <Route path="/resultats" element={<Resultats />} />
                <Route path="/kabbale/succes" element={<KabbaleSucces />} />
                <Route path="/astrocartographie/succes" element={<AstrocartographieSucces />} />
                <Route path="/pack-karmique/succes" element={<PackKarmiqueSucces />} />
                <Route path="/karma-destin" element={<Navigate to="/voyage-karmique" replace />} />
                <Route path="/tarologie" element={<Tarologie />} />
                <Route path="/quotidien" element={<Quotidien />} />
                <Route path="/premium" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/premium/decouvrir" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/premium/experience" element={<Navigate to="/acheter-credits" replace />} />
                <Route path="/acheter-credits" element={<BuyCredits />} />
                <Route path="/credits/succes" element={<CreditSuccess />} />
                <Route path="/livre" element={<Navigate to="/livres" replace />} />
                <Route path="/commande/succes" element={<Navigate to="/livres" replace />} />
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
                <Route path="/composer" element={<ComposerPage />} />
                <Route path="/composer/succes" element={<ComposerSucces />} />
                <Route path="/mon-compte/mon-livre" element={<MonLivrePage />} />
                {/* SEO P0 (2026-02-16) : catch-all 404 réel avec noindex */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </>
          } />
        </Routes>
        </React.Suspense>
        </main>
        <CartCheckoutBridge />
        <Footer />
      </BrowserRouter>
      </AuraProvider>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
