/**
 * src/components/NebulaWeb.jsx
 * Interactive canvas — floating particles connected by lines (web/constellation).
 * Cursor repels nearby particles. Nebula cloud blobs as soft background color.
 */
import React, { useEffect, useRef, useCallback } from 'react';
import { useTheme } from '../hooks/useTheme.js';

const PARTICLE_COUNT   = 90;
const CONNECT_DISTANCE = 140;
const MOUSE_RADIUS     = 130;
const MOUSE_STRENGTH   = 3.5;
const BASE_SPEED       = 0.28;

function createParticle(w, h) {
  const vx = (Math.random() - 0.5) * BASE_SPEED;
  const vy = (Math.random() - 0.5) * BASE_SPEED;
  return {
    x:  Math.random() * w,
    y:  Math.random() * h,
    vx: vx,
    vy: vy,
    baseVx: vx,
    baseVy: vy,
    radius: Math.random() * 1.6 + 0.5,
    opacity: Math.random() * 0.55 + 0.25,
  };
}

export default function NebulaWeb() {
  const canvasRef  = useRef(null);
  const mouse      = useRef({ x: -9999, y: -9999 });
  const particles  = useRef([]);
  const animId     = useRef(null);
  const { isDark } = useTheme();

  const draw = useCallback((ctx, w, h) => {
    ctx.clearRect(0, 0, w, h);

    /* ── Nebula cloud blobs ──────────────────────────────── */
    const clouds = [
      { x: w * 0.15, y: h * 0.22, r: Math.min(w, h) * 0.38, c: isDark ? 'rgba(60,60,60,0.12)' : 'rgba(215,115,76,0.15)' },
      { x: w * 0.80, y: h * 0.60, r: Math.min(w, h) * 0.32, c: isDark ? 'rgba(80,70,50,0.10)' : 'rgba(92,156,150,0.15)' },
      { x: w * 0.50, y: h * 0.80, r: Math.min(w, h) * 0.26, c: isDark ? 'rgba(50,50,50,0.09)' : 'rgba(100,120,180,0.12)' },
    ];
    clouds.forEach(cl => {
      const g = ctx.createRadialGradient(cl.x, cl.y, 0, cl.x, cl.y, cl.r);
      g.addColorStop(0, cl.c);
      g.addColorStop(1, 'transparent');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(cl.x, cl.y, cl.r, 0, Math.PI * 2);
      ctx.fill();
    });

    const pts = particles.current;
    const mx  = mouse.current.x;
    const my  = mouse.current.y;

    /* ── Update positions ────────────────────────────────── */
    pts.forEach(p => {
      const dx   = p.x - mx;
      const dy   = p.y - my;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < MOUSE_RADIUS && dist > 1) {
        const force = (MOUSE_RADIUS - dist) / MOUSE_RADIUS;
        p.vx += (dx / dist) * force * MOUSE_STRENGTH * 0.08;
        p.vy += (dy / dist) * force * MOUSE_STRENGTH * 0.08;
      }

      // Instead of absolute dampening, slowly return to original base velocity
      const angle = Math.atan2(p.baseVy, p.baseVx);
      const baseSpeed = Math.sqrt(p.baseVx * p.baseVx + p.baseVy * p.baseVy);
      
      p.vx = p.vx * 0.95 + (Math.cos(angle) * baseSpeed) * 0.05;
      p.vy = p.vy * 0.95 + (Math.sin(angle) * baseSpeed) * 0.05;

      // Clamp max speed from mouse interaction
      const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
      if (speed > 2.5) { p.vx = (p.vx / speed) * 2.5; p.vy = (p.vy / speed) * 2.5; }

      p.x += p.vx;
      p.y += p.vy;

      // Wrap at edges
      if (p.x < 0)  p.x = w;
      if (p.x > w)  p.x = 0;
      if (p.y < 0)  p.y = h;
      if (p.y > h)  p.y = 0;
    });

    /* ── Draw connection lines ───────────────────────────── */
    const lineAlphaScale = isDark ? 0.28 : 0.15;
    for (let i = 0; i < pts.length; i++) {
      for (let j = i + 1; j < pts.length; j++) {
        const dx   = pts[i].x - pts[j].x;
        const dy   = pts[i].y - pts[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONNECT_DISTANCE) {
          const alpha = (1 - dist / CONNECT_DISTANCE) * lineAlphaScale;
          ctx.beginPath();
          ctx.moveTo(pts[i].x, pts[i].y);
          ctx.lineTo(pts[j].x, pts[j].y);
          ctx.strokeStyle = isDark
            ? `rgba(200,200,200,${alpha})`
            : `rgba(20,20,20,${alpha})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }
    }

    /* ── Draw particles ──────────────────────────────────── */
    pts.forEach(p => {
      // Glow halo
      const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius * 4);
      const particleAlpha = isDark ? p.opacity : p.opacity * 0.55;
      grd.addColorStop(0, isDark
        ? `rgba(220,220,220,${particleAlpha})`
        : `rgba(30,30,30,${particleAlpha})`);
      grd.addColorStop(1, 'transparent');
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius * 4, 0, Math.PI * 2);
      ctx.fillStyle = grd;
      ctx.fill();

      // Core dot
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = isDark
        ? `rgba(255,255,255,${particleAlpha})`
        : `rgba(0,0,0,${particleAlpha})`;
      ctx.fill();
    });
  }, [isDark]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

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
    const onLeave = () => { mouse.current = { x: -9999, y: -9999 }; };
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
        inset: 0,
        pointerEvents: 'none',
        zIndex: 0,
        opacity: isDark ? 1 : 0.7,
      }}
    />
  );
}
