/
  src/pages/activities/WritingPage.jsx
  Fully dynamic: writingPrompt, wordBank[], referenceHints[], evaluationCriteria[].
 /
import React, { useState } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

export default function WritingPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback, submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'writing' });

  const [showHints, setShowHints] = useState(false);
  const [showExample, setShowExample] = useState(false);
  const userResponse = answers.response || '';
  const wordCount = userResponse.trim().split(/\s+/).filter(Boolean).length;

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const minWords = data.minimumWordCount || ;
  const maxWords = data.maximumWordCount || ;
  const wordBank = data.wordBank || [];
  const hints = data.referenceHints || [];
  const criteria = data.evaluationCriteria || [];
  const examples = data.modelExampleOutputs || [];

  const handleSubmit = async () => {
    const questions = [{
      question_id: 'writing_response',
      block_type: 'writing',
      user_answer: userResponse,
      correct_answer: data.adminCorrectAnswerSet?.sampleAnswer || '',
      prompt: data.writingPrompt || '',
    }];
    await submitAnswers(questions);
  };

  const canSubmit = userResponse.trim().length >  && (minWords ===  || wordCount >= minWords);

  return (
    <div style={{ maxWidth: , margin: ' auto' }}>
      <ActivityHeader label={` ${label || 'Writing'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/ Prompt /}
      <div className="card" style={{ marginBottom: '.rem', border: 'px solid rgba(,,,.)', background: 'rgba(,,,.)' }}>
        <div style={{ fontSize: '.rem', fontWeight: , textTransform: 'uppercase', color: 'var(--color-success-light)', marginBottom: '.rem' }}>Writing Prompt</div>
        <p style={{ fontSize: 'rem', fontWeight: , lineHeight: . }}>{data.writingPrompt}</p>
        {data.promptGoal && <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)', marginTop: '.rem' }}> Goal: {data.promptGoal}</p>}
        {data.expectedWritingType && <span style={{ fontSize: '.rem', background: 'rgba(,,,.)', color: 'var(--color-success-light)', borderRadius: 'var(--radius-full)', padding: '.rem .rem', marginTop: '.rem', display: 'inline-block' }}>{data.expectedWritingType}</span>}
      </div>

      {/ Word Count limits /}
      {(minWords >  || maxWords < ) && (
        <div style={{ fontSize: '.rem', color: 'var(--color-text-muted)', marginBottom: 'rem' }}>
           Length: {minWords >  ? `${minWords}–` : ''}{maxWords} words
        </div>
      )}

      {/ Word Bank — dynamic, only shows if admin added words /}
      {wordBank.length >  && (
        <div style={{ marginBottom: '.rem' }}>
          <div style={{ fontSize: '.rem', fontWeight: , color: 'var(--color-text-muted)', marginBottom: '.rem' }}> Word Bank:</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '.rem' }}>
            {wordBank.map((item, i) => (
              <div key={i} style={{ padding: '.rem .rem', background: 'var(--color-surface-)', border: 'px solid var(--color-border)', borderRadius: 'var(--radius-full)', cursor: 'help' }}
                title={`${item.transliteration || ''} — ${item.baseTranslation || ''}`}>
                <TargetTextBlock data={item} size="sm" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/ Textarea /}
      <div style={{ marginBottom: '.rem' }}>
        <textarea
          className="form-input"
          rows={}
          style={{ resize: 'vertical', minHeight: , fontFamily: 'inherit', fontSize: '.rem', lineHeight: . }}
          placeholder={`Write your ${data.expectedWritingType || 'response'} here...`}
          value={userResponse}
          onChange={e => setAnswers(a => ({ ...a, response: e.target.value }))}
          disabled={!!result}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '.rem', fontSize: '.rem', color: wordCount < minWords && minWords >  ? 'var(--color-danger-light)' : 'var(--color-text-muted)' }}>
          <span>{wordCount} word{wordCount !==  ? 's' : ''}</span>
          {minWords >  && <span>Minimum: {minWords} words</span>}
        </div>
      </div>

      {/ Hints & Example toggles /}
      <div style={{ display: 'flex', gap: '.rem', marginBottom: '.rem', flexWrap: 'wrap' }}>
        {hints.length >  && <button className={`btn btn-sm ${showHints ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowHints(s => !s)}> Hints ({hints.length})</button>}
        {examples.length >  && <button className={`btn btn-sm ${showExample ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowExample(s => !s)}> Example</button>}
      </div>

      {showHints && hints.length >  && (
        <div className="card" style={{ marginBottom: '.rem' }}>
          <h style={{ fontSize: '.rem', fontWeight: , marginBottom: '.rem', color: 'var(--color-accent-light)' }}> Reference Hints</h>
          {hints.map((h, i) => (
            <div key={i} style={{ marginBottom: '.rem', fontSize: '.rem' }}>
              {typeof h === 'string' ? h : <TargetTextBlock data={h} size="sm" />}
            </div>
          ))}
        </div>
      )}

      {showExample && examples.length >  && (
        <div className="card" style={{ marginBottom: '.rem', border: 'px solid rgba(,,,.)', background: 'rgba(,,,.)' }}>
          <h style={{ fontSize: '.rem', fontWeight: , marginBottom: '.rem', color: 'var(--color-primary-light)' }}> Example Response</h>
          {examples.slice(, ).map((ex, i) => (
            <div key={i}><p style={{ fontSize: '.rem', whiteSpace: 'pre-line', lineHeight: . }}>{typeof ex === 'string' ? ex : ex.text || ex.targetText || JSON.stringify(ex)}</p></div>
          ))}
        </div>
      )}

      {/ Evaluation Criteria /}
      {criteria.length >  && (
        <div className="card" style={{ marginBottom: '.rem' }}>
          <h style={{ fontSize: '.rem', fontWeight: , marginBottom: '.rem' }}> How you'll be scored:</h>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '.rem' }}>
            {criteria.map((c, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '.rem' }}>
                <span>{c.criterion}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '.rem' }}>
                  <div style={{ width: , height: , background: 'var(--color-border)', borderRadius: , overflow: 'hidden' }}>
                    <div style={{ width: `${c.weight}%`, height: '%', background: 'var(--color-primary-light)', borderRadius:  }} />
                  </div>
                  <span style={{ color: 'var(--color-primary-light)', fontWeight: , minWidth:  }}>{c.weight}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting || !canSubmit}>
            {submitting ? <><span className="spinner" /> Evaluating with AI...</> : !canSubmit ? `Write at least ${minWords || } words` : ' Submit Writing'}
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="writing" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="writing" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
