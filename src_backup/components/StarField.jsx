/
  src/components/StarField.jsx
  Animated parallax star background — CSS only, no canvas.
  Only visible in dark mode. Renders below all content (z-index:).
 /
import React from 'react';

export default function StarField() {
  return (
    <div className="star-bg" aria-hidden="true">
      {/ Three parallax layers at different speeds /}
      <div className="stars-layer stars-small" />
      <div className="stars-layer stars-med" />
      <div className="stars-layer stars-large" />

      {/ Ambient orbs for atmospheric depth /}
      <div
        className="ambient-orb"
        style={{
          width: , height: ,
          left: '-%', top: '%',
          background: 'radial-gradient(circle, rgba(,,,.) %, transparent %)',
          '--orb-duration': 's',
          '--orb-delay': 's',
        }}
      />
      <div
        className="ambient-orb"
        style={{
          width: , height: ,
          right: '-%', top: '%',
          background: 'radial-gradient(circle, rgba(,,,.) %, transparent %)',
          '--orb-duration': 's',
          '--orb-delay': 's',
        }}
      />
      <div
        className="ambient-orb"
        style={{
          width: , height: ,
          left: '%', bottom: '%',
          background: 'radial-gradient(circle, rgba(,,,.) %, transparent %)',
          '--orb-duration': 's',
          '--orb-delay': 's',
        }}
      />
    </div>
  );
}
