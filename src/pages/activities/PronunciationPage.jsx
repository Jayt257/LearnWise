/**
 * src/pages/activities/PronunciationPage.jsx
 * Renders targetPhrasesOrWords[] — each with 3-field text, phonetic hints,
 * conditional audio players (only real paths), speech recording, scoring.
 */
import React, { useState } from 'react';
import { Volume2 } from 'lucide-react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';
import AudioRecorder from '../../components/AudioRecorder.jsx';

export default function PronunciationPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback, submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'pronunciation' });

  const [currentIdx, setCurrentIdx] = useState(0);
  const [recordings, setRecordings] = useState({}); // idx → transcript

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const phrases = data.targetPhrasesOrWords || [];
  const total = phrases.length;
  const current = phrases[currentIdx];
  const recordedCount = Object.keys(recordings).length;
  const allRecorded = recordedCount === total && total > 0;

  const handleRecordingDone = (transcript, idx) => {
    setRecordings(r => ({ ...r, [idx]: transcript }));
    setAnswers(a => ({ ...a, [idx]: transcript }));
  };

  const handleSubmit = async () => {
    if (total === 0) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: 100, passed: true,
        feedback: 'Pronunciation reviewed! Keep practicing. 🗣', suggestion: '',
        question_results: [],
      });
      return;
    }
    const questions = phrases.map((p, i) => ({
      question_id: p.itemId || `pr_${i}`,
      block_type: 'pronunciation',
      user_answer: recordings[i] || '(no recording)',
      correct_answer: data.adminCorrectAnswerSet?.exactCorrectTranscript
        || data.adminCorrectAnswerSet?.acceptedVariants?.[0]
        || p.targetText || '',
      prompt: `Pronounce: ${p.targetText} (${p.transliteration})`,
    }));
    await submitAnswers(questions);
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <ActivityHeader label={`🗣 ${label || 'Pronunciation'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/* Instructions */}
      {data.instructions && (
        <div style={{ background: 'var(--color-primary-glow)', border: '1px solid var(--color-primary)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', marginBottom: '1.5rem', fontSize: '0.85rem' }}>
          💡 {data.instructions}
        </div>
      )}

      {/* Progress dots */}
      {total > 1 && (
        <div style={{ display: 'flex', gap: '0.375rem', justifyContent: 'center', marginBottom: '1.5rem' }}>
          {phrases.map((_, i) => (
            <div key={i} onClick={() => setCurrentIdx(i)} title={`Item ${i + 1}`}
              style={{ width: 10, height: 10, borderRadius: '50%', cursor: 'pointer', transition: 'all 0.2s',
                background: recordings[i] ? 'var(--color-success-light)' : i === currentIdx ? 'var(--color-primary-light)' : 'var(--color-border)' }} />
          ))}
        </div>
      )}

      {current && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <TargetTextBlock data={current} size="lg" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'flex-end' }}>
              {/* Native audio — only if real path */}
              {current.nativeAudioRef && !current.nativeAudioRef.includes('dummy') && (
                <AudioPlayer audioUrl={current.nativeAudioRef} label="Native Speed" />
              )}
              {current.slowAudioRef && !current.slowAudioRef.includes('dummy') && (
                <AudioPlayer audioUrl={current.slowAudioRef} label="Slow Speed" />
              )}
            </div>
          </div>

          {/* Phonetic details */}
          {(current.phoneticHint || current.syllableSplit) && (
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', padding: '0.75rem', background: 'var(--color-surface-3)', borderRadius: 'var(--radius-sm)', flexWrap: 'wrap' }}>
              {current.phoneticHint && (
                <div><div style={{ fontSize: '0.65rem', color: 'var(--color-text-dim)', textTransform: 'uppercase' }}>Phonetic Hint</div>
                  <div style={{ fontSize: '0.875rem', fontStyle: 'italic', color: 'var(--color-secondary-light)' }}>{current.phoneticHint}</div></div>
              )}
              {current.syllableSplit && (
                <div><div style={{ fontSize: '0.65rem', color: 'var(--color-text-dim)', textTransform: 'uppercase' }}>Syllable Split</div>
                  <div style={{ fontSize: '0.875rem', fontFamily: 'monospace', color: 'var(--color-accent-light)' }}>{current.syllableSplit}</div></div>
              )}
            </div>
          )}

          {/* Common mispronunciation warning */}
          {current.commonMispronunciation && (
            <div style={{ marginTop: '0.75rem', padding: '0.625rem', background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-danger-light)' }}>⚠️ Common mistake: {current.commonMispronunciation}</span>
            </div>
          )}

          {/* Speech Recorder - includes Whisper transcript + audio playback in review state */}
          <div style={{ marginTop: '1.25rem' }}>
            <AudioRecorder
              key={currentIdx} /* remount per phrase so state resets */
              label={`Record phrase ${currentIdx + 1}: "${current.transliteration || current.targetText}"`}
              expectedText={current.transliteration || current.targetText}
              onResult={(t) => {
                handleRecordingDone(t, currentIdx);
                // Auto advance to next phrase after a short delay
                if (currentIdx < total - 1) {
                  setTimeout(() => setCurrentIdx(i => i + 1), 800);
                }
              }}
            />
          </div>
        </div>
      )}

      {/* Navigation between phrases */}
      {total > 1 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <button className="btn btn-ghost" disabled={currentIdx === 0} onClick={() => setCurrentIdx(i => i - 1)}>← Previous</button>
          <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', alignSelf: 'center' }}>{currentIdx + 1} / {total}</span>
          <button className="btn btn-ghost" disabled={currentIdx === total - 1} onClick={() => setCurrentIdx(i => i + 1)}>Next →</button>
        </div>
      )}

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit}
            disabled={submitting || (total > 0 && recordedCount === 0)}>
            {submitting
              ? <><span className="spinner" /> Evaluating...</>
              : recordedCount === 0 && total > 0
                ? `Record at least 1 of ${total} to submit`
                : recordedCount < total && total > 0
                  ? `Submit (${recordedCount}/${total} recorded)`
                  : '✅ Submit Pronunciation'
            }
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="pronunciation" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="pronunciation" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
