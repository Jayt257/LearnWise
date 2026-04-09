/**
 * src/pages/activities/TestPage.jsx
 * Formal test activity — MCQ quiz with strict 50% pass threshold.
 * Local scoring + Groq feedback. Must pass to unlock next activities.
 */
import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActivity } from '../../api/content.js';
import { validateActivity, completeActivity } from '../../api/progress.js';
import { useSelector } from 'react-redux';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

export default function TestPage({ pairId, activityFile, activityId, maxXP, label }) {
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
    getActivity(pairId, activityFile).then(r => { setData(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, [activityFile, pairId]);

  const quizBlocks = data?.blocks?.filter(b => b.type === 'quiz') || [];
  const allAnswered = quizBlocks.length > 0 && quizBlocks.every(b => answers[b.id] !== undefined);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const questions = quizBlocks.map(block => ({
        question_id: block.id,
        block_type: 'quiz',
        user_answer: answers[block.id] !== undefined ? answers[block.id] : -1,
        correct_answer: block.correct,
        prompt: block.question,
      }));
      
      const { data: res } = await validateActivity({
        activity_id: activityId, activity_type: 'test', lang_pair_id: pairId,
        max_xp: maxXP, user_lang: user?.native_lang || 'hi', target_lang: pairId.split('-')[1],
        questions,
        attempt_count: attemptCount.current,
      });
      setResult(res);
      attemptCount.current += 1;
      await completeActivity(pairId, { activity_id: activityId, activity_type: 'test', lang_pair_id: pairId, score_earned: res.total_score, max_score: maxXP, passed: res.passed, ai_feedback: res.feedback, ai_suggestion: res.suggestion });
    } catch (e) { console.error(e); } finally { setSubmitting(false); }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>;
  if (!data) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-danger-light)' }}>Failed to load test.</div>;

  const answered = Object.keys(answers).length;

  return (
    <div style={{ maxWidth: 760, margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>← Back</button>
        <div style={{ flex: 1 }}>
          <div className="badge badge-danger" style={{ marginBottom: '0.5rem' }}>📝 Test • +{maxXP} XP • Pass: 50%</div>
          <h1 className="heading-md">{data.title}</h1>
          <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{data.description}</p>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Progress</div>
          <div style={{ fontWeight: 700, fontSize: '1.125rem' }}>{answered}/{quizBlocks.length}</div>
        </div>
      </div>

      <div className="xp-bar-container" style={{ marginBottom: '2rem' }}>
        <div className="xp-bar-fill" style={{ width: `${quizBlocks.length ? (answered / quizBlocks.length) * 100 : 0}%`, background: 'linear-gradient(90deg, var(--color-danger), var(--color-accent))' }} />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {quizBlocks.map((block, qi) => (
          <div key={block.id} className="card" style={{ borderColor: answers[block.id] !== undefined ? 'var(--color-border-strong)' : 'var(--color-border)' }}>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', marginBottom: '1rem' }}>
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: answers[block.id] !== undefined ? 'var(--color-success-glow)' : 'var(--color-surface-3)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700, border: `2px solid ${answers[block.id] !== undefined ? 'var(--color-success)' : 'var(--color-border)'}` }}>
                {answers[block.id] !== undefined ? '✓' : qi + 1}
              </div>
              <p style={{ fontWeight: 600, fontSize: '0.9375rem', lineHeight: 1.5 }}>{block.question}</p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', paddingLeft: '2.25rem' }}>
              {block.options?.map((opt, i) => (
                <button key={i} type="button"
                  onClick={() => setAnswers(p => ({ ...p, [block.id]: i }))}
                  style={{ padding: '0.625rem 1rem', borderRadius: 'var(--radius-md)', border: `2px solid ${answers[block.id] === i ? 'var(--color-primary)' : 'var(--color-border)'}`, background: answers[block.id] === i ? 'var(--color-primary-glow)' : 'var(--color-surface-2)', cursor: 'pointer', textAlign: 'left', fontSize: '0.875rem', transition: 'all 0.15s', color: 'var(--color-text)' }}>
                  <span style={{ marginRight: '0.625rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>{String.fromCharCode(65 + i)}.</span>{opt}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {!result && (
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          {!allAnswered && (
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '0.75rem' }}>
              Answer all {quizBlocks.length} questions to submit
            </p>
          )}
          <button className="btn btn-danger btn-lg" onClick={handleSubmit} disabled={submitting || !allAnswered}>
            {submitting ? <><span className="spinner" /> Grading...</> : '📊 Submit Test'}
          </button>
        </div>
      )}

      {result && (
        <ScoreModal result={result} maxXP={maxXP}
          onNext={() => setShowFeedback(true)}
          onRetry={() => { setResult(null); setAnswers({}); }}
          activityType="test"
        />
      )}

      {showFeedback && result && (
        <ActivityFeedback
          result={result}
          activityType="test"
          onDismiss={() => { setShowFeedback(false); navigate('/dashboard'); }}
        />
      )}
    </div>
  );
}
