import React, { useState, useEffect } from 'react';
import {
  listLanguages, getContentFile, updateMeta, addMonth, addBlock,
  deleteBlock, deleteMonth,
  getActivityTypes, createActivity, deleteActivity, updateContent,
  listContent
} from '../../api/admin.js';

const ACTIVITY_ICONS = {
  lesson: '📖', vocabulary: '🔤', vocab: '🔤',
  reading: '📄', writing: '✍', listening: '🎧',
  speaking: '🎙', pronunciation: '🗣', test: '📋',
};
const ACTIVITY_COLORS = {
  lesson: '#6366f1', vocabulary: '#8b5cf6', vocab: '#8b5cf6',
  reading: '#06b6d4', writing: '#10b981', listening: '#f59e0b',
  speaking: '#f97316', pronunciation: '#ec4899', test: '#ef4444',
};

export default function CurriculumBuilder({ onError, onSuccess }) {
  const [pairs, setPairs] = useState([]);
  const [selectedPair, setSelectedPair] = useState('');
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [builderView, setBuilderView] = useState('tree'); // 'tree' | 'files'
  const [allFiles, setAllFiles] = useState([]);
  const [activityTypes, setActivityTypes] = useState(null);

  // For Add Activity Modal
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [targetBlock, setTargetBlock] = useState(null); // { month, block }
  const [activityForm, setActivityForm] = useState({ type: 'lesson', path: '' });

  // For JSON Editor Modal
  const [editingFile, setEditingFile] = useState(null);
  const [fileContentStr, setFileContentStr] = useState('');
  const [savingFile, setSavingFile] = useState(false);

  useEffect(() => {
    Promise.all([listLanguages(), getActivityTypes()])
      .then(([langsRes, typesRes]) => {
        setPairs(langsRes.data);
        setActivityTypes(typesRes.data);
        if (langsRes.data.length > 0) {
          setSelectedPair(prev => prev || langsRes.data[0].pairId);
        } else {
          setLoading(false);
        }
      }).catch(err => {
        // Even if activity-types fails, still load languages
        listLanguages().then(res => {
          setPairs(res.data);
          if (res.data.length > 0) setSelectedPair(prev => prev || res.data[0].pairId);
          else setLoading(false);
        }).catch(onError);
      });
  }, [onError]);

  const loadMeta = async (pairId) => {
    setLoading(true);
    try {
      const res = await getContentFile(pairId, 'meta.json');
      setMeta(res.data);
      const filesRes = await listContent(pairId);
      setAllFiles(filesRes.data.files || []);
    } catch (e) {
      onError(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedPair) loadMeta(selectedPair);
  }, [selectedPair]);

  const handleAddMonth = async () => {
    if (!window.confirm("Add a new month (with 6 empty blocks) to this pair?")) return;
    try {
      await addMonth(selectedPair);
      onSuccess("Month added successfully");
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  const handleEditMonth = async (monthNum, currentTitle) => {
    const newTitle = window.prompt("Enter new title for Month " + monthNum, currentTitle);
    if (newTitle === null || newTitle === currentTitle) return;
    try {
      const newMeta = JSON.parse(JSON.stringify(meta));
      const m = newMeta.months.find(x => x.month === monthNum);
      m.title = newTitle;
      await updateMeta(selectedPair, newMeta);
      onSuccess(`Month ${monthNum} title updated`);
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  const handleEditBlock = async (monthNum, blockNum, currentTitle) => {
    const newTitle = window.prompt(`Enter new title for Block ${blockNum}`, currentTitle);
    if (newTitle === null || newTitle === currentTitle) return;
    try {
      const newMeta = JSON.parse(JSON.stringify(meta));
      const m = newMeta.months.find(x => x.month === monthNum);
      const b = m.blocks.find(x => x.block === blockNum);
      b.title = newTitle;
      await updateMeta(selectedPair, newMeta);
      onSuccess(`Block ${blockNum} title updated`);
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
    if (!window.confirm(`Delete entire Block ${blockNum} in Month ${monthNum}? This deletes ALL activity files inside. Cannot undo!`)) return;
    try {
      await deleteBlock(selectedPair, monthNum, blockNum);
      onSuccess(`Block ${blockNum} in Month ${monthNum} deleted`);
      loadMeta(selectedPair);
    } catch (err) { onError(err); }
  };

  const handleDeleteMonth = async (monthNum, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete entire Month ${monthNum}? This deletes ALL blocks and files inside. Cannot undo!`)) return;
    try {
      await deleteMonth(selectedPair, monthNum);
      onSuccess(`Month ${monthNum} deleted`);
      loadMeta(selectedPair);
    } catch (err) { onError(err); }
  };

  const openAddActivity = (monthNum, blockNum) => {
    setTargetBlock({ month: monthNum, block: blockNum });
    const blockCode = `M${monthNum}B${blockNum}`;
    setActivityForm({ type: 'lesson', path: `month_${monthNum}/block_${blockNum}/${blockCode}_lesson.json` });
    setShowActivityModal(true);
  };

  const submitAddActivity = async (e) => {
    e.preventDefault();
    try {
      const template = activityTypes?.templates?.[activityForm.type] || {};
      try {
        await createActivity(selectedPair, activityForm.path, template);
      } catch (fileErr) {
        const status = fileErr?.response?.status;
        if (status === 409) {
          // File already exists on disk — that's fine, just re-register it in meta.json
          console.warn('File already exists on disk, re-linking in meta.json:', activityForm.path);
        } else {
          throw fileErr; // real error, re-throw
        }
      }
      const newMeta = JSON.parse(JSON.stringify(meta));
      const m = newMeta.months.find(x => x.month === targetBlock.month);
      const b = m.blocks.find(x => x.block === targetBlock.block);
      // Only add if not already present to avoid duplicates
      const alreadyInMeta = b.activities.some(a => a.file === activityForm.path);
      if (!alreadyInMeta) {
        b.activities.push({
          id: (b.activities.reduce((max, a) => Math.max(max, a.id || 0), 0) + 1),
          type: activityForm.type,
          file: activityForm.path,
          xp: activityForm.type === 'test' ? 150 : 50,
        });
      }

      await updateMeta(selectedPair, newMeta);
      onSuccess(`Created activity ${activityForm.path}`);
      setShowActivityModal(false);
      loadMeta(selectedPair);
    } catch (err) { onError(err); }
  };

  const handleDeleteActivity = async (monthNum, blockNum, activity, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete activity ${activity.file}? Cannot undo!`)) return;
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
      if (e instanceof SyntaxError) onError({ message: 'Invalid JSON syntax — check the editor for errors' });
      else onError(e);
    } finally { setSavingFile(false); }
  };

  if (loading && !meta) return <div className="spinner" style={{ margin: '2rem auto' }} />;

  return (
    <div style={{ position: 'relative' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <h2 className="heading-md">Curriculum Builder</h2>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>Language Pair:</label>
          <select className="form-input" style={{ width: 140, padding: '0.4rem 0.8rem' }} value={selectedPair} onChange={e => setSelectedPair(e.target.value)}>
            {pairs.map(p => <option key={p.pairId} value={p.pairId}>{p.pairId}</option>)}
          </select>
        </div>
      </div>

      {!meta ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          No meta.json found. Create a language pair first or manually build it.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className={`btn btn-sm ${builderView === 'tree' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setBuilderView('tree')}>🌳 Visual Tree</button>
              <button className={`btn btn-sm ${builderView === 'files' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setBuilderView('files')}>📂 All Files</button>
            </div>
            {builderView === 'tree' && (
              <button className="btn btn-primary" onClick={handleAddMonth}>+ Add Month</button>
            )}
          </div>

          {builderView === 'tree' && (meta.months || []).map(month => (
            <div key={month.month} className="glass" style={{ padding: '1.5rem', borderRadius: 'var(--radius-xl)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 className="heading-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{ background: 'var(--color-primary-glow)', width: 32, height: 32, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {month.month}
                  </div>
                  {month.title || `Month ${month.month}`}
                  <button className="btn btn-ghost btn-sm" style={{ padding: '0.1rem 0.4rem', fontSize: '1rem', marginLeft: '0.5rem' }} onClick={() => handleEditMonth(month.month, month.title || `Month ${month.month}`)} title="Edit Month Title">✏️</button>
                </h3>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="btn btn-secondary btn-sm" onClick={() => handleAddBlock(month.month)}>+ Add Block</button>
                  <button
                    className="btn btn-sm"
                    style={{ background: 'rgba(239,68,68,0.15)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.4)' }}
                    onClick={(e) => handleDeleteMonth(month.month, e)}
                    title={`Delete Month ${month.month}`}
                  >
                    🗑 Delete Month
                  </button>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {(month.blocks || []).map(block => (
                  <div key={block.block} style={{ background: 'var(--color-surface-2)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                      <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                        Block {block.block}: {block.title || `Block ${block.block}`}
                        <button className="btn btn-ghost" style={{ padding: '0 0.4rem', fontSize: '0.9rem', marginLeft: '0.5rem' }} onClick={() => handleEditBlock(month.month, block.block, block.title || `Block ${block.block}`)} title="Edit Block Title">✏️</button>
                      </span>
                      <div style={{ display: 'flex', gap: '0.4rem' }}>
                        <button
                          className="btn btn-sm"
                          style={{ padding: '0.2rem 0.5rem', background: 'rgba(239,68,68,0.1)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.3)' }}
                          onClick={(e) => handleDeleteBlock(month.month, block.block, e)}
                          title="Delete this block"
                        >
                          🗑
                        </button>
                      </div>
                    </div>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {(block.activities || []).map((act, i) => {
                        const color = ACTIVITY_COLORS[act.type] || '#6366f1';
                        return (
                          <div key={i} className="card-interactive" onClick={() => openJsonEditor(act.file)}
                            style={{
                              display: 'flex', alignItems: 'center', gap: '0.5rem', background: `${color}15`,
                              border: `1px solid ${color}40`, padding: '0.4rem 0.8rem', borderRadius: 'var(--radius-full)',
                              fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text)', cursor: 'pointer'
                            }}>
                            <span>{ACTIVITY_ICONS[act.type]}</span>
                            <span style={{ textTransform: 'capitalize' }}>{act.type}</span>
                            <span className="truncate" style={{ maxWidth: 100, color: 'var(--color-text-muted)', fontWeight: 400 }}>{act.file.split('/').pop()}</span>
                          </div>
                        )
                      })}
                      {(!block.activities || block.activities.length === 0) && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', fontStyle: 'italic', padding: '0.4rem' }}>No activities in this block</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {builderView === 'files' && (
            <div className="card" style={{ padding: '1.5rem', maxHeight: 600, overflowY: 'auto' }}>
              <h3 className="heading-sm" style={{ marginBottom: '1rem' }}>Raw JSON Files</h3>
              <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {allFiles.map(f => (
                  <li key={f.path} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)' }}>
                    <span style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{f.path}</span>
                    <button className="btn btn-ghost btn-sm" onClick={() => openJsonEditor(f.path)}>Edit</button>
                  </li>
                ))}
                {allFiles.length === 0 && <span className="text-muted">No files found.</span>}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Add Activity Modal */}
      {showActivityModal && (
        <div className="modal-overlay">
          <div className="modal-box glass-strong">
            <h3 className="heading-md" style={{ marginBottom: '1rem' }}>Add Activity (M{targetBlock.month}B{targetBlock.block})</h3>
            <form onSubmit={submitAddActivity} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Activity Type</label>
                <select className="form-input" value={activityForm.type} onChange={e => {
                  const type = e.target.value;
                  const blockCode = `M${targetBlock.month}B${targetBlock.block}`;
                  setActivityForm({ ...activityForm, type, path: `month_${targetBlock.month}/block_${targetBlock.block}/${blockCode}_${type}.json` });
                }}>
                  {(activityTypes?.types || ['lesson','pronunciation','reading','writing','listening','vocabulary','speaking','test']).map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">File Path</label>
                <input className="form-input" value={activityForm.path} onChange={e => setActivityForm({ ...activityForm, path: e.target.value })} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-ghost" onClick={() => setShowActivityModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Activity</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* JSON Editor Modal */}
      {editingFile && (
        <div className="modal-overlay">
          <div className="modal-box glass-strong" style={{ maxWidth: 900, height: '90vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div>
                <h3 className="heading-sm">Edit: {editingFile.split('/').pop()}</h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{editingFile}</span>
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => setEditingFile(null)}>✕</button>
            </div>
            <textarea
              className="form-input"
              style={{ flex: 1, fontFamily: 'monospace', fontSize: '0.82rem', color: '#68d391', background: '#0d1117', border: '1px solid #30363d', resize: 'none', lineHeight: 1.6 }}
              value={fileContentStr}
              onChange={e => setFileContentStr(e.target.value)}
              spellCheck={false}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
                {(() => { try { JSON.parse(fileContentStr); return '✅ Valid JSON'; } catch { return '❌ Invalid JSON'; } })()}
              </span>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button className="btn btn-ghost" onClick={() => setEditingFile(null)}>Cancel</button>
                <button className="btn btn-primary" onClick={saveJsonEditor} disabled={savingFile}>{savingFile ? 'Saving...' : 'Save Content'}</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
