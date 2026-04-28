import { Loader2, Plus } from 'lucide-react';
import type { ChatSession } from '@/proto/generated/chat';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { SessionItem } from '@/components/chat/SessionItem';

interface SessionSidebarProps {
  sessions: ChatSession[];
  sessionsLoading: boolean;
  activeSessionId: string | null;
  creatingSession: boolean;
  onNewSession: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
}

export function SessionSidebar({
  sessions,
  sessionsLoading,
  activeSessionId,
  creatingSession,
  onNewSession,
  onSelectSession,
  onDeleteSession,
}: SessionSidebarProps) {
  return (
    <aside className="w-64 min-w-0 overflow-hidden bg-background border-r border-border flex flex-col shrink-0">
      <div className="p-3 border-b border-border">
        <Button className="w-full" size="sm" onClick={onNewSession} disabled={creatingSession}>
          {creatingSession ? (
            <><Loader2 className="w-3.5 h-3.5 animate-spin" />Создание…</>
          ) : (
            <><Plus className="w-3.5 h-3.5" />Новый чат</>
          )}
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1 w-full">
          {sessionsLoading && (
            <div className="text-center text-muted-foreground text-xs py-6">Загрузка сессий…</div>
          )}
          {!sessionsLoading && sessions.length === 0 && (
            <div className="text-center text-muted-foreground text-xs py-6">
              Нет сессий.
              <br />
              Создайте первый чат выше.
            </div>
          )}
          {sessions.map((session) => (
            <SessionItem
              key={session.id}
              session={session}
              isActive={session.id === activeSessionId}
              onClick={() => onSelectSession(session.id)}
              onDelete={() => onDeleteSession(session.id)}
            />
          ))}
        </div>
      </ScrollArea>
    </aside>
  );
}
