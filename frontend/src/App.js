import "@/App.css";
import "@/index.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

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

// 404 Component
const NotFound = () => (
  <div className="min-h-screen flex items-center justify-center px-6">
    <div className="text-center">
      <h1 className="text-6xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300 }}>404</h1>
      <p className="text-sm mb-8" style={{ color: 'var(--pa-muted)' }}>Cette page n'existe pas</p>
      <a href="/" className="btn-editorial inline-flex">
        Retourner a l'accueil
      </a>
    </div>
  </div>
);

function App() {
  return (
    <div className="App min-h-screen relative" style={{ background: 'linear-gradient(180deg, #0C0918 0%, #080614 50%, #0C0918 100%)' }}>
      <StarField count={160} />
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Index />} />
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
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
