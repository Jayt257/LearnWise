/**
 * src/pages/social/ProfilePage.jsx
 * Premium redesign — hero avatar, stats row, glass cards.
 * All API calls and state management are untouched.
 */
import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  getMyProfile, updateProfile, getFriends,
  getFriendRequests, acceptFriendRequest,
  declineFriendRequest, removeFriend,
} from '../../api/users.js';
import { updateUser } from '../../store/authSlice.js';

function UserRow({ name, username, children, color }) {
  const initial = (name || username || '?')[0].toUpperCase();
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      background: 'var(--surface-2)',
      padding: '0.875rem 1rem',
      borderRadius: 'var(--radius-md)',
      border: '1px solid var(--border)',
      transition: 'border-color var(--transition)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
        <div style={{
          width: 38, height: 38, borderRadius: '50%',
          background: color || 'var(--primary-glow)',
          border: `2px solid ${color || 'var(--primary)'}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'var(--font-display)', fontWeight: 700, color: 'white',
          flexShrink: 0,
        }}>
          {initial}
        </div>
        <div>
          <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{name || username}</div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            @{username}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>{children}</div>
    </div>
  );
}

export default function ProfilePage() {
  const dispatch = useDispatch();
  const { user } = useSelector(s => s.auth);
  const [profile,  setProfile]  = useState(null);
  const [friends,  setFriends]  = useState([]);
  const [requests, setRequests] = useState([]);
  const [editing,  setEditing]  = useState(false);
  const [form,     setForm]     = useState({ display_name: '', native_lang: '' });

  const loadData = () => {
    getMyProfile().then(r => { setProfile(r.data); setForm({ display_name: r.data.display_name || '', native_lang: r.data.native_lang || '' }); });
    getFriends().then(r => setFriends(r.data.friends));
    getFriendRequests().then(r => setRequests(r.data.requests));
  };

  useEffect(() => { loadData(); }, []);

  const handleSave = async () => {
    try {
      const { data } = await updateProfile(form);
      setProfile(data); dispatch(updateUser(data)); setEditing(false);
    } catch { alert('Update failed'); }
  };

  const handleAccept  = async (id) => { await acceptFriendRequest(id);  loadData(); };
  const handleDecline = async (id) => { await declineFriendRequest(id); loadData(); };
  const handleRemove  = async (id) => { if (confirm('Remove friend?')) { await removeFriend(id); loadData(); } };

  if (!profile) return (
    <div style={{ padding: '6rem', textAlign: 'center' }}>
      <span className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
    </div>
  );

  const initial = (profile.display_name || profile.username || '?')[0].toUpperCase();

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.75rem' }} className="animate-fade-up">

      {/* ── Hero ────────────────────────────────────────────── */}
      <div className="card" style={{ 
        padding: '2.25rem', 
        textAlign: 'center', 
        position: 'relative', 
        overflow: 'hidden',
        backdropFilter: 'blur(60px) saturate(220%)',
        WebkitBackdropFilter: 'blur(60px) saturate(220%)',
        background: 'color-mix(in srgb, var(--glass-bg-strong) 80%, transparent)'
      }}>
        {/* Background glow */}
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(var(--primary-rgb),0.10) 0%, transparent 60%)', pointerEvents: 'none' }} />

        {/* Avatar */}
        <div style={{ position: 'relative', display: 'inline-block', marginBottom: '1.25rem' }}>
          <div style={{
            width: 88, height: 88,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--primary), var(--cyan))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'var(--font-display)', fontWeight: 800,
            fontSize: '2.25rem', color: 'white',
            boxShadow: '0 0 32px var(--primary-glow), 0 8px 20px rgba(0,0,0,0.3)',
          }}>
            {initial}
          </div>
        </div>

        <h1 className="heading-lg" style={{ marginBottom: '0.25rem' }}>
          {profile.display_name || profile.username}
        </h1>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
          @{profile.username}
        </div>
        <div style={{ marginTop: '0.5rem', fontSize: '0.83rem', color: 'var(--text-muted)' }}>
          {profile.email}
        </div>

        {/* Stats row */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginTop: '1.75rem', flexWrap: 'wrap' }}>
          {[
            { label: 'Friends',  value: friends.length,  icon: '🤝' },
            { label: 'Requests', value: requests.length, icon: '📩' },
            { label: 'Language', value: (profile.native_lang || 'N/A').toUpperCase(), icon: '🌐' },
          ].map(stat => (
            <div key={stat.label} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{stat.icon}</div>
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.25rem' }}>
                {stat.value}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Account info ────────────────────────────────────── */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 className="heading-sm">Account Information</h2>
          <button
            className={`btn btn-sm ${editing ? 'btn-success' : 'btn-ghost'}`}
            onClick={() => editing ? handleSave() : setEditing(true)}
          >
            {editing ? '💾 Save Changes' : '✏️ Edit Profile'}
          </button>
        </div>

        <div className="grid-2">
          <div className="form-group">
            <label className="form-label">Username</label>
            <input className="form-input" disabled value={profile.username} />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-input" disabled value={profile.email} />
          </div>
          <div className="form-group">
            <label className="form-label">Display Name</label>
            <input
              className="form-input"
              disabled={!editing}
              value={editing ? form.display_name : profile.display_name || ''}
              onChange={e => setForm(p => ({ ...p, display_name: e.target.value }))}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Native Language</label>
            <select
              className="form-input"
              disabled={!editing}
              value={editing ? form.native_lang : profile.native_lang || ''}
              onChange={e => setForm(p => ({ ...p, native_lang: e.target.value }))}
            >
              <option value="en">🇬🇧 English</option>
              <option value="hi">🇮🇳 Hindi</option>
              <option value="ja">🇯🇵 Japanese</option>
            </select>
          </div>
        </div>
      </div>

      {/* ── Friend requests + friends ────────────────────────── */}
      <div className="grid-2" style={{ gap: '1.5rem' }}>
        {/* Friend Requests */}
        <div className="card">
          <h2 className="heading-sm" style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📩 Requests
            {requests.length > 0 && (
              <span className="badge badge-danger">{requests.length}</span>
            )}
          </h2>
          {requests.length === 0 ? (
            <p className="text-muted" style={{ fontSize: '0.875rem', textAlign: 'center', padding: '1.5rem 0' }}>
              No pending requests
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {requests.map(req => (
                <UserRow key={req.id} name={req.sender.display_name} username={req.sender.username} color="var(--rose)">
                  <button className="btn btn-success btn-sm" onClick={() => handleAccept(req.id)}>✓</button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDecline(req.id)}>✕</button>
                </UserRow>
              ))}
            </div>
          )}
        </div>

        {/* Friends List */}
        <div className="card">
          <h2 className="heading-sm" style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            🤝 Friends
            <span className="badge badge-secondary">{friends.length}</span>
          </h2>
          {friends.length === 0 ? (
            <p className="text-muted" style={{ fontSize: '0.875rem', textAlign: 'center', padding: '1.5rem 0' }}>
              No friends yet. Search to add some!
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {friends.map(f => (
                <UserRow key={f.id} name={f.display_name} username={f.username} color="var(--cyan)">
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => handleRemove(f.id)}
                    style={{ color: 'var(--danger)' }}
                  >
                    Remove
                  </button>
                </UserRow>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
