import "@/App.css";
import "@/index.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";

// Components
import Navbar from "@/components/Navbar";
import StarField from "@/components/StarField/StarField";
import SEO from "@/components/SEO";

// Pages
import Index from "@/pages/Index";
import Formulaire from "@/pages/Formulaire";
import Apercu from "@/pages/Apercu";
import Choix from "@/pages/Choix";
import Paiement from "@/pages/Paiement";
import PaiementSucces from "@/pages/PaiementSucces";
import Resultats from "@/pages/Resultats";
import Tarot from "@/pages/Tarot";
import Compatibilite from "@/pages/Compatibilite";
import Horoscope from "@/pages/Horoscope";
import Livre from "@/pages/Livre";
import CommandeSucces from "@/pages/CommandeSucces";
import Quotidien from "@/pages/Quotidien";
import TarotOuiNon from "@/pages/TarotOuiNon";
import Tarologie from "@/pages/Tarologie";
import Compatibilite2 from "@/pages/Compatibilite2";
import Numerologie from "@/pages/Numerologie";
import PremiumLanding from "@/pages/PremiumLanding";
import PremiumExperience from "@/pages/PremiumExperience";
import CharteConfiance from "@/pages/CharteConfiance";
import TirageTarot from "@/pages/TirageTarot";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import BuyCredits from "@/pages/BuyCredits";
import CreditSuccess from "@/pages/CreditSuccess";
import Cercle from "@/pages/Cercle";
import MonCompte from "@/pages/MonCompte";
// 404 Component
const NotFound = () => (
  <div className="min-h-screen flex items-center justify-center px-6">
    <div className="text-center">
      <h1 className="text-6xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300 }}>404</h1>
      <p className="text-sm mb-8" style={{ color: 'var(--pa-muted)' }}>Cette page n'existe pas</p>
      <a href="/" className="btn-editorial inline-flex">
      Retourner &agrave; l'accueil
      </a>
    </div>
  </div>
);

function App() {
  return (
    <div className="App min-h-screen relative" style={{ background: 'linear-gradient(180deg, #0F0D1A 0%, #0B091A 50%, #0F0D1A 100%)' }}>
      <StarField count={60} />
      <BrowserRouter>
        <AuthProvider>
          <Navbar />
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/connexion" element={<Login />} />
            <Route path="/inscription" element={<Register />} />
            <Route path="/acheter-credits" element={<BuyCredits />} />
            <Route path="/credits/succes" element={<CreditSuccess />} />
            <Route path="/cercle" element={<Cercle />} />
            <Route path="/formulaire" element={<Formulaire />} />
            <Route path="/apercu" element={<Apercu />} />
            <Route path="/choix" element={<Choix />} />
            <Route path="/paiement" element={<Paiement />} />
            <Route path="/paiement/succes" element={<PaiementSucces />} />
            <Route path="/resultats" element={<Resultats />} />
            <Route path="/livre" element={<Livre />} />
            <Route path="/commande/succes" element={<CommandeSucces />} />
            <Route path="/tarot" element={<Tarot />} />
            <Route path="/compatibilite" element={<Compatibilite />} />
            <Route path="/horoscope" element={<Horoscope />} />
            <Route path="/quotidien" element={<Quotidien />} />
            <Route path="/tarot-oui-non" element={<TarotOuiNon />} />
            <Route path="/tarologie" element={<Tarologie />} />
            <Route path="/compatibilite-amoureuse" element={<Compatibilite2 />} />
            <Route path="/numerologie" element={<Numerologie />} />
            <Route path="/premium" element={<PremiumLanding />} />
            <Route path="/premium/experience" element={<PremiumExperience />} />
            <Route path="/charte-de-confiance" element={<CharteConfiance />} />
            <Route path="/tirage-tarot" element={<TirageTarot />} />
            <Route path="/mon-compte" element={<MonCompte />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
