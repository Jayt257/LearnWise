import React, { useEffect, useState } from 'react';

const STAR_COUNT = 30;

function randomBetween(min, max) {
  return Math.round(min + Math.random() * (max - min));
}

export default function XPBurst({ x = 0, y = 0, active = false }) {
  const [particles, setParticles] = useState([]);

  useEffect(() => {
    if (!active) return;
    const pts = Array.from({ length: STAR_COUNT }, (_, i) => {
      const angle = (i / STAR_COUNT) * 360;
      const dist  = randomBetween(20, 150);
      const rad   = (angle * Math.PI) / 180;
      return {
        id: i,
        tx: Math.cos(rad) * dist,
        ty: Math.sin(rad) * dist,
        size: randomBetween(3, 8),
        delay: randomBetween(0, 150),
        color: ['#CEFA05','#00DFF0','#FF00EB','#FFB000','#FFBA00'][i % 5],
      };
    });
    setParticles(pts);
    const t = setTimeout(() => setParticles([]), 1500);
    return () => clearTimeout(t);
  }, [active]);

  if (!particles.length) return null;

  return (
    <div
      style={{
        position: 'fixed',
        left: x,
        top: y,
        pointerEvents: 'none',
        zIndex: 9999,
      }}
      aria-hidden="true"
    >
      {particles.map(p => (
        <div
          key={p.id}
          style={{
            position: 'absolute',
            width: p.size,
            height: p.size,
            borderRadius: '50%',
            background: p.color,
            '--tx': `${p.tx}px`,
            '--ty': `${p.ty}px`,
            animation: `confettiBurst 0.8s ease-out ${p.delay}ms forwards`,
            boxShadow: `0 0 8px ${p.color}`,
          }}
        />
      ))}
    </div>
  );
}
