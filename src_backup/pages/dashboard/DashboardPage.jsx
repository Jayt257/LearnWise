/
  src/pages/dashboard/DashboardPage.jsx
  Skill-tree redesign — circular nodes, glow rings, skeleton loaders.
  ALL logic (data fetching, navigation, progress calculation) is untouched.
 /
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAllProgress, fetchPairs, setCurrentPair } from '../../store/progressSlice.js';
import { getMeta } from '../../api/content.js';
import { getCompletions, startPair } from '../../api/progress.js';

const ACTIVITY_ICONS = {
  lesson: '', vocabulary: '', vocab: '',
  reading: '', writing: '', listening: '',
  speaking: '', pronunciation: '', test: '',
};
const ACTIVITY_COLORS = {
  lesson: 'CEFA', vocabulary: 'BFF', vocab: 'BFF',
  reading: 'DFF', writing: 'EB', listening: 'FFB',
  speaking: 'FCC', pronunciation: 'FFBA', test: 'FFDD',
};

/ ── Skeleton placeholder card ─────────────────────────────── /
function SkeletonCard() {
  return (
    <div style={{ borderRadius: 'var(--radius-lg)', overflow: 'hidden', border: 'px solid var(--border)' }}>
      <div className="skeleton" style={{ height: , marginBottom:  }} />
      <div style={{ padding: '.rem', display: 'flex', flexWrap: 'wrap', gap: '.rem' }}>
        {Array.from({ length:  }).map((_, i) => (
          <div key={i} className="skeleton" style={{ width: , height: , borderRadius: '%' }} />
        ))}
      </div>
    </div>
  );
}

