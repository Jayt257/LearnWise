import React, { useState, useEffect, useRef } from 'react';
import {
  listLanguages, getContentFile, updateMeta, addMonth, addBlock,
  deleteBlock, deleteMonth,
  getActivityTypes, updateContent,
  listContent
} from '../../api/admin.js';

const ACTIVITY_ICONS = {
  lesson: '', vocabulary: '', vocab: '',
  reading: '', writing: '', listening: '',
  speaking: '', pronunciation: '', test: '',
};
const ACTIVITY_COLORS = {
  lesson: 'f', vocabulary: 'bcf', vocab: 'bcf',
  reading: 'bd', writing: 'b', listening: 'feb',
  speaking: 'f', pronunciation: 'ec', test: 'ef',
};

export default function CurriculumBuilder({ onError, onSuccess }) {
  const [pairs, setPairs] = useState([]);
  const [selectedPair, setSelectedPair] = useState('');
  // Bug  fix: keep a ref so loadMeta can restore selectedPair even after pair-list reload
  const selectedPairRef = useRef('');
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [builderView, setBuilderView] = useState('tree'); // 'tree' | 'files'
  const [allFiles, setAllFiles] = useState([]);

  // For JSON Editor Modal
  const [editingFile, setEditingFile] = useState(null);
  const [fileContentStr, setFileContentStr] = useState('');
  const [savingFile, setSavingFile] = useState(false);

  // Update ref when selectedPair changes
  useEffect(() => { selectedPairRef.current = selectedPair; }, [selectedPair]);

  // Load pairs once on mount; don't override user's current selection
  useEffect(() => {
    Promise.all([listLanguages(), getActivityTypes()])
      .then(([langsRes]) => {
        const langList = langsRes.data;
        setPairs(langList);
        // Only set default if nothing is selected yet
        if (!selectedPairRef.current && langList.length > ) {
          setSelectedPair(langList[].pairId);
        } else {
          setLoading(false);
        }
      })
      .catch(() => {
        listLanguages()
          .then(res => {
            const langList = res.data;
            setPairs(langList);
            if (!selectedPairRef.current && langList.length > ) {
              setSelectedPair(langList[].pairId);
            } else {
              setLoading(false);
            }
          })
          .catch(onError);
      });
  }, []); // run once

  const loadMeta = async (pairId) => {
    if (!pairId) return;
    setLoading(true);
    try {
      const [metaRes, filesRes, langsRes] = await Promise.all([
        getContentFile(pairId, 'meta.json'),
        listContent(pairId),
        listLanguages(),
      ]);
      setMeta(metaRes.data);
      setAllFiles(filesRes.data.files || []);
      // Refresh pair list but KEEP current selection (Bug  fix)
      setPairs(langsRes.data);
    } catch (e) {
      onError(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedPair) loadMeta(selectedPair);
  }, [selectedPair]);

  // ── Month / Block actions ──────────────────────────────────────
  const handleAddMonth = async () => {
    if (!window.confirm('Add a new month (with  blocks + default activities) to this pair?')) return;
    try {
      await addMonth(selectedPair);
      onSuccess('Month added successfully');
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  const handleEditMonth = async (monthNum, currentTitle) => {
    const newTitle = window.prompt(`Rename Month ${monthNum}`, currentTitle);
    if (!newTitle || newTitle === currentTitle) return;
    try {
      const newMeta = JSON.parse(JSON.stringify(meta));
      const m = newMeta.months.find(x => x.month === monthNum);
      m.title = newTitle;
      await updateMeta(selectedPair, newMeta);
      onSuccess(`Month ${monthNum} renamed`);
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  const handleAddBlock = async (monthNum) => {
    if (!window.confirm(`Add a new block (with default activities) to Month ${monthNum}?`)) return;
    try {
      await addBlock(selectedPair, monthNum);
      onSuccess(`Block added to Month ${monthNum}`);
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  const handleEditBlock = async (monthNum, blockNum, currentTitle) => {
    const newTitle = window.prompt(`Rename Block ${blockNum}`, currentTitle);
    if (!newTitle || newTitle === currentTitle) return;
    try {
      const newMeta = JSON.parse(JSON.stringify(meta));
      const m = newMeta.months.find(x => x.month === monthNum);
      const b = m.blocks.find(x => x.block === blockNum);
      b.title = newTitle;
      await updateMeta(selectedPair, newMeta);
      onSuccess(`Block ${blockNum} renamed`);
      loadMeta(selectedPair);
    } catch (e) { onError(e); }
  };

  const handleDeleteBlock = async (monthNum, blockNum, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete Block ${blockNum} in Month ${monthNum}? ALL files inside will be deleted. Cannot undo!`)) return;
    try {
      await deleteBlock(selectedPair, monthNum, blockNum);
      onSuccess(`Block ${blockNum} deleted`);
      loadMeta(selectedPair);
    } catch (err) { onError(err); }
  };

  const handleDeleteMonth = async (monthNum, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete Month ${monthNum}? ALL blocks and files inside will be deleted. Cannot undo!`)) return;
    try {
      await deleteMonth(selectedPair, monthNum);
      onSuccess(`Month ${monthNum} deleted`);
      loadMeta(selectedPair);
    } catch (err) { onError(err); }
  };

  // ── JSON Editor ───────────────────────────────────────────────
  const openJsonEditor = async (file) => {
    try {
      const res = await getContentFile(selectedPair, file);
      setEditingFile(file);
      setFileContentStr(JSON.stringify(res.data, null, ));
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
      if (e instanceof SyntaxError) onError({ message: 'Invalid JSON — check the editor for errors' });
      else onError(e);
    } finally { setSavingFile(false); }
  };

  if (loading && !meta) return <div className="spinner" style={{ margin: 'rem auto' }} />;

  return (
    <div style={{ position: 'relative' }}>
      {/ Header /}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '.rem' }}>
        <h className="heading-md">Curriculum Builder</h>
        <div style={{ display: 'flex', gap: 'rem', alignItems: 'center' }}>
          <label style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}>Language Pair:</label>
          <select
            className="form-input"
            style={{ width: , padding: '.rem .rem' }}
            value={selectedPair}
            onChange={e => setSelectedPair(e.target.value)}
          >
            {pairs.map(p => (
              <option key={p.pairId} value={p.pairId}>{p.pairId}</option>
            ))}
          </select>
        </div>
      </div>

      {!meta ? (
        <div className="card" style={{ textAlign: 'center', padding: 'rem' }}>
          No meta.json found. Create a language pair first.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'rem' }}>

          {/ View toggle + Add Month /}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '.rem' }}>
              <button className={`btn btn-sm ${builderView === 'tree' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setBuilderView('tree')}> Visual Tree</button>
              <button className={`btn btn-sm ${builderView === 'files' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setBuilderView('files')}> All Files</button>
            </div>
            {builderView === 'tree' && (
              <button className="btn btn-primary" onClick={handleAddMonth}>+ Add Month</button>
            )}
          </div>

          {/ Tree View /}
          {builderView === 'tree' && (meta.months || []).map(month => (
            <div key={month.month} className="glass" style={{ padding: '.rem', borderRadius: 'var(--radius-xl)' }}>
              {/ Month header /}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'rem' }}>
                <h className="heading-sm" style={{ display: 'flex', alignItems: 'center', gap: '.rem' }}>
                  <div style={{ background: 'var(--color-primary-glow)', width: , height: , borderRadius: '%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight:  }}>
                    {month.month}
                  </div>
                  {month.title || `Month ${month.month}`}
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ padding: '.rem .rem', fontSize: 'rem' }}
                    onClick={() => handleEditMonth(month.month, month.title || `Month ${month.month}`)}
                    title="Rename month"
                  ></button>
                </h>
                <div style={{ display: 'flex', gap: '.rem' }}>
                  <button className="btn btn-secondary btn-sm" onClick={() => handleAddBlock(month.month)}>+ Add Block</button>
                  <button
                    className="btn btn-sm"
                    style={{ background: 'rgba(,,,.)', color: 'ef', border: 'px solid rgba(,,,.)' }}
                    onClick={(e) => handleDeleteMonth(month.month, e)}
                    title="Delete month"
                  > Delete Month</button>
                </div>
              </div>

              {/ Blocks /}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'rem' }}>
                {(month.blocks || []).map(block => (
                  <div key={block.block} style={{ background: 'var(--color-surface-)', padding: 'rem', borderRadius: 'var(--radius-md)', border: 'px solid var(--color-border)' }}>
                    {/ Block header /}
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '.rem', fontSize: '.rem', color: 'var(--color-text-muted)' }}>
                      <span style={{ fontWeight: , display: 'flex', alignItems: 'center', gap: '.rem' }}>
                        Block {block.block}: {block.title || `Block ${block.block}`}
                        <button
                          className="btn btn-ghost"
                          style={{ padding: ' .rem', fontSize: '.rem' }}
                          onClick={() => handleEditBlock(month.month, block.block, block.title || `Block ${block.block}`)}
                          title="Rename block"
                        ></button>
                      </span>
                      <button
                        className="btn btn-sm"
                        style={{ padding: '.rem .rem', background: 'rgba(,,,.)', color: 'ef', border: 'px solid rgba(,,,.)' }}
                        onClick={(e) => handleDeleteBlock(month.month, block.block, e)}
                        title="Delete block"
                      ></button>
                    </div>

                    {/ Activity pills — EDIT only (Bug : no add/delete per activity) /}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '.rem' }}>
                      {(block.activities || []).map((act, i) => {
                        const color = ACTIVITY_COLORS[act.type] || 'f';
                        return (
                          <div
                            key={i}
                            className="card-interactive"
                            onClick={() => openJsonEditor(act.file)}
                            title={`Edit ${act.file}`}
                            style={{
                              display: 'flex', alignItems: 'center', gap: '.rem',
                              background: `${color}`, border: `px solid ${color}`,
                              padding: '.rem .rem', borderRadius: 'var(--radius-full)',
                              fontSize: '.rem', fontWeight: , color: 'var(--color-text)', cursor: 'pointer',
                              transition: 'all .s'
                            }}
                          >
                            <span>{ACTIVITY_ICONS[act.type]}</span>
                            <span style={{ textTransform: 'capitalize' }}>{act.type}</span>
                            <span style={{ maxWidth: , overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--color-text-muted)', fontWeight:  }}>
                              {act.file.split('/').pop()}
                            </span>
                            <span style={{ opacity: ., fontSize: '.rem' }}></span>
                          </div>
                        );
                      })}
                      {(!block.activities || block.activities.length === ) && (
                        <div style={{ fontSize: '.rem', color: 'var(--color-text-dim)', fontStyle: 'italic', padding: '.rem' }}>
                          No activities in this block
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/ Files View /}
          {builderView === 'files' && (
            <div className="card" style={{ padding: '.rem', maxHeight: , overflowY: 'auto' }}>
              <h className="heading-sm" style={{ marginBottom: 'rem' }}>Raw JSON Files ({allFiles.length})</h>
              <ul style={{ listStyle: 'none', padding: , display: 'flex', flexDirection: 'column', gap: '.rem' }}>
                {allFiles.map(f => (
                  <li key={f.path} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '.rem', background: 'var(--color-surface-)', borderRadius: 'var(--radius-sm)', border: 'px solid var(--color-border)' }}>
                    <span style={{ fontFamily: 'monospace', fontSize: '.rem' }}>{f.path}</span>
                    <button className="btn btn-ghost btn-sm" onClick={() => openJsonEditor(f.path)}> Edit</button>
                  </li>
                ))}
                {allFiles.length ===  && <span className="text-muted">No files found.</span>}
              </ul>
            </div>
          )}
        </div>
      )}

      {/ JSON Editor Modal /}
      {editingFile && (
        <div className="modal-overlay">
          <div className="modal-box glass-strong" style={{ maxWidth: , height: 'vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'rem' }}>
              <div>
                <h className="heading-sm"> Edit: {editingFile.split('/').pop()}</h>
                <span style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}>{selectedPair} / {editingFile}</span>
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => setEditingFile(null)}>✕</button>
            </div>
            <textarea
              className="form-input"
              style={{ flex: , fontFamily: 'monospace', fontSize: '.rem', color: 'd', background: 'd', border: 'px solid d', resize: 'none', lineHeight: . }}
              value={fileContentStr}
              onChange={e => setFileContentStr(e.target.value)}
              spellCheck={false}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'rem' }}>
              <span style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}>
                {(() => { try { JSON.parse(fileContentStr); return ' Valid JSON'; } catch { return ' Invalid JSON'; } })()}
              </span>
              <div style={{ display: 'flex', gap: 'rem' }}>
                <button className="btn btn-ghost" onClick={() => setEditingFile(null)}>Cancel</button>
                <button className="btn btn-primary" onClick={saveJsonEditor} disabled={savingFile}>
                  {savingFile ? 'Saving...' : 'Save Content'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
