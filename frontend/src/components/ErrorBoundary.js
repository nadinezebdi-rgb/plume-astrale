import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

static getDerivedStateFromError() {
  return { hasError: true };
}

componentDidCatch(error, info) {
  console.error('ErrorBoundary caught an error:', error, info);
}

render() {
  if (this.state.hasError) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0C0918' }}>
  <div className="text-center px-6">
    <p className="text-[#B8B0C8] mb-4">Cette section est temporairement indisponible.</p>
  <button onClick={() => window.location.reload()} className="btn-mystical">Recharger la page</button>
  </div>
  </div>
  );
}
return this.props.children;
}
}

export default ErrorBoundary;
