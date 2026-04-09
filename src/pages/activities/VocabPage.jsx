/**
 * src/pages/activities/VocabPage.jsx
 * Fully dynamic vocabulary activity — wordList[] + quizQuestions[].
 * Displays 3-field TargetTextBlock, audio (if real path), part of speech, formality.
 *
 * Fixes:
 *   Bug #5 (422): correctAnswer resolved from adminCorrectAnswerSet.mcqAnswerKey
 *   Bug #5 (422): block_type 'multiple_choice' mapped → 'vocab' for API
 *   Bug #5 (422): integer option-index converted to option string before API call
 *   Bug #4 (flip audio): TTS call on card flip via /api/speech/tts
 */
import React, { useState, useRef } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import DynamicQuiz from '../../components/DynamicQuiz.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';
import client from '../../api/client.js';

const POS_COLORS = { noun: '#6366f1', verb: '#10b981', adjective: '#f59e0b', adverb: '#ec4899', particle: '#06b6d4', phrase: '#8b5cf6' };
const FORMALITY_LABELS = { formal: '🎩 Formal', neutral: '😐 Neutral', informal: '😊 Casual', polite: '🙏 Polite' };

/** Play TTS audio for a word using ElevenLabs via backend */
async function playTTS(text, lang = 'ja') {
  try {
    const resp = await client.post('/speech/tts', { text, lang }, { responseType: 'blob' });
    const url = URL.createObjectURL(resp.data);
    const audio = new Audio(url);
    audio.play();
    audio.onended = () => URL.revokeObjectURL(url);
  } catch (e) {
    // TTS not critical — silently ignore (e.g. ElevenLabs key not set)
    console.warn('TTS not available:', e.message);
  }
}

export default function VocabPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback, submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'vocab' });

  const [activeTab, setActiveTab] = useState('words'); // 'words' | 'quiz'
  const [flipped, setFlipped] = useState({});
  const ttsPlaying = useRef({});

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const words = data.wordList || [];
  const quizQs = data.quizQuestions || [];
  const hasQuiz = quizQs.length > 0;
  // Correct answer lookup map from adminCorrectAnswerSet.mcqAnswerKey
  const answerKey = data.adminCorrectAnswerSet?.mcqAnswerKey || {};

  const handleCardFlip = (i, word) => {
    const isNowFlipped = !flipped[i];
    setFlipped(p => ({ ...p, [i]: isNowFlipped }));
    // BUG FIX #4: Play TTS on flip to front (showing target language text)
    if (isNowFlipped && word.targetText && !ttsPlaying.current[i]) {
      ttsPlaying.current[i] = true;
      playTTS(word.targetText, data.targetLanguage || 'ja')
        .finally(() => { ttsPlaying.current[i] = false; });
    }
  };

  const handleSubmit = async () => {
    if (!hasQuiz) {
      // No quiz — just studying words, auto-pass
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: 100, passed: true,
        feedback: 'Great job studying the vocabulary! 🔤 Try using these words in a sentence.',
        suggestion: 'Review the words again tomorrow to lock them into memory.',
        question_results: [],
      });
      return;
    }

    // Score vocab MCQ LOCALLY — definitive exact match answer key.
    // We do NOT send to Groq because:
    //  a) MCQ has a single unambiguous correct answer
    //  b) Groq was returning random scores and causing 422s
    const perQ = Math.round(maxXP / quizQs.length);
    let totalScore = 0;
    const qResults = quizQs.map((q, i) => {
      // Resolve correct answer from mcqAnswerKey
      const correctAnswer = String(answerKey[q.questionId] || q.correctAnswer || '').trim().toLowerCase();

      // Convert integer option-index to string
      const raw = answers[i];
      const userAnswer = typeof raw === 'number'
        ? String(q.options?.[raw] || raw || '').trim().toLowerCase()
        : String(raw ?? '').trim().toLowerCase();

      const correct = userAnswer.length > 0 && userAnswer === correctAnswer;
      const score = correct ? perQ : 0;
      totalScore += score;

      return {
        question_id: q.questionId || `vq_${i}`,
        correct,
        score,
        feedback: correct
          ? '✅ Correct!'
          : userAnswer.length === 0
            ? '❌ Not answered'
            : `❌ Incorrect — correct answer: "${answerKey[q.questionId] || q.correctAnswer}"`,
        prompt: q.questionText || '',
        user_answer: raw === undefined ? '(skipped)' : String(raw),
        correct_answer: answerKey[q.questionId] || q.correctAnswer || '',
      };
    });

    const pct = Math.round(Math.min((totalScore / maxXP) * 100, 100));
    const passed = pct >= 50;
    const data = {
      total_score: totalScore,
      max_score: maxXP,
      percentage: pct,
      passed,
      feedback: passed
        ? `Well done! You scored ${pct}% on the vocab quiz. 🔤`
        : `You scored ${pct}%. Review the word list and try again.`,
      suggestion: passed
        ? 'Try using these words in sentences to deepen your understanding.'
        : 'Focus on the words you got wrong and flip the cards again.',
      question_results: qResults,
    };
    await submitAnswers([], data);
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
                onClick={() => handleCardFlip(i, word)}
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

                {/* Audio — only real paths (non-dummy) */}
                {word.audioRef && !word.audioRef.includes('dummy') && (
                  <div style={{ marginTop: 'auto' }} onClick={e => e.stopPropagation()}>
                    <AudioPlayer audioUrl={word.audioRef} label="Listen" />
                  </div>
                )}

                {/* TTS indicator when flipped */}
                {isFlipped && (
                  <div style={{ position: 'absolute', top: 8, right: 10, fontSize: '0.65rem', color: 'var(--color-text-dim)' }}>🔊 tap to flip back</div>
                )}
                {!isFlipped && (
                  <div style={{ position: 'absolute', bottom: 8, right: 10, fontSize: '0.65rem', color: 'var(--color-text-dim)' }}>tap to flip</div>
                )}
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
