/**
 * src/pages/onboarding/OnboardingPage.jsx
 * Language pair selection — dynamically built from backend pairs API.
 * No hardcoded languages — any pair admin creates appears here automatically.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { startLanguagePair, fetchPairs, setCurrentPair } from '../../store/progressSlice.js';

// Fallback info for unknown languages
const LANG_FALLBACKS = {
  hi: { name: 'Hindi',    flag: '🇮🇳', desc: 'Spoken by 600M+ people' },
  en: { name: 'English',  flag: '🇬🇧', desc: 'Global language of business' },
  ja: { name: 'Japanese', flag: '🇯🇵', desc: 'Rich culture, anime & tech' },
  fr: { name: 'French',   flag: '🇫🇷', desc: 'Language of art & diplomacy' },
  de: { name: 'German',   flag: '🇩🇪', desc: 'Precision language of engineering' },
  zh: { name: 'Chinese',  flag: '🇨🇳', desc: 'Most spoken language on Earth' },
  es: { name: 'Spanish',  flag: '🇪🇸', desc: 'Spoken across 20+ countries' },
  ko: { name: 'Korean',   flag: '🇰🇷', desc: 'K-pop & tech culture' },
};

export default function OnboardingPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { pairs, allProgress, loading } = useSelector(s => s.progress);
  const { user } = useSelector(s => s.auth);

  const [source, setSource] = useState('');
  const [target, setTarget] = useState('');
  const [starting, setStarting] = useState(false);

  // Re-fetch pairs every time this page is visited
  useEffect(() => { dispatch(fetchPairs()); }, [dispatch]);

  // Build a dynamic map of unique languages from backend pairs
  const langMap = {};
  pairs.forEach(p => {
    // pairs from /api/content/pairs has {pairId, from, to, dataPath}
    // pairs from /api/admin/languages has {pairId, from, to, meta: {source, target, ...}}
    const srcId = p.from;
    const tgtId = p.to;
    const srcMeta = p.meta?.source;
    const tgtMeta = p.meta?.target;

    if (!langMap[srcId]) {
      langMap[srcId] = {
        id: srcId,
        name: srcMeta?.name || LANG_FALLBACKS[srcId]?.name || srcId.toUpperCase(),
        flag: srcMeta?.flag || LANG_FALLBACKS[srcId]?.flag || '🏳',
        desc: LANG_FALLBACKS[srcId]?.desc || `Learn ${srcId}`,
      };
    }
    if (!langMap[tgtId]) {
      langMap[tgtId] = {
        id: tgtId,
        name: tgtMeta?.name || LANG_FALLBACKS[tgtId]?.name || tgtId.toUpperCase(),
        flag: tgtMeta?.flag || LANG_FALLBACKS[tgtId]?.flag || '🏳',
        desc: LANG_FALLBACKS[tgtId]?.desc || `Learn ${tgtId}`,
      };
    }
  });

  // When native_lang is known, pre-select source on first load
  useEffect(() => {
    if (!source && user?.native_lang && langMap[user.native_lang]) {
      setSource(user.native_lang);
    }
  }, [pairs]);

  // Available targets: pairs where source = selected source
  const availableTargetIds = pairs
    .filter(p => p.from === source)
    .map(p => p.to)
    .filter((id, idx, arr) => arr.indexOf(id) === idx);

  const handleStart = async () => {
    if (!source || !target || source === target) return;
    const pairId = `${source}-${target}`;
    // Check pair is actually available
    const pairExists = pairs.some(p => p.pairId === pairId);
    if (!pairExists) {
      alert(`Language pair ${pairId} is not available. Please contact admin.`);
      return;
    }
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

  const existingPairs = allProgress.filter(p => p.total_xp > 0);
  const allLangs = Object.values(langMap);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: '1rem' }}>
      <div style={{ position: 'fixed', inset: 0, background: 'radial-gradient(ellipse at 30% 50%, rgba(99,102,241,0.12) 0%, transparent 60%)', pointerEvents: 'none' }} />

      <div style={{ width: '100%', maxWidth: 680 }} className="animate-fade-in">
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
                const srcInfo = langMap[src] || LANG_FALLBACKS[src] || {};
                const tgtInfo = langMap[tgt] || LANG_FALLBACKS[tgt] || {};
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

          {loading && allLangs.length === 0 ? (
            <div className="spinner" style={{ margin: '2rem auto' }} />
          ) : allLangs.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--color-text-muted)' }}>No language pairs available yet. Please contact admin.</p>
          ) : (
            <>
              {/* Source language */}
              <div style={{ marginBottom: '1.5rem' }}>
                <label className="form-label" style={{ marginBottom: '0.75rem', display: 'block' }}>I speak (My language)</label>
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  {allLangs.map(info => (
                    <button key={info.id} type="button"
                      onClick={() => { setSource(info.id); setTarget(''); }}
                      style={{ flex: '1 1 120px', padding: '1rem', borderRadius: 'var(--radius-md)', border: `2px solid ${source === info.id ? 'var(--color-primary)' : 'var(--color-border)'}`, background: source === info.id ? 'var(--color-primary-glow)' : 'var(--color-surface-2)', cursor: 'pointer', transition: 'all 0.2s', textAlign: 'center' }}>
                      <div style={{ fontSize: '1.75rem' }}>{info.flag}</div>
                      <div style={{ fontWeight: 600, marginTop: '0.375rem', fontSize: '0.875rem' }}>{info.name}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--color-text-dim)', marginTop: '0.25rem' }}>{info.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Target language */}
              {source && (
                <div style={{ marginBottom: '2rem' }}>
                  <label className="form-label" style={{ marginBottom: '0.75rem', display: 'block' }}>I want to learn</label>
                  {availableTargetIds.length === 0 ? (
                    <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>No target languages available for this source. Ask admin to add more pairs.</p>
                  ) : (
                    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                      {availableTargetIds.map(id => {
                        const info = langMap[id] || LANG_FALLBACKS[id] || { name: id, flag: '🏳', desc: '' };
                        return (
                          <button key={id} type="button"
                            onClick={() => setTarget(id)}
                            style={{ flex: '1 1 120px', padding: '1rem', borderRadius: 'var(--radius-md)', border: `2px solid ${target === id ? 'var(--color-secondary)' : 'var(--color-border)'}`, background: target === id ? 'var(--color-secondary-glow)' : 'var(--color-surface-2)', cursor: 'pointer', transition: 'all 0.2s', textAlign: 'center' }}>
                            <div style={{ fontSize: '1.75rem' }}>{info.flag}</div>
                            <div style={{ fontWeight: 600, marginTop: '0.375rem', fontSize: '0.875rem' }}>{info.name}</div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--color-text-dim)', marginTop: '0.25rem' }}>{info.desc}</div>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* Summary */}
              {source && target && langMap[source] && langMap[target] && (
                <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem' }}>
                  <span style={{ fontSize: '1.5rem' }}>{langMap[source].flag}</span>
                  <span style={{ margin: '0 0.75rem', color: 'var(--color-text-muted)' }}>→</span>
                  <span style={{ fontSize: '1.5rem' }}>{langMap[target].flag}</span>
                  <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                    {langMap[source].name} → {langMap[target].name} • 6-month roadmap • 8 activity types
                  </p>
                </div>
              )}

              <button className="btn btn-primary btn-full btn-lg" onClick={handleStart}
                disabled={!source || !target || starting || source === target}>
                {starting ? <span className="spinner" /> : '🚀 Start Learning'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
