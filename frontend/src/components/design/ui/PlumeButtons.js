import React from 'react';

/**
 * Bouton Primary — Design System v2.
 * Or brosse + glow doux. A reserver au CTA de conversion.
 */
export const PrimaryButton = React.forwardRef(({
  children, as: Comp = 'button', className = '', ...props
}, ref) => (
  <Comp
    ref={ref}
    className={`plume-btn-primary ${className}`}
    data-cursor="hover"
    {...props}
  >
    {children}
  </Comp>
));
PrimaryButton.displayName = 'PrimaryButton';

/**
 * Bouton Secondary — bordure or, transparent.
 * Actions secondaires (En savoir plus, Retour, Annuler).
 */
export const SecondaryButton = React.forwardRef(({
  children, as: Comp = 'button', className = '', ...props
}, ref) => (
  <Comp
    ref={ref}
    className={`plume-btn-secondary ${className}`}
    data-cursor="hover"
    {...props}
  >
    {children}
  </Comp>
));
SecondaryButton.displayName = 'SecondaryButton';

/**
 * Bouton Ghost — texte lavande, sans fond.
 * Navigation, retour, actions tertiaires.
 */
export const GhostButton = React.forwardRef(({
  children, as: Comp = 'button', className = '', ...props
}, ref) => (
  <Comp
    ref={ref}
    className={`plume-btn-ghost ${className}`}
    data-cursor="hover"
    {...props}
  >
    {children}
  </Comp>
));
GhostButton.displayName = 'GhostButton';
