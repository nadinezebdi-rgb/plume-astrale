import "@/App.css";
import "@/index.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Pages
import Index from "@/pages/Index";
import Formulaire from "@/pages/Formulaire";
import Apercu from "@/pages/Apercu";
import Paiement from "@/pages/Paiement";
import Resultats from "@/pages/Resultats";

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
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/formulaire" element={<Formulaire />} />
          <Route path="/apercu" element={<Apercu />} />
          <Route path="/paiement" element={<Paiement />} />
          <Route path="/resultats" element={<Resultats />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
