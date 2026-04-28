import { useState, useEffect } from 'react';
import { X, CheckCircle2, XCircle, Info } from 'lucide-react';
import { subscribe, dismiss, type Toast } from '@/lib/toast';
import { cn } from '@/lib/utils';

const ICONS = {
  success: <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />,
  error:   <XCircle      className="w-4 h-4 shrink-0 text-red-500" />,
  info:    <Info         className="w-4 h-4 shrink-0 text-blue-500" />,
};

const STYLES: Record<Toast['variant'], string> = {
  success: 'border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950/60',
  error:   'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/60',
  info:    'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/60',
};

function ToastItem({ toast }: { toast: Toast }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const raf = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(raf);
  }, []);

  function handleDismiss() {
    setVisible(false);
    setTimeout(() => dismiss(toast.id), 200);
  }

  return (
    <div
      className={cn(
        'flex items-start gap-3 w-80 rounded-lg border px-4 py-3 shadow-md',
        'transition-all duration-200',
        visible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4',
        STYLES[toast.variant],
      )}
    >
      {ICONS[toast.variant]}
      <p className="flex-1 text-sm text-foreground leading-snug break-all">{toast.message}</p>
      <button
        onClick={handleDismiss}
        className="shrink-0 text-muted-foreground hover:text-foreground transition-colors mt-0.5"
        aria-label="Закрыть"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

export function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => subscribe(setToasts), []);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => (
        <div key={t.id} className="pointer-events-auto">
          <ToastItem toast={t} />
        </div>
      ))}
    </div>
  );
}
