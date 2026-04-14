/
  src/components/Sidebar.jsx
  Fixed left sidebar — premium redesign.
  Logic (logout, navigation, progress reading) untouched.
 /
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/authSlice.js';
import AuroraBar    from './AuroraBar.jsx';
import ThemeToggle  from './ThemeToggle.jsx';

const NAV_ITEMS = [
  { icon: '', label: 'Roadmap',     path: '/dashboard' },
  { icon: '', label: 'Leaderboard', path: '/leaderboard' },
  { icon: '', label: 'Profile',      path: '/profile' },
  { icon: '', label: 'Find Friends', path: '/search' },
];

export default function Sidebar() {
  const navigate  = useNavigate();
  const location  = useLocation();
  const dispatch  = useDispatch();
  const { user }          = useSelector(s => s.auth);
  const { currentPairId } = useSelector(s => s.progress);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const initial = (user?.display_name?.[] || user?.username?.[] || '?').toUpperCase();
  const displayName = user?.display_name || user?.username || '';

  const SidebarContent = () => (
    <>
      {/ Aurora accent bar /}
      <AuroraBar />

      {/ Logo /}
      <div className="sidebar-logo">
        <span className="logo-star">✦</span>
        <span className="gradient-text">LearnWise</span>
      </div>

      {/ User info /}
      {user && (
        <div style={{
          padding: 'rem .rem',
          borderBottom: 'px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: '.rem',
        }}>
          {/ Avatar with gradient ring /}
          <div style={{
            width: , height: ,
            borderRadius: '%',
            background: 'linear-gradient(deg, var(--primary), var(--cyan))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'var(--font-display)',
            fontWeight: ,
            fontSize: 'rem',
            color: 'white',
            flexShrink: ,
            boxShadow: '  px var(--primary-glow)',
          }}>
            {initial}
          </div>
          <div style={{ minWidth:  }}>
            <div style={{
              fontWeight: ,
              fontSize: '.rem',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {displayName}
            </div>
            <div style={{
              fontSize: '.rem',
              color: 'var(--text-dim)',
              fontFamily: 'var(--font-mono)',
            }}>
              @{user.username}
            </div>
          </div>
        </div>
      )}

      {/ Nav items /}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item, i) => (
          <div
            key={item.path}
            className={`nav-item animate-slide-in stagger-${i + } ${
              location.pathname.startsWith(item.path) ? 'active' : ''
            }`}
            onClick={() => { navigate(item.path); setMobileOpen(false); }}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>

      {/ Current language badge /}
      {currentPairId && (
        <div style={{ padding: '.rem .rem', borderTop: 'px solid var(--border)' }}>
          <div style={{
            fontSize: '.rem',
            color: 'var(--text-dim)',
            marginBottom: '.rem',
            textTransform: 'uppercase',
            letterSpacing: '.em',
            fontWeight: ,
          }}>
            Active Path
          </div>
          <div className="badge badge-primary" style={{ fontSize: '.rem', padding: '.rem .rem' }}>
             {currentPairId.toUpperCase()}
          </div>
        </div>
      )}

      {/ Bottom section /}
      <div style={{ padding: '.rem rem', borderTop: 'px solid var(--border)', display: 'flex', flexDirection: 'column', gap: '.rem' }}>
        <ThemeToggle />
        <button
          className="btn btn-ghost btn-full"
          style={{ justifyContent: 'flex-start', gap: '.rem', color: 'var(--danger-light)' }}
          onClick={handleLogout}
        >
          <span></span> Logout
        </button>
      </div>
    </>
  );

  return (
    <>
      {/ Desktop sidebar /}
      <div className="sidebar" id="sidebar">
        <SidebarContent />
      </div>

      {/ Mobile: top bar + hamburger /}
      <div className="mobile-header">
        <span className="gradient-text" style={{ fontFamily: 'var(--font-display)', fontWeight: , fontSize: '.rem' }}>
          ✦ LearnWise
        </span>
        <button
          className="btn btn-ghost btn-icon"
          onClick={() => setMobileOpen(o => !o)}
          aria-label="Open menu"
        >
          ☰
        </button>
      </div>

      {/ Mobile drawer /}
      {mobileOpen && (
        <>
          <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} />
          <div className="sidebar open">
            <SidebarContent />
          </div>
        </>
      )}
    </>
  );
}
