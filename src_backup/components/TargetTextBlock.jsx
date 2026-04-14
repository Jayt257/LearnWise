/
  src/components/TargetTextBlock.jsx
  Reusable component to render the -field requirement from the data_README schema:
  . targetText (Target Language)
  . transliteration (Romanized / Phonetic)
  . baseTranslation (Native Language)
 
  If any field is missing, it gracefully omitting that part.
 /
import React from 'react';

export default function TargetTextBlock({ data, size = 'md' }) {
  if (!data) return null;

  const { targetText, transliteration, baseTranslation } = data;
  if (!targetText && !transliteration && !baseTranslation) return null;

  const sizes = {
    sm: { target: 'rem', base: '.rem' },
    md: { target: '.rem', base: '.rem' },
    lg: { target: '.rem', base: 'rem' },
  };

  const { target, base } = sizes[size] || sizes.md;

  return (
    <div className="target-text-block" style={{ display: 'flex', flexDirection: 'column', gap: '.rem' }}>
      {targetText && (
        <div style={{ fontSize: target, fontWeight: , color: 'var(--color-primary-light)' }}>
          {targetText}
        </div>
      )}
      {transliteration && (
        <div style={{ fontSize: base, color: 'var(--color-secondary-light)', fontStyle: 'italic' }}>
          {transliteration}
        </div>
      )}
      {baseTranslation && (
        <div style={{ fontSize: base, color: 'var(--color-text-muted)' }}>
          {baseTranslation}
        </div>
      )}
    </div>
  );
}
