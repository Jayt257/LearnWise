/**
 * src/pages/activities/PronunciationPage.jsx
 * Pronunciation activity — shows a phrase, records user, scores based on transcription match.
 *
 * Bug Fix #6: Replaced alert() with in-component error state.
 * Bug Fix #9: Detects is_mock=true — shows warning, blocks submission.
 * Added attempt_count tracking for feedback tier.
 */
import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActivity } from '../../api/content.js';
import { transcribeAudio, validateActivity, completeActivity } from '../../api/progress.js';
import { useSelector } from 'react-redux';
import AudioRecorder from '../../components/AudioRecorder.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

export default function PronunciationPage({ pairId, activityFile, activityId, maxXP, label }) {
  const navigate = useNavigate();
  const { user } = useSelector(s => s.auth);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [transcriptions, setTranscriptions] = useState({});
  const [transcribingIndex, setTranscribingIndex] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [errors, setErrors] = useState({});
  const [mockWarning, setMockWarning] = useState(false);
  const attemptCount = useRef(1);

  useEffect(() => {
    setLoading(true);
    setData(null);
    getActivity(pairId, activityFile)
      .then(r => { setData(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [activityFile, pairId]);

  const words = data?.words || [];

  const handleRecordingComplete = async (blob, index) => {
    setTranscribingIndex(index);
    setErrors(p => ({ ...p, [index]: null }));

    try {
      const res = await transcribeAudio(blob);
      const { text, is_mock } = res.data;

      if (is_mock) {
        setMockWarning(true);
        setErrors(p => ({
          ...p,
          [index]: 'Whisper is not installed — audio transcription unavailable.',
        }));
        return;
      }
      if (!text?.trim()) {
        setErrors(p => ({ ...p, [index]: 'No speech detected. Please speak clearly and try again.' }));
        return;
      }
      setTranscriptions(p => ({ ...p, [index]: text }));
    } catch (e) {
      const detail = e.response?.data?.detail || 'Transcription failed. Please try again.';
      setErrors(p => ({ ...p, [index]: detail }));
    } finally {
      setTranscribingIndex(null);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const questions = words.map((w, i) => ({
        question_id: `pronunc_${i}`,
        block_type: 'pronunciation',
        user_answer: transcriptions[i] || '',
        correct_answer: w.target,
        prompt: `Read aloud: ${w.target}`,
      }));

      const { data: res } = await validateActivity({
        activity_id: activityId, activity_type: 'pronunciation', lang_pair_id: pairId,
        max_xp: maxXP, user_lang: user?.native_lang || 'hi', target_lang: pairId.split('-')[1],
        questions,
        attempt_count: attemptCount.current,
      });
      setResult(res);
      attemptCount.current += 1;
      await completeActivity(pairId, {
        activity_id: activityId, activity_type: 'pronunciation', lang_pair_id: pairId,
        score_earned: res.total_score, max_score: maxXP, passed: res.passed,
        ai_feedback: res.feedback, ai_suggestion: res.suggestion,
      });
    } catch (e) { console.error(e); } finally { setSubmitting(false); }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>;
  if (!data) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-danger-light)' }}>Failed to load pronunciation tasks.</div>;

  const allRecorded = words.length > 0 && words.every((_, i) => transcriptions[i]);

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>← Back</button>
        <div>
          <div className="badge badge-primary" style={{ marginBottom: '0.5rem', background: 'rgba(236, 72, 153, 0.2)', color: '#f9a8d4' }}>🗣 Pronunciation • +{maxXP} XP</div>
          <h1 className="heading-md">{data.title}</h1>
          <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{data.description}</p>
        </div>
      </div>

      {mockWarning && (
        <div style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.4)', borderRadius: 'var(--radius-md)', padding: '0.875rem 1rem', marginBottom: '1.25rem', fontSize: '0.85rem', color: '#fbbf24' }}>
          ⚠ <strong>Demo Mode:</strong> Whisper speech recognition is not available on this server. Please contact your administrator.
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {words.map((w, i) => (
          <div key={i} className="card" style={{ textAlign: 'center', display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem', color: 'var(--color-primary-light)' }}>{w.target}</h3>
            {w.romanization && <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>{w.romanization}</p>}
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-dim)', marginBottom: '1.5rem' }}>{w.native}</p>

            <div style={{ background: 'var(--color-surface-2)', borderRadius: 'var(--radius-md)', marginTop: 'auto' }}>
              {transcribingIndex === i ? (
                <div style={{ padding: '1.5rem', textAlign: 'center' }}>
                  <span className="spinner" style={{ display: 'inline-block' }} />
                  <p style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Transcribing...</p>
                </div>
              ) : (
                <AudioRecorder onRecordingComplete={(blob) => handleRecordingComplete(blob, i)} label="Read aloud" />
              )}
            </div>

            {errors[i] && (
              <div style={{ marginTop: '0.75rem', padding: '0.625rem', background: 'var(--color-danger-glow)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-md)', color: 'var(--color-danger-light)', fontSize: '0.8rem' }}>
                ⚠ {errors[i]}
              </div>
            )}

            {transcriptions[i] && (
              <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--color-success-light)', marginBottom: '0.25rem', fontWeight: 600 }}>✅ Heard:</p>
                <p style={{ fontStyle: 'italic', fontSize: '0.9rem' }}>"{transcriptions[i]}"</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button
            className="btn btn-primary btn-lg"
            onClick={handleSubmit}
            disabled={submitting || !allRecorded || mockWarning}
            style={{ background: 'linear-gradient(135deg, #ec4899, #be185d)' }}
          >
            {submitting ? <><span className="spinner" /> Evaluating...</> : '✅ Submit Recordings'}
          </button>
          {!allRecorded && !mockWarning && (
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '0.75rem' }}>Record all words to submit</p>
          )}
        </div>
      )}

      {result && (
        <ScoreModal
          result={result}
          maxXP={maxXP}
          onNext={() => setShowFeedback(true)}
          onRetry={() => { setResult(null); setTranscriptions({}); setErrors({}); }}
          activityType="pronunciation"
        />
      )}

      {showFeedback && result && (
        <ActivityFeedback
          result={result}
          activityType="pronunciation"
          onDismiss={() => { setShowFeedback(false); navigate('/dashboard'); }}
        />
      )}
    </div>
  );
}
