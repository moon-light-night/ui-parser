import { useEffect, useState } from 'react';

export const THEME = { LIGHT: 'light', DARK: 'dark' } as const;
type Theme = typeof THEME[keyof typeof THEME];

const STORAGE_KEY = 'ui-parser-theme';

function getInitialTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
  if (stored === THEME.DARK || stored === THEME.LIGHT) return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? THEME.DARK : THEME.LIGHT;
}

function applyTheme(theme: Theme) {
  document.documentElement.classList.toggle(THEME.DARK, theme === THEME.DARK);
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    applyTheme(theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const toggle = () => setTheme((t) => (t === THEME.DARK ? THEME.LIGHT : THEME.DARK));

  return { theme, toggle };
}
