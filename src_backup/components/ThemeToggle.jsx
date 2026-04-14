/
  src/components/ThemeToggle.jsx
  Sun/moon toggle — persists theme to localStorage.
 /
import React from 'react';
import { useTheme } from '../hooks/useTheme.js';

export default function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      className="theme-toggle"
      onClick={toggleTheme}
      title={isDark ? 'Switch to Light mode' : 'Switch to Dark mode'}
      aria-label="Toggle theme"
    >
      <span style={{ fontSize: '.rem' }}>{isDark ? '' : ''}</span>
      <span style={{ flex: , textAlign: 'left' }}>
        {isDark ? 'Dark mode' : 'Light mode'}
      </span>
      <div className="toggle-pill">
        <div className="toggle-thumb" />
      </div>
    </button>
  );
}
