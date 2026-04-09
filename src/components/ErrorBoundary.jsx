/**
 * src/components/ErrorBoundary.jsx
 * Global Error Boundary to catch React component errors and prevent a blank white screen.
 */
import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', maxWidth: 800, margin: '0 auto', textAlign: 'center', minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h1 className="heading-lg" style={{ color: 'var(--color-danger-light)', marginBottom: '1rem' }}>⚠ Something went wrong</h1>
          <p className="text-muted" style={{ marginBottom: '2rem', fontSize: '1.1rem' }}>
            We encountered an unexpected error while loading this page.
          </p>
          
          <div style={{ background: 'var(--color-surface-2)', padding: '1.5rem', borderRadius: '12px', textAlign: 'left', overflowX: 'auto', marginBottom: '2rem', border: '1px solid var(--color-border)' }}>
            <p style={{ fontWeight: 600, color: 'var(--color-danger)', marginBottom: '0.5rem' }}>
              {this.state.error && this.state.error.toString()}
            </p>
            <pre style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', whiteSpace: 'pre-wrap' }}>
              {this.state.errorInfo && this.state.errorInfo.componentStack}
            </pre>
          </div>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button className="btn btn-secondary btn-lg" onClick={this.handleReload}>
              🔄 Refresh Page
            </button>
            <button className="btn btn-primary btn-lg" onClick={this.handleGoHome}>
              🏠 Go to Dashboard
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
