/**
 * src/components/AudioRecorder.jsx
 *
 * Full-featured voice recorder:
 *   ✓ Records via MediaRecorder → sends to /api/speech/transcribe (Whisper)
 *   ✓ Shows playback controls for the recorded audio
 *   ✓ Shows the Whisper transcript so user can confirm before submitting
 *   ✓ is_mock=true → typed fallback (Whisper unavailable on server)
 *   ✓ Mic permission denied / browser unsupported → graceful fallback
 *
 * API contract:
 *   POST /api/speech/transcribe
 *     field: 'audio' (Blob, audio/webm)
 *   Response: { text: string, confidence: float|null, language: string, is_mock: bool }
 *
 * Props:
 *   onResult(transcript: string) — called when transcript is confirmed
 *   expectedText?: string        — passed to Whisper for hint (optional)
 *   disabled?: bool
 *   label?: string               — e.g. "Record pronunciation"
 */
import React, { useState, useRef } from 'react';
import { Mic, MicOff, Loader, Play, Pause, RotateCcw, CheckCircle } from 'lucide-react';
import client from '../api/client.js';

export default function AudioRecorder({ onResult, expectedText, disabled, label }) {
  // state machine: idle → recording → processing → review | mock | error | unsupported
  const [state, setState] = useState('idle');
  const [transcript, setTranscript] = useState('');
  const [confidence, setConfidence] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [typedAnswer, setTypedAnswer] = useState('');

  const mediaRecorder = useRef(null);
  const chunks = useRef([]);
  const audioBlob = useRef(null);
  const audioUrl = useRef(null);
  const audioEl = useRef(null);

  const isSupported = typeof navigator !== 'undefined' && !!navigator?.mediaDevices?.getUserMedia;

  // Clean up audio URL on unmount
  React.useEffect(() => {
    return () => {
      if (audioUrl.current) URL.revokeObjectURL(audioUrl.current);
    };
  }, []);

  if (!isSupported) {
    return <FallbackTyped onChange={onResult} reason="browser-unsupported" />;
  }

  const startRecording = async () => {
    // Reset state
    setTranscript('');
    setConfidence(null);
    if (audioUrl.current) { URL.revokeObjectURL(audioUrl.current); audioUrl.current = null; }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorder.current = recorder;
      chunks.current = [];

      recorder.ondataavailable = e => { if (e.data.size > 0) chunks.current.push(e.data); };

      recorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        setState('processing');

        const blob = new Blob(chunks.current, { type: recorder.mimeType || 'audio/webm' });
        audioBlob.current = blob;
        audioUrl.current = URL.createObjectURL(blob);

        try {
          const formData = new FormData();
          // Use generic audio.webm but the backend will convert to wav regardless
          formData.append('audio', blob, 'recording.webm');
          if (expectedText) formData.append('expected_text', expectedText);

          const { data } = await client.post('/speech/transcribe', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });

          // Backend returns { text, confidence, language, is_mock }
          if (data.is_mock) {
            setState('mock');
            return;
          }

          const txt = data.text ?? '';
          setTranscript(txt);
          setConfidence(data.confidence);
          setState('review'); // show playback + transcript, user confirms
        } catch (err) {
          console.error('STT error:', err);
          setState('error');
          setErrorMsg('Speech recognition failed. Please type your answer below.');
        }
      };

      recorder.start();
      setState('recording');
    } catch (err) {
      setState('error');
      setErrorMsg(
        err.name === 'NotAllowedError'
          ? 'Microphone access denied. Allow microphone access in browser settings.'
          : `Microphone error: ${err.message}`
      );
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current?.state === 'recording') {
      mediaRecorder.current.stop();
    }
  };

  const togglePlayback = () => {
    if (!audioUrl.current) return;
    if (!audioEl.current) {
      audioEl.current = new Audio(audioUrl.current);
      audioEl.current.onended = () => setIsPlaying(false);
    }
    if (isPlaying) {
      audioEl.current.pause();
      setIsPlaying(false);
    } else {
      audioEl.current.currentTime = 0;
      audioEl.current.play();
      setIsPlaying(true);
    }
  };

  const confirmTranscript = () => {
    onResult(transcript);
  };

  const reRecord = () => {
    if (audioEl.current) { audioEl.current.pause(); audioEl.current = null; }
    if (audioUrl.current) { URL.revokeObjectURL(audioUrl.current); audioUrl.current = null; }
    setTranscript('');
    setConfidence(null);
    setIsPlaying(false);
    setState('idle');
  };

  // ─── Review state: playback + transcript ───────────────────────────────────
  if (state === 'review') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {/* Playback bar */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.75rem',
          padding: '0.75rem 1rem',
          background: 'rgba(16,185,129,0.08)',
          border: '1px solid rgba(16,185,129,0.25)',
          borderRadius: 'var(--radius-md)',
        }}>
          <button type="button" onClick={togglePlayback}
            style={{ width: 36, height: 36, borderRadius: '50%', border: 'none', cursor: 'pointer',
              background: 'var(--color-success)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {isPlaying ? <Pause size={16} color="#fff" /> : <Play size={16} color="#fff" />}
          </button>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>
              Your Recording {confidence !== null && `· Confidence: ${Math.round(confidence * 100)}%`}
            </div>
            {/* Audio waveform bar (visual only) */}
            <div style={{ height: 4, background: 'var(--color-border)', borderRadius: 2, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: isPlaying ? '100%' : '0%', background: 'var(--color-success)', transition: 'width 0.1s linear' }} />
            </div>
          </div>
          <button type="button" onClick={reRecord} title="Re-record"
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}>
            <RotateCcw size={16} />
          </button>
        </div>

        {/* Whisper transcript block */}
        <div style={{
          padding: '0.75rem 1rem',
          background: 'rgba(99,102,241,0.06)',
          border: '1px solid rgba(99,102,241,0.22)',
          borderRadius: 'var(--radius-md)',
        }}>
          <div style={{ fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-primary-light)', marginBottom: '0.375rem', letterSpacing: '0.05em' }}>
            🤖 Whisper Transcript
          </div>
          {transcript ? (
            <p style={{ fontSize: '0.95rem', color: 'var(--color-text)', margin: 0, lineHeight: 1.6 }}>
              "{transcript}"
            </p>
          ) : (
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', fontStyle: 'italic', margin: 0 }}>
              (No speech detected — try speaking louder or closer to the mic)
            </p>
          )}
        </div>

        {/* Edit transcript manually if needed */}
        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'block', marginBottom: '0.25rem' }}>
            Edit transcript if incorrect:
          </label>
          <input
            className="form-input"
            value={transcript}
            onChange={e => setTranscript(e.target.value)}
            style={{ width: '100%', fontSize: '0.9rem' }}
            placeholder="Edit if Whisper made a mistake..."
          />
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button type="button" className="btn btn-primary" style={{ flex: 1 }} onClick={confirmTranscript} disabled={!transcript.trim()}>
            <CheckCircle size={16} style={{ marginRight: 6 }} /> Use This Answer
          </button>
          <button type="button" className="btn btn-ghost" onClick={reRecord}>
            <RotateCcw size={14} style={{ marginRight: 4 }} /> Re-record
          </button>
        </div>
      </div>
    );
  }

  // ─── Mock mode: Whisper unavailable ────────────────────────────────────────
  if (state === 'mock') {
    return (
      <div style={{ padding: '0.75rem 1rem', background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.3)', borderRadius: 'var(--radius-md)' }}>
        <p style={{ fontSize: '0.85rem', color: 'var(--color-accent-light)', marginBottom: '0.5rem' }}>
          ⚠️ Speech recognition is in demo mode (Whisper model unavailable). Type your answer:
        </p>
        <input className="form-input" value={typedAnswer}
          onChange={e => { setTypedAnswer(e.target.value); onResult(e.target.value); }}
          placeholder="Type what you would say..."
          style={{ width: '100%', marginBottom: '0.5rem' }} />
        <button className="btn btn-ghost btn-sm" onClick={reRecord}>↩ Try recording again</button>
      </div>
    );
  }

  // ─── Error state ────────────────────────────────────────────────────────────
  if (state === 'error') {
    return (
      <FallbackTyped reason={errorMsg} onChange={v => { onResult(v); }} onRetry={reRecord} />
    );
  }

  // ─── Idle / Recording / Processing ─────────────────────────────────────────
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
      {label && (
        <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', margin: 0 }}>{label}</p>
      )}
      <button
        type="button"
        disabled={disabled || state === 'processing'}
        onClick={state === 'recording' ? stopRecording : startRecording}
        style={{
          width: 64, height: 64, borderRadius: '50%', border: 'none', cursor: state === 'processing' ? 'wait' : 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: state === 'recording'
            ? 'var(--color-danger)'
            : state === 'processing'
            ? '#374151'
            : 'var(--color-primary)',
          boxShadow: state === 'recording'
            ? '0 0 0 10px rgba(239,68,68,0.2), 0 0 0 20px rgba(239,68,68,0.08)'
            : '0 4px 20px rgba(99,102,241,0.45)',
          transition: 'all 0.2s',
        }}>
        {state === 'processing'
          ? <Loader size={24} color="#9ca3af" style={{ animation: 'spin 1s linear infinite' }} />
          : state === 'recording'
          ? <MicOff size={24} color="#fff" />
          : <Mic size={24} color="#fff" />}
      </button>

      <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', textAlign: 'center', minHeight: 20 }}>
        {state === 'idle'       && 'Tap the mic to start recording'}
        {state === 'recording'  && <span style={{ color: '#ef4444', fontWeight: 600 }}>● Recording — tap to stop</span>}
        {state === 'processing' && '⏳ Sending to Whisper...'}
      </div>
    </div>
  );
}

// ─── Helper: Typed fallback ─────────────────────────────────────────────────
function FallbackTyped({ onChange, reason, onRetry }) {
  const [v, setV] = useState('');
  const isUnsupported = reason === 'browser-unsupported';
  return (
    <div style={{ padding: '0.75rem 1rem', background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)' }}>
      {!isUnsupported && (
        <p style={{ fontSize: '0.85rem', color: 'var(--color-danger-light)', marginBottom: '0.5rem' }}>⚠️ {reason}</p>
      )}
      {isUnsupported && (
        <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
          🎤 Your browser doesn't support microphone access. Type your answer:
        </p>
      )}
      <input
        className="form-input"
        value={v}
        onChange={e => { setV(e.target.value); onChange(e.target.value); }}
        placeholder="Type your spoken answer..."
        style={{ width: '100%', marginBottom: onRetry ? '0.5rem' : 0 }}
      />
      {onRetry && (
        <button className="btn btn-ghost btn-sm" style={{ marginTop: '0.5rem' }} onClick={onRetry}>
          <RotateCcw size={12} style={{ marginRight: 4 }} /> Try recording again
        </button>
      )}
    </div>
  );
}
