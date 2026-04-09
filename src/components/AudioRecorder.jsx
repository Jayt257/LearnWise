/**
 * src/components/AudioRecorder.jsx
 * Records user speech via MediaRecorder, sends to /api/speech/stt (Whisper),
 * returns transcript string via onResult callback.
 * If path not resolved or browser doesn't support mic, shows graceful fallback.
 */
import React, { useState, useRef } from 'react';
import { Mic, MicOff, Loader } from 'lucide-react';
import client from '../api/client.js';

export default function AudioRecorder({ onResult, expectedText, disabled }) {
  const [state, setState] = useState('idle'); // idle | recording | processing | error | unsupported
  const [errorMsg, setErrorMsg] = useState('');
  const mediaRecorder = useRef(null);
  const chunks = useRef([]);

  const isSupported = typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia;

  if (!isSupported) {
    return (
      <div style={{ padding: '0.75rem', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
        🎤 Your browser doesn't support microphone access. Type your answer instead.
        <textarea className="form-input" style={{ marginTop: '0.5rem', width: '100%', minHeight: 80, resize: 'vertical' }}
          placeholder="Type what you would say..."
          onChange={e => onResult(e.target.value)} />
      </div>
    );
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorder.current = recorder;
      chunks.current = [];

      recorder.ondataavailable = e => chunks.current.push(e.data);
      recorder.onstop = async () => {
        setState('processing');
        try {
          const blob = new Blob(chunks.current, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('file', blob, 'recording.webm');
          if (expectedText) formData.append('expected_text', expectedText);

          const { data } = await client.post('/speech/transcribe', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          if (data.is_mock) {
            setState('error');
            setErrorMsg('Whisper fallback (Demo mode). Type your answer below.');
            return;
          }
          onResult(data.text || '');
          setState('idle');
        } catch (err) {
          console.error('STT error:', err);
          // If Whisper backend fails, let user type their answer
          setState('error');
          setErrorMsg('Speech recognition unavailable. Type your answer below.');
        }
        // Stop all tracks
        stream.getTracks().forEach(t => t.stop());
      };

      recorder.start();
      setState('recording');
    } catch (err) {
      setState('error');
      setErrorMsg(err.name === 'NotAllowedError' ? 'Microphone access denied. Please allow microphone in browser settings.' : `Microphone error: ${err.message}`);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current?.state === 'recording') {
      mediaRecorder.current.stop();
    }
  };

  if (state === 'error') {
    return (
      <div style={{ padding: '0.75rem', background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)' }}>
        <p style={{ fontSize: '0.85rem', color: 'var(--color-danger-light)', marginBottom: '0.5rem' }}>⚠️ {errorMsg}</p>
        <textarea className="form-input" rows={2} placeholder="Type your spoken answer..."
          style={{ width: '100%', resize: 'vertical' }}
          onChange={e => onResult(e.target.value)} />
        <button className="btn btn-ghost btn-sm" style={{ marginTop: '0.5rem' }} onClick={() => setState('idle')}>↩ Try recording again</button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
      <button
        type="button"
        disabled={disabled || state === 'processing'}
        onClick={state === 'recording' ? stopRecording : startRecording}
        style={{
          width: 64, height: 64, borderRadius: '50%', border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: state === 'recording' ? 'var(--color-danger)' : state === 'processing' ? 'var(--color-border)' : 'var(--color-primary)',
          boxShadow: state === 'recording' ? '0 0 0 8px rgba(239,68,68,0.25)' : '0 4px 16px rgba(99,102,241,0.4)',
          transition: 'all 0.2s',
          animation: state === 'recording' ? 'pulse 1.5s ease-in-out infinite' : 'none',
        }}>
        {state === 'processing' ? <Loader size={24} color="#fff" style={{ animation: 'spin 1s linear infinite' }} />
          : state === 'recording' ? <MicOff size={24} color="#fff" />
          : <Mic size={24} color="#fff" />}
      </button>

      <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>
        {state === 'idle' && 'Click the mic to start recording'}
        {state === 'recording' && '🔴 Recording... click again to stop'}
        {state === 'processing' && '⏳ Processing with Whisper...'}
      </div>
    </div>
  );
}
