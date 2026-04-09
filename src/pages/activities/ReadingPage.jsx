/**
 * src/pages/activities/ReadingPage.jsx
 * Reading activity — text passage + comprehension questions.
 */
import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActivity } from '../../api/content.js';
import { validateActivity, completeActivity } from '../../api/progress.js';
import { useSelector } from 'react-redux';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

const MAX_INPUT_CHARS = 1000;

export default function ReadingPage({ pairId, activityFile, activityId, maxXP, label }) {
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

  // Extract passage and questions from the new blocks schema or fallback to old root structure
  let passage = data?.passage || '';
  let questions = data?.questions || [];
  
  if (data?.blocks) {
    const readingBlock = data.blocks.find(b => b.type === 'reading');
    if (readingBlock) {
      passage = readingBlock.passage || passage;
      questions = readingBlock.questions?.map(q => ({
        question: q.q || q.question,
        answer: q.a || q.answer,
        type: q.type || 'text',
        options: q.options
      })) || questions;
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const qData = questions.map((q, i) => ({
        question_id: `reading_q${i}`,
        block_type: 'reading',
        user_answer: answers[`q${i}`] || '',
        correct_answer: q.correct_answer || q.answer,
        prompt: q.question,
      }));
      
      const { data: res } = await validateActivity({
        activity_id: activityId, activity_type: 'reading', lang_pair_id: pairId,
        max_xp: maxXP, user_lang: user?.native_lang || 'hi', target_lang: pairId.split('-')[1],
        questions: qData,
        attempt_count: attemptCount.current,
      });
      setResult(res);
      attemptCount.current += 1;
      await completeActivity(pairId, { activity_id: activityId, activity_type: 'reading', lang_pair_id: pairId, score_earned: res.total_score, max_score: maxXP, passed: res.passed, ai_feedback: res.feedback, ai_suggestion: res.suggestion });
    } catch (e) { console.error(e); } finally { setSubmitting(false); }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>;
  if (!data) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-danger-light)' }}>Failed to load reading content.</div>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>← Back</button>
        <div>
          <div className="badge badge-primary" style={{ marginBottom: '0.5rem', background: 'rgba(6, 182, 212, 0.2)', color: '#67e8f9' }}>📄 Reading • +{maxXP} XP</div>
          <h1 className="heading-md">{data.title}</h1>
          <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{data.description}</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '2rem', background: 'var(--color-surface-2)' }}>
        <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8, fontSize: '1.05rem' }}>{passage}</p>
      </div>

      <h2 className="heading-sm" style={{ marginBottom: '1rem' }}>Comprehension Questions</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
        {questions.map((q, i) => (
          <div key={i} className="card">
            <p style={{ fontWeight: 600, marginBottom: '0.75rem' }}>{i + 1}. {q.question}</p>
            {q.type === 'mcq' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {q.options?.map((opt, j) => (
                  <button key={j} type="button"
                    onClick={() => setAnswers(p => ({ ...p, [`q${i}`]: opt }))}
                    style={{ padding: '0.625rem 1rem', borderRadius: 'var(--radius-md)', border: `2px solid ${answers[`q${i}`] === opt ? 'var(--color-secondary)' : 'var(--color-border)'}`, background: answers[`q${i}`] === opt ? 'var(--color-secondary-glow)' : 'var(--color-surface-2)', cursor: 'pointer', textAlign: 'left', fontSize: '0.875rem' }}>
                    {opt}
                  </button>
                ))}
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <textarea className="form-input" rows="3" placeholder="Type your answer based on the passage..."
                  value={answers[`q${i}`] || ''} 
                  onChange={e => {
                    const val = e.target.value;
                    if (val.length <= MAX_INPUT_CHARS) {
                      setAnswers(p => ({ ...p, [`q${i}`]: val }));
                    }
                  }} />
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.375rem' }}>
                  <span style={{ fontSize: '0.75rem', color: (MAX_INPUT_CHARS - (answers[`q${i}`]?.length || 0)) < 100 ? 'var(--color-danger-light)' : 'var(--color-text-dim)' }}>
                    {(answers[`q${i}`] || '').length}/{MAX_INPUT_CHARS} chars
                  </span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting} style={{ background: 'linear-gradient(135deg, var(--color-secondary), #0369a1)' }}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : '✅ Submit Answers'}
          </button>
        </div>
      )}

      {result && (
        <ScoreModal result={result} maxXP={maxXP}
          onNext={() => setShowFeedback(true)}
          onRetry={() => { setResult(null); setAnswers({}); }}
          activityType="reading"
        />
      )}

      {showFeedback && result && (
        <ActivityFeedback
          result={result}
          activityType="reading"
          onDismiss={() => { setShowFeedback(false); navigate('/dashboard'); }}
        />
      )}
    </div>
  );
}
