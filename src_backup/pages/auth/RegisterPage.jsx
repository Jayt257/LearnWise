/
  src/pages/auth/RegisterPage.jsx
  Premium redesign — glass card, split feel, floating language selector.
  All auth logic (dispatch, Redux, navigate) is untouched.
 /
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { registerUser, clearError } from '../../store/authSlice.js';

const LANGUAGES = [
  { id: 'hi', name: 'Hindi',    flag: '' },
  { id: 'en', name: 'English',  flag: '' },
  { id: 'ja', name: 'Japanese', flag: '' },
];

export default function RegisterPage() {
  const navigate  = useNavigate();
  const dispatch  = useDispatch();
  const { loading, error, isAuthenticated } = useSelector(s => s.auth);
  const [form, setForm] = useState({
    username: '', email: '', password: '', display_name: '', native_lang: 'hi',
  });

  useEffect(() => { if (isAuthenticated) navigate('/onboarding', { replace: true }); }, [isAuthenticated]);
  useEffect(() => { return () => dispatch(clearError()); }, []);

  const handleSubmit = (e) => { e.preventDefault(); dispatch(registerUser(form)); };
  const set = key => e => setForm(p => ({ ...p, [key]: e.target.value }));

  return (
    <div style={{
      minHeight: 'vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg)',
      padding: '.rem rem',
      position: 'relative',
    }}>
      {/ Ambient glows /}
      <div style={{
        position: 'fixed', top: '%', right: '%',
        width: , height: ,
        background: 'radial-gradient(circle, rgba(,,,.) %, transparent %)',
        pointerEvents: 'none', zIndex: ,
      }} />
      <div style={{
        position: 'fixed', bottom: '%', left: '%',
        width: , height: ,
        background: 'radial-gradient(circle, rgba(,,,.) %, transparent %)',
        pointerEvents: 'none', zIndex: ,
      }} />

      <div
        className="glass-strong animate-fade-up"
        style={{ width: '%', maxWidth: , padding: '.rem .rem', position: 'relative', zIndex:  }}
      >
        {/ Header /}
        <div style={{ textAlign: 'center', marginBottom: 'rem' }}>
          <div style={{ fontSize: '.rem', marginBottom: '.rem' }} className="animate-float"></div>
          <h className="heading-lg gradient-text" style={{ marginBottom: '.rem' }}>Join LearnWise</h>
          <p style={{ color: 'var(--text-muted)', fontSize: '.rem' }}>
            Start your language learning journey today
          </p>
          <div style={{
            margin: 'rem auto ',
            width: , height: ,
            background: 'linear-gradient(deg, transparent, var(--cyan), transparent)',
            borderRadius: 'var(--radius-full)',
          }} />
        </div>

        {/ Error /}
        {error && (
          <div style={{
            background: 'var(--danger-glow)', border: 'px solid var(--danger)',
            borderRadius: 'var(--radius-md)', padding: '.rem rem',
            marginBottom: '.rem', color: 'var(--danger-light)', fontSize: '.rem',
            display: 'flex', alignItems: 'center', gap: '.rem',
          }}>
             {Array.isArray(error) ? error.map(e => e.msg || e).join(', ') : error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'rem' }}>
          <div className="grid-">
            <div className="form-group">
              <label className="form-label">Username </label>
              <input className="form-input" placeholder="jay"
                value={form.username} onChange={set('username')} required minLength={} maxLength={} />
            </div>
            <div className="form-group">
              <label className="form-label">Display Name</label>
              <input className="form-input" placeholder="Jay Thakkar"
                value={form.display_name} onChange={set('display_name')} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Email </label>
            <input className="form-input" type="email" placeholder="you@example.com"
              value={form.email} onChange={set('email')} required />
          </div>

          <div className="form-group">
            <label className="form-label">Password  (min  chars)</label>
            <input className="form-input" type="password" placeholder="••••••••"
              value={form.password} onChange={set('password')} required minLength={} />
          </div>

          {/ Native language selector /}
          <div className="form-group">
            <label className="form-label">Your Native Language</label>
            <div style={{ display: 'flex', gap: '.rem' }}>
              {LANGUAGES.map(lang => (
                <button
                  key={lang.id}
                  type="button"
                  onClick={() => setForm(p => ({ ...p, native_lang: lang.id }))}
                  style={{
                    flex: ,
                    padding: '.rem .rem',
                    borderRadius: 'var(--radius-md)',
                    border: `px solid ${form.native_lang === lang.id
                      ? 'var(--primary)'
                      : 'var(--border)'}`,
                    background: form.native_lang === lang.id
                      ? 'rgba(var(--primary-rgb), .)'
                      : 'var(--surface-)',
                    cursor: 'pointer',
                    transition: 'all var(--transition)',
                    fontSize: '.rem',
                    color: 'var(--text)',
                    textAlign: 'center',
                    boxShadow: form.native_lang === lang.id
                      ? '  px var(--primary-glow)'
                      : 'none',
                  }}
                >
                  <div style={{ fontSize: '.rem', marginBottom: '.rem' }}>{lang.flag}</div>
                  <div style={{ fontWeight: , fontSize: '.rem' }}>{lang.name}</div>
                </button>
              ))}
            </div>
          </div>

          <button
            className="btn btn-primary btn-full btn-lg"
            type="submit"
            disabled={loading}
            style={{ marginTop: '.rem' }}
          >
            {loading ? <span className="spinner" /> : ' Create Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '.rem', fontSize: '.rem', color: 'var(--text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--primary-light)', fontWeight:  }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
