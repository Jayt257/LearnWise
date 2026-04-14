/
  src/pages/auth/LoginPage.jsx
  Premium redesign — star bg, typing cursor, glass card.
  All auth logic (dispatch, navigate, Redux) is untouched.
 /
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { loginUser, clearError } from '../../store/authSlice.js';
import { useTheme } from '../../hooks/useTheme.js';

export default function LoginPage() {
  const navigate  = useNavigate();
  const dispatch  = useDispatch();
  const { isDark } = useTheme();
  const { loading, error, isAuthenticated } = useSelector(s => s.auth);
  const [form, setForm] = useState({ email: '', password: '' });
  const [focusedField, setFocusedField] = useState(null);

  useEffect(() => { if (isAuthenticated) navigate('/dashboard', { replace: true }); }, [isAuthenticated]);
  useEffect(() => { return () => dispatch(clearError()); }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(loginUser(form));
  };

  return (
    <div style={{
      minHeight: 'vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg)',
      padding: 'rem',
      position: 'relative',
    }}>
      {/ Radial glow spots /}
      <div style={{
        position: 'fixed', top: '%', left: '%',
        transform: 'translate(-%, -%)',
        width: , height: ,
        background: 'radial-gradient(circle, rgba(,,,.) %, transparent %)',
        pointerEvents: 'none', zIndex: ,
      }} />
      <div style={{
        position: 'fixed', bottom: '%', right: '%',
        width: , height: ,
        background: 'radial-gradient(circle, rgba(,,,.) %, transparent %)',
        pointerEvents: 'none', zIndex: ,
      }} />

      {/ Card /}
      <div
        className="glass-strong animate-fade-up"
        style={{
          width: '%',
          maxWidth: ,
          padding: '.rem .rem',
          position: 'relative',
          zIndex: ,
        }}
      >
        {/ Logo /}
        <div style={{ textAlign: 'center', marginBottom: '.rem' }}>
          <div style={{
            fontSize: '.rem',
            marginBottom: '.rem',
            display: 'inline-block',
          }}
            className="animate-float"
          >
            
          </div>
          <h
            className="heading-lg gradient-text typing-cursor"
            style={{ marginBottom: '.rem' }}
          >
            LearnWise
          </h>
          <p style={{
            color: 'var(--text-muted)',
            fontSize: '.rem',
            letterSpacing: '.em',
          }}>
            AI-powered language learning
          </p>

          {/ Decorative divider /}
          <div style={{
            margin: '.rem auto ',
            width: , height: ,
            background: 'linear-gradient(deg, transparent, var(--primary), transparent)',
            borderRadius: 'var(--radius-full)',
          }} />
        </div>

        <h className="heading-sm" style={{ marginBottom: '.rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          Welcome back
        </h>

        {/ Error /}
        {error && (
          <div style={{
            background: 'var(--danger-glow)',
            border: 'px solid var(--danger)',
            borderRadius: 'var(--radius-md)',
            padding: '.rem rem',
            marginBottom: '.rem',
            color: 'var(--danger-light)',
            fontSize: '.rem',
            display: 'flex',
            alignItems: 'center',
            gap: '.rem',
          }}>
             {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '.rem' }}>
          {/ Email /}
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              className="form-input"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onFocus={() => setFocusedField('email')}
              onBlur={() => setFocusedField(null)}
              onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
              required
              style={{
                boxShadow: focusedField === 'email' ? '   px var(--primary-glow)' : 'none',
              }}
            />
          </div>

          {/ Password /}
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              className="form-input"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onFocus={() => setFocusedField('password')}
              onBlur={() => setFocusedField(null)}
              onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
              required
              style={{
                boxShadow: focusedField === 'password' ? '   px var(--primary-glow)' : 'none',
              }}
            />
          </div>

          <button
            className="btn btn-primary btn-full btn-lg"
            type="submit"
            disabled={loading}
            style={{ marginTop: '.rem' }}
          >
            {loading ? <span className="spinner" /> : '✦ Sign In'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '.rem', fontSize: '.rem', color: 'var(--text-muted)' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: 'var(--primary-light)', fontWeight:  }}>
            Sign up free
          </Link>
        </p>
        <p style={{ textAlign: 'center', marginTop: '.rem', fontSize: '.rem' }}>
          <Link to="/admin/login" style={{ color: 'var(--text-dim)' }}>Admin login →</Link>
        </p>
      </div>
    </div>
  );
}
