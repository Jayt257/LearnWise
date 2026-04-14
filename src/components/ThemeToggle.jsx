import React from 'react';
import { useTheme } from '../hooks/useTheme.js';

export default function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
      <span style={{ flex: 1, textAlign: 'left' }}>
        {isDark ? '🌙 Dark Mode' : '☀️ Light Mode'}
      </span>
      <div className="toggle-pill">
        <div className="toggle-thumb" />
      </div>
    </button>
  );
}
