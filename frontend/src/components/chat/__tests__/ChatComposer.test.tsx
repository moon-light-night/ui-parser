import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatComposer } from '../ChatComposer';

vi.mock('@/components/ui/tooltip', () => ({
  Tooltip: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  TooltipTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  TooltipContent: () => null,
}));

function setup(overrides: Partial<React.ComponentProps<typeof ChatComposer>> = {}) {
  const props = {
    onSend: vi.fn(),
    sending: false,
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

  it('кнопка disabled если textarea пустая', () => {
    setup();
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('кнопка disabled если sending=true', async () => {
    setup({ sending: true });
    await userEvent.type(screen.getByRole('textbox'), 'hello');
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('кнопка активна после ввода текста', async () => {
    setup();
    await userEvent.type(screen.getByRole('textbox'), 'hello');
    expect(screen.getByRole('button')).not.toBeDisabled();
  });

  it('Enter вызывает onSend с текстом и очищает поле', async () => {
    const onSend = vi.fn();
    setup({ onSend });
    const textarea = screen.getByRole('textbox');
    await userEvent.type(textarea, 'Hello');
    await userEvent.type(textarea, '{Enter}');
    expect(onSend).toHaveBeenCalledOnce();
    expect(onSend).toHaveBeenCalledWith('Hello');
    await waitFor(() => expect(textarea).toHaveValue(''));
  });

  it('Shift+Enter не вызывает onSend', async () => {
    const onSend = vi.fn();
    setup({ onSend });
    await userEvent.type(screen.getByRole('textbox'), 'Hello');
    await userEvent.type(screen.getByRole('textbox'), '{Shift>}{Enter}{/Shift}');
    expect(onSend).not.toHaveBeenCalled();
  });

  it('клик по кнопке вызывает onSend с текстом', async () => {
    const onSend = vi.fn();
    setup({ onSend });
    await userEvent.type(screen.getByRole('textbox'), 'Hello');
    await userEvent.click(screen.getByRole('button'));
    expect(onSend).toHaveBeenCalledWith('Hello');
  });

  it('textarea задизейблена во время sending', () => {
    setup({ sending: true });
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('не вызывает onSend для сообщения только из пробелов', async () => {
    const onSend = vi.fn();
    setup({ onSend });
    await userEvent.type(screen.getByRole('textbox'), '   ');
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('показывает счётчик символов вблизи лимита', async () => {
    setup();
    const longText = 'a'.repeat(6000);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: longText } });
    await waitFor(() =>
      expect(screen.getByText(new RegExp(`${longText.length}`))).toBeInTheDocument(),
    );
  });

  it('показывает sendError из пропсов', () => {
    setup({ sendError: 'Сеть недоступна' });
    expect(screen.getByText('Сеть недоступна')).toBeInTheDocument();
  });
});
