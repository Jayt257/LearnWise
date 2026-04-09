/**
 * src/components/ActivityFeedback.jsx
 * Detailed AI feedback panel shown after activity submission.
 * Dismisses to dashboard. Shows feedback, suggestion, per-question results.
 */
import React from 'react';

const TIER_CONFIG = {
  hint:    { icon: '💡', color: 'var(--color-accent-light)',   bg: 'rgba(245,158,11,0.06)',   border: 'rgba(245,158,11,0.25)' },
  lesson:  { icon: '📖', color: 'var(--color-primary-light)',  bg: 'rgba(99,102,241,0.06)',   border: 'rgba(99,102,241,0.25)' },
  praise:  { icon: '⭐', color: 'var(--color-success-light)',  bg: 'rgba(16,185,129,0.06)',   border: 'rgba(16,185,129,0.25)' },
};

export default function ActivityFeedback({ result, activityType, onDismiss }) {
  if (!result) return null;

  const tier = result.feedback_tier || (result.passed ? 'praise' : 'lesson');
  const config = TIER_CONFIG[tier] || TIER_CONFIG.lesson;
  const questionResults = result.question_results || [];

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', zIndex: 200, padding: '1rem' }}
      onClick={onDismiss}>
      <div style={{ background: 'var(--color-surface)', borderRadius: 'var(--radius-lg) var(--radius-lg) 0 0', padding: '1.5rem', width: '100%', maxWidth: 620, maxHeight: '80vh', overflowY: 'auto', boxShadow: '0 -8px 32px rgba(0,0,0,0.5)' }}
        onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h3 style={{ fontWeight: 700, fontSize: '1.1rem', margin: 0 }}>AI Feedback {config.icon}</h3>
          <button className="btn btn-ghost btn-sm" onClick={onDismiss}>✕ Close</button>
        </div>

        {/* Main feedback */}
        {result.feedback && (
          <div style={{ background: config.bg, border: `1px solid ${config.border}`, borderRadius: 'var(--radius-md)', padding: '1rem', marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: config.color, marginBottom: '0.375rem' }}>Overall Feedback</div>
            <p style={{ fontSize: '0.9rem', lineHeight: 1.7 }}>{result.feedback}</p>
          </div>
        )}

        {/* Suggestion */}
        {result.suggestion && (
          <div style={{ background: 'var(--color-surface-2)', borderRadius: 'var(--radius-md)', padding: '0.875rem', marginBottom: '1.25rem' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-text-muted)', marginBottom: '0.375rem' }}>💬 Suggestion</div>
            <p style={{ fontSize: '0.875rem', lineHeight: 1.7 }}>{result.suggestion}</p>
          </div>
        )}

        {/* Per-question breakdown */}
        {questionResults.length > 0 && (
          <div>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--color-text-muted)' }}>Question Results</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
              {questionResults.map((qr, i) => (
                <div key={i} style={{ display: 'flex', gap: '0.625rem', padding: '0.625rem', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)' }}>
                  <span style={{ flexShrink: 0, fontSize: '1rem' }}>{qr.correct ? '✅' : '❌'}</span>
                  <div style={{ flex: 1, fontSize: '0.8rem' }}>
                    {qr.prompt && <div style={{ color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>{qr.prompt}</div>}
                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                      <span>Your: <strong>{qr.user_answer || '—'}</strong></span>
                      {!qr.correct && qr.correct_answer && <span style={{ color: 'var(--color-success-light)' }}>Expected: <strong>{qr.correct_answer}</strong></span>}
                    </div>
                    {qr.ai_comment && <div style={{ marginTop: '0.25rem', color: 'var(--color-accent-light)', fontStyle: 'italic' }}>{qr.ai_comment}</div>}
                  </div>
                  {typeof qr.score !== 'undefined' && (
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-primary-light)', flexShrink: 0 }}>{qr.score}pts</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <button className="btn btn-primary" style={{ width: '100%', marginTop: '1.5rem' }} onClick={onDismiss}>
          ← Back to Roadmap
        </button>
      </div>
    </div>
  );
}
