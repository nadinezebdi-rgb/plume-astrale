import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import Navbar from "./components/Navbar";

// pages
import Index from "./pages/Index";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Tarot from "./pages/Tarot";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
<Routes>
          <Route path="/" element={<Index />} />
          <Route path="/inscription" element={<Register />} />
          <Route path="/connexion" element={<Login />} />
          <Route path="/tarot" element={<Tarot />} />
        </Routes>

      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
