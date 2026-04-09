/**
 * src/components/AssetRenderer.jsx
 * Renders multiple media items (audio, images, video) dynamically based on admin input.
 */
import React from 'react';
import AudioPlayer from './AudioPlayer.jsx';

export default function AssetRenderer({ audioAssets, imageAssets = [], videoAssets = [] }) {
  // Check if we actually have anything to render
  const hasAudio = audioAssets && Object.values(audioAssets).some(v => v !== null && typeof v === 'string' && v.length > 0);
  const hasImages = Array.isArray(imageAssets) && imageAssets.length > 0;
  const hasVideo = Array.isArray(videoAssets) && videoAssets.length > 0;

  if (!hasAudio && !hasImages && !hasVideo) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem', padding: '1rem', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-md)' }}>
      {hasAudio && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
          {audioAssets.nativeAudio && <AudioPlayer audioUrl={audioAssets.nativeAudio} label="Native Audio" />}
          {audioAssets.slowAudio && <AudioPlayer audioUrl={audioAssets.slowAudio} label="Slow Audio" />}
          {audioAssets.referenceAudio && <AudioPlayer audioUrl={audioAssets.referenceAudio} label="Reference Audio" />}
        </div>
      )}

      {hasImages && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          {imageAssets.map((img, i) => (
            <figure key={i} style={{ margin: 0 }}>
              <img src={img.url} alt={img.altText || 'Activity visual'} style={{ width: '100%', borderRadius: 'var(--radius-sm)', objectFit: 'cover' }} />
              {img.caption && <figcaption style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textAlign: 'center', marginTop: '0.25rem' }}>{img.caption}</figcaption>}
            </figure>
          ))}
        </div>
      )}

      {hasVideo && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {videoAssets.map((vid, i) => (
            <div key={i}>
               <video controls style={{ width: '100%', borderRadius: 'var(--radius-sm)' }}>
                 <source src={vid.url} />
                 Your browser does not support the video tag.
               </video>
               {vid.description && <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '0.5rem' }}>{vid.description}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
