/**
 * src/components/ScoreModal.jsx
 * In-page result card shown after activity submission.
 * Shows score ring, XP earned, pass/fail, and CTA buttons.
 */
import React from 'react';

const ACTIVITY_PRAISE = {
  lesson: "You've absorbed the lesson content! 📖",
  vocabulary: "Your vocabulary is growing! 🔤",
  pronunciation: "Your pronunciation practice counts! 🗣",
  reading: "Your reading comprehension improved! 📄",
  writing: "Great writing effort! ✍",
  listening: "Your listening is sharpening! 🎧",
  speaking: "Speaking practice builds confidence! 🎙",
  test: "You completed the block test! 📋",
};

export default function ScoreModal({ result, maxXP, onNext, onRetry, activityType }) {
  if (!result) return null;

  const percent = Math.round(result.percentage || 0);
  const passed = result.passed;
  const earned = result.total_score || 0;
  const tier = result.feedback_tier || (passed ? 'praise' : 'lesson');

  const ringColor = passed ? 'var(--color-success-light)' : percent >= 50 ? 'var(--color-accent-light)' : 'var(--color-danger-light)';
  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (percent / 100) * circumference;

  return (
    <div style={{ marginTop: '2rem', padding: '1.5rem', borderRadius: 'var(--radius-lg)', background: passed ? 'rgba(16,185,129,0.06)' : 'rgba(239,68,68,0.06)', border: `1px solid ${passed ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.25)'}` }}>
      <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
        {/* Score ring */}
        <div style={{ position: 'relative', width: 100, height: 100, flexShrink: 0 }}>
          <svg width="100" height="100" style={{ transform: 'rotate(-90deg)' }}>
            <circle cx="50" cy="50" r="40" fill="none" stroke="var(--color-border)" strokeWidth="8" />
            <circle cx="50" cy="50" r="40" fill="none" stroke={ringColor} strokeWidth="8"
              strokeDasharray={circumference} strokeDashoffset={strokeDashoffset}
              strokeLinecap="round" style={{ transition: 'stroke-dashoffset 1s ease' }} />
          </svg>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
            <span style={{ fontWeight: 800, fontSize: '1.25rem', color: ringColor }}>{percent}</span>
            <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>%</span>
          </div>
        </div>

        {/* Result info */}
        <div style={{ flex: 1, minWidth: 180 }}>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.25rem' }}>
            {passed ? '🎉 Passed!' : '📚 Keep Practicing'}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
            {ACTIVITY_PRAISE[activityType] || 'Activity completed!'}
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ background: 'var(--color-accent-glow)', border: '1px solid var(--color-accent)', color: 'var(--color-accent-light)', borderRadius: 'var(--radius-full)', padding: '0.2rem 0.625rem', fontSize: '0.8rem', fontWeight: 700 }}>
              +{earned} XP
            </span>
            <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{earned} / {maxXP} max XP</span>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div style={{ marginTop: '1.25rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
        {passed ? (
          <button className="btn btn-primary" onClick={onNext}>Continue →</button>
        ) : (
          <>
            <button className="btn btn-ghost" onClick={onRetry}>↩ Try Again</button>
            <button className="btn btn-primary" onClick={onNext}>View Feedback & Continue</button>
          </>
        )}
      </div>
    </div>
  );
}
