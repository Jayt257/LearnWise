/
  src/pages/activities/VocabPage.jsx
  Fully dynamic vocabulary activity — wordList[] + quizQuestions[].
  Displays -field TargetTextBlock, audio (if real path), part of speech, formality.
 
  Fixes:
    Bug  (): correctAnswer resolved from adminCorrectAnswerSet.mcqAnswerKey
    Bug  (): block_type 'multiple_choice' mapped → 'vocab' for API
    Bug  (): integer option-index converted to option string before API call
    Bug  (flip audio): TTS call on card flip via /api/speech/tts
 /
import React, { useState, useRef } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import DynamicQuiz from '../../components/DynamicQuiz.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';
import client from '../../api/client.js';

const POS_COLORS = { noun: 'f', verb: 'b', adjective: 'feb', adverb: 'ec', particle: 'bd', phrase: 'bcf' };
const FORMALITY_LABELS = { formal: ' Formal', neutral: ' Neutral', informal: ' Casual', polite: ' Polite' };

/ Play TTS audio for a word using ElevenLabs via backend /
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
  const hasQuiz = quizQs.length > ;
  // Correct answer lookup map from adminCorrectAnswerSet.mcqAnswerKey
  const answerKey = data.adminCorrectAnswerSet?.mcqAnswerKey || {};

  const handleCardFlip = (i, word) => {
    const isNowFlipped = !flipped[i];
    setFlipped(p => ({ ...p, [i]: isNowFlipped }));
    // BUG FIX : Play TTS on flip to front (showing target language text)
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
        total_score: maxXP, max_score: maxXP, percentage: , passed: true,
        feedback: 'Great job studying the vocabulary!  Try using these words in a sentence.',
        suggestion: 'Review the words again tomorrow to lock them into memory.',
        question_results: [],
      });
      return;
    }

    // Score vocab MCQ LOCALLY — definitive exact match answer key.
    // We do NOT send to Groq because:
    //  a) MCQ has a single unambiguous correct answer
    //  b) Groq was returning random scores and causing s
    const perQ = Math.round(maxXP / quizQs.length);
    let totalScore = ;
    const qResults = quizQs.map((q, i) => {
      // Resolve correct answer from mcqAnswerKey
      const correctAnswer = String(answerKey[q.questionId] || q.correctAnswer || '').trim().toLowerCase();

      // Convert integer option-index to string
      const raw = answers[i];
      const userAnswer = typeof raw === 'number'
        ? String(q.options?.[raw] || raw || '').trim().toLowerCase()
        : String(raw ?? '').trim().toLowerCase();

      const correct = userAnswer.length >  && userAnswer === correctAnswer;
      const score = correct ? perQ : ;
      totalScore += score;

      return {
        question_id: q.questionId || `vq_${i}`,
        correct,
        score,
        feedback: correct
          ? ' Correct!'
          : userAnswer.length === 
            ? ' Not answered'
            : ` Incorrect — correct answer: "${answerKey[q.questionId] || q.correctAnswer}"`,
        prompt: q.questionText || '',
        user_answer: raw === undefined ? '(skipped)' : String(raw),
        correct_answer: answerKey[q.questionId] || q.correctAnswer || '',
      };
    });

    const pct = Math.round(Math.min((totalScore / maxXP)  , ));
    const passed = pct >= ;
    const data = {
      total_score: totalScore,
      max_score: maxXP,
      percentage: pct,
      passed,
      feedback: passed
        ? `Well done! You scored ${pct}% on the vocab quiz. `
        : `You scored ${pct}%. Review the word list and try again.`,
      suggestion: passed
        ? 'Try using these words in sentences to deepen your understanding.'
        : 'Focus on the words you got wrong and flip the cards again.',
      question_results: qResults,
    };
    await submitAnswers([], data);
  };

  return (
    <div style={{ maxWidth: , margin: ' auto' }}>
      <ActivityHeader label={` ${label || 'Vocabulary'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/ Theme badge /}
      {data.vocabTheme && (
        <div style={{ marginBottom: '.rem' }}>
          <span style={{ background: 'rgba(,,,.)', color: 'cbfd', border: 'px solid rgba(,,,.)', borderRadius: 'var(--radius-full)', padding: '.rem .rem', fontSize: '.rem' }}>
             Theme: {data.vocabTheme}
          </span>
        </div>
      )}

      {/ Tab bar — show quiz tab only if quiz exists /}
      {hasQuiz && (
        <div style={{ display: 'flex', gap: '.rem', marginBottom: '.rem' }}>
          {[['words', ' Word List'], ['quiz', ' Quiz']].map(([tab, lbl]) => (
            <button key={tab} className={`btn btn-sm ${activeTab === tab ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setActiveTab(tab)}>{lbl}</button>
          ))}
        </div>
      )}

      {/ Word List /}
      {(activeTab === 'words' || !hasQuiz) && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(px, fr))', gap: 'rem', marginBottom: 'rem' }}>
          {words.map((word, i) => {
            const isFlipped = flipped[i];
            const pos = word.partOfSpeech;
            return (
              <div key={word.wordId || i}
                onClick={() => handleCardFlip(i, word)}
                style={{ cursor: 'pointer', minHeight: , borderRadius: 'var(--radius-md)', border: `px solid ${POS_COLORS[pos] || 'var(--color-border)'}`, background: isFlipped ? `${POS_COLORS[pos] || 'f'}` : 'var(--color-surface-)', padding: '.rem', display: 'flex', flexDirection: 'column', gap: '.rem', transition: 'all .s', position: 'relative' }}>
                {/ POS + formality badges /}
                <div style={{ display: 'flex', gap: '.rem', flexWrap: 'wrap' }}>
                  {pos && <span style={{ fontSize: '.rem', fontWeight: , color: POS_COLORS[pos] || 'var(--color-text-muted)', textTransform: 'uppercase' }}>{pos}</span>}
                  {word.formalityLevel && <span style={{ fontSize: '.rem', color: 'var(--color-text-dim)' }}>{FORMALITY_LABELS[word.formalityLevel] || word.formalityLevel}</span>}
                </div>

                <TargetTextBlock data={word} size={isFlipped ? 'sm' : 'lg'} />

                {/ Example sentence (shown when flipped) /}
                {isFlipped && word.exampleSentence && (
                  <div style={{ marginTop: '.rem', padding: '.rem', background: 'var(--color-surface-)', borderRadius: 'var(--radius-sm)' }}>
                    <p style={{ fontSize: '.rem', color: 'var(--color-primary-light)' }}>{word.exampleSentence.targetText}</p>
                    {word.exampleSentence.baseTranslation && <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}>{word.exampleSentence.baseTranslation}</p>}
                  </div>
                )}

                {/ Audio — only real paths (non-dummy) /}
                {word.audioRef && !word.audioRef.includes('dummy') && (
                  <div style={{ marginTop: 'auto' }} onClick={e => e.stopPropagation()}>
                    <AudioPlayer audioUrl={word.audioRef} label="Listen" />
                  </div>
                )}

                {/ TTS indicator when flipped /}
                {isFlipped && (
                  <div style={{ position: 'absolute', top: , right: , fontSize: '.rem', color: 'var(--color-text-dim)' }}> tap to flip back</div>
                )}
                {!isFlipped && (
                  <div style={{ position: 'absolute', bottom: , right: , fontSize: '.rem', color: 'var(--color-text-dim)' }}>tap to flip</div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/ Quiz /}
      {activeTab === 'quiz' && hasQuiz && (
        <div style={{ marginBottom: 'rem' }}>
          {quizQs.map((q, i) => (
            <DynamicQuiz key={q.questionId || i} question={q} index={i}
              answer={answers[i]} onChange={v => setAnswers(p => ({ ...p, [i]: v }))}
              showResult={!!result} />
          ))}
        </div>
      )}

      {/ Submit /}
      {!result && (
        <div style={{ textAlign: 'center', marginTop: 'rem' }}>
          {hasQuiz && activeTab === 'words' ? (
            <button className="btn btn-ghost" onClick={() => setActiveTab('quiz')}>Go to Quiz →</button>
          ) : (
            <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
              {submitting ? <><span className="spinner" /> Evaluating...</> : words.length >  && !hasQuiz ? ' Mark Complete' : ' Submit Quiz'}
            </button>
          )}
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="vocabulary" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="vocabulary" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
