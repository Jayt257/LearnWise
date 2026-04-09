/**
 * src/pages/social/LeaderboardPage.jsx
 * Displays global and friends-only leaderboards.
 */
import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { getLeaderboard, getFriendsLeaderboard } from '../../api/users.js';

export default function LeaderboardPage() {
  const { currentPairId } = useSelector(s => s.progress);
  const { user } = useSelector(s => s.auth);
  const [globalBoard, setGlobalBoard] = useState([]);
  const [friendsBoard, setFriendsBoard] = useState([]);
  const [view, setView] = useState('global');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!currentPairId) { setLoading(false); return; }
    setLoading(true);
    Promise.all([
      getLeaderboard(currentPairId).then(r => setGlobalBoard(r.data)),
      getFriendsLeaderboard(currentPairId).then(r => setFriendsBoard(r.data)),
    ]).finally(() => setLoading(false));
  }, [currentPairId]);

  if (!currentPairId) return <div style={{ padding: '2rem' }}>Please select a language path in the roadmap first.</div>;
  if (loading) return <div style={{ padding: '4rem', textAlign: 'center' }}><span className="spinner" /></div>;

  const data = view === 'global' ? globalBoard : friendsBoard;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 className="heading-lg" style={{ marginBottom: '0.5rem' }}>🏆 Leaderboard</h1>
        <p className="text-muted">Top learners in {currentPairId.toUpperCase()}</p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '2rem' }}>
        <button className={`btn ${view === 'global' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setView('global')}>🌍 Global</button>
        <button className={`btn ${view === 'friends' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setView('friends')}>🤝 Friends</button>
      </div>

      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        {data.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>No data available yet.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--color-surface-2)', borderBottom: '1px solid var(--color-border)', textAlign: 'left' }}>
                <th style={{ padding: '1rem 1.5rem', width: 80 }}>Rank</th>
                <th style={{ padding: '1rem' }}>User</th>
                <th style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>Total XP</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry, i) => (
                <tr key={entry.user_id} style={{ borderBottom: '1px solid var(--color-border)', background: entry.user_id === user.id ? 'var(--color-primary-glow)' : 'transparent' }}>
                  <td style={{ padding: '1rem 1.5rem', fontWeight: 700, color: i < 3 ? 'var(--color-accent-light)' : 'var(--color-text-muted)' }}>
                    {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${entry.rank}`}
                  </td>
                  <td style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--color-surface-3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600 }}>
                      {entry.display_name?.[0]?.toUpperCase() || entry.username[0].toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600 }}>{entry.display_name || entry.username} {entry.user_id === user.id && '(You)'}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>@{entry.username}</div>
                    </div>
                  </td>
                  <td style={{ padding: '1rem 1.5rem', textAlign: 'right', fontWeight: 700, color: 'var(--color-accent-light)' }}>
                    {entry.total_xp}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
