/**
 * src/pages/admin/AdminDashboard.jsx
 * Fully rebuilt Admin Dashboard with 5 tabs: Overview, Users, Languages, Content, and Templates.
 * Includes proper error handling, loading states, and full CRUD via the admin API.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logout } from '../../store/authSlice.js';
import {
  getAdminStats, getAdminAnalytics, getActivityTypes,
  listAdminUsers, updateUserRole, deactivateUser, activateUser,
  listLanguages, createLanguage, deleteLanguage,
} from '../../api/admin.js';
import CurriculumBuilder from '../../components/admin/CurriculumBuilder.jsx';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user } = useSelector(s => s.auth);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // Protect route
  useEffect(() => {
    if (user && user.role !== 'admin') {
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);

  const showMessage = (msg) => {
    setMessage(msg);
    setTimeout(() => setMessage(''), 4000);
  };
  const handleError = (err) => {
    setError(err.response?.data?.detail || err.message || 'An error occurred');
    setTimeout(() => setError(''), 5000);
  };

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login', { replace: true });
  };

  return (
    <div style={{ padding: '2rem', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 className="heading-lg" style={{ color: 'var(--color-danger-light)' }}>🛡 Admin Portal</h1>
          <p className="text-muted">Manage users, content, and system configuration</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-ghost" onClick={() => navigate('/dashboard')}>← Exit Admin</button>
          <button className="btn btn-sm" style={{ background: 'rgba(239,68,68,0.15)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.4)' }} onClick={handleLogout}>🚪 Logout</button>
        </div>
      </div>

      {/* Toasts */}
      {error && <div style={{ background: 'var(--color-danger)', color: 'white', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>⚠ {error}</div>}
      {message && <div style={{ background: 'var(--color-success)', color: 'white', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>✅ {message}</div>}

      {/* Tabs Navigation */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '1rem', overflowX: 'auto' }}>
        {['overview', 'users', 'languages', 'curriculum'].map(tab => (
          <button key={tab}
            className={`btn ${activeTab === tab ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab(tab)}
            style={{ textTransform: 'capitalize', whiteSpace: 'nowrap' }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="animate-fade-in">
        {activeTab === 'overview' && <OverviewTab onError={handleError} />}
        {activeTab === 'users' && <UsersTab onError={handleError} onSuccess={showMessage} />}
        {activeTab === 'languages' && <LanguagesTab onError={handleError} onSuccess={showMessage} />}
        {activeTab === 'curriculum' && <CurriculumBuilder onError={handleError} onSuccess={showMessage} />}
      </div>
    </div>
  );
}

// ── TAB COMPONENTS ──────────────────────────────────────────────────────────

function OverviewTab({ onError }) {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getAdminStats(), getAdminAnalytics()])
      .then(([sRes, aRes]) => { setStats(sRes.data); setAnalytics(aRes.data); })
      .catch(onError).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner" />;
  if (!stats || !analytics) return null;

  return (
    <div>
      <h2 className="heading-md" style={{ marginBottom: '1rem' }}>Platform Statistics</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <StatCard title="Total Users" value={stats.total_users} />
        <StatCard title="Active Today" value={stats.active_today} />
        <StatCard title="Total XP Awarded" value={stats.total_xp_awarded} />
        <StatCard title="Total Completions" value={stats.total_completions} />
      </div>

      <h2 className="heading-md" style={{ marginBottom: '1rem' }}>Activity Performance</h2>
      <div className="card" style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
              <th style={{ padding: '0.5rem' }}>Type</th>
              <th style={{ padding: '0.5rem' }}>Completions</th>
              <th style={{ padding: '0.5rem' }}>Avg Score</th>
              <th style={{ padding: '0.5rem' }}>Pass Rate</th>
            </tr>
          </thead>
          <tbody>
            {analytics.activity_stats.map(a => (
              <tr key={a.activity_type} style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '0.5rem', textTransform: 'capitalize' }}>{a.activity_type}</td>
                <td style={{ padding: '0.5rem' }}>{a.total_completions}</td>
                <td style={{ padding: '0.5rem' }}>{a.avg_score} XP</td>
                <td style={{ padding: '0.5rem' }}>{a.pass_rate}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function UsersTab({ onError, onSuccess }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = () => {
    setLoading(true);
    listAdminUsers().then(r => setUsers(r.data)).catch(onError).finally(() => setLoading(false));
  };
  useEffect(() => { fetchUsers(); }, []);

  const handleToggleStatus = async (u) => {
    try {
      if (u.is_active) await deactivateUser(u.id);
      else await activateUser(u.id);
      onSuccess(`Status updated for ${u.username}`);
      fetchUsers();
    } catch (e) { onError(e); }
  };

  if (loading) return <div className="spinner" />;

  return (
    <div className="card" style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
            <th style={{ padding: '0.75rem' }}>Username</th>
            <th style={{ padding: '0.75rem' }}>Email</th>
            <th style={{ padding: '0.75rem' }}>Role</th>
            <th style={{ padding: '0.75rem' }}>Status</th>
            <th style={{ padding: '0.75rem' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(u => (
            <tr key={u.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
              <td style={{ padding: '0.75rem' }}>{u.username}</td>
              <td style={{ padding: '0.75rem' }}>{u.email}</td>
              <td style={{ padding: '0.75rem' }}>
                <span className={`badge ${u.role === 'admin' ? 'badge-danger' : 'badge-primary'}`}>{u.role}</span>
              </td>
              <td style={{ padding: '0.75rem' }}>
                <span style={{ color: u.is_active ? 'var(--color-success)' : 'var(--color-danger)' }}>
                  {u.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td style={{ padding: '0.75rem', display: 'flex', gap: '0.5rem' }}>
                <button className={`btn btn-sm ${u.is_active ? 'btn-danger' : 'btn-primary'}`} onClick={() => handleToggleStatus(u)}>
                  {u.is_active ? 'Deactivate' : 'Activate'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function LanguagesTab({ onError, onSuccess }) {
  const [pairs, setPairs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ source_lang_id: 'hi', source_lang_name: 'Hindi', source_lang_flag: '🇮🇳', target_lang_id: 'en', target_lang_name: 'English', target_lang_flag: '🇺🇸' });

  const fetchPairs = () => {
    setLoading(true);
    listLanguages().then(r => setPairs(r.data)).catch(onError).finally(() => setLoading(false));
  };
  useEffect(() => { fetchPairs(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createLanguage(form);
      onSuccess('Language pair created!');
      fetchPairs();
    } catch (err) { onError(err); }
  };

  const handleDelete = async (pairId) => {
    if (!window.confirm(`Delete ${pairId}? This cannot be undone.`)) return;
    try {
      await deleteLanguage(pairId);
      onSuccess('Language pair deleted');
      fetchPairs();
    } catch (err) { onError(err); }
  };

  if (loading) return <div className="spinner" />;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
      <div className="card">
        <h2 className="heading-md" style={{ marginBottom: '1rem' }}>Active Language Pairs</h2>
        {pairs.length === 0 ? <p>No language pairs found.</p> : (
          <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {pairs.map(p => (
              <li key={p.pairId} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--color-surface-2)', padding: '1rem', borderRadius: '8px' }}>
                <div>
                  <strong>{p.pairId}</strong> <br/>
                  <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                    {p.meta?.source?.name} → {p.meta?.target?.name}
                  </span>
                </div>
                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(p.pairId)}>Delete</button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="card">
        <h2 className="heading-md" style={{ marginBottom: '1rem' }}>Create New Pair</h2>
        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Source ID (e.g. hi)</label>
              <input className="form-input" value={form.source_lang_id} onChange={e => setForm(f => ({ ...f, source_lang_id: e.target.value }))} required />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Target ID (e.g. en)</label>
              <input className="form-input" value={form.target_lang_id} onChange={e => setForm(f => ({ ...f, target_lang_id: e.target.value }))} required />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Source Name (e.g. Hindi)</label>
              <input className="form-input" value={form.source_lang_name} onChange={e => setForm(f => ({ ...f, source_lang_name: e.target.value }))} required />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Target Name (e.g. English)</label>
              <input className="form-input" value={form.target_lang_name} onChange={e => setForm(f => ({ ...f, target_lang_name: e.target.value }))} required />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Source Flag (emoji)</label>
              <input className="form-input" value={form.source_lang_flag} onChange={e => setForm(f => ({ ...f, source_lang_flag: e.target.value }))} required />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Target Flag (emoji)</label>
              <input className="form-input" value={form.target_lang_flag} onChange={e => setForm(f => ({ ...f, target_lang_flag: e.target.value }))} required />
            </div>
          </div>
          <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }}>Create Language Pair</button>
        </form>
      </div>
    </div>
  );
}



function StatCard({ title, value }) {
  return (
    <div style={{ background: 'var(--color-surface-2)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--color-border)', textAlign: 'center' }}>
      <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{title}</div>
      <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-primary-light)' }}>{value}</div>
    </div>
  );
}
