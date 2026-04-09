/**
 * src/pages/social/ProfilePage.jsx
 * User profile, settings, and friend requests.
 */
import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { getMyProfile, updateProfile, getFriends, getFriendRequests, acceptFriendRequest, declineFriendRequest, removeFriend } from '../../api/users.js';
import { updateUser } from '../../store/authSlice.js';

export default function ProfilePage() {
  const dispatch = useDispatch();
  const { user } = useSelector(s => s.auth);
  const [profile, setProfile] = useState(null);
  const [friends, setFriends] = useState([]);
  const [requests, setRequests] = useState([]);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ display_name: '', native_lang: '' });

  const loadData = () => {
    getMyProfile().then(r => { setProfile(r.data); setForm({ display_name: r.data.display_name || '', native_lang: r.data.native_lang || '' }); });
    getFriends().then(r => setFriends(r.data.friends));
    getFriendRequests().then(r => setRequests(r.data.requests));
  };

  useEffect(() => { loadData(); }, []);

  const handleSave = async () => {
    try {
      const { data } = await updateProfile(form);
      setProfile(data);
      dispatch(updateUser(data));
      setEditing(false);
    } catch (e) { alert('Update failed'); }
  };

  const handleAccept = async (id) => { await acceptFriendRequest(id); loadData(); };
  const handleDecline = async (id) => { await declineFriendRequest(id); loadData(); };
  const handleRemove = async (id) => { if(confirm('Remove friend?')) { await removeFriend(id); loadData(); } };

  if (!profile) return <div style={{ padding: '4rem', textAlign: 'center' }}><span className="spinner" /></div>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <h1 className="heading-lg">My Profile</h1>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <h2 className="heading-sm">Account Information</h2>
          <button className="btn btn-ghost btn-sm" onClick={() => editing ? handleSave() : setEditing(true)}>
            {editing ? '💾 Save' : '✏ Edit'}
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
            <input className="form-input" disabled={!editing} value={editing ? form.display_name : profile.display_name || ''} onChange={e => setForm(p => ({ ...p, display_name: e.target.value }))} />
          </div>
          <div className="form-group">
            <label className="form-label">Native Language</label>
            <select className="form-input" disabled={!editing} value={editing ? form.native_lang : profile.native_lang || ''} onChange={e => setForm(p => ({ ...p, native_lang: e.target.value }))}>
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="ja">Japanese</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid-2" style={{ gap: '2rem' }}>
        {/* Friend Requests */}
        <div className="card">
          <h2 className="heading-sm" style={{ marginBottom: '1.5rem' }}>Friend Requests ({requests.length})</h2>
          {requests.length === 0 ? <p className="text-muted" style={{ fontSize: '0.875rem' }}>No pending requests.</p> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {requests.map(req => (
                <div key={req.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--color-surface-2)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{req.sender.display_name || req.sender.username}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>@{req.sender.username}</div>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button className="btn btn-success btn-sm" onClick={() => handleAccept(req.id)}>✓</button>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDecline(req.id)}>✕</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Friends List */}
        <div className="card">
          <h2 className="heading-sm" style={{ marginBottom: '1.5rem' }}>My Friends ({friends.length})</h2>
          {friends.length === 0 ? <p className="text-muted" style={{ fontSize: '0.875rem' }}>No friends yet. Search for users to add them!</p> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {friends.map(f => (
                <div key={f.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--color-surface-2)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{f.display_name || f.username}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>@{f.username}</div>
                  </div>
                  <button className="btn btn-ghost btn-sm" onClick={() => handleRemove(f.id)} style={{ color: 'var(--color-danger)' }}>Remove</button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
