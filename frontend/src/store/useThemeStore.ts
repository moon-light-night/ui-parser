import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const THEME = { LIGHT: 'light', DARK: 'dark' } as const;
export type Theme = (typeof THEME)[keyof typeof THEME];

function getSystemTheme(): Theme {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return THEME.LIGHT;
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? THEME.DARK
    : THEME.LIGHT;
}

function applyTheme(theme: Theme) {
  document.documentElement.classList.toggle(THEME.DARK, theme === THEME.DARK);
}

interface ThemeState {
  theme: Theme;
  toggle: () => void;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: getSystemTheme(),
      setTheme: (theme) => {
        applyTheme(theme);
        set({ theme });
      },
      toggle: () => {
        const next = get().theme === THEME.DARK ? THEME.LIGHT : THEME.DARK;
        applyTheme(next);
        set({ theme: next });
      },
    }),
    {
      name: 'ui-parser-theme',
      onRehydrateStorage: () => (state) => {
        if (state) applyTheme(state.theme);
      },
    },
  ),
);