/ ── Single activity node ───────────────────────────────────── /
function SkillNode({ activity, unlocked, completed, isCurrent, onClick }) {
  const color = ACTIVITY_COLORS[activity.type] || 'CEFA';
  const icon  = ACTIVITY_ICONS[activity.type] || '';
  const lbl   = activity.label || (activity.type.charAt().toUpperCase() + activity.type.slice());

  let nodeClass = 'skill-node';
  if (completed)  nodeClass += ' completed';
  else if (isCurrent) nodeClass += ' current';
  else if (!unlocked) nodeClass += ' locked';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '.rem', width:  }}>
      <div
        className={nodeClass}
        onClick={() => unlocked && onClick()}
        title={unlocked ? lbl : 'Complete previous activities first'}
        style={{
          '--node-color': color,
          borderColor: completed ? color : isCurrent ? color : undefined,
        }}
      >
        {/ Status badge /}
        {completed && (
          <div style={{ position: 'absolute', top: -, right: -, width: , height: , borderRadius: '%', background: 'var(--emerald)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '.rem', border: 'px solid var(--bg)' }}>✓</div>
        )}
        {!unlocked && !completed && (
          <div style={{ position: 'absolute', top: -, right: -, width: , height: , borderRadius: '%', background: 'var(--surface-)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '.rem', border: 'px solid var(--bg)' }}></div>
        )}

        <div className="node-icon">{icon}</div>
        <div className="node-xp" style={{ color: unlocked ? color : 'var(--text-dim)' }}>+{activity.xp}</div>
      </div>

      {/ Label below node /}
      <div style={{
        fontSize: '.rem',
        fontWeight: ,
        color: unlocked ? 'var(--text-muted)' : 'var(--text-dim)',
        textAlign: 'center',
        width: '%',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
      }}>
        {lbl}
      </div>
    </div>
  );
}

/ ── Main page ─────────────────────────────────────────────── /
export default function DashboardPage() {
  const navigate  = useNavigate();
  const dispatch  = useDispatch();
  const { allProgress, currentPairId, pairs } = useSelector(s => s.progress);

  const [meta,         setMeta]         = useState(null);
  const [completions,  setCompletions]  = useState([]);
  const [selectedPair, setSelectedPair] = useState(currentPairId);
  const [loading,      setLoading]      = useState(true);
  const [expandedMonth, setExpandedMonth] = useState();

  const currentProgress = allProgress.find(p => p.lang_pair_id === selectedPair);

  useEffect(() => { dispatch(fetchAllProgress()); dispatch(fetchPairs()); }, []);

  useEffect(() => {
    if (!selectedPair && allProgress.length > ) setSelectedPair(allProgress[].lang_pair_id);
  }, [allProgress, selectedPair]);

  useEffect(() => {
    if (!selectedPair) return;
    setLoading(true);
    Promise.all([
      getMeta(selectedPair).then(r => setMeta(r.data)),
      getCompletions(selectedPair).then(r => setCompletions(r.data)),
    ]).catch(console.error).finally(() => setLoading(false));
  }, [selectedPair]);

  const completedSeqIds  = new Set(completions.filter(c => c.passed).map(c => c.activity_seq_id));
  const currentActivityId = currentProgress?.current_activity_id || ;
  const isUnlocked  = seqId => seqId <= currentActivityId;
  const isCompleted = seqId => completedSeqIds.has(seqId);

  const handleActivityClick = (activity, pairId, monthNum, blockNum) => {
    if (!isUnlocked(activity.id)) return;
    navigate(`/activity/${pairId}/${activity.type}`, {
      state: {
        activityFile: activity.file,
        activitySeqId: activity.id,
        activityJsonId: null,
        maxXP: activity.xp,
        label: activity.label || activity.type,
        monthNumber: monthNum,
        blockNumber: blockNum,
      }
    });
  };

  const srcInfo = meta?.source || {};
  const tgtInfo = meta?.target || {};

  if (!selectedPair) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 'vh', flexDirection: 'column', gap: '.rem' }}>
        <div style={{ fontSize: 'rem' }} className="animate-float"></div>
        <h className="heading-md">No language path selected</h>
        <button className="btn btn-primary btn-lg" onClick={() => navigate('/onboarding')}>Choose a Language</button>
      </div>
    );
  }

  // Progress stats
  const totalActivities = (meta?.months || []).reduce((acc, m) =>
    acc + m.blocks.reduce((a, b) => a + (b.activities?.length || ), ), );
  const progressPct = totalActivities > 
    ? Math.min(((currentActivityId - ) / totalActivities)  , )
    : ;

  return (
    <div>
      {/ ── Hero header ────────────────────────────────────── /}
      <div style={{ marginBottom: 'rem' }} className="animate-fade-up">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '.rem', marginBottom: '.rem' }}>
              <span style={{ fontSize: '.rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', letterSpacing: '.em' }}>
                Learning Roadmap
              </span>
            </div>
            <h className="heading-lg">
              <span style={{ fontSize: '.rem' }}>{srcInfo.flag || ''}</span>
              {' '}
              <span style={{ color: 'var(--text-dim)', margin: ' .rem' }}>→</span>
              {' '}
              <span style={{ fontSize: '.rem' }}>{tgtInfo.flag || ''}</span>
              {' '}
              <span className="gradient-text">
                {srcInfo.name} to {tgtInfo.name || tgtInfo.native}
              </span>
            </h>
            <p className="text-muted" style={{ marginTop: '.rem', fontSize: '.rem' }}>
              {meta?.totalMonths || }-month roadmap ·{' '}
              {(meta?.months || []).reduce((acc, m) => acc + (m.blocks?.length || ), )} blocks ·{' '}
              {completedSeqIds.size} activities completed
            </p>
          </div>

          <div style={{ display: 'flex', gap: '.rem', alignItems: 'center', flexWrap: 'wrap' }}>
            {currentProgress && (
              <div style={{
                background: 'var(--amber-glow)',
                border: 'px solid var(--amber)',
                borderRadius: 'var(--radius-full)',
                padding: '.rem rem',
                display: 'flex', alignItems: 'center', gap: '.rem',
              }}>
                <span></span>
                <span style={{ fontWeight: , color: 'var(--amber)', fontFamily: 'var(--font-mono)' }}>
                  {currentProgress.total_xp} XP
                </span>
              </div>
            )}
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/onboarding')}>
               Switch Language
            </button>
          </div>
        </div>

        {/ XP bar /}
        {currentProgress && (
          <div style={{ marginTop: '.rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.rem', color: 'var(--text-muted)', marginBottom: '.rem', fontFamily: 'var(--font-mono)' }}>
              <span>Month {currentProgress.current_month} · Block {currentProgress.current_block}</span>
              <span>{Math.round(progressPct)}% complete</span>
            </div>
            <div className="xp-bar-container">
              <div className="xp-bar-fill" style={{ width: `${progressPct}%` }} />
            </div>
          </div>
        )}
      </div>

      {/ ── Pair switcher ───────────────────────────────────── /}
      {allProgress.length >  && (
        <div style={{ display: 'flex', gap: '.rem', marginBottom: '.rem', flexWrap: 'wrap' }}>
          {allProgress.map(p => (
            <button key={p.lang_pair_id}
              className={`btn btn-sm ${selectedPair === p.lang_pair_id ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => { setSelectedPair(p.lang_pair_id); dispatch(setCurrentPair(p.lang_pair_id)); }}>
              {p.lang_pair_id.toUpperCase()}
            </button>
          ))}
        </div>
      )}

      {/ ── Roadmap ─────────────────────────────────────────── /}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'rem' }}>
          {[,,].map(i => <SkeletonCard key={i} />)}
        </div>
      ) : meta ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'rem' }}>
          {(meta.months || []).map((month, mIdx) => {
            const monthBlocks     = month.blocks || [];
            const monthActivities = monthBlocks.flatMap(b => b.activities || []);
            const monthCompleted  = monthActivities.filter(a => isCompleted(a.id)).length;
            const monthTotal      = monthActivities.length;
            const isExpanded      = expandedMonth === month.month;
            const monthPct        = monthTotal >  ? Math.round((monthCompleted / monthTotal)  ) : ;

            return (
              <div
                key={month.month}
                className="card animate-fade-up"
                style={{ animationDelay: `${mIdx  .}s`, padding: '', overflow: 'hidden' }}
              >
                {/ Month header /}
                <div
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '.rem .rem',
                    cursor: 'pointer',
                    borderBottom: isExpanded ? 'px solid var(--border)' : 'none',
                    background: isExpanded ? 'var(--surface-)' : 'transparent',
                    transition: 'background var(--transition)',
                  }}
                  onClick={() => setExpandedMonth(isExpanded ? null : month.month)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'rem' }}>
                    {/ Month number disc /}
                    <div style={{
                      width: , height: ,
                      borderRadius: '%',
                      background: isExpanded
                        ? 'linear-gradient(deg, var(--primary), var(--cyan))'
                        : 'var(--surface-)',
                      border: isExpanded ? 'none' : 'px solid var(--border)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontFamily: 'var(--font-display)', fontWeight: ,
                      color: isExpanded ? 'white' : 'var(--text-muted)',
                      fontSize: '.rem',
                      flexShrink: ,
                      boxShadow: isExpanded ? '  px var(--primary-glow)' : 'none',
                      transition: 'all var(--transition)',
                    }}>
                      M{month.month}
                    </div>
                    <div>
                      <div className="heading-sm">{month.title}</div>
                      <div style={{ fontSize: '.rem', color: 'var(--text-muted)', marginTop: '.rem', fontFamily: 'var(--font-mono)' }}>
                        {month.targetLevel} · {monthBlocks.length} blocks · {monthCompleted}/{monthTotal} done
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 'rem' }}>
                    {/ Mini progress /}
                    <div style={{
                      display: 'flex', alignItems: 'center', gap: '.rem',
                      padding: '.rem .rem',
                      borderRadius: 'var(--radius-full)',
                      background: monthCompleted === monthTotal && monthTotal > 
                        ? 'var(--success-glow)'
                        : 'var(--surface-)',
                      border: 'px solid var(--border)',
                    }}>
                      <div style={{
                        width: , height: ,
                        borderRadius: 'var(--radius-full)',
                        background: 'var(--surface-)',
                        overflow: 'hidden',
                      }}>
                        <div style={{
                          width: `${monthPct}%`, height: '%',
                          background: monthCompleted === monthTotal && monthTotal > 
                            ? 'var(--emerald)'
                            : 'var(--primary)',
                          borderRadius: 'var(--radius-full)',
                          transition: 'width .s ease',
                        }} />
                      </div>
                      <span style={{
                        fontSize: '.rem', fontFamily: 'var(--font-mono)',
                        color: monthCompleted === monthTotal && monthTotal > 
                          ? 'var(--success-light)'
                          : 'var(--text-muted)',
                      }}>
                        {monthPct}%
                      </span>
                    </div>
                    <span style={{ color: 'var(--text-dim)', fontSize: 'rem', transition: 'transform var(--transition)', transform: isExpanded ? 'rotate(deg)' : 'none' }}>
                      ▼
                    </span>
                  </div>
                </div>

                {/ Blocks /}
                {isExpanded && (
                  <div style={{ padding: '.rem' }}>
                    {monthBlocks.map((block, bIdx) => {
                      const blockDone  = (block.activities || []).filter(a => isCompleted(a.id)).length;
                      const blockTotal = (block.activities || []).length;
                      const allDone    = blockDone === blockTotal && blockTotal > ;

                      return (
                        <div key={block.block} style={{ marginBottom: bIdx < monthBlocks.length -  ? 'rem' :  }}>
                          {/ Block header /}
                          <div style={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            marginBottom: '.rem',
                            paddingBottom: '.rem',
                            borderBottom: 'px dashed var(--border)',
                          }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '.rem' }}>
                              <div style={{
                                width: , height: , borderRadius: '%',
                                background: allDone ? 'var(--emerald)' : 'var(--border-strong)',
                                boxShadow: allDone ? '  px var(--emerald)' : 'none',
                              }} />
                              <span style={{ fontSize: '.rem', fontWeight: , color: 'var(--text-muted)' }}>
                                Block {block.block}: {block.title}
                              </span>
                            </div>
                            <span style={{
                              fontSize: '.rem',
                              fontFamily: 'var(--font-mono)',
                              color: allDone ? 'var(--success-light)' : 'var(--text-dim)',
                            }}>
                              {blockDone}/{blockTotal}{allDone ? ' ✓' : ''}
                            </span>
                          </div>

                          {/ Skill nodes grid /}
                          <div style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '.rem',
                          }}>
                            {(block.activities || []).map(activity => (
                              <SkillNode
                                key={activity.id}
                                activity={activity}
                                unlocked={isUnlocked(activity.id)}
                                completed={isCompleted(activity.id)}
                                isCurrent={activity.id === currentActivityId}
                                onClick={() => handleActivityClick(activity, selectedPair, month.month, block.block)}
                              />
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: 'rem', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: 'rem', marginBottom: 'rem' }}></div>
          <p>No roadmap data found for this language pair.</p>
        </div>
      )}
    </div>
  );
}
