import React, { useState, useEffect, useCallback } from 'react';
import {
  listLanguages, getContentFile, updateMeta, addMonth, addBlock,
  deleteBlock, deleteMonth, updateMonth, updateBlock,
  getActivityTypes, createActivity, deleteActivity, updateContent,
  listContent
} from '../../api/admin.js';

const ACTIVITY_ICONS = {
  lesson: '📖', vocabulary: '🔤', vocab: '🔤',
  reading: '📄', writing: '✍️', listening: '🎧',
  speaking: '🎙️', pronunciation: '🗣️', test: '📋',
};
const ACTIVITY_COLORS = {
  lesson: '#6366f1', vocabulary: '#8b5cf6', vocab: '#8b5cf6',
  reading: '#06b6d4', writing: '#10b981', listening: '#f59e0b',
  speaking: '#f97316', pronunciation: '#ec4899', test: '#ef4444',
};

// ── Inline editable label ─────────────────────────────────────────────────────
function InlineEdit({ value, onSave, style = {}, inputStyle = {} }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);

  useEffect(() => { setDraft(value); }, [value]);

  const commit = async () => {
    if (draft.trim() && draft !== value) await onSave(draft.trim());
    setEditing(false);
  };

  if (editing) {
    return (
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
        <input
          autoFocus
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') commit(); if (e.key === 'Escape') setEditing(false); }}
          style={{ fontSize: 'inherit', fontWeight: 'inherit', background: 'var(--color-surface-2)', border: '1px solid var(--color-primary)', borderRadius: '4px', padding: '0.1rem 0.4rem', color: 'var(--color-text)', ...inputStyle }}
        />
        <button onClick={commit} style={{ background: 'var(--color-success)', border: 'none', borderRadius: '4px', color: '#fff', padding: '0.1rem 0.4rem', cursor: 'pointer', fontSize: '0.75rem' }}>✓</button>
        <button onClick={() => setEditing(false)} style={{ background: 'var(--color-surface-2)', border: '1px solid var(--color-border)', borderRadius: '4px', color: 'var(--color-text-muted)', padding: '0.1rem 0.4rem', cursor: 'pointer', fontSize: '0.75rem' }}>✕</button>
      </span>
    );
  }
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', cursor: 'default', ...style }}>
      <span>{value}</span>
      <button onClick={() => setEditing(true)} title="Rename" style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-dim)', fontSize: '0.75rem', padding: '0 2px', lineHeight: 1 }}>✏</button>
    </span>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function CurriculumBuilder({ onError, onSuccess, initialPair = '' }) {
  const [pairs, setPairs] = useState([]);
  const [selectedPair, setSelectedPair] = useState(initialPair);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [builderView, setBuilderView] = useState('tree');
  const [allFiles, setAllFiles] = useState([]);
  const [activityTypes, setActivityTypes] = useState(null);

  // Add Activity modal
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [targetBlock, setTargetBlock] = useState(null);
  const [activityForm, setActivityForm] = useState({ type: 'lesson', path: '' });

  // JSON Editor modal
  const [editingFile, setEditingFile] = useState(null);
  const [fileContentStr, setFileContentStr] = useState('');
  const [savingFile, setSavingFile] = useState(false);

  // Load pairs + activity types on mount
  useEffect(() => {
    Promise.all([listLanguages(), getActivityTypes()])
      .then(([langsRes, typesRes]) => {
        const langs = langsRes.data;
        setPairs(langs);
        setActivityTypes(typesRes.data);
        if (!initialPair && langs.length > 0) setSelectedPair(langs[0].pairId);
        else if (initialPair) setSelectedPair(initialPair);
        else setLoading(false);
      })
      .catch(() => {
        listLanguages().then(res => {
          const langs = res.data;
          setPairs(langs);
          if (!initialPair && langs.length > 0) setSelectedPair(langs[0].pairId);
          else if (initialPair) setSelectedPair(initialPair);
          else setLoading(false);
        }).catch(onError);
      });
  }, [initialPair]);

  // Sync if parent changes initialPair
  useEffect(() => { if (initialPair) setSelectedPair(initialPair); }, [initialPair]);

  const loadMeta = useCallback(async (pairId) => {
    if (!pairId) return;
    setLoading(true);
    try {
      const [metaRes, filesRes] = await Promise.all([
        getContentFile(pairId, 'meta.json'),
        listContent(pairId),
      ]);
      setMeta(metaRes.data);
      setAllFiles(filesRes.data.files || []);
    } catch (e) {
      onError(e);
    } finally {
      setLoading(false);
    }
  }, [onError]);

  useEffect(() => { if (selectedPair) loadMeta(selectedPair); }, [selectedPair]);

  // ── Month / Block handlers ─────────────────────────────────────────────────

  const handleAddMonth = async () => {
    if (!window.confirm('Add a new month (with 6 empty blocks) to this pair?')) return;
    try {
      await addMonth(selectedPair);
      onSuccess('Month added successfully');
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  const handleAddBlock = async (monthNum) => {
    if (!window.confirm(`Add a new block to Month ${monthNum}?`)) return;
    try {
      await addBlock(selectedPair, monthNum);
      onSuccess(`Block added to Month ${monthNum}`);
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  const handleDeleteBlock = async (monthNum, blockNum, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete Block ${blockNum} in Month ${monthNum}? ALL activity files inside will be permanently deleted!`)) return;
    try {
      await deleteBlock(selectedPair, monthNum, blockNum);
      onSuccess(`Block ${blockNum} deleted`);
      loadMeta(selectedPair);
    } catch (err) { onError(err); }
  };

  const handleDeleteMonth = async (monthNum, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete ENTIRE Month ${monthNum}? All ${6 * 8} activity files will be permanently deleted!`)) return;
    try {
      await deleteMonth(selectedPair, monthNum);
      onSuccess(`Month ${monthNum} deleted`);
      loadMeta(selectedPair);
    } catch (err) { onError(err); }
  };

  const handleRenameMonth = async (monthNum, newTitle) => {
    try {
      await updateMonth(selectedPair, monthNum, { title: newTitle });
      onSuccess(`Month ${monthNum} renamed`);
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  const handleRenameBlock = async (monthNum, blockNum, newTitle) => {
    try {
      await updateBlock(selectedPair, monthNum, blockNum, { title: newTitle });
      onSuccess(`Block ${blockNum} renamed`);
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  // ── Activity handlers ──────────────────────────────────────────────────────

  const openAddActivity = (monthNum, blockNum, existingTypes = []) => {
    setTargetBlock({ month: monthNum, block: blockNum, existingTypes });
    const blockCode = `M${monthNum}B${blockNum}`;
    const allTypes = activityTypes?.types || ['lesson', 'pronunciation', 'reading', 'writing', 'listening', 'vocabulary', 'speaking', 'test'];
    const firstAvailable = allTypes.find(t => !existingTypes.includes(t)) || 'lesson';
    setActivityForm({
      type: firstAvailable,
      path: `month_${monthNum}/block_${blockNum}/${blockCode}_${firstAvailable}.json`,
    });
    setShowActivityModal(true);
  };

  const submitAddActivity = async (e) => {
    e.preventDefault();
    try {
      const template = activityTypes?.templates?.[activityForm.type] || {};
      try {
        await createActivity(selectedPair, activityForm.path, template);
      } catch (fileErr) {
        if (fileErr?.response?.status === 409) {
          // File already exists — just re-link in meta.json
          console.warn('Re-linking existing file:', activityForm.path);
        } else {
          throw fileErr;
        }
      }
      const newMeta = JSON.parse(JSON.stringify(meta));
      const m = newMeta.months.find(x => x.month === targetBlock.month);
      const b = m.blocks.find(x => x.block === targetBlock.block);
      const alreadyInMeta = b.activities.some(a => a.file === activityForm.path);
      if (!alreadyInMeta) {
        b.activities.push({
          id: b.activities.reduce((max, a) => Math.max(max, a.id || 0), 0) + 1,
          type: activityForm.type,
          file: activityForm.path,
          xp: activityForm.type === 'test' ? 150 : 50,
        });
      }
      await updateMeta(selectedPair, newMeta);
      onSuccess(`Activity ${activityForm.path} created`);
      setShowActivityModal(false);
      loadMeta(selectedPair);
    } catch (err) { onError(err); }
  };

  const handleDeleteActivity = async (monthNum, blockNum, activity, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete ${activity.file}? Cannot be undone!`)) return;
    try {
      await deleteActivity(selectedPair, activity.file);
      const newMeta = JSON.parse(JSON.stringify(meta));
      const m = newMeta.months.find(x => x.month === monthNum);
      const b = m.blocks.find(x => x.block === blockNum);
      b.activities = b.activities.filter(a => a.file !== activity.file);
      await updateMeta(selectedPair, newMeta);
      onSuccess(`Deleted ${activity.file}`);
      loadMeta(selectedPair);
    } catch (err) { onError(err); }
  };

  // ── JSON Editor ────────────────────────────────────────────────────────────

  const openJsonEditor = async (file) => {
    try {
      const res = await getContentFile(selectedPair, file);
      setEditingFile(file);
      setFileContentStr(JSON.stringify(res.data, null, 2));
    } catch (e) { onError(e); }
  };

  const saveJsonEditor = async () => {
    setSavingFile(true);
    try {
      const parsed = JSON.parse(fileContentStr);
      await updateContent(selectedPair, editingFile, parsed);
      onSuccess(`Saved ${editingFile}`);
      setEditingFile(null);
    } catch (e) {
      if (e instanceof SyntaxError) onError({ message: 'Invalid JSON — fix syntax errors before saving' });
      else onError(e);
    } finally { setSavingFile(false); }
  };

  // ── Render helpers ─────────────────────────────────────────────────────────

  const isValidJson = () => {
    try { JSON.parse(fileContentStr); return true; } catch { return false; }
  };

  if (loading && !meta) return <div className="spinner" style={{ margin: '2rem auto' }} />;

  const allActivityTypes = activityTypes?.types || ['lesson', 'pronunciation', 'reading', 'writing', 'listening', 'vocabulary', 'speaking', 'test'];

  return (
    <div style={{ position: 'relative' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <h2 className="heading-md">Curriculum Builder</h2>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>Language Pair:</label>
          <select
            className="form-input"
            style={{ width: 160, padding: '0.4rem 0.8rem' }}
            value={selectedPair}
            onChange={e => setSelectedPair(e.target.value)}
          >
            {pairs.map(p => (
              <option key={p.pairId} value={p.pairId}>
                {p.meta?.source?.flag || ''} {p.meta?.source?.name || p.pairId.split('-')[0]} → {p.meta?.target?.flag || ''} {p.meta?.target?.name || p.pairId.split('-')[1]}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!meta ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-muted)' }}>
          No curriculum found for this pair.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* View Toggle + Add Month */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className={`btn btn-sm ${builderView === 'tree' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setBuilderView('tree')}>🌳 Visual Tree</button>
              <button className={`btn btn-sm ${builderView === 'files' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setBuilderView('files')}>📂 All Files</button>
            </div>
            {builderView === 'tree' && (
              <button className="btn btn-primary" onClick={handleAddMonth}>+ Add Month</button>
            )}
          </div>

          {/* Tree View */}
          {builderView === 'tree' && (meta.months || []).map(month => (
            <div key={month.month} className="glass" style={{ padding: '1.5rem', borderRadius: 'var(--radius-xl)' }}>
              {/* Month header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 className="heading-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <div style={{ background: 'var(--color-primary-glow)', width: 32, height: 32, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, flexShrink: 0 }}>
                    {month.month}
                  </div>
                  <InlineEdit
                    value={month.title || `Month ${month.month}`}
                    onSave={newTitle => handleRenameMonth(month.month, newTitle)}
                    style={{ fontWeight: 700 }}
                  />
                  <span style={{ fontSize: '0.7rem', color: 'var(--color-text-dim)', fontWeight: 400 }}>{month.targetLevel}</span>
                </h3>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="btn btn-secondary btn-sm" onClick={() => handleAddBlock(month.month)}>+ Block</button>
                  <button
                    className="btn btn-sm"
                    style={{ background: 'rgba(239,68,68,0.15)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.4)', fontSize: '0.78rem' }}
                    onClick={e => handleDeleteMonth(month.month, e)}
                  >🗑 Month</button>
                </div>
              </div>

              {/* Blocks */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {(month.blocks || []).map(block => {
                  const existingTypes = (block.activities || []).map(a => a.type);
                  return (
                    <div key={block.block} style={{ background: 'var(--color-surface-2)', padding: '0.875rem 1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                      {/* Block header */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <code style={{ fontSize: '0.7rem', opacity: 0.6 }}>{block.blockCode}</code>
                          <InlineEdit
                            value={block.title || `Block ${block.block}`}
                            onSave={newTitle => handleRenameBlock(month.month, block.block, newTitle)}
                          />
                        </span>
                        <div style={{ display: 'flex', gap: '0.35rem' }}>
                          <button
                            className="btn btn-ghost btn-sm"
                            style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                            onClick={() => openAddActivity(month.month, block.block, existingTypes)}
                          >+ Activity</button>
                          <button
                            className="btn btn-sm"
                            style={{ padding: '0.2rem 0.5rem', background: 'rgba(239,68,68,0.1)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.3)', fontSize: '0.75rem' }}
                            onClick={e => handleDeleteBlock(month.month, block.block, e)}
                          >🗑</button>
                        </div>
                      </div>

                      {/* Activity pills */}
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                        {(block.activities || []).map((act, i) => {
                          const color = ACTIVITY_COLORS[act.type] || '#6366f1';
                          return (
                            <div key={i}
                              onClick={() => openJsonEditor(act.file)}
                              style={{
                                display: 'flex', alignItems: 'center', gap: '0.35rem',
                                background: `${color}18`, border: `1px solid ${color}45`,
                                padding: '0.35rem 0.7rem', borderRadius: 'var(--radius-full)',
                                fontSize: '0.72rem', fontWeight: 600, cursor: 'pointer',
                                color: 'var(--color-text)', transition: 'all 0.15s',
                              }}
                              title={`Edit ${act.file}`}
                            >
                              <span>{ACTIVITY_ICONS[act.type] || '📄'}</span>
                              <span style={{ textTransform: 'capitalize' }}>{act.type}</span>
                              <span style={{ color: 'var(--color-text-dim)', fontWeight: 400, maxWidth: 80, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                {act.file.split('/').pop()}
                              </span>
                              <span
                                style={{ color: '#ef4444', marginLeft: '0.1rem' }}
                                onClick={e => handleDeleteActivity(month.month, block.block, act, e)}
                                title="Delete activity"
                              >✕</span>
                            </div>
                          );
                        })}
                        {existingTypes.length === 0 && (
                          <span style={{ fontSize: '0.72rem', color: 'var(--color-text-dim)', fontStyle: 'italic', padding: '0.3rem 0' }}>No activities — click + Activity to add</span>
                        )}
                      </div>

                      {/* Missing types hint */}
                      {existingTypes.length > 0 && existingTypes.length < 8 && (
                        <div style={{ marginTop: '0.5rem', fontSize: '0.68rem', color: 'var(--color-text-dim)' }}>
                          Missing: {allActivityTypes.filter(t => !existingTypes.includes(t)).join(', ')}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          {/* Files View */}
          {builderView === 'files' && (
            <div className="card" style={{ padding: '1.5rem', maxHeight: 600, overflowY: 'auto' }}>
              <h3 className="heading-sm" style={{ marginBottom: '1rem' }}>Raw JSON Files ({allFiles.length})</h3>
              <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {allFiles.map(f => (
                  <li key={f.path} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.6rem 0.875rem', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)' }}>
                    <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{f.path}</span>
                    <span style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--color-text-dim)' }}>{(f.size_bytes / 1024).toFixed(1)} KB</span>
                      <button className="btn btn-ghost btn-sm" style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }} onClick={() => openJsonEditor(f.path)}>Edit</button>
                    </span>
                  </li>
                ))}
                {allFiles.length === 0 && <span className="text-muted">No activity files found.</span>}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* ── Add Activity Modal ─────────────────────────────────────────────── */}
      {showActivityModal && targetBlock && (
        <div className="modal-overlay">
          <div className="modal-box glass-strong" style={{ maxWidth: 480 }}>
            <h3 className="heading-md" style={{ marginBottom: '1rem' }}>
              Add Activity — <code style={{ fontSize: '0.9rem' }}>M{targetBlock.month}B{targetBlock.block}</code>
            </h3>
            <form onSubmit={submitAddActivity} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Activity Type</label>
                <select
                  className="form-input"
                  value={activityForm.type}
                  onChange={e => {
                    const type = e.target.value;
                    const blockCode = `M${targetBlock.month}B${targetBlock.block}`;
                    setActivityForm({ type, path: `month_${targetBlock.month}/block_${targetBlock.block}/${blockCode}_${type}.json` });
                  }}
                >
                  {allActivityTypes.map(t => (
                    <option key={t} value={t} disabled={targetBlock.existingTypes?.includes(t)}>
                      {ACTIVITY_ICONS[t] || '📄'} {t} {targetBlock.existingTypes?.includes(t) ? '(already exists)' : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">File Path (auto-generated)</label>
                <input
                  className="form-input"
                  style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}
                  value={activityForm.path}
                  onChange={e => setActivityForm({ ...activityForm, path: e.target.value })}
                  required
                />
                <span style={{ fontSize: '0.72rem', color: 'var(--color-text-dim)', marginTop: '0.25rem', display: 'block' }}>
                  Edit only if you need a custom filename.
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn btn-ghost" onClick={() => setShowActivityModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Activity</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── JSON Editor Modal ──────────────────────────────────────────────── */}
      {editingFile && (
        <div className="modal-overlay">
          <div className="modal-box glass-strong" style={{ maxWidth: 960, height: '90vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
              <div>
                <h3 className="heading-sm">{editingFile.split('/').pop()}</h3>
                <code style={{ fontSize: '0.72rem', color: 'var(--color-text-dim)' }}>{editingFile}</code>
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => setEditingFile(null)}>✕</button>
            </div>
            <textarea
              className="form-input"
              style={{
                flex: 1, fontFamily: '"Fira Code", "Cascadia Code", monospace', fontSize: '0.82rem',
                color: '#86efac', background: '#0d1117', border: '1px solid #30363d',
                resize: 'none', lineHeight: 1.65,
              }}
              value={fileContentStr}
              onChange={e => setFileContentStr(e.target.value)}
              spellCheck={false}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.875rem' }}>
              <span style={{
                fontSize: '0.78rem', fontWeight: 600, padding: '0.25rem 0.625rem', borderRadius: '4px',
                background: isValidJson() ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                color: isValidJson() ? '#10b981' : '#ef4444',
              }}>
                {isValidJson() ? '✅ Valid JSON' : '❌ Invalid JSON'}
              </span>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button className="btn btn-ghost" onClick={() => setEditingFile(null)}>Cancel</button>
                <button className="btn btn-primary" onClick={saveJsonEditor} disabled={savingFile || !isValidJson()}>
                  {savingFile ? 'Saving…' : 'Save Content'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
