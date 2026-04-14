/
  src/components/ActivityFeedback.jsx
  Detailed AI feedback panel shown after activity submission.
  Dismisses to dashboard. Shows feedback, suggestion, per-question results.
 /
import React from 'react';

const TIER_CONFIG = {
  hint:    { icon: '', color: 'var(--color-accent-light)',   bg: 'rgba(,,,.)',   border: 'rgba(,,,.)' },
  lesson:  { icon: '', color: 'var(--color-primary-light)',  bg: 'rgba(,,,.)',   border: 'rgba(,,,.)' },
  praise:  { icon: '', color: 'var(--color-success-light)',  bg: 'rgba(,,,.)',   border: 'rgba(,,,.)' },
};

export default function ActivityFeedback({ result, activityType, onDismiss }) {
  if (!result) return null;

  const tier = result.feedback_tier || (result.passed ? 'praise' : 'lesson');
  const config = TIER_CONFIG[tier] || TIER_CONFIG.lesson;
  const questionResults = result.question_results || [];

  return (
    <div style={{ position: 'fixed', inset: , background: 'rgba(,,,.)', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', zIndex: , padding: 'rem' }}
      onClick={onDismiss}>
      <div style={{ background: 'var(--color-surface)', borderRadius: 'var(--radius-lg) var(--radius-lg)  ', padding: '.rem', width: '%', maxWidth: , maxHeight: 'vh', overflowY: 'auto', boxShadow: ' -px px rgba(,,,.)' }}
        onClick={e => e.stopPropagation()}>

        {/ Header /}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '.rem' }}>
          <h style={{ fontWeight: , fontSize: '.rem', margin:  }}>AI Feedback {config.icon}</h>
          <button className="btn btn-ghost btn-sm" onClick={onDismiss}>✕ Close</button>
        </div>

        {/ Main feedback /}
        {result.feedback && (
          <div style={{ background: config.bg, border: `px solid ${config.border}`, borderRadius: 'var(--radius-md)', padding: 'rem', marginBottom: 'rem' }}>
            <div style={{ fontSize: '.rem', fontWeight: , textTransform: 'uppercase', color: config.color, marginBottom: '.rem' }}>Overall Feedback</div>
            <p style={{ fontSize: '.rem', lineHeight: . }}>{result.feedback}</p>
          </div>
        )}

        {/ Suggestion /}
        {result.suggestion && (
          <div style={{ background: 'var(--color-surface-)', borderRadius: 'var(--radius-md)', padding: '.rem', marginBottom: '.rem' }}>
            <div style={{ fontSize: '.rem', fontWeight: , textTransform: 'uppercase', color: 'var(--color-text-muted)', marginBottom: '.rem' }}> Suggestion</div>
            <p style={{ fontSize: '.rem', lineHeight: . }}>{result.suggestion}</p>
          </div>
        )}

        {/ Per-question breakdown /}
        {questionResults.length >  && (
          <div>
            <h style={{ fontSize: '.rem', fontWeight: , marginBottom: '.rem', color: 'var(--color-text-muted)' }}>Question Results</h>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '.rem' }}>
              {questionResults.map((qr, i) => (
                <div key={i} style={{ display: 'flex', gap: '.rem', padding: '.rem', background: 'var(--color-surface-)', borderRadius: 'var(--radius-sm)' }}>
                  <span style={{ flexShrink: , fontSize: 'rem' }}>{qr.correct ? '' : ''}</span>
                  <div style={{ flex: , fontSize: '.rem' }}>
                    {qr.prompt && <div style={{ color: 'var(--color-text-muted)', marginBottom: '.rem' }}>{qr.prompt}</div>}
                    <div style={{ display: 'flex', gap: 'rem', flexWrap: 'wrap' }}>
                      <span>Your: <strong>{qr.user_answer || '—'}</strong></span>
                      {!qr.correct && qr.correct_answer && <span style={{ color: 'var(--color-success-light)' }}>Expected: <strong>{qr.correct_answer}</strong></span>}
                    </div>
                    {qr.ai_comment && <div style={{ marginTop: '.rem', color: 'var(--color-accent-light)', fontStyle: 'italic' }}>{qr.ai_comment}</div>}
                  </div>
                  {typeof qr.score !== 'undefined' && (
                    <span style={{ fontSize: '.rem', fontWeight: , color: 'var(--color-primary-light)', flexShrink:  }}>{qr.score}pts</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <button className="btn btn-primary" style={{ width: '%', marginTop: '.rem' }} onClick={onDismiss}>
          ← Back to Roadmap
        </button>
      </div>
    </div>
  );
}
