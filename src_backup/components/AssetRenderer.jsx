/
  src/components/AssetRenderer.jsx
  Renders multiple media items (audio, images, video) dynamically based on admin input.
 /
import React from 'react';
import AudioPlayer from './AudioPlayer.jsx';

export default function AssetRenderer({ audioAssets, imageAssets = [], videoAssets = [] }) {
  // Check if we actually have anything to render
  const hasAudio = audioAssets && Object.values(audioAssets).some(v => v !== null && typeof v === 'string' && v.length > );
  const hasImages = Array.isArray(imageAssets) && imageAssets.length > ;
  const hasVideo = Array.isArray(videoAssets) && videoAssets.length > ;

  if (!hasAudio && !hasImages && !hasVideo) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'rem', marginTop: 'rem', padding: 'rem', background: 'var(--color-surface-)', borderRadius: 'var(--radius-md)' }}>
      {hasAudio && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '.rem' }}>
          {audioAssets.nativeAudio && <AudioPlayer audioUrl={audioAssets.nativeAudio} label="Native Audio" />}
          {audioAssets.slowAudio && <AudioPlayer audioUrl={audioAssets.slowAudio} label="Slow Audio" />}
          {audioAssets.referenceAudio && <AudioPlayer audioUrl={audioAssets.referenceAudio} label="Reference Audio" />}
        </div>
      )}

      {hasImages && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(px, fr))', gap: 'rem' }}>
          {imageAssets.map((img, i) => (
            <figure key={i} style={{ margin:  }}>
              <img src={img.url} alt={img.altText || 'Activity visual'} style={{ width: '%', borderRadius: 'var(--radius-sm)', objectFit: 'cover' }} />
              {img.caption && <figcaption style={{ fontSize: '.rem', color: 'var(--color-text-muted)', textAlign: 'center', marginTop: '.rem' }}>{img.caption}</figcaption>}
            </figure>
          ))}
        </div>
      )}

      {hasVideo && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'rem' }}>
          {videoAssets.map((vid, i) => (
            <div key={i}>
               <video controls style={{ width: '%', borderRadius: 'var(--radius-sm)' }}>
                 <source src={vid.url} />
                 Your browser does not support the video tag.
               </video>
               {vid.description && <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)', marginTop: '.rem' }}>{vid.description}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
