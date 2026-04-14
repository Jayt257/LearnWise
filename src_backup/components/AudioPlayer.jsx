/
  src/components/AudioPlayer.jsx
  Dynamic audio component. If audioUrl is null/missing, it renders a subtle placeholder
  (since we shouldn't hard-fail if admin forgets audio).
 /
import React, { useRef, useState, useEffect } from 'react';
import { Volume, Play, Pause, AlertCircle } from 'lucide-react';
import { API_URL } from '../api/client';

export default function AudioPlayer({ audioUrl, label = "Listen" }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState(false);

  // Stop if audio changes
  useEffect(() => {
    setIsPlaying(false);
    setError(false);
  }, [audioUrl]);

  if (!audioUrl) {
    return (
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '.rem', padding: '.rem', borderRadius: 'var(--radius-md)', background: 'var(--color-surface-)', color: 'var(--color-text-dim)', fontSize: '.rem' }}>
        <Volume size={} style={{ opacity: . }} />
        <span>Audio not available</span>
      </div>
    );
  }

  // Construct full URL if it's a relative path from our backend static files
  let srcUrl = audioUrl;
  if (!audioUrl.startsWith('http')) {
    // e.g. "lang_audio/hi_ja/MB_hello.mp"
    srcUrl = `${API_URL}/static/${audioUrl}`;
  }

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(err => {
        console.error("Audio playback failed:", err);
        setError(true);
      });
    }
  };

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '.rem' }}>
      <button 
        type="button"
        onClick={togglePlay}
        disabled={error}
        style={{ 
          display: 'flex', alignItems: 'center', gap: '.rem', 
          padding: '.rem .rem', borderRadius: 'var(--radius-md)',
          background: isPlaying ? 'var(--color-primary-glow)' : 'var(--color-surface-)',
          border: `px solid ${isPlaying ? 'var(--color-primary)' : 'var(--color-border)'}`,
          color: isPlaying ? 'var(--color-primary-light)' : 'var(--color-text)',
          cursor: error ? 'not-allowed' : 'pointer',
          transition: 'all .s'
        }}
      >
        {error ? <AlertCircle size={} color="var(--color-danger)" /> : isPlaying ? <Pause size={} /> : <Play size={} />}
        <span style={{ fontSize: '.rem', fontWeight:  }}>{error ? 'File missing' : label}</span>
      </button>

      <audio 
        ref={audioRef} 
        src={srcUrl} 
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        onError={() => setError(true)}
        style={{ display: 'none' }}
      />
    </div>
  );
}
