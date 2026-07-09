import { useAstralElement } from '@/hooks/useAstralElement';

/**
 * Wrapper qui active l'Aura Connectee — teinte subtilement l'app selon
 * l'element astral (feu / eau / air / terre) de l'utilisateur connecte.
 * A monter A L'INTERIEUR de AuthProvider.
 */
const AuraProvider = ({ children }) => {
  useAstralElement();
  return children;
};

export default AuraProvider;
