import { Loader2, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface ChatComposerProps {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  sending: boolean;
  textareaRef: React.Ref<HTMLTextAreaElement>;
}

export function ChatComposer({ value, onChange, onSend, sending, textareaRef }: ChatComposerProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="shrink-0 border-t border-border bg-background px-4 py-3">
      <div className="flex gap-3 items-end max-w-3xl mx-auto">
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={sending}
          placeholder="Задайте вопрос о скриншоте…"
          rows={1}
          className="flex-1 resize-none rounded-xl min-h-[42px] max-h-[160px] overflow-y-auto py-2.5"
          style={{ height: 'auto' }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = 'auto';
            target.style.height = `${Math.min(target.scrollHeight, 160)}px`;
          }}
        />
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={onSend}
              disabled={!value.trim() || sending}
              size="sm"
              className="shrink-0 h-10 w-10 rounded-xl p-0"
            >
              {sending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">Отправить (Enter)</TooltipContent>
        </Tooltip>
      </div>
      <p className="text-center text-xs text-muted-foreground/60 mt-2">
        Enter — отправить · Shift+Enter — новая строка
      </p>
    </div>
  );
}
