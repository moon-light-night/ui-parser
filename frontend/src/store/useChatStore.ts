import { create } from 'zustand';
import { chatApi, screenshotApi } from '@/api';
import type { ChatSession, ChatMessage } from '@/proto/generated/chat';
import type { Screenshot } from '@/proto/generated/screenshot';
import { MessageRole, MessageStatus } from '@/proto/generated/common';
import { LOCALE, PAGE_SIZE_SESSIONS, PAGE_SIZE_MESSAGES } from '@/lib/constants';

interface ChatState {
  screenshotId: string | null;
  screenshot: Screenshot | null;

  sessions: ChatSession[];
  sessionsLoading: boolean;
  activeSessionId: string | null;
  creatingSession: boolean;

  messages: ChatMessage[];
  loadedSessionId: string | null;

  loadForScreenshot: (
    screenshotId: string,
    onResumeStream?: (messageId: string) => void,
  ) => void;

  loadMessages: (
    sessionId: string,
    onResumeStream?: (messageId: string) => void,
  ) => void;

  setActiveSessionId: (id: string | null) => void;

  addMessage: (msg: ChatMessage) => void;
  handleAssistantDone: (msg: ChatMessage, newTitle?: string, countDelta?: number) => void;

  createSession: () => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;

  reset: () => void;
}

const initialState = {
  screenshotId: null,
  screenshot: null,
  sessions: [],
  sessionsLoading: true,
  activeSessionId: null,
  creatingSession: false,
  messages: [],
  loadedSessionId: null,
};

export const useChatStore = create<ChatState>()((set, get) => ({
  ...initialState,

  loadForScreenshot: (screenshotId, onResumeStream) => {
    if (get().screenshotId === screenshotId) return;

    set({ ...initialState, screenshotId, sessionsLoading: true });

    screenshotApi
      .getScreenshot({ screenshotId })
      .then(({ response: res }) => set({ screenshot: res.screenshot ?? null }))
      .catch(() => set({ screenshot: null }));

    chatApi
      .listSessions({ screenshotId, pagination: { pageSize: PAGE_SIZE_SESSIONS, pageToken: '' } })
      .then(({ response: res }) => {
        const list = res.sessions ?? [];
        set({ sessions: list, sessionsLoading: false });

        if (list.length > 0) {
          const firstId = list[0].id;
          set({ activeSessionId: firstId });
          get().loadMessages(firstId, onResumeStream);
        }
      })
      .catch(() => set({ sessionsLoading: false }));
  },

  loadMessages: (sessionId, onResumeStream) => {
    chatApi
      .listMessages({ sessionId, pagination: { pageSize: PAGE_SIZE_MESSAGES, pageToken: '' } })
      .then(({ response: res }) => {
        const all = res.messages ?? [];

        const streamingMsg = [...all].reverse().find(
          (m) => m.role === MessageRole.ASSISTANT && m.status === MessageStatus.STREAMING,
        );

        if (streamingMsg && onResumeStream) {
          set({
            messages: all.filter((m) => m.id !== streamingMsg.id),
            loadedSessionId: sessionId,
          });
          onResumeStream(streamingMsg.id);
        } else {
          set({ messages: all, loadedSessionId: sessionId });
        }
      })
      .catch(() => set({ loadedSessionId: sessionId }));
  },

  setActiveSessionId: (id) => set({ activeSessionId: id }),

  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),

  handleAssistantDone: (msg, newTitle, countDelta = 2) => {
    set((state) => ({
      messages: [...state.messages, msg],
      sessions: state.sessions.map((s) =>
        s.id === state.activeSessionId
          ? {
              ...s,
              messageCount: (s.messageCount ?? 0) + countDelta,
              ...(newTitle ? { title: newTitle } : {}),
            }
          : s,
      ),
    }));
  },

  createSession: async () => {
    const { screenshotId, creatingSession } = get();
    if (!screenshotId || creatingSession) return;

    set({ creatingSession: true });
    try {
      const { response: res } = await chatApi.createSession({
        screenshotId,
        title: `Чат ${new Date().toLocaleString(LOCALE, {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })}`,
      });
      const newSession = res.session;
      if (newSession) {
        set((state) => ({
          sessions: [newSession, ...state.sessions],
          activeSessionId: newSession.id,
          messages: [],
          loadedSessionId: newSession.id,
        }));
      }
    } catch (err) {
      console.error('Ошибка при создании сессии', err);
    } finally {
      set({ creatingSession: false });
    }
  },

  deleteSession: async (sessionId) => {
    try {
      await chatApi.deleteSession({ sessionId });
      const { sessions, activeSessionId } = get();

      const remaining = sessions.filter((s) => s.id !== sessionId);
      set({ sessions: remaining });

      if (activeSessionId === sessionId) {
        const nextId = remaining.length > 0 ? remaining[0].id : null;
        set({ activeSessionId: nextId, messages: [], loadedSessionId: nextId });
      }
    } catch (err) {
      console.error('Ошибка при удалении сессии', err);
    }
  },

  reset: () => set(initialState),
}));
