/**
 * src/pages/social/LeaderboardPage.jsx
 * Premium leaderboard — Olympic podium top-3 with metallic cards + glass row list.
 * One-shot metallic flash via JS state (no CSS-only loop bug).
 */
import React, { useEffect, useState, useRef } from 'react';
import { useSelector } from 'react-redux';
import { getLeaderboard, getFriendsLeaderboard } from '../../api/users.js';

/* ── Metallic colour palettes ──────────────────────────────── */
const MEDALS = {
  0: {
    rank: 1,
    border:  '#D4AF37',
    bg:      'linear-gradient(160deg, rgba(212,175,55,0.18) 0%, rgba(170,130,20,0.06) 100%)',
    shine:   'rgba(255,235,140,0.55)',
    label:   'GOLD',
    height:  200,
    badge:   null,          // crown handled separately
  },
  1: {
    rank: 2,
    border:  '#C0C0C0',
    bg:      'linear-gradient(160deg, rgba(192,192,192,0.15) 0%, rgba(140,140,140,0.05) 100%)',
    shine:   'rgba(240,240,240,0.55)',
    label:   'SILVER',
    height:  170,
    badge:   '🥈',
  },
  2: {
    rank: 3,
    border:  '#CD7F32',
    bg:      'linear-gradient(160deg, rgba(205,127,50,0.15) 0%, rgba(150,90,30,0.05) 100%)',
    shine:   'rgba(255,200,120,0.50)',
    label:   'BRONZE',
    height:  155,
    badge:   '🥉',
  },
};

/* podium order: 2nd | 1st | 3rd */
const PODIUM_ORDER = [1, 0, 2];

/* ── Podium card component ─────────────────────────────────── */
function PodiumCard({ entry, medalIdx, isMe }) {
  const [shining, setShining] = useState(false);
  const timerRef = useRef(null);
  const m = MEDALS[medalIdx];

  const handleMouseEnter = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setShining(true);
    // Auto-clear after animation completes so class doesn't linger
    timerRef.current = setTimeout(() => setShining(false), 600);
  };
  const handleMouseLeave = () => {
    // No immediate clear — let the animation finish naturally via timeout above
  };

  return (
    <div
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        position: 'relative',
        overflow: 'hidden',
        width: 160,
        height: m.height,
        borderRadius: 'var(--radius-lg)',
        border: `2px solid ${m.border}`,
        background: m.bg,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        cursor: 'default',
        transition: 'transform 0.2s, box-shadow 0.2s',
        boxShadow: isMe
          ? `0 0 0 2px var(--primary), 0 8px 32px ${m.border}44`
          : `0 8px 32px ${m.border}33`,
        transform: medalIdx === 0 ? 'translateY(-16px)' : 'none',
      }}
    >
      {/* Metallic shine — sweeps once on JS class toggle */}
      <div style={{
        position: 'absolute',
        inset: 0,
        background: `linear-gradient(105deg, transparent 25%, ${m.shine} 50%, transparent 75%)`,
        transform: shining ? 'translateX(200%)' : 'translateX(-200%)',
        transition: shining ? 'transform 0.55s ease' : 'none',
        pointerEvents: 'none',
        zIndex: 2,
      }} />

      {/* Crown — only on #1 */}
      {medalIdx === 0 && (
        <div style={{
          position: 'absolute',
          top: -28,
          left: '50%',
          transform: 'translateX(-50%)',
          fontSize: '1.6rem',
          animation: 'float 2.2s ease-in-out infinite',
          zIndex: 3,
        }}>👑</div>
      )}

      {/* Medal badge — #2 and #3 */}
      {m.badge && (
        <div style={{
          position: 'absolute',
          bottom: 8,
          right: 10,
          fontSize: '1.4rem',
          zIndex: 3,
        }}>{m.badge}</div>
      )}

      {/* Avatar */}
      <div style={{
        width: 52,
        height: 52,
        borderRadius: '50%',
        border: `2px solid ${m.border}`,
        background: 'var(--surface-3)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '1.3rem',
        fontWeight: 700,
        fontFamily: 'var(--font-display)',
        color: m.border,
        zIndex: 1,
        position: 'relative',
      }}>
        {(entry.display_name?.[0] || entry.username[0]).toUpperCase()}
      </div>

      {/* Name */}
      <div style={{ textAlign: 'center', zIndex: 1, position: 'relative' }}>
        <div style={{ fontWeight: 700, fontSize: '0.82rem', color: 'var(--text)' }}>
          {entry.display_name || entry.username}
          {isMe && <span style={{ color: m.border, marginLeft: 4 }}>(You)</span>}
        </div>
        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>@{entry.username}</div>
        <div style={{ fontWeight: 800, fontSize: '0.9rem', color: m.border, marginTop: '0.25rem' }}>
          {entry.total_xp} XP
        </div>
      </div>

      {/* Rank label */}
      <div style={{ fontSize: '0.65rem', fontWeight: 700, letterSpacing: '0.1em', color: m.border, zIndex: 1, position: 'relative' }}>
        #{m.rank} · {m.label}
      </div>
    </div>
  );
}

