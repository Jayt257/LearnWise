/**
 * src/components/TargetTextBlock.jsx
 * Reusable component to render the 3-field requirement from the data_README schema:
 * 1. targetText (Target Language)
 * 2. transliteration (Romanized / Phonetic)
 * 3. baseTranslation (Native Language)
 *
 * If any field is missing, it gracefully omitting that part.
 */
import React from 'react';

export default function TargetTextBlock({ data, size = 'md' }) {
  if (!data) return null;

  const { targetText, transliteration, baseTranslation } = data;
  if (!targetText && !transliteration && !baseTranslation) return null;

  const sizes = {
    sm: { target: '1rem', base: '0.8rem' },
    md: { target: '1.25rem', base: '0.875rem' },
    lg: { target: '1.75rem', base: '1rem' },
  };

  const { target, base } = sizes[size] || sizes.md;

  return (
    <div className="target-text-block" style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
      {targetText && (
        <div style={{ fontSize: target, fontWeight: 700, color: 'var(--color-primary-light)' }}>
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
