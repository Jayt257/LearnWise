/**
 * src/pages/activities/WritingPage.jsx
 * Fully dynamic: writingPrompt, wordBank[], referenceHints[], evaluationCriteria[].
 */
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

  const minWords = data.minimumWordCount || 0;
  const maxWords = data.maximumWordCount || 500;
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

  const canSubmit = userResponse.trim().length > 10 && (minWords === 0 || wordCount >= minWords);

  return (
    <div style={{ maxWidth: 820, margin: '0 auto' }}>
      <ActivityHeader label={`✍ ${label || 'Writing'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/* Prompt */}
      <div className="card" style={{ marginBottom: '1.25rem', border: '1px solid rgba(16,185,129,0.3)', background: 'rgba(16,185,129,0.04)' }}>
        <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-success-light)', marginBottom: '0.5rem' }}>Writing Prompt</div>
        <p style={{ fontSize: '1rem', fontWeight: 600, lineHeight: 1.7 }}>{data.writingPrompt}</p>
        {data.promptGoal && <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginTop: '0.5rem' }}>🎯 Goal: {data.promptGoal}</p>}
        {data.expectedWritingType && <span style={{ fontSize: '0.75rem', background: 'rgba(16,185,129,0.12)', color: 'var(--color-success-light)', borderRadius: 'var(--radius-full)', padding: '0.15rem 0.6rem', marginTop: '0.25rem', display: 'inline-block' }}>{data.expectedWritingType}</span>}
      </div>

      {/* Word Count limits */}
      {(minWords > 0 || maxWords < 500) && (
        <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
          📝 Length: {minWords > 0 ? `${minWords}–` : ''}{maxWords} words
        </div>
      )}

      {/* Word Bank — dynamic, only shows if admin added words */}
      {wordBank.length > 0 && (
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>💡 Word Bank:</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {wordBank.map((item, i) => (
              <div key={i} style={{ padding: '0.375rem 0.75rem', background: 'var(--color-surface-2)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-full)', cursor: 'help' }}
                title={`${item.transliteration || ''} — ${item.baseTranslation || ''}`}>
                <TargetTextBlock data={item} size="sm" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Textarea */}
      <div style={{ marginBottom: '1.5rem' }}>
        <textarea
          className="form-input"
          rows={8}
          style={{ resize: 'vertical', minHeight: 180, fontFamily: 'inherit', fontSize: '0.95rem', lineHeight: 1.7 }}
          placeholder={`Write your ${data.expectedWritingType || 'response'} here...`}
          value={userResponse}
          onChange={e => setAnswers(a => ({ ...a, response: e.target.value }))}
          disabled={!!result}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.375rem', fontSize: '0.75rem', color: wordCount < minWords && minWords > 0 ? 'var(--color-danger-light)' : 'var(--color-text-muted)' }}>
          <span>{wordCount} word{wordCount !== 1 ? 's' : ''}</span>
          {minWords > 0 && <span>Minimum: {minWords} words</span>}
        </div>
      </div>

      {/* Hints & Example toggles */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {hints.length > 0 && <button className={`btn btn-sm ${showHints ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowHints(s => !s)}>💡 Hints ({hints.length})</button>}
        {examples.length > 0 && <button className={`btn btn-sm ${showExample ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowExample(s => !s)}>📋 Example</button>}
      </div>

      {showHints && hints.length > 0 && (
        <div className="card" style={{ marginBottom: '1.25rem' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--color-accent-light)' }}>💡 Reference Hints</h4>
          {hints.map((h, i) => (
            <div key={i} style={{ marginBottom: '0.5rem', fontSize: '0.875rem' }}>
              {typeof h === 'string' ? h : <TargetTextBlock data={h} size="sm" />}
            </div>
          ))}
        </div>
      )}

      {showExample && examples.length > 0 && (
        <div className="card" style={{ marginBottom: '1.25rem', border: '1px solid rgba(99,102,241,0.3)', background: 'rgba(99,102,241,0.03)' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--color-primary-light)' }}>📋 Example Response</h4>
          {examples.slice(0, 1).map((ex, i) => (
            <div key={i}><p style={{ fontSize: '0.875rem', whiteSpace: 'pre-line', lineHeight: 1.7 }}>{typeof ex === 'string' ? ex : ex.text || ex.targetText || JSON.stringify(ex)}</p></div>
          ))}
        </div>
      )}

      {/* Evaluation Criteria */}
      {criteria.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem' }}>📊 How you'll be scored:</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {criteria.map((c, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                <span>{c.criterion}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{ width: 80, height: 6, background: 'var(--color-border)', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{ width: `${c.weight}%`, height: '100%', background: 'var(--color-primary-light)', borderRadius: 3 }} />
                  </div>
                  <span style={{ color: 'var(--color-primary-light)', fontWeight: 600, minWidth: 32 }}>{c.weight}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting || !canSubmit}>
            {submitting ? <><span className="spinner" /> Evaluating with AI...</> : !canSubmit ? `Write at least ${minWords || 10} words` : '✅ Submit Writing'}
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="writing" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="writing" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
