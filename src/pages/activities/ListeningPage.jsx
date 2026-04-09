/**
 * src/pages/activities/ListeningPage.jsx
 * Listening activity — plays audio from backend (if available) and asks comprehension questions.
 */
import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActivity } from '../../api/content.js';
import { validateActivity, completeActivity } from '../../api/progress.js';
import { useSelector } from 'react-redux';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

const MAX_INPUT_CHARS = 500; // limit gap-fill answers

export default function ListeningPage({ pairId, activityFile, activityId, maxXP, label }) {
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

  const audioSrc = data?.audio_url ? `http://localhost:5000${data.audio_url}` : null;
  const questions = data?.questions || [];

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const qData = questions.map((q, i) => ({
        question_id: `listening_q${i}`,
        block_type: 'listening',
        user_answer: answers[`q${i}`] || '',
        correct_answer: q.correct_answer || q.answer,
        prompt: q.question,
      }));
      
      const { data: res } = await validateActivity({
        activity_id: activityId, activity_type: 'listening', lang_pair_id: pairId,
        max_xp: maxXP, user_lang: user?.native_lang || 'hi', target_lang: pairId.split('-')[1],
        questions: qData,
        attempt_count: attemptCount.current,
      });
      setResult(res);
      attemptCount.current += 1;
      await completeActivity(pairId, { activity_id: activityId, activity_type: 'listening', lang_pair_id: pairId, score_earned: res.total_score, max_score: maxXP, passed: res.passed, ai_feedback: res.feedback, ai_suggestion: res.suggestion });
    } catch (e) { console.error(e); } finally { setSubmitting(false); }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>;
  if (!data) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-danger-light)' }}>Failed to load listening content.</div>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>← Back</button>
        <div style={{ flex: 1 }}>
          <div className="badge badge-primary" style={{ marginBottom: '0.5rem', background: 'rgba(245, 158, 11, 0.2)', color: '#fcd34d' }}>🎧 Listening • +{maxXP} XP</div>
          <h1 className="heading-md">{data.title}</h1>
          <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{data.description}</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '2rem', textAlign: 'center', padding: '2.5rem 1rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔊</div>
        {audioSrc ? (
          <audio controls src={audioSrc} style={{ width: '100%', maxWidth: 400, borderRadius: 'var(--radius-md)' }} />
        ) : (
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', fontStyle: 'italic', background: 'var(--color-surface-3)', padding: '1rem', borderRadius: 'var(--radius-md)', display: 'inline-block' }}>
            {data.transcript || "Audio file unavailable. Please read the transcript if provided."}
          </div>
        )}
      </div>

      <h2 className="heading-sm" style={{ marginBottom: '1rem' }}>Questions</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
        {questions.map((q, i) => (
          <div key={i} className="card">
            <p style={{ fontWeight: 600, marginBottom: '0.75rem' }}>{i + 1}. {q.question}</p>
            {q.type === 'mcq' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {q.options?.map((opt, j) => (
                  <button key={j} type="button"
                    onClick={() => setAnswers(p => ({ ...p, [`q${i}`]: opt }))}
                    style={{ padding: '0.625rem 1rem', borderRadius: 'var(--radius-md)', border: `2px solid ${answers[`q${i}`] === opt ? 'var(--color-primary)' : 'var(--color-border)'}`, background: answers[`q${i}`] === opt ? 'var(--color-primary-glow)' : 'var(--color-surface-2)', cursor: 'pointer', textAlign: 'left', fontSize: '0.875rem' }}>
                    {opt}
                  </button>
                ))}
              </div>
            ) : (
              <input className="form-input" placeholder="Type your answer..."
                maxLength={MAX_INPUT_CHARS}
                value={answers[`q${i}`] || ''} onChange={e => setAnswers(p => ({ ...p, [`q${i}`]: e.target.value }))} />
            )}
          </div>
        ))}
      </div>

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting} style={{ background: 'linear-gradient(135deg, var(--color-accent), #d97706)' }}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : '✅ Submit Answers'}
          </button>
        </div>
      )}

      {result && (
        <ScoreModal result={result} maxXP={maxXP}
          onNext={() => setShowFeedback(true)}
          onRetry={() => { setResult(null); setAnswers({}); }}
          activityType="listening"
        />
      )}

      {showFeedback && result && (
        <ActivityFeedback
          result={result}
          activityType="listening"
          onDismiss={() => { setShowFeedback(false); navigate('/dashboard'); }}
        />
      )}
    </div>
  );
}
