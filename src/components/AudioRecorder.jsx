/**
 * src/components/AudioRecorder.jsx
 * Shared audio recording UI component used by Speaking, Pronunciation, Vocab activities.
 */
import React from 'react';
import { useAudioRecorder } from '../hooks/useAudioRecorder.js';

export default function AudioRecorder({ onRecordingComplete, label = 'Record your answer' }) {
  const { isRecording, startRecording, stopRecording, audioBlob, audioUrl, error, reset } = useAudioRecorder();

  const handleStop = () => {
    stopRecording();
  };

  const handleUse = () => {
    if (audioBlob) onRecordingComplete(audioBlob);
  };

  return (
    <div style={{ textAlign: 'center', padding: '1.5rem' }}>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>{label}</p>

      {error && (
        <div style={{ background: 'var(--color-danger-glow)', border: '1px solid var(--color-danger)', borderRadius: 'var(--radius-md)', padding: '0.75rem', marginBottom: '1rem', color: 'var(--color-danger-light)', fontSize: '0.85rem' }}>
          {error}
        </div>
      )}

      {/* Record button */}
      <button
        className={`record-btn ${isRecording ? 'recording' : ''}`}
        onClick={isRecording ? handleStop : startRecording}
        style={{ border: 'none', cursor: 'pointer' }}
      >
        {isRecording ? '⏹' : '🎙'}
      </button>

      <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--color-text-dim)' }}>
        {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
      </p>

      {/* Playback + use */}
      {audioUrl && !isRecording && (
        <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <audio controls src={audioUrl} style={{ width: '100%', maxWidth: 320, borderRadius: 'var(--radius-md)' }} />
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn btn-ghost btn-sm" onClick={reset}>🔄 Re-record</button>
            <button className="btn btn-primary btn-sm" onClick={handleUse}>✅ Use This Recording</button>
          </div>
        </div>
      )}
    </div>
  );
}
