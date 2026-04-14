/
  src/pages/onboarding/OnboardingPage.jsx
  Premium redesign — animated language cards, step indicator, floating globe.
  All selection/routing logic is untouched.
 /
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { startLanguagePair, fetchPairs, setCurrentPair } from '../../store/progressSlice.js';

const LANG_FALLBACKS = {
  hi: { name: 'Hindi',    flag: '', desc: 'Spoken by M+ people' },
  en: { name: 'English',  flag: '', desc: 'Global language of business' },
  ja: { name: 'Japanese', flag: '', desc: 'Rich culture, anime & tech' },
  fr: { name: 'French',   flag: '', desc: 'Language of art & diplomacy' },
  de: { name: 'German',   flag: '', desc: 'Precision language of engineering' },
  zh: { name: 'Chinese',  flag: '', desc: 'Most spoken language on Earth' },
  es: { name: 'Spanish',  flag: '', desc: 'Spoken across + countries' },
  ko: { name: 'Korean',   flag: '', desc: 'K-pop & tech culture' },
};

function LangCard({ info, selected, color, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        flex: '  px',
        padding: '.rem .rem',
        borderRadius: 'var(--radius-lg)',
        border: `px solid ${selected ? color : 'var(--border)'}`,
        background: selected ? `${color}` : 'var(--surface-)',
        cursor: 'pointer',
        transition: 'all var(--transition-spring)',
        textAlign: 'center',
        boxShadow: selected ? `  px ${color},  px px rgba(,,,.)` : 'none',
        transform: selected ? 'translateY(-px) scale(.)' : 'none',
        backdropFilter: 'blur(px)',
      }}
    >
      <div style={{ fontSize: '.rem', marginBottom: '.rem' }}>{info.flag}</div>
      <div style={{
        fontFamily: 'var(--font-display)',
        fontWeight: ,
        fontSize: '.rem',
        color: selected ? 'var(--text)' : 'var(--text-muted)',
        marginBottom: '.rem',
      }}>
        {info.name}
      </div>
      <div style={{ fontSize: '.rem', color: 'var(--text-dim)', lineHeight: . }}>
        {info.desc}
      </div>
      {selected && (
        <div style={{
          marginTop: '.rem',
          width: , height: ,
          borderRadius: '%',
          background: color,
          margin: '.rem auto ',
          boxShadow: `  px ${color}`,
        }} />
      )}
    </button>
  );
}

