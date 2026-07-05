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
import Admin from "./pages/Admin";
import Bibliotheque from "./pages/Bibliotheque";
// ... (toutes tes autres imports de pages)

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        {/* Bandeau sticky pour l'offre de lancement */}
        <StickyBanner />

        <Routes>
          {/* Page admin — sans Navbar */}
          <Route path="/admin" element={<Admin />} />
          <Route path="/bibliotheque" element={<Bibliotheque />} />

          {/* Toutes les autres pages — DEBUG: disabled */}
          {/* <Route
            path="*"
            element={
              <>
                ...
              </>
            }
          /> */}
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
