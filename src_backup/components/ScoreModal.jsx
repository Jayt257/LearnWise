/
  src/components/ScoreModal.jsx
  In-page result card — animated SVG ring, XP burst, premium typography.
  All scoring logic (passed, percent, earned, tier) is untouched.
 /
import React, { useEffect, useRef, useState } from 'react';
import XPBurst from './XPBurst.jsx';

const ACTIVITY_PRAISE = {
  lesson:       "You've absorbed the lesson content! ",
  vocabulary:   "Your vocabulary is growing! ",
  pronunciation:"Your pronunciation practice counts! ",
  reading:      "Your reading comprehension improved! ",
  writing:      "Great writing effort! ",
  listening:    "Your listening is sharpening! ",
  speaking:     "Speaking practice builds confidence! ",
  test:         "You completed the block test! ",
};

export default function ScoreModal({ result, maxXP, onNext, onRetry, activityType }) {
  const xpBadgeRef = useRef(null);
  const [burstActive, setBurstActive] = useState(false);
  const [burstPos, setBurstPos] = useState({ x: , y:  });
  const [ringOffset, setRingOffset] = useState(.);

  if (!result) return null;

  const percent  = Math.round(result.percentage || );
  const passed   = result.passed;
  const earned   = result.total_score || ;

  const ringColor = passed
    ? 'var(--success)'
    : percent >= 
      ? 'var(--warning)'
      : 'var(--danger)';

  const circumference =   Math.PI  ; // ~.

  // Animate ring draw + trigger XP burst after short delay
  useEffect(() => {
    const target = circumference - (percent / )  circumference;
    // Small delay so transition is visible
    const t = setTimeout(() => setRingOffset(target), );
    // Trigger XP burst if passed
    if (passed) {
      const t = setTimeout(() => {
        if (xpBadgeRef.current) {
          const rect = xpBadgeRef.current.getBoundingClientRect();
          setBurstPos({ x: rect.left + rect.width / , y: rect.top + rect.height /  });
          setBurstActive(true);
          setTimeout(() => setBurstActive(false), );
        }
      }, );
      return () => { clearTimeout(t); clearTimeout(t); };
    }
    return () => clearTimeout(t);
  }, [percent, passed]);

  const bgColor   = passed ? 'rgba(,,,.)' : percent >=  ? 'rgba(,,,.)' : 'rgba(,,,.)';
  const bdColor   = passed ? 'rgba(,,,.)' : percent >=  ? 'rgba(,,,.)' : 'rgba(,,,.)';

  return (
    <>
      <XPBurst x={burstPos.x} y={burstPos.y} active={burstActive} />

      <div
        className="animate-fade-up"
        style={{
          marginTop: 'rem',
          padding: '.rem',
          borderRadius: 'var(--radius-lg)',
          background: bgColor,
          border: `px solid ${bdColor}`,
          backdropFilter: 'blur(px)',
        }}
      >
        <div style={{ display: 'flex', gap: '.rem', alignItems: 'center', flexWrap: 'wrap' }}>
          {/ Animated score ring /}
          <div style={{ position: 'relative', width: , height: , flexShrink:  }}>
            <svg width="" height="" style={{ transform: 'rotate(-deg)' }}>
              <circle cx="" cy="" r="" fill="none" stroke="var(--border)" strokeWidth="" />
              <circle
                cx="" cy="" r=""
                fill="none"
                stroke={ringColor}
                strokeWidth=""
                strokeDasharray={circumference}
                strokeDashoffset={ringOffset}
                strokeLinecap="round"
                style={{ transition: 'stroke-dashoffset .s cubic-bezier(.,,.,)' }}
              />
            </svg>
            <div style={{
              position: 'absolute', inset: ,
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column',
            }}>
              <span style={{
                fontFamily: 'var(--font-display)',
                fontWeight: ,
                fontSize: '.rem',
                color: ringColor,
                lineHeight: ,
              }}>
                {percent}
              </span>
              <span style={{ fontSize: '.rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>%</span>
            </div>
          </div>

          {/ Result info /}
          <div style={{ flex: , minWidth:  }}>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: '.rem',
              fontWeight: ,
              marginBottom: '.rem',
              color: ringColor,
            }}>
              {passed ? ' Passed!' : percent >=  ? ' Almost There' : ' Keep Practicing'}
            </div>
            <div style={{ fontSize: '.rem', color: 'var(--text-muted)', marginBottom: '.rem' }}>
              {ACTIVITY_PRAISE[activityType] || 'Activity completed!'}
            </div>

            <div style={{ display: 'flex', gap: '.rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <span
                ref={xpBadgeRef}
                style={{
                  background: 'var(--amber-glow)',
                  border: 'px solid var(--amber)',
                  color: 'var(--amber)',
                  borderRadius: 'var(--radius-full)',
                  padding: '.rem .rem',
                  fontSize: '.rem',
                  fontWeight: ,
                  fontFamily: 'var(--font-mono)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '.rem',
                }}
              >
                 +{earned} XP
              </span>
              <span style={{ fontSize: '.rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                {earned} / {maxXP} max
              </span>
            </div>
          </div>
        </div>

        {/ Action buttons /}
        <div style={{ marginTop: '.rem', display: 'flex', gap: '.rem', flexWrap: 'wrap' }}>
          {passed ? (
            <button className="btn btn-primary" onClick={onNext}>
              Continue →
            </button>
          ) : (
            <>
              <button className="btn btn-ghost" onClick={onRetry}> Try Again</button>
              <button className="btn btn-primary" onClick={onNext}>View Feedback & Continue</button>
            </>
          )}
        </div>
      </div>
    </>
  );
}
