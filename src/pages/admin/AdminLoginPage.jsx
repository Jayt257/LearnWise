/**
 * src/pages/admin/AdminLoginPage.jsx
 * Separate admin-only login page.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { adminLoginUser, clearError } from '../../store/authSlice.js';

export default function AdminLoginPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading, error, isAuthenticated, user } = useSelector(s => s.auth);
  const [form, setForm] = useState({ email: '', password: '' });

  useEffect(() => {
    if (isAuthenticated && user?.role === 'admin') navigate('/admin', { replace: true });
  }, [isAuthenticated, user]);
  useEffect(() => { return () => dispatch(clearError()); }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(adminLoginUser(form));
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: '1rem' }}>
      <div style={{ position: 'fixed', inset: 0, background: 'radial-gradient(ellipse at center, rgba(239,68,68,0.08) 0%, transparent 60%)', pointerEvents: 'none' }} />

      <div className="glass-strong animate-fade-in" style={{ width: '100%', maxWidth: 400, padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🛡</div>
          <h1 className="heading-lg" style={{ color: 'var(--color-danger-light)' }}>Admin Portal</h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>LearnWise Administration</p>
        </div>

        {error && (
          <div style={{ background: 'var(--color-danger-glow)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-md)', padding: '0.75rem', marginBottom: '1rem', color: 'var(--color-danger-light)', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Admin Email</label>
            <input className="form-input" type="email" placeholder="admin@learnwise.app"
              value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className="form-input" type="password" placeholder="••••••••"
              value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))} required />
          </div>
          <button className="btn btn-danger btn-full btn-lg" type="submit" disabled={loading} style={{ marginTop: '0.5rem' }}>
            {loading ? <span className="spinner" /> : '🔐 Admin Sign In'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.8rem' }}>
          <Link to="/login" style={{ color: 'var(--color-text-dim)' }}>← Back to user login</Link>
        </p>
      </div>
    </div>
  );
}
