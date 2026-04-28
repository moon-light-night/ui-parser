import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatComposer } from '../ChatComposer';

vi.mock('@/components/ui/tooltip', () => ({
  Tooltip: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  TooltipTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  TooltipContent: () => null,
}));

function setup(overrides: Partial<React.ComponentProps<typeof ChatComposer>> = {}) {
  const props = {
    value: '',
    onChange: vi.fn(),
    onSend: vi.fn(),
    sending: false,
    textareaRef: { current: null },
    ...overrides,
  };
  render(<ChatComposer {...props} />);
  return props;
}

describe('ChatComposer', () => {
  it('рендерит textarea и кнопку отправки', () => {
    setup();
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('кнопка disabled если value пустой', () => {
    setup({ value: '' });
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('кнопка disabled если sending=true', () => {
    setup({ value: 'hello', sending: true });
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('кнопка активна если value не пустой и sending=false', () => {
    setup({ value: 'hello', sending: false });
    expect(screen.getByRole('button')).not.toBeDisabled();
  });

  it('Enter вызывает onSend', async () => {
    const onSend = vi.fn();
    setup({ value: 'Hello', onSend });
    await userEvent.type(screen.getByRole('textbox'), '{Enter}');
    expect(onSend).toHaveBeenCalledOnce();
  });

  it('Shift+Enter не вызывает onSend', async () => {
    const onSend = vi.fn();
    setup({ value: 'Hello', onSend });
    await userEvent.type(screen.getByRole('textbox'), '{Shift>}{Enter}{/Shift}');
    expect(onSend).not.toHaveBeenCalled();
  });

  it('клик по кнопке вызывает onSend', async () => {
    const onSend = vi.fn();
    setup({ value: 'Hello', onSend });
    await userEvent.click(screen.getByRole('button'));
    expect(onSend).toHaveBeenCalledOnce();
  });

  it('textarea задизейблена во время sending', () => {
    setup({ sending: true });
    expect(screen.getByRole('textbox')).toBeDisabled();
  });
});
