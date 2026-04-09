/**
 * src/pages/activities/SpeakingPage.jsx
 * Dynamic: scenarioContext (3-field), subTasks[], speaking recording, AI scoring.
 */
import React, { useState } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';
import AudioRecorder from '../../components/AudioRecorder.jsx';

export default function SpeakingPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback, submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'speaking' });

  const [recordings, setRecordings] = useState({});
  const [expandedTask, setExpandedTask] = useState(0);
  const [showRubric, setShowRubric] = useState(false);

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const subTasks = data.subTasks || [];
  const scoringRules = data.scoringRules;
  const scenario = data.scenarioContext;
  const baselineTranscript = data.baselineTranscriptSentences || [];
  const allRecorded = subTasks.length === 0 || Object.keys(recordings).length >= Math.min(subTasks.length, 1);

  const handleRecording = (transcript, taskIdx) => {
    setRecordings(r => ({ ...r, [taskIdx]: transcript }));
    setAnswers(a => ({ ...a, [taskIdx]: transcript }));
  };

  const handleSubmit = async () => {
    if (subTasks.length === 0) {
      // Free-speaking without tasks
      const transcript = recordings[0] || '(no recording)';
      const questions = [{
        question_id: 'speaking_free',
        block_type: 'speaking',
        user_answer: transcript,
        correct_answer: data.adminCorrectAnswerSet?.sampleAnswer || '',
        prompt: data.speakingPrompt || data.scenario || '',
      }];
      await submitAnswers(questions);
      return;
    }

    const questions = subTasks.map((task, i) => ({
      question_id: task.taskId || `st_${i}`,
      block_type: 'speaking',
      user_answer: recordings[i] || '(no recording)',
      correct_answer: task.sampleResponse || data.adminCorrectAnswerSet?.sampleAnswer || '',
      prompt: task.taskInstruction || task.prompt || '',
    }));
    await submitAnswers(questions);
  };

  return (
    <div style={{ maxWidth: 820, margin: '0 auto' }}>
      <ActivityHeader label={`🎙 ${label || 'Speaking'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/* Scenario context — 3-field TargetTextBlock */}
      {scenario && (scenario.targetText || scenario.baseTranslation) && (
        <div className="card" style={{ marginBottom: '1.5rem', background: 'rgba(99,102,241,0.05)', border: '1px solid rgba(99,102,241,0.25)' }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-primary-light)', marginBottom: '0.75rem' }}>🎭 Scenario</div>
          <TargetTextBlock data={scenario} size="md" />
        </div>
      )}

      {/* Free text scenario */}
      {data.scenario && !scenario?.targetText && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>Scenario</div>
          <p style={{ fontSize: '0.9rem', lineHeight: 1.7 }}>{data.scenario}</p>
        </div>
      )}

      {/* Scoring rules toggle */}
      {scoringRules && (
        <div style={{ marginBottom: '1.25rem' }}>
          <button className={`btn btn-sm ${showRubric ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowRubric(s => !s)}>
            📊 Scoring Rubric
          </button>
          {showRubric && (
            <div className="card" style={{ marginTop: '0.75rem', display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
              {Object.entries(scoringRules).map(([key, val]) => typeof val === 'number' && (
                <div key={key} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-primary-light)' }}>{val}%</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>{key.replace('Weight', '').replace(/([A-Z])/g, ' $1')}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Sub tasks */}
      {subTasks.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
          {subTasks.map((task, i) => (
            <div key={task.taskId || i} className="card" style={{ border: expandedTask === i ? '1px solid var(--color-primary)' : '1px solid var(--color-border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', cursor: 'pointer' }} onClick={() => setExpandedTask(i)}>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Task {i + 1}: {task.taskInstruction || task.prompt || `Speaking Task ${i + 1}`}</div>
                {recordings[i] && <span style={{ color: 'var(--color-success-light)', fontSize: '0.8rem' }}>✓ Recorded</span>}
              </div>

              {expandedTask === i && (
                <div style={{ marginTop: '1rem' }}>
                  {task.expectedSpeakingPoints?.length > 0 && (
                    <div style={{ marginBottom: '0.75rem', padding: '0.75rem', background: 'var(--color-surface-3)', borderRadius: 'var(--radius-sm)' }}>
                      <div style={{ fontSize: '0.75rem', fontWeight: 700, marginBottom: '0.375rem', color: 'var(--color-text-muted)' }}>Key Points to Cover:</div>
                      {task.expectedSpeakingPoints.map((pt, j) => <div key={j} style={{ fontSize: '0.85rem' }}>• {pt}</div>)}
                    </div>
                  )}
                  {task.sampleResponse && (
                    <div style={{ marginBottom: '0.75rem', fontSize: '0.85rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
                      Sample: "{task.sampleResponse}"
                    </div>
                  )}
                  {recordings[i] ? (
                    <div style={{ padding: '0.75rem', background: 'rgba(16,185,129,0.08)', borderRadius: 'var(--radius-md)' }}>
                      <p style={{ fontSize: '0.8rem', color: 'var(--color-success-light)' }}>🎤 "{recordings[i]}"</p>
                      <button className="btn btn-ghost btn-sm" style={{ marginTop: '0.5rem' }} onClick={() => setRecordings(r => { const n={...r}; delete n[i]; return n; })}>Re-record</button>
                    </div>
                  ) : (
                    <AudioRecorder expectedText={task.sampleResponse || ''} onResult={t => handleRecording(t, i)} />
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        // Free-form speaking (no tasks defined by admin)
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <p style={{ marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>{data.speakingPrompt || 'Speak about the scenario above.'}</p>
          {recordings[0] ? (
            <div style={{ padding: '0.75rem', background: 'rgba(16,185,129,0.08)', borderRadius: 'var(--radius-md)' }}>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-success-light)' }}>🎤 "{recordings[0]}"</p>
              <button className="btn btn-ghost btn-sm" style={{ marginTop: '0.5rem' }} onClick={() => setRecordings({})}>Re-record</button>
            </div>
          ) : (
            <AudioRecorder expectedText={data.adminCorrectAnswerSet?.sampleAnswer || ''} onResult={t => handleRecording(t, 0)} />
          )}
        </div>
      )}

      {/* Baseline transcript reference */}
      {baselineTranscript.length > 0 && (
        <details style={{ marginBottom: '1.5rem' }}>
          <summary style={{ cursor: 'pointer', fontSize: '0.85rem', color: 'var(--color-text-muted)', userSelect: 'none' }}>📄 Model transcript (expand to check)</summary>
          <div className="card" style={{ marginTop: '0.75rem' }}>
            {baselineTranscript.map((line, i) => (
              <div key={i} style={{ marginBottom: '0.75rem' }}><TargetTextBlock data={line} size="sm" /></div>
            ))}
          </div>
        </details>
      )}

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : '✅ Submit Speaking'}
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="speaking" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="speaking" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
