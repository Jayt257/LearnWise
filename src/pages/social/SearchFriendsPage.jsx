/**
 * src/pages/social/SearchFriendsPage.jsx
 * Search users to send friend requests.
 */
import React, { useState } from 'react';
import { searchUsers, sendFriendRequest } from '../../api/users.js';

export default function SearchFriendsPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(new Set());

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);
    try {
      const { data } = await searchUsers(query);
      setResults(data.users);
    } catch (e) {
      console.error(e);
    } finally { setLoading(false); }
  };

  const handleSendRequest = async (userId) => {
    try {
      await sendFriendRequest(userId);
      setSent(new Set([...sent, userId]));
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to send request');
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 className="heading-lg" style={{ marginBottom: '0.5rem' }}>🔍 Find Friends</h1>
        <p className="text-muted">Search by username to add friends to your leaderboard.</p>
      </div>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem' }}>
          <input className="form-input" style={{ flex: 1 }} placeholder="Search by username..." value={query} onChange={e => setQuery(e.target.value)} />
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Search'}
          </button>
        </form>
      </div>

      {results.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.25rem' }}>
          {results.map(u => (
            <div key={u.id} className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--color-primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>
                  {u.display_name?.[0]?.toUpperCase() || u.username[0].toUpperCase()}
                </div>
                <div>
                  <div style={{ fontWeight: 600 }}>{u.display_name || u.username}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>@{u.username}</div>
                </div>
              </div>
              <button className="btn btn-secondary btn-sm" onClick={() => handleSendRequest(u.id)} disabled={sent.has(u.id)}>
                {sent.has(u.id) ? 'Sent' : '+ Add'}
              </button>
            </div>
          ))}
        </div>
      )}
      {!loading && query && results.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-muted)' }}>No users found.</div>
      )}
    </div>
  );
}
