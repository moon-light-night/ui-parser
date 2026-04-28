import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChatSend } from '../useChatSend';
import { ChatStreamEvent } from '@/lib/streamEvents';

const mockSendMessage = vi.fn();
const mockResumeStream = vi.fn();

vi.mock('@/api', () => ({
  chatApi: {
    sendMessage: (...args: unknown[]) => mockSendMessage(...args),
    resumeMessageStream: (...args: unknown[]) => mockResumeStream(...args),
  },
}));

function makeStream(events: object[]) {
  return {
    responses: (async function* () {
      for (const e of events) yield e;
    })(),
  };
}

const SESSION_ID = 'session-1';
const BASE_MSG = { id: 'msg-1', content: 'hi', role: 1, status: 1, modelName: '', createdAt: undefined };

describe('useChatSend — начальное состояние', () => {
  it('sending=false, streamingContent=null, sendError=null', () => {
    const { result } = renderHook(() =>
      useChatSend({
        activeSessionId: SESSION_ID,
        onMessageCreated: vi.fn(),
        onAssistantDone: vi.fn(),
      }),
    );
    expect(result.current.sending).toBe(false);
    expect(result.current.streamingContent).toBeNull();
    expect(result.current.sendError).toBeNull();
  });
});

describe('useChatSend — защитные условия', () => {
  it('игнорирует пустую строку', () => {
    mockSendMessage.mockReturnValue(makeStream([]));
    const { result } = renderHook(() =>
      useChatSend({
        activeSessionId: SESSION_ID,
        onMessageCreated: vi.fn(),
        onAssistantDone: vi.fn(),
      }),
    );
    act(() => result.current.sendMessage('   '));
    expect(mockSendMessage).not.toHaveBeenCalled();
  });

  it('игнорирует вызов если нет activeSessionId', () => {
    const { result } = renderHook(() =>
      useChatSend({
        activeSessionId: null,
        onMessageCreated: vi.fn(),
        onAssistantDone: vi.fn(),
      }),
    );
    act(() => result.current.sendMessage('Hello'));
    expect(mockSendMessage).not.toHaveBeenCalled();
  });
});

describe('useChatSend — стриминг сообщений', () => {
  beforeEach(() => {
    mockSendMessage.mockClear();
  });

  it('вызывает onMessageCreated при событии messageCreated', async () => {
    const onMessageCreated = vi.fn();
    mockSendMessage.mockReturnValue(
      makeStream([
        { event: { oneofKind: ChatStreamEvent.MESSAGE_CREATED, messageCreated: { message: BASE_MSG } } },
        { event: { oneofKind: ChatStreamEvent.ASSISTANT_DONE, assistantDone: { message: BASE_MSG, newSessionTitle: '' } } },
      ]),
    );

    const { result } = renderHook(() =>
      useChatSend({
        activeSessionId: SESSION_ID,
        onMessageCreated,
        onAssistantDone: vi.fn(),
      }),
    );

    await act(async () => result.current.sendMessage('Hello'));
    expect(onMessageCreated).toHaveBeenCalledWith(BASE_MSG);
  });

  it('накапливает чанки в streamingContent', async () => {
    const onAssistantDone = vi.fn();
    mockSendMessage.mockReturnValue(
      makeStream([
        { event: { oneofKind: ChatStreamEvent.ASSISTANT_CHUNK, assistantChunk: { chunk: 'Hello' } } },
        { event: { oneofKind: ChatStreamEvent.ASSISTANT_CHUNK, assistantChunk: { chunk: ' World' } } },
        { event: { oneofKind: ChatStreamEvent.ASSISTANT_DONE, assistantDone: { message: BASE_MSG, newSessionTitle: '' } } },
      ]),
    );

    const { result } = renderHook(() =>
      useChatSend({
        activeSessionId: SESSION_ID,
        onMessageCreated: vi.fn(),
        onAssistantDone,
      }),
    );

    await act(async () => result.current.sendMessage('Hello'));
    // После DONE streamingContent должен быть null
    expect(result.current.streamingContent).toBeNull();
    expect(result.current.sending).toBe(false);
    expect(onAssistantDone).toHaveBeenCalledWith(BASE_MSG, '', 2);
  });

  it('устанавливает sendError при событии error', async () => {
    mockSendMessage.mockReturnValue(
      makeStream([
        { event: { oneofKind: ChatStreamEvent.ERROR, error: { message: 'something went wrong' } } },
      ]),
    );

    const { result } = renderHook(() =>
      useChatSend({
        activeSessionId: SESSION_ID,
        onMessageCreated: vi.fn(),
        onAssistantDone: vi.fn(),
      }),
    );

    await act(async () => result.current.sendMessage('Hello'));
    expect(result.current.sendError).toBe('something went wrong');
    expect(result.current.sending).toBe(false);
  });
});
