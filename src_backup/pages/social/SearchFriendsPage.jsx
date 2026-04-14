/
  src/pages/social/SearchFriendsPage.jsx
  Premium redesign — styled search bar, user cards with glow button.
  All API logic is untouched.
 /
import React, { useState } from 'react';
import { searchUsers, sendFriendRequest } from '../../api/users.js';

export default function SearchFriendsPage() {
  const [query,   setQuery]   = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sent,    setSent]    = useState(new Set());

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);
    try {
      const { data } = await searchUsers(query);
      setResults(data.users);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
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
    <div style={{ maxWidth: , margin: ' auto' }} className="animate-fade-up">
      {/ Header /}
      <div style={{ textAlign: 'center', marginBottom: '.rem' }}>
        <div style={{ fontSize: 'rem', marginBottom: '.rem' }}></div>
        <h className="heading-lg" style={{ marginBottom: '.rem' }}>Find Friends</h>
        <p className="text-muted" style={{ fontSize: '.rem' }}>
          Search by username to add friends to your leaderboard
        </p>
      </div>

      {/ Search bar /}
      <div className="card" style={{ marginBottom: 'rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '.rem' }}>
          <div style={{ flex: , position: 'relative' }}>
            <span style={{
              position: 'absolute', left: 'rem', top: '%', transform: 'translateY(-%)',
              fontSize: 'rem', color: 'var(--text-dim)', pointerEvents: 'none',
            }}>
              
            </span>
            <input
              className="form-input"
              style={{ paddingLeft: '.rem' }}
              placeholder="Search by username..."
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading} style={{ flexShrink:  }}>
            {loading ? <span className="spinner" /> : 'Search'}
          </button>
        </form>
      </div>

      {/ Results /}
      {results.length >  && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(px, fr))', gap: 'rem' }}>
          {results.map((u, i) => {
            const initial  = (u.display_name?.[] || u.username[]).toUpperCase();
            const isSent   = sent.has(u.id);
            return (
              <div
                key={u.id}
                className="card card-interactive animate-fade-up"
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  gap: 'rem',
                  animationDelay: `${i  .}s`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 'rem' }}>
                  <div style={{
                    width: , height: , borderRadius: '%',
                    background: 'linear-gradient(deg, var(--primary), var(--cyan))',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: 'var(--font-display)', fontWeight: , color: 'white',
                    fontSize: '.rem', flexShrink: ,
                    boxShadow: '  px var(--primary-glow)',
                  }}>
                    {initial}
                  </div>
                  <div>
                    <div style={{ fontWeight: , fontSize: '.rem' }}>
                      {u.display_name || u.username}
                    </div>
                    <div style={{ fontSize: '.rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                      @{u.username}
                    </div>
                  </div>
                </div>

                <button
                  className={`btn btn-sm ${isSent ? 'btn-ghost' : 'btn-secondary'}`}
                  onClick={() => !isSent && handleSendRequest(u.id)}
                  disabled={isSent}
                  style={{ flexShrink:  }}
                >
                  {isSent ? '✓ Sent' : '+ Add'}
                </button>
              </div>
            );
          })}
        </div>
      )}

      {!loading && query && results.length ===  && (
        <div style={{ textAlign: 'center', padding: 'rem', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '.rem', marginBottom: '.rem' }}></div>
          <p>No users found for "<strong>{query}</strong>"</p>
        </div>
      )}

      {/ Empty state (no search yet) /}
      {!query && results.length ===  && (
        <div style={{ textAlign: 'center', padding: 'rem', color: 'var(--text-dim)' }}>
          <div style={{ fontSize: 'rem', marginBottom: '.rem', opacity: . }}></div>
          <p style={{ fontSize: '.rem' }}>Start typing to search for friends</p>
        </div>
      )}
    </div>
  );
}
