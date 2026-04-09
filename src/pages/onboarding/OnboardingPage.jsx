/**
 * src/pages/onboarding/OnboardingPage.jsx
 * Language pair selection — choose source and target language.
 * Prevents same source + target. Starts the progress record then goes to dashboard.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { startLanguagePair, fetchPairs } from '../../store/progressSlice.js';
import { setCurrentPair } from '../../store/progressSlice.js';

const LANG_INFO = {
  hi: { name: 'Hindi', flag: '🇮🇳', desc: 'Spoken by 600M+ people' },
  en: { name: 'English', flag: '🇬🇧', desc: 'Global language of business' },
  ja: { name: 'Japanese', flag: '🇯🇵', desc: 'Rich culture, anime & tech' },
};

export default function OnboardingPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { pairs, allProgress, loading } = useSelector(s => s.progress);
  const { user } = useSelector(s => s.auth);

  const [source, setSource] = useState(user?.native_lang || 'hi');
  const [target, setTarget] = useState('');
  const [starting, setStarting] = useState(false);

  useEffect(() => { dispatch(fetchPairs()); }, []);

  // Get available targets given source
  const availableTargets = Object.keys(LANG_INFO).filter(l => l !== source);

  const handleStart = async () => {
    if (!source || !target || source === target) return;
    const pairId = `${source}-${target}`;
    setStarting(true);
    try {
      await dispatch(startLanguagePair(pairId)).unwrap();
      dispatch(setCurrentPair(pairId));
      navigate('/dashboard');
    } catch (e) {
      console.error(e);
    } finally {
      setStarting(false);
    }
  };

  // Existing progress to resume
  const existingPairs = allProgress.filter(p => p.total_xp > 0);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: '1rem' }}>
      <div style={{ position: 'fixed', inset: 0, background: 'radial-gradient(ellipse at 30% 50%, rgba(99,102,241,0.12) 0%, transparent 60%)', pointerEvents: 'none' }} />

      <div style={{ width: '100%', maxWidth: 640 }} className="animate-fade-in">
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }} className="animate-float">🌍</div>
          <h1 className="heading-xl">
            <span className="gradient-text">Choose Your Language Path</span>
          </h1>
          <p style={{ color: 'var(--color-text-muted)', marginTop: '0.75rem' }}>
            Hi {user?.display_name || user?.username}! What would you like to learn today?
          </p>
        </div>

        {/* Resume existing */}
        {existingPairs.length > 0 && (
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <h3 className="heading-sm" style={{ marginBottom: '1rem' }}>📚 Resume Learning</h3>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {existingPairs.map(p => {
                const [src, tgt] = p.lang_pair_id.split('-');
                const srcInfo = LANG_INFO[src] || {};
                const tgtInfo = LANG_INFO[tgt] || {};
                return (
                  <button key={p.lang_pair_id} className="btn btn-secondary"
                    onClick={() => { dispatch(setCurrentPair(p.lang_pair_id)); navigate('/dashboard'); }}>
                    {srcInfo.flag} → {tgtInfo.flag} {tgtInfo.name}
                    <span className="badge badge-accent" style={{ marginLeft: '0.5rem' }}>{p.total_xp} XP</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div className="glass-strong" style={{ padding: '2rem' }}>
          <h3 className="heading-sm" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>🆕 Start New Language Path</h3>

          {/* Source language */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label className="form-label" style={{ marginBottom: '0.75rem', display: 'block' }}>I speak (My language)</label>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              {Object.entries(LANG_INFO).map(([id, info]) => (
                <button key={id} type="button"
                  onClick={() => { setSource(id); if (target === id) setTarget(''); }}
                  style={{ flex: 1, padding: '1rem', borderRadius: 'var(--radius-md)', border: `2px solid ${source === id ? 'var(--color-primary)' : 'var(--color-border)'}`, background: source === id ? 'var(--color-primary-glow)' : 'var(--color-surface-2)', cursor: 'pointer', transition: 'all 0.2s', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.75rem' }}>{info.flag}</div>
                  <div style={{ fontWeight: 600, marginTop: '0.375rem', fontSize: '0.875rem' }}>{info.name}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--color-text-dim)', marginTop: '0.25rem' }}>{info.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Target language */}
          <div style={{ marginBottom: '2rem' }}>
            <label className="form-label" style={{ marginBottom: '0.75rem', display: 'block' }}>I want to learn</label>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              {availableTargets.map(id => {
                const info = LANG_INFO[id];
                return (
                  <button key={id} type="button"
                    onClick={() => setTarget(id)}
                    style={{ flex: 1, padding: '1rem', borderRadius: 'var(--radius-md)', border: `2px solid ${target === id ? 'var(--color-secondary)' : 'var(--color-border)'}`, background: target === id ? 'var(--color-secondary-glow)' : 'var(--color-surface-2)', cursor: 'pointer', transition: 'all 0.2s', textAlign: 'center' }}>
                    <div style={{ fontSize: '1.75rem' }}>{info.flag}</div>
                    <div style={{ fontWeight: 600, marginTop: '0.375rem', fontSize: '0.875rem' }}>{info.name}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--color-text-dim)', marginTop: '0.25rem' }}>{info.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Summary + start */}
          {source && target && (
            <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem' }}>
              <span style={{ fontSize: '1.5rem' }}>{LANG_INFO[source]?.flag}</span>
              <span style={{ margin: '0 0.75rem', color: 'var(--color-text-muted)' }}>→</span>
              <span style={{ fontSize: '1.5rem' }}>{LANG_INFO[target]?.flag}</span>
              <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                {LANG_INFO[source]?.name} → {LANG_INFO[target]?.name} • 6-month roadmap • 8 activity types
              </p>
            </div>
          )}

          <button className="btn btn-primary btn-full btn-lg" onClick={handleStart}
            disabled={!source || !target || starting || source === target}>
            {starting ? <span className="spinner" /> : '🚀 Start Learning'}
          </button>
        </div>
      </div>
    </div>
  );
}
