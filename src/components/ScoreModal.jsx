/**
 * src/components/ScoreModal.jsx
 * Displayed after an activity is submitted — shows Groq AI feedback + XP earned.
 *
 * Bug Fix #8: Overlay click no longer dismisses accidentally during scroll/drag.
 *   Uses mousedown+mouseup pair to confirm the click started AND ended on the overlay.
 */
import React, { useRef } from 'react';

export default function ScoreModal({ result, maxXP, onNext, onRetry, activityType }) {
  if (!result) return null;
  const { total_score, percentage, passed, feedback, suggestion } = result;
  const pct = Math.round(percentage);

  // Bug Fix #8: Track where mousedown started to prevent accidental dismiss
  const mouseDownTarget = useRef(null);

  const handleOverlayMouseDown = (e) => {
    mouseDownTarget.current = e.target;
  };

  const handleOverlayMouseUp = (e) => {
    // Only dismiss if BOTH mousedown and mouseup were on the overlay itself
    if (mouseDownTarget.current === e.currentTarget && e.target === e.currentTarget) {
      onNext();
    }
    mouseDownTarget.current = null;
  };

  // Color scheme based on tier
  const tierColors = {
    hint:   { bg: 'rgba(239,68,68,0.08)',   border: 'rgba(239,68,68,0.25)',   text: 'var(--color-danger-light)' },
    lesson: { bg: 'rgba(245,158,11,0.08)',  border: 'rgba(245,158,11,0.25)',  text: '#fbbf24' },
    praise: { bg: 'rgba(16,185,129,0.08)',  border: 'rgba(16,185,129,0.25)', text: 'var(--color-success-light)' },
  };
  const tier = result.feedback_tier || (passed ? 'praise' : 'lesson');
  const tierColor = tierColors[tier] || tierColors.lesson;

  return (
    <div
      className="modal-overlay"
      onMouseDown={handleOverlayMouseDown}
      onMouseUp={handleOverlayMouseUp}
    >
      <div
        className="modal-box animate-fade-in"
        style={{ textAlign: 'center' }}
        onClick={e => e.stopPropagation()}
      >
        {/* Result icon */}
        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>
          {passed ? '🎉' : pct >= 50 ? '📚' : '💡'}
        </div>

        {/* Title */}
        <h2 className="heading-md" style={{ marginBottom: '0.5rem', color: passed ? 'var(--color-success-light)' : 'var(--color-danger-light)' }}>
          {passed ? 'Activity Passed!' : 'Not Quite There Yet'}
        </h2>

        {/* Score ring */}
        <div style={{ margin: '1.5rem auto', position: 'relative', width: 120, height: 120 }}>
          <svg width="120" height="120" style={{ transform: 'rotate(-90deg)' }}>
            <circle cx="60" cy="60" r="52" fill="none" stroke="var(--color-surface-3)" strokeWidth="8" />
            <circle
              cx="60" cy="60" r="52" fill="none"
              stroke={passed ? 'var(--color-success)' : 'var(--color-danger)'}
              strokeWidth="8"
              strokeDasharray={`${2 * Math.PI * 52}`}
              strokeDashoffset={`${2 * Math.PI * 52 * (1 - pct / 100)}`}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 1s ease' }}
            />
          </svg>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>{pct}%</span>
            <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>score</span>
          </div>
        </div>

        {/* XP earned */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--color-accent-glow)', border: '1px solid var(--color-accent)', borderRadius: 'var(--radius-full)', padding: '0.375rem 1rem', marginBottom: '1.25rem' }}>
          <span style={{ fontSize: '1.1rem' }}>⭐</span>
          <span style={{ fontWeight: 700, color: 'var(--color-accent-light)' }}>+{total_score} XP</span>
          <span style={{ color: 'var(--color-text-dim)', fontSize: '0.8rem' }}>/ {maxXP}</span>
        </div>

        {/* Feedback */}
        <div style={{ background: tierColor.bg, border: `1px solid ${tierColor.border}`, borderRadius: 'var(--radius-md)', padding: '1rem', marginBottom: '0.75rem', textAlign: 'left' }}>
          <p style={{ fontSize: '0.875rem', lineHeight: 1.6, color: tierColor.text }}>{feedback}</p>
        </div>

        {/* Suggestion */}
        {suggestion && (
          <div style={{ background: 'rgba(6,182,212,0.08)', border: '1px solid rgba(6,182,212,0.2)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', marginBottom: '1.5rem', textAlign: 'left' }}>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-secondary-light)' }}>
              💡 <strong>Tip:</strong> {suggestion}
            </p>
          </div>
        )}

        {/* Pass threshold notice */}
        {!passed && (
          <p style={{ fontSize: '0.8rem', color: 'var(--color-text-dim)', marginBottom: '1rem' }}>
            You need 50% to pass. You scored {pct}%.
          </p>
        )}

        {/* Action buttons */}
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
          {!passed && onRetry && (
            <button className="btn btn-secondary" onClick={onRetry}>🔄 Try Again</button>
          )}
          <button className="btn btn-primary" onClick={onNext}>
            {passed ? '➡ Continue' : '📖 Back to Activity'}
          </button>
        </div>
      </div>
    </div>
  );
}
