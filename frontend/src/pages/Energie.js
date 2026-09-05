import React from 'react';
import EnergyToday from '@/components/EnergyToday';
import SEO from '@/components/SEO';
import SEOServiceEnrich from '@/components/SEOServiceEnrich';

export default function Energie() {
  return (
    <>
      <SEO path="/services/energie" />
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #131840 0%, #1B2150 50%, #131840 100%)',
        paddingTop: 100,
        paddingBottom: 60,
        padding: '100px 16px 60px',
      }}>
        <EnergyToday />
      </div>
      <SEOServiceEnrich slug="energie" />
    </>
  );
}
