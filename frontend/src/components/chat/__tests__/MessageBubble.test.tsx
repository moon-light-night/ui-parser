import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MessageBubble, StreamingBubble } from '../MessageBubble';
import { MessageRole } from '@/proto/generated/common';

function makeMsg(overrides: object) {
  return {
    id: 'm1',
    sessionId: 's1',
    content: '',
    role: MessageRole.USER,
    status: 1,
    modelName: '',
    createdAt: undefined,
    ...overrides,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } as any;
}

describe('MessageBubble', () => {
  it('рендерит текст пользователя', () => {
    render(<MessageBubble message={makeMsg({ role: MessageRole.USER, content: 'Привет!' })} />);
    expect(screen.getByText('Привет!')).toBeInTheDocument();
  });

  it('сообщение пользователя выравнено вправо', () => {
    const { container } = render(
      <MessageBubble message={makeMsg({ role: MessageRole.USER, content: 'Hi' })} />,
    );
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('justify-end');
  });

  it('сообщение ассистента выравнено влево', () => {
    const { container } = render(
      <MessageBubble message={makeMsg({ role: MessageRole.ASSISTANT, content: 'Hi back' })} />,
    );
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('justify-start');
  });

  it('показывает modelName для ассистента', () => {
    render(
      <MessageBubble
        message={makeMsg({ role: MessageRole.ASSISTANT, content: 'Hi', modelName: 'llava:7b' })}
      />,
    );
    expect(screen.getByText('llava:7b')).toBeInTheDocument();
  });

  it('не показывает modelName для пользователя даже если задан', () => {
    render(
      <MessageBubble
        message={makeMsg({ role: MessageRole.USER, content: 'Hi', modelName: 'llava:7b' })}
      />,
    );
    expect(screen.queryByText('llava:7b')).not.toBeInTheDocument();
  });
});

describe('StreamingBubble', () => {
  it('рендерит контент если он не пуст', () => {
    render(<StreamingBubble content="Думаю..." />);
    expect(screen.getByText('Думаю...')).toBeInTheDocument();
  });

  it('показывает точки загрузки при пустом контенте', () => {
    const { container } = render(<StreamingBubble content="" />);
    const dots = container.querySelectorAll('span.animate-bounce');
    expect(dots.length).toBe(3);
  });
});
