import { Loader2 } from 'lucide-react';
import type { ChatMessage } from '@/proto/generated/chat';
import { MessageRole } from '@/proto/generated/common';
import { MessageBubble, StreamingBubble } from '@/components/chat/MessageBubble';

interface ChatThreadProps {
  messages: ChatMessage[];
  messagesLoading: boolean;
  streamingContent: string | null;
  sendError: string | null;
  bottomRef: React.Ref<HTMLDivElement>;
}

export function ChatThread({
  messages,
  messagesLoading,
  streamingContent,
  sendError,
  bottomRef,
}: ChatThreadProps) {
  const lastMessage = messages[messages.length - 1];
  const hasOrphanedUserMessage =
    !messagesLoading &&
    streamingContent === null &&
    lastMessage?.role === MessageRole.USER;

  if (messagesLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Loader2 className="w-5 h-5 text-muted-foreground animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
      {messages.length === 0 && streamingContent === null && (
        <div className="flex flex-col items-center justify-center h-full text-center py-12">
          <p className="text-muted-foreground text-sm">
            Отправьте сообщение, чтобы начать разговор.
          </p>
          <p className="text-muted-foreground/60 text-xs mt-1">
            AI будет использовать анализ скриншота как контекст.
          </p>
        </div>
      )}

      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}

      {streamingContent !== null && (
        <StreamingBubble content={streamingContent} />
      )}

      {hasOrphanedUserMessage && (
        <div className="flex justify-center">
          <p className="text-xs text-muted-foreground bg-muted/50 border border-border/50 rounded-lg px-4 py-2">
            Предыдущий ответ был прерван. Отправьте новое сообщение.
          </p>
        </div>
      )}

      {sendError && (
        <div className="flex justify-center">
          <p className="text-xs text-red-600 dark:text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2">
            {sendError}
          </p>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
