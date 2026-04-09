/**
 * src/pages/activities/LessonPage.jsx
 * Renders lesson content from lessonContent[] array. Fully dynamic — no hardcoded fields.
 * Supports: sectionTitle, bodyText, targetLanguageExamples (3-field), audioRef, checkpointQuestions
 */
import React, { useState } from 'react';
import { useActivity } from '../../hooks/useActivity.js';
import TargetTextBlock from '../../components/TargetTextBlock.jsx';
import AudioPlayer from '../../components/AudioPlayer.jsx';
import DynamicQuiz from '../../components/DynamicQuiz.jsx';
import ScoreModal from '../../components/ScoreModal.jsx';
import ActivityFeedback from '../../components/ActivityFeedback.jsx';

const BADGE_STYLE = { background: 'rgba(99,102,241,0.15)', color: '#a5b4fc', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 'var(--radius-full)', padding: '0.25rem 0.75rem', fontSize: '0.78rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.375rem' };

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
    if (checkpointQs.length === 0) {
      await submitAnswers([], {
        total_score: maxXP, max_score: maxXP, percentage: 100, passed: true,
        feedback: 'Great job reading through the lesson! 📖', suggestion: 'Move on to the next activity.',
        question_results: [],
      });
      return;
    }
    const questions = checkpointQs.map((q, i) => ({
      question_id: q.questionId || `cq_${i}`,
      block_type: 'quiz',
      user_answer: typeof answers[i] === 'number' ? q.options[answers[i]] : (answers[i] || ''),
      correct_answer: q.correctAnswer || q.options?.[q.correct] || '',
      prompt: q.questionText || '',
    }));
    await submitAnswers(questions);
  };

  return (
    <div style={{ maxWidth: 820, margin: '0 auto' }}>
      <ActivityHeader label={`📖 ${label || 'Lesson'}`} maxXP={maxXP} title={data.title} description={data.learningGoal} goBack={goToDashboard} />

      {/* Instructions */}
      {data.instructions && (
        <div style={{ background: 'var(--color-primary-glow)', border: '1px solid var(--color-primary)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', marginBottom: '1.5rem', fontSize: '0.85rem' }}>
          💡 {data.instructions}
        </div>
      )}

      {/* Lesson sections */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {sections.map((sec, idx) => (
          <div key={sec.sectionId || idx} className="card">
            <h3 className="heading-sm" style={{ marginBottom: '0.75rem', color: 'var(--color-primary-light)' }}>{sec.sectionTitle}</h3>
            {sec.bodyText && <p style={{ whiteSpace: 'pre-line', lineHeight: 1.85, fontSize: '0.9rem', color: 'var(--color-text)', marginBottom: sec.targetLanguageExamples?.length ? '1rem' : 0 }}>{sec.bodyText}</p>}

            {/* Examples with 3-field TargetTextBlock */}
            {sec.targetLanguageExamples?.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.75rem' }}>
                {sec.targetLanguageExamples.map((ex, j) => (
                  <div key={j} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--color-surface-3)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <TargetTextBlock data={ex} size="md" />
                    {/* Only render audio player if audioRef is a real path (not dummy) */}
                    {ex.audioRef && !ex.audioRef.includes('dummy') && (
                      <AudioPlayer audioUrl={ex.audioRef} label="Listen" />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Important Rules */}
        {importantRules.length > 0 && (
          <div className="card" style={{ border: '1px solid rgba(99,102,241,0.3)', background: 'rgba(99,102,241,0.05)' }}>
            <h3 className="heading-sm" style={{ marginBottom: '0.75rem', color: 'var(--color-primary-light)' }}>⚠️ Important Rules</h3>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {importantRules.map((rule, i) => (
                <li key={i} style={{ display: 'flex', gap: '0.625rem', fontSize: '0.875rem' }}>
                  <span style={{ color: 'var(--color-accent-light)' }}>✦</span>
                  <span>{typeof rule === 'object' ? rule.rule || JSON.stringify(rule) : rule}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Cultural Context (only if applicable) */}
        {culture?.isApplicable && culture.contextText && (
          <div style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
            <h4 style={{ color: 'var(--color-accent-light)', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 600 }}>🌸 Cultural Note</h4>
            <p style={{ fontSize: '0.875rem', lineHeight: 1.7 }}>{culture.contextText}</p>
            {culture.dosList?.length > 0 && (
              <div style={{ marginTop: '0.75rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-success-light)', marginBottom: '0.375rem' }}>✓ Do</div>
                {culture.dosList.map((d, i) => <div key={i} style={{ fontSize: '0.8rem' }}>• {d}</div>)}
              </div>
            )}
            {culture.dontsList?.length > 0 && (
              <div style={{ marginTop: '0.75rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-danger-light)', marginBottom: '0.375rem' }}>✗ Don't</div>
                {culture.dontsList.map((d, i) => <div key={i} style={{ fontSize: '0.8rem' }}>• {d}</div>)}
              </div>
            )}
          </div>
        )}

        {/* Summary */}
        {summary && (
          <div style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
            <h4 style={{ color: 'var(--color-success-light)', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 600 }}>✅ Lesson Summary</h4>
            <p style={{ fontSize: '0.875rem', lineHeight: 1.7 }}>{summary}</p>
          </div>
        )}

        {/* Checkpoint Questions (dynamic quiz) */}
        {checkpointQs.length > 0 && (
          <div>
            <h3 className="heading-sm" style={{ marginBottom: '1rem', color: 'var(--color-text-muted)' }}>📋 Checkpoint Questions</h3>
            {checkpointQs.map((q, i) => (
              <DynamicQuiz key={q.questionId || i} question={q} index={i}
                answer={answers[i]} onChange={v => setAnswers(p => ({ ...p, [i]: v }))}
                showResult={!!result} />
            ))}
          </div>
        )}
      </div>

      {/* Submit */}
      {!result && (
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Evaluating...</> : checkpointQs.length === 0 ? '✅ Mark as Complete' : '✅ Submit & Get Feedback'}
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
    <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
      <button className="btn btn-ghost btn-sm" onClick={goBack}>← Back</button>
      <div>
        <div style={BADGE_STYLE}>{label} • +{maxXP} XP</div>
        {title && <h1 className="heading-md" style={{ marginTop: '0.5rem' }}>{title}</h1>}
        {description && <p className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>{description}</p>}
      </div>
    </div>
  );
}

export function Spinner() {
  return <div style={{ textAlign: 'center', padding: '4rem' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>;
}

export function ContentMissing({ goBack }) {
  return (
    <div style={{ textAlign: 'center', padding: '4rem' }}>
      <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🚧</div>
      <h2 className="heading-md" style={{ marginBottom: '0.5rem' }}>Content Not Available Yet</h2>
      <p className="text-muted" style={{ marginBottom: '1.5rem' }}>The admin hasn't created this activity's content yet. Check back later!</p>
      <button className="btn btn-primary" onClick={goBack}>← Back to Roadmap</button>
    </div>
  );
}

export function LoadError({ goBack }) {
  return (
    <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-danger-light)' }}>
      <p>Failed to load activity. Please try again.</p>
      <button className="btn btn-secondary" style={{ marginTop: '1rem' }} onClick={goBack}>← Back</button>
    </div>
  );
}
