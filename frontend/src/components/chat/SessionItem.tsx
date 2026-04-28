import { Trash2 } from 'lucide-react';
import type { ChatSession } from '@/proto/generated/chat';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface SessionItemProps {
  session: ChatSession;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}

export function SessionItem({ session, isActive, onClick, onDelete }: SessionItemProps) {
  return (
    <div
      className={`group w-full flex items-start gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
        isActive
          ? 'bg-primary/10 border border-primary/20'
          : 'hover:bg-muted border border-transparent'
      }`}
      onClick={onClick}
    >
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium truncate ${isActive ? 'text-primary' : 'text-foreground'}`}>
          {session.title}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">
          {session.messageCount ?? 0} сообщений
        </p>
      </div>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0 shrink-0 text-muted-foreground hover:text-red-500"
            onClick={(e) => { e.stopPropagation(); onDelete(); }}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="right">Удалить сессию</TooltipContent>
      </Tooltip>
    </div>
  );
}
