/
  src/pages/activities/TestPage.jsx
  Block-level test: sections[] → questions[] with MCQ, true_false, fill_blank.
  Answers checked against adminCorrectAnswerSet.answerKey.
  Hints shown only after submission. All % dynamic.
 /
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

  const [activeSection, setActiveSection] = useState();
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
    if (allQuestions.length === ) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: , passed: true,
        feedback: 'Test completed! ', suggestion: '',
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
    <div style={{ maxWidth: , margin: ' auto' }}>
      <ActivityHeader label={` ${label || 'Test'}`} maxXP={maxXP} title={data.title || data.testTitle} description={data.learningGoal} goBack={goToDashboard} />

      {/ Instructions /}
      {data.instructions && (
        <div style={{ background: 'rgba(,,,.)', border: 'px solid rgba(,,,.)', borderRadius: 'var(--radius-md)', padding: '.rem rem', marginBottom: '.rem', fontSize: '.rem' }}>
           {data.instructions}
        </div>
      )}

      {/ Test info bar /}
      <div style={{ display: 'flex', gap: '.rem', marginBottom: '.rem', flexWrap: 'wrap' }}>
        <div style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}> {totalQ} Questions</div>
        {data.estimatedTime && <div style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}> ~{data.estimatedTime} min</div>}
        <div style={{ fontSize: '.rem', color: answeredCount < totalQ ? 'var(--color-accent-light)' : 'var(--color-success-light)' }}>
          ✓ {answeredCount}/{totalQ} answered
        </div>
      </div>

      {/ Section tabs /}
      {sections.length >  && (
        <div style={{ display: 'flex', gap: '.rem', marginBottom: '.rem', flexWrap: 'wrap' }}>
          {sections.map((sec, i) => (
            <button key={sec.sectionId || i}
              className={`btn btn-sm ${activeSection === i ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveSection(i)}>
              {sec.sectionTitle || `Section ${i + }`}
            </button>
          ))}
        </div>
      )}

      {/ Questions for active section /}
      {sections.length >  ? (
        <div>
          {sections[activeSection] && (
            <div>
              {sections[activeSection].sectionTitle && sections.length ===  && (
                <h className="heading-sm" style={{ marginBottom: 'rem', color: 'var(--color-text-muted)' }}>
                  {sections[activeSection].sectionTitle}
                </h>
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
                    {/ Hints — only shown after submit /}
                    {result && showHints && q.questionHints && (
                      <div style={{ marginTop: '-.rem', marginBottom: '.rem', padding: '.rem', background: 'rgba(,,,.)', border: 'px solid rgba(,,,.)', borderRadius: 'var(--radius-sm)' }}>
                        <div style={{ fontSize: '.rem', color: 'var(--color-accent-light)', fontWeight: , marginBottom: '.rem' }}> Hint</div>
                        <TargetTextBlock data={q.questionHints} size="sm" />
                      </div>
                    )}
                    {q.audioRef && !q.audioRef.includes('dummy') && (
                      <div style={{ marginBottom: '.rem' }}>
                        <AudioPlayer audioUrl={q.audioRef} label="Listen to question" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/ Section navigation /}
          {sections.length >  && (
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 'rem', marginBottom: '.rem' }}>
              <button className="btn btn-ghost" disabled={activeSection === } onClick={() => setActiveSection(s => s - )}>← Previous Section</button>
              <button className="btn btn-ghost" disabled={activeSection === sections.length - } onClick={() => setActiveSection(s => s + )}>Next Section →</button>
            </div>
          )}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: 'rem', color: 'var(--color-text-muted)' }}>
          No questions found in this test.
        </div>
      )}

      {/ Submit area /}
      {!result && (
        <div style={{ textAlign: 'center', marginTop: '.rem' }}>
          {answeredCount < totalQ && totalQ >  && (
            <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)', marginBottom: '.rem' }}>
               You have {totalQ - answeredCount} unanswered question{totalQ - answeredCount !==  ? 's' : ''}
            </p>
          )}
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : ' Submit Test'}
          </button>
        </div>
      )}

      {/ Post-submit hint toggle /}
      {result && !showHints && allQuestions.some(q => q.questionHints) && (
        <div style={{ textAlign: 'center', marginTop: 'rem' }}>
          <button className="btn btn-ghost btn-sm" onClick={() => setShowHints(true)}> Show Hints for All Questions</button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} activityType="test" />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="test" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}
