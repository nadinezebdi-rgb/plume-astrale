import React from 'react';
import ReactDOM from 'react-dom/client';
import { HelmetProvider } from 'react-helmet-async';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { installMetaAttribution } from '@/lib/metaAttribution';

// Attache les signaux Meta (_fbp/_fbc/event_id) aux appels de checkout.
installMetaAttribution();

// Mute console.log/debug/info en production (garde console.error/warn pour les vrais problèmes).
// Réduit le bruit dans la console des visiteurs + évite d'exposer des infos internes.
if (process.env.NODE_ENV === 'production') {
  const noop = () => {};
  console.log = noop;
  console.debug = noop;
  console.info = noop;
}

class RootErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('RootErrorBoundary caught an error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#0C0918',
            color: '#F0E6D3',
            padding: '24px',
            textAlign: 'center',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          <h1 style={{ margin: 0, fontFamily: 'Cormorant Garamond, serif', fontWeight: 400 }}>
            Plume Astrale
          </h1>
          <p style={{ margin: 0, color: '#B8B0C8' }}>
            Une erreur est survenue au chargement.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '8px',
              padding: '10px 16px',
              borderRadius: '999px',
              border: '1px solid rgba(212,180,106,0.5)',
              background: 'rgba(212,180,106,0.12)',
              color: '#D4B46A',
              cursor: 'pointer',
            }}
          >
            Recharger la page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <RootErrorBoundary>
      <HelmetProvider>
        <App />
      </HelmetProvider>
    </RootErrorBoundary>
  </React.StrictMode>
);
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
