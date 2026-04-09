/**
 * src/pages/activities/TestPage.jsx
 * Block-level test: sections[] → questions[] with MCQ, true_false, fill_blank.
 * Answers checked against adminCorrectAnswerSet.answerKey.
 * Hints shown only after submission. All 100% dynamic.
 */
import React, { useState } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import { ActivityHeader, Spinner, ContentMissing, LoadError } from './LessonPage.jsx';
import DynamicQuiz from '../../components/DynamicQuiz.jsx';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

export default function TestPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback, submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'test' });

  const [activeSection, setActiveSection] = useState(0);
  const [showHints, setShowHints] = useState(false);

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  // Support both 'sections' and 'questionSections' field names
  const sections = data.sections || data.questionSections || [];
  const answerKey = data.adminCorrectAnswerSet?.answerKey || {};
  const totalMarks = data.totalMarks || maxXP;

  // Flatten all questions with their section key for submission
  const allQuestions = sections.flatMap(sec =>
    (sec.questions || []).map(q => ({ ...q, sectionId: sec.sectionId }))
  );

  const handleSubmit = async () => {
    if (allQuestions.length === 0) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: 100, passed: true,
        feedback: 'Test completed! 📋', suggestion: '',
        question_results: [],
      });
      return;
    }

    const questions = allQuestions.map((q, globalIdx) => {
      const qid = q.questionId || `tq_${globalIdx}`;
      const userAns = answers[qid];
      let answerText = '';
      if (typeof userAns === 'number') {
        answerText = q.options?.[userAns] || String(userAns);
      } else {
        answerText = userAns || '';
      }
      // Look up correct answer from answerKey
      const correctAns = answerKey[qid] || q.correctAnswer || '';
      return {
        question_id: qid,
        block_type: q.questionType || 'mcq',
        user_answer: answerText,
        correct_answer: correctAns,
        prompt: q.questionText || '',
      };
    });

    await submitAnswers(questions);
  };

  const answeredCount = Object.keys(answers).length;
  const totalQ = allQuestions.length;

  return (
    <div style={{ maxWidth: 820, margin: '0 auto' }}>
      <ActivityHeader label={`📋 ${label || 'Test'}`} maxXP={maxXP} title={data.title || data.testTitle} description={data.learningGoal} goBack={goToDashboard} />

      {/* Instructions */}
      {data.instructions && (
        <div style={{ background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', marginBottom: '1.5rem', fontSize: '0.85rem' }}>
          📋 {data.instructions}
        </div>
      )}

      {/* Test info bar */}
      <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>📝 {totalQ} Questions</div>
        {data.estimatedTime && <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>⏱ ~{data.estimatedTime} min</div>}
        <div style={{ fontSize: '0.8rem', color: answeredCount < totalQ ? 'var(--color-accent-light)' : 'var(--color-success-light)' }}>
          ✓ {answeredCount}/{totalQ} answered
        </div>
      </div>

      {/* Section tabs */}
      {sections.length > 1 && (
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          {sections.map((sec, i) => (
            <button key={sec.sectionId || i}
              className={`btn btn-sm ${activeSection === i ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveSection(i)}>
              {sec.sectionTitle || `Section ${i + 1}`}
            </button>
          ))}
        </div>
      )}

      {/* Questions for active section */}
      {sections.length > 0 ? (
        <div>
          {sections[activeSection] && (
            <div>
              {sections[activeSection].sectionTitle && sections.length === 1 && (
                <h3 className="heading-sm" style={{ marginBottom: '1rem', color: 'var(--color-text-muted)' }}>
                  {sections[activeSection].sectionTitle}
                </h3>
              )}
              {(sections[activeSection].questions || []).map((q, qi) => {
                const qid = q.questionId || `tq_${qi}`;
                return (
                  <div key={qid}>
                    <DynamicQuiz
                      question={{ ...q, questionType: q.questionType || 'mcq' }}
                      index={qi}
                      answer={answers[qid]}
                      onChange={v => setAnswers(p => ({ ...p, [qid]: v }))}
                      showResult={!!result}
                    />
                    {/* Hints — only shown after submit */}
                    {result && showHints && q.questionHints && (
                      <div style={{ marginTop: '-0.5rem', marginBottom: '0.75rem', padding: '0.625rem', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 'var(--radius-sm)' }}>
                        <div style={{ fontSize: '0.7rem', color: 'var(--color-accent-light)', fontWeight: 700, marginBottom: '0.25rem' }}>💡 Hint</div>
                        <TargetTextBlock data={q.questionHints} size="sm" />
                      </div>
                    )}
                    {q.audioRef && !q.audioRef.includes('dummy') && (
                      <div style={{ marginBottom: '0.75rem' }}>
                        <AudioPlayer audioUrl={q.audioRef} label="Listen to question" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Section navigation */}
          {sections.length > 1 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem', marginBottom: '1.5rem' }}>
              <button className="btn btn-ghost" disabled={activeSection === 0} onClick={() => setActiveSection(s => s - 1)}>← Previous Section</button>
              <button className="btn btn-ghost" disabled={activeSection === sections.length - 1} onClick={() => setActiveSection(s => s + 1)}>Next Section →</button>
            </div>
          )}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-muted)' }}>
          No questions found in this test.
        </div>
      )}

      {/* Submit area */}
      {!result && (
        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          {answeredCount < totalQ && totalQ > 0 && (
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '0.75rem' }}>
              ⚠️ You have {totalQ - answeredCount} unanswered question{totalQ - answeredCount !== 1 ? 's' : ''}
            </p>
          )}
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : '✅ Submit Test'}
          </button>
        </div>
      )}

      {/* Post-submit hint toggle */}
      {result && !showHints && allQuestions.some(q => q.questionHints) && (
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <button className="btn btn-ghost btn-sm" onClick={() => setShowHints(true)}>💡 Show Hints for All Questions</button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="test" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="test" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
