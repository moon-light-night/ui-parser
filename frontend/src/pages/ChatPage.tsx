import { useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Loader2, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ChatComposer } from '@/components/chat/ChatComposer';
import { ChatThread } from '@/components/chat/ChatThread';
import { SessionSidebar } from '@/components/chat/SessionSidebar';
import { useChatSend } from '@/hooks/useChatSend';
import { AppHeader } from '@/components/AppHeader';
import { useChatStore } from '@/store';

export default function ChatPage() {
  const { id: screenshotId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    screenshot,
    sessions,
    sessionsLoading,
    activeSessionId,
    creatingSession,
    messages,
    loadedSessionId,
    loadForScreenshot,
    loadMessages,
    setActiveSessionId,
    addMessage,
    handleAssistantDone,
    createSession,
    deleteSession,
  } = useChatStore();

  const messagesLoading = !!activeSessionId && loadedSessionId !== activeSessionId;
  const visibleMessages = loadedSessionId === activeSessionId ? messages : [];

  const threadBottomRef = useRef<HTMLDivElement>(null);
  const prevActiveSessionRef = useRef<string | null>(null);

  const { sending, streamingContent, setStreamingContent, sendError, sendMessage, resumeStream, resetSendError } = useChatSend({
    activeSessionId,
    onMessageCreated: (msg) => addMessage(msg),
    onAssistantDone: (msg, newTitle, countDelta = 2) => handleAssistantDone(msg, newTitle, countDelta),
  });

  useEffect(() => {
    if (!screenshotId) return;
    loadForScreenshot(screenshotId, (messageId) => resumeStream(messageId));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screenshotId]);

  useEffect(() => {
    if (!activeSessionId || activeSessionId === prevActiveSessionRef.current) return;
    if (loadedSessionId !== activeSessionId) {
      loadMessages(activeSessionId, (messageId) => resumeStream(messageId));
    }
    prevActiveSessionRef.current = activeSessionId;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSessionId]);

  useEffect(() => {
    threadBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <TooltipProvider>
    <div className="h-screen flex flex-col bg-muted/30">
      <AppHeader
        right={
          <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
            Чат
          </span>
        }
      />

      <div className="bg-card border-b border-border px-4 h-9 flex items-center gap-1.5 text-sm text-muted-foreground shrink-0">
        <Button variant="ghost" size="sm" className="h-6 px-2 gap-1.5 text-xs" onClick={() => navigate(`/screenshots/${screenshotId}`)}>
          <ArrowLeft className="w-3 h-3" />
          Анализ
        </Button>
        <span>/</span>
        <span className="truncate max-w-[300px]">
          {screenshot
            ? screenshot.title || screenshot.originalFilename
            : <Loader2 className="w-3 h-3 animate-spin inline-block" />
          }
        </span>
      </div>

      <div className="flex flex-1 min-h-0">
        <SessionSidebar
          sessions={sessions}
          sessionsLoading={sessionsLoading}
          activeSessionId={activeSessionId}
          creatingSession={creatingSession}
          onNewSession={() => createSession()}
          onSelectSession={(id) => {
            if (id !== activeSessionId) {
              setActiveSessionId(id);
              setStreamingContent(null);
              resetSendError();
            }
          }}
          onDeleteSession={(id) => deleteSession(id)}
        />

        <main className="flex-1 flex flex-col min-h-0">
          {sessionsLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <Loader2 className="w-5 h-5 text-muted-foreground animate-spin" />
            </div>
          ) : !activeSessionId ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center px-8">
              <div className="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center mb-4">
                <MessageSquare className="w-7 h-7 text-blue-400" />
              </div>
              <h2 className="text-base font-semibold text-foreground mb-1">Начать общение</h2>
              <p className="text-sm text-muted-foreground max-w-xs mb-5">
                Создайте новую сессию, чтобы задавать вопросы о скриншоте и его анализе.
              </p>
              <Button onClick={() => createSession()} disabled={creatingSession}>
                {creatingSession ? (
                  <><Loader2 className="w-4 h-4 animate-spin" />Создание…</>
                ) : (
                  <><Plus className="w-4 h-4" />Новый чат</>
                )}
              </Button>
            </div>
          ) : (
            <>
              <ChatThread
                messages={visibleMessages}
                messagesLoading={messagesLoading}
                streamingContent={streamingContent}
                sendError={sendError}
                bottomRef={threadBottomRef}
              />

              <ChatComposer
                onSend={sendMessage}
                sending={sending}
                sendError={sendError}
              />
            </>
          )}
        </main>
      </div>
    </div>
    </TooltipProvider>
  );
}
