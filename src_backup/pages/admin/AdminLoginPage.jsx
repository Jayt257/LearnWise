/
  src/pages/admin/AdminLoginPage.jsx
  Separate admin-only login page.
 /
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
    <div style={{ minHeight: 'vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: 'rem' }}>
      <div style={{ position: 'fixed', inset: , background: 'radial-gradient(ellipse at center, rgba(,,,.) %, transparent %)', pointerEvents: 'none' }} />

      <div className="glass-strong animate-fade-in" style={{ width: '%', maxWidth: , padding: '.rem' }}>
        <div style={{ textAlign: 'center', marginBottom: 'rem' }}>
          <div style={{ fontSize: '.rem', marginBottom: '.rem' }}></div>
          <h className="heading-lg" style={{ color: 'var(--color-danger-light)' }}>Admin Portal</h>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '.rem' }}>LearnWise Administration</p>
        </div>

        {error && (
          <div style={{ background: 'var(--color-danger-glow)', border: 'px solid var(--color-danger)', borderRadius: 'var(--radius-md)', padding: '.rem', marginBottom: 'rem', color: 'var(--color-danger-light)', fontSize: '.rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'rem' }}>
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
          <button className="btn btn-danger btn-full btn-lg" type="submit" disabled={loading} style={{ marginTop: '.rem' }}>
            {loading ? <span className="spinner" /> : ' Admin Sign In'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '.rem', fontSize: '.rem' }}>
          <Link to="/login" style={{ color: 'var(--color-text-dim)' }}>← Back to user login</Link>
        </p>
      </div>
    </div>
  );
}
