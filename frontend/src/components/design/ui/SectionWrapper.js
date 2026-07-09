import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';

/**
 * Section Wrapper — signature Plume Astrale.
 * Padding vertical genereux + radial-gradient de transition en background.
 * Applique un fade-in-up au scroll (cascade 80ms via staggerChildren).
 *
 * @param {string} variant — 'default' | 'alt' (radial-gradient inverse)
 * @param {string} id — identifiant HTML pour ancre / navigation
 */
const SectionWrapper = ({
  children, variant = 'default', id, className = '', containerClassName = '', ...props
}) => {
  const reduce = useReducedMotion();
  const cls = `plume-section ${variant === 'alt' ? 'plume-section-alt' : ''} ${className}`;

  return (
    <motion.section
      id={id}
      className={cls}
      initial={reduce ? false : 'hidden'}
      whileInView={reduce ? undefined : 'visible'}
      viewport={{ once: true, margin: '-100px' }}
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: {
          opacity: 1, y: 0,
          transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1], staggerChildren: 0.08 },
        },
      }}
      {...props}
    >
      <div className={`max-w-7xl mx-auto ${containerClassName}`}>
        {children}
      </div>
    </motion.section>
  );
};

export default SectionWrapper;
