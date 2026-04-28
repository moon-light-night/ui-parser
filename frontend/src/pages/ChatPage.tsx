import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Loader2, MessageSquare } from 'lucide-react';
import { screenshotApi, chatApi } from '@/api';
import type { ChatSession, ChatMessage } from '@/proto/generated/chat';
import type { Screenshot } from '@/proto/generated/screenshot';
import { MessageRole, MessageStatus } from '@/proto/generated/common';
import { Button } from '@/components/ui/button';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ChatComposer } from '@/components/chat/ChatComposer';
import { ChatThread } from '@/components/chat/ChatThread';
import { SessionSidebar } from '@/components/chat/SessionSidebar';
import { useChatSend } from '@/hooks/useChatSend';
import { AppHeader } from '@/components/AppHeader';
import { LOCALE, PAGE_SIZE_SESSIONS, PAGE_SIZE_MESSAGES } from '@/lib/constants';

export default function ChatPage() {
  const { id: screenshotId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [screenshot, setScreenshot] = useState<Screenshot | null>(null);

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [creatingSession, setCreatingSession] = useState(false);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loadedSessionId, setLoadedSessionId] = useState<string | null>(null);
  const messagesLoading = !!activeSessionId && loadedSessionId !== activeSessionId;
  const visibleMessages = loadedSessionId === activeSessionId ? messages : [];

  const [inputValue, setInputValue] = useState('');

  const threadBottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { sending, streamingContent, setStreamingContent, sendError, sendMessage, resumeStream, resetSendError } = useChatSend({
    activeSessionId,
    onMessageCreated: (msg) => setMessages((prev) => [...prev, msg]),
    onAssistantDone: (msg, newTitle, countDelta = 2) => {
      setMessages((prev) => [...prev, msg]);
      setSessions((prev) =>
        prev.map((s) =>
          s.id === activeSessionId
            ? {
                ...s,
                messageCount: (s.messageCount ?? 0) + countDelta,
                ...(newTitle ? { title: newTitle } : {}),
              }
            : s
        )
      );
    },
  });

  useEffect(() => {
    if (!screenshotId) return;
    screenshotApi
      .getScreenshot({ screenshotId })
      .then(({ response: res }) => setScreenshot(res.screenshot ?? null))
      .catch(() => setScreenshot(null));
  }, [screenshotId]);

  useEffect(() => {
    if (!screenshotId) return;
    chatApi
      .listSessions({ screenshotId, pagination: { pageSize: PAGE_SIZE_SESSIONS, pageToken: '' } })
      .then(({ response: res }) => {
        const list = res.sessions ?? [];
        setSessions(list);
        setSessionsLoading(false);
        setActiveSessionId((prev) => (prev === null && list.length > 0 ? list[0].id : prev));
      })
      .catch(() => setSessionsLoading(false));
  }, [screenshotId]);

  useEffect(() => {
    if (!activeSessionId) return;
    const sessionId = activeSessionId;
    chatApi
      .listMessages({ sessionId, pagination: { pageSize: PAGE_SIZE_MESSAGES, pageToken: '' } })
      .then(({ response: res }) => {
        const all = res.messages ?? [];

        const streamingMsg = [...all].reverse().find(
          (m) => m.role === MessageRole.ASSISTANT && m.status === MessageStatus.STREAMING,
        );

        if (streamingMsg) {
          setMessages(all.filter((m) => m.id !== streamingMsg.id));
          setLoadedSessionId(sessionId);
          resumeStream(streamingMsg.id);
        } else {
          setMessages(all);
          setLoadedSessionId(sessionId);
        }
      })
      .catch(() => setLoadedSessionId(sessionId));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSessionId]);

  useEffect(() => {
    threadBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const handleNewSession = async () => {
    if (!screenshotId || creatingSession) return;
    setCreatingSession(true);
    try {
      const { response: res } = await chatApi.createSession({
        screenshotId,
        title: `Чат ${new Date().toLocaleString(LOCALE, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`,
      });
      const newSession = res.session;
      if (newSession) {
        setSessions((prev) => [newSession, ...prev]);
        setActiveSessionId(newSession.id);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to create session', err);
    } finally {
      setCreatingSession(false);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await chatApi.deleteSession({ sessionId });
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        const remaining = sessions.filter((s) => s.id !== sessionId);
        setActiveSessionId(remaining.length > 0 ? remaining[0].id : null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to delete session', err);
    }
  };

  const handleSend = () => {
    sendMessage(inputValue);
    setInputValue('');
  };

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
          onNewSession={handleNewSession}
          onSelectSession={(id) => {
            if (id !== activeSessionId) {
              setActiveSessionId(id);
              setStreamingContent(null);
              resetSendError();
            }
          }}
          onDeleteSession={handleDeleteSession}
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
              <Button onClick={handleNewSession} disabled={creatingSession}>
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
                value={inputValue}
                onChange={setInputValue}
                onSend={handleSend}
                sending={sending}
                textareaRef={textareaRef}
              />
            </>
          )}
        </main>
      </div>
    </div>
    </TooltipProvider>
  );
}
