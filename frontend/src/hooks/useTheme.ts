import { useThemeStore, THEME } from '@/store';
export type { Theme } from '@/store';
export { THEME };

export function useTheme() {
  const theme = useThemeStore((s) => s.theme);
  const toggle = useThemeStore((s) => s.toggle);

  return { theme, toggle };
}
