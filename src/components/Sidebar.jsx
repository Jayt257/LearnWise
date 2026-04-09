/**
 * src/components/Sidebar.jsx
 * Fixed left sidebar navigation for all user pages.
 */
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/authSlice.js';

const NAV_ITEMS = [
  { icon: '🗺', label: 'Roadmap', path: '/dashboard' },
  { icon: '🏆', label: 'Leaderboard', path: '/leaderboard' },
  { icon: '👤', label: 'Profile', path: '/profile' },
  { icon: '🔍', label: 'Find Friends', path: '/search' },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { user } = useSelector(s => s.auth);
  const { currentPairId } = useSelector(s => s.progress);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <div className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <span className="gradient-text">🌐 LearnWise</span>
      </div>

      {/* User info */}
      {user && (
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--color-primary-glow)', border: '2px solid var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem', flexShrink: 0 }}>
            {user.display_name?.[0]?.toUpperCase() || user.username?.[0]?.toUpperCase() || '?'}
          </div>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontWeight: 600, fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user.display_name || user.username}</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--color-text-dim)' }}>@{user.username}</div>
          </div>
        </div>
      )}

      {/* Nav items */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map(item => (
          <div
            key={item.path}
            className={`nav-item ${location.pathname.startsWith(item.path) ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>

      {/* Current language badge */}
      {currentPairId && (
        <div style={{ padding: '0.75rem 1.5rem', borderTop: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--color-text-dim)', marginBottom: '0.25rem' }}>Current path</div>
          <div className="badge badge-primary" style={{ fontSize: '0.8rem' }}>
            🌐 {currentPairId.toUpperCase()}
          </div>
        </div>
      )}

      {/* Logout */}
      <div style={{ padding: '1rem' }}>
        <button className="btn btn-ghost btn-full" style={{ justifyContent: 'flex-start', gap: '0.75rem' }} onClick={handleLogout}>
          <span>🚪</span> Logout
        </button>
      </div>
    </div>
  );
}
