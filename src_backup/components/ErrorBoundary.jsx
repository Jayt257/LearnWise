/
  src/components/ErrorBoundary.jsx
  Global Error Boundary to catch React component errors and prevent a blank white screen.
 /
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
        <div style={{ padding: 'rem', maxWidth: , margin: ' auto', textAlign: 'center', minHeight: 'vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h className="heading-lg" style={{ color: 'var(--color-danger-light)', marginBottom: 'rem' }}> Something went wrong</h>
          <p className="text-muted" style={{ marginBottom: 'rem', fontSize: '.rem' }}>
            We encountered an unexpected error while loading this page.
          </p>
          
          <div style={{ background: 'var(--color-surface-)', padding: '.rem', borderRadius: 'px', textAlign: 'left', overflowX: 'auto', marginBottom: 'rem', border: 'px solid var(--color-border)' }}>
            <p style={{ fontWeight: , color: 'var(--color-danger)', marginBottom: '.rem' }}>
              {this.state.error && this.state.error.toString()}
            </p>
            <pre style={{ fontSize: '.rem', color: 'var(--color-text-muted)', whiteSpace: 'pre-wrap' }}>
              {this.state.errorInfo && this.state.errorInfo.componentStack}
            </pre>
          </div>

          <div style={{ display: 'flex', gap: 'rem', justifyContent: 'center' }}>
            <button className="btn btn-secondary btn-lg" onClick={this.handleReload}>
               Refresh Page
            </button>
            <button className="btn btn-primary btn-lg" onClick={this.handleGoHome}>
               Go to Dashboard
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
