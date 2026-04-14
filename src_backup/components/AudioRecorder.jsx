/
  src/components/AudioRecorder.jsx
 
  Full-featured voice recorder:
    ✓ Records via MediaRecorder → sends to /api/speech/transcribe (Whisper)
    ✓ Shows playback controls for the recorded audio
    ✓ Shows the Whisper transcript so user can confirm before submitting
    ✓ is_mock=true → typed fallback (Whisper unavailable on server)
    ✓ Mic permission denied / browser unsupported → graceful fallback
 
  API contract:
    POST /api/speech/transcribe
      field: 'audio' (Blob, audio/webm)
    Response: { text: string, confidence: float|null, language: string, is_mock: bool }
 
  Props:
    onResult(transcript: string) — called when transcript is confirmed
    expectedText?: string        — passed to Whisper for hint (optional)
    disabled?: bool
    label?: string               — e.g. "Record pronunciation"
 /
import React, { useState, useRef } from 'react';
import { Mic, MicOff, Loader, RotateCcw, CheckCircle } from 'lucide-react';
import client from '../api/client.js';

export default function AudioRecorder({ onResult, expectedText, disabled, label }) {
  // state machine: idle → recording → processing → review | mock | error | unsupported
  const [state, setState] = useState('idle');
  const [transcript, setTranscript] = useState('');
  const [confidence, setConfidence] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
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

      recorder.ondataavailable = e => {
        chunks.current.push(e.data); // Follow friend's exact logic
      };

      recorder.onstop = async () => {
        setState('processing');

        // Create Blob exactly like the friend's README (no mimetype fallback logic that defaults to weird opus containers)
        const blob = new Blob(chunks.current, { type: 'audio/webm' });
        audioBlob.current = blob;
        audioUrl.current = URL.createObjectURL(blob);

        // Stop streams AFTER creating the blob to prevent abrupt audio truncations
        stream.getTracks().forEach(t => t.stop());

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

  const confirmTranscript = () => {
    onResult(transcript);
  };

  const reRecord = () => {
    if (audioEl.current) { audioEl.current.pause(); audioEl.current = null; }
    if (audioUrl.current) { URL.revokeObjectURL(audioUrl.current); audioUrl.current = null; }
    setTranscript('');
    setConfidence(null);
    setState('idle');
  };

  // ─── Review state: playback + transcript ───────────────────────────────────
  if (state === 'review') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '.rem' }}>
        {/ Native Audio Player /}
        <div style={{
          padding: '.rem rem',
          background: 'rgba(,,,.)',
          border: 'px solid rgba(,,,.)',
          borderRadius: 'var(--radius-md)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '.rem' }}>
            <span style={{ fontSize: '.rem', color: 'var(--color-success)', fontWeight:  }}> Your Recording</span>
            {confidence !== null && <span style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}>Confidence: {Math.round(confidence  )}%</span>}
          </div>
          <audio controls src={audioUrl.current} style={{ width: '%', height: 'px', outline: 'none' }} />
        </div>

        {/ Whisper transcript block /}
        <div style={{
          padding: '.rem rem',
          background: 'rgba(,,,.)',
          border: 'px solid rgba(,,,.)',
          borderRadius: 'var(--radius-md)',
        }}>
          <div style={{ fontSize: '.rem', fontWeight: , textTransform: 'uppercase', color: 'var(--color-primary-light)', marginBottom: '.rem', letterSpacing: '.em' }}>
             Whisper Transcript
          </div>
          {transcript ? (
            <p style={{ fontSize: '.rem', color: 'var(--color-text)', margin: , lineHeight: . }}>
              "{transcript}"
            </p>
          ) : (
            <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)', fontStyle: 'italic', margin:  }}>
              (No speech detected — try speaking louder or closer to the mic)
            </p>
          )}
        </div>

        {/ Edit transcript manually if needed /}
        <div>
          <label style={{ fontSize: '.rem', color: 'var(--color-text-muted)', display: 'block', marginBottom: '.rem' }}>
            Edit transcript if incorrect:
          </label>
          <input
            className="form-input"
            value={transcript}
            onChange={e => setTranscript(e.target.value)}
            style={{ width: '%', fontSize: '.rem' }}
            placeholder="Edit if Whisper made a mistake..."
          />
        </div>

        {/ Actions /}
        <div style={{ display: 'flex', gap: '.rem' }}>
          <button type="button" className="btn btn-primary" style={{ flex:  }} onClick={confirmTranscript} disabled={!transcript.trim()}>
            <CheckCircle size={} style={{ marginRight:  }} /> Use This Answer
          </button>
          <button type="button" className="btn btn-ghost" onClick={reRecord}>
            <RotateCcw size={} style={{ marginRight:  }} /> Re-record
          </button>
        </div>
      </div>
    );
  }

  // ─── Mock mode: Whisper unavailable ────────────────────────────────────────
  if (state === 'mock') {
    return (
      <div style={{ padding: '.rem rem', background: 'rgba(,,,.)', border: 'px solid rgba(,,,.)', borderRadius: 'var(--radius-md)' }}>
        <p style={{ fontSize: '.rem', color: 'var(--color-accent-light)', marginBottom: '.rem' }}>
           Speech recognition is in demo mode (Whisper model unavailable). Type your answer:
        </p>
        <input className="form-input" value={typedAnswer}
          onChange={e => { setTypedAnswer(e.target.value); onResult(e.target.value); }}
          placeholder="Type what you would say..."
          style={{ width: '%', marginBottom: '.rem' }} />
        <button className="btn btn-ghost btn-sm" onClick={reRecord}> Try recording again</button>
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
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '.rem' }}>
      {label && (
        <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)', margin:  }}>{label}</p>
      )}
      <button
        type="button"
        disabled={disabled || state === 'processing'}
        onClick={state === 'recording' ? stopRecording : startRecording}
        style={{
          width: , height: , borderRadius: '%', border: 'none', cursor: state === 'processing' ? 'wait' : 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: state === 'recording'
            ? 'var(--color-danger)'
            : state === 'processing'
            ? ''
            : 'var(--color-primary)',
          boxShadow: state === 'recording'
            ? '   px rgba(,,,.),    px rgba(,,,.)'
            : ' px px rgba(,,,.)',
          transition: 'all .s',
        }}>
        {state === 'processing'
          ? <Loader size={} color="caaf" style={{ animation: 'spin s linear infinite' }} />
          : state === 'recording'
          ? <MicOff size={} color="fff" />
          : <Mic size={} color="fff" />}
      </button>

      <div style={{ fontSize: '.rem', color: 'var(--color-text-muted)', textAlign: 'center', minHeight:  }}>
        {state === 'idle'       && 'Tap the mic to start recording'}
        {state === 'recording'  && <span style={{ color: 'ef', fontWeight:  }}>● Recording — tap to stop</span>}
        {state === 'processing' && ' Sending to Whisper...'}
      </div>
    </div>
  );
}

// ─── Helper: Typed fallback ─────────────────────────────────────────────────
function FallbackTyped({ onChange, reason, onRetry }) {
  const [v, setV] = useState('');
  const isUnsupported = reason === 'browser-unsupported';
  return (
    <div style={{ padding: '.rem rem', background: 'rgba(,,,.)', border: 'px solid rgba(,,,.)', borderRadius: 'var(--radius-md)' }}>
      {!isUnsupported && (
        <p style={{ fontSize: '.rem', color: 'var(--color-danger-light)', marginBottom: '.rem' }}> {reason}</p>
      )}
      {isUnsupported && (
        <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)', marginBottom: '.rem' }}>
           Your browser doesn't support microphone access. Type your answer:
        </p>
      )}
      <input
        className="form-input"
        value={v}
        onChange={e => { setV(e.target.value); onChange(e.target.value); }}
        placeholder="Type your spoken answer..."
        style={{ width: '%', marginBottom: onRetry ? '.rem' :  }}
      />
      {onRetry && (
        <button className="btn btn-ghost btn-sm" style={{ marginTop: '.rem' }} onClick={onRetry}>
          <RotateCcw size={} style={{ marginRight:  }} /> Try recording again
        </button>
      )}
    </div>
  );
}
