import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";

// pages
import Index from "./pages/Index";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Tarot from "./pages/Tarot";

// fallback simple
const NotFound = () => (
  <div style={{ color: "white", textAlign: "center", marginTop: "100px" }}>
    Page non trouvée
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: "100vh", background: "#0C0918" }}>

        {/* Navbar */}
        <Navbar />

        {/* ROUTES */}
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/inscription" element={<Register />} />
          <Route path="/connexion" element={<Login />} />
          <Route path="/tarot" element={<Tarot />} />

          {/* fallback */}
          <Route path="/" element={<div style={{color:"white"}}>SITE OK</div>} />
        </Routes>

      </div>
    </BrowserRouter>
  );
}

export default App;
