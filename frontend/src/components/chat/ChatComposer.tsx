import { useRef, useCallback } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Send, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { chatMessageSchema, type ChatMessageValues } from '@/lib/schemas';
import { useDebounce } from '@/hooks/useDebounce';
import { MAX_CHAT_MESSAGE_LENGTH } from '@/lib/constants';

interface ChatComposerProps {
  onSend: (text: string) => void;
  sending: boolean;
  sendError?: string | null;
}

const CHAR_COUNTER_THRESHOLD = 0.7;

export function ChatComposer({ onSend, sending, sendError }: ChatComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
  } = useForm<ChatMessageValues>({
    resolver: zodResolver(chatMessageSchema),
    mode: 'onChange',
    defaultValues: { message: '' },
  });

  const messageValue = useWatch({ control, name: 'message', defaultValue: '' });
  const charCount = messageValue?.length ?? 0;
  const showCounter = charCount >= MAX_CHAT_MESSAGE_LENGTH * CHAR_COUNTER_THRESHOLD;

  const debouncedError = useDebounce(errors.message?.message, 500);

  const { ref: rhfRef, ...textareaProps } = register('message');

  const autoResize = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, []);

  const onFormSubmit = useCallback(
    (e?: React.BaseSyntheticEvent) =>
      handleSubmit((values) => {
        const text = values.message.trim();
        if (!text) return;
        onSend(text);
        reset();
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto';
        }
      })(e),
    [handleSubmit, onSend, reset],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        onFormSubmit();
      }
    },
    [onFormSubmit],
  );

  return (
    <div className="shrink-0 border-t border-border bg-background px-4 py-3">
      <form
        onSubmit={onFormSubmit}
        noValidate
        className="flex flex-col gap-2 max-w-3xl mx-auto"
      >
        <div className="flex gap-3 items-end">
          <Textarea
            {...textareaProps}
            ref={(el) => {
              rhfRef(el);
              textareaRef.current = el;
            }}
            onKeyDown={handleKeyDown}
            onInput={autoResize}
            disabled={sending}
            placeholder="Задайте вопрос о скриншоте…"
            rows={1}
            aria-invalid={!!errors.message}
            className={`flex-1 resize-none rounded-xl min-h-[42px] max-h-[160px] overflow-y-auto py-2.5 transition-colors ${
              debouncedError ? 'border-red-400 focus-visible:ring-red-300' : ''
            }`}
            style={{ height: 'auto' }}
          />
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                type="submit"
                disabled={!messageValue?.trim() || sending || !!errors.message}
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

        <div className="relative flex items-center justify-center h-4">
          <p
            className={`text-xs text-muted-foreground/60 transition-opacity duration-150 ${
              debouncedError || sendError ? 'opacity-0' : 'opacity-100'
            }`}
          >
            Enter — отправить · Shift+Enter — новая строка
          </p>

          {(debouncedError || sendError) && (
            <p
              role="alert"
              className="absolute inset-0 flex items-center gap-1 text-xs text-red-600"
            >
              <AlertCircle className="w-3 h-3 shrink-0" />
              <span className="truncate">{debouncedError ?? sendError}</span>
            </p>
          )}

          {showCounter && (
            <span
              className={`ml-auto shrink-0 text-xs tabular-nums transition-colors ${
                charCount > MAX_CHAT_MESSAGE_LENGTH
                  ? 'text-red-600 font-medium'
                  : charCount > MAX_CHAT_MESSAGE_LENGTH * 0.9
                  ? 'text-amber-500'
                  : 'text-muted-foreground/60'
              }`}
            >
              {charCount}&nbsp;/&nbsp;{MAX_CHAT_MESSAGE_LENGTH}
            </span>
          )}
        </div>
      </form>
    </div>
  );
}
