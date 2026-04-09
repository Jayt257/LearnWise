/**
 * src/pages/activities/WritingPage.jsx
 * Writing activity — translation and free-text composition tasks.
 *
 * Bug Fix #2: Added 2000-char limit per textarea with live character counter.
 * Added empty-answer guard on submit.
 * Pass attempt_count to validateActivity for feedback tier calculation.
 */
import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActivity } from '../../api/content.js';
import { validateActivity, completeActivity } from '../../api/progress.js';
import { useSelector } from 'react-redux';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

const MAX_CHARS = 2000;

export default function WritingPage({ pairId, activityFile, activityId, maxXP, label }) {
  const navigate = useNavigate();
  const { user } = useSelector(s => s.auth);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [error, setError] = useState('');
  const attemptCount = useRef(1);

  useEffect(() => {
    setLoading(true);
    setData(null);
    getActivity(pairId, activityFile)
      .then(r => { setData(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [activityFile, pairId]);

  const tasks = data?.tasks || [];

  const handleChange = (key, val) => {
    if (val.length > MAX_CHARS) return; // Hard cap
    setAnswers(p => ({ ...p, [key]: val }));
  };

  const handleSubmit = async () => {
    setError('');
    // Guard: warn if all answers are empty
    const allEmpty = tasks.every((_, i) => !answers[`task_${i}`]?.trim());
    if (allEmpty) {
      setError('Please write at least one answer before submitting.');
      return;
    }

    setSubmitting(true);
    try {
      const questions = tasks.map((t, i) => ({
        question_id: `writing_${i}`,
        block_type: 'writing',
        user_answer: answers[`task_${i}`] || '',
        prompt: t.prompt,
        sample_answer: t.sample_answer,
      }));

      const { data: res } = await validateActivity({
        activity_id: activityId, activity_type: 'writing', lang_pair_id: pairId,
        max_xp: maxXP, user_lang: user?.native_lang || 'hi', target_lang: pairId.split('-')[1],
        questions,
        attempt_count: attemptCount.current,
      });
      setResult(res);
      attemptCount.current += 1;
      await completeActivity(pairId, {
        activity_id: activityId, activity_type: 'writing', lang_pair_id: pairId,
        score_earned: res.total_score, max_score: maxXP, passed: res.passed,
        ai_feedback: res.feedback, ai_suggestion: res.suggestion,
      });
    } catch (e) {
      const msg = e.response?.data?.detail;
      setError(Array.isArray(msg) ? msg.map(m => m.msg).join('; ') : (msg || 'Submission failed. Please try again.'));
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>;
  if (!data) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-danger-light)' }}>Failed to load writing tasks.</div>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>← Back</button>
        <div>
          <div className="badge badge-primary" style={{ marginBottom: '0.5rem', background: 'rgba(16, 185, 129, 0.2)', color: '#6ee7b7' }}>✍ Writing • +{maxXP} XP</div>
          <h1 className="heading-md">{data.title}</h1>
          <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{data.description}</p>
        </div>
      </div>

      {error && (
        <div style={{ background: 'var(--color-danger-glow)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', marginBottom: '1rem', color: 'var(--color-danger-light)', fontSize: '0.875rem' }}>
          ⚠ {error}
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2rem' }}>
        {tasks.map((t, i) => {
          const val = answers[`task_${i}`] || '';
          const remaining = MAX_CHARS - val.length;
          return (
            <div key={i} className="card">
              <h3 className="heading-sm" style={{ marginBottom: '0.5rem', color: 'var(--color-success-light)' }}>Task {i + 1}</h3>
              <p style={{ fontWeight: 500, marginBottom: '1rem' }}>{t.prompt}</p>
              {t.hint && <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '1rem', fontStyle: 'italic' }}>Hint: {t.hint}</p>}

              <textarea
                className="form-input"
                rows="4"
                placeholder="Write your response here..."
                value={val}
                onChange={e => handleChange(`task_${i}`, e.target.value)}
                style={{ fontSize: '1rem', lineHeight: 1.5 }}
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.375rem' }}>
                <span style={{ fontSize: '0.75rem', color: remaining < 200 ? 'var(--color-danger-light)' : 'var(--color-text-dim)' }}>
                  {val.length}/{MAX_CHARS} chars
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button
            className="btn btn-primary btn-lg"
            onClick={handleSubmit}
            disabled={submitting}
            style={{ background: 'linear-gradient(135deg, var(--color-success), #047857)' }}
          >
            {submitting ? <><span className="spinner" /> Evaluating with AI...</> : '✅ Submit Writing'}
          </button>
        </div>
      )}

      {result && (
        <ScoreModal
          result={result}
          maxXP={maxXP}
          onNext={() => { setShowFeedback(true); }}
          onRetry={() => { setResult(null); setAnswers({}); setError(''); }}
          activityType="writing"
        />
      )}

      {showFeedback && result && (
        <ActivityFeedback
          result={result}
          activityType="writing"
          onDismiss={() => { setShowFeedback(false); navigate('/dashboard'); }}
        />
      )}
    </div>
  );
}