/* ── Main page ─────────────────────────────────────────────── */
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

  if (!currentPairId) return (
    <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
      Please select a language path in the roadmap first.
    </div>
  );
  if (loading) return (
    <div style={{ padding: '4rem', textAlign: 'center' }}>
      <span className="spinner" />
    </div>
  );

  const data = view === 'global' ? globalBoard : friendsBoard;
  const top3 = data.slice(0, 3);
  const rest = data.slice(3);

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 className="heading-lg" style={{ marginBottom: '0.5rem' }}>🏆 Leaderboard</h1>
        <p className="text-muted">Top learners in {currentPairId.toUpperCase()}</p>
      </div>

      {/* Pill tab switcher */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        marginBottom: '3rem',
      }}>
        <div style={{
          display: 'inline-flex',
          border: '1px solid var(--border-strong)',
          borderRadius: 'var(--radius-full)',
          padding: '3px',
          background: 'var(--surface-2)',
          backdropFilter: 'blur(12px)',
        }}>
          {[['global', '🌍 Global'], ['friends', '🤝 Friends']].map(([key, label]) => (
            <button
              key={key}
              onClick={() => setView(key)}
              style={{
                padding: '0.45rem 1.25rem',
                borderRadius: 'var(--radius-full)',
                border: 'none',
                background: view === key ? 'var(--surface-3)' : 'transparent',
                color: view === key ? 'var(--text)' : 'var(--text-muted)',
                fontWeight: view === key ? 700 : 500,
                cursor: 'pointer',
                fontSize: '0.875rem',
                transition: 'all 0.2s',
              }}
            >{label}</button>
          ))}
        </div>
      </div>

      {data.length === 0 ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          No data available yet.
        </div>
      ) : (
        <>
          {/* ── Podium ─────────────────────────────────── */}
          {top3.length > 0 && (
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'flex-end',
              gap: '1rem',
              marginBottom: '2.5rem',
              paddingTop: '2.5rem', // space for floating crown
            }}>
              {PODIUM_ORDER.map(idx => {
                const entry = top3[idx];
                if (!entry) return null;
                return (
                  <PodiumCard
                    key={entry.user_id}
                    entry={entry}
                    medalIdx={idx}
                    isMe={entry.user_id === user?.id}
                  />
                );
              })}
            </div>
          )}

          {/* ── Rows 4+ ───────────────────────────────── */}
          {rest.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {rest.map((entry, i) => {
                const isMe = entry.user_id === user?.id;
                return (
                  <div key={entry.user_id} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '0.75rem 1.25rem',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--glass-bg)',
                    backdropFilter: 'blur(16px)',
                    WebkitBackdropFilter: 'blur(16px)',
                    border: isMe ? '1px solid var(--primary)' : '1px solid var(--glass-border)',
                    transition: 'box-shadow 0.2s',
                  }}>
                    {/* Rank */}
                    <div style={{ width: 36, textAlign: 'center', fontWeight: 700, color: 'var(--text-muted)', fontSize: '0.85rem', flexShrink: 0 }}>
                      #{entry.rank || i + 4}
                    </div>
                    {/* Avatar */}
                    <div style={{
                      width: 36, height: 36, borderRadius: '50%',
                      background: 'var(--surface-3)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: 700, fontSize: '0.9rem', flexShrink: 0,
                      color: 'var(--text-muted)',
                    }}>
                      {(entry.display_name?.[0] || entry.username[0]).toUpperCase()}
                    </div>
                    {/* Name */}
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>
                        {entry.display_name || entry.username}
                        {isMe && <span style={{ color: 'var(--primary)', marginLeft: 6 }}>(You)</span>}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>@{entry.username}</div>
                    </div>
                    {/* XP */}
                    <div style={{ fontWeight: 700, color: 'var(--amber)', fontSize: '0.9rem' }}>
                      {entry.total_xp} XP
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
