import React, { useEffect, useState } from 'react';
import QuickOracleDebug from '../components/QuickOracleDebug';

/**
 * CTATestPage - Page de débogage du 1er CTA
 * Trace chaque étape du flux QuickOracle → Packs → Checkout
 */
export default function CTATestPage() {
  const [showOracle, setShowOracle] = useState(false);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    // Clear previous logs
    localStorage.setItem('qo_logs', '[]');
    console.log('[CTATest] Page montée - Logs réinitialisés');
  }, []);

  useEffect(() => {
    // Poll logs every 500ms
    const interval = setInterval(() => {
      try {
        const qologs = JSON.parse(localStorage.getItem('qo_logs') || '[]');
        setLogs(qologs);
      } catch (e) { /* ignore */ }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const handleSelectPack = (packId) => {
    console.log(`[CTATest] onSelectPack called with packId:`, packId);
    alert(`Pack sélectionné: ${packId}\n\nVérifiez la console (F12) pour les logs complets.\n\n✅ REDIRECTION EN COURS...`);
    
    // Redirect to payment (same as production)
    const packMap = {
      initiation: 'essentiel',
      clarte: 'premium',
      flammes: 'premium'
    };
    localStorage.setItem('plume_astrale_plan', packMap[packId]);
    console.log(`[CTATest] Plan stocké: ${packMap[packId]}`);
    
    // Simulate production redirect
    setTimeout(() => {
      window.location.href = '/paiement';
    }, 300);
  };

  return (
    <div style={{
      background: '#000',
      color: '#fff',
      minHeight: '100vh',
      padding: '40px 20px',
      fontFamily: 'Inter, sans-serif',
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '40px', borderBottom: '1px solid #333', paddingBottom: '20px' }}>
          <h1 style={{ margin: 0, marginBottom: '10px', fontSize: '2rem' }}>
            🧪 CTA Test Page
          </h1>
          <p style={{ margin: 0, color: '#999', fontSize: '0.9rem' }}>
            Test et débogage du flux: CTA → QuickOracle → Packs → Checkout
          </p>
        </div>

        {/* Main content */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' }}>
          
          {/* Left: Test Controls */}
          <div>
            <h2 style={{ marginTop: 0 }}>Test Controls</h2>
            
            <div style={{
              background: 'rgba(212,175,55,0.1)',
              border: '1px solid rgba(212,175,55,0.3)',
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '20px',
            }}>
              <h3 style={{ marginTop: 0, color: '#D4AF37' }}>Étape 1: Lancer QuickOracle</h3>
              <p style={{ color: '#ccc', fontSize: '0.9rem' }}>
                Cliquez sur le bouton ci-dessous pour ouvrir QuickOracle (avec logs détaillés)
              </p>
              <button
                onClick={() => {
                  console.log('[CTATest] CTA button clicked');
                  setShowOracle(true);
                }}
                style={{
                  width: '100%',
                  padding: '12px 24px',
                  background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                  color: '#0C0918',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '1rem',
                }}
              >
                ✨ Découvrez votre oracle du jour GRATUITEMENT
              </button>
            </div>

            {/* Instructions */}
            <div style={{
              background: 'rgba(100,150,200,0.1)',
              border: '1px solid rgba(100,150,200,0.3)',
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '20px',
            }}>
              <h3 style={{ marginTop: 0, color: '#64B5F6' }}>Instructions de test</h3>
              <ol style={{ margin: 0, paddingLeft: '20px', color: '#ccc' }}>
                <li>Cliquez sur le CTA "Découvrez votre oracle"</li>
                <li>Sélectionnez un signe zodiacal</li>
                <li>Lisez l'oracle généré</li>
                <li>Cliquez "Voir la lecture COMPLÈTE"</li>
                <li>Vérifiez que les 3 packs s'affichent</li>
                <li>Cliquez sur un pack (ex: "Débloquer Clarté")</li>
                <li>Vérifiez l'alerte et les logs</li>
              </ol>
            </div>

            {/* Problème à corriger */}
            <div style={{
              background: 'rgba(200,50,50,0.1)',
              border: '1px solid rgba(200,50,50,0.3)',
              borderRadius: '12px',
              padding: '20px',
            }}>
              <h3 style={{ marginTop: 0, color: '#EF5350' }}>❌ Problèmes possibles</h3>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#ccc', fontSize: '0.9rem' }}>
                <li>CTA button ne déclenche rien → Vérifier onClick</li>
                <li>QuickOracle ne s'ouvre pas → Vérifier showOracle state</li>
                <li>Signe non cliquable → Vérifier handleSelectSign</li>
                <li>Oracle n'apparaît pas → Vérifier step 2 condition</li>
                <li>CTA upsell fail → Vérifier proceedToUpsell</li>
                <li>Packs ne s'affichent pas → Vérifier step 3 condition</li>
                <li>Pack CTA fail → Vérifier onSelectPack callback</li>
              </ul>
            </div>
          </div>

          {/* Right: Logs Console */}
          <div>
            <h2 style={{ marginTop: 0 }}>📊 Console Logs</h2>
            
            <div style={{
              background: '#111',
              border: '1px solid #333',
              borderRadius: '8px',
              padding: '16px',
              fontFamily: 'monospace',
              fontSize: '11px',
              height: '600px',
              overflowY: 'auto',
              color: '#0f0',
            }}>
              {logs.length === 0 ? (
                <div style={{ color: '#666' }}>
                  [En attente de logs...]
                </div>
              ) : (
                logs.map((log, i) => (
                  <div key={i} style={{ marginBottom: '8px', borderBottom: '1px solid #222', paddingBottom: '4px' }}>
                    <span style={{ color: '#999' }}>{log.time}</span>
                    {' '}
                    <span style={{ color: '#0f0' }}>{log.msg}</span>
                    {log.data && (
                      <>
                        <br />
                        <span style={{ color: '#0a0', marginLeft: '20px' }}>
                          {JSON.stringify(log.data, null, 2)}
                        </span>
                      </>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Log controls */}
            <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
              <button
                onClick={() => {
                  localStorage.setItem('qo_logs', '[]');
                  setLogs([]);
                }}
                style={{
                  flex: 1,
                  padding: '8px',
                  background: '#333',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                }}
              >
                🗑️ Effacer logs
              </button>
              <button
                onClick={() => console.log('📋 Copy logs:', logs)}
                style={{
                  flex: 1,
                  padding: '8px',
                  background: '#333',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                }}
              >
                📋 Copy to console
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal QuickOracle */}
      {showOracle && (
        <QuickOracleDebug
          onClose={() => {
            console.log('[CTATest] onClose called');
            setShowOracle(false);
          }}
          onSelectPack={handleSelectPack}
        />
      )}
    </div>
  );
}
