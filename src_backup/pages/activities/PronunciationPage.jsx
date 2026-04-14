/
  src/pages/activities/PronunciationPage.jsx
  Renders targetPhrasesOrWords[] — each with -field text, phonetic hints,
  conditional audio players (only real paths), speech recording, scoring.
 /
import React, { useState } from 'react';
import { Volume } from 'lucide-react';
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

  const [currentIdx, setCurrentIdx] = useState();
  const [recordings, setRecordings] = useState({}); // idx → transcript

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const phrases = data.targetPhrasesOrWords || [];
  const total = phrases.length;
  const current = phrases[currentIdx];
  const recordedCount = Object.keys(recordings).length;
  const allRecorded = recordedCount === total && total > ;

  const handleRecordingDone = (transcript, idx) => {
    setRecordings(r => ({ ...r, [idx]: transcript }));
    setAnswers(a => ({ ...a, [idx]: transcript }));
  };

  const handleSubmit = async () => {
    if (total === ) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: , passed: true,
        feedback: 'Pronunciation reviewed! Keep practicing. ', suggestion: '',
        question_results: [],
      });
      return;
    }
    const questions = phrases.map((p, i) => ({
      question_id: p.itemId || `pr_${i}`,
      block_type: 'pronunciation',
      user_answer: recordings[i] || '(no recording)',
      correct_answer: data.adminCorrectAnswerSet?.exactCorrectTranscript
        || data.adminCorrectAnswerSet?.acceptedVariants?.[]
        || p.targetText || '',
      prompt: `Pronounce: ${p.targetText} (${p.transliteration})`,
    }));
    await submitAnswers(questions);
  };

  return (
    <div style={{ maxWidth: , margin: ' auto' }}>
      <ActivityHeader label={` ${label || 'Pronunciation'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/ Instructions /}
      {data.instructions && (
        <div style={{ background: 'var(--color-primary-glow)', border: 'px solid var(--color-primary)', borderRadius: 'var(--radius-md)', padding: '.rem rem', marginBottom: '.rem', fontSize: '.rem' }}>
           {data.instructions}
        </div>
      )}

      {/ Progress dots /}
      {total >  && (
        <div style={{ display: 'flex', gap: '.rem', justifyContent: 'center', marginBottom: '.rem' }}>
          {phrases.map((_, i) => (
            <div key={i} onClick={() => setCurrentIdx(i)} title={`Item ${i + }`}
              style={{ width: , height: , borderRadius: '%', cursor: 'pointer', transition: 'all .s',
                background: recordings[i] ? 'var(--color-success-light)' : i === currentIdx ? 'var(--color-primary-light)' : 'var(--color-border)' }} />
          ))}
        </div>
      )}

      {current && (
        <div className="card" style={{ marginBottom: '.rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'rem' }}>
            <TargetTextBlock data={current} size="lg" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '.rem', alignItems: 'flex-end' }}>
              {/ Native audio — only if real path /}
              {current.nativeAudioRef && !current.nativeAudioRef.includes('dummy') && (
                <AudioPlayer audioUrl={current.nativeAudioRef} label="Native Speed" />
              )}
              {current.slowAudioRef && !current.slowAudioRef.includes('dummy') && (
                <AudioPlayer audioUrl={current.slowAudioRef} label="Slow Speed" />
              )}
            </div>
          </div>

          {/ Phonetic details /}
          {(current.phoneticHint || current.syllableSplit) && (
            <div style={{ display: 'flex', gap: 'rem', marginTop: 'rem', padding: '.rem', background: 'var(--color-surface-)', borderRadius: 'var(--radius-sm)', flexWrap: 'wrap' }}>
              {current.phoneticHint && (
                <div><div style={{ fontSize: '.rem', color: 'var(--color-text-dim)', textTransform: 'uppercase' }}>Phonetic Hint</div>
                  <div style={{ fontSize: '.rem', fontStyle: 'italic', color: 'var(--color-secondary-light)' }}>{current.phoneticHint}</div></div>
              )}
              {current.syllableSplit && (
                <div><div style={{ fontSize: '.rem', color: 'var(--color-text-dim)', textTransform: 'uppercase' }}>Syllable Split</div>
                  <div style={{ fontSize: '.rem', fontFamily: 'monospace', color: 'var(--color-accent-light)' }}>{current.syllableSplit}</div></div>
              )}
            </div>
          )}

          {/ Common mispronunciation warning /}
          {current.commonMispronunciation && (
            <div style={{ marginTop: '.rem', padding: '.rem', background: 'rgba(,,,.)', border: 'px solid rgba(,,,.)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '.rem', color: 'var(--color-danger-light)' }}> Common mistake: {current.commonMispronunciation}</span>
            </div>
          )}

          {/ Speech Recorder - includes Whisper transcript + audio playback in review state /}
          <div style={{ marginTop: '.rem' }}>
            <AudioRecorder
              key={currentIdx} / remount per phrase so state resets /
              label={`Record phrase ${currentIdx + }: "${current.transliteration || current.targetText}"`}
              expectedText={current.transliteration || current.targetText}
              onResult={(t) => {
                handleRecordingDone(t, currentIdx);
                // Auto advance to next phrase after a short delay
                if (currentIdx < total - ) {
                  setTimeout(() => setCurrentIdx(i => i + ), );
                }
              }}
            />
          </div>
        </div>
      )}

      {/ Navigation between phrases /}
      {total >  && (
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '.rem', marginBottom: '.rem' }}>
          <button className="btn btn-ghost" disabled={currentIdx === } onClick={() => setCurrentIdx(i => i - )}>← Previous</button>
          <span style={{ fontSize: '.rem', color: 'var(--color-text-muted)', alignSelf: 'center' }}>{currentIdx + } / {total}</span>
          <button className="btn btn-ghost" disabled={currentIdx === total - } onClick={() => setCurrentIdx(i => i + )}>Next →</button>
        </div>
      )}

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit}
            disabled={submitting || (total >  && recordedCount === )}>
            {submitting
              ? <><span className="spinner" /> Evaluating...</>
              : recordedCount ===  && total > 
                ? `Record at least  of ${total} to submit`
                : recordedCount < total && total > 
                  ? `Submit (${recordedCount}/${total} recorded)`
                  : ' Submit Pronunciation'
            }
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="pronunciation" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="pronunciation" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
