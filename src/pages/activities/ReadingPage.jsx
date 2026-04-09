/**
 * src/pages/activities/ReadingPage.jsx
 * Fully dynamic: readingText, sentenceSupportPairs[], glossary[], comprehensionQuestions[].
 * Toggle between reading-only view and sentence-by-sentence support.
 */
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
    if (questions.length === 0) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: 100, passed: true,
        feedback: 'Excellent reading! 📄', suggestion: 'Try to recall the main points from memory.',
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
    <div style={{ maxWidth: 820, margin: '0 auto' }}>
      <ActivityHeader label={`📄 ${label || 'Reading'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/* Toolbar */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        {sentencePairs.length > 0 && (
          <button className={`btn btn-sm ${showSupport ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowSupport(s => !s)}>
            {showSupport ? '🙈 Hide Support' : '👁 Show Support'}
          </button>
        )}
        {glossary.length > 0 && (
          <button className={`btn btn-sm ${showGlossary ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setShowGlossary(s => !s)}>
            📖 Glossary ({glossary.length})
          </button>
        )}
        {data.audioAssets?.nativeAudio && !data.audioAssets.nativeAudio.includes('dummy') && (
          <AudioPlayer audioUrl={data.audioAssets.nativeAudio} label="Listen to passage" />
        )}
      </div>

      {/* Main reading passage */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        {data.readingTitle && <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--color-primary-light)' }}>{data.readingTitle}</h2>}

        {sentencePairs.length > 0 && showSupport ? (
          // Sentence-by-sentence support mode
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {sentencePairs.map((pair, i) => (
              <div key={i} style={{ borderLeft: '3px solid var(--color-primary)', paddingLeft: '1rem' }}>
                {pair.targetText && <p style={{ fontWeight: 600, fontSize: '1rem', marginBottom: '0.25rem' }}>{pair.targetText}</p>}
                {pair.transliteration && <p style={{ fontSize: '0.8rem', color: 'var(--color-secondary-light)', fontStyle: 'italic' }}>{pair.transliteration}</p>}
                {pair.baseTranslation && <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{pair.baseTranslation}</p>}
              </div>
            ))}
          </div>
        ) : (
          // Full passage
          <p style={{ whiteSpace: 'pre-line', lineHeight: 2, fontSize: '1rem' }}>{readingText}</p>
        )}

        {supportText && !showSupport && (
          <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--color-text-muted)', borderTop: '1px solid var(--color-border)', paddingTop: '0.75rem' }}>{supportText}</p>
        )}
      </div>

      {/* Glossary */}
      {showGlossary && glossary.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 className="heading-sm" style={{ marginBottom: '1rem' }}>📖 Glossary</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '0.75rem' }}>
            {glossary.map((item, i) => (
              <div key={item.wordId || i} style={{ padding: '0.75rem', background: 'var(--color-surface-3)', borderRadius: 'var(--radius-sm)' }}>
                <TargetTextBlock data={item} size="sm" />
                {item.audioRef && !item.audioRef.includes('dummy') && (
                  <div style={{ marginTop: '0.5rem' }}><AudioPlayer audioUrl={item.audioRef} label="Listen" /></div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Comprehension Questions */}
      {questions.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 className="heading-sm" style={{ marginBottom: '1rem', color: 'var(--color-text-muted)' }}>💬 Comprehension Questions</h3>
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
            {submitting ? <><span className="spinner" /> Evaluating...</> : questions.length === 0 ? '✅ Mark as Complete' : '✅ Submit Answers'}
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="reading" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="reading" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
