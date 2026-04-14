/
  src/pages/activities/SpeakingPage.jsx
  Dynamic: scenarioContext (-field), subTasks[], speaking recording, AI scoring.
 
  Fix Bug : subTasks[].sampleResponse is an object {targetText, transliteration, baseTranslation}
              — NOT a string. Render it as TargetTextBlock, pass transliteration to AudioRecorder.
 /
import React, { useState } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';
import AudioRecorder from '../../components/AudioRecorder.jsx';

/
  Extract a plain string from sampleResponse which may be:
    - a string: "Ohayou gozaimasu"
    - an object: { targetText: "おはよう", transliteration: "Ohayou gozaimasu", baseTranslation: "..." }
  Returns the romanization (transliteration) or targetText for Groq evaluation.
 /
function getSampleText(sampleResponse) {
  if (!sampleResponse) return '';
  if (typeof sampleResponse === 'string') return sampleResponse;
  // Prefer transliteration for Groq (ASCII-safe, model understands it better)
  return sampleResponse.transliteration || sampleResponse.targetText || '';
}

export default function SpeakingPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback, submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'speaking' });

  const [recordings, setRecordings] = useState({});
  const [expandedTask, setExpandedTask] = useState();
  const [showRubric, setShowRubric] = useState(false);

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const subTasks = data.subTasks || [];
  const scoringRules = data.scoringRules;
  const scenario = data.scenarioContext;
  const baselineTranscript = data.baselineTranscriptSentences || [];

  const handleRecording = (transcript, taskIdx) => {
    setRecordings(r => ({ ...r, [taskIdx]: transcript }));
    setAnswers(a => ({ ...a, [taskIdx]: transcript }));
  };

  const handleSubmit = async () => {
    if (subTasks.length === ) {
      const transcript = recordings[] || '(no recording)';
      const questions = [{
        question_id: 'speaking_free',
        block_type: 'speaking',
        user_answer: transcript,
        // FIX: use getSampleText to extract string from object
        correct_answer: getSampleText(data.adminCorrectAnswerSet?.sampleAnswer) || '',
        prompt: data.speakingPrompt || data.scenario || '',
      }];
      await submitAnswers(questions);
      return;
    }

    const questions = subTasks.map((task, i) => ({
      question_id: task.taskId || task.subTaskId || `st_${i}`,
      block_type: 'speaking',
      user_answer: recordings[i] || '(no recording)',
      // FIX: sampleResponse may be an object — extract transliteration/targetText string
      correct_answer: getSampleText(task.sampleResponse) || getSampleText(data.adminCorrectAnswerSet?.sampleAnswer) || '',
      prompt: task.taskInstruction || task.prompt || '',
    }));
    await submitAnswers(questions);
  };

  return (
    <div style={{ maxWidth: , margin: ' auto' }}>
      <ActivityHeader label={` ${label || 'Speaking'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/ Scenario context — -field TargetTextBlock /}
      {scenario && (scenario.targetText || scenario.baseTranslation) && (
        <div className="card" style={{ marginBottom: '.rem', background: 'rgba(,,,.)', border: 'px solid rgba(,,,.)' }}>
          <div style={{ fontSize: '.rem', fontWeight: , textTransform: 'uppercase', color: 'var(--color-primary-light)', marginBottom: '.rem' }}> Scenario</div>
          <TargetTextBlock data={scenario} size="md" />
        </div>
      )}

      {/ Free text scenario /}
      {data.scenario && !scenario?.targetText && (
        <div className="card" style={{ marginBottom: '.rem' }}>
          <div style={{ fontSize: '.rem', fontWeight: , textTransform: 'uppercase', color: 'var(--color-text-muted)', marginBottom: '.rem' }}>Scenario</div>
          <p style={{ fontSize: '.rem', lineHeight: . }}>{data.scenario}</p>
        </div>
      )}

      {/ Scoring rules toggle /}
      {scoringRules && (
        <div style={{ marginBottom: '.rem' }}>
          <button className={`btn btn-sm ${showRubric ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowRubric(s => !s)}>
             Scoring Rubric
          </button>
          {showRubric && (
            <div className="card" style={{ marginTop: '.rem', display: 'flex', gap: '.rem', flexWrap: 'wrap' }}>
              {Object.entries(scoringRules).map(([key, val]) => typeof val === 'number' && (
                <div key={key} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '.rem', fontWeight: , color: 'var(--color-primary-light)' }}>{val}%</div>
                  <div style={{ fontSize: '.rem', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>{key.replace('Weight', '').replace(/([A-Z])/g, ' $')}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/ Sub tasks /}
      {subTasks.length >  ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'rem', marginBottom: '.rem' }}>
          {subTasks.map((task, i) => {
            const sampleStr = getSampleText(task.sampleResponse);
            const sampleIsObj = task.sampleResponse && typeof task.sampleResponse === 'object';
            return (
              <div key={task.taskId || task.subTaskId || i} className="card"
                style={{ border: expandedTask === i ? 'px solid var(--color-primary)' : 'px solid var(--color-border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', cursor: 'pointer' }} onClick={() => setExpandedTask(i)}>
                  <div style={{ fontWeight: , fontSize: '.rem' }}>
                    Task {i + }: {task.taskInstruction || task.prompt || `Speaking Task ${i + }`}
                  </div>
                  {recordings[i] && <span style={{ color: 'var(--color-success-light)', fontSize: '.rem' }}>✓ Recorded</span>}
                </div>

                {expandedTask === i && (
                  <div style={{ marginTop: 'rem' }}>
                    {task.expectedSpeakingPoints?.length >  && (
                      <div style={{ marginBottom: '.rem', padding: '.rem', background: 'var(--color-surface-)', borderRadius: 'var(--radius-sm)' }}>
                        <div style={{ fontSize: '.rem', fontWeight: , marginBottom: '.rem', color: 'var(--color-text-muted)' }}>Key Points to Cover:</div>
                        {task.expectedSpeakingPoints.map((pt, j) => <div key={j} style={{ fontSize: '.rem' }}>• {pt}</div>)}
                      </div>
                    )}

                    {/ FIX: render sampleResponse as TargetTextBlock if it's an object /}
                    {task.sampleResponse && (
                      <div style={{ marginBottom: '.rem', padding: '.rem', background: 'rgba(,,,.)', borderRadius: 'var(--radius-sm)', border: 'px solid rgba(,,,.)' }}>
                        <div style={{ fontSize: '.rem', fontWeight: , color: 'var(--color-text-muted)', marginBottom: '.rem', textTransform: 'uppercase' }}>Sample Response</div>
                        {sampleIsObj
                          ? <TargetTextBlock data={task.sampleResponse} size="sm" />
                          : <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>"{sampleStr}"</p>
                        }
                      </div>
                    )}

                    {/ AudioRecorder handles review/playback/re-record internally /}
                    <AudioRecorder
                      key={`task-${i}`}
                      label={`Record Task ${i + }`}
                      expectedText={sampleStr}
                      onResult={t => handleRecording(t, i)}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="card" style={{ marginBottom: '.rem' }}>
          <p style={{ marginBottom: 'rem', fontSize: '.rem', color: 'var(--color-text-muted)' }}>{data.speakingPrompt || 'Speak about the scenario above.'}</p>
          {/ AudioRecorder handles review/playback/re-record internally /}
          <AudioRecorder
            key="free-speaking"
            label="Record your spoken response"
            expectedText={getSampleText(data.adminCorrectAnswerSet?.sampleAnswer)}
            onResult={t => handleRecording(t, )}
          />
        </div>
      )}

      {/ Baseline transcript reference /}
      {baselineTranscript.length >  && (
        <details style={{ marginBottom: '.rem' }}>
          <summary style={{ cursor: 'pointer', fontSize: '.rem', color: 'var(--color-text-muted)', userSelect: 'none' }}> Model transcript (expand to check)</summary>
          <div className="card" style={{ marginTop: '.rem' }}>
            {baselineTranscript.map((line, i) => (
              <div key={i} style={{ marginBottom: '.rem' }}><TargetTextBlock data={line} size="sm" /></div>
            ))}
          </div>
        </details>
      )}

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : ' Submit Speaking'}
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="speaking" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="speaking" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
