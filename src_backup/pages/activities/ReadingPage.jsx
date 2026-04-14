/
  src/pages/activities/ReadingPage.jsx
  Fully dynamic: readingText, sentenceSupportPairs[], glossary[], comprehensionQuestions[].
  Toggle between reading-only view and sentence-by-sentence support.
 /
import React, { useState } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import DynamicQuiz from '../../components/DynamicQuiz.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

export default function ReadingPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback, submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'reading' });

  const [showSupport, setShowSupport] = useState(false);
  const [showGlossary, setShowGlossary] = useState(false);

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const readingText = data.textInTargetLanguage || data.readingText || '';
  const supportText = data.baseLanguageSupportText;
  const sentencePairs = data.sentenceSupportPairs || [];
  const glossary = data.glossary || [];
  const questions = data.comprehensionQuestions || [];

  const handleSubmit = async () => {
    if (questions.length === ) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: , passed: true,
        feedback: 'Excellent reading! ', suggestion: 'Try to recall the main points from memory.',
        question_results: [],
      });
      return;
    }
    const qs = questions.map((q, i) => ({
      question_id: q.questionId || `rq_${i}`,
      block_type: q.questionType || 'short_answer',
      user_answer: typeof answers[i] === 'number' ? (q.options?.[answers[i]] || answers[i]) : (answers[i] || ''),
      correct_answer: q.correctAnswer || q.options?.[q.correct] || '',
      prompt: q.questionText || '',
    }));
    await submitAnswers(qs);
  };

  return (
    <div style={{ maxWidth: , margin: ' auto' }}>
      <ActivityHeader label={` ${label || 'Reading'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/ Toolbar /}
      <div style={{ display: 'flex', gap: '.rem', marginBottom: '.rem', flexWrap: 'wrap' }}>
        {sentencePairs.length >  && (
          <button className={`btn btn-sm ${showSupport ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowSupport(s => !s)}>
            {showSupport ? ' Hide Support' : ' Show Support'}
          </button>
        )}
        {glossary.length >  && (
          <button className={`btn btn-sm ${showGlossary ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowGlossary(s => !s)}>
             Glossary ({glossary.length})
          </button>
        )}
        {data.audioAssets?.nativeAudio && !data.audioAssets.nativeAudio.includes('dummy') && (
          <AudioPlayer audioUrl={data.audioAssets.nativeAudio} label="Listen to passage" />
        )}
      </div>

      {/ Main reading passage /}
      <div className="card" style={{ marginBottom: '.rem' }}>
        {data.readingTitle && <h style={{ fontSize: '.rem', fontWeight: , marginBottom: 'rem', color: 'var(--color-primary-light)' }}>{data.readingTitle}</h>}

        {sentencePairs.length >  && showSupport ? (
          // Sentence-by-sentence support mode
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'rem' }}>
            {sentencePairs.map((pair, i) => (
              <div key={i} style={{ borderLeft: 'px solid var(--color-primary)', paddingLeft: 'rem' }}>
                {pair.targetText && <p style={{ fontWeight: , fontSize: 'rem', marginBottom: '.rem' }}>{pair.targetText}</p>}
                {pair.transliteration && <p style={{ fontSize: '.rem', color: 'var(--color-secondary-light)', fontStyle: 'italic' }}>{pair.transliteration}</p>}
                {pair.baseTranslation && <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}>{pair.baseTranslation}</p>}
              </div>
            ))}
          </div>
        ) : (
          // Full passage
          <p style={{ whiteSpace: 'pre-line', lineHeight: , fontSize: 'rem' }}>{readingText}</p>
        )}

        {supportText && !showSupport && (
          <p style={{ marginTop: 'rem', fontSize: '.rem', color: 'var(--color-text-muted)', borderTop: 'px solid var(--color-border)', paddingTop: '.rem' }}>{supportText}</p>
        )}
      </div>

      {/ Glossary /}
      {showGlossary && glossary.length >  && (
        <div className="card" style={{ marginBottom: '.rem' }}>
          <h className="heading-sm" style={{ marginBottom: 'rem' }}> Glossary</h>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(px, fr))', gap: '.rem' }}>
            {glossary.map((item, i) => (
              <div key={item.wordId || i} style={{ padding: '.rem', background: 'var(--color-surface-)', borderRadius: 'var(--radius-sm)' }}>
                <TargetTextBlock data={item} size="sm" />
                {item.audioRef && !item.audioRef.includes('dummy') && (
                  <div style={{ marginTop: '.rem' }}><AudioPlayer audioUrl={item.audioRef} label="Listen" /></div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/ Comprehension Questions /}
      {questions.length >  && (
        <div style={{ marginBottom: '.rem' }}>
          <h className="heading-sm" style={{ marginBottom: 'rem', color: 'var(--color-text-muted)' }}> Comprehension Questions</h>
          {questions.map((q, i) => (
            <DynamicQuiz key={q.questionId || i} question={q} index={i}
              answer={answers[i]} onChange={v => setAnswers(p => ({ ...p, [i]: v }))}
              showResult={!!result} />
          ))}
        </div>
      )}

      {!result && (
        <div style={{ textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : questions.length ===  ? ' Mark as Complete' : ' Submit Answers'}
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="reading" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="reading" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
