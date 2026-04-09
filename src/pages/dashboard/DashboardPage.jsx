/**
 * src/pages/dashboard/DashboardPage.jsx
 * Main roadmap view — shows months, weeks, and activities with lock/unlock states.
 * Loads meta.json from backend and overlays user's completion data.
 */
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAllProgress, fetchPairs, setCurrentPair } from '../../store/progressSlice.js';
import { getMeta } from '../../api/content.js';
import { getCompletions } from '../../api/progress.js';

const ACTIVITY_ICONS = {
  lesson: '📖', vocab: '🔤', reading: '📄', writing: '✍', 
  listening: '🎧', speaking: '🎙', pronunciation: '🗣', test: '📝',
};
const ACTIVITY_COLORS = {
  lesson: '#6366f1', vocab: '#8b5cf6', reading: '#06b6d4',
  writing: '#10b981', listening: '#f59e0b', speaking: '#f97316',
  pronunciation: '#ec4899', test: '#ef4444',
};

const LANG_INFO = {
  hi: { name: 'Hindi', flag: '🇮🇳' },
  en: { name: 'English', flag: '🇬🇧' },
  ja: { name: 'Japanese', flag: '🇯🇵' },
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { allProgress, currentPairId } = useSelector(s => s.progress);
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

  useEffect(() => {
    if (!selectedPair) return;
    setLoading(true);
    Promise.all([
      getMeta(selectedPair).then(r => setMeta(r.data)),
      getCompletions(selectedPair).then(r => setCompletions(r.data)),
    ]).catch(console.error).finally(() => setLoading(false));
  }, [selectedPair]);

  const completedIds = new Set(completions.filter(c => c.passed).map(c => c.activity_id));
  const currentActivityId = currentProgress?.current_activity_id || 1;

  const isUnlocked = (activityId) => activityId <= currentActivityId;
  const isCompleted = (activityId) => completedIds.has(activityId);

  const handleActivityClick = (activity, pairId) => {
    if (!isUnlocked(activity.id)) return;
    navigate(`/activity/${pairId}/${activity.type}`, {
      state: { activityFile: activity.file, activityId: activity.id, maxXP: activity.xp, label: activity.label }
    });
  };

  if (!selectedPair) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ fontSize: '3rem' }}>🌍</div>
        <h2 className="heading-md">No language path selected</h2>
        <button className="btn btn-primary" onClick={() => navigate('/onboarding')}>Choose a Language</button>
      </div>
    );
  }

  const [src, tgt] = selectedPair.split('-');

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="heading-lg">
              {LANG_INFO[src]?.flag} → {LANG_INFO[tgt]?.flag}{' '}
              <span className="gradient-text">{LANG_INFO[src]?.name} to {LANG_INFO[tgt]?.name}</span>
            </h1>
            <p className="text-muted" style={{ marginTop: '0.25rem' }}>Your 6-month learning roadmap</p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            {/* XP badge */}
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
              <span>Month {currentProgress.current_month}, Week {currentProgress.current_week}</span>
              <span>{completedIds.size} activities completed</span>
            </div>
            <div className="xp-bar-container">
              <div className="xp-bar-fill" style={{ width: `${Math.min((currentProgress.current_activity_id / 43) * 100, 100)}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* Pair switcher for users with multiple pairs */}
      {allProgress.length > 1 && (
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          {allProgress.map(p => {
            const [s, t] = p.lang_pair_id.split('-');
            return (
              <button key={p.lang_pair_id}
                className={`btn btn-sm ${selectedPair === p.lang_pair_id ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => { setSelectedPair(p.lang_pair_id); dispatch(setCurrentPair(p.lang_pair_id)); }}>
                {LANG_INFO[s]?.flag} → {LANG_INFO[t]?.flag} {LANG_INFO[t]?.name}
              </button>
            );
          })}
        </div>
      )}

      {/* Roadmap */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-text-muted)' }}>
          <div className="spinner" style={{ margin: '0 auto 1rem' }} />
          Loading roadmap...
        </div>
      ) : meta ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {meta.months?.map(month => (
            <div key={month.month} className="card">
              {/* Month header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', marginBottom: expandedMonth === month.month ? '1.5rem' : 0 }}
                onClick={() => setExpandedMonth(expandedMonth === month.month ? null : month.month)}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--color-primary-glow)', border: '2px solid var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.875rem' }}>
                      M{month.month}
                    </div>
                    <div>
                      <div className="heading-sm">{month.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{month.targetLevel} • {month.description}</div>
                    </div>
                  </div>
                </div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '1.25rem' }}>{expandedMonth === month.month ? '▲' : '▼'}</span>
              </div>

              {/* Weeks */}
              {expandedMonth === month.month && month.weeks?.map(week => (
                <div key={week.week} style={{ marginBottom: '1.25rem' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '0.75rem', paddingBottom: '0.375rem', borderBottom: '1px solid var(--color-border)' }}>
                    Week {week.globalWeek || week.week}: {week.title}
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '0.625rem' }}>
                    {week.activities?.map(activity => {
                      const unlocked = isUnlocked(activity.id);
                      const completed = isCompleted(activity.id);
                      const isCurrent = activity.id === currentActivityId;
                      const color = ACTIVITY_COLORS[activity.type] || '#6366f1';
                      const icon = ACTIVITY_ICONS[activity.type] || '📋';
                      const label = activity.label || activity.type.charAt(0).toUpperCase() + activity.type.slice(1);

                      return (
                        <div key={activity.id}
                          onClick={() => handleActivityClick(activity, selectedPair)}
                          style={{
                            padding: '0.75rem',
                            borderRadius: 'var(--radius-md)',
                            border: `1px solid ${isCurrent ? color : completed ? `${color}66` : 'var(--color-border)'}`,
                            background: completed ? `${color}18` : isCurrent ? `${color}28` : 'var(--color-surface-2)',
                            cursor: unlocked ? 'pointer' : 'not-allowed',
                            opacity: unlocked ? 1 : 0.45,
                            transition: 'all 0.2s',
                            position: 'relative',
                            textAlign: 'center',
                          }}
                          className={unlocked ? 'card-interactive' : ''}
                        >
                          {/* Status indicator */}
                          {completed && <div style={{ position: 'absolute', top: 4, right: 6, fontSize: '0.65rem' }}>✅</div>}
                          {!unlocked && <div style={{ position: 'absolute', top: 4, right: 6, fontSize: '0.65rem' }}>🔒</div>}
                          {isCurrent && !completed && <div style={{ position: 'absolute', top: 4, right: 6, width: 6, height: 6, borderRadius: '50%', background: color, boxShadow: `0 0 6px ${color}` }} />}

                          <div style={{ fontSize: '1.5rem', marginBottom: '0.375rem' }}>{icon}</div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: unlocked ? 'var(--color-text)' : 'var(--color-text-dim)' }}>{label}</div>
                          <div style={{ fontSize: '0.65rem', color: color, marginTop: '0.25rem', fontWeight: 600 }}>+{activity.xp} XP</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-text-muted)' }}>
          <p>No roadmap data found for this language pair.</p>
        </div>
      )}
    </div>
  );
}
