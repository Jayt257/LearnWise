/**
 * src/components/ActivityFeedback.jsx
 * Post-activity contextual feedback notification panel.
 *
 * 3 tiers driven by result.feedback_tier from the backend:
 *   🔴 hint   — failed multiple times; actionable next-try hints
 *   🟡 lesson — moderate score (50–79%); brief mini-lesson on concept
 *   🟢 praise — high score (≥80%); celebration + advanced mastery tip
 *
 * Features:
 *  - Animated slide-in from right
 *  - Auto-dismiss countdown for praise tier (15s)
 *  - Swipe-to-dismiss on mobile
 *  - Progress bar for auto-dismiss
 *  - X button always visible
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';

const TIER_CONFIG = {
  hint: {
    icon: '💡',
    label: 'Keep Trying',
    accent: '#ef4444',
    accentLight: '#fca5a5',
    accentGlow: 'rgba(239,68,68,0.12)',
    border: 'rgba(239,68,68,0.35)',
    headerBg: 'rgba(239,68,68,0.18)',
    autoDismiss: false,
    emoji: '🔴',
    subtitle: 'Here\'s what to focus on next time',
  },
  lesson: {
    icon: '📚',
    label: 'Quick Lesson',
    accent: '#f59e0b',
    accentLight: '#fbbf24',
    accentGlow: 'rgba(245,158,11,0.12)',
    border: 'rgba(245,158,11,0.35)',
    headerBg: 'rgba(245,158,11,0.18)',
    autoDismiss: false,
    emoji: '🟡',
    subtitle: 'A concept to help you improve',
  },
  praise: {
    icon: '🏆',
    label: 'Excellent Work!',
    accent: '#10b981',
    accentLight: '#6ee7b7',
    accentGlow: 'rgba(16,185,129,0.12)',
    border: 'rgba(16,185,129,0.35)',
    headerBg: 'rgba(16,185,129,0.18)',
    autoDismiss: true,
    autoDismissSeconds: 15,
    emoji: '🟢',
    subtitle: 'You\'re on fire! Keep up the great work',
  },
};

export default function ActivityFeedback({ result, activityType, onDismiss }) {
  if (!result) return null;

  const tier = result.feedback_tier || (result.passed ? 'praise' : 'lesson');
  const config = TIER_CONFIG[tier] || TIER_CONFIG.lesson;

  const [visible, setVisible] = useState(false);
  const [countdown, setCountdown] = useState(config.autoDismissSeconds || 15);
  const [progress, setProgress] = useState(100);
  const intervalRef = useRef(null);
  const panelRef = useRef(null);

  // Touch swipe-to-dismiss
  const touchStartX = useRef(null);

  const dismiss = useCallback(() => {
    setVisible(false);
    setTimeout(onDismiss, 300); // Allow slide-out animation
  }, [onDismiss]);

  // Slide in on mount
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 50);
    return () => clearTimeout(t);
  }, []);

  // Auto-dismiss countdown for praise tier
  useEffect(() => {
    if (!config.autoDismiss) return;
    const total = config.autoDismissSeconds * 1000;
    const tick = 100;
    let elapsed = 0;

    intervalRef.current = setInterval(() => {
      elapsed += tick;
      const remaining = Math.ceil((total - elapsed) / 1000);
      setCountdown(remaining);
      setProgress(Math.max(0, 100 - (elapsed / total) * 100));
      if (elapsed >= total) {
        clearInterval(intervalRef.current);
        dismiss();
      }
    }, tick);

    return () => clearInterval(intervalRef.current);
  }, [config.autoDismiss, config.autoDismissSeconds, dismiss]);

  const handleTouchStart = (e) => { touchStartX.current = e.touches[0].clientX; };
  const handleTouchEnd = (e) => {
    if (touchStartX.current === null) return;
    const diff = e.changedTouches[0].clientX - touchStartX.current;
    if (diff > 80) dismiss(); // Swipe right to dismiss
    touchStartX.current = null;
  };

  const { feedback, suggestion, total_score, max_score, percentage } = result;
  const pct = Math.round(percentage);
  const activityLabels = {
    lesson: 'Lesson', vocab: 'Vocabulary', reading: 'Reading',
    writing: 'Writing', listening: 'Listening', speaking: 'Speaking',
    pronunciation: 'Pronunciation', test: 'Test',
  };

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={dismiss}
        style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
          zIndex: 1200, opacity: visible ? 1 : 0,
          transition: 'opacity 0.3s ease',
        }}
      />

      {/* Slide-in panel from right */}
      <div
        ref={panelRef}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        style={{
          position: 'fixed',
          top: 0, right: 0, bottom: 0,
          width: 'min(420px, 100vw)',
          background: 'var(--color-surface)',
          borderLeft: `1px solid ${config.border}`,
          boxShadow: `-8px 0 40px rgba(0,0,0,0.5)`,
          zIndex: 1201,
          display: 'flex', flexDirection: 'column',
          transform: visible ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.35s cubic-bezier(0.16,1,0.3,1)',
          overflowY: 'auto',
        }}
      >
        {/* Auto-dismiss progress bar */}
        {config.autoDismiss && (
          <div style={{ height: 3, background: 'var(--color-surface-2)', flexShrink: 0 }}>
            <div style={{
              height: '100%', width: `${progress}%`,
              background: config.accent,
              transition: 'width 0.1s linear',
            }} />
          </div>
        )}

        {/* Header */}
        <div style={{
          padding: '1.5rem',
          background: config.headerBg,
          borderBottom: `1px solid ${config.border}`,
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '2rem' }}>{config.icon}</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1.05rem', color: config.accentLight }}>
                  {config.label}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginTop: '0.125rem' }}>
                  {activityLabels[activityType] || activityType} · {pct}% · {total_score} XP
                </div>
              </div>
            </div>
            <button
              onClick={dismiss}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-dim)', fontSize: '1.25rem', padding: '0.25rem', lineHeight: 1 }}
              aria-label="Dismiss feedback"
            >
              ✕
            </button>
          </div>
          {config.autoDismiss && (
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', marginTop: '0.625rem' }}>
              Auto-closing in {countdown}s · Swipe right to dismiss
            </p>
          )}
        </div>

        {/* Body */}
        <div style={{ padding: '1.5rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Subtitle */}
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
            {config.subtitle}
          </p>

          {/* Main feedback */}
          <div style={{
            background: config.accentGlow,
            border: `1px solid ${config.border}`,
            borderRadius: 'var(--radius-md)',
            padding: '1.125rem',
          }}>
            <div style={{ display: 'flex', gap: '0.625rem', alignItems: 'flex-start' }}>
              <span style={{ fontSize: '1.1rem', flexShrink: 0, marginTop: '0.05rem' }}>
                {tier === 'hint' ? '🎯' : tier === 'lesson' ? '💡' : '🌟'}
              </span>
              <p style={{ fontSize: '0.9rem', lineHeight: 1.7, color: 'var(--color-text)' }}>
                {feedback}
              </p>
            </div>
          </div>

          {/* Suggestion / tip */}
          {suggestion && (
            <div style={{
              background: 'var(--color-surface-2)',
              borderRadius: 'var(--radius-md)',
              padding: '1rem 1.125rem',
              borderLeft: `3px solid ${config.accent}`,
            }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: config.accentLight, marginBottom: '0.375rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {tier === 'hint' ? 'Next Step' : tier === 'lesson' ? 'Practice Tip' : 'Go Further'}
              </div>
              <p style={{ fontSize: '0.875rem', lineHeight: 1.6, color: 'var(--color-text-muted)' }}>
                {suggestion}
              </p>
            </div>
          )}

          {/* Score breakdown */}
          <div style={{
            background: 'var(--color-surface-2)',
            borderRadius: 'var(--radius-md)',
            padding: '1rem',
          }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-muted)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Score Breakdown
            </div>
            <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
              <div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: config.accentLight }}>{pct}%</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>Accuracy</div>
              </div>
              <div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-accent-light)' }}>+{total_score}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>XP Earned</div>
              </div>
              <div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: result.passed ? 'var(--color-success-light)' : 'var(--color-danger-light)' }}>
                  {result.passed ? '✓' : '✗'}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)' }}>{result.passed ? 'Passed' : 'Try Again'}</div>
              </div>
            </div>
          </div>

          {/* Motivational quote by tier */}
          <div style={{ fontSize: '0.8rem', color: 'var(--color-text-dim)', textAlign: 'center', fontStyle: 'italic', padding: '0.5rem 0' }}>
            {tier === 'hint' && '"Every expert was once a beginner. Keep going!"'}
            {tier === 'lesson' && '"Progress, not perfection. You\'re getting better!"'}
            {tier === 'praise' && '"Outstanding! You\'re mastering this language!"'}
          </div>
        </div>

        {/* Footer CTA */}
        <div style={{ padding: '1.25rem 1.5rem', borderTop: '1px solid var(--color-border)', flexShrink: 0 }}>
          <button
            className="btn btn-primary"
            onClick={dismiss}
            style={{
              width: '100%',
              background: `linear-gradient(135deg, ${config.accent}, ${config.accent}cc)`,
              border: 'none',
            }}
          >
            {result.passed ? '➡ Back to Roadmap' : '🔄 Continue Learning'}
          </button>
        </div>
      </div>
    </>
  );
}