export default function OnboardingPage() {
  const navigate  = useNavigate();
  const dispatch  = useDispatch();
  const { pairs, allProgress, loading } = useSelector(s => s.progress);
  const { user } = useSelector(s => s.auth);

  const [source,   setSource]   = useState('');
  const [target,   setTarget]   = useState('');
  const [starting, setStarting] = useState(false);

  useEffect(() => { dispatch(fetchPairs()); }, [dispatch]);

  const langMap = {};
  pairs.forEach(p => {
    const srcId = p.from, tgtId = p.to;
    const srcMeta = p.meta?.source, tgtMeta = p.meta?.target;
    if (!langMap[srcId]) langMap[srcId] = {
      id: srcId,
      name: srcMeta?.name || LANG_FALLBACKS[srcId]?.name || srcId.toUpperCase(),
      flag: srcMeta?.flag || LANG_FALLBACKS[srcId]?.flag || '',
      desc: LANG_FALLBACKS[srcId]?.desc || `Learn ${srcId}`,
    };
    if (!langMap[tgtId]) langMap[tgtId] = {
      id: tgtId,
      name: tgtMeta?.name || LANG_FALLBACKS[tgtId]?.name || tgtId.toUpperCase(),
      flag: tgtMeta?.flag || LANG_FALLBACKS[tgtId]?.flag || '',
      desc: LANG_FALLBACKS[tgtId]?.desc || `Learn ${tgtId}`,
    };
  });

  useEffect(() => {
    if (!source && user?.native_lang && langMap[user.native_lang]) {
      setSource(user.native_lang);
    }
  }, [pairs]);

  const availableTargetIds = pairs
    .filter(p => p.from === source)
    .map(p => p.to)
    .filter((id, idx, arr) => arr.indexOf(id) === idx);

  const handleStart = async () => {
    if (!source || !target || source === target) return;
    const pairId = `${source}-${target}`;
    const pairExists = pairs.some(p => p.pairId === pairId);
    if (!pairExists) { alert(`Language pair ${pairId} is not available.`); return; }
    setStarting(true);
    try {
      await dispatch(startLanguagePair(pairId)).unwrap();
      dispatch(setCurrentPair(pairId));
      navigate('/dashboard');
    } catch (e) { console.error(e); }
    finally { setStarting(false); }
  };

  const existingPairs = allProgress.filter(p => p.total_xp > );
  const allLangs = Object.values(langMap);
  const step = !source ?  : !target ?  : ;

  return (
    <div style={{
      minHeight: 'vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)', padding: '.rem rem',
      position: 'relative',
    }}>
      {/ Ambient glows /}
      <div style={{ position: 'fixed', inset: , background: 'radial-gradient(ellipse at % %, rgba(,,,.) %, transparent %)', pointerEvents: 'none', zIndex:  }} />
      <div style={{ position: 'fixed', inset: , background: 'radial-gradient(ellipse at % %, rgba(,,,.) %, transparent %)', pointerEvents: 'none', zIndex:  }} />

      <div style={{ width: '%', maxWidth: , position: 'relative', zIndex:  }} className="animate-fade-up">

        {/ Step indicator /}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '.rem', marginBottom: 'rem' }}>
          {[,,].map(s => (
            <div key={s} style={{
              width: s === step ?  : ,
              height: ,
              borderRadius: 'var(--radius-full)',
              background: s < step ? 'var(--emerald)' : s === step ? 'var(--primary)' : 'var(--surface-)',
              transition: 'all var(--transition-slow)',
              boxShadow: s === step ? '  px var(--primary-glow)' : 'none',
            }} />
          ))}
        </div>

        {/ Hero /}
        <div style={{ textAlign: 'center', marginBottom: '.rem' }}>
          <div style={{ fontSize: '.rem', marginBottom: 'rem' }} className="animate-float"></div>
          <h className="heading-xl">
            <span className="gradient-text">Choose Your Language Path</span>
          </h>
          <p style={{ color: 'var(--text-muted)', marginTop: '.rem', fontSize: 'rem' }}>
            Hi <strong style={{ color: 'var(--text)' }}>{user?.display_name || user?.username}</strong>! What would you like to learn today?
          </p>
        </div>

        {/ Resume existing /}
        {existingPairs.length >  && (
          <div className="card" style={{ marginBottom: '.rem' }}>
            <h className="heading-sm" style={{ marginBottom: 'rem' }}> Resume Learning</h>
            <div style={{ display: 'flex', gap: '.rem', flexWrap: 'wrap' }}>
              {existingPairs.map(p => {
                const [src, tgt] = p.lang_pair_id.split('-');
                const srcInfo = langMap[src] || LANG_FALLBACKS[src] || {};
                const tgtInfo = langMap[tgt] || LANG_FALLBACKS[tgt] || {};
                return (
                  <button key={p.lang_pair_id} className="btn btn-secondary"
                    onClick={() => { dispatch(setCurrentPair(p.lang_pair_id)); navigate('/dashboard'); }}>
                    {srcInfo.flag} → {tgtInfo.flag} {tgtInfo.name}
                    <span className="badge badge-accent" style={{ marginLeft: '.rem' }}>{p.total_xp} XP</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div className="glass-strong" style={{ padding: '.rem' }}>
          <h className="heading-sm" style={{ marginBottom: '.rem', textAlign: 'center', color: 'var(--text-muted)' }}>
             Start a New Language Path
          </h>

          {loading && allLangs.length ===  ? (
            <div className="spinner" style={{ margin: 'rem auto' }} />
          ) : allLangs.length ===  ? (
            <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No language pairs available yet.</p>
          ) : (
            <>
              {/ Source language /}
              <div style={{ marginBottom: 'rem' }}>
                <label className="form-label" style={{ marginBottom: 'rem', display: 'block' }}>
                  I speak (my language)
                </label>
                <div style={{ display: 'flex', gap: '.rem', flexWrap: 'wrap' }}>
                  {allLangs.map(info => (
                    <LangCard
                      key={info.id}
                      info={info}
                      selected={source === info.id}
                      color="var(--primary)"
                      onClick={() => { setSource(info.id); setTarget(''); }}
                    />
                  ))}
                </div>
              </div>

              {/ Animated arrow + target /}
              {source && (
                <div className="animate-fade-up">
                  {/ Arrow connector /}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'rem', marginBottom: '.rem' }}>
                    <div style={{ flex: , height: , background: 'linear-gradient(deg, transparent, var(--border))' }} />
                    <div style={{
                      padding: '.rem rem',
                      borderRadius: 'var(--radius-full)',
                      background: 'var(--surface-)',
                      border: 'px solid var(--border)',
                      fontSize: '.rem',
                      color: 'var(--text-muted)',
                      fontFamily: 'var(--font-mono)',
                    }}>
                      {langMap[source]?.flag} {langMap[source]?.name} → learn ↓
                    </div>
                    <div style={{ flex: , height: , background: 'linear-gradient(deg, var(--border), transparent)' }} />
                  </div>

                  <label className="form-label" style={{ marginBottom: 'rem', display: 'block' }}>
                    I want to learn
                  </label>

                  {availableTargetIds.length ===  ? (
                    <p style={{ color: 'var(--text-muted)', fontSize: '.rem', textAlign: 'center', padding: 'rem' }}>
                      No target languages available for this source. Ask admin to add more pairs.
                    </p>
                  ) : (
                    <div style={{ display: 'flex', gap: '.rem', flexWrap: 'wrap', marginBottom: '.rem' }}>
                      {availableTargetIds.map(id => {
                        const info = langMap[id] || LANG_FALLBACKS[id] || { name: id, flag: '', desc: '' };
                        return (
                          <LangCard
                            key={id}
                            info={info}
                            selected={target === id}
                            color="var(--cyan)"
                            onClick={() => setTarget(id)}
                          />
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/ Summary /}
              {source && target && langMap[source] && langMap[target] && (
                <div className="animate-fade-up" style={{
                  textAlign: 'center',
                  padding: '.rem',
                  background: 'rgba(var(--primary-rgb), .)',
                  borderRadius: 'var(--radius-lg)',
                  border: 'px solid var(--border-strong)',
                  marginBottom: '.rem',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'rem', marginBottom: '.rem' }}>
                    <span style={{ fontSize: 'rem' }}>{langMap[source].flag}</span>
                    <span style={{ color: 'var(--primary-light)', fontSize: '.rem' }}>→</span>
                    <span style={{ fontSize: 'rem' }}>{langMap[target].flag}</span>
                  </div>
                  <p style={{ fontSize: '.rem', color: 'var(--text-muted)' }}>
                    <strong style={{ color: 'var(--text)' }}>{langMap[source].name}</strong>
                    {' → '}
                    <strong style={{ color: 'var(--text)' }}>{langMap[target].name}</strong>
                    {' • -month roadmap •  activity types'}
                  </p>
                </div>
              )}

              <button
                className="btn btn-primary btn-full btn-lg"
                onClick={handleStart}
                disabled={!source || !target || starting || source === target}
              >
                {starting ? <span className="spinner" /> : ' Start Learning'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
