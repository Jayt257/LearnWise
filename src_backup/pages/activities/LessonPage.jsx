/
  src/pages/activities/LessonPage.jsx
  Renders lesson content from lessonContent[] array. Fully dynamic — no hardcoded fields.
  Supports: sectionTitle, bodyText, targetLanguageExamples (-field), audioRef, checkpointQuestions
 /
import React, { useState } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import DynamicQuiz from '../../components/DynamicQuiz.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

const BADGE_STYLE = { background: 'rgba(,,,.)', color: 'abfc', border: 'px solid rgba(,,,.)', borderRadius: 'var(--radius-full)', padding: '.rem .rem', fontSize: '.rem', fontWeight: , display: 'inline-flex', alignItems: 'center', gap: '.rem' };

export default function LessonPage({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber }) {
  const {
    data, loading, error, answers, setAnswers, submitting,
    result, showFeedback, setShowFeedback,
    submitAnswers, retryActivity, goToDashboard,
  } = useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType: 'lesson' });

  const [expandedSections, setExpandedSections] = useState({});

  if (loading) return <Spinner />;
  if (error === 'content_missing') return <ContentMissing goBack={goToDashboard} />;
  if (error) return <LoadError goBack={goToDashboard} />;
  if (!data) return null;

  const sections = data.lessonContent || [];
  const checkpointQs = data.checkpointQuestions || [];
  const importantRules = data.importantRules || [];
  const culture = data.cultureContext;
  const summary = data.summary;

  const handleSubmit = async () => {
    if (checkpointQs.length === ) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: , passed: true,
        feedback: 'Great job reading through the lesson! ', suggestion: 'Move on to the next activity.',
        question_results: [],
      });
      return;
    }

    // Score locally — exact/normalised string match.
    // We do NOT send lesson MCQ/short-answer to Groq because:
    //   a) Groq gives inconsistent marks even for correct answers
    //   b) Groq hallucinates partial scores (%) for empty submissions
    const perQ = Math.round(maxXP / checkpointQs.length);
    let totalScore = ;
    const qResults = checkpointQs.map((q, i) => {
      const correctRaw = String(q.expectedAnswer || q.correctAnswer || q.options?.[q.correct] || '').trim().toLowerCase();
      const userRaw    = typeof answers[i] === 'number'
        ? String(q.options?.[answers[i]] || answers[i] || '').trim().toLowerCase()
        : String(answers[i] || '').trim().toLowerCase();

      // Empty answer → , no partial credit
      const correct = userRaw.length >  && (
        userRaw === correctRaw ||
        // Accept answer contains correct key word (for open-ended where user types a subset)
        (correctRaw.length >  && userRaw.includes(correctRaw))
      );
      const score = correct ? perQ : ;
      totalScore += score;
      return {
        question_id: q.questionId || `cq_${i}`,
        correct,
        score,
        feedback: correct
          ? ' Correct!'
          : userRaw.length === 
            ? ' No answer provided'
            : ` Incorrect — the correct answer was: "${q.expectedAnswer || q.correctAnswer || q.options?.[q.correct] || '(see lesson)'}"`,
      };
    });

    const pct = Math.round((totalScore / maxXP)  );
    const passed = pct >= ;

    await submitAnswers([], {
      total_score: totalScore,
      max_score: maxXP,
      percentage: pct,
      passed,
      feedback: passed
        ? `Great work! You scored ${pct}% on the checkpoint. `
        : `You scored ${pct}%. Review the lesson content and try again.`,
      suggestion: passed
        ? 'Move on to the next activity or revisit for deeper understanding.'
        : 'Read each section again and pay attention to the examples.',
      question_results: qResults,
    });
  };

  return (
    <div style={{ maxWidth: , margin: ' auto' }}>
      <ActivityHeader label={` ${label || 'Lesson'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/ Instructions /}
      {data.instructions && (
        <div style={{ background: 'var(--color-primary-glow)', border: 'px solid var(--color-primary)', borderRadius: 'var(--radius-md)', padding: '.rem rem', marginBottom: '.rem', fontSize: '.rem' }}>
           {data.instructions}
        </div>
      )}

      {/ Lesson sections /}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '.rem' }}>
        {sections.map((sec, idx) => (
          <div key={sec.sectionId || idx} className="card">
            <h className="heading-sm" style={{ marginBottom: '.rem', color: 'var(--color-primary-light)' }}>{sec.sectionTitle}</h>
            {sec.bodyText && <p style={{ whiteSpace: 'pre-line', lineHeight: ., fontSize: '.rem', color: 'var(--color-text)', marginBottom: sec.targetLanguageExamples?.length ? 'rem' :  }}>{sec.bodyText}</p>}

            {/ Examples with -field TargetTextBlock /}
            {sec.targetLanguageExamples?.length >  && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '.rem', marginTop: '.rem' }}>
                {sec.targetLanguageExamples.map((ex, j) => (
                  <div key={j} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--color-surface-)', borderRadius: 'var(--radius-sm)', padding: '.rem', flexWrap: 'wrap', gap: '.rem' }}>
                    <TargetTextBlock data={ex} size="md" />
                    {/ Only render audio player if audioRef is a real path (not dummy) /}
                    {ex.audioRef && !ex.audioRef.includes('dummy') && (
                      <AudioPlayer audioUrl={ex.audioRef} label="Listen" />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {/ Important Rules /}
        {importantRules.length >  && (
          <div className="card" style={{ border: 'px solid rgba(,,,.)', background: 'rgba(,,,.)' }}>
            <h className="heading-sm" style={{ marginBottom: '.rem', color: 'var(--color-primary-light)' }}> Important Rules</h>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '.rem' }}>
              {importantRules.map((rule, i) => (
                <li key={i} style={{ display: 'flex', gap: '.rem', fontSize: '.rem' }}>
                  <span style={{ color: 'var(--color-accent-light)' }}>✦</span>
                  <span>{typeof rule === 'object' ? rule.rule || JSON.stringify(rule) : rule}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/ Cultural Context (only if applicable) /}
        {culture?.isApplicable && culture.contextText && (
          <div style={{ background: 'rgba(,,,.)', border: 'px solid rgba(,,,.)', borderRadius: 'var(--radius-md)', padding: 'rem' }}>
            <h style={{ color: 'var(--color-accent-light)', marginBottom: '.rem', fontSize: '.rem', fontWeight:  }}> Cultural Note</h>
            <p style={{ fontSize: '.rem', lineHeight: . }}>{culture.contextText}</p>
            {culture.dosList?.length >  && (
              <div style={{ marginTop: '.rem' }}>
                <div style={{ fontSize: '.rem', fontWeight: , color: 'var(--color-success-light)', marginBottom: '.rem' }}>✓ Do</div>
                {culture.dosList.map((d, i) => <div key={i} style={{ fontSize: '.rem' }}>• {d}</div>)}
              </div>
            )}
            {culture.dontsList?.length >  && (
              <div style={{ marginTop: '.rem' }}>
                <div style={{ fontSize: '.rem', fontWeight: , color: 'var(--color-danger-light)', marginBottom: '.rem' }}>✗ Don't</div>
                {culture.dontsList.map((d, i) => <div key={i} style={{ fontSize: '.rem' }}>• {d}</div>)}
              </div>
            )}
          </div>
        )}

        {/ Summary /}
        {summary && (
          <div style={{ background: 'rgba(,,,.)', border: 'px solid rgba(,,,.)', borderRadius: 'var(--radius-md)', padding: 'rem' }}>
            <h style={{ color: 'var(--color-success-light)', marginBottom: '.rem', fontSize: '.rem', fontWeight:  }}> Lesson Summary</h>
            <p style={{ fontSize: '.rem', lineHeight: . }}>{summary}</p>
          </div>
        )}

        {/ Checkpoint Questions (dynamic quiz) /}
        {checkpointQs.length >  && (
          <div>
            <h className="heading-sm" style={{ marginBottom: 'rem', color: 'var(--color-text-muted)' }}> Checkpoint Questions</h>
            {checkpointQs.map((q, i) => (
              <DynamicQuiz key={q.questionId || i} question={q} index={i}
                answer={answers[i]} onChange={v => setAnswers(p => ({ ...p, [i]: v }))}
                showResult={!!result} />
            ))}
          </div>
        )}
      </div>

      {/ Submit /}
      {!result && (
        <div style={{ marginTop: 'rem', textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : checkpointQs.length ===  ? ' Mark as Complete' : ' Submit & Get Feedback'}
          </button>
        </div>
      )}

      {result && <ScoreModal result={result} maxXP={maxXP} onNext={() => setShowFeedback(true)} onRetry={retryActivity} />}
      {showFeedback && result && <ActivityFeedback result={result} activityType="lesson" onDismiss={() => { setShowFeedback(false); goToDashboard(); }} />}
    </div>
  );
}

// ── Shared sub-components ─────────────────────────────────────────
export function ActivityHeader({ label, maxXP, title, description, goBack }) {
  return (
    <div style={{ marginBottom: '.rem', display: 'flex', alignItems: 'flex-start', gap: 'rem' }}>
      <button className="btn btn-ghost btn-sm" onClick={goBack}>← Back</button>
      <div>
        <div style={BADGE_STYLE}>{label} • +{maxXP} XP</div>
        {title && <h className="heading-md" style={{ marginTop: '.rem' }}>{title}</h>}
        {description && <p className="text-muted" style={{ fontSize: '.rem', marginTop: '.rem' }}>{description}</p>}
      </div>
    </div>
  );
}

export function Spinner() {
  return <div style={{ textAlign: 'center', padding: 'rem' }}><div className="spinner" style={{ margin: ' auto' }} /></div>;
}

export function ContentMissing({ goBack }) {
  return (
    <div style={{ textAlign: 'center', padding: 'rem' }}>
      <div style={{ fontSize: 'rem', marginBottom: 'rem' }}></div>
      <h className="heading-md" style={{ marginBottom: '.rem' }}>Content Not Available Yet</h>
      <p className="text-muted" style={{ marginBottom: '.rem' }}>The admin hasn't created this activity's content yet. Check back later!</p>
      <button className="btn btn-primary" onClick={goBack}>← Back to Roadmap</button>
    </div>
  );
}

export function LoadError({ goBack }) {
  return (
    <div style={{ textAlign: 'center', padding: 'rem', color: 'var(--color-danger-light)' }}>
      <p>Failed to load activity. Please try again.</p>
      <button className="btn btn-secondary" style={{ marginTop: 'rem' }} onClick={goBack}>← Back</button>
    </div>
  );
}
