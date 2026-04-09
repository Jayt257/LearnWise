/**
 * src/pages/auth/LoginPage.jsx
 * User login page with premium glass UI.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser, clearError } from '../../store/authSlice.js';

export default function LoginPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading, error, isAuthenticated } = useSelector(s => s.auth);
  const [form, setForm] = useState({ email: '', password: '' });

  useEffect(() => { if (isAuthenticated) navigate('/dashboard', { replace: true }); }, [isAuthenticated]);
  useEffect(() => { return () => dispatch(clearError()); }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(loginUser(form));
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: '1rem' }}>
      {/* Background glow */}
      <div style={{ position: 'fixed', top: '30%', left: '50%', transform: 'translate(-50%,-50%)', width: 600, height: 600, background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div className="glass-strong animate-fade-in" style={{ width: '100%', maxWidth: 420, padding: '2.5rem' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🌐</div>
          <h1 className="heading-lg gradient-text">LearnWise</h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginTop: '0.25rem' }}>AI-powered language learning</p>
        </div>

        <h2 className="heading-sm" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Welcome back</h2>

        {error && (
          <div style={{ background: 'var(--color-danger-glow)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', marginBottom: '1rem', color: 'var(--color-danger-light)', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-input" type="email" placeholder="you@example.com" value={form.email}
              onChange={e => setForm(p => ({ ...p, email: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className="form-input" type="password" placeholder="••••••••" value={form.password}
              onChange={e => setForm(p => ({ ...p, password: e.target.value }))} required />
          </div>
          <button className="btn btn-primary btn-full btn-lg" type="submit" disabled={loading} style={{ marginTop: '0.5rem' }}>
            {loading ? <span className="spinner" /> : 'Sign In'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: 'var(--color-primary-light)', fontWeight: 600 }}>Sign up free</Link>
        </p>
        <p style={{ textAlign: 'center', marginTop: '0.75rem', fontSize: '0.8rem' }}>
          <Link to="/admin/login" style={{ color: 'var(--color-text-dim)' }}>Admin login →</Link>
        </p>
      </div>
    </div>
  );
}
