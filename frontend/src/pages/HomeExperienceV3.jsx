/**
 * HomeExperienceV3 — Page shell (Phase 1)
 *
 * Route : /home-experience-v3
 * Meta  : noindex (tant que non validé pour prod)
 *
 * Phase 1 rend uniquement les Actes I → IV (identiques aux 4 scènes
 * de /experience) enrichis d'une navigation verticale des actes.
 * Phase 2 ajoutera les Actes V-VIII (Univers services, Personnalisation,
 * Conversion, Rassurance) sans remplacer cette route.
 */
import React from 'react';
import SEO from '@/components/SEO';
import HomeExperienceRoot from '@/home-experience/HomeExperienceRoot';

export default function HomeExperienceV3() {
  return (
    <>
      <SEO
        path="/home-experience-v3"
        title="Prototype · Plume Astrale"
        description="Prototype homepage immersive Plume Astrale — non-indexé."
        noindex
      />
      <HomeExperienceRoot />
    </>
  );
}
