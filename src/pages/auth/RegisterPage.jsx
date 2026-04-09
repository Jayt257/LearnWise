/**
 * src/pages/auth/RegisterPage.jsx
 * New user registration with username + language selection.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { registerUser, clearError } from '../../store/authSlice.js';

const LANGUAGES = [
  { id: 'hi', name: 'Hindi', flag: '🇮🇳' },
  { id: 'en', name: 'English', flag: '🇬🇧' },
  { id: 'ja', name: 'Japanese', flag: '🇯🇵' },
];

export default function RegisterPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading, error, isAuthenticated } = useSelector(s => s.auth);
  const [form, setForm] = useState({ username: '', email: '', password: '', display_name: '', native_lang: 'hi' });

  useEffect(() => { if (isAuthenticated) navigate('/onboarding', { replace: true }); }, [isAuthenticated]);
  useEffect(() => { return () => dispatch(clearError()); }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(registerUser(form));
  };

  const set = (key) => (e) => setForm(p => ({ ...p, [key]: e.target.value }));

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: '1rem' }}>
      <div style={{ position: 'fixed', top: '40%', right: '20%', width: 500, height: 500, background: 'radial-gradient(circle, rgba(6,182,212,0.12) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div className="glass-strong animate-fade-in" style={{ width: '100%', maxWidth: 460, padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🌐</div>
          <h1 className="heading-lg gradient-text">Join LearnWise</h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>Start your language learning journey</p>
        </div>

        {error && (
          <div style={{ background: 'var(--color-danger-glow)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-md)', padding: '0.75rem', marginBottom: '1rem', color: 'var(--color-danger-light)', fontSize: '0.875rem' }}>
            {Array.isArray(error) ? error.map(e => e.msg || e).join(', ') : error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Username *</label>
              <input className="form-input" placeholder="jay123" value={form.username} onChange={set('username')} required minLength={3} maxLength={50} />
            </div>
            <div className="form-group">
              <label className="form-label">Display Name</label>
              <input className="form-input" placeholder="Jay Thakkar" value={form.display_name} onChange={set('display_name')} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Email *</label>
            <input className="form-input" type="email" placeholder="you@example.com" value={form.email} onChange={set('email')} required />
          </div>

          <div className="form-group">
            <label className="form-label">Password * (min 8 chars)</label>
            <input className="form-input" type="password" placeholder="••••••••" value={form.password} onChange={set('password')} required minLength={8} />
          </div>

          <div className="form-group">
            <label className="form-label">Your native language</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {LANGUAGES.map(lang => (
                <button key={lang.id} type="button"
                  onClick={() => setForm(p => ({ ...p, native_lang: lang.id }))}
                  style={{ flex: 1, padding: '0.625rem', borderRadius: 'var(--radius-md)', border: `2px solid ${form.native_lang === lang.id ? 'var(--color-primary)' : 'var(--color-border)'}`, background: form.native_lang === lang.id ? 'var(--color-primary-glow)' : 'var(--color-surface-2)', cursor: 'pointer', transition: 'all 0.2s', fontSize: '0.8rem', color: 'var(--color-text)' }}>
                  {lang.flag}<br />{lang.name}
                </button>
              ))}
            </div>
          </div>

          <button className="btn btn-primary btn-full btn-lg" type="submit" disabled={loading} style={{ marginTop: '0.5rem' }}>
            {loading ? <span className="spinner" /> : '🚀 Create Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--color-primary-light)', fontWeight: 600 }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
