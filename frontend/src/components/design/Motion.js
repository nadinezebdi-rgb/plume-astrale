import React from 'react';
import { motion } from 'framer-motion';

/**
 * SectionTransition — transitions brumeuses entre sections.
 * Radial gradient alpha or 0→10% pour effet "flottant", sans coupure franche.
 * À placer entre chaque grande section de la homepage.
 */
export const SectionTransition = ({ height = 120 }) => (
  <div
    aria-hidden="true"
    style={{
      position: 'relative',
      width: '100%',
      height,
      pointerEvents: 'none',
      background:
        'radial-gradient(ellipse 60% 100% at 50% 50%, rgba(212,175,55,0.08) 0%, rgba(212,175,55,0.03) 40%, transparent 75%)',
    }}
  />
);

/**
 * FadeInUp — wrapper motion pour animer les enfants au scroll.
 * Cascade 60ms par default.
 */
export const FadeInUp = ({ children, delay = 0, y = 24, ...rest }) => (
  <motion.div
    initial={{ opacity: 0, y }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: '-80px' }}
    transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}
    {...rest}
  >
    {children}
  </motion.div>
);

/**
 * StaggerGroup — anime les enfants en cascade 60ms.
 * Usage: <StaggerGroup><FadeInUp>...</FadeInUp><FadeInUp>...</FadeInUp></StaggerGroup>
 */
export const StaggerGroup = ({ children, staggerMs = 60, initialDelay = 0, ...rest }) => (
  <motion.div
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true, margin: '-80px' }}
    variants={{
      hidden: {},
      visible: {
        transition: {
          staggerChildren: staggerMs / 1000,
          delayChildren: initialDelay,
        },
      },
    }}
    {...rest}
  >
    {React.Children.map(children, (child, i) => (
      <motion.div
        key={i}
        variants={{
          hidden: { opacity: 0, y: 22 },
          visible: {
            opacity: 1,
            y: 0,
            transition: { duration: 0.65, ease: [0.22, 1, 0.36, 1] },
          },
        }}
      >
        {child}
      </motion.div>
    ))}
  </motion.div>
);

export default SectionTransition;
