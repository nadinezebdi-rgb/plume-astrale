/**
 * Configuration du Nouveau Design Plume Astrale
 * 
 * Ce fichier centralise toutes les configurations du nouveau design immersif 3D
 * pour faciliter la maintenance et les mises à jour.
 */

export const NEW_DESIGN_CONFIG = {
  // ===================================================================
  // COULEURS - Palette Luxe Nocturne & Mystique
  // ===================================================================
  colors: {
    // Fond
    background: {
      primary: '#000000',      // Noir absolu
      deep: '#000000',
      light: '#050308',
    },
    
    // Or Lunaire (dégradé)
    gold: {
      primary: '#E2BF65',     // Or principal
      light: '#F4D98C',      // Or clair
      dark: '#B8860B',       // Or foncé
      glow: 'rgba(226, 191, 101, 0.3)',
    },
    
    // Aura Violet/Indigo
    aura: {
      violet: '#8B6FE6',
      violetLight: '#A78BFA',
      violetDark: '#7C6BF0',
      indigo: '#181042',
      indigoLight: '#2A1E4A',
    },
    
    // Textes
    text: {
      primary: '#FFFFFF',
      secondary: '#CBD5E1',
      muted: 'rgba(203, 213, 225, 0.6)',
      faint: 'rgba(203, 213, 225, 0.3)',
    },
    
    // Surfaces
    surface: {
      primary: 'rgba(0, 0, 0, 0.45)',
      light: 'rgba(0, 0, 0, 0.35)',
      glass: 'rgba(255, 255, 255, 0.02)',
    },
    
    // Bordures
    border: {
      gold: 'rgba(226, 191, 101, 0.18)',
      goldStrong: 'rgba(226, 191, 101, 0.35)',
      violet: 'rgba(167, 139, 250, 0.25)',
    },
  },
  
  // ===================================================================
  // TYPOGRAPHIE
  // ===================================================================
  typography: {
    fontFamily: {
      serif: 'Cinzel, Playfair Display, Cormorant Garamond, serif',
      body: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
      mystic: 'Cinzel, serif',
    },
    
    fontSize: {
      heroTitle: 'clamp(2rem, 6vw, 4rem)',
      sectionTitle: 'clamp(1.9rem, 4.5vw, 3rem)',
      body: 'clamp(0.9rem, 1.3vw, 1.1rem)',
      small: 'clamp(0.85rem, 1.2vw, 1rem)',
    },
    
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      bold: 600,
      heavy: 700,
    },
    
    letterSpacing: {
      tight: '0.01em',
      normal: '0.02em',
      wide: '0.12em',
      wider: '0.16em',
      widest: '0.22em',
    },
  },
  
  // ===================================================================
  // ANIMATIONS
  // ===================================================================
  animations: {
    duration: {
      fast: '0.2s',
      normal: '0.4s',
      slow: '0.6s',
      slower: '0.8s',
    },
    
    easing: {
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      liquid: 'cubic-bezier(0.16, 1, 0.3, 1)',
    },
    
    // Configurations des keyframes
    keyframes: {
      auroraDrift: {
        duration: '25s',
        function: 'ease-in-out',
        iterationCount: 'infinite',
        direction: 'alternate',
      },
      starsTwinkle: {
        duration: '8s',
        function: 'ease-in-out',
        iterationCount: 'infinite',
        direction: 'alternate',
      },
      glowPulse: {
        duration: '3.5s',
        function: 'ease-in-out',
        iterationCount: 'infinite',
      },
      shimmerText: {
        duration: '5s',
        function: 'linear',
        iterationCount: 'infinite',
      },
      fadeUp: {
        duration: '0.8s',
        function: 'ease-out',
        fill: 'both',
      },
      floatSoft: {
        duration: '5s',
        function: 'ease-in-out',
        iterationCount: 'infinite',
      },
      moonVibrate: {
        duration: '0.5s',
        function: 'ease-in-out',
      },
      liquidMorph: {
        duration: '4s',
        function: 'ease-in-out',
        iterationCount: 'infinite',
      },
    },
  },
  
  // ===================================================================
  // 3D CONFIGURATION
  // ===================================================================
  moon3d: {
    // Taille et position
    size: {
      diameter: 1.1,
      distance: 5.5,
      segments: 128,
    },
    
    // Rotation
    rotation: {
      mouseSensitivity: 0.4,
      autoRotation: 0.04,
      maxAngle: Math.PI * 2,
    },
    
    // Zoom
    zoom: {
      step1: 1.0,
      step2: 1.08,
      step3: 1.25,
      transitionSpeed: 0.08,
    },
    
    // Éclairage
    lighting: {
      ambient: { color: 0xffffff, intensity: 0.15 },
      keyLight: { color: 0xF4E8D2, intensity: 1.8, position: [3, 2.5, 4] },
      rimLight: { color: 0x8B6FE6, intensity: 0.4, position: [-2.5, -1.5, -2] },
      fillLight: { color: 0xD4B46A, intensity: 0.3, position: [-1, 1, 2] },
    },
    
    // Aura
    aura: {
      size: [6, 6],
      position: -1.2,
      rotationSpeed: 0.015,
      opacity: 0.85,
    },
    
    // Performance
    performance: {
      antialias: true,
      pixelRatio: 2, // Max 2 pour les écrans retina
      powerPreference: 'high-performance',
      precision: 'highp',
    },
  },
  
  // ===================================================================
  // FORMULAIRE
  // ===================================================================
  form: {
    steps: [
      { id: 1, label: "Indiquez votre jour de naissance", icon: "📅", fields: ['day', 'month', 'year'] },
      { id: 2, label: "L'heure exacte", icon: "🕒", fields: ['hour', 'minute'] },
      { id: 3, label: "Votre lieu de naissance", icon: "📍", fields: ['place'] },
    ],
    
    // Validation
    validation: {
      day: (value) => value && value.length <= 2 && parseInt(value) >= 1 && parseInt(value) <= 31,
      month: (value) => value && parseInt(value) >= 1 && parseInt(value) <= 12,
      year: (value) => value && value.length === 4 && parseInt(value) >= 1900 && parseInt(value) <= new Date().getFullYear(),
      hour: (value) => value && parseInt(value) >= 0 && parseInt(value) <= 23,
      minute: (value) => value && parseInt(value) >= 0 && parseInt(value) <= 59,
      place: (value) => value && value.trim().length >= 2,
    },
    
    // Messages d'erreur
    errorMessages: {
      day: "Jour invalide (1-31)",
      month: "Mois invalide (1-12)",
      year: "Année invalide",
      hour: "Heure invalide (0-23)",
      minute: "Minutes invalides (0-59)",
      place: "Lieu trop court",
    },
  },
  
  // ===================================================================
  // BANDEAU D'URGENCE
  // ===================================================================
  banner: {
    height: 40,
    text: "✧ OFFRE DE LANCEMENT : 20 CRÉDITS OFFERTS À L'INSCRIPTION POUR DÉCOUVRIR VOTRE AVENIR AMOUREUX ✧",
    background: 'linear-gradient(90deg, transparent 0%, rgba(226, 191, 101, 0.12) 20%, rgba(244, 217, 140, 0.18) 50%, rgba(226, 191, 101, 0.12) 80%, transparent 100%)',
    border: '1px solid rgba(226, 191, 101, 0.25)',
    shadow: '0 0 32px rgba(226, 191, 101, 0.25)',
  },
  
  // ===================================================================
  // OPTIMISATIONS MOBILE
  // ===================================================================
  mobile: {
    // Taille maximale des assets
    maxAssetSize: 1.5, // en Mo
    
    // Lazy loading
    lazyLoad: {
      enabled: true,
      threshold: 100, // pixels
    },
    
    // Touch interactions
    touch: {
      sensitivity: 0.01,
      gyroscope: true,
    },
    
    // Claviers natifs
    keyboard: {
      date: 'numeric',
      time: 'numeric',
      text: 'default',
    },
  },
  
  // ===================================================================
  // ACCESSIBILITÉ
  // ===================================================================
  accessibility: {
    focusVisible: true,
    focusOutline: '2px solid rgba(226, 191, 101, 0.5)',
    focusOffset: '2px',
    reducedMotion: true,
  },
};

export default NEW_DESIGN_CONFIG;
