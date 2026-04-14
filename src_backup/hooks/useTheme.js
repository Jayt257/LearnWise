/**
 * src/hooks/useTheme.js
 * Dual theme hook — reads/writes data-theme on <html>.
 * Persists choice to localStorage.
 */
import { useState, useEffect } from 'react';

export function useTheme() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('lw-theme') || 'dark';
  });

  useEffect(() => {
    const html = document.documentElement;
    html.setAttribute('data-theme', theme);
    localStorage.setItem('lw-theme', theme);
  }, [theme]);

  // Apply on first mount (before React paint)
  useEffect(() => {
    const saved = localStorage.getItem('lw-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    setTheme(saved);
  }, []);

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');

  return { theme, toggleTheme, isDark: theme === 'dark' };
}
