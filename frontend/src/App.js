import "@/App.css";
import "@/index.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Components
import Navbar from "@/components/Navbar";

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

// 404 Component
const NotFound = () => (
  <div className="min-h-screen flex items-center justify-center px-4">
    <div className="text-center">
      <h1 className="text-6xl mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F3E5AB' }}>404</h1>
      <p className="text-[#E0D9F6]/70 mb-8">Cette page n'existe pas dans notre cosmos</p>
      <a href="/" className="btn-mystical rounded-full inline-block">
        Retourner à l'accueil
      </a>
    </div>
  </div>
);

function App() {
  return (
    <div className="App min-h-screen" style={{ background: 'linear-gradient(180deg, #0F0518 0%, #1A0B2E 100%)' }}>
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
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
