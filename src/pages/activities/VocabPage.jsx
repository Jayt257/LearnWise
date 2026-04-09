/**
 * src/pages/activities/VocabPage.jsx
 * Vocabulary activity — flashcards + spelling input.
 */
import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActivity } from '../../api/content.js';
import { validateActivity, completeActivity } from '../../api/progress.js';
import { useSelector } from 'react-redux';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

const MAX_INPUT_CHARS = 200;

export default function VocabPage({ pairId, activityFile, activityId, maxXP, label }) {
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

  // Extract words from the new blocks schema or fallback to old root words
  const words = [];
  if (data?.blocks) {
    data.blocks.forEach(b => {
      if (b.type === 'image_word' && b.items) {
        b.items.forEach(item => words.push({ target: item.word, native: item.meaning, notes: item.example, emoji: item.emoji }));
      } else if (b.type === 'vocab_table' && b.words) {
        b.words.forEach(item => words.push({ target: item.word, native: item.meaning, notes: item.example }));
      }
    });
  } else if (data?.words) {
    words.push(...data.words);
  }

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const questions = words.map((w, i) => ({
        question_id: `word_${i}`,
        block_type: 'vocab',
        user_answer: answers[`word_${i}`] || '',
        correct_answer: w.target,
        prompt: `Translate to target language: ${w.native}`,
      }));
      
      const { data: res } = await validateActivity({
        activity_id: activityId, activity_type: 'vocab', lang_pair_id: pairId,
        max_xp: maxXP, user_lang: user?.native_lang || 'hi', target_lang: pairId.split('-')[1],
        questions,
        attempt_count: attemptCount.current,
      });
      setResult(res);
      attemptCount.current += 1;
      await completeActivity(pairId, { activity_id: activityId, activity_type: 'vocab', lang_pair_id: pairId, score_earned: res.total_score, max_score: maxXP, passed: res.passed, ai_feedback: res.feedback, ai_suggestion: res.suggestion });
    } catch (e) { console.error(e); } finally { setSubmitting(false); }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>;
  if (!data) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-danger-light)' }}>Failed to load vocabulary.</div>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>← Back</button>
        <div>
          <div className="badge badge-primary" style={{ marginBottom: '0.5rem', background: 'rgba(139, 92, 246, 0.2)', color: '#c4b5fd' }}>🔤 Vocabulary • +{maxXP} XP</div>
          <h1 className="heading-md">{data.title}</h1>
          <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{data.description}</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {words.map((w, i) => (
          <div key={i} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              {w.emoji && <span style={{ marginRight: '0.5rem' }}>{w.emoji}</span>}
              {w.native}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '1rem', flex: 1 }}>{w.notes}</div>
            
            <div className="form-group" style={{ marginTop: 'auto' }}>
              <label className="form-label" style={{ fontSize: '0.75rem' }}>Type the translation:</label>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <input className="form-input" placeholder="Enter word..." 
                  value={answers[`word_${i}`] || ''} 
                  onChange={e => {
                    const val = e.target.value;
                    if (val.length <= MAX_INPUT_CHARS) {
                      setAnswers(p => ({ ...p, [`word_${i}`]: val }));
                    }
                  }} />
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.25rem' }}>
                  <span style={{ fontSize: '0.7rem', color: (MAX_INPUT_CHARS - (answers[`word_${i}`]?.length || 0)) < 20 ? 'var(--color-danger-light)' : 'var(--color-text-dim)' }}>
                    {(answers[`word_${i}`] || '').length}/{MAX_INPUT_CHARS}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : '✅ Submit Vocabulary'}
          </button>
        </div>
      )}

      {result && (
        <ScoreModal result={result} maxXP={maxXP}
          onNext={() => setShowFeedback(true)}
          onRetry={() => { setResult(null); setAnswers({}); }}
          activityType="vocab"
        />
      )}

      {showFeedback && result && (
        <ActivityFeedback
          result={result}
          activityType="vocab"
          onDismiss={() => { setShowFeedback(false); navigate('/dashboard'); }}
        />
      )}
    </div>
  );
}
