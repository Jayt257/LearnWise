/**
 * src/pages/activities/LessonPage.jsx
 * Renders lesson content blocks (text, table, dialogue, grammar, fill_blank, quiz).
 * Collects user answers from fill_blank/quiz blocks, submits to Groq for validation.
 */
import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActivity } from '../../api/content.js';
import { validateActivity, completeActivity } from '../../api/progress.js';
import { useSelector } from 'react-redux';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

const MAX_INPUT_CHARS = 100;

export default function LessonPage({ pairId, activityFile, activityId, maxXP, label }) {
  const navigate = useNavigate();
  const { user } = useSelector(s => s.auth);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const attemptCount = useRef(1);

  useEffect(() => {
    setLoading(true);
    setData(null);
    getActivity(pairId, activityFile)
      .then(r => { setData(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [activityFile, pairId]); // Bug Fix #7: include pairId so data reloads on pair change

  const interactiveBlocks = data?.blocks?.filter(b => ['fill_blank', 'quiz', 'matching'].includes(b.type)) || [];

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const questions = interactiveBlocks.map(block => {
        if (block.type === 'fill_blank') {
          return block.items.map((item, i) => ({
            question_id: `${block.id}_${i}`,
            block_type: 'fill_blank',
            user_answer: answers[`${block.id}_${i}`] || '',
            correct_answer: item.answer,
            prompt: item.sentence,
          }));
        } else if (block.type === 'quiz') {
          return [{
            question_id: block.id,
            block_type: 'quiz',
            user_answer: answers[block.id] !== undefined ? block.options[answers[block.id]] : '',
            correct_answer: block.options[block.correct],
            prompt: block.question,
          }];
        }
        return [];
      }).flat();

      // If no interactive blocks, auto-pass lesson reading
      if (questions.length === 0) {
        const autoResult = { total_score: maxXP, max_score: maxXP, percentage: 100, passed: true, feedback: 'Great job completing the lesson! You have read all the content.', suggestion: 'Continue to the vocabulary activity to reinforce what you learned.', question_results: [] };
        setResult(autoResult);
        await completeActivity(pairId, { activity_id: activityId, activity_type: 'lesson', lang_pair_id: pairId, score_earned: maxXP, max_score: maxXP, passed: true, ai_feedback: autoResult.feedback });
        return;
      }

      const { data: res } = await validateActivity({
        activity_id: activityId, activity_type: 'lesson', lang_pair_id: pairId,
        max_xp: maxXP, user_lang: user?.native_lang || 'hi', target_lang: pairId.split('-')[1],
        questions,
        attempt_count: attemptCount.current,
      });
      setResult(res);
      attemptCount.current += 1;
      await completeActivity(pairId, { activity_id: activityId, activity_type: 'lesson', lang_pair_id: pairId, score_earned: res.total_score, max_score: maxXP, passed: res.passed, ai_feedback: res.feedback, ai_suggestion: res.suggestion });
    } catch (e) { console.error(e); } finally { setSubmitting(false); }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>;
  if (!data) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-danger-light)' }}>Failed to load lesson.</div>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>← Back</button>
        <div>
          <div className="badge badge-primary" style={{ marginBottom: '0.5rem' }}>📖 Lesson • +{maxXP} XP</div>
          <h1 className="heading-md">{data.title}</h1>
          <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{data.description}</p>
        </div>
      </div>

      {/* Blocks */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {data.blocks?.map(block => <LessonBlock key={block.id} block={block} answers={answers} setAnswers={setAnswers} />)}
      </div>

      {/* Submit */}
      {!result && (
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating with AI...</> : '✅ Submit & Get AI Feedback'}
          </button>
        </div>
      )}

      {result && (
        <ScoreModal result={result} maxXP={maxXP}
          onNext={() => setShowFeedback(true)}
          onRetry={() => { setResult(null); setAnswers({}); }}
        />
      )}

      {showFeedback && result && (
        <ActivityFeedback
          result={result}
          activityType="lesson"
          onDismiss={() => { setShowFeedback(false); navigate('/dashboard'); }}
        />
      )}
    </div>
  );
}

function LessonBlock({ block, answers, setAnswers }) {
  const setAnswer = (key, val) => setAnswers(p => ({ ...p, [key]: val }));

  switch (block.type) {
    case 'text':
      return (
        <div className="card">
          {block.title && <h3 className="heading-sm" style={{ marginBottom: '0.75rem', color: 'var(--color-primary-light)' }}>{block.title}</h3>}
          <p style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>{block.body}</p>
        </div>
      );
    case 'keypoints':
      return (
        <div className="card">
          <h3 className="heading-sm" style={{ marginBottom: '0.75rem' }}>{block.title}</h3>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {block.points?.map((pt, i) => (
              <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.625rem', fontSize: '0.9rem' }}>
                <span style={{ color: 'var(--color-primary-light)', marginTop: '0.125rem', flexShrink: 0 }}>✦</span>{pt}
              </li>
            ))}
          </ul>
        </div>
      );
    case 'comparison_table':
      return (
        <div className="card" style={{ overflow: 'auto' }}>
          <h3 className="heading-sm" style={{ marginBottom: '0.75rem' }}>{block.title}</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr>{block.headers?.map((h, i) => <th key={i} style={{ padding: '0.5rem 0.75rem', textAlign: 'left', borderBottom: '1px solid var(--color-border)', color: 'var(--color-primary-light)' }}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {block.rows?.map((row, i) => (
                <tr key={i} style={{ background: i % 2 === 0 ? 'transparent' : 'var(--color-surface-2)' }}>
                  {row.map((cell, j) => <td key={j} style={{ padding: '0.5rem 0.75rem', borderBottom: '1px solid var(--color-border)' }}>{cell}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    case 'dialogue':
      return (
        <div className="card">
          <h3 className="heading-sm" style={{ marginBottom: '1rem' }}>{block.title}</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {block.lines?.map((line, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', flexDirection: line.speaker === 0 ? 'row' : 'row-reverse' }}>
                <div style={{ width: 32, height: 32, borderRadius: '50%', background: line.speaker === 0 ? 'var(--color-primary-glow)' : 'var(--color-secondary-glow)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', border: `2px solid ${line.speaker === 0 ? 'var(--color-primary)' : 'var(--color-secondary)'}` }}>
                  {line.speaker === 0 ? '👤' : '🤝'}
                </div>
                <div style={{ background: 'var(--color-surface-2)', borderRadius: 'var(--radius-md)', padding: '0.625rem 0.875rem', maxWidth: '80%' }}>
                  <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>{line.text}</p>
                  {line.romanization && <p style={{ fontSize: '0.75rem', color: 'var(--color-secondary-light)', marginTop: '0.25rem' }}>{line.romanization}</p>}
                  {line.translation && <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.125rem' }}>{line.translation}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    case 'grammar_rule':
      return (
        <div className="card" style={{ border: '1px solid rgba(99,102,241,0.3)', background: 'rgba(99,102,241,0.05)' }}>
          <h3 className="heading-sm" style={{ marginBottom: '0.75rem', color: 'var(--color-primary-light)' }}>{block.title}</h3>
          <div style={{ background: 'var(--color-surface-3)', borderRadius: 'var(--radius-sm)', padding: '0.5rem 1rem', display: 'inline-block', marginBottom: '0.75rem', fontFamily: 'monospace', fontSize: '0.9rem', color: 'var(--color-accent-light)' }}>{block.pattern}</div>
          {block.examples?.map((ex, i) => (
            <div key={i} style={{ background: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)', padding: '0.625rem', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
              <div style={{ color: 'var(--color-text-muted)' }}>{ex.native}</div>
              <div style={{ fontWeight: 600, color: 'var(--color-success-light)', marginTop: '0.25rem' }}>{ex.target}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', marginTop: '0.125rem' }}>{ex.translation}</div>
            </div>
          ))}
          {block.note && <p style={{ fontSize: '0.8rem', color: 'var(--color-accent-light)', marginTop: '0.5rem', padding: '0.5rem', background: 'var(--color-accent-glow)', borderRadius: 'var(--radius-sm)' }}>💡 {block.note}</p>}
        </div>
      );
    case 'tip':
      return (
        <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
          <p style={{ fontSize: '0.875rem', lineHeight: 1.7 }}>{block.body}</p>
        </div>
      );
    case 'fill_blank':
      return (
        <div className="card">
          <h3 className="heading-sm" style={{ marginBottom: '0.5rem' }}>{block.title}</h3>
          {block.instructions && <p className="text-muted" style={{ fontSize: '0.8rem', marginBottom: '1rem' }}>{block.instructions}</p>}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {block.items?.map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.875rem', flex: 1, minWidth: 180 }}>{item.sentence}</span>
                <input className="form-input" style={{ width: 180, flex: '0 0 auto' }} placeholder={item.hint || 'Your answer...'}
                  maxLength={MAX_INPUT_CHARS}
                  value={answers[`${block.id}_${i}`] || ''}
                  onChange={e => setAnswer(`${block.id}_${i}`, e.target.value)} />
              </div>
            ))}
          </div>
        </div>
      );
    case 'quiz':
      return (
        <div className="card">
          <p style={{ fontWeight: 600, marginBottom: '1rem' }}>{block.question}</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {block.options?.map((opt, i) => (
              <button key={i} type="button"
                onClick={() => setAnswer(block.id, i)}
                style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', border: `2px solid ${answers[block.id] === i ? 'var(--color-primary)' : 'var(--color-border)'}`, background: answers[block.id] === i ? 'var(--color-primary-glow)' : 'var(--color-surface-2)', cursor: 'pointer', textAlign: 'left', fontSize: '0.875rem', transition: 'all 0.15s' }}>
                <span style={{ marginRight: '0.5rem', color: 'var(--color-text-muted)' }}>{String.fromCharCode(65 + i)}.</span>{opt}
              </button>
            ))}
          </div>
        </div>
      );
    case 'cultural_note':
      return (
        <div style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
          <h4 style={{ color: 'var(--color-accent-light)', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 600 }}>
            {block.icon || '🌍'} {block.title}
          </h4>
          <p style={{ fontSize: '0.875rem', lineHeight: 1.7 }}>{block.content}</p>
        </div>
      );
    case 'progress_checkpoint':
      return (
        <div style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
          <h4 style={{ color: 'var(--color-success-light)', marginBottom: '0.75rem', fontSize: '0.875rem', fontWeight: 600 }}>✅ {block.title}</h4>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
            {block.items?.map((item, i) => <li key={i} style={{ fontSize: '0.85rem', display: 'flex', gap: '0.5rem' }}><span>☑</span>{item}</li>)}
          </ul>
          {block.xpBonus && <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--color-accent-light)' }}>⭐ Bonus: +{block.xpBonus} XP for completing all checkpoints!</p>}
        </div>
      );
    default:
      return null;
  }
}
