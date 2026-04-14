/
  src/components/NebulaWeb.jsx
  Interactive canvas — floating particles connected by lines (web/constellation).
  Cursor repels nearby particles. Nebula cloud blobs as soft background color.
  Replaces the old CSS StarField.
 /
import React, { useEffect, useRef, useCallback } from 'react';
import { useTheme } from '../hooks/useTheme.js';

const PARTICLE_COUNT   = ;
const CONNECT_DISTANCE = ;
const MOUSE_RADIUS     = ;
const MOUSE_STRENGTH   = .;
const BASE_SPEED       = .;

function createParticle(w, h) {
  const vx = (Math.random() - .)  BASE_SPEED;
  const vy = (Math.random() - .)  BASE_SPEED;
  return {
    x:  Math.random()  w,
    y:  Math.random()  h,
    vx: vx,
    vy: vy,
    baseVx: vx,
    baseVy: vy,
    radius: Math.random()  . + .,
    opacity: Math.random()  . + .,
  };
}

export default function NebulaWeb() {
  const canvasRef  = useRef(null);
  const mouse      = useRef({ x: -, y: - });
  const particles  = useRef([]);
  const animId     = useRef(null);
  const { isDark } = useTheme();

  const draw = useCallback((ctx, w, h) => {
    ctx.clearRect(, , w, h);

    / ── Nebula cloud blobs ──────────────────────────────── /
    const clouds = [
      { x: w  ., y: h  ., r: Math.min(w, h)  ., c: isDark ? 'rgba(,,,.)' : 'rgba(,,,.)' },
      { x: w  ., y: h  ., r: Math.min(w, h)  ., c: isDark ? 'rgba(,,,.)' : 'rgba(,,,.)' },
      { x: w  ., y: h  ., r: Math.min(w, h)  ., c: isDark ? 'rgba(,,,.)' : 'rgba(,,,.)' },
    ];
    clouds.forEach(cl => {
      const g = ctx.createRadialGradient(cl.x, cl.y, , cl.x, cl.y, cl.r);
      g.addColorStop(, cl.c);
      g.addColorStop(, 'transparent');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(cl.x, cl.y, cl.r, , Math.PI  );
      ctx.fill();
    });

    const pts = particles.current;
    const mx  = mouse.current.x;
    const my  = mouse.current.y;

    / ── Update positions ────────────────────────────────── /
    pts.forEach(p => {
      const dx   = p.x - mx;
      const dy   = p.y - my;
      const dist = Math.sqrt(dx  dx + dy  dy);

      if (dist < MOUSE_RADIUS && dist > ) {
        const force = (MOUSE_RADIUS - dist) / MOUSE_RADIUS;
        p.vx += (dx / dist)  force  MOUSE_STRENGTH  .;
        p.vy += (dy / dist)  force  MOUSE_STRENGTH  .;
      }

      // Instead of absolute dampening, slowly return to original base velocity
      const angle = Math.atan(p.baseVy, p.baseVx);
      const baseSpeed = Math.sqrt(p.baseVx  p.baseVx + p.baseVy  p.baseVy);
      
      p.vx = p.vx  . + (Math.cos(angle)  baseSpeed)  .;
      p.vy = p.vy  . + (Math.sin(angle)  baseSpeed)  .;

      // Clamp max speed from mouse interaction
      const speed = Math.sqrt(p.vx  p.vx + p.vy  p.vy);
      if (speed > .) { p.vx = (p.vx / speed)  .; p.vy = (p.vy / speed)  .; }

      p.x += p.vx;
      p.y += p.vy;

      // Wrap at edges
      if (p.x < )  p.x = w;
      if (p.x > w)  p.x = ;
      if (p.y < )  p.y = h;
      if (p.y > h)  p.y = ;
    });

    / ── Draw connection lines ───────────────────────────── /
    const lineAlphaScale = isDark ? . : .;
    for (let i = ; i < pts.length; i++) {
      for (let j = i + ; j < pts.length; j++) {
        const dx   = pts[i].x - pts[j].x;
        const dy   = pts[i].y - pts[j].y;
        const dist = Math.sqrt(dx  dx + dy  dy);

        if (dist < CONNECT_DISTANCE) {
          const alpha = ( - dist / CONNECT_DISTANCE)  lineAlphaScale;
          ctx.beginPath();
          ctx.moveTo(pts[i].x, pts[i].y);
          ctx.lineTo(pts[j].x, pts[j].y);
          ctx.strokeStyle = isDark
            ? `rgba(,,,${alpha})`
            : `rgba(,,,${alpha})`;
          ctx.lineWidth = .;
          ctx.stroke();
        }
      }
    }

    / ── Draw particles ──────────────────────────────────── /
    pts.forEach(p => {
      // Glow halo
      const grd = ctx.createRadialGradient(p.x, p.y, , p.x, p.y, p.radius  );
      const particleAlpha = isDark ? p.opacity : p.opacity  .;
      grd.addColorStop(, isDark
        ? `rgba(,,,${particleAlpha})`
        : `rgba(,,,${particleAlpha})`);
      grd.addColorStop(, 'transparent');
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius  , , Math.PI  );
      ctx.fillStyle = grd;
      ctx.fill();

      // Core dot
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, , Math.PI  );
      ctx.fillStyle = isDark
        ? `rgba(,,,${particleAlpha})`
        : `rgba(,,,${particleAlpha})`;
      ctx.fill();
    });
  }, [isDark]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('d');

    const resize = () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
      // Re-create particles on resize so they fill new dimensions
      particles.current = Array.from(
        { length: PARTICLE_COUNT },
        () => createParticle(canvas.width, canvas.height)
      );
    };

    resize();
    window.addEventListener('resize', resize);

    const loop = () => {
      draw(ctx, canvas.width, canvas.height);
      animId.current = requestAnimationFrame(loop);
    };
    animId.current = requestAnimationFrame(loop);

    const onMouse = e => { mouse.current = { x: e.clientX, y: e.clientY }; };
    const onLeave = () => { mouse.current = { x: -, y: - }; };
    window.addEventListener('mousemove', onMouse, { passive: true });
    window.addEventListener('mouseleave', onLeave);

    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', onMouse);
      window.removeEventListener('mouseleave', onLeave);
      if (animId.current) cancelAnimationFrame(animId.current);
    };
  }, [draw]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: ,
        pointerEvents: 'none',
        zIndex: ,
        opacity: isDark ?  : .,
      }}
    />
  );
}
