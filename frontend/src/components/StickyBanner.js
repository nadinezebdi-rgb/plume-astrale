import React from "react";

const StickyBanner = () => {
  return (
    <div
      className="fixed top-0 left-0 right-0 z-50"
      style={{
        background: "linear-gradient(90deg, #D4AF37, #AA7C11)",
        padding: "12px 24px",
        textAlign: "center",
        fontSize: "14px",
        fontWeight: "600",
        color: "#0B0E14",
        letterSpacing: "0.05em",
        boxShadow: "0 2px 12px rgba(212, 175, 55, 0.3)",
      }}
    >
      ✨ OFFRE DE LANCEMENT : 20 CRÉDITS OFFERTS À L'INSCRIPTION POUR DÉCOUVRIR VOTRE AVENIR AMOUREUX ✨
    </div>
  );
};

export default StickyBanner;
