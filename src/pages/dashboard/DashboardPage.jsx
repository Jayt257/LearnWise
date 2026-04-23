/**
 * src/pages/dashboard/DashboardPage.jsx
 * Roadmap view — months → blocks → 8 activities. 100% dynamic from meta.json.
 * No hardcoded language info — reads from meta.source/target.
 * Activities listed in meta but JSON missing show as "coming soon" (not clickable but visible).
 */
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAllProgress, fetchPairs, setCurrentPair } from '../../store/progressSlice.js';
import { getMeta } from '../../api/content.js';
import { getCompletions, startPair } from '../../api/progress.js';

const ACTIVITY_ICONS = {
  lesson: '📖', vocabulary: '🔤', vocab: '🔤',
  reading: '📄', writing: '✍', listening: '🎧',
  speaking: '🎙', pronunciation: '🗣', test: '📋',
};
const ACTIVITY_COLORS = {
  lesson:        { base: '#f43841', glow: 'rgba(244,56,65,0.22)'   },
  vocabulary:    { base: '#73c936', glow: 'rgba(115,201,54,0.22)'  },
  vocab:         { base: '#73c936', glow: 'rgba(115,201,54,0.22)'  },
  reading:       { base: '#ffdd33', glow: 'rgba(255,221,51,0.22)'  },
  writing:       { base: '#cc8c3c', glow: 'rgba(204,140,60,0.22)'  },
  listening:     { base: '#96a6c8', glow: 'rgba(150,166,200,0.22)' },
  speaking:      { base: '#9e95c7', glow: 'rgba(158,149,199,0.22)' },
  pronunciation: { base: '#95a99f', glow: 'rgba(149,169,159,0.22)' },
  test:          { base: '#ff4f58', glow: 'rgba(255,79,88,0.22)'   },
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { allProgress, currentPairId, pairs } = useSelector(s => s.progress);

  const [meta, setMeta] = useState(null);
  const [completions, setCompletions] = useState([]);
  const [selectedPair, setSelectedPair] = useState(currentPairId);
  const [loading, setLoading] = useState(true);
  const [expandedMonth, setExpandedMonth] = useState(1);

  const currentProgress = allProgress.find(p => p.lang_pair_id === selectedPair);

  useEffect(() => {
    dispatch(fetchAllProgress());
    dispatch(fetchPairs());
  }, []);

  // Auto-select first pair if none selected
  useEffect(() => {
    if (!selectedPair && allProgress.length > 0) {
      setSelectedPair(allProgress[0].lang_pair_id);
    }
  }, [allProgress, selectedPair]);

  useEffect(() => {
    if (!selectedPair) return;
    setLoading(true);
    Promise.all([
      getMeta(selectedPair).then(r => setMeta(r.data)),
      getCompletions(selectedPair).then(r => setCompletions(r.data)),
    ]).catch(console.error).finally(() => setLoading(false));
  }, [selectedPair]);

  const completedSeqIds = new Set(completions.filter(c => c.passed).map(c => c.activity_seq_id));
  const currentActivityId = currentProgress?.current_activity_id || 1;
  const isUnlocked = (seqId) => seqId <= currentActivityId;
  const isCompleted = (seqId) => completedSeqIds.has(seqId);

  const handleActivityClick = (activity, pairId, monthNum, blockNum) => {
    if (!isUnlocked(activity.id)) return;
    navigate(`/activity/${pairId}/${activity.type}`, {
      state: {
        activityFile: activity.file,
        activitySeqId: activity.id,
        activityJsonId: null,
        maxXP: activity.xp,
        label: activity.label || activity.type,
        monthNumber: monthNum,
        blockNumber: blockNum,
      }
    });
  };

  // Dynamic language info from meta
  const srcInfo = meta?.source || {};
  const tgtInfo = meta?.target || {};

  if (!selectedPair) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ fontSize: '3rem' }}>🌍</div>
        <h2 className="heading-md">No language path selected</h2>
        <button className="btn btn-primary" onClick={() => navigate('/onboarding')}>Choose a Language</button>
      </div>
    );
  }

  return (
    <div>
      {/* Header — language names from meta */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="heading-lg">
              {srcInfo.flag || '🏳'} → {tgtInfo.flag || '🏳'}{' '}
              <span className="gradient-text">{srcInfo.name} to {tgtInfo.name || tgtInfo.native}</span>
            </h1>
            <p className="text-muted" style={{ marginTop: '0.25rem' }}>
              {meta?.totalMonths || 3}-month learning roadmap — {(meta?.months || []).reduce((acc, m) => acc + (m.blocks?.length || 0), 0)} blocks
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            {currentProgress && (
              <div style={{ background: 'var(--color-accent-glow)', border: '1px solid var(--color-accent)', borderRadius: 'var(--radius-full)', padding: '0.375rem 0.875rem', display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                <span>⭐</span>
                <span style={{ fontWeight: 700, color: 'var(--color-accent-light)' }}>{currentProgress.total_xp} XP</span>
              </div>
            )}
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/onboarding')}>🔄 Switch Language</button>
          </div>
        </div>

        {/* Progress bar */}
        {currentProgress && (
          <div style={{ marginTop: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '0.375rem' }}>
              <span>Month {currentProgress.current_month}, Block {currentProgress.current_block}</span>
              <span>{completedSeqIds.size} / {Math.max(currentActivityId - 1, 0)} activities done</span>
            </div>
            <div className="xp-bar-container">
              <div className="xp-bar-fill" style={{ width: `${Math.max(Math.min((currentProgress.current_activity_id / 144) * 100, 100), 1)}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* Pair switcher */}
      {allProgress.length > 1 && (
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          {allProgress.map(p => (
            <button key={p.lang_pair_id}
              className={`btn btn-sm ${selectedPair === p.lang_pair_id ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => { setSelectedPair(p.lang_pair_id); dispatch(setCurrentPair(p.lang_pair_id)); }}>
              {p.lang_pair_id}
            </button>
          ))}
        </div>
      )}

      {/* Roadmap */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-text-muted)' }}>
          <div className="spinner" style={{ margin: '0 auto 1rem' }} />Loading roadmap...
        </div>
      ) : meta ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {(meta.months || []).map(month => {
            const monthBlocks = month.blocks || [];
            const monthActivities = monthBlocks.flatMap(b => b.activities || []);
            const monthCompleted = monthActivities.filter(a => isCompleted(a.id)).length;
            const monthTotal = monthActivities.length;

            return (
              <div key={month.month} className="card">
                {/* Month header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', marginBottom: expandedMonth === month.month ? '1.5rem' : 0 }}
                  onClick={() => setExpandedMonth(expandedMonth === month.month ? null : month.month)}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--color-primary-glow)', border: '2px solid var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, flexShrink: 0 }}>
                      M{month.month}
                    </div>
                    <div>
                      <div className="heading-sm">{month.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                        {month.targetLevel} · {monthBlocks.length} blocks · {monthCompleted}/{monthTotal} done
                      </div>
                    </div>
                  </div>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: '1.25rem' }}>
                    {expandedMonth === month.month ? '▲' : '▼'}
                  </span>
                </div>

                {/* Blocks */}
                {expandedMonth === month.month && monthBlocks.map(block => {
                  const blockDone = (block.activities || []).filter(a => isCompleted(a.id)).length;
                  const blockTotal = (block.activities || []).length;
                  return (
                    <div key={block.block} style={{ marginBottom: '1.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '0.75rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--color-border)' }}>
                        <span>Block {block.block}: {block.title}</span>
                        <span style={{ color: blockDone === blockTotal ? 'var(--color-success-light)' : 'var(--color-text-dim)' }}>
                          {blockDone}/{blockTotal} {blockDone === blockTotal ? '✓' : ''}
                        </span>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '0.625rem' }}>
                        {(block.activities || []).map(activity => {
                          const unlocked = isUnlocked(activity.id);
                          const completed = isCompleted(activity.id);
                          const isCurrent = activity.id === currentActivityId;
          const color = (ACTIVITY_COLORS[activity.type] || { base: '#888', glow: 'rgba(136,136,136,0.2)' }).base;
          const glow  = (ACTIVITY_COLORS[activity.type] || { base: '#888', glow: 'rgba(136,136,136,0.2)' }).glow;
                          const icon = ACTIVITY_ICONS[activity.type] || '📋';
                          const lbl = activity.label || (activity.type.charAt(0).toUpperCase() + activity.type.slice(1));

                          return (
                            <div key={activity.id}
                              onClick={() => handleActivityClick(activity, selectedPair, month.month, block.block)}
                              title={unlocked ? lbl : 'Complete previous activities first'}
                              style={{
                                padding: '0.75rem', borderRadius: 'var(--radius-md)', textAlign: 'center',
                                border: `1px solid ${isCurrent ? color : completed ? `${color}77` : 'var(--border)'}`,
                                background: completed
                                  ? `${color}20`
                                  : isCurrent
                                    ? 'var(--glass-bg)'
                                    : 'var(--glass-bg)',
                                backdropFilter: 'blur(12px)',
                                WebkitBackdropFilter: 'blur(12px)',
                                boxShadow: isCurrent ? `0 0 14px ${glow}` : completed ? `0 0 8px ${glow}` : 'none',
                                cursor: unlocked ? 'pointer' : 'not-allowed',
                                opacity: unlocked ? 1 : 0.38,
                                transition: 'all 0.2s', position: 'relative',
                              }}
                              className={unlocked ? 'card-interactive' : ''}>

                              {completed && <div style={{ position: 'absolute', top: 4, right: 6, fontSize: '0.65rem' }}>✅</div>}
                              {!unlocked && <div style={{ position: 'absolute', top: 4, right: 6, fontSize: '0.65rem' }}>🔒</div>}
                              {isCurrent && !completed && <div style={{ position: 'absolute', top: 5, right: 7, width: 6, height: 6, borderRadius: '50%', background: color, boxShadow: `0 0 6px ${color}` }} />}

                              <div style={{ fontSize: '1.4rem', marginBottom: '0.375rem' }}>{icon}</div>
                              <div style={{ fontSize: '0.72rem', fontWeight: 600, color: unlocked ? 'var(--text)' : 'var(--text-dim)' }}>{lbl}</div>
                              <div style={{ fontSize: '0.65rem', color, marginTop: '0.25rem', fontWeight: 700 }}>+{activity.xp} XP</div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-text-muted)' }}>
          <p>No roadmap data found for this language pair.</p>
        </div>
      )}
    </div>
  );
}
