/
  src/pages/activities/ListeningPage.jsx
  Dynamic: audioAssets (real path only), audioTranscriptSentences[] (with toggle),
  questionSet[] (multiple question types), replay controls.
 /
import React, { useState, useRef } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import DynamicQuiz from '../../components/DynamicQuiz.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

export default function ListeningPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback, submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'listening' });

  const [showTranscript, setShowTranscript] = useState(false);

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const audio = data.audioAssets || {};
  const hasRealAudio = audio.nativeAudio && !audio.nativeAudio.includes('dummy');
  const hasRealSampleAudio = audio.sampleAudio && !audio.sampleAudio.includes('dummy');
  const transcript = data.audioTranscriptSentences || [];
  const questions = data.questionSet || [];
  const replayAllowed = data.replayAllowed !== false;
  const slowAllowed = data.slowPlaybackAllowed === true;

  const handleSubmit = async () => {
    if (questions.length === ) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: , passed: true,
        feedback: 'Great listening session! ', suggestion: 'Try to recall key words from the audio.',
        question_results: [],
      });
      return;
    }
    const qs = questions.map((q, i) => {
      const userAns = answers[i];
      return {
        question_id: q.questionId || `lq_${i}`,
        block_type: q.questionType || 'multiple_choice',
        user_answer: typeof userAns === 'number' ? (q.options?.[userAns] || '') : (userAns || ''),
        correct_answer: data.adminCorrectAnswerSet?.correctAnswers?.[q.questionId] || q.correctAnswer || '',
        prompt: q.questionText || '',
      };
    });
    await submitAnswers(qs);
  };

  return (
    <div style={{ maxWidth: , margin: ' auto' }}>
      <ActivityHeader label={` ${label || 'Listening'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/ Scenario context /}
      {data.audioScenario && (
        <div style={{ background: 'var(--color-surface-)', border: 'px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: 'rem', marginBottom: '.rem' }}>
          <div style={{ fontSize: '.rem', fontWeight: , textTransform: 'uppercase', color: 'var(--color-text-dim)', marginBottom: '.rem' }}>Scenario</div>
          <p style={{ fontSize: '.rem' }}>{data.audioScenario}</p>
        </div>
      )}

      {/ Audio player — only shows if real path /}
      <div className="card" style={{ marginBottom: '.rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '.rem' }}>
          <div>
            <div style={{ fontWeight: , marginBottom: '.rem' }}> Audio Clip</div>
            {data.audioDuration && <div style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}>Duration: ~{data.audioDuration}s</div>}
          </div>
          <div style={{ display: 'flex', gap: '.rem', flexWrap: 'wrap' }}>
            {hasRealAudio ? (
              <>
                <AudioPlayer audioUrl={audio.nativeAudio} label={replayAllowed ? 'Play (replay OK)' : 'Play (once)'} />
                {slowAllowed && audio.slowAudio && !audio.slowAudio.includes('dummy') && (
                  <AudioPlayer audioUrl={audio.slowAudio} label="Slow Speed" />
                )}
              </>
            ) : hasRealSampleAudio ? (
              <AudioPlayer audioUrl={audio.sampleAudio} label="Play" />
            ) : (
              <div style={{ padding: '.rem .rem', background: 'var(--color-surface-)', borderRadius: 'var(--radius-md)', fontSize: '.rem', color: 'var(--color-text-dim)' }}>
                 Audio not available — use transcript to complete activity
              </div>
            )}
          </div>
        </div>

        {/ Transcript toggle /}
        {transcript.length >  && (
          <button className={`btn btn-sm ${showTranscript ? 'btn-primary' : 'btn-ghost'}`}
            style={{ marginTop: '.rem' }} onClick={() => setShowTranscript(s => !s)}>
            {showTranscript ? ' Hide Transcript' : ' Show Transcript'}
          </button>
        )}
      </div>

      {/ Transcript /}
      {showTranscript && transcript.length >  && (
        <div className="card" style={{ marginBottom: '.rem' }}>
          <h className="heading-sm" style={{ marginBottom: 'rem' }}> Transcript</h>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'rem' }}>
            {transcript.map((line, i) => (
              <div key={i} style={{ borderLeft: 'px solid var(--color-secondary)', paddingLeft: '.rem' }}>
                <TargetTextBlock data={line} size="sm" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/ Questions /}
      {questions.length >  && (
        <div style={{ marginBottom: '.rem' }}>
          <h className="heading-sm" style={{ marginBottom: 'rem', color: 'var(--color-text-muted)' }}>
             Comprehension Questions
          </h>
          {questions.map((q, i) => (
            <DynamicQuiz key={q.questionId || i} question={{ ...q, questionType: q.questionType || 'mcq', options: q.options }} index={i}
              answer={answers[i]} onChange={v => setAnswers(p => ({ ...p, [i]: v }))}
              showResult={!!result} />
          ))}
        </div>
      )}

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : questions.length ===  ? ' Mark Complete' : ' Submit Answers'}
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="listening" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="listening" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
