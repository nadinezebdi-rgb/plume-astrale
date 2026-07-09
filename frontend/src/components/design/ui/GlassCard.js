import React from 'react';

/**
 * GlassCard — Card avec glassmorphism signature Plume Astrale.
 * Fond translucide + backdrop-blur + bordure 1px or 20%.
 *
 * @param {boolean} featured — true pour la variante Pack Clarte (glow subtil).
 */
export const GlassCard = React.forwardRef(({
  children, featured = false, className = '', as: Comp = 'div', ...props
}, ref) => (
  <Comp
    ref={ref}
    className={`${featured ? 'plume-glass-featured' : 'plume-glass'} p-6 md:p-8 ${className}`}
    {...props}
  >
    {children}
  </Comp>
));
GlassCard.displayName = 'GlassCard';

export default GlassCard;
