/
  src/components/XPBurst.jsx
  Confetti-star burst when XP is earned.
  Usage: <XPBurst key={trigger} />   (change key to re-trigger)
 /
import React, { useEffect, useState } from 'react';

const STAR_COUNT = ;

function randomBetween(min, max) {
  return Math.round(min + Math.random()  (max - min));
}

export default function XPBurst({ x = , y = , active = false }) {
  const [particles, setParticles] = useState([]);

  useEffect(() => {
    if (!active) return;
    const pts = Array.from({ length: STAR_COUNT }, (_, i) => {
      const angle = (i / STAR_COUNT)  ;
      const dist  = randomBetween(, );
      const rad   = (angle  Math.PI) / ;
      return {
        id: i,
        tx: Math.cos(rad)  dist,
        ty: Math.sin(rad)  dist,
        size: randomBetween(, ),
        delay: randomBetween(, ),
        color: ['CEFA','DFF','EB','FFB','FFBA'][i % ],
      };
    });
    setParticles(pts);
    const t = setTimeout(() => setParticles([]), );
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
        zIndex: ,
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
            borderRadius: '%',
            background: p.color,
            '--tx': `${p.tx}px`,
            '--ty': `${p.ty}px`,
            animation: `confettiBurst .s ease-out ${p.delay}ms forwards`,
            boxShadow: `  px ${p.color}`,
          }}
        />
      ))}
    </div>
  );
}
