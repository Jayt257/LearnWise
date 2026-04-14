/**
 * src/pages/social/LeaderboardPage.jsx
 * Premium redesign — podium top-3, card-per-row layout, pill tabs.
 * All data fetching logic is untouched.
 */
import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { getLeaderboard, getFriendsLeaderboard } from '../../api/users.js';

const PODIUM = ['🥇', '🥈', '🥉'];
const PODIUM_COLORS = ['#FFB830', '#94A3B8', '#FC8C61'];

function AvatarCircle({ name, size = 40, color }) {
  const initial = (name || '?')[0].toUpperCase();
  return (
    <div style={{
      width: size, height: size,
      borderRadius: '50%',
      background: color || 'var(--primary-glow)',
      border: `2px solid ${color || 'var(--primary)'}`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'var(--font-display)',
      fontWeight: 700,
      fontSize: size * 0.4,
      color: 'white',
      flexShrink: 0,
      boxShadow: `0 0 12px ${color || 'var(--primary-glow)'}`,
    }}>
      {initial}
    </div>
  );
}

export default function LeaderboardPage() {
  const { currentPairId } = useSelector(s => s.progress);
  const { user }          = useSelector(s => s.auth);
  const [globalBoard, setGlobalBoard] = useState([]);
  const [friendsBoard, setFriendsBoard] = useState([]);
  const [view,    setView]    = useState('global');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!currentPairId) { setLoading(false); return; }
    setLoading(true);
    Promise.all([
      getLeaderboard(currentPairId).then(r => setGlobalBoard(r.data)),
      getFriendsLeaderboard(currentPairId).then(r => setFriendsBoard(r.data)),
    ]).finally(() => setLoading(false));
  }, [currentPairId]);

  if (!currentPairId) return (
    <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
      <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🗺️</div>
      <p>Please select a language path in the roadmap first.</p>
    </div>
  );

  if (loading) return (
    <div style={{ padding: '4rem', textAlign: 'center' }}>
      <span className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
    </div>
  );

  const data = view === 'global' ? globalBoard : friendsBoard;
  const top3 = data.slice(0, 3);
  const rest  = data.slice(3);

  return (
    <div style={{ maxWidth: 760, margin: '0 auto' }} className="animate-fade-up">
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>🏆</div>
        <h1 className="heading-lg" style={{ marginBottom: '0.375rem' }}>Leaderboard</h1>
        <p className="text-muted">
          Top learners in{' '}
          <span className="badge badge-primary" style={{ fontSize: '0.85rem' }}>
            {currentPairId.toUpperCase()}
          </span>
        </p>
      </div>

      {/* Pill tab switcher */}
      <div style={{
        display: 'flex', justifyContent: 'center', marginBottom: '2rem',
        background: 'var(--surface-2)', borderRadius: 'var(--radius-full)',
        padding: '0.25rem', width: 'fit-content', margin: '0 auto 2rem',
        border: '1px solid var(--border)',
      }}>
        {[
          { key: 'global', label: '🌍 Global' },
          { key: 'friends', label: '🤝 Friends' },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setView(tab.key)}
            style={{
              padding: '0.5rem 1.375rem',
              borderRadius: 'var(--radius-full)',
              border: 'none',
              background: view === tab.key
                ? 'linear-gradient(135deg, var(--primary), var(--primary-dark))'
                : 'transparent',
              color: view === tab.key ? 'white' : 'var(--text-muted)',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: 'pointer',
              transition: 'all var(--transition)',
              boxShadow: view === tab.key ? '0 4px 12px var(--primary-glow)' : 'none',
              fontFamily: 'var(--font-sans)',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {data.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📭</div>
          <p>No data available yet.</p>
        </div>
      ) : (
        <>
          {/* Podium — top 3 */}
          {top3.length > 0 && (
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
              {top3.map((entry, i) => (
                <div
                  key={entry.user_id}
                  className="card card-interactive podium-metal animate-fade-up"
                  style={{
                    flex: '1 1 180px',
                    textAlign: 'center',
                    background: entry.user_id === user.id
                      ? 'rgba(var(--primary-rgb), 0.10)'
                      : 'var(--surface)',
                    border: `1px solid ${PODIUM_COLORS[i]}80`,
                    boxShadow: `0 8px 32px ${PODIUM_COLORS[i]}40`,
                    animationDelay: `${i * 0.06}s`,
                    transform: i === 0 ? 'scale(1.04)' : 'none',
                    '--hover-glow': `${PODIUM_COLORS[i]}80`,
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = i === 0 ? 'scale(1.08) translateY(-6px)' : 'scale(1.04) translateY(-6px)';
                    e.currentTarget.style.boxShadow = `0 12px 48px ${PODIUM_COLORS[i]}80`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = i === 0 ? 'scale(1.04)' : 'none';
                    e.currentTarget.style.boxShadow = `0 8px 32px ${PODIUM_COLORS[i]}40`;
                  }}
                >
                  <div style={{ position: 'relative', display: 'inline-block', marginBottom: '0.5rem' }}>
                    <AvatarCircle
                      name={entry.display_name || entry.username}
                      size={i === 0 ? 64 : 52}
                      color={PODIUM_COLORS[i]}
                    />
                    <div style={{ 
                      position: 'absolute', 
                      bottom: -8, 
                      right: -8, 
                      fontSize: i === 0 ? '1.85rem' : '1.35rem',
                      filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.4))'
                    }}>
                      {PODIUM[i]}
                    </div>
                  </div>
                  <div style={{ marginTop: '0.75rem', fontWeight: 700, fontSize: '0.9rem' }}>
                    {entry.display_name || entry.username}
                    {entry.user_id === user.id && ' (You)'}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    @{entry.username}
                  </div>
                  <div style={{
                    marginTop: '0.75rem',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 700,
                    color: PODIUM_COLORS[i],
                    fontSize: '1rem',
                  }}>
                    {entry.total_xp} XP
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Remaining rows */}
          {rest.length > 0 && (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              {rest.map((entry, i) => (
                <div
                  key={entry.user_id}
                  className="podium-metal"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '0.875rem 1.5rem',
                    borderBottom: i < rest.length - 1 ? '1px solid var(--border)' : 'none',
                    background: entry.user_id === user.id
                      ? 'rgba(var(--primary-rgb), 0.08)'
                      : 'transparent',
                    transition: 'background var(--transition)',
                  }}
                >
                  <div style={{
                    width: 32, textAlign: 'center',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 700,
                    color: 'var(--text-dim)',
                    fontSize: '0.8rem',
                    flexShrink: 0,
                  }}>
                    #{entry.rank || i + 4}
                  </div>
                  <AvatarCircle name={entry.display_name || entry.username} size={36} color="var(--primary)" />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>
                      {entry.display_name || entry.username}
                      {entry.user_id === user.id && (
                        <span className="badge badge-primary" style={{ marginLeft: '0.5rem' }}>You</span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                      @{entry.username}
                    </div>
                  </div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--amber)' }}>
                    {entry.total_xp} XP
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
