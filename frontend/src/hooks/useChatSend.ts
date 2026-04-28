import { useState, useRef } from 'react';
import { chatApi } from '@/api';
import type { ChatMessage } from '@/proto/generated/chat';
import { ChatStreamEvent } from '@/lib/streamEvents';

interface UseChatSendOptions {
  activeSessionId: string | null;
  onMessageCreated: (msg: ChatMessage) => void;
  onAssistantDone: (msg: ChatMessage, newTitle?: string, countDelta?: number) => void;
}

export function useChatSend({ activeSessionId, onMessageCreated, onAssistantDone }: UseChatSendOptions) {
  const [sending, setSending] = useState(false);
  const [streamingContent, setStreamingContent] = useState<string | null>(null);
  const [sendError, setSendError] = useState<string | null>(null);

  const activeStreamRef = useRef<AbortController | null>(null);

  const sendMessage = (text: string) => {
    if (!text.trim() || !activeSessionId || sending) return;

    setSending(true);
    setSendError(null);
    setStreamingContent('');

    if (activeStreamRef.current) {
      activeStreamRef.current.abort();
    }
    const abortController = new AbortController();
    activeStreamRef.current = abortController;

    const stream = chatApi.sendMessage(
      { sessionId: activeSessionId, content: text.trim() },
      { abort: abortController.signal },
    );

    (async () => {
      try {
        for await (const event of stream.responses) {
          if (event.event.oneofKind === ChatStreamEvent.MESSAGE_CREATED) {
            const msg = event.event.messageCreated.message;
            if (msg) onMessageCreated(msg);
          } else if (event.event.oneofKind === ChatStreamEvent.ASSISTANT_CHUNK) {
            const chunk = event.event.assistantChunk.chunk;
            setStreamingContent((prev) => (prev ?? '') + chunk);
          } else if (event.event.oneofKind === ChatStreamEvent.ASSISTANT_DONE) {
            const { message: msg, newSessionTitle } = event.event.assistantDone;
            setStreamingContent(null);
            setSending(false);
            if (msg) onAssistantDone(msg, newSessionTitle, 2);
          } else if (event.event.oneofKind === ChatStreamEvent.ERROR) {
            throw new Error(event.event.error.message);
          }
        }
        setStreamingContent(null);
        setSending(false);
      } catch (err: unknown) {
        setStreamingContent(null);
        setSending(false);
        setSendError(err instanceof Error ? err.message : 'Failed to get response');
      }
    })();
  };

  const resumeStream = (messageId: string) => {
    if (sending) return;

    setSending(true);
    setSendError(null);
    setStreamingContent('');

    if (activeStreamRef.current) {
      activeStreamRef.current.abort();
    }
    const abortController = new AbortController();
    activeStreamRef.current = abortController;

    const stream = chatApi.resumeMessageStream(
      { messageId },
      { abort: abortController.signal },
    );

    (async () => {
      try {
        for await (const event of stream.responses) {
          if (event.event.oneofKind === ChatStreamEvent.ASSISTANT_CHUNK) {
            const chunk = event.event.assistantChunk.chunk;
            setStreamingContent((prev) => (prev ?? '') + chunk);
          } else if (event.event.oneofKind === ChatStreamEvent.ASSISTANT_DONE) {
            const { message: msg, newSessionTitle } = event.event.assistantDone;
            setStreamingContent(null);
            setSending(false);
            if (msg) onAssistantDone(msg, newSessionTitle, 0);
          } else if (event.event.oneofKind === ChatStreamEvent.ERROR) {
            throw new Error(event.event.error.message);
          }
        }
        setStreamingContent(null);
        setSending(false);
      } catch (err: unknown) {
        setStreamingContent(null);
        setSending(false);
        setSendError(err instanceof Error ? err.message : 'Failed to resume response');
      }
    })();
  };

  const resetSendError = () => setSendError(null);

  return { sending, streamingContent, setStreamingContent, sendError, sendMessage, resumeStream, resetSendError };
}
