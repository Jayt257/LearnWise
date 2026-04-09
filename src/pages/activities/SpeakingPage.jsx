/**
 * src/pages/activities/SpeakingPage.jsx
 * Speaking activity — scenario roleplay.
 * Records user audio, transcribes with Whisper, validates with Groq.
 *
 * Bug Fix #6: Replaced alert() with in-component error state.
 * Bug Fix #9: Detects is_mock=true from Whisper — shows warning, blocks submission.
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

export default function SpeakingPage({ pairId, activityFile, activityId, maxXP, label }) {
  const navigate = useNavigate();
  const { user } = useSelector(s => s.auth);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [transcriptions, setTranscriptions] = useState({});
  const [transcribingIndex, setTranscribingIndex] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [errors, setErrors] = useState({});        // per-scenario errors
  const [globalError, setGlobalError] = useState('');
  const [mockWarning, setMockWarning] = useState(false); // Bug Fix #9
  const attemptCount = useRef(1);

  useEffect(() => {
    setLoading(true);
    setData(null);
    getActivity(pairId, activityFile)
      .then(r => { setData(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [activityFile, pairId]);

  const scenarios = data?.scenarios || [];

  const handleRecordingComplete = async (blob, index) => {
    setTranscribingIndex(index);
    setErrors(p => ({ ...p, [index]: null }));

    try {
      const res = await transcribeAudio(blob);
      const { text, is_mock } = res.data;

      // Bug Fix #9: Detect mock transcription
      if (is_mock) {
        setMockWarning(true);
        setErrors(p => ({
          ...p,
          [index]: 'Whisper is not installed on this server — audio transcription is unavailable. Please contact your administrator.',
        }));
        return;
      }

      if (!text?.trim()) {
        setErrors(p => ({
          ...p,
          [index]: 'No speech detected in the recording. Please speak clearly and try again.',
        }));
        return;
      }

      setTranscriptions(p => ({ ...p, [index]: text }));
    } catch (e) {
      // Bug Fix #6: No more alert() — use in-component error state
      const detail = e.response?.data?.detail || 'Transcription failed. Please try again.';
      setErrors(p => ({ ...p, [index]: detail }));
    } finally {
      setTranscribingIndex(null);
    }
  };

  const handleSubmit = async () => {
    setGlobalError('');
    setSubmitting(true);
    try {
      const questions = scenarios.map((s, i) => ({
        question_id: `scenario_${i}`,
        block_type: 'speaking',
        user_answer: transcriptions[i] || '',
        prompt: s.prompt,
      }));

      const { data: res } = await validateActivity({
        activity_id: activityId, activity_type: 'speaking', lang_pair_id: pairId,
        max_xp: maxXP, user_lang: user?.native_lang || 'hi', target_lang: pairId.split('-')[1],
        questions,
        attempt_count: attemptCount.current,
      });
      setResult(res);
      attemptCount.current += 1;
      await completeActivity(pairId, {
        activity_id: activityId, activity_type: 'speaking', lang_pair_id: pairId,
        score_earned: res.total_score, max_score: maxXP, passed: res.passed,
        ai_feedback: res.feedback, ai_suggestion: res.suggestion,
      });
    } catch (e) {
      setGlobalError(e.response?.data?.detail || 'Submission failed. Please try again.');
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>;
  if (!data) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-danger-light)' }}>Failed to load speaking tasks.</div>;

  const allRecorded = scenarios.length > 0 && scenarios.every((_, i) => transcriptions[i]);

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>← Back</button>
        <div>
          <div className="badge badge-primary" style={{ marginBottom: '0.5rem', background: 'rgba(249, 115, 22, 0.2)', color: '#fdba74' }}>🎙 Speaking • +{maxXP} XP</div>
          <h1 className="heading-md">{data.title}</h1>
          <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{data.description}</p>
        </div>
      </div>

      {mockWarning && (
        <div style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.4)', borderRadius: 'var(--radius-md)', padding: '0.875rem 1rem', marginBottom: '1.25rem', fontSize: '0.85rem', color: '#fbbf24' }}>
          ⚠ <strong>Demo Mode:</strong> Whisper speech recognition is not installed on this server. Audio transcription is unavailable. Please contact your administrator to enable full speaking functionality.
        </div>
      )}

      {globalError && (
        <div style={{ background: 'var(--color-danger-glow)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', marginBottom: '1rem', color: 'var(--color-danger-light)', fontSize: '0.875rem' }}>
          ⚠ {globalError}
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', marginBottom: '2rem' }}>
        {scenarios.map((s, i) => (
          <div key={i} className="card">
            <h3 className="heading-sm" style={{ marginBottom: '0.5rem', color: '#fdba74' }}>Scenario {i + 1}</h3>
            <p style={{ fontWeight: 500, marginBottom: '1.5rem' }}>{s.prompt}</p>

            <div style={{ background: 'var(--color-surface-2)', borderRadius: 'var(--radius-md)' }}>
              {transcribingIndex === i ? (
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                  <span className="spinner" style={{ display: 'inline-block', margin: '0 auto' }} />
                  <p style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>Transcribing with Whisper...</p>
                </div>
              ) : (
                <AudioRecorder
                  onRecordingComplete={(blob) => handleRecordingComplete(blob, i)}
                  label="Press record and reply to the scenario above"
                />
              )}
            </div>

            {/* Per-scenario error */}
            {errors[i] && (
              <div style={{ marginTop: '0.75rem', padding: '0.75rem 1rem', background: 'var(--color-danger-glow)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-md)', color: 'var(--color-danger-light)', fontSize: '0.85rem' }}>
                ⚠ {errors[i]}
              </div>
            )}

            {/* Transcription result */}
            {transcriptions[i] && (
              <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--color-success-light)', marginBottom: '0.25rem', fontWeight: 600 }}>✅ Heard (Whisper STT):</p>
                <p style={{ fontStyle: 'italic' }}>"{transcriptions[i]}"</p>
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
            style={{ background: 'linear-gradient(135deg, #f97316, #c2410c)' }}
          >
            {submitting ? <><span className="spinner" /> Evaluating with AI...</> : '✅ Submit Recordings'}
          </button>
          {!allRecorded && !mockWarning && (
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '0.75rem' }}>
              Record all {scenarios.length} scenario{scenarios.length > 1 ? 's' : ''} to submit
            </p>
          )}
        </div>
      )}

      {result && (
        <ScoreModal
          result={result}
          maxXP={maxXP}
          onNext={() => setShowFeedback(true)}
          onRetry={() => { setResult(null); setTranscriptions({}); setErrors({}); setGlobalError(''); }}
          activityType="speaking"
        />
      )}

      {showFeedback && result && (
        <ActivityFeedback
          result={result}
          activityType="speaking"
          onDismiss={() => { setShowFeedback(false); navigate('/dashboard'); }}
        />
      )}
    </div>
  );
}
