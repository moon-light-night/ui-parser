import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTheme, THEME } from '../useTheme';

function stubMatchMedia(prefersDark: boolean) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: prefersDark && query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove(THEME.DARK, THEME.LIGHT);
    stubMatchMedia(false);
  });

  it('по умолчанию использует светлую тему если нет prefers-color-scheme dark', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe(THEME.LIGHT);
  });

  it('читает тему из localStorage', () => {
    localStorage.setItem('ui-parser-theme', THEME.DARK);
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe(THEME.DARK);
  });

  it('toggle переключает тему', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe(THEME.LIGHT);
    act(() => result.current.toggle());
    expect(result.current.theme).toBe(THEME.DARK);
    act(() => result.current.toggle());
    expect(result.current.theme).toBe(THEME.LIGHT);
  });

  it('применяет dark класс на documentElement', () => {
    const { result } = renderHook(() => useTheme());
    act(() => result.current.toggle());
    expect(document.documentElement.classList.contains(THEME.DARK)).toBe(true);
  });

  it('сохраняет тему в localStorage при toggle', () => {
    const { result } = renderHook(() => useTheme());
    act(() => result.current.toggle());
    expect(localStorage.getItem('ui-parser-theme')).toBe(THEME.DARK);
  });

  it('использует тёмную тему если prefers-color-scheme dark и нет сохранённой', () => {
    stubMatchMedia(true);

    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe(THEME.DARK);
  });
});
