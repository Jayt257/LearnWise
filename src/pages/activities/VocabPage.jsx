/**
 * src/pages/activities/VocabPage.jsx
 * Fully dynamic vocabulary activity — wordList[] + quizQuestions[].
 * Displays 3-field TargetTextBlock, audio (if real path), part of speech, formality.
 */
import React, { useState } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import DynamicQuiz from '../../components/DynamicQuiz.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

const POS_COLORS = { noun: '#6366f1', verb: '#10b981', adjective: '#f59e0b', adverb: '#ec4899', particle: '#06b6d4', phrase: '#8b5cf6' };
const FORMALITY_LABELS = { formal: '🎩 Formal', neutral: '😐 Neutral', informal: '😊 Casual', polite: '🙏 Polite' };

export default function VocabPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback, submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'vocabulary' });

  const [activeTab, setActiveTab] = useState('words'); // 'words' | 'quiz'
  const [flipped, setFlipped] = useState({});

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const words = data.wordList || [];
  const quizQs = data.quizQuestions || [];
  const hasQuiz = quizQs.length > 0;

  const handleSubmit = async () => {
    if (!hasQuiz) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: 100, passed: true,
        feedback: 'Great job studying the vocabulary! 🔤', suggestion: 'Try to use these words in sentences.',
        question_results: [],
      });
      return;
    }
    const questions = quizQs.map((q, i) => ({
      question_id: q.questionId || `vq_${i}`,
      block_type: q.questionType || 'vocab',
      user_answer: typeof answers[i] === 'number' ? (q.options?.[answers[i]] || answers[i]) : (answers[i] || ''),
      correct_answer: q.correctAnswer || '',
      prompt: q.questionText || '',
    }));
    await submitAnswers(questions);
  };

  return (
    <div style={{ maxWidth: 860, margin: '0 auto' }}>
      <ActivityHeader label={`🔤 ${label || 'Vocabulary'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/* Theme badge */}
      {data.vocabTheme && (
        <div style={{ marginBottom: '1.25rem' }}>
          <span style={{ background: 'rgba(139,92,246,0.15)', color: '#c4b5fd', border: '1px solid rgba(139,92,246,0.3)', borderRadius: 'var(--radius-full)', padding: '0.25rem 0.75rem', fontSize: '0.78rem' }}>
            📚 Theme: {data.vocabTheme}
          </span>
        </div>
      )}

      {/* Tab bar — show quiz tab only if quiz exists */}
      {hasQuiz && (
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
          {[['words', '📖 Word List'], ['quiz', '📝 Quiz']].map(([tab, lbl]) => (
            <button key={tab} className={`btn btn-sm ${activeTab === tab ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setActiveTab(tab)}>{lbl}</button>
          ))}
        </div>
      )}

      {/* Word List */}
      {(activeTab === 'words' || !hasQuiz) && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          {words.map((word, i) => {
            const isFlipped = flipped[i];
            const pos = word.partOfSpeech;
            return (
              <div key={word.wordId || i}
                onClick={() => setFlipped(p => ({ ...p, [i]: !p[i] }))}
                style={{ cursor: 'pointer', minHeight: 160, borderRadius: 'var(--radius-md)', border: `1px solid ${POS_COLORS[pos] || 'var(--color-border)'}`, background: isFlipped ? `${POS_COLORS[pos] || '#6366f1'}18` : 'var(--color-surface-2)', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', transition: 'all 0.25s', position: 'relative' }}>
                
                {/* POS + formality badges */}
                <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }}>
                  {pos && <span style={{ fontSize: '0.65rem', fontWeight: 700, color: POS_COLORS[pos] || 'var(--color-text-muted)', textTransform: 'uppercase' }}>{pos}</span>}
                  {word.formalityLevel && <span style={{ fontSize: '0.65rem', color: 'var(--color-text-dim)' }}>{FORMALITY_LABELS[word.formalityLevel] || word.formalityLevel}</span>}
                </div>

                <TargetTextBlock data={word} size={isFlipped ? 'sm' : 'lg'} />

                {/* Example sentence (shown when flipped) */}
                {isFlipped && word.exampleSentence && (
                  <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'var(--color-surface-3)', borderRadius: 'var(--radius-sm)' }}>
                    <p style={{ fontSize: '0.8rem', color: 'var(--color-primary-light)' }}>{word.exampleSentence.targetText}</p>
                    {word.exampleSentence.baseTranslation && <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{word.exampleSentence.baseTranslation}</p>}
                  </div>
                )}

                {/* Audio — only real paths */}
                {word.audioRef && !word.audioRef.includes('dummy') && (
                  <div style={{ marginTop: 'auto' }} onClick={e => e.stopPropagation()}>
                    <AudioPlayer audioUrl={word.audioRef} label="Listen" />
                  </div>
                )}

                <div style={{ position: 'absolute', bottom: 8, right: 10, fontSize: '0.65rem', color: 'var(--color-text-dim)' }}>
                  {isFlipped ? 'click to flip back' : 'tap to flip'}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Quiz */}
      {activeTab === 'quiz' && hasQuiz && (
        <div style={{ marginBottom: '2rem' }}>
          {quizQs.map((q, i) => (
            <DynamicQuiz key={q.questionId || i} question={q} index={i}
              answer={answers[i]} onChange={v => setAnswers(p => ({ ...p, [i]: v }))}
              showResult={!!result} />
          ))}
        </div>
      )}

      {/* Submit */}
      {!result && (
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          {hasQuiz && activeTab === 'words' ? (
            <button className="btn btn-ghost" onClick={() => setActiveTab('quiz')}>Go to Quiz →</button>
          ) : (
            <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
              {submitting ? <><span className="spinner" /> Evaluating...</> : words.length > 0 && !hasQuiz ? '✅ Mark Complete' : '✅ Submit Quiz'}
            </button>
          )}
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="vocabulary" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="vocabulary" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
